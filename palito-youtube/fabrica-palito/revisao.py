"""Monta pranchas visuais a partir dos quadros que chegaram ao MP4 e gera relatório QA (blackdetect, freezedetect, ebur128)."""
import json
from pathlib import Path
import re
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

from inspecionar_audio import hash_arquivo


def varrer_qa(mp4, mapa, com_audio):
    """Sinaliza trechos escuros ou estáticos e mede o áudio do master."""
    cmd = [
        'ffmpeg', '-nostdin', '-hide_banner', '-nostats', '-xerror', '-i', str(mp4),
        '-map', '0:v:0',
        '-vf', 'blackdetect=d=0.25:pix_th=0.10,freezedetect=n=-50dB:d=2.5',
    ]
    if com_audio:
        cmd += ['-map', '0:a:0', '-af', 'ebur128=peak=true']
    cmd += ['-f', 'null', '-']
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f'Falha na revisão do MP4: {r.stderr.strip()[-1600:]}')
    linhas = r.stderr.splitlines()
    eventos = [l.strip() for l in linhas if re.search(r'black_start:|freeze_(start|end|duration):', l)]
    resumo_audio = None
    if 'Summary:' in r.stderr:
        resumo_audio = [l.strip() for l in r.stderr[r.stderr.rfind('Summary:'):].splitlines() if l.strip()]
    return {
        'arquivo': mp4.name,
        'mp4_sha256': mapa.get('mp4_sha256'),
        'fps': mapa.get('fps'),
        'quadros': mapa.get('quadros'),
        'tamanho': mapa.get('tamanho'),
        'exposicao': mapa.get('exposicao'),
        'technical_status': 'warn' if eventos else 'pass',
        'artistic_status': 'not_assessed',
        'black_freeze_events': eventos,
        'ebur128_summary': resumo_audio,
    }


def fonte(px):
    try:
        return ImageFont.truetype('DejaVuSans.ttf', px)
    except OSError:
        return ImageFont.load_default()


def revisar(base, mudo=False):
    nome=base.name+('-animatic' if mudo else '')
    mp4=base/(nome+'.mp4')
    pasta=base/'producao'
    mapa=json.loads((pasta/('mapa-animatic.json' if mudo else 'mapa.json')).read_text(encoding='utf-8'))
    if hash_arquivo(mp4)!=mapa['mp4_sha256']:
        raise ValueError(f'O mapa de {nome} pertence a outra exportação.')
    destino=pasta/('revisao-'+mapa['mp4_sha256'][:12])
    selecoes=[]
    for plano in mapa['planos']:
        a,b=plano['inicio_q'],plano['fim_q_exclusivo']
        selecoes.append([a+round((b-a-1)*u) for u in (.16,.5,.84)])
    indices=sorted(set(q for grupo in selecoes for q in grupo))
    w,h=272,153
    legenda_h=24
    fila_h=h+legenda_h+27
    margem=14
    col=w+8
    pagina_max=8
    exp='+'.join(f'eq(n\\,{q})' for q in indices)
    cmd=['ffmpeg','-nostdin','-v','error','-xerror','-i',str(mp4),'-map','0:v:0','-an',
         '-vf',f'select={exp},scale={w}:{h}:flags=area','-fps_mode','passthrough',
         '-pix_fmt','rgb24','-threads','1','-f','rawvideo','pipe:1']
    titulo,menor=fonte(17),fonte(13)
    ultimo=-1
    with tempfile.TemporaryDirectory(dir=pasta) as tmp, subprocess.Popen(cmd,stdout=subprocess.PIPE) as proc:
        try:
            for inicio in range(0,len(selecoes),pagina_max):
                pagina=selecoes[inicio:inicio+pagina_max]
                folha=Image.new('RGB',(margem*2+col*3-8,margem+len(pagina)*fila_h),'#f4f0e3')
                lapis=ImageDraw.Draw(folha)
                for r,grupo in enumerate(pagina):
                    y=margem+r*fila_h
                    plano=mapa['planos'][inicio+r]
                    lapis.text((margem,y),plano['id'].replace('-',' '),font=titulo,fill='#194f56')
                    for j,q in enumerate(grupo):
                        if q!=ultimo:
                            bloco=proc.stdout.read(w*h*3)
                            if len(bloco)!=w*h*3:
                                raise ValueError('O vídeo terminou antes do quadro solicitado.')
                            imagem=Image.frombytes('RGB',(w,h),bloco)
                            ultimo=q
                        x=margem+j*col
                        folha.paste(imagem,(x,y+25))
                        lapis.text((x,y+h+28),f'{q/mapa["fps"]:.2f} s   ·   q {q}',font=menor,fill='#40595a')
                num=1+inicio//pagina_max
                folha.save(Path(tmp)/f'planos-{num:02}.jpg',quality=92)
            if proc.wait():
                raise RuntimeError('FFmpeg falhou ao ler o master para revisão.')
        except BaseException:
            proc.kill()
            raise
        qa = varrer_qa(mp4, mapa, com_audio=not mudo)
        (Path(tmp)/'qa.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        destino.mkdir(exist_ok=True)
        for arquivo in sorted(Path(tmp).iterdir()):
            arquivo.replace(destino/arquivo.name)
    print(destino)
