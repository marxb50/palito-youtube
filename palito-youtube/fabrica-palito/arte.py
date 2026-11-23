"""Ilustrações originais em coordenadas de palco. Pés e objetos têm uma âncora editável."""
from functools import lru_cache
from math import sin, cos, pi

import cairo
from puppet_30 import draw_puppet_30, solve_2bone_ik
from scenes_and_props import (
    create_paper_background,
    draw_detailed_gas_station,
    draw_detailed_sedan_car,
    draw_office_lobby_environment,
    draw_puzzle_grid_2x2,
)
from stickman_engine import (
    draw_vault_shield,
    draw_fii_building,
    draw_money_bundle,
    draw_badge_card,
    draw_curved_banner_text,
)


def rgb(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def paleta(*cores):
    nomes = ('tinta', 'papel', 'pele', 'sombra', 'medio', 'claro', 'acento', 'ouro', 'salvia')
    return dict(zip(nomes, map(rgb, cores)))


PALETAS = {
    'creme': paleta('13535B', 'F5EDD6', 'FFFAE9', '23484B', '54858A', 'B1CBC0', 'C8734E', 'E8B858', '819D86'),
    'kraft': paleta('4A392F', 'C7B59C', 'F6E6CF', '59443A', '94735B', 'D9C5A7', 'AB644A', 'D9AC62', '85947A')
}


def cor(c, tinta, alpha=1):
    c.set_source_rgba(*tinta, alpha)


def forma(c, pontos, recheio=None, tinta=None, esp=2, fechar=True):
    c.new_path()
    c.move_to(*pontos[0])
    for p in pontos[1:]:
        if len(p) == 2:
            c.line_to(*p)
        else:
            c.curve_to(*p)
    if fechar:
        c.close_path()
    if recheio:
        cor(c, recheio)
        c.fill_preserve()
    if tinta:
        cor(c, tinta)
        c.set_line_width(esp)
        c.stroke()
    else:
        c.new_path()


def linha(c, pontos, tinta, esp=2):
    forma(c, pontos, tinta=tinta, esp=esp, fechar=False)


def oval(c, x, y, rx, ry, recheio, tinta=None, esp=2):
    c.save()
    c.translate(x, y)
    c.scale(rx, ry)
    c.new_path()
    c.arc(0, 0, 1, 0, 2*pi)
    c.restore()
    if recheio:
        cor(c, recheio)
        c.fill_preserve()
    if tinta:
        cor(c, tinta)
        c.set_line_width(esp)
        c.stroke()
    else:
        c.new_path()


def sombra(c, x, y, raio, p):
    c.save()
    c.translate(x, y)
    c.scale(raio, raio * .107)
    grad = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    grad.add_color_stop_rgba(0, *p['sombra'], .17)
    grad.add_color_stop_rgba(1, *p['sombra'], 0)
    c.set_source(grad)
    c.arc(0, 0, 1, 0, 2*pi)
    c.fill()
    c.restore()


def legenda(c, texto, x, y, tamanho, tinta):
    c.select_font_face('DejaVu Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(tamanho)
    ext = c.text_extents(texto)
    c.move_to(x - ext.width / 2 - ext.x_bearing, y)
    cor(c, tinta)
    c.show_text(texto)


@lru_cache(maxsize=2)
def papel(mundo):
    return create_paper_background(960, 540, 'cream' if mundo == 'creme' else 'kraft')


@lru_cache(maxsize=32)
def imagem(caminho):
    return cairo.ImageSurface.create_from_png(str(caminho))


PAPEIS = ('bia', 'lia', 'atendente', 'padeiro', 'cliente', 'rapaz', 'guia')
GESTOS = {'repouso', 'abrir', 'indicar', 'pensar', 'andar', 'receber', 'surpresa'}


def sapato(c, x, y, p):
    forma(c, [(x-5,y-3),(x-1,y-5,x+3,y-5,x+6,y-4),
              (x+10,y-3,x+14,y-2,x+14,y),(x-5,y)], p['tinta'])


def braco(c, lado, alvo, p):
    sx, sy = lado*16, -123
    tx, ty = alvo
    ex, ey = solve_2bone_ik(sx, sy, tx, ty, max_reach=33, bend_sign=-lado if ty-sy > 18 else lado)
    linha(c, [(sx,sy),(sx+.94*(ex-sx),sy+.94*(ey-sy),
                         tx+.91*(ex-tx),ty+.91*(ey-ty),tx,ty)], p['tinta'], 3.7)
    oval(c, tx, ty, 2.3, 2.1, p['tinta'])


def boneco(c, p, papel_ator, t, gesto, anterior, mistura, dir_olho, alvos, fase):
    i, a, pele = p['tinta'], p['acento'], p['pele']
    guia = papel_ator in ('guia', 'bia')
    servico = papel_ator in ('atendente', 'padeiro')
    anda = gesto == 'andar'
    passo = sin(t*8 + fase) if anda else 0
    respira = sin(t*2.3+fase)
    sobe = -abs(passo)*3 + respira*.55
    quadril = -75+sobe
    for lado in (-1,1):
        pe = lado*12 + lado*passo*17
        altura = -max(0,lado*passo)*5
        linha(c, [(lado*11,quadril),(lado*12,quadril+19,pe-6,-24+altura,pe,altura-3)], i, 3.4)
        sapato(c, pe, altura, p)
    c.save()
    c.translate(0, sobe)
    mexe = 1.4*sin(t*2+fase)
    alvos_padrao = {
        'repouso': ((-24,-79),(26,-80)), 'abrir': ((-57,-118+mexe),(56,-129-mexe)),
        'indicar': ((-22,-78),(61,-136+mexe)), 'pensar': ((-20,-92),(13,-143)),
        'receber': ((-27,-87),(54,-106+mexe)), 'surpresa': ((-39,-143),(44,-149)),
        'andar': ((-22+passo*14,-80),(22-passo*14,-80))
    }
    maos = [tuple(a + (b-a)*mistura for a,b in zip(inicial,final))
            for inicial,final in zip(alvos_padrao[anterior],alvos_padrao[gesto])]
    for k, (tx,ty,peso) in alvos.items():
        idx = 0 if k == 'esq' else 1
        mx,my = maos[idx]
        maos[idx] = (mx+(tx-mx)*peso,my+(ty-sobe-my)*peso)
    braco(c,-1,maos[0],p)
    roupa = p['medio'] if papel_ator in ('lia','rapaz') else i
    if servico:
        roupa = p['pele']
    if papel_ator == 'cliente':
        roupa = p['salvia']
    forma(c,[(-19,-122),(-17,-133,13,-133,19,-120),(23,-105,19,-83,19,-74),
             (8,-68,-7,-70,-18,-76),(-21,-89,-22,-112,-19,-122)],roupa,i,2.2)
    if guia:
        forma(c,[(-12,-127),(-1,-119),(12,-127),(5,-117),(-4,-117)],p['ouro'])
        forma(c,[(5,-119),(15,-114),(12,-105),(1,-115)], a, i, .9)
        linha(c,[(-11,-82),(-5,-80,2,-79,10,-81)],p['medio'],1.5)
    elif servico:
        forma(c,[(-15,-126),(-11,-126),(-9,-112),(9,-112),(12,-126),(16,-125),
                  (14,-104),(18,-76),(-17,-76),(-14,-103)],p['salvia'],i,1.3)
        forma(c,[(-8,-96),(8,-96),(7,-87,0,-85,-7,-89)],p['claro'],i,1)
    elif papel_ator == 'lia':
        for y in (-112,-105,-98):
            linha(c,[(-19,y),(0,y+2,6,y+1,19,y)],p['claro'],2.1)
    else:
        forma(c,[(-9,-127),(0,-118),(11,-127),(6,-117),(0,-114)],p['papel'])
    braco(c,1,maos[1],p)
    c.translate(0,-159)
    c.rotate((-.065 if gesto == 'pensar' else .02) + .023*sin(t*1.55+fase))
    if guia:
        for x,y,r in [(-21,-15,8),(-24,-22,7),(-17,-26,7),(-12,-22,7)]:
            oval(c,x,y,r,r,i)
        linha(c,[(-24,-14),(-18,-19,-16,-20,-12,-20)],p['ouro'],2)
    if papel_ator == 'lia':
        forma(c,[(-16,-11),(-13,-25,21,-23,20,-3),(19,5,21,16,25,21),
                 (10,25,-14,23,-22,14)],i)
    forma(c,[(-16,-7),(-16,-25,14,-28,19,-10),(24,1,20,18,9,24),
             (2,29,-7,22,-12,15),(-17,7,-17,0,-16,-7)],pele,i,2.4)
    oval(c,-14,4,3.9,5.5,pele,i,1.3)
    if guia or papel_ator in ('lia','rapaz'):
        forma(c,[(-17,5),(-23,-12,-17,-25,-3,-25),(6,-27,20,-23,23,-14),
                 (17,-10,12,-9,6,-12),(0,-4,-6,-2,-10,-1),(-12,6),(-14,0)],i)
        if guia:
            oval(c,-13,11,2.2,2.6,p['ouro'],i,.8)
            linha(c,[(-13,-15),(-8,-19,-4,-20,1,-20)],p['medio'],1.2)
    if servico:
        forma(c,[(-18,-10),(-22,-16,-22,-23,-15,-25),(-14,-33,-4,-34,0,-30),
                 (7,-34,17,-30,17,-25),(24,-24,23,-15,18,-11)],p['pele'],i,1.8)
        forma(c,[(-18,-13),(18,-15),(18,-9),(-16,-6)],p['claro'],i,1.3)
    if papel_ator == 'cliente':
        forma(c,[(-20,-10),(-25,-23,-4,-30,9,-23),(16,-21,20,-17,18,-14),
                 (27,-13),(24,-10),(-17,-7)],p['medio'],i,1.7)
    if papel_ator == 'lia':
        forma(c,[(-17,-16),(-8,-27,6,-28,17,-19),(19,-14),(-20,-9)],p['acento'],i,1.3)
    pisca = ((t+fase) % 3.45) < .13
    for ex in (-3,11):
        if pisca:
            linha(c,[(ex-2,6),(ex+2,6)],i,1.4)
        else:
            oval(c,ex+dir_olho,5,1.6,2.4,i)
        dy = -2.3 if gesto in ('pensar','surpresa') and ex>0 else 0
        linha(c,[(ex-3,-1+dy),(ex,-2+dy,ex+1,-2+dy,ex+3,-1.4+dy)],i,1.5)
        if papel_ator == 'cliente':
            oval(c,ex,5,5.3,5.2,None,i,1.1)
    if papel_ator == 'cliente':
        linha(c,[(2,4),(6,4)],i,1)
    linha(c,[(6,7),(7,11),(5,12)],i,1.2)
    c.restore()


def trigo(c,x,y,s,p):
    c.save()
    c.translate(x,y)
    c.scale(s,s)
    linha(c,[(0,2),(-1,-8,1,-21,4,-31)],p['tinta'],1.4)
    for k in range(3):
        yy=-5-k*7
        forma(c,[(1,yy),(-5,yy-1,-6,yy-8,-6,yy-10),(0,yy-6,1,yy-3,1,yy)],p['ouro'],p['tinta'],.9)
        forma(c,[(1,yy-2),(7,yy-5,9,yy-9,9,yy-12),(4,yy-10,1,yy-6,1,yy-2)],p['ouro'],p['tinta'],.9)
    c.restore()


def pao(c,x,y,s,p):
    c.save()
    c.translate(x,y)
    c.scale(s,s)
    forma(c,[(-30,-4),(-34,-14,-25,-25,-8,-29),(7,-35,25,-32,31,-22),
             (36,-12,21,-4,4,-1),(-12,2,-25,1,-30,-4)],p['ouro'],p['tinta'],2.2)
    for a,b in [(-16,-19),(-3,-24),(10,-25)]:
        linha(c,[(a,b),(a+4,b+1,a+5,b+4,a+5,b+8)],p['pele'],2.8)
    c.restore()


def saco(c,x,y,s,p):
    c.save()
    c.translate(x,y)
    c.scale(s,s)
    i=p['tinta']
    forma(c,[(-19,-1),(-23,-49),(-18,-54),(-13,-51),(-8,-55),(-3,-52),(2,-56),
             (7,-52),(14,-56),(18,-52),(22,-54),(22,-9),(18,0)],p['ouro'],i,2)
    forma(c,[(13,-51),(22,-54),(22,-9),(18,0),(13,-4)],p['medio'],i,1)
    linha(c,[(-18,-7),(-2,-5,7,-5,13,-6)],i,.9)
    trigo(c,-2,-12,.78,p)
    c.restore()


def vitrine(c,p):
    i=p['medio']
    forma(c,[(-162,0),(-162,-110),(-162,-210,162,-210,162,-110),(162,0)],p['claro'],i,2.2)
    forma(c,[(-153,-7),(-153,-109),(-152,-197,152,-197,153,-109),(153,-7)],p['papel'],i,1.6)
    linha(c,[(-151,-100),(150,-100)],i,1.5)
    for x in (-83,0,83):
        linha(c,[(x,-6),(x,-164 if x else -176)],i,1.8)
    for x,y in [(-129,-33),(-120,-37),(80,-120),(90,-117)]:
        linha(c,[(x,y),(x+18,y-20)],p['claro'],2)
    forma(c,[(-168,-5),(169,-5),(171,2),(-170,2)],p['claro'],i,1.4)


def fornada(c,p,modelo):
    vitrine(c,p)
    # A mesma estante comporta pães redondos ou baguetes. O fundo usa menos contraste que o balcão.
    fundo={**p,'tinta':p['medio'],'ouro':tuple((a+b)/2 for a,b in zip(p['ouro'],p['papel']))}
    for x in (-120,-85,-50,42,77,112):
        c.save()
        c.translate(x, -68 if modelo==1 else -72)
        c.rotate(-.34 if modelo==1 else -.84)
        c.scale(1,.85 if modelo==1 else .61)
        pao(c,0,0,.50,fundo)
        c.restore()
    forma(c,[(-146,-69),(147,-69),(143,-64),(-143,-64)],p['claro'],p['medio'],1.2)
    for x in (-108,-63,64,106):
        pao(c,x,-16,.53,fundo)
    forma(c,[(-145,-15),(147,-15),(144,-11),(-142,-11)],p['claro'],p['medio'],1.1)


def balcao(c,p,rotulo):
    i=p['tinta']
    forma(c,[(-97,-64),(85,-64),(86,-3),(-92,0)],p['medio'],i,2.8)
    forma(c,[(-87,-54),(74,-54),(74,-12),(-85,-10)],p['claro'],i,1.6)
    linha(c,[(-78,-47),(65,-47),(65,-18)],p['medio'],1.2)
    for x,y in [(-78,-18),(-78,-46),(66,-46),(66,-18)]:
        oval(c,x,y,1.4,1.4,i)
    forma(c,[(-105,-68),(-95,-76),(85,-76),(95,-69),(95,-63),(-105,-62)],p['pele'],i,2.6)
    forma(c,[(40,-77),(40,-85),(48,-89),(47,-103),(69,-102),(71,-86),(77,-83),
             (77,-77)],p['medio'],i,1.9)
    forma(c,[(51,-100),(66,-99),(66,-93),(51,-94)],p['claro'],i,1)
    for x in (48,54,60,66):
        linha(c,[(x,-83),(x+2,-83)],p['pele'],1.2)
    if rotulo:
        oval(c,-8,-34,14,14,p['pele'],i,1.3)
        legenda(c,rotulo,-8,-29,14,i)


def pacoteira(c,p,v):
    # Âncora no centro da borda superior da lista. O papel cresce abaixo da mão.
    comprimento=18+105*max(0,min(1,v))
    i=p['tinta']
    forma(c,[(-13,0),(20,0),(22,comprimento-6),(18,comprimento-2),(13,comprimento-5),
             (8,comprimento),(2,comprimento-4),(-3,comprimento-1),(-10,comprimento-4)],p['pele'],i,1.8)
    for n in range(6):
        y=11+n*15
        if y+5 < comprimento:
            linha(c,[(-6,y),(-4,y+2),(-1,y-2)],p['salvia'],1.7)
            linha(c,[(3,y),(14-(n%3)*2,y)],p['medio'],1.4)


def objeto(c,tipo,p,valor,rotulo):
    i=p['tinta']
    if tipo=='vitrine':
        vitrine(c,p)
    elif tipo=='fornada':
        fornada(c,p,1 if valor<1.5 else 2)
    elif tipo=='balcao':
        balcao(c,p,rotulo)
    elif tipo=='pao':
        pao(c,0,0,1,p)
    elif tipo=='saco':
        saco(c,0,0,1,p)
    elif tipo=='trigo':
        trigo(c,0,0,1,p)
    elif tipo=='lista':
        pacoteira(c,p,valor)
    elif tipo=='bandeja':
        forma(c,[(-112,-6),(-102,-15),(100,-15),(112,-8),(107,1),(-106,2)],p['claro'],i,2)
        linha(c,[(-103,-5),(103,-7)],p['medio'],1.2)
    elif tipo=='pacotes':
        for j in range(6):
            u=max(0,min(1,valor-j))
            if u:
                x=(j%3-1)*48
                y=-(j//3)*56-15*sin(pi*u)
                saco(c,x,y,max(.02,u),p)
    elif tipo=='ficha':
        forma(c,[(-27,-49),(25,-49),(27,0),(-27,0)],p['pele'],i,2)
        forma(c,[(-27,-50),(25,-50),(25,-39),(-27,-39)],p['acento'],i,1.3)
        legenda(c,rotulo,0,-10,27,i)
        linha(c,[(-20,-6),(19,-6)],p['medio'],1)
    elif tipo=='relogio':
        x,y=0,-36
        oval(c,x,y,37,37,p['claro'],i,2.8)
        oval(c,x,y,31,31,p['pele'],i,1.4)
        for n in range(12):
            ang=2*pi*n/12
            linha(c,[(24*sin(ang),y-24*cos(ang)),(27*sin(ang),y-27*cos(ang))],i,1.4)
        ang=valor*2*pi
        linha(c,[(0,y),(18*sin(ang/12+1.65),y-18*cos(ang/12+1.65))],i,3)
        linha(c,[(0,y),(24*sin(ang),y-24*cos(ang))],p['acento'],2.3)
        oval(c,0,y,3,3,i)
    elif tipo in ('livro','caixa'):
        altura=19 if tipo=='livro' else 48
        forma(c,[(-35,-altura),(21,-altura-8),(36,-altura),(36,-7),(-21,2),(-35,-5)],p['salvia'],i,2)
        forma(c,[(-35,-altura),(-21,-altura+7),(36,-altura)],None,i,1.3,False)
        linha(c,[(-21,-altura+7),(-21,1)],i,1.2)
        if tipo=='caixa':
            forma(c,[(-14,-altura-3),(-4,-altura-4),(11,-altura+2),(1,-altura+4)],p['ouro'])
            if rotulo:
                forma(c,[(-12,-30),(29,-36),(29,-19),(-12,-13)],p['pele'],i,.9)
                c.save()
                c.translate(8,-21)
                c.rotate(-.13)
                legenda(c,rotulo,0,0,7.7,i)
                c.restore()
    elif tipo=='moeda':
        oval(c,0,-17,18,18,p['ouro'],i,2)
        oval(c,0,-17,13,13,None,i,1)
        legenda(c,rotulo or '1',0,-12,14,i)
    elif tipo=='posto':
        c.save()
        c.scale(0.5, 0.5)
        draw_detailed_gas_station(c, 0, 0, scale=1.0, brand='green' if rotulo=='verde' else 'red', is_closed=(valor < 0.5), t=valor)
        c.restore()
    elif tipo=='sedan':
        c.save()
        c.scale(0.5, 0.5)
        draw_detailed_sedan_car(c, 0, 0, scale=1.0, driver_archetype=rotulo or '3_detective',
                                world='cream' if p is PALETAS['creme'] else 'kraft', t=valor)
        c.restore()
    elif tipo=='recepcao':
        c.save()
        c.scale(0.5, 0.5)
        draw_office_lobby_environment(c, t=valor)
        c.restore()
    elif tipo=='cofre':
        c.save()
        c.scale(0.5, 0.5)
        draw_vault_shield(c, 0, -145, scale=1.0, t=valor)
        c.restore()
    elif tipo=='predio':
        c.save()
        c.scale(0.5, 0.5)
        draw_fii_building(c, 0, 0, 235, 350, rotulo or 'EMPRESA', scale=1.0, accent=p['medio'])
        c.restore()
    elif tipo=='dinheiro':
        n = max(1, min(18, round(valor)))
        for idx in range(n):
            col = idx % 3
            row = idx // 3
            c.save()
            c.scale(0.5, 0.5)
            draw_money_bundle(c, (col - 1) * 78, -18 - row * 34, scale=0.88)
            c.restore()
    elif tipo=='boleto':
        forma(c, [(-22,-56),(22,-56),(22,0),(-22,0)], p['pele'], p['acento'], 2.2)
        forma(c, [(-21,-55),(21,-55),(21,-43),(-21,-43)], p['acento'])
        legenda(c, rotulo or 'BOLETO', 0, -46, 7.5, p['pele'])
        for ly in (-34, -26, -18):
            linha(c, [(-15, ly), (15, ly)], i, 1.3)
        for bx in range(-15, 16, 4):
            forma(c, [(bx, -12), (bx+1.8, -12), (bx+1.8, -3), (bx, -3)], i)
    elif tipo=='quebra_cabeca':
        c.save()
        c.scale(0.5, 0.5)
        draw_puzzle_grid_2x2(c, 0, -160, separation=max(0.0, 1.0 - valor), scale=1.0)
        c.restore()
    elif tipo=='arco_texto':
        c.save()
        c.scale(0.5, 0.5)
        draw_curved_banner_text(c, rotulo or 'CONCEITO', 0, 0, 185, progress=max(0.0, min(1.0, valor)), color=i, font_size=32)
        c.restore()
    elif tipo=='placa':
        partes = (rotulo or 'TÍTULO|SUBTÍTULO').split('|', 1)
        t1 = partes[0]
        t2 = partes[1] if len(partes) > 1 else ''
        c.save()
        c.scale(0.5, 0.5)
        draw_badge_card(c, 0, -60, 620, 118, t1, t2, scale=max(0.01, min(1.2, valor)), accent=p['acento'], ink=i)
        c.restore()
    elif tipo in ('gaveta','celular','regua','elo','bilhete','cozinha'):
        oficina(c,tipo,p,valor,rotulo)


OBJETOS = {'vitrine','fornada','balcao','pao','saco','trigo','lista','bandeja','pacotes',
           'ficha','relogio','livro','caixa','moeda','gaveta','celular','regua','elo','bilhete','cozinha',
           'posto','sedan','recepcao','cofre','predio','dinheiro','boleto','quebra_cabeca','arco_texto','placa'}


def elo(c,p,s=1):
    c.save()
    c.scale(s,s)
    c.rotate(-.52)
    for x in (-6,6):
        oval(c,x,0,9,5.6,None,p['tinta'],3.5)
        linha(c,[(x-5,-2),(x-3,-3)],p['claro'],1.1)
    c.restore()


def talher(c,p,tipo):
    tinta=p['tinta']
    linha(c,[(0,-3),(0,19)],tinta,2.9)
    if tipo%3==0:
        oval(c,0,-8,4.8,7.5,p['claro'],tinta,1.3)
    elif tipo%3==1:
        for x in (-3,0,3):
            linha(c,[(x,-16),(x,-6)],tinta,1.4)
        forma(c,[(-3,-7),(3,-7),(3,-3,2,-1,0,-1),(-2,-1,-3,-3,-3,-7)],p['claro'],tinta,1)
    else:
        forma(c,[(-1,-17),(5,-13,6,-2,1,4),(-1,4)],p['pele'],tinta,1.3)


def gaveta(c,p,u):
    i=p['tinta']
    forma(c,[(-70,-7),(-80,-67),(-62,-95),(72,-95),(81,-77),(69,-6),(48,4),(-51,5)],p['medio'],i,2.4)
    forma(c,[(-72,-66),(-56,-88),(62,-88),(71,-75),(58,-17),(-57,-16)],p['claro'],i,1.4)
    if u>.01:
        c.save()
        c.push_group()
        for xx in (-25,18):
            forma(c,[(xx,-86),(xx+4,-86),(xx+1,-18),(xx-5,-18)],p['ouro'],i,1)
        c.pop_group_to_source()
        c.paint_with_alpha(min(1,u*1.6))
        c.restore()
    bagunca=[(-27,-49,.96),(26,-46,-.25),(-9,-65,-1.15),(-31,-51,-.73),(2,-54,1.38),(25,-53,1.02)]
    em_ordem=[(-42,-52,0),(-32,-52,0),(-5,-57,0),(6,-57,0),(35,-53,0),(46,-53,0)]
    for j,(a,b) in enumerate(zip(bagunca,em_ordem)):
        x,y,angulo=[v+(w-v)*u for v,w in zip(a,b)]
        c.save()
        c.translate(x,y)
        c.rotate(angulo)
        talher(c,p,j//2)
        c.restore()
    forma(c,[(-73,-20),(62,-20),(70,-11),(67,0),(-55,9),(-73,3)],p['ouro'],i,2)
    forma(c,[(-13,-10),(13,-11),(12,-6),(-12,-5)],p['medio'],i,1.1)


def celular(c,p,tela,u):
    i=p['tinta']
    forma(c,[(-26,0),(-32,0,-34,-4,-34,-10),(-34,-103),(-34,-111,-30,-115,-22,-115),
             (24,-115),(31,-115,34,-112,34,-105),(34,-10),(34,-3,31,0,25,0)],p['medio'],i,2.3)
    forma(c,[(-27,-105),(27,-105),(27,-10),(-27,-10)],p['pele'],i,1.2)
    linha(c,[(-10,-110),(8,-110)],i,1.7)
    linha(c,[(-6,-5),(7,-5)],p['pele'],1.4)
    if tela=='painel':
        for j,v in enumerate((.42,.66,.52,.93)):
            x=-20+j*11
            alt=(13+28*v)*(.5+.5*u)
            forma(c,[(x,-37),(x,-37-alt),(x+7,-37-alt),(x+7,-37)],p['acento'] if j==3 else p['salvia'])
        linha(c,[(-22,-36),(23,-36)],i,1)
        for x,ganho in [(-11,.86),(12,.67)]:
            oval(c,x,-23,4.9,4.9,None,p['medio'],1.3)
            linha(c,[(x,-23),(x+3*ganho,-26)],i,1.3)
    elif tela=='cadastro':
        oval(c,0,-81,8,8,p['claro'],i,1.2)
        forma(c,[(-14,-62),(-13,-72,12,-73,14,-62)],p['claro'],i,1.2)
        linha(c,[(-17,-50),(17,-50)],p['medio'],1.5)
        linha(c,[(-17,-44),(9,-44)],p['medio'],1.5)
        oval(c,0,-26,8,8,p['salvia'] if u>=.5 else p['claro'],i,1.1)
        if u>=.5:
            linha(c,[(-4,-26),(-1,-23),(5,-30)],p['pele'],1.9)
    else:
        c.save()
        c.translate(0,-64)
        c.scale(.287,.287)
        gaveta(c,p,u if tela=='gravar' else 1)
        c.restore()
        if tela=='gravar':
            for x,sinal in [(-21,1),(21,-1)]:
                linha(c,[(x,-91),(x,-96),(x+6*sinal,-96)],i,1)
                linha(c,[(x,-49),(x,-44),(x+6*sinal,-44)],i,1)
            oval(c,0,-26,6.5,6.5,p['acento'],i,1)
        else:
            linha(c,[(-18,-54),(16,-54)],p['medio'],1.3)
            linha(c,[(-18,-49),(7,-49)],p['medio'],1.3)
            c.save()
            c.translate(0,-29)
            elo(c,p,.66)
            c.restore()


def oficina(c,tipo,p,v,rotulo):
    u=max(0,min(1,v))
    i=p['tinta']
    if tipo=='gaveta':
        gaveta(c,p,u)
    elif tipo=='celular':
        celular(c,p,rotulo,u)
    elif tipo=='regua':
        forma(c,[(-48,-10),(46,-10),(46,1),(-48,1)],p['ouro'],i,1.5)
        for j in range(19):
            x=-45+j*5
            linha(c,[(x,-9),(x,-4 if j%2==0 else -6)],i,.8)
    elif tipo=='elo':
        elo(c,p)
    elif tipo=='bilhete':
        forma(c,[(-64,-34),(60,-34),(65,-30),(64,-2),(-62,0)],p['pele'],i,1.6)
        forma(c,[(-64,-34),(-58,-34),(-57,-1),(-62,0)],p['acento'])
        legenda(c,rotulo,2,-14,8.8 if len(rotulo)>19 else 10.5,i)
    elif tipo=='cozinha':
        # Prateleira suspensa com cerâmica, azulejos e uma bancada de madeira.
        for j,(x,y) in enumerate([(-106,-112),(-77,-112),(-47,-112)]):
            alt=22+j*4
            forma(c,[(x-8,y),(x-10,y-3),(x-10,y-alt+4),(x-6,y-alt),(x+6,y-alt),
                     (x+10,y-alt+4),(x+10,y-3),(x+7,y)],p['pele'],p['medio'],1.3)
            linha(c,[(x-6,y-alt),(x+6,y-alt)],i,2.2)
            forma(c,[(x-8,y-8),(x+9,y-8),(x+9,y-6),(x-8,y-6)],p['acento'])
        forma(c,[(-124,-111),(-24,-111),(-23,-107),(-124,-107)],p['medio'],i,1)
        for x in (70,82,94):
            linha(c,[(x,-112),(x,-104)],p['medio'],1.2)
            c.save()
            c.translate(x,-93)
            c.scale(.49,.49)
            talher(c,p,(x//10)%3)
            c.restore()
        linha(c,[(64,-111),(101,-111)],p['medio'],1.8)
        forma(c,[(-136,-3),(135,-3),(127,3),(-136,3)],p['claro'],i,1.5)
        forma(c,[(-124,4),(122,4),(121,31),(-123,31)],p['medio'],i,1.6)
        for x in (-115,-31,53):
            forma(c,[(x,8),(x+60,8),(x+60,25),(x,25)],p['claro'],i,.85)
            linha(c,[(x+25,14),(x+36,14)],i,1.1)
