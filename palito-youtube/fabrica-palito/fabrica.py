#!/usr/bin/env python3
"""Produz episódios narrados a partir de um roteiro e da direção de cada plano."""
import argparse
from collections import defaultdict
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unicodedata

BASE = Path(__file__).resolve().parent
SCRIPTS = BASE.parent / 'scripts'
if not (SCRIPTS / 'renderizar.py').is_file():
    SCRIPTS = BASE.parent / 'palito youtube' / 'scripts'
sys.path.insert(0, str(SCRIPTS))

from inspecionar_audio import hash_arquivo
from renderizar import preparar_tempo, codificar, conferir
from mixagem import mixar
from palco import Cena, pintor
from revisao import revisar


def salvar(path, dados):
    path.write_text(json.dumps(dados, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')


def tokens(texto):
    return re.findall(r'[^\W_]+',unicodedata.normalize('NFC',texto).casefold(),re.UNICODE)


def novo(destino, arquivo):
    if destino.exists():
        raise ValueError(f'{destino} já existe. Escolha outra pasta para o novo episódio.')
    fonte=arquivo.read_text(encoding='utf-8-sig') if arquivo else (
        'Qual objeto ajuda a contar esta história?\n\n'
        'Um livro muda de mãos. O que acontece depois?\n\n'
        'O detalhe que mudou foi quem ficou com o livro.')
    paragrafos=[p.strip().replace('\n',' ') for p in re.split(r'\n\s*\n',fonte.strip()) if p.strip()]
    if not paragrafos:
        raise ValueError('O roteiro está vazio.')
    cenas=[]
    for k,fala in enumerate(paragrafos):
        mundo='creme' if k in (0,len(paragrafos)-1) else 'kraft'
        elementos=[{'id':'apresentadora','tipo':'ator','papel':'guia','pos':[330,605,2.35],
                    'gestos':[[0,'pensar'],[.42,'indicar']]},
                   {'id':'objeto','tipo':'livro','pos':[[0,670,369,1.5],[.52,635,316,2.1]]}]
        cenas.append({'id':f'plano-{k+1:02}','fala':fala,'mundo':mundo,
                      'entrada':'folha' if k and cenas[-1]['mundo']!=mundo else 'corte',
                      'elementos':elementos})
    destino.mkdir(parents=True)
    salvar(destino/'episodio.json',{'versao':1,'voz':'pt-BR-ThalitaNeural','ritmo':'+0%',
                                    'exposicao':2,'planos':cenas})
    print(destino/'episodio.json')


def voz(episodio, base, texto, mudo):
    if 'audio' in episodio:
        if mudo and not (base/episodio['audio']).is_file():
            return None,None
        audio=(base/episodio['audio']).resolve(strict=True)
        marcas=(base/episodio['marcas']).resolve(strict=True) if episodio.get('marcas') else None
        return audio,marcas
    nome=episodio.get('voz','pt-BR-ThalitaNeural')
    ritmo=episodio.get('ritmo','+0%')
    chave=hashlib.sha256('\0'.join((nome,ritmo,texto)).encode()).hexdigest()[:16]
    pasta=base/'producao'/('voz-'+chave)
    if mudo:
        if (pasta/'locucao.wav').is_file() and (pasta/'palavras.json').is_file():
            return pasta/'locucao.wav',pasta/'palavras.json'
        return None,None
    pasta.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=pasta.parent) as tmp:
        roteiro=Path(tmp)/'roteiro.txt'
        roteiro.write_text(texto+'\n',encoding='utf-8')
        subprocess.run([sys.executable,'-B',str(SCRIPTS/'gerar_locucao.py'),str(roteiro),str(pasta),
                        '--voz',nome,'--ritmo='+ritmo],check=True)
    return pasta/'locucao.wav',pasta/'palavras.json'


def alinhar(planos,tempo,marcas,audio):
    grupos=[tokens(p['fala']) for p in planos]
    if not all(grupos):
        raise ValueError('Cada plano precisa de uma fala.')
    roteiro=[s for grupo in grupos for s in grupo]
    if marcas:
        dados=json.loads(marcas.read_text(encoding='utf-8-sig'))
        if isinstance(dados,dict) and dados.get('audio_sha256') and dados['audio_sha256']!=hash_arquivo(audio):
            raise ValueError('O hash das marcas diverge da faixa deste episódio.')
        entradas=dados['palavras'] if isinstance(dados,dict) else dados
        lidas=[(s,tempo.quadro(p.get('inicio_s',p.get('s')))) for p in entradas for s in tokens(p['texto'])]
        for k in range(max(len(roteiro),len(lidas))):
            a=roteiro[k] if k<len(roteiro) else '(fim do roteiro)'
            b=lidas[k][0] if k<len(lidas) else '(fim da voz)'
            if a!=b:
                raise ValueError(f'Palavra {k+1}: o roteiro traz {a!r} e a voz traz {b!r}. '
                                 'Ajuste a fala à transcrição, inclusive números por extenso.')
        modo='palavras da tomada'
    elif audio:
        lidas=[]
        modo='segundos do manifesto'
        if any('inicio_s' not in p for p in planos[1:]):
            raise ValueError('Com áudio sem marcas, defina inicio_s em cada plano após o primeiro e use chaves numéricas.')
    else:
        # Prévia silenciosa. Os índices simulados só orientam a edição do animatic.
        lidas=[(s,int(k*tempo.total/len(roteiro))) for k,s in enumerate(roteiro)]
        modo='estimativa por palavras para animatic mudo'
    pos=0
    inicios=[]
    grupos_marcados=[]
    for k,(plano,grupo) in enumerate(zip(planos,grupos)):
        trecho=lidas[pos:pos+len(grupo)]
        pos+=len(grupo)
        q=tempo.quadro(plano['inicio_s']) if 'inicio_s' in plano else (trecho[0][1] if k else 0)
        if not 0<=q<tempo.total or (k==0 and q!=0) or (k and q<=inicios[-1]):
            raise ValueError(f"{plano['id']}: início de plano fora da ordem ou da duração.")
        inicios.append(q)
        mapa=defaultdict(list)
        for palavra,indice in trecho:
            mapa[palavra].append(indice)
        grupos_marcados.append(mapa)
    return inicios,grupos_marcados,modo


def ler_manifesto(path):
    if path.is_dir():
        path=path/'episodio.json'
    path=path.resolve(strict=True)
    dados=json.loads(path.read_text(encoding='utf-8-sig'))
    if dados.get('versao')!=1:
        raise ValueError('O manifesto precisa de versao igual a 1.')
    planos=dados['planos']
    if not isinstance(planos,list) or not planos or len({p['id'] for p in planos})!=len(planos):
        raise ValueError('O manifesto requer planos com IDs únicos.')
    exp=dados.get('exposicao',2)
    if type(exp) is not int or not 1<=exp<=6:
        raise ValueError('exposicao deve ser um inteiro entre 1 e 6.')
    return path,dados


def produzir(path,args):
    path,dados=ler_manifesto(path)
    base=path.parent
    planos=dados['planos']
    texto='\n\n'.join(p['fala'].strip() for p in planos)
    audio,marcas=voz(dados,base,texto,args.mudo)
    duracao=dados.get('duracao_s')
    if duracao is None and args.mudo and audio is None:
        duracao=max(2.0,round(len(tokens(texto))/2.45,2))
    config=argparse.Namespace(fps='60',tamanho=args.tamanho,audio=audio,marcas=marcas,
                              duracao=str(duracao) if duracao is not None else None)
    tempo,amostras=preparar_tempo(config)
    if 9*tempo.largura!=16*tempo.altura:
        raise ValueError('O palco horizontal requer uma resolução 16:9.')
    inicios,grupos,modo=alinhar(planos,tempo,marcas,audio)
    fins=inicios[1:]+[tempo.total]
    cenas=[Cena(p,a,b,m,tempo,base,dados.get('exposicao',2))
           for p,a,b,m in zip(planos,inicios,fins,grupos)]
    pintar=pintor(cenas,tempo)
    nome=base.name+('-animatic' if args.mudo else '')
    if args.comando=='prova':
        if not 0<=args.quadro<tempo.total:
            raise ValueError(f'O quadro precisa estar entre 0 e {tempo.total-1}.')
        saida=args.saida or base/'producao'/f'quadro-{args.quadro:06}.png'
        if saida.suffix.lower()!='.png':
            raise ValueError('A prova precisa ter extensão .png.')
        entradas={path,audio,marcas}
        entradas.update(e.arquivo for cena in cenas for e in cena.elementos if e.tipo=='imagem')
        if saida.resolve() in entradas:
            raise ValueError('Escolha uma prova diferente das entradas.')
        saida.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=saida.parent) as tmp:
            quadro=Path(tmp)/'prova.png'
            pintar(args.quadro).write_to_png(str(quadro))
            quadro.replace(saida)
        print(saida)
        return
    saida=base/(nome+'.mp4')
    if saida.resolve()==audio:
        raise ValueError('O nome da faixa externa coincide com o da saída.')
    mapa={'fps':60,'quadros':tempo.total,'tamanho':[tempo.largura,tempo.altura],'sincronia':modo,
          'exposicao':dados.get('exposicao',2),'audio_sha256':hash_arquivo(audio) if audio else None,
          'planos':[{'id':p['id'],'inicio_q':a,'fim_q_exclusivo':b,'inicio_s':a/60,'mundo':p['mundo'],
                     'deixas_q':{termo:val for termo,val in g.items()}}
                    for p,a,b,g in zip(planos,inicios,fins,grupos)]}
    with tempfile.TemporaryDirectory(dir=base) as tmp:
        arquivo=Path(tmp)/'master.mp4'
        som_de_saida=None if args.mudo else audio
        lufs_alvo=args.lufs if args.lufs is not None else dados.get('lufs')
        sfx = args.sfx or dados.get('sfx', False)
        if som_de_saida is not None and (sfx or lufs_alvo is not None):
            som_de_saida, amostras, loudness = mixar(
                audio, amostras, tempo, Path(tmp), cenas, sfx, lufs_alvo,
            )
            if loudness is not None:
                mapa['loudness_lufs'] = loudness
        codificar(arquivo,tempo,pintar,som_de_saida,amostras)
        conferir(arquivo,tempo,som_de_saida is not None)
        mapa['mp4_sha256']=hash_arquivo(arquivo)
        caminho_mapa=Path(tmp)/'mapa.json'
        salvar(caminho_mapa,mapa)
        (base/'producao').mkdir(exist_ok=True)
        arquivo.replace(saida)
        caminho_mapa.replace(base/'producao'/('mapa-animatic.json' if args.mudo else 'mapa.json'))
    print(f'{saida} — {tempo.total} quadros, {float(tempo.total/tempo.fps):.3f} s',flush=True)


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    sub=cli.add_subparsers(dest='comando',required=True)
    n=sub.add_parser('novo',help='Cria um manifesto editável, com um plano por parágrafo.')
    n.add_argument('pasta',type=Path)
    n.add_argument('--roteiro',type=Path,help='Texto UTF-8 separado em parágrafos.')
    r=sub.add_parser('revisar',help='Extrai três quadros por plano do MP4 já produzido.')
    r.add_argument('episodios',type=Path,nargs='+')
    r.add_argument('--mudo',action='store_true',help='Examina o master do animatic.')
    for modo in ('produzir','prova'):
        p=sub.add_parser(modo,help='Exporta o lote na ordem indicada.' if modo=='produzir' else 'Desenha um quadro do episódio.')
        p.add_argument('episodios',type=Path,nargs='+' if modo=='produzir' else 1)
        p.add_argument('--mudo',action='store_true',help='Cria um animatic silencioso com a tomada local ou tempos estimados.')
        p.add_argument('--sfx',action='store_true',help='Mixa efeitos sonoros procedurais sincronizados às folhas e deixas.')
        p.add_argument('--lufs',type=float,help='Normaliza loudness em duas passagens (ex.: -16 para YouTube).')
        p.add_argument('--tamanho',default='1920x1080',help='Resolução horizontal 16:9, por exemplo 960x540.')
        if modo=='prova':
            p.add_argument('--quadro',type=int,required=True)
            p.add_argument('--saida',type=Path)
    a=cli.parse_args()
    try:
        if a.comando=='novo':
            novo(a.pasta,a.roteiro)
        else:
            for ep in a.episodios:
                pasta=ep if ep.is_dir() else ep.parent
                fd=os.open(pasta,os.O_RDONLY)
                try:
                    # Cada pasta tem um único master e mapa. Serializa publicações simultâneas do mesmo episódio.
                    fcntl.flock(fd,fcntl.LOCK_EX)
                    if a.comando=='revisar':
                        revisar(pasta.resolve(),a.mudo)
                    else:
                        produzir(ep,a)
                finally:
                    os.close(fd)
    except (OSError,ValueError,TypeError,KeyError,RuntimeError,ArithmeticError,subprocess.SubprocessError) as erro:
        cli.exit(1,f'Falha na fábrica: {erro}\n')


if __name__=='__main__':
    main()
