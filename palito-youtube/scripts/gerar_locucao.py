#!/usr/bin/env python3
"""Gera uma locução contínua e as marcas de palavra da mesma tomada."""

import argparse
import asyncio
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import wave

from inspecionar_audio import hash_arquivo


def localizar_edge_tts():
    if importlib.util.find_spec("edge_tts") is not None:
        return
    # O pipx instala o executável e o Python com a biblioteca no mesmo ambiente.
    executavel = shutil.which("edge-tts")
    if executavel:
        nome = "python.exe" if os.name == "nt" else "python"
        python = Path(executavel).resolve().with_name(nome)
        if python.is_file() and python != Path(sys.executable).absolute():
            os.execv(str(python), [str(python), "-B", str(Path(__file__).resolve()), *sys.argv[1:]])
    raise RuntimeError("Execute com um Python que tenha o pacote edge-tts com suporte a WordBoundary.")


async def sintetizar(texto, voz, ritmo, pasta):
    import edge_tts

    fala = edge_tts.Communicate(texto, voz, rate=ritmo, boundary="WordBoundary")
    palavras = []
    with (pasta / "sintese.mp3").open("wb") as audio:
        async for evento in fala.stream():
            if evento["type"] == "audio":
                audio.write(evento["data"])
            elif evento["type"] == "WordBoundary":
                inicio = evento["offset"]
                palavras.append({
                    "texto": evento["text"],
                    "inicio_s": inicio / 10_000_000,
                    "fim_s": (inicio + evento["duration"]) / 10_000_000,
                })
    if not palavras:
        raise RuntimeError("A síntese terminou sem devolver marcas de palavra.")
    return palavras


def gerar(roteiro, destino, voz, ritmo):
    texto = roteiro.read_text(encoding="utf-8-sig").strip()
    if not texto:
        raise ValueError("O roteiro está vazio.")
    tomada = {
        "roteiro_sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
        "voz": voz,
        "ritmo": ritmo,
    }
    if destino.exists():
        marcas = destino / "palavras.json"
        audio = destino / "locucao.wav"
        if marcas.is_file() and audio.is_file():
            anterior = json.loads(marcas.read_text(encoding="utf-8"))
            if (isinstance(anterior, dict) and anterior.get("tomada") == tomada
                    and anterior.get("palavras") and anterior.get("audio_sha256") == hash_arquivo(audio)):
                print(f"Locução existente reutilizada em {destino}")
                return
        raise ValueError(f"A pasta {destino} já existe. Use outra pasta para uma nova tomada.")

    localizar_edge_tts()
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg precisa estar no PATH para decodificar a locução.")
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destino.parent) as temporario:
        pasta = Path(temporario) / "tomada"
        pasta.mkdir()
        palavras = asyncio.run(sintetizar(texto, voz, ritmo, pasta))
        wav = pasta / "locucao.wav"
        mp3 = pasta / "sintese.mp3"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", str(mp3),
                        "-map", "0:a:0", "-c:a", "pcm_s16le", str(wav)], check=True)
        with wave.open(str(wav), "rb") as arquivo:
            duracao = arquivo.getnframes() / arquivo.getframerate()
        anterior = 0
        for p in palavras:
            if not (p["texto"].strip() and anterior <= p["inicio_s"] < p["fim_s"] <= duracao):
                raise ValueError(f"A marca de {p['texto']!r} diverge da duração ou da ordem da tomada.")
            anterior = p["inicio_s"]
        marcas = {"tomada": tomada, "audio_sha256": hash_arquivo(wav),
                  "duracao_s": duracao, "palavras": palavras}
        (pasta / "palavras.json").write_text(
            json.dumps(marcas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        mp3.unlink()
        pasta.rename(destino)
    print(f"{len(palavras)} marcas em {duracao:.3f} s. Arquivos em {destino}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roteiro", type=Path, help="Texto em UTF-8 que será enviado à síntese.")
    parser.add_argument("destino", type=Path, help="Pasta para locucao.wav e palavras.json.")
    parser.add_argument("--voz", required=True, help="Identificador da voz escolhida, como pt-BR-ThalitaNeural.")
    parser.add_argument("--ritmo", default="+0%", help="Variação de velocidade, por exemplo --ritmo=-3%%.")
    args = parser.parse_args()
    try:
        gerar(args.roteiro, args.destino, args.voz, args.ritmo)
    except Exception as erro:
        parser.exit(1, f"Falha ao preparar a locução: {erro}\n")


if __name__ == "__main__":
    main()
