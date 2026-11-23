"""Traduz as trajetórias do manifesto em desenhos e cortes na cadência da voz."""
from bisect import bisect_right
import hashlib
import math
from pathlib import Path

import cairo

from puppet_30 import ARCHETYPE_ALIASES
import arte


ARQUETIPOS = set(ARCHETYPE_ALIASES) | set(ARCHETYPE_ALIASES.values())
POSE_ELENCO = {
    'andar': 'walk', 'indicar': 'point_right', 'abrir': 'present_both',
    'receber': 'point_right', 'surpresa': 'cheer', 'pensar': 'hips', 'repouso': 'idle',
}


def numero(v):
    if type(v) not in (int, float) or not math.isfinite(v):
        raise ValueError(f'Número inválido: {v!r}.')
    return v


def vetor(v, tamanho):
    if not isinstance(v,list) or len(v) != tamanho:
        raise ValueError(f'Esperava uma lista com {tamanho} coordenadas, recebi {v!r}.')
    return tuple(numero(x) for x in v)


class Trilha:
    def __init__(self, valor, padrao, chave):
        self.instantes = []
        self.valores = []
        dados = valor if valor is not None else list(padrao)
        if not isinstance(dados,list) or not dados:
            raise ValueError(f'Trilha vazia ou inválida: {dados!r}.')
        if not isinstance(dados[0], list):
            dados = [[0, *dados]]
        for instante, *v in dados:
            q = chave(instante)
            if self.instantes and self.instantes[-1] >= q:
                raise ValueError(f'Chaves fora de ordem ou no mesmo quadro: {dados!r}.')
            self.instantes.append(q)
            self.valores.append(vetor(v,len(padrao)))

    def valor(self,q):
        n = bisect_right(self.instantes,q)
        if n==0:
            return self.valores[0]
        if n==len(self.instantes):
            return self.valores[-1]
        u=(q-self.instantes[n-1])/(self.instantes[n]-self.instantes[n-1])
        u=u*u*(3-2*u)
        return tuple(a+(b-a)*u for a,b in zip(self.valores[n-1],self.valores[n]))


def faixas(dados, chave, opcoes=None):
    tabela=[]
    for marca,estado in dados:
        if opcoes and estado not in opcoes:
            raise ValueError(f'Estado desconhecido: {estado}.')
        q=chave(marca)
        if tabela and q<=tabela[-1][0]:
            raise ValueError(f'Estados fora de ordem: {dados!r}.')
        tabela.append((q,estado))
    return tabela


class Elemento:
    def __init__(self,d,chave,base):
        self.id=d['id']
        self.tipo=d['tipo']
        self.pos=Trilha(d.get('pos'),(480,410,1),chave)
        self.valor=Trilha(d.get('valor'),(1,),chave)
        self.angulo=Trilha(d.get('angulo'),(0,),chave)
        self.opacidade=Trilha(d.get('opacidade'),(1,),chave)
        if any(s[2]<=0 for s in self.pos.valores):
            raise ValueError(f'{self.id}: a escala deve ser positiva.')
        self.frente=d.get('frente',1)
        if self.frente not in (-1,1):
            raise ValueError(f'{self.id}: frente deve ser 1 ou -1.')
        self.olhar=Trilha(d.get('olhar'),(.15,),chave)
        self.rotulo=str(d.get('rotulo',''))
        self.papel=d.get('papel','guia')
        self.expressao=d.get('expressao')
        self.prop_esq=d.get('prop_esq')
        self.prop_dir=d.get('prop_dir')
        self.colete=bool(d.get('colete',False))
        self.tela=bool(d.get('tela',False))
        self.fase=int.from_bytes(hashlib.sha256(self.id.encode()).digest()[:2],'big')/2500
        self.sombra=bool(d.get('sombra',self.tipo in ('ator','elenco') and not self.tela))
        self.gestos=faixas(d.get('gestos',[[0,'repouso']]),chave,arte.GESTOS)
        self.toques=[]
        for toque in d.get('toques',[]):
            inicio, fim = chave(toque['de']), chave(toque['ate'])
            mao=toque.get('mao','dir')
            if mao not in ('esq','dir') or inicio>fim:
                raise ValueError(f'{self.id}: contato inválido.')
            self.toques.append((inicio,fim,mao,toque['em'],vetor(toque.get('offset',[0,0]),2)))
        conhecidos=arte.OBJETOS|{'ator','imagem','elenco'}
        if self.tipo not in conhecidos:
            raise ValueError(f'Tipo de elemento desconhecido: {self.tipo}.')
        if self.tipo=='ator' and self.papel not in arte.PAPEIS:
            raise ValueError(f'Figurino desconhecido: {self.papel}.')
        if self.tipo=='elenco' and self.papel not in ARQUETIPOS:
            raise ValueError('O campo papel do elenco recebe um número de 1 a 40 ou apelido do catálogo.')
        if self.tipo=='imagem':
            self.arquivo=(base / d['arquivo']).resolve(strict=True)
            if self.arquivo.suffix.lower()!='.png':
                raise ValueError('O palco aceita arte externa em PNG.')
            self.sprite=arte.imagem(self.arquivo)
        if self.toques and (self.tipo not in ('ator','elenco') or any(v[0]!=0 for v in self.angulo.valores)):
            raise ValueError('A mão em contato requer um ator com rotação corporal zero.')

    def desenhar(self,c,p,q,t,posicoes):
        opac=self.opacidade.valor(q)[0]
        if opac<=0:
            return
        x,y,s=posicoes[self.id]
        if self.sombra and opac > .75:
            arte.sombra(c,x,y+1,34*s,p)
        c.save()
        c.translate(x,y)
        c.scale(s*self.frente,s)
        c.rotate(math.radians(self.angulo.valor(q)[0]))
        if opac<.999:
            c.push_group()
        tipo=self.tipo
        if tipo in ('ator','elenco'):
            idx=bisect_right([f for f,_ in self.gestos],q)-1
            gesto=self.gestos[idx][1] if idx>=0 else 'repouso'
            anterior=self.gestos[idx-1][1] if idx>0 else gesto
            mistura=min(1,(q-self.gestos[idx][0]+1)/7) if idx>0 else 1
            alvos={}
            for de,ate,mao,id_alvo,(ox,oy) in self.toques:
                distancia=max(0,de-q,q-ate)
                if distancia<7:
                    ax,ay,_=posicoes[id_alvo]
                    peso=1-distancia/7
                    if mao not in alvos or alvos[mao][2]<peso:
                        alvos[mao]=((ax+ox-x)/(self.frente*s),(ay+oy-y)/s,peso)
            olhar=self.olhar.valor(q)[0]
            if tipo=='ator':
                arte.boneco(c,p,self.papel,t,gesto,anterior,mistura,olhar,alvos,self.fase)
            else:
                expressao = self.expressao or {'surpresa':'happy_eyes','pensar':'focused'}.get(gesto,'neutral')
                escala = 0.58
                pontos = {mao: (x/escala,y/escala) for mao,(x,y,_) in alvos.items()}
                pesos = {mao: peso for mao,(_,_,peso) in alvos.items()}
                arte.draw_puppet_30(c,0,0,scale=escala,t=t,archetype=self.papel,
                                    world='cream' if p is arte.PALETAS['creme'] else 'kraft',
                                    pose=POSE_ELENCO[gesto],expression=expressao,walk_phase=t*8,look_dir=(olhar,0),
                                    prop_l=self.prop_esq,prop_r=self.prop_dir,high_vis_vest=self.colete,
                                    ik_hand_l=pontos.get('esq'),ik_hand_r=pontos.get('dir'),
                                    pose_anterior=POSE_ELENCO[anterior],peso_pose=mistura,
                                    peso_ik_l=pesos.get('esq',0),peso_ik_r=pesos.get('dir',0))
        elif tipo=='imagem':
            c.set_source_surface(self.sprite,-self.sprite.get_width()/2,-self.sprite.get_height())
            c.paint()
        else:
            arte.objeto(c,tipo,p,self.valor.valor(q)[0],self.rotulo)
        if opac<.999:
            c.pop_group_to_source()
            c.paint_with_alpha(max(0,min(1,opac)))
        c.restore()


class Cena:
    def __init__(self,d,inicio,fim,marcas,tempo,base,exposicao):
        self.nome=d['id']
        self.mundo=d['mundo']
        self.inicio=inicio
        self.duracao=fim-inicio
        self.exposicao=exposicao
        self.ancoras={0}
        self.deixas_faladas=set()
        self.fps=float(tempo.fps)
        if self.mundo not in arte.PALETAS:
            raise ValueError(f'{self.nome}: escolha creme ou kraft.')
        self.p=arte.PALETAS[self.mundo]
        self.entrada=d.get('entrada','corte')
        if self.entrada not in ('corte','folha'):
            raise ValueError(f'{self.nome}: entrada desconhecida.')
        def chave(v):
            if isinstance(v,str) and v.startswith('@'):
                termo,sep,n=v[1:].partition('#')
                ocorrencia=int(n) if sep else 1
                termos=marcas.get(termo.casefold(),[])
                if not 1<=ocorrencia<=len(termos):
                    raise ValueError(f'{self.nome}: a deixa {v} não existe nesta fala.')
                indice=termos[ocorrencia-1]-inicio
                self.deixas_faladas.add(indice)
            else:
                prop=numero(v)
                if not 0<=prop<=1:
                    raise ValueError(f'{self.nome}: o instante {v} deve estar entre 0 e 1.')
                indice=round(prop*(self.duracao-1))
            if not 0<=indice<self.duracao:
                raise ValueError(f'{self.nome}: deixa fora do plano.')
            self.ancoras.add(indice)
            return indice
        self.camera=Trilha(d.get('camera'),(480,270,1),chave)
        if any(z<=0 for _,_,z in self.camera.valores):
            raise ValueError('Zoom de câmera precisa ser positivo.')
        self.elementos=[Elemento(e,chave,base) for e in d['elementos']]
        if not self.elementos or len({e.id for e in self.elementos})!=len(self.elementos):
            raise ValueError(f'{self.nome}: elementos vazios ou IDs repetidos.')
        por_id={e.id:e for e in self.elementos}
        for e in self.elementos:
            for _,_,_,alvo,_ in e.toques:
                if alvo not in por_id or por_id[alvo].tela!=e.tela:
                    raise ValueError(f'{e.id}: alvo {alvo} ausente ou em outro espaço de câmera.')
        self.ancoras=sorted(self.ancoras)

    def desenho_atual(self,q):
        ancora=self.ancoras[bisect_right(self.ancoras,q)-1]
        return ancora + (q-ancora)//self.exposicao*self.exposicao

    def desenhar(self,c,q):
        q=self.desenho_atual(q)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.set_source_surface(arte.papel(self.mundo),0,0)
        c.paint()
        cx,cy,zoom=self.camera.valor(q)
        pos={e.id:e.pos.valor(q) for e in self.elementos}
        t=(self.inicio+q)/self.fps
        c.save()
        c.translate(480,270)
        c.scale(zoom,zoom)
        c.translate(-cx,-cy)
        for e in self.elementos:
            if not e.tela:
                e.desenhar(c,self.p,q,t,pos)
        c.restore()
        for e in self.elementos:
            if e.tela:
                e.desenhar(c,self.p,q,t,pos)


def virar_folha(c,anterior,atual,q,n):
    anterior.desenhar(c,anterior.duracao-1)
    u=q/max(1,n-1)
    u=u*u*(3-2*u)
    x=-115+1200*u
    p=atual.p
    c.save()
    c.move_to(-140,-10)
    c.line_to(x-35,-10)
    c.line_to(x+64,550)
    c.line_to(-140,550)
    c.close_path()
    c.clip()
    atual.desenhar(c,q)
    c.restore()
    arte.forma(c,[(x-43,-4),(x-32,-4),(x+68,544),(x+47,544)],p['claro'],p['medio'],1.4)
    hy=215+32*u
    hx=x+5
    # Manga e pinça acompanham a borda inclinada até fora do quadro.
    arte.forma(c,[(hx+15,hy+20),(hx+40,hy+10),(hx+295,545),(hx+233,545)],p['tinta'])
    arte.forma(c,[(hx+14,hy+20),(hx+36,hy+5),(hx+46,hy+17),(hx+23,hy+32)],p['pele'],p['tinta'],2)
    arte.forma(c,[(hx+16,hy+20),(hx+6,hy+15,hx-3,hy+7,hx-4,hy+2),
               (hx-9,hy-8,hx-12,hy-15,hx-7,hy-16),(hx-3,hy-17,hx+2,hy-6,hx+5,hy-3),
               (hx+1,hy-18,hx+4,hy-21,hx+8,hy-17),(hx+12,hy-22,hx+17,hy-16,hx+19,hy-13),
               (hx+24,hy-15,hx+28,hy-10,hx+30,hy-4),(hx+35,hy+5),(hx+16,hy+20)],p['pele'],p['tinta'],2)


def pintor(cenas,tempo):
    indices=[c.inicio for c in cenas]
    superficie=cairo.ImageSurface(cairo.FORMAT_RGB24,tempo.largura,tempo.altura)
    ultimo=None
    def pintar(quadro):
        nonlocal ultimo
        idx=bisect_right(indices,quadro)-1
        cena=cenas[idx]
        q=cena.desenho_atual(quadro-cena.inicio)
        if (idx,q)==ultimo:
            return superficie
        ctx=cairo.Context(superficie)
        ctx.scale(tempo.largura/960,tempo.altura/540)
        duracao_folha=min(cena.duracao,round(cena.fps*.46))
        if idx>0 and cena.entrada=='folha' and q<duracao_folha:
            virar_folha(ctx,cenas[idx-1],cena,q,duracao_folha)
        else:
            cena.desenhar(ctx,q)
        superficie.flush()
        ultimo=(idx,q)
        return superficie
    return pintar
