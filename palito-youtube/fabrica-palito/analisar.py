"""Mede todos os quadros exibidos de uma referência e preserva o PTS de cada um."""

import argparse
import csv
from fractions import Fraction
import json
import os
from pathlib import Path
import re
import statistics
import subprocess
import tempfile

from PIL import Image, ImageChops, ImageDraw


LARGURA, ALTURA = 256, 144
PIXELS = LARGURA * ALTURA
PONTOS = [(x, y) for x in (5, 25, 60, 128, 196, 230, 250) for y in (4, 11, 132, 139)]
LINHA = re.compile(r"\bn:\s*(\d+)\s+pts:\s*(-?\d+)")
BASE = re.compile(r"config in time_base:\s*(\d+/\d+)")


def por_paridade(areas):
    grupos = {}
    for inicio, tipo in ((1,"impar"),(2,"par")):
        pares = areas[inicio::2]
        grupos[tipo] = {"comparacoes":len(pares),
                        "sem_pixel_acima_do_limiar":sum(a == 0 for a in pares),
                        "area_maxima_pct":max(pares) if pares else None}
    return grupos


def extrair_tira(video, pasta, inicio, quantidade):
    if inicio < 0 or not 1 <= quantidade <= 24:
        raise ValueError("Use índice inicial positivo ou zero e quantidade entre 1 e 24.")
    stream = next(s for s in inspecionar(video)["streams"] if s["codec_type"]=="video")
    w = 288
    h = max(1, round(w * stream["height"] / stream["width"]))
    # trim conta quadros decodificados e também funciona em entradas com fps variável.
    filtro=f"trim=start_frame={inicio}:end_frame={inicio+quantidade},scale={w}:{h}:flags=area"
    cmd=["ffmpeg","-nostdin","-v","error","-xerror","-i",str(video),"-map","0:v:0","-an",
         "-vf",filtro,"-fps_mode","passthrough","-threads","1","-pix_fmt","rgb24","-f","rawvideo","-"]
    raw=subprocess.check_output(cmd)
    if len(raw)!=w*h*3*quantidade:
        raise ValueError("A tira ultrapassa o último quadro da referência.")
    colunas=min(quantidade,6)
    saida=Image.new("RGB",((w+6)*colunas,(h+25)*((quantidade+colunas-1)//colunas)),"#f4f0e2")
    draw=ImageDraw.Draw(saida)
    for j in range(quantidade):
        a=j*w*h*3
        img=Image.frombytes("RGB",(w,h),raw[a:a+w*h*3])
        x,y=j%colunas*(w+6),j//colunas*(h+25)
        saida.paste(img,(x,y))
        draw.text((x+4,y+h+3),f"q {inicio+j}",fill="#255258")
    pasta.mkdir(parents=True,exist_ok=True)
    destino=pasta/f"tira-{inicio:06d}-{inicio+quantidade-1:06d}.png"
    saida.save(destino)
    print(destino)


def inspecionar(video):
    campos = "stream=index,codec_type,codec_name,width,height,nb_frames,avg_frame_rate,duration:format=duration"
    dados = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", campos,
                                     "-of", "json", str(video)], text=True)
    return json.loads(dados)


def medir(video, log, amostras):
    filtro = f"scale={LARGURA}:{ALTURA}:flags=area,format=rgb24,showinfo=checksum=0"
    cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-nostats", "-loglevel", "info", "-xerror",
           "-i", str(video), "-map", "0:v:0", "-an", "-vf", filtro, "-fps_mode", "passthrough",
           "-c:v", "rawvideo", "-threads", "1", "-f", "rawvideo", "pipe:1"]
    linhas = []
    anterior = None
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=log) as proc:
        try:
            while bloco := proc.stdout.read(PIXELS * 3):
                if len(bloco) != PIXELS * 3:
                    raise ValueError("FFmpeg devolveu um quadro incompleto.")
                rgb = Image.frombytes("RGB", (LARGURA, ALTURA), bloco)
                y = rgb.convert("L")
                if anterior is None:
                    delta = area = 0.0
                else:
                    hist = ImageChops.difference(y, anterior).histogram()
                    delta = sum(n * quantidade for n, quantidade in enumerate(hist)) / PIXELS
                    area = 100 * sum(hist[8:]) / PIXELS
                borda = [rgb.getpixel(p) for p in PONTOS]
                cor = [int(statistics.median(c)) for c in zip(*borda)]
                escuro = 100 * sum(y.histogram()[:115]) / PIXELS
                indice = len(linhas)
                if amostras and indice % 60 == 0:
                    rgb.save(amostras / f"{indice:06}.jpg", quality=90)
                linhas.append((delta, area, escuro, *cor))
                anterior = y
        except BaseException:
            proc.kill()
            raise
        if proc.wait():
            log.seek(0)
            raise RuntimeError(log.read()[-2400:].decode(errors="replace"))
    return linhas


def analisar(video, saida, amostras=None):
    info = inspecionar(video)
    stream = next(s for s in info["streams"] if s["codec_type"] == "video")
    saida.mkdir(parents=True, exist_ok=True)
    if amostras:
        amostras.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=saida) as tmp:
        tmp = Path(tmp)
        with (tmp / "ffmpeg.log").open("w+b") as log:
            dados = medir(video, log, amostras)
            log.seek(0)
            base, pts = None, []
            for linha in log:
                linha = linha.decode(errors="replace")
                if m := BASE.search(linha):
                    nova_base = Fraction(m[1])
                    if base is not None and base != nova_base:
                        raise ValueError("A base de tempo mudou durante a leitura.")
                    base = nova_base
                if m := LINHA.search(linha):
                    if int(m[1]) != len(pts):
                        raise ValueError("Numeração de quadros descontínua.")
                    pts.append(int(m[2]))
        if base is None or not pts or len(pts) != len(dados) or any(b <= a for a, b in zip(pts, pts[1:])):
            raise ValueError("A contagem de PTS diverge dos quadros medidos.")
        if stream.get("nb_frames", "N/A") != "N/A" and len(pts) != int(stream["nb_frames"]):
            raise ValueError("A contagem decodificada diverge do cabeçalho do vídeo.")
        with (tmp / "quadros.csv").open("w", newline="", encoding="utf-8") as f:
            tabelar = csv.writer(f)
            tabelar.writerow(["quadro", "pts", "tempo_s", "delta_luma", "area_mudou_pct",
                              "area_escura_pct", "borda_r", "borda_g", "borda_b"])
            for n, (p, linha) in enumerate(zip(pts, dados)):
                delta, area, escuro, r, g, b = linha
                tabelar.writerow([n, p, f"{float(p * base):.6f}", f"{delta:.5f}",
                                  f"{area:.4f}", f"{escuro:.4f}", r, g, b])
        # A primeira imagem não tem par de comparação.
        areas = sorted(d[1] for d in dados[1:])
        grandes = [i for i, d in enumerate(dados) if d[1] >= 35]
        eventos = []
        for q in grandes:
            if eventos and q == eventos[-1][1] + 1:
                eventos[-1][1] = q
            else:
                eventos.append([q, q])
        resultado = {
            "arquivo": video.name, "midia": info, "quadros_medidos": len(pts), "base_pts": str(base),
            "primeiro_pts": pts[0], "ultimo_pts": pts[-1],
            "passos_pts": sorted(set(b-a for a,b in zip(pts,pts[1:]))),
            "resolucao_de_medicao": [LARGURA, ALTURA],
            "limiar_de_variacao_luma": 8, "comparacao_por_indice_do_quadro": por_paridade([d[1] for d in dados]),
            "mediana_area_mudou_pct": statistics.median(areas) if areas else None,
            "percentil_90_area_mudou_pct": areas[round(.9*(len(areas)-1))] if areas else None,
            "pares_com_menos_de_1pct": sum(a < 1 for a in areas),
            "pares_com_35pct_ou_mais": len(grandes),
            "intervalos_35pct_inclusivos": eventos,
        }
        (tmp / "medidas.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        for nome in ("quadros.csv", "medidas.json"):
            os.replace(tmp / nome, saida / nome)
    print(f"{len(pts)} quadros medidos em {saida}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("saida", type=Path)
    parser.add_argument("--amostras", type=Path, help="Salva uma miniatura de apoio a cada 60 quadros.")
    parser.add_argument("--tira",type=int,metavar="PRIMEIRO_QUADRO",help="Extrai quadros consecutivos em uma prancha PNG.")
    parser.add_argument("--quantidade",type=int,default=6,help="Número de quadros consecutivos da tira (1 a 24).")
    args = parser.parse_args()
    if args.tira is not None:
        extrair_tira(args.video.resolve(strict=True),args.saida,args.tira,args.quantidade)
    else:
        analisar(args.video.resolve(strict=True), args.saida, args.amostras)
