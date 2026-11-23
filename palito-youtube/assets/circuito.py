"""Cena editável. O dedo abaixa um botão com trava e o contato acende a lâmpada."""

import math

import cairo


TINTA = (0.059, 0.294, 0.345)
CLARO = (0.993, 0.977, 0.920)
AZUL = (0.34, 0.55, 0.58)
CORAL = (0.83, 0.35, 0.22)
OURO = (0.97, 0.73, 0.24)


def suave(valor):
    t = max(0.0, min(1.0, valor))
    return t * t * (3 - 2 * t)


def entre(a, b, p):
    return a + (b - a) * p


def preencher(c, cor, borda=3):
    c.set_source_rgb(*cor)
    if borda:
        c.fill_preserve()
        c.set_line_width(borda)
        c.set_source_rgb(*TINTA)
        c.stroke()
    else:
        c.fill()


def oval(c, x, y, rx, ry, cor, borda=3):
    c.save()
    c.translate(x, y)
    c.scale(rx, ry)
    c.arc(0, 0, 1, 0, math.tau)
    c.restore()
    preencher(c, cor, borda)


def linha(c, pontos, cor=TINTA, largura=4):
    c.move_to(*pontos[0])
    for ponto in pontos[1:]:
        c.line_to(*ponto)
    c.set_source_rgb(*cor)
    c.set_line_width(largura)
    c.stroke()


def placa(c, x, y, w, h, r, cor, borda=3):
    c.new_sub_path()
    for cx, cy, a in ((x+w-r, y+r, -90), (x+w-r, y+h-r, 0),
                      (x+r, y+h-r, 90), (x+r, y+r, 180)):
        c.arc(cx, cy, r, math.radians(a), math.radians(a+90))
    c.close_path()
    preencher(c, cor, borda)


def bancada(c, deslocamento, acesa):
    placa(c, 398, 360, 419, 26, 9, (0.77, 0.65, 0.46))
    for x in (425, 779):
        placa(c, x, 386, 15, 88, 4, AZUL)

    # Os três trechos formam um laço entre a pilha, o interruptor e a lâmpada.
    linha(c, [(446, 350), (424, 350), (424, 374), (566, 374), (566, 345)], largura=3)
    linha(c, [(498, 349), (510, 349), (510, 320), (692, 320), (692, 349)], largura=3)
    linha(c, [(634, 346), (634, 374), (752, 374), (752, 348)], largura=3)
    placa(c, 559, 329, 81, 28, 5, AZUL)
    placa(c, 626, 330, 12, 26, 3, CORAL, 0)
    linha(c, [(572, 343), (582, 343)], CLARO, 2)
    linha(c, [(612, 343), (622, 343)], CLARO, 2)
    linha(c, [(617, 338), (617, 348)], CLARO, 2)

    placa(c, 438, 338, 66, 21, 5, TINTA)
    placa(c, 447, 322 + 11 * deslocamento, 46, 16, 6, CORAL)
    if acesa:
        brilho = cairo.RadialGradient(721, 248, 8, 721, 248, 103)
        brilho.add_color_stop_rgba(0, *OURO, .71)
        brilho.add_color_stop_rgba(1, *OURO, 0)
        c.arc(721, 248, 103, 0, math.tau)
        c.set_source(brilho)
        c.fill()
        for graus in (-155, -120, -88, -55, -23):
            a = math.radians(graus)
            linha(c, [(721 + 64 * math.cos(a), 248 + 64 * math.sin(a)),
                      (721 + 79 * math.cos(a), 248 + 79 * math.sin(a))], CORAL, 4)
    c.move_to(704, 304)
    c.curve_to(704, 283, 679, 278, 679, 248)
    c.curve_to(679, 192, 763, 192, 763, 248)
    c.curve_to(763, 278, 738, 285, 738, 304)
    c.close_path()
    preencher(c, OURO if acesa else CLARO, 4)
    linha(c, [(713, 307), (710, 266), (720, 276), (732, 260), (728, 307)], largura=3)
    placa(c, 700, 303, 42, 31, 6, AZUL)
    linha(c, [(703, 313), (738, 309)], largura=2)
    linha(c, [(703, 322), (738, 318)], largura=2)
    placa(c, 685, 334, 73, 25, 6, TINTA)


def boneco(c, t, alcance, ponta, acesa):
    inclinar = 11 * alcance
    respirar = 1.4 * math.sin(t * 3)
    quadril = (317, 394)
    ombro = (340 + inclinar*.5, 317 + respirar)
    oval(c, 316, 473, 60, 6, (0.79, 0.80, 0.70), 0)
    for ponta_pe, lado in ((279, -1), (346, 1)):
        linha(c, [(quadril[0] + 18*lado, 390), (ponta_pe-6*lado, 433), (ponta_pe, 464)], largura=6)
        placa(c, ponta_pe-15, 458, 35, 14, 7, TINTA, 2)
    linha(c, [(292+inclinar, 314), (269, 345+respirar), (276, 376+respirar)], largura=5)
    for dx in (-6, 0, 6):
        linha(c, [(276, 376+respirar), (276+dx, 383+respirar)], largura=3)
    oval(c, 317+inclinar*.5, 349+respirar, 39, 54, AZUL, 5)
    # A ponta do indicador e a face superior do botão compartilham o ponto de contato.
    pulso = (ponta[0]-13, ponta[1]-5)
    dx, dy = pulso[0]-ombro[0], pulso[1]-ombro[1]
    distancia = math.hypot(dx, dy)
    altura = math.sqrt(max(0, 59**2 - (distancia/2)**2))
    cotovelo = ((pulso[0]+ombro[0])/2 - dy/distancia*altura,
                (pulso[1]+ombro[1])/2 + dx/distancia*altura)
    linha(c, [ombro, cotovelo, pulso, ponta], largura=5)
    linha(c, [pulso, (pulso[0]+6, pulso[1]+9)], largura=3)
    linha(c, [pulso, (pulso[0]-2, pulso[1]+10)], largura=3)
    c.save()
    c.translate(321+inclinar, 251+respirar)
    c.rotate(.045*alcance)
    oval(c, 0, 0, 46, 49, CLARO, 5)
    c.move_to(-46, -7)
    c.curve_to(-46, -56, 12, -71, 39, -33)
    c.line_to(55, -27)
    c.curve_to(30, -18, -13, -8, -46, -7)
    c.close_path()
    preencher(c, AZUL, 4)
    for x in (6, 29):
        oval(c, x + (2 if acesa else 0), 4 - (3 if acesa else 0), 3, 5, TINTA, 0)
        linha(c, [(x-6, -5 - 2*acesa), (x+4, -9 - 2*acesa)], largura=3)
    linha(c, [(21, 9), (25, 14), (21, 15)], largura=2)
    c.restore()


def montar(tempo):
    if tempo.palavras:
        corte = tempo.palavra("Observe")
        fecha = tempo.palavra("fecha", depois_de=corte)
    else:
        corte, fecha = tempo.total // 3, tempo.total * 3 // 5
    if not 0 < corte < fecha < tempo.total:
        raise ValueError("A cena do circuito precisa de tempo para mostrar o contato antes de fechar.")
    instante = float(fecha / tempo.fps)

    def desenhar(c, quadro, detalhe):
        t = float(quadro / tempo.fps)
        acesa = quadro >= fecha
        prepara = suave((t - instante + .85) / .69)
        pressao = suave((t - instante + .16) / .16)
        recuo = suave((t - instante - .48) / .55)
        alcance = prepara * (1 - recuo)
        ponta = (entre(378, 470, alcance), entre(354, 322 + 11*pressao, alcance))
        escala = min(tempo.largura/960, tempo.altura/540)
        c.translate((tempo.largura-960*escala)/2, (tempo.altura-540*escala)/2)
        c.scale(escala, escala)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.save()
        if detalhe:
            c.translate(480, 314)
            c.scale(1.3, 1.3)
            c.translate(-535, -315)
        linha(c, [(110, 475), (857, 475)], (0.71, 0.71, 0.60), 2)
        bancada(c, pressao, acesa)
        boneco(c, t, alcance, ponta, acesa)
        c.restore()
        c.set_source_rgb(*TINTA)
        c.select_font_face("Noto Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(30)
        c.move_to(72, 83)
        c.show_text("Circuito fechado" if acesa else "Circuito aberto")
        linha(c, [(74, 101), (149, 101)], CORAL, 4)

    def geral(c, local):
        desenhar(c, local, False)

    def detalhe(c, local):
        desenhar(c, corte + local, True)

    return [(0, geral), (corte, detalhe)]
