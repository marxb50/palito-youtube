"""Prepara a mixagem na mesma linha do tempo da imagem e das marcas de fala."""

import json
import math
import re
import subprocess

from renderizar import AUDIO_HZ, filtro_ajuste_audio
from stickman_engine import generate_sfx_track


def eventos_sonoros(cenas, fps):
    eventos = []
    for cena in cenas:
        inicio = cena.inicio / fps
        if cena.inicio and cena.entrada == 'folha':
            eventos.append((inicio, 'paper_flip', 0.32))
        elif cena.inicio:
            eventos.append((inicio, 'whoosh', 0.18))
        for quadro in sorted(cena.deixas_faladas):
            if quadro:
                eventos.append(((cena.inicio + quadro) / fps, 'pop', 0.11))
    return eventos


def medir_loudness(audio, filtro):
    resultado = subprocess.run(
        ['ffmpeg', '-nostdin', '-hide_banner', '-nostats', '-xerror',
         '-i', str(audio), '-map', '0:a:0', '-af', filtro + ':print_format=json',
         '-f', 'null', '-'],
        capture_output=True, text=True,
    )
    if resultado.returncode:
        raise ValueError(f'Falha ao medir loudness: {resultado.stderr.strip()[-1600:]}')
    blocos = re.findall(r'\{[^{}]*"input_i"[^{}]*\}', resultado.stderr, re.S)
    if not blocos:
        raise ValueError('O FFmpeg não retornou a medição de loudness.')
    return json.loads(blocos[-1])


def mixar(audio, amostras_entrada, tempo, pasta, cenas, sfx, lufs):
    """Devolve um WAV a 48 kHz com a duração do vídeo e seu número de amostras."""
    alvo = float(lufs) if lufs is not None else None
    if alvo is not None and not -70 <= alvo <= -5:
        raise ValueError('O alvo de loudness precisa estar entre -70 e -5 LUFS.')

    amostras = math.ceil(tempo.total * AUDIO_HZ / tempo.fps)
    ajuste = filtro_ajuste_audio(amostras_entrada, amostras)
    ffmpeg = ['ffmpeg', '-nostdin', '-v', 'error', '-xerror']
    mix = pasta / 'mix.wav'
    eventos = eventos_sonoros(cenas, float(tempo.fps)) if sfx else []
    if eventos:
        efeitos = pasta / 'sfx.wav'
        generate_sfx_track(str(efeitos), float(tempo.total / tempo.fps), eventos, fundo=False)
        filtros = (
            f'[0:a:0]{ajuste}[voz];[1:a:0]aresample={AUDIO_HZ}[sfx];'
            '[voz][sfx]amix=inputs=2:duration=first:normalize=0,'
            'alimiter=limit=0.95:level=false:latency=true[mix]'
        )
        subprocess.run(
            [*ffmpeg, '-i', str(audio), '-i', str(efeitos), '-filter_complex', filtros,
             '-map', '[mix]', '-c:a', 'pcm_s24le', str(mix)], check=True,
        )
    else:
        subprocess.run(
            [*ffmpeg, '-i', str(audio), '-map', '0:a:0', '-af', ajuste,
             '-c:a', 'pcm_s24le', str(mix)], check=True,
        )

    if alvo is None:
        return mix, amostras, None

    filtro = f'loudnorm=I={alvo}:TP=-1.5:LRA=11'
    medida = medir_loudness(mix, filtro)
    ajustes = {'I': 'input_i', 'TP': 'input_tp', 'LRA': 'input_lra', 'thresh': 'input_thresh'}
    info = {'alvo': alvo, 'entrada': medida}
    campos = (*ajustes.values(), 'target_offset')
    if not all(math.isfinite(float(medida[chave])) for chave in campos):
        info['estado'] = 'sem loudness mensurável'
        return mix, amostras, info

    parametros = ':'.join(f'measured_{nome}={medida[chave]}' for nome, chave in ajustes.items())
    normalizado = pasta / 'loudnorm.wav'
    filtro += (f':{parametros}:offset={medida["target_offset"]}:linear=true,'
               f'aresample={AUDIO_HZ},asetpts=N/SR/TB')
    subprocess.run(
        [*ffmpeg, '-i', str(mix), '-map', '0:a:0', '-af', filtro,
         '-c:a', 'pcm_s24le', str(normalizado)], check=True,
    )
    info['estado'] = 'normalizado'
    return normalizado, amostras, info
