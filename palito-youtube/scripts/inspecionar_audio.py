#!/usr/bin/env python3
"""Mede a duração e as pausas da primeira faixa de áudio local."""

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys


AMOSTRAS = re.compile(r"(?m)^\[[^\]\n]*astats[^\]\n]*\]\s+Number of samples:\s*(\d+)\b")
PAUSA = re.compile(
    r"(?m)^\[[^\]\n]*silencedetect[^\]\n]*\]\s+"
    r"silence_(start|end):\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)"
)


def hash_arquivo(caminho):
    with caminho.open("rb") as arquivo:
        resumo = hashlib.sha256()
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            resumo.update(bloco)
        return resumo.hexdigest()


def executar(comando):
    try:
        resultado = subprocess.run(
            comando, capture_output=True, encoding="utf-8", errors="replace", check=False
        )
    except FileNotFoundError as erro:
        raise RuntimeError(f"Instale {comando[0]} e disponibilize-o no PATH.") from erro

    if resultado.returncode != 0:
        linhas = resultado.stderr.strip().splitlines()
        detalhe = linhas[-1] if linhas else f"código de saída {resultado.returncode}"
        raise RuntimeError(f"{comando[0]} falhou: {detalhe}")
    return resultado


def primeira_faixa(caminho):
    resultado = executar(
        [
            "ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
            "stream=index,codec_name,sample_rate,channels,duration_ts,time_base:format=format_name",
            "-of", "json", str(caminho),
        ]
    )
    dados = json.loads(resultado.stdout)
    faixas = dados["streams"]
    if not faixas:
        raise RuntimeError("O arquivo não contém uma faixa de áudio.")

    faixa = faixas[0]
    try:
        taxa = int(faixa.get("sample_rate", 0))
    except ValueError as erro:
        raise RuntimeError("A faixa de áudio não informa uma taxa de amostragem válida.") from erro
    if taxa <= 0:
        raise RuntimeError("A faixa de áudio não informa uma taxa de amostragem válida.")

    metadados = {
        "indice": faixa["index"],
        "codec": faixa.get("codec_name"),
        "taxa_amostragem_hz": taxa,
        "canais": faixa.get("channels"),
    }
    formatos = dados.get("format", {}).get("format_name", "").split(",")
    if faixa.get("codec_name") == "aac" and "mov" in formatos and isinstance(faixa.get("duration_ts"), int):
        declaradas = faixa["duration_ts"] * Fraction(faixa["time_base"]) * taxa
        if declaradas > 0 and declaradas.denominator == 1:
            metadados["amostras_declaradas"] = int(declaradas)
    return metadados


def intervalos_de_pausa(registro, duracao):
    pausas = []
    inicio = None
    for evento, segundos in PAUSA.findall(registro):
        tempo = max(0.0, min(duracao, float(segundos)))
        if evento == "start":
            inicio = round(tempo, 6)
        elif inicio is not None:
            fim = round(tempo, 6)
            if fim > inicio:
                pausas.append({"inicio_s": inicio, "fim_s": fim})
            inicio = None

    fim = round(duracao, 6)
    if inicio is not None and fim > inicio:
        pausas.append({"inicio_s": inicio, "fim_s": fim})
    return pausas


def inspecionar(caminho, ruido_db, pausa_minima):
    faixa = primeira_faixa(caminho)
    taxa = faixa["taxa_amostragem_hz"]
    # A contagem de amostras também cobre o fim do último bloco decodificado.
    filtros = (
        f"aformat=sample_rates={taxa},asetpts=N/SR/TB,"
        f"silencedetect=noise={ruido_db:g}dB:d={pausa_minima:.6f},"
        "astats=metadata=0:reset=0:measure_perchannel=none:measure_overall=Number_of_samples"
    )
    resultado = executar(
        [
            "ffmpeg", "-hide_banner", "-nostdin", "-nostats", "-loglevel", "info", "-xerror",
            "-i", str(caminho), "-map", f"0:{faixa['indice']}", "-vn", "-sn", "-dn",
            "-af", filtros, "-f", "null", "-",
        ]
    )
    contagens = AMOSTRAS.findall(resultado.stderr)
    if len(contagens) != 1 or int(contagens[0]) <= 0:
        raise RuntimeError("Não foi possível medir a duração contínua da faixa decodificada.")
    amostras = int(contagens[0])
    duracao = amostras / taxa
    # Um MP4/M4A pode apresentar só parte do último bloco AAC decodificado.
    declaradas = faixa.get("amostras_declaradas", amostras)
    apresentadas = declaradas if 0 <= amostras - declaradas < 2048 else amostras
    return {
        "duracao_s": round(duracao, 6),
        "amostras_por_canal": amostras,
        "amostras_apresentadas": apresentadas,
        "stream_audio": faixa,
        "pausas": intervalos_de_pausa(resultado.stderr, duracao),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", type=Path, help="Arquivo de áudio ou vídeo com áudio.")
    parser.add_argument("--ruido-db", type=float, default=-35, help="Limiar em dBFS (padrão: -35).")
    parser.add_argument(
        "--pausa-minima", type=float, default=0.25,
        help="Duração mínima de pausa em segundos (padrão: 0,25).",
    )
    args = parser.parse_args()
    if not math.isfinite(args.ruido_db) or args.ruido_db > 0:
        parser.error("--ruido-db deve ser um número finito menor ou igual a 0.")
    if not math.isfinite(args.pausa_minima) or args.pausa_minima < 0.000001:
        parser.error("--pausa-minima deve ser um número finito de ao menos 0,000001 s.")

    try:
        caminho = args.audio.expanduser().resolve()
        if not caminho.is_file():
            raise RuntimeError(f"Arquivo local não encontrado: {caminho}")
        dados = inspecionar(caminho, args.ruido_db, args.pausa_minima)
    except (OSError, RuntimeError, ValueError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1

    print(json.dumps(dados, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
