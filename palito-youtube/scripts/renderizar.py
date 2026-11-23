#!/usr/bin/env python3
"""Renderiza uma composição PyCairo do episódio em MP4 ou um quadro de prova em PNG."""

import argparse
from bisect import bisect_right
from dataclasses import dataclass
from fractions import Fraction
import json
import math
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile
import unicodedata

from inspecionar_audio import hash_arquivo, inspecionar


def termo(texto):
    return re.sub(r"^\W+|\W+$", "", unicodedata.normalize("NFC", texto).casefold())


@dataclass
class Tempo:
    fps: Fraction
    total: int
    largura: int
    altura: int
    palavras: dict

    def quadro(self, segundos):
        """Quadro que contém o instante global, com origem em zero."""
        return math.floor(Fraction(str(segundos)) * self.fps)

    def palavra(self, texto, ocorrencia=None, *, depois_de=0):
        """Quadro da palavra na tomada. Ocorrências começam em 1 após o limite inclusivo."""
        quadros = [q for q in self.palavras.get(termo(texto), ()) if q >= depois_de]
        if not quadros:
            raise ValueError(f"Palavra {texto!r} ausente a partir do quadro {depois_de}.")
        if ocorrencia is None:
            if len(quadros) != 1:
                raise ValueError(f"{texto!r} aparece {len(quadros)} vezes. Indique a ocorrência ou depois_de.")
            return quadros[0]
        if type(ocorrencia) is not int or not 1 <= ocorrencia <= len(quadros):
            raise ValueError(f"Ocorrência {ocorrencia} inválida para {texto!r} ({len(quadros)} disponíveis).")
        return quadros[ocorrencia - 1]


def ler_marcas(caminho, tempo, audio=None, duracao_audio=None):
    dados = json.loads(caminho.read_text(encoding="utf-8-sig"))
    registros = dados.get("palavras") if isinstance(dados, dict) else dados
    if not isinstance(registros, list) or not registros:
        raise ValueError("O arquivo de marcas precisa de uma lista de palavras.")
    if audio and isinstance(dados, dict) and dados.get("audio_sha256"):
        if dados["audio_sha256"] != hash_arquivo(audio):
            print("As marcas pertencem a outra versão do arquivo de áudio. "
                  "Confira o alinhamento no início e no fim da faixa.", file=sys.stderr)
    limite = duracao_audio if duracao_audio is not None else tempo.total / tempo.fps
    indice = {}
    anterior = Fraction(0)
    for i, p in enumerate(registros, 1):
        if not isinstance(p, dict) or not isinstance(p.get("texto"), str) or not termo(p["texto"]):
            raise ValueError(f"Marca {i} sem palavra.")
        # Também aceita o formato {texto, s, fim} usado na primeira demo do projeto.
        inicio = Fraction(str(p.get("inicio_s", p.get("s"))))
        fim = Fraction(str(p.get("fim_s", p.get("fim"))))
        if not anterior <= inicio < fim <= limite:
            raise ValueError(f"Tempos da marca {i} ({p['texto']!r}) fora da ordem ou da duração do vídeo.")
        indice.setdefault(termo(p["texto"]), []).append(tempo.quadro(inicio))
        anterior = inicio
    return indice


def preparar_tempo(args):
    fps = Fraction(args.fps)
    formato = re.fullmatch(r"(\d+)[xX](\d+)", args.tamanho)
    if fps <= 0 or formato is None:
        raise ValueError("Use fps positivo e tamanho no formato 1920x1080.")
    largura, altura = map(int, formato.groups())
    if min(largura, altura) < 2 or largura % 2 or altura % 2:
        raise ValueError("O formato H.264/yuv420p exige largura e altura positivas e pares.")

    audio_s = None
    amostras_audio = None
    if args.audio is not None:
        audio = inspecionar(args.audio.resolve(strict=True), -35, 0.25)
        amostras_audio = audio["amostras_apresentadas"]
        audio_s = Fraction(amostras_audio, audio["stream_audio"]["taxa_amostragem_hz"])
    duracao = Fraction(args.duracao) if args.duracao is not None else audio_s
    if duracao is None or duracao <= 0:
        raise ValueError("Informe --audio ou --duracao com uma duração positiva em segundos.")
    quadros_exatos = duracao * fps
    total = math.ceil(quadros_exatos)
    if audio_s is not None and audio_s * fps > total:
        raise ValueError(f"A faixa mede {float(audio_s):.6f} s e ultrapassa o alvo de {float(duracao):g} s. "
                         "Ajuste as pausas ou a locução antes de exportar.")
    if args.duracao is not None and quadros_exatos.denominator != 1:
        mais_proximo = math.floor(quadros_exatos + Fraction(1, 2))
        min_audio = math.ceil(audio_s * fps) if audio_s is not None else 0
        total = max(1, mais_proximo, min_audio)
        unidade = "quadro" if total == 1 else "quadros"
        print(f"Alvo entre quadros a {fps} fps. O vídeo terá {total} {unidade} "
              f"({float(total / fps):.6f} s).", file=sys.stderr)
    tempo = Tempo(fps, total, largura, altura, {})
    if args.marcas:
        tempo.palavras = ler_marcas(args.marcas, tempo, args.audio, audio_s)
    return tempo, amostras_audio


def carregar_planos(composicao, tempo):
    sys.path.insert(0, str(composicao.resolve(strict=True).parent))
    montar = runpy.run_path(str(composicao)).get("montar")
    if not callable(montar):
        raise ValueError("A composição deve fornecer montar(tempo).")
    planos = list(montar(tempo))
    inicios, desenhos = [], []
    for inicio, desenhar in planos:
        if type(inicio) is not int or not 0 <= inicio < tempo.total or not callable(desenhar):
            raise ValueError(f"Plano inválido no quadro {inicio!r}.")
        if inicios and inicio <= inicios[-1]:
            raise ValueError("Os planos devem começar em quadros estritamente crescentes.")
        inicios.append(inicio)
        desenhos.append(desenhar)
    if not inicios or inicios[0] != 0:
        raise ValueError("O primeiro plano deve começar no quadro zero.")
    return inicios, desenhos


def criar_pintor(tempo, planos):
    import cairo

    inicios, desenhos = planos
    superficie = cairo.ImageSurface(cairo.FORMAT_RGB24, tempo.largura, tempo.altura)

    def pintar(quadro):
        ctx = cairo.Context(superficie)
        ctx.set_source_rgb(245/255, 237/255, 214/255)
        ctx.paint()
        indice = bisect_right(inicios, quadro) - 1
        desenhos[indice](ctx, quadro - inicios[indice])
        superficie.flush()
        return superficie

    return pintar


AUDIO_HZ = 48000


def filtro_ajuste_audio(amostras_origem, amostras_destino):
    return (f"atrim=end_sample={amostras_origem},aresample={AUDIO_HZ},asetpts=N/SR/TB,"
            f"apad=whole_len={amostras_destino},atrim=end_sample={amostras_destino}")


def codificar(arquivo, tempo, pintar, audio, amostras_audio):
    pixel = "bgr0" if sys.byteorder == "little" else "0rgb"
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-f", "rawvideo",
           "-pixel_format", pixel, "-video_size", f"{tempo.largura}x{tempo.altura}",
           "-framerate", str(tempo.fps), "-i", "pipe:0"]
    if audio:
        amostras = math.ceil(tempo.total * AUDIO_HZ / tempo.fps)
        filtro = filtro_ajuste_audio(amostras_audio, amostras)
        cmd += ["-i", str(audio.resolve()), "-map", "0:v:0", "-map", "1:a:0",
                "-af", filtro, "-c:a", "aac", "-b:a", "160k"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(arquivo)]
    with tempfile.TemporaryFile() as log, subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log) as proc:
        try:
            for quadro in range(tempo.total):
                proc.stdin.write(pintar(quadro).get_data())
            proc.stdin.close()
        except BrokenPipeError:
            pass
        except BaseException:
            proc.kill()
            raise
        if proc.wait():
            log.seek(0)
            raise RuntimeError(log.read().decode(errors="replace").strip() or "Falha ao codificar o vídeo.")


def conferir(arquivo, tempo, com_audio):
    campos = "stream=codec_type,codec_name,width,height,avg_frame_rate,nb_frames,duration"
    resultado = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", campos,
                                         "-of", "json", str(arquivo)], text=True)
    streams = json.loads(resultado)["streams"]
    video = next(s for s in streams if s["codec_type"] == "video")
    if (video["codec_name"] != "h264" or int(video["nb_frames"]) != tempo.total
            or Fraction(video["avg_frame_rate"]) != tempo.fps
            or (video["width"], video["height"]) != (tempo.largura, tempo.altura)):
        raise ValueError("O vídeo exportado diverge da composição em formato, quadros ou cadência.")
    audios = [s for s in streams if s["codec_type"] == "audio"]
    if len(audios) != int(com_audio):
        raise ValueError("A quantidade de faixas de áudio exportadas diverge do pedido.")
    if audios:
        duracao = tempo.total / tempo.fps
        if audios[0]["codec_name"] != "aac" or abs(Fraction(audios[0]["duration"]) - duracao) > Fraction(1024, 48000):
            raise ValueError("O áudio exportado diverge da duração ou do formato planejado.")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", str(arquivo),
                    "-map", "0:v:0", "-map", "0:a:0?", "-f", "null", "-"], check=True)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("composicao", type=Path, help="Arquivo .py do episódio com montar(tempo).")
    cli.add_argument("saida", type=Path, help="Arquivo .mp4 ou, com --quadro, .png.")
    cli.add_argument("--audio", type=Path, help="Locução ou mistura já sincronizada.")
    cli.add_argument("--marcas", type=Path, help="JSON com os tempos das palavras desta tomada.")
    cli.add_argument("--duracao", help="Duração alvo em segundos. Por padrão, usa a faixa inteira.")
    cli.add_argument("--fps", default="60", help="Quadros por segundo. Aceita frações como 30000/1001.")
    cli.add_argument("--tamanho", default="1920x1080")
    cli.add_argument("--quadro", type=int, help="Extrai só este quadro global, contado a partir de zero.")
    args = cli.parse_args()
    try:
        extensao = ".png" if args.quadro is not None else ".mp4"
        if args.saida.suffix.lower() != extensao:
            raise ValueError(f"Use saída {extensao} neste modo.")
        for entrada in (args.composicao, args.audio, args.marcas):
            if entrada and entrada.resolve() == args.saida.resolve():
                raise ValueError("Escolha uma saída diferente dos arquivos de entrada.")
        tempo, amostras_audio = preparar_tempo(args)
        if args.quadro is not None and not 0 <= args.quadro < tempo.total:
            raise ValueError(f"O quadro deve estar entre 0 e {tempo.total - 1}.")
        planos = carregar_planos(args.composicao, tempo)
        pintar = criar_pintor(tempo, planos)
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=args.saida.parent) as trabalho:
            provisoria = Path(trabalho) / ("render" + extensao)
            if args.quadro is not None:
                pintar(args.quadro).write_to_png(str(provisoria))
            else:
                codificar(provisoria, tempo, pintar, args.audio, amostras_audio)
                conferir(provisoria, tempo, args.audio is not None)
            provisoria.replace(args.saida)
        print(f"{args.saida} · {float(tempo.total / tempo.fps):.6f} s a {tempo.fps} fps")
    except (OSError, ValueError, TypeError, ArithmeticError, RuntimeError, ImportError,
            KeyError, StopIteration, subprocess.SubprocessError) as erro:
        cli.exit(1, f"Falha no render: {erro}\n")


if __name__ == "__main__":
    main()
