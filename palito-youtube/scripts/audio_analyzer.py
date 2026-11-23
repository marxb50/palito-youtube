#!/usr/bin/env python3
"""
audio_analyzer.py — Analisador e Sincronizador de Áudio Externo (Google TTS com Expressões) + Roteiro
Mede a duração exata do áudio enviado pelo usuário, detecta todas as pausas naturais de fala
via FFmpeg `silencedetect` e distribui/alinha os blocos do texto do roteiro em um `timeline.json`
preciso para dirigir a animação a 60 FPS.
"""

import os
import re
import sys
import json
import argparse
import subprocess

def get_audio_duration(audio_path):
    res = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(res.stdout.strip())

def detect_silences(audio_path, noise_db=-32, min_silence_dur=0.22):
    """Retorna uma lista de tuplas (silence_start, silence_end, midpoint) detectadas no áudio."""
    cmd = [
        "ffmpeg", "-i", audio_path,
        "-af", f"silencedetect=noise={noise_db}dB:d={min_silence_dur}",
        "-f", "null", "-",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    stderr = res.stderr

    starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", stderr)]

    silences = []
    for s, e in zip(starts, ends):
        silences.append((round(s, 3), round(e, 3), round((s + e) / 2.0, 3)))
    return silences

def align_script_to_audio(audio_path, script_paragraphs):
    """
    Alinha uma lista de parágrafos/cenas do roteiro aos timestamps reais do arquivo de áudio
    combinando o peso proporcional de caracteres com as pausas reais detectadas no áudio.
    """
    total_dur = get_audio_duration(audio_path)
    silences = detect_silences(audio_path)

    paragraphs = [p.strip() for p in script_paragraphs if p.strip()]
    if not paragraphs:
        return [{"id": "seg01", "text": "", "start": 0.0, "duration": total_dur, "end": total_dur}]

    total_chars = sum(len(p) for p in paragraphs)
    timeline = []
    cur_start = 0.0

    for idx, text in enumerate(paragraphs):
        seg_id = f"seg{idx+1:02d}"
        if idx == len(paragraphs) - 1:
            seg_end = round(total_dur, 3)
        else:
            # Estimativa proporcional pelo tamanho do texto
            weight = len(text) / max(1, total_chars)
            est_end = cur_start + weight * total_dur
            # Procura a pausa real (silêncio) mais próxima da estimativa (dentro de +-2.5s)
            best_cut = est_end
            best_dist = 2.5
            for (s_start, s_end, mid) in silences:
                dist = abs(mid - est_end)
                if dist < best_dist and mid > cur_start + 1.0:
                    best_dist = dist
                    best_cut = mid
            seg_end = round(min(total_dur - 0.2, best_cut), 3)

        timeline.append({
            "id": seg_id,
            "text": text,
            "file": os.path.abspath(audio_path),
            "start": round(cur_start, 3),
            "duration": round(seg_end - cur_start, 3),
            "end": seg_end,
        })
        cur_start = seg_end

    return timeline

def main():
    parser = argparse.ArgumentParser(description="Alinha áudio externo (Google TTS) com texto do roteiro.")
    parser.add_argument("--audio", required=True, help="Caminho do arquivo de áudio (.mp3, .wav, .m4a)")
    parser.add_argument("--script", required=False, help="Arquivo .txt com o roteiro (uma cena por linha/parágrafo)")
    parser.add_argument("--output", required=True, help="Caminho de saída do timeline.json")
    args = parser.parse_args()

    if args.script and os.path.exists(args.script):
        with open(args.script, "r", encoding="utf-8") as f:
            raw_lines = [line.strip() for line in f.read().split("\n") if line.strip()]
    else:
        raw_lines = ["Cena Completa"]

    tl = align_script_to_audio(args.audio, raw_lines)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(tl, f, indent=2, ensure_ascii=False)

    print(f"[Audio Analyzer] Duração total: {tl[-1]['end']:.2f}s | {len(tl)} cenas mapeadas em: {args.output}")
    print(json.dumps(tl, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
