"""CENÁRIO INTERATIVO (v2.0, pedido do Gomes, tipo Injustice): coisas do cenário que reagem quando levam golpe.
Sem botão novo: acerte o objeto com um golpe (soco, chute, especial de perto, laser) e ele faz a parte dele
contra o OUTRO lutador. Se alguém for jogado contra o objeto, ele leva uma pancada a mais.
Cada objeto funciona uma vez e volta depois de RECARGA quadros (e no começo de cada round).

4 jeitos de reagir:
  ROLA   sai rolando pelo chão até o outro (dá pra defender, pular ou dar parry)
  ONDA   uma onda sai do objeto e deixa TONTO quem estiver no chão (pular escapa)
  CAI    uma coisa cai do alto em cima do outro (a sombra avisa; dá pra defender em pé ou sair de baixo)
  CHAO   algo corre pelo chão até o outro (água/lama derrubam, choque paralisa; pular escapa)

ONLINE: o estado só muda no passo(); o desenhar() só lê (o random usado é o global, que a partida
sorteia igual nos dois PCs a cada quadro). Nada de time.time().
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403

LIGADO_NO_TREINO = True   # o MODO TREINO também tem os objetos
RECARGA = 900             # quadros (15 s) até o objeto voltar depois de usado
BATIDA_DANO = 6           # quem é jogado contra o objeto leva isso a mais

# golpes dos objetos (mesmo formato dos golpes do golpes.py, pro Lutador.receber entender)
ROLANDO = dict(dano=10, nivel="medio", defe=14, emp=5, hit=20, derruba=True, voo=(5, 8), especial=True, proj=True)
BOMBA = dict(ROLANDO, dano=12, voo=(4, 11))
ONDA = dict(dano=3, nivel="medio", defe=10, emp=1, hit=10, paralisa=45, especial=True, proj=True, imbloqueavel=True)
CAINDO = dict(dano=10, nivel="alto", defe=16, emp=2, hit=22, derruba=True, voo=(2, 6), especial=True, proj=True)
ESCORREGA = dict(dano=6, nivel="baixo", defe=10, emp=3, hit=16, derruba=True, voo=(2, 5), especial=True, proj=True,
                 imbloqueavel=True)
CHOQUE = dict(dano=5, nivel="baixo", defe=10, emp=1, hit=10, paralisa=35, especial=True, proj=True, imbloqueavel=True)
BATIDA = dict(dano=BATIDA_DANO, nivel="medio", defe=0, emp=0, hit=0, especial=True, proj=True)


# =====================================================================
# desenhos (em coordenadas do mundo; x = meio do objeto, embaixo = CHAO)
# =====================================================================
def _lanterna(tela, x, t, usado):
    base = CHAO
    pedra, escura = (150, 146, 140), (96, 92, 88)
    pygame.draw.rect(tela, escura, (x - 26, base - 14, 52, 14))                 # pé
    pygame.draw.rect(tela, pedra, (x - 9, base - 74, 18, 60))                   # coluna
    pygame.draw.rect(tela, escura, (x - 22, base - 84, 44, 12))                 # prato
    pygame.draw.rect(tela, pedra, (x - 18, base - 116, 36, 32))                 # caixa da luz
    pygame.draw.rect(tela, (255, 200, 110) if not usado else (60, 50, 44), (x - 9, base - 108, 18, 16))  # luz
    if not usado:  # o "chapéu" e a bolinha de cima (é o que sai rolando)
        pygame.draw.polygon(tela, escura, [(x - 34, base - 116), (x + 34, base - 116), (x + 12, base - 136),
                                           (x - 12, base - 136)])
        pygame.draw.circle(tela, pedra, (x, base - 142), 9)


def _pedra(tela, x, y, giro):
    pygame.draw.circle(tela, (96, 92, 88), (int(x), int(y)), 22)
    pygame.draw.circle(tela, (150, 146, 140), (int(x), int(y)), 18)
    for k in range(3):
        a = giro + k * 2.1
        pygame.draw.line(tela, (90, 86, 82), (x, y), (x + math.cos(a) * 16, y + math.sin(a) * 16), 3)


def _tambor(tela, x, t, usado, deitado=None, cor=(170, 50, 36)):
    if usado and deitado is None:
        return
    if deitado is not None:  # rolando: é um círculo girando
        y = CHAO - 24
        pygame.draw.circle(tela, (40, 30, 30), (int(x), int(y)), 25)
        pygame.draw.circle(tela, cor, (int(x), int(y)), 22)
        pygame.draw.circle(tela, (40, 30, 30), (int(x), int(y)), 10, 3)
        for k in range(2):
            a = deitado + k * math.pi
            pygame.draw.line(tela, (230, 200, 60), (x + math.cos(a) * 11, y + math.sin(a) * 11),
                             (x + math.cos(a) * 21, y + math.sin(a) * 21), 4)
        return
    pygame.draw.rect(tela, cor, (x - 24, CHAO - 66, 48, 66), border_radius=5)
    for y in (CHAO - 50, CHAO - 18):
        pygame.draw.line(tela, (40, 30, 30), (x - 24, y), (x + 23, y), 3)
    pygame.draw.rect(tela, (230, 200, 60), (x - 12, CHAO - 42, 24, 16))        # rótulo amarelo
    pygame.draw.polygon(tela, (40, 30, 30), [(x, CHAO - 40), (x - 6, CHAO - 29), (x + 6, CHAO - 29)])
    pygame.draw.ellipse(tela, (90, 30, 24), (x - 24, CHAO - 72, 48, 12))


def _barril_polvora(tela, x, t, usado, deitado=None):
    if usado and deitado is None:
        return
    madeira, aro = (120, 82, 44), (60, 56, 52)
    if deitado is not None:
        y = CHAO - 24
        pygame.draw.circle(tela, aro, (int(x), int(y)), 25)
        pygame.draw.circle(tela, madeira, (int(x), int(y)), 22)
        pygame.draw.circle(tela, (40, 36, 34), (int(x), int(y)), 5)
        fx, fy = x + math.cos(deitado) * 22, y + math.sin(deitado) * 22  # o pavio aceso girando junto
        pygame.draw.circle(tela, (255, 220, 80) if (t // 3) % 2 else (255, 120, 40), (int(fx), int(fy)), 5)
        return
    pygame.draw.rect(tela, madeira, (x - 26, CHAO - 62, 52, 62), border_radius=10)
    for y in (CHAO - 50, CHAO - 12):
        pygame.draw.line(tela, aro, (x - 25, y), (x + 24, y), 4)
    for dx in (-12, 0, 12):
        pygame.draw.line(tela, (96, 64, 34), (x + dx, CHAO - 60), (x + dx, CHAO - 2), 1)
    pygame.draw.rect(tela, (230, 220, 200), (x - 15, CHAO - 40, 30, 16))
    pygame.draw.line(tela, (180, 40, 30), (x - 9, CHAO - 32), (x + 9, CHAO - 32), 3)  # "TNT"
    pygame.draw.line(tela, (40, 36, 34), (x + 8, CHAO - 64), (x + 16, CHAO - 80), 2)  # pavio
    if (t // 8) % 2:
        pygame.draw.circle(tela, (255, 220, 80), (x + 16, CHAO - 80), 3)


def _tronco(tela, x, t, usado, deitado=None):
    if usado and deitado is None:
        return
    casca, miolo = (86, 58, 34), (196, 160, 104)
    if deitado is not None:
        y = CHAO - 26
        pygame.draw.circle(tela, casca, (int(x), int(y)), 27)
        pygame.draw.circle(tela, miolo, (int(x), int(y)), 21)
        for r in (14, 7):
            pygame.draw.circle(tela, (160, 120, 74), (int(x), int(y)), r, 2)
        a = deitado
        pygame.draw.line(tela, (160, 120, 74), (x, y), (x + math.cos(a) * 20, y + math.sin(a) * 20), 2)
        return
    # tronco em pé (um toco alto com musgo)
    pygame.draw.rect(tela, casca, (x - 24, CHAO - 110, 48, 110))
    for dx in (-14, -2, 10):
        pygame.draw.line(tela, (64, 42, 24), (x + dx, CHAO - 106), (x + dx + 3, CHAO - 4), 2)
    pygame.draw.ellipse(tela, miolo, (x - 24, CHAO - 118, 48, 16))
    pygame.draw.ellipse(tela, (160, 120, 74), (x - 14, CHAO - 114, 28, 8), 2)
    pygame.draw.rect(tela, (70, 140, 60), (x - 24, CHAO - 40, 18, 12))  # musgo
    pygame.draw.rect(tela, (70, 140, 60), (x + 8, CHAO - 82, 16, 10))


def _gongo(tela, x, t, usado, treme=0):
    madeira = (110, 64, 34)
    pygame.draw.rect(tela, madeira, (x - 52, CHAO - 170, 10, 170))
    pygame.draw.rect(tela, madeira, (x + 42, CHAO - 170, 10, 170))
    pygame.draw.rect(tela, (140, 40, 30), (x - 60, CHAO - 180, 120, 14))
    dx = math.sin(t * 0.9) * treme * 0.4
    cy = CHAO - 100
    pygame.draw.line(tela, (60, 40, 30), (x - 20, CHAO - 166), (x - 12 + dx, cy - 32), 2)
    pygame.draw.line(tela, (60, 40, 30), (x + 20, CHAO - 166), (x + 12 + dx, cy - 32), 2)
    cor = (200, 160, 60) if not usado else (150, 120, 60)
    pygame.draw.circle(tela, (120, 90, 30), (int(x + dx), cy), 37)
    pygame.draw.circle(tela, cor, (int(x + dx), cy), 33)
    pygame.draw.circle(tela, (230, 200, 110), (int(x + dx), cy), 14)
    pygame.draw.circle(tela, (150, 110, 40), (int(x + dx), cy), 25, 2)


def _taiko(tela, x, t, usado, treme=0):
    dy = math.sin(t * 1.1) * treme * 0.3
    pygame.draw.line(tela, (80, 50, 30), (x - 30, CHAO), (x - 20, CHAO - 60), 6)  # suporte
    pygame.draw.line(tela, (80, 50, 30), (x + 30, CHAO), (x + 20, CHAO - 60), 6)
    corpo = pygame.Rect(x - 40, CHAO - 120 + dy, 80, 76)
    pygame.draw.ellipse(tela, (150, 40, 30), corpo)
    pygame.draw.ellipse(tela, (232, 216, 180) if not usado else (190, 170, 140), corpo.inflate(-30, -6))
    pygame.draw.ellipse(tela, (40, 24, 20), corpo.inflate(-30, -6), 2)
    for k in range(5):  # pregos
        a = k * math.tau / 5
        pygame.draw.circle(tela, (230, 200, 90), (int(corpo.centerx + math.cos(a) * 30),
                                                  int(corpo.centery + math.sin(a) * 34)), 2)
    pygame.draw.circle(tela, (40, 24, 20), corpo.center, 8)  # o tomoe no meio


def _cogumelo(tela, x, t, usado, treme=0):
    brilho = 0.5 + 0.5 * math.sin(t * 0.05)
    pygame.draw.rect(tela, (210, 200, 170), (x - 11, CHAO - 70, 22, 70), border_radius=6)
    chapeu = (60, 200 if not usado else 120, 180 if not usado else 120)
    cy = CHAO - 78 + math.sin(t * 0.9) * treme * 0.3
    pygame.draw.ellipse(tela, chapeu, (x - 46, cy - 34, 92, 46))
    pygame.draw.rect(tela, (20, 30, 30), (x - 46, cy - 4, 92, 6))
    if not usado:
        for dx, dy in ((-22, -18), (6, -26), (24, -12), (-4, -8)):
            pygame.draw.circle(tela, (170, 255, 230), (x + dx, int(cy + dy)), 4 + int(2 * brilho))


def _caldeirao(tela, x, t, usado):
    pygame.draw.polygon(tela, (60, 40, 30), [(x - 30, CHAO), (x - 20, CHAO - 20), (x + 20, CHAO - 20), (x + 30, CHAO)])
    for k in range(3):  # fogo
        fx = x - 18 + k * 18
        h = 14 + 6 * math.sin(t * 0.3 + k * 2)
        pygame.draw.polygon(tela, (255, 140, 40), [(fx - 7, CHAO - 2), (fx + 7, CHAO - 2), (fx, CHAO - 2 - h)])
    corpo = pygame.Rect(x - 40, CHAO - 82, 80, 64)
    pygame.draw.ellipse(tela, (40, 36, 44), corpo)
    pygame.draw.ellipse(tela, (70, 64, 76), corpo.inflate(-14, -16), 2)
    caldo = (160, 70, 220) if not usado else (90, 60, 110)
    pygame.draw.ellipse(tela, (30, 26, 34), (x - 40, CHAO - 90, 80, 18))
    pygame.draw.ellipse(tela, caldo, (x - 34, CHAO - 88, 68, 13))
    if not usado:
        for k in range(3):  # bolhas subindo
            u = (t * 1.5 + k * 33) % 100 / 100
            pygame.draw.circle(tela, (200, 140, 255), (int(x - 14 + k * 14), int(CHAO - 88 - u * 40)),
                               max(1, int(5 * (1 - u))), 1)


def _bolha(tela, x, y, t):
    pygame.draw.circle(tela, (110, 40, 170), (int(x), int(y)), 34)
    pygame.draw.circle(tela, (170, 80, 240), (int(x), int(y)), 30)
    pygame.draw.circle(tela, (230, 190, 255), (int(x - 10), int(y - 12)), 8)
    for k in range(4):
        a = t * 0.2 + k * math.tau / 4
        pygame.draw.circle(tela, (255, 230, 120), (int(x + math.cos(a) * 42), int(y + math.sin(a) * 42)), 3)


def _cacaniquel(tela, x, t, usado):
    pygame.draw.rect(tela, (90, 30, 40), (x - 32, CHAO - 130, 64, 130), border_radius=8)
    pygame.draw.rect(tela, (220, 180, 60), (x - 32, CHAO - 130, 64, 130), 3, border_radius=8)
    pygame.draw.rect(tela, (240, 236, 220), (x - 24, CHAO - 104, 48, 26))
    simbolos = "777" if not usado else "x-x"
    for i, s in enumerate(simbolos):  # os 3 rolinhos (o 7 é desenhado com 2 traços)
        sx = x - 16 + i * 16
        cor = (210, 30, 30) if s == "7" else (120, 120, 120)
        pygame.draw.line(tela, cor, (sx - 5, CHAO - 99), (sx + 5, CHAO - 99), 3)
        pygame.draw.line(tela, cor, (sx + 5, CHAO - 99), (sx - 2, CHAO - 83), 3)
    pygame.draw.line(tela, (180, 180, 190), (x + 32, CHAO - 100), (x + 44, CHAO - 136), 4)  # alavanca
    pygame.draw.circle(tela, (220, 30, 30), (x + 44, CHAO - 138), 7)
    luz = (255, 230, 120) if (t // 12) % 2 and not usado else (120, 90, 50)
    pygame.draw.rect(tela, luz, (x - 24, CHAO - 124, 48, 10), border_radius=4)
    pygame.draw.rect(tela, (40, 20, 24), (x - 18, CHAO - 50, 36, 10))  # saída das moedas


def _ficha(tela, x, y, giro, cor):
    w = max(6, int(abs(math.cos(giro)) * 30))
    r = pygame.Rect(0, 0, w, 30)
    r.center = (int(x), int(y))
    pygame.draw.ellipse(tela, cor, r)
    pygame.draw.ellipse(tela, (250, 250, 250), r.inflate(-max(2, w // 3), -10), 2)


def _vitoria_regia(tela, x, t, usado):
    for dx, r in ((-30, 26), (22, 20)):
        cy = CHAO - 4
        pygame.draw.ellipse(tela, (40, 110, 60), (x + dx - r, cy - 8, r * 2, 14))
        pygame.draw.ellipse(tela, (70, 160, 80), (x + dx - r + 3, cy - 7, r * 2 - 6, 10))
        pygame.draw.line(tela, (40, 110, 60), (x + dx, cy - 1), (x + dx + r - 4, cy - 4), 2)  # o cortezinho
    if not usado:  # a flor rosa
        fx, fy = x - 30, CHAO - 14 + math.sin(t * 0.05) * 2
        for k in range(5):
            a = k * math.tau / 5 - math.pi / 2
            pygame.draw.circle(tela, (240, 130, 170), (int(fx + math.cos(a) * 7), int(fy + math.sin(a) * 5)), 6)
        pygame.draw.circle(tela, (255, 220, 120), (int(fx), int(fy)), 4)
    # o cano de água (onde o golpe acerta): um bambu com água pingando
    pygame.draw.rect(tela, (120, 150, 70), (x + 40, CHAO - 120, 12, 120))
    for y in (CHAO - 90, CHAO - 50):
        pygame.draw.line(tela, (80, 110, 50), (x + 40, y), (x + 51, y), 2)
    if not usado:
        pygame.draw.rect(tela, (120, 150, 70), (x + 20, CHAO - 124, 32, 10))
        u = (t * 2) % 30
        pygame.draw.circle(tela, (140, 200, 230), (x + 22, CHAO - 112 + u), 3)


def _gerador(tela, x, t, usado):
    pygame.draw.rect(tela, (60, 70, 80), (x - 30, CHAO - 120, 60, 120), border_radius=4)
    pygame.draw.rect(tela, (30, 36, 40), (x - 30, CHAO - 120, 60, 120), 2, border_radius=4)
    for k in range(3):  # bobinas
        pygame.draw.rect(tela, (190, 120, 60), (x - 22 + k * 16, CHAO - 150, 12, 30))
        pygame.draw.line(tela, (230, 170, 90), (x - 22 + k * 16, CHAO - 140), (x - 10 + k * 16, CHAO - 140), 1)
    pygame.draw.rect(tela, (230, 200, 40), (x - 20, CHAO - 90, 40, 26))  # placa de perigo
    pygame.draw.lines(tela, (30, 30, 30), False, [(x + 2, CHAO - 87), (x - 6, CHAO - 77), (x + 4, CHAO - 77),
                                                  (x - 4, CHAO - 67)], 3)
    if not usado:
        luz = (120, 255, 140) if (t // 10) % 2 else (40, 120, 60)
        pygame.draw.circle(tela, luz, (x + 18, CHAO - 108), 5)
        if (t // 4) % 5 == 0:  # faisquinha entre as bobinas
            pygame.draw.line(tela, (180, 240, 255), (x - 16, CHAO - 152), (x + 14, CHAO - 152), 2)
    else:
        pygame.draw.circle(tela, (120, 40, 40), (x + 18, CHAO - 108), 5)


def _balde_lama(tela, x, t, usado):
    pygame.draw.polygon(tela, (110, 110, 120), [(x - 26, CHAO - 56), (x + 26, CHAO - 56), (x + 20, CHAO),
                                                (x - 20, CHAO)])
    pygame.draw.line(tela, (80, 80, 90), (x - 23, CHAO - 36), (x + 23, CHAO - 36), 3)
    pygame.draw.arc(tela, (80, 80, 90), (x - 26, CHAO - 84, 52, 56), 0, math.pi, 3)  # alça
    if not usado:
        pygame.draw.ellipse(tela, (110, 76, 40), (x - 26, CHAO - 62, 52, 12))
        pygame.draw.circle(tela, (110, 76, 40), (x + 18, CHAO - 54), 6)  # lama escorrendo pela borda
        pygame.draw.rect(tela, (110, 76, 40), (x + 15, CHAO - 54, 6, 16))
    # a plaquinha da vila do lado
    pygame.draw.rect(tela, (120, 90, 50), (x - 54, CHAO - 100, 6, 100))
    pygame.draw.rect(tela, (170, 130, 80), (x - 76, CHAO - 112, 50, 24))
    pygame.draw.circle(tela, (60, 140, 60), (x - 51, CHAO - 100), 7)  # carinha de sapo na placa


def _corda_palco(tela, x, t, usado):
    """TEATRO DE MÁGICA: a corda do cenário presa no gancho da coxia, com o saco de areia lá em cima."""
    pygame.draw.rect(tela, (70, 44, 30), (x - 6, CHAO - 150, 12, 150))           # poste da coxia
    pygame.draw.rect(tela, (110, 74, 44), (x - 18, CHAO - 96, 36, 8))            # o gancho (cunha)
    pygame.draw.circle(tela, (150, 110, 60), (x - 18, CHAO - 92), 5)
    pygame.draw.circle(tela, (150, 110, 60), (x + 18, CHAO - 92), 5)
    if not usado:
        pygame.draw.line(tela, (210, 190, 140), (x + 14, CHAO - 92), (x + 14, 0), 3)  # a corda subindo
        for y in range(CHAO - 88, CHAO - 50, 6):  # a corda enrolada no gancho
            pygame.draw.line(tela, (190, 170, 120), (x - 14, y), (x + 14, y + 3), 2)
        _saco(tela, x + 14, 60 + math.sin(t * 0.04) * 3)  # o saco lá em cima, balançando
    else:
        pygame.draw.line(tela, (210, 190, 140), (x + 14, CHAO - 92), (x + 30, CHAO - 70), 3)  # corda solta
    pygame.draw.rect(tela, (230, 200, 90), (x - 22, CHAO - 130, 44, 14), border_radius=3)  # plaquinha "PERIGO"
    pygame.draw.line(tela, (60, 30, 20), (x - 14, CHAO - 123), (x + 14, CHAO - 123), 2)


def _saco(tela, x, y):
    pygame.draw.polygon(tela, (170, 140, 96), [(x - 22, y - 14), (x + 22, y - 14), (x + 28, y + 26), (x - 28, y + 26)])
    pygame.draw.rect(tela, (120, 94, 60), (x - 24, y - 20, 48, 8), border_radius=3)  # a boca amarrada
    pygame.draw.line(tela, (210, 190, 140), (x, y - 20), (x, y - 40), 3)
    pygame.draw.line(tela, (130, 104, 66), (x - 12, y + 4), (x + 10, y + 4), 2)        # "AREIA"
    pygame.draw.line(tela, (130, 104, 66), (x - 8, y + 12), (x + 6, y + 12), 2)


def _coqueiro(tela, x, t, usado):
    """CERCADO DO DESERTO (casa do MAGNUS): o coqueiro do oásis, com os cocos lá em cima."""
    balanca = math.sin(t * 0.03) * 3
    pts = [(x + math.sin(k / 6) * 10 + balanca * k / 12, CHAO - k * 15) for k in range(12)]  # tronco curvinho
    for k in range(len(pts) - 1):
        pygame.draw.line(tela, (130, 92, 52), pts[k], pts[k + 1], 16 - k // 2)
        pygame.draw.line(tela, (96, 66, 36), (pts[k][0] - 6, pts[k][1] - 2), (pts[k][0] + 6, pts[k][1] + 2), 2)
    topo = pts[-1]
    for k in range(7):  # folhas
        a = -math.pi / 2 + (k - 3) * 0.55 + math.sin(t * 0.04 + k) * 0.06
        fim = (topo[0] + math.cos(a) * 64, topo[1] + math.sin(a) * 30 + 26)
        meio = (topo[0] + math.cos(a) * 34, topo[1] + math.sin(a) * 30 - 6)
        pygame.draw.lines(tela, (60, 140, 60), False, [topo, meio, fim], 7)
        pygame.draw.lines(tela, (90, 180, 80), False, [topo, meio, fim], 2)
    if not usado:
        for dx in (-9, 3, 13):  # os cocos
            pygame.draw.circle(tela, (110, 76, 40), (int(topo[0] + dx), int(topo[1] + 10)), 8)
            pygame.draw.circle(tela, (150, 110, 60), (int(topo[0] + dx - 2), int(topo[1] + 8)), 3)


def _cocos(tela, x, y):
    for dx, dy in ((-12, 0), (0, -10), (12, 2)):
        pygame.draw.circle(tela, (110, 76, 40), (int(x + dx), int(y + dy)), 10)
        pygame.draw.circle(tela, (150, 110, 60), (int(x + dx - 3), int(y + dy - 3)), 3)


def _boia_poste(tela, x, t, usado):
    """PRAIA DA ILHA (casa do SPHYRUS): o poste do salva-vidas com a boia pendurada."""
    pygame.draw.rect(tela, (150, 110, 70), (x - 6, CHAO - 150, 12, 150))           # poste de madeira
    pygame.draw.rect(tela, (120, 86, 52), (x - 20, CHAO - 150, 40, 10))
    pygame.draw.rect(tela, (230, 60, 50), (x - 18, CHAO - 176, 36, 18), border_radius=3)  # plaquinha vermelha
    pygame.draw.line(tela, BRANCO, (x - 8, CHAO - 167), (x + 8, CHAO - 167), 3)    # (a cruz do salva-vidas)
    pygame.draw.line(tela, BRANCO, (x, CHAO - 174), (x, CHAO - 160), 3)
    if not usado:
        _boia(tela, x, CHAO - 104 + math.sin(t * 0.05) * 2, 0.0)


def _boia(tela, x, y, giro):
    """A boia salva-vidas (vermelha e branca), girando quando rola."""
    for k in range(8):
        a0 = giro + k * math.tau / 8
        cor = (230, 50, 40) if k % 2 == 0 else (245, 245, 245)
        pts = [(x + math.cos(a0 + i * math.tau / 32) * 26, y + math.sin(a0 + i * math.tau / 32) * 26) for i in range(5)]
        pts += [(x + math.cos(a0 + i * math.tau / 32) * 13, y + math.sin(a0 + i * math.tau / 32) * 13) for i in range(4, -1, -1)]
        pygame.draw.polygon(tela, cor, pts)
    pygame.draw.circle(tela, (60, 30, 30), (int(x), int(y)), 26, 2)
    pygame.draw.circle(tela, (60, 30, 30), (int(x), int(y)), 13, 2)


def _cristal(tela, x, t, usado, treme=0):
    """CAVERNA DOS MORCEGOS (casa do NOCTURNUS): o CRISTAL ROXO gigante (bateu: estoura numa onda de som)."""
    x += treme
    if usado:
        for k in range(3):  # (sobraram só os tocos quebrados)
            pygame.draw.polygon(tela, (90, 50, 130), [(x - 20 + k * 16, CHAO), (x - 12 + k * 16, CHAO - 18), (x - 6 + k * 16, CHAO)])
        return
    brilha = 120 + int(60 * math.sin(t * 0.08))
    camada = pygame.Surface((160, 160), pygame.SRCALPHA)
    pygame.draw.circle(camada, (180, 100, 255, brilha // 3), (80, 80), 70)
    tela.blit(camada, (x - 80, CHAO - 150))
    for k, (dx, h, a) in enumerate(((-18, 80, -0.25), (0, 130, 0.0), (20, 96, 0.22), (-34, 50, -0.5), (34, 56, 0.5))):
        bx = x + dx
        c, s = math.cos(a), math.sin(a)
        pts = [(bx - 10, CHAO), (bx - 10 + s * h * 0.8, CHAO - c * h * 0.8), (bx + s * h, CHAO - c * h),
               (bx + 10 + s * h * 0.8, CHAO - c * h * 0.8), (bx + 10, CHAO)]
        pygame.draw.polygon(tela, (30, 16, 46), [(px, py + 2) for px, py in pts])
        pygame.draw.polygon(tela, (130, 66, 200), pts)
        pygame.draw.polygon(tela, (210, 170, 255), [pts[1], pts[2], ((pts[1][0] + pts[2][0]) / 2 + 4, CHAO - c * h * 0.4)])


def _pedra_runa(tela, x, t, usado, deitado=None):
    """FLORESTA ANTIGA (casa do SILVANUS): a PEDRA RÚNICA redonda com musgo (bateu: sai rolando, a runa acesa)."""
    if usado and deitado is None:
        return
    acesa = (140, 240, 160) if (t // 30) % 2 else (110, 210, 130)
    if deitado is not None:  # rolando: a roda de pedra girando
        y = CHAO - 26
        pygame.draw.circle(tela, (88, 92, 80), (int(x), int(y)), 27)
        pygame.draw.circle(tela, (128, 132, 116), (int(x), int(y)), 23)
        for k in range(3):
            a = deitado + k * 2.1
            pygame.draw.line(tela, acesa, (x, y), (x + math.cos(a) * 16, y + math.sin(a) * 16), 3)
        return
    # em pé: a pedra em cima de uma base, com musgo e a runa brilhando
    pygame.draw.rect(tela, (88, 92, 80), (x - 30, CHAO - 12, 60, 12), border_radius=3)
    pygame.draw.circle(tela, (88, 92, 80), (int(x), CHAO - 38), 27)
    pygame.draw.circle(tela, (128, 132, 116), (int(x), CHAO - 38), 23)
    pygame.draw.ellipse(tela, (70, 120, 52), (x - 22, CHAO - 66, 34, 12))
    pygame.draw.line(tela, acesa, (x, CHAO - 50), (x, CHAO - 26), 3)
    pygame.draw.line(tela, acesa, (x, CHAO - 42), (x + 8, CHAO - 50), 3)
    pygame.draw.line(tela, acesa, (x, CHAO - 36), (x - 8, CHAO - 44), 3)


def _bolota(tela, x, t, usado, deitado=None):
    """CAMPO GIGANTE (casa do KATCHADE): a BOLOTA gigante (o fruto do carvalho) — bateu: sai rolando."""
    if usado and deitado is None:
        return
    casca, escura, chapeu, chapeu_e = (176, 120, 60), (120, 78, 36), (140, 104, 64), (96, 70, 40)
    if deitado is not None:  # rolando: a bolota deitada girando
        y = CHAO - 24
        pygame.draw.circle(tela, escura, (int(x), int(y)), 25)
        pygame.draw.circle(tela, casca, (int(x), int(y)), 21)
        a = deitado
        pygame.draw.line(tela, chapeu_e, (x - math.cos(a) * 21, y - math.sin(a) * 21),
                         (x + math.cos(a) * 21, y + math.sin(a) * 21), 6)
        pygame.draw.circle(tela, (230, 200, 150), (int(x + math.cos(a + 1) * 10), int(y + math.sin(a + 1) * 10)), 4)
        return
    # em pé: a bolota com o chapeuzinho e o cabinho
    pygame.draw.ellipse(tela, escura, (x - 24, CHAO - 56, 48, 56))
    pygame.draw.ellipse(tela, casca, (x - 20, CHAO - 52, 40, 50))
    pygame.draw.ellipse(tela, (214, 160, 96), (x - 12, CHAO - 44, 10, 22))
    pygame.draw.ellipse(tela, chapeu_e, (x - 27, CHAO - 66, 54, 24))
    pygame.draw.ellipse(tela, chapeu, (x - 24, CHAO - 64, 48, 18))
    for k in range(5):
        pygame.draw.line(tela, chapeu_e, (x - 18 + k * 9, CHAO - 62), (x - 20 + k * 9, CHAO - 50), 2)
    pygame.draw.line(tela, escura, (x, CHAO - 64), (x + 4, CHAO - 76), 4)


def _boneco_palha(tela, x, t, usado, deitado=None):
    """MONTE KARASUMA (casa do INAZUMANEKO): o BONECO DE PALHA de treino (tomba e sai rolando)."""
    palha, palha_esc, corda, borda = (214, 182, 100), (160, 124, 60), (120, 60, 40), (60, 40, 20)
    if usado and deitado is None:
        pygame.draw.line(tela, (90, 60, 30), (x, CHAO), (x, CHAO - 30), 6)  # (sobrou só o toco do poste)
        return
    if deitado is not None:  # rolando (a palha enrolada vista de lado, girando)
        y = CHAO - 24
        pygame.draw.circle(tela, borda, (int(x), int(y)), 26)
        pygame.draw.circle(tela, palha, (int(x), int(y)), 23)
        for k in range(4):
            a = deitado + k * math.pi / 4
            pygame.draw.line(tela, palha_esc, (x - math.cos(a) * 22, y - math.sin(a) * 22), (x + math.cos(a) * 22, y + math.sin(a) * 22), 2)
        pygame.draw.circle(tela, corda, (int(x), int(y)), 23, 3)
        return
    pygame.draw.line(tela, (90, 60, 30), (x, CHAO), (x, CHAO - 150), 6)  # o poste
    corpo = pygame.Rect(x - 20, CHAO - 130, 40, 96)
    pygame.draw.rect(tela, borda, corpo.inflate(4, 4), border_radius=10)
    pygame.draw.rect(tela, palha, corpo, border_radius=10)
    for k in range(3):  # as amarras
        yy = corpo.y + 18 + k * 28
        pygame.draw.line(tela, corda, (corpo.x, yy), (corpo.right, yy), 4)
    for k in range(6):  # os fiapos de palha
        pygame.draw.line(tela, palha_esc, (corpo.x + 6 + k * 6, corpo.y + 4), (corpo.x + 4 + k * 6, corpo.bottom - 4), 1)
    pygame.draw.line(tela, borda, (corpo.x - 2, corpo.y + 30), (corpo.right + 2, corpo.y + 56), 2)  # um corte de espada
    pygame.draw.rect(tela, (90, 60, 30), (x - 26, CHAO - 104, 52, 6))  # os "braços" (a trave)


def _placa_avalanche(tela, x, t, usado):
    """MONTANHA NEVADA (casa do FRIGANTUS): a placa de PERIGO: AVALANCHE, com neve em cima."""
    pygame.draw.rect(tela, (110, 80, 50), (x - 5, CHAO - 130, 10, 130))           # o poste
    placa = [(x, CHAO - 178), (x + 38, CHAO - 116), (x - 38, CHAO - 116)]        # triângulo amarelo
    pygame.draw.polygon(tela, (240, 200, 40), placa)
    pygame.draw.polygon(tela, (30, 24, 20), placa, 3)
    pygame.draw.line(tela, (30, 24, 20), (x, CHAO - 160), (x, CHAO - 134), 4)     # o "!" de perigo
    pygame.draw.circle(tela, (30, 24, 20), (x, CHAO - 126), 3)
    pygame.draw.rect(tela, (240, 240, 245), (x - 34, CHAO - 112, 68, 16), border_radius=3)  # "AVALANCHE"
    for k in range(5):
        pygame.draw.line(tela, (180, 40, 40), (x - 26 + k * 12, CHAO - 104), (x - 20 + k * 12, CHAO - 104), 3)
    if not usado:  # a neve acumulada em cima da placa (é ela que cai)
        pygame.draw.ellipse(tela, (245, 248, 255), (x - 20, CHAO - 190, 40, 18))
        pygame.draw.ellipse(tela, (215, 228, 245), (x - 14, CHAO - 184, 28, 10))


def _bolada_neve(tela, x, y):
    pygame.draw.circle(tela, (200, 215, 235), (int(x), int(y)), 36)
    pygame.draw.circle(tela, (245, 248, 255), (int(x - 4), int(y - 4)), 32)
    for dx, dy, r in ((-22, 18, 12), (20, 20, 10), (28, -10, 9), (-26, -14, 8)):  # pedaços soltos
        pygame.draw.circle(tela, (235, 242, 252), (int(x + dx), int(y + dy)), r)


# =====================================================================
# o que cada cenário tem
# =====================================================================
# x: onde fica; tipo: ROLA/ONDA/CAI/CHAO; desenho; golpe; cor do efeito; tamanho da área que leva golpe
CONFIG = {
    "TEMPLO": dict(nome="LANTERNA DE PEDRA", x=170, tipo="ROLA", desenho=_lanterna, golpe=ROLANDO,
                   rolante=lambda tela, x, giro, t: _pedra(tela, x, CHAO - 22, giro), som="terra"),
    "PÂNTANO": dict(nome="BAMBU D'ÁGUA", x=790, tipo="CHAO", desenho=_vitoria_regia, golpe=ESCORREGA,
                    cor=(120, 190, 230), som="puf"),
    "FERRO-VELHO": dict(nome="TAMBOR DE ÓLEO", x=720, tipo="ROLA", desenho=_tambor, golpe=ROLANDO, som="terra"),
    "TOCA": dict(nome="COGUMELO GIGANTE", x=190, tipo="ONDA", desenho=_cogumelo, golpe=ONDA,
                 cor=(150, 255, 210), som="puf"),
    "DOJO": dict(nome="GONGO", x=790, tipo="ONDA", desenho=_gongo, golpe=ONDA, cor=(255, 220, 120), som="parry"),
    "CAMPO DE BATALHA": dict(nome="BARRIL DE PÓLVORA", x=190, tipo="ROLA", desenho=_barril_polvora, golpe=BOMBA,
                             explode=True, som="terra"),
    "TORRE DO MAGO": dict(nome="CALDEIRÃO", x=780, tipo="CAI", desenho=_caldeirao, golpe=CAINDO,
                          caindo=lambda tela, x, y, t: _bolha(tela, x, y, t), som="carga"),
    "CASSINO": dict(nome="CAÇA-NÍQUEL", x=190, tipo="CAI", desenho=_cacaniquel, golpe=CAINDO,
                    caindo=lambda tela, x, y, t: [_ficha(tela, x + dx, y + dy, t * 0.3 + dx, c) for dx, dy, c in
                                                  ((-26, 10, (220, 40, 40)), (0, -12, (40, 120, 220)),
                                                   (26, 6, (40, 160, 60)))],
                    som="carga"),
    "LABORATÓRIO": dict(nome="GERADOR", x=790, tipo="CHAO", desenho=_gerador, golpe=CHOQUE, cor=(170, 240, 255),
                        som="laser"),
    "ARENA DE SUMÔ": dict(nome="TAMBOR TAIKO", x=180, tipo="ONDA", desenho=_taiko, golpe=ONDA, cor=(255, 150, 120),
                          som="queda"),
    "SELVA": dict(nome="TRONCO", x=780, tipo="ROLA", desenho=_tronco, golpe=ROLANDO, som="terra"),
    "TEATRO DE MÁGICA": dict(nome="SACO DE AREIA", x=780, tipo="CAI", desenho=_corda_palco, golpe=CAINDO,
                             caindo=lambda tela, x, y, t: _saco(tela, x, y), som="vento", ja_no_alto=True,
                             cor_quebra=(200, 176, 120)),
    "NAVIO FANTASMA": dict(nome="BARRIL DO CONVÉS", x=760, tipo="ROLA",
                           desenho=lambda tela, x, t, usado, deitado=None: _tambor(tela, x, t, usado, deitado,
                                                                                   cor=(120, 80, 44)),
                           golpe=ROLANDO, som="terra"),
    "CERCADO DO DESERTO": dict(nome="COQUEIRO", x=790, tipo="CAI", desenho=_coqueiro, golpe=CAINDO,
                               caindo=lambda tela, x, y, t: _cocos(tela, x, y), som="vento",
                               cor_quebra=(150, 110, 60)),  # (os cocos saem lançados pra cima e caem no outro)
    "PRAIA DA ILHA": dict(nome="BOIA SALVA-VIDAS", x=180, tipo="ROLA", desenho=_boia_poste, golpe=ROLANDO,
                          rolante=lambda tela, x, giro, t: _boia(tela, x, CHAO - 26, giro), som="terra"),
    "MONTANHA NEVADA": dict(nome="PLACA DE AVALANCHE", x=790, tipo="CAI", desenho=_placa_avalanche, golpe=CAINDO,
                            caindo=lambda tela, x, y, t: _bolada_neve(tela, x, y), som="vento", ja_no_alto=True,
                            altura=-60, dx_alto=0, cor_quebra=(240, 245, 255)),  # (a neve cai lá de cima: só a sombra avisa)
    "CAVERNA DOS MORCEGOS": dict(nome="CRISTAL ROXO", x=180, tipo="ONDA", desenho=_cristal, golpe=ONDA,
                                 cor=(200, 140, 255), som="laser"),
    "FLORESTA ANTIGA": dict(nome="PEDRA RÚNICA", x=205, tipo="ROLA", desenho=_pedra_runa, golpe=ROLANDO, som="terra"),
    "CAMPO GIGANTE": dict(nome="BOLOTA GIGANTE", x=760, tipo="ROLA", desenho=_bolota, golpe=ROLANDO, som="terra"),
    "MONTE KARASUMA": dict(nome="BONECO DE PALHA", x=800, tipo="ROLA", desenho=_boneco_palha, golpe=ROLANDO,
                           som="terra"),
    "VILA DOS SAPOS": dict(nome="BALDE DE LAMA", x=190, tipo="CHAO", desenho=_balde_lama, golpe=ESCORREGA,
                           cor=(120, 84, 44), som="puf"),
}


def em_ultimate(l):
    """No meio de uma ultimate (fazendo ou levando): os objetos ficam de fora (igual à transição de cenário)."""
    return bool(getattr(l, "ult_recente", 0)) or (l.estado == "ataque" and bool(l.golpe)
                                                    and bool(l.golpe.get("ultimate")))


def criar(nome_do_cenario):
    """Os objetos desse cenário (se o cenário não tiver nenhum, um que não faz nada)."""
    cfg = CONFIG.get(nome_do_cenario)
    return Objeto(nome_do_cenario, cfg) if cfg else Nada()


class Nada:
    nome = ""

    def passo(self, partida):
        pass

    def desenhar(self, tela):
        pass

    def resetar(self):
        pass

    def area(self):
        return None


class Objeto:
    def __init__(self, cenario, cfg):
        self.cenario = cenario
        self.cfg = cfg
        self.nome = cfg["nome"]
        self.x = cfg["x"]
        self.tipo = cfg["tipo"]
        self.t = 0
        self.resetar()

    def resetar(self):
        """Começo de round: o objeto volta inteiro e some qualquer efeito que estava acontecendo."""
        self.pronto = True
        self.recarga = 0
        self.volta = 0        # quadros do objeto "aparecendo" de volta (desenho)
        self.treme = 0        # objeto balançando depois de levar golpe
        self.ef = None        # o efeito andando: dict com o que precisa
        self.particulas = []  # [x, y, vx, vy, vida, cor, tam]
        self.clarao = 0       # explosão / jackpot
        self.ef_explosao = (self.x, 0)

    # ------------------------------------------------------------ lógica (só aqui o estado muda)
    def caixa(self):
        """Onde o objeto pode levar golpe."""
        return pygame.Rect(self.x - 40, CHAO - 150, 80, 150)

    def passo(self, partida):
        self.t += 1
        if partida.treino and not LIGADO_NO_TREINO:
            return
        if self.treme > 0:
            self.treme -= 1
        if self.clarao > 0:
            self.clarao -= 1
        if self.volta > 0:
            self.volta -= 1
        for p in self.particulas:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += 0.35
            p[4] -= 1
        self.particulas = [p for p in self.particulas if p[4] > 0]
        if not self.pronto:
            self.recarga -= 1
            if self.recarga <= 0 and self.ef is None:
                self.pronto = True
                self.volta = 30
        if self.ef is not None:
            self.andar_efeito(partida)
        if self.pronto and partida.fase == "luta":
            self.ver_golpes(partida)

    def ver_golpes(self, partida):
        cx = self.caixa()
        if any(em_ultimate(l) for l in partida.L):
            return  # ultimate já é forte o bastante: não usa objeto (nem bater nele, nem ser jogado nele)
        for i, l in enumerate(partida.L):
            outro = partida.L[1 - i]
            # 1) levou golpe (caixa do golpe, ou o laser)
            bateu = False
            if l.estado == "ataque" and not l.acertou:
                cg = l.caixa_golpe()
                bateu = bool(cg and cg.colliderect(cx))
                if not bateu and l.feixe:
                    bateu = bool(cx.clipline(*l.feixe))
            if bateu:
                self.disparar(partida, l, outro)
                return
            # 2) alguém foi jogado contra ele
            if l.estado == "voando" and abs(l.vx) > 2.5 and cx.left < l.x < cx.right and l.y > CHAO - 170 \
                    and not getattr(l, "ult_recente", 0):
                self.batida(partida, l, outro)
                return

    def gastar(self):
        self.pronto = False
        self.recarga = RECARGA
        self.treme = 30

    def disparar(self, partida, dono, alvo):
        """O objeto levou golpe de 'dono': faz a parte dele contra o 'alvo'."""
        self.gastar()
        if hasattr(dono, "bonus_amarelo"):  # (2ª ULTIMATE: usar objeto enche a parte amarela da barra)
            dono.bonus_amarelo(BONUS_OBJETO)
        if dono is partida.L[0] and hasattr(partida, "stats"):  # (ESTATÍSTICAS / MISSÕES: objetos que o jogador usou)
            partida.stats["objetos"] = partida.stats.get("objetos", 0) + 1
        som.tocar(self.cfg.get("som", "soco"))
        partida.tremer(4)
        sentido = 1 if alvo.x >= self.x else -1
        if self.tipo == "ROLA":
            self.ef = dict(tipo="ROLA", x=self.x + sentido * 30, vx=sentido * 10, giro=0.0, dono=dono, alvo=alvo)
        elif self.tipo == "ONDA":
            self.ef = dict(tipo="ONDA", r=20.0, dono=dono, alvo=alvo, acertou=False)
            self.poeira(self.x, CHAO - 90, self.cfg.get("cor", BRANCO), 14)
        elif self.tipo == "CAI":
            alto = self.cfg.get("ja_no_alto")  # (o saco/o coco cai de onde estava pendurado)
            y0 = float(self.cfg.get("altura", 60)) if alto else -80.0
            self.ef = dict(tipo="CAI", fase="mira", t=0, x=self.x + self.cfg.get("dx_alto", 14) if alto else alvo.x,
                           y=y0, vy=0.0, dono=dono, alvo=alvo)
            self.clarao = 20  # (jackpot / caldeirão brilhando)
            self.poeira(self.x, CHAO - 110, (255, 230, 120), 12)
        elif self.tipo == "CHAO":
            self.ef = dict(tipo="CHAO", x=float(self.x), vx=sentido * 11, x0=self.x, dono=dono, alvo=alvo)

    def batida(self, partida, vitima, outro):
        """Alguém foi jogado contra o objeto: leva uma pancada a mais e o objeto se gasta."""
        self.gastar()
        vitima.levar(BATIDA_DANO, outro, BATIDA)
        partida.ultimo_hit = partida.tf
        partida.tremer(10)
        partida.faisca(self.x, CHAO - 80, False, True)
        som.tocar("explosao" if self.cfg.get("explode") else "chute")
        self.poeira(self.x, CHAO - 60, self.cfg.get("cor", (200, 180, 150)), 16)
        if self.cfg.get("explode"):
            self.clarao = 14
            self.ef_explosao = (self.x, 0)

    def acertar(self, partida, alvo, dono, g, ponto, sinal):
        """O efeito pegou no alvo: o Lutador.receber decide (defesa, parry, guarda quebrada, golpe)."""
        res = alvo.receber(g, sinal, dono, 1.0)
        partida.ultimo_hit = partida.tf
        if res == "quebrou":
            partida.guarda_quebrada(alvo, ponto)
        elif res == "parry":
            partida.parry(alvo, ponto)
        else:
            partida.som_do_golpe(res, g)
            partida.faisca(ponto[0], ponto[1], res == "def", g["dano"] >= 10)
            partida.parada = PARADA_GOLPE if res == "hit" else 4
            if res == "hit":
                partida.tremer(9)
        return res

    def poeira(self, x, y, cor, n):
        for _ in range(n):
            a = random.uniform(0, math.tau)
            v = random.uniform(2, 6)
            self.particulas.append([x, y, math.cos(a) * v, math.sin(a) * v - 2, random.randint(14, 26), cor,
                                    random.randint(3, 6)])

    def andar_efeito(self, partida):
        ef = self.ef
        alvo, dono = ef["alvo"], ef["dono"]
        if alvo not in partida.L:  # TRIO: trocou de lutador no meio: o efeito vai no que está lutando agora
            alvo = ef["alvo"] = partida.L[1 - partida.L.index(dono)] if dono in partida.L else partida.L[0]
        if ef["tipo"] == "ROLA":
            ef["x"] += ef["vx"]
            ef["giro"] += ef["vx"] * 0.045
            if self.t % 4 == 0:
                self.particulas.append([ef["x"] - ef["vx"] * 2, CHAO - 4, -ef["vx"] * 0.1, -1.5, 14,
                                        (170, 150, 120), 3])
            r = pygame.Rect(ef["x"] - 24, CHAO - 50, 48, 50)
            c = alvo.corpo()
            if c and r.colliderect(c):
                self.acertar(partida, alvo, dono, self.cfg["golpe"], r.clip(c).center, 1 if ef["vx"] > 0 else -1)
                self.fim_rolando(partida, ef["x"])
            elif ef["x"] < PAREDE_E - 30 or ef["x"] > PAREDE_D + 30:
                self.fim_rolando(partida, ef["x"])
        elif ef["tipo"] == "ONDA":
            antes = ef["r"]
            ef["r"] += 14
            d = abs(alvo.x - self.x)
            if not ef["acertou"] and antes < d <= ef["r"]:
                ef["acertou"] = True
                c = alvo.corpo()
                if c and alvo.no_chao():  # pulou: a onda passa por baixo
                    self.acertar(partida, alvo, dono, self.cfg["golpe"], c.center, 1 if alvo.x > self.x else -1)
            if ef["r"] > 1000:
                self.ef = None
        elif ef["tipo"] == "CAI":
            ef["t"] += 1
            if ef["fase"] == "mira":  # a sombra persegue o alvo e trava um pouco antes de cair
                if ef["t"] < 40:
                    ef["x"] += (alvo.x - ef["x"]) * 0.12
                if ef["t"] >= 55:
                    ef["fase"], ef["vy"] = "cai", 4.0
            else:
                ef["vy"] += 1.1
                ef["y"] += ef["vy"]
                r = pygame.Rect(ef["x"] - 34, ef["y"] - 34, 68, 68)
                c = alvo.corpo()
                if c and r.colliderect(c):
                    self.acertar(partida, alvo, dono, self.cfg["golpe"], r.clip(c).center,
                                 1 if alvo.x >= ef["x"] else -1)
                    self.quebrar(ef["x"], ef["y"])
                elif ef["y"] >= CHAO - 30:
                    som.tocar("queda", 0.6)
                    self.quebrar(ef["x"], CHAO - 30)
        elif ef["tipo"] == "CHAO":
            antes = ef["x"]
            ef["x"] += ef["vx"]
            if self.t % 2 == 0:
                self.particulas.append([ef["x"], CHAO - 4, random.uniform(-1, 1), random.uniform(-5, -2), 16,
                                        self.cfg.get("cor", BRANCO), 4])
            lo, hi = min(antes, ef["x"]), max(antes, ef["x"])
            if lo <= alvo.x <= hi:
                c = alvo.corpo()
                if c and alvo.no_chao():
                    self.acertar(partida, alvo, dono, self.cfg["golpe"], (alvo.x, CHAO - 20),
                                 1 if ef["vx"] > 0 else -1)
                    self.ef = None
                    return
            if ef["x"] < PAREDE_E - 40 or ef["x"] > PAREDE_D + 40:
                self.ef = None

    def fim_rolando(self, partida, x):
        if self.cfg.get("explode"):  # o barril de pólvora explode
            som.tocar("explosao")
            partida.tremer(12)
            self.clarao = 14
            self.ef_explosao = (x, 20)
            self.poeira(x, CHAO - 30, (255, 170, 60), 24)
        else:
            self.poeira(x, CHAO - 24, (170, 150, 120), 12)
        self.ef = None

    def quebrar(self, x, y):
        cor = self.cfg.get("cor_quebra", (255, 230, 120) if self.cenario == "CASSINO" else (200, 140, 255))
        self.poeira(x, y, cor, 20)
        self.ef = None

    # ------------------------------------------------------------ desenho (só lê o estado)
    def area(self):
        """Pedaço da tela onde tem coisa do objeto pra desenhar (pra partida passar pra pixel art só ele)."""
        r = self.caixa().inflate(140, 60)
        if self.ef is not None or self.particulas:
            return pygame.Rect(0, 0, LARGURA, ALTURA)
        return r

    def desenhar(self, tela):
        t = self.t
        cfg = self.cfg
        desenho = cfg["desenho"]
        usado = not self.pronto
        if self.volta > 0 and self.volta % 6 < 3:
            pass  # voltando: pisca
        elif desenho in (_gongo, _taiko, _cogumelo):
            desenho(tela, self.x, t, usado, self.treme)
        else:
            desenho(tela, self.x, t, usado)
        ef = self.ef
        if ef is not None:
            if ef["tipo"] == "ROLA":
                if cfg.get("rolante"):
                    cfg["rolante"](tela, ef["x"], ef["giro"], t)
                else:
                    desenho(tela, ef["x"], t, True, ef["giro"])
            elif ef["tipo"] == "ONDA":
                cor = cfg.get("cor", BRANCO)
                camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                alfa = max(0, int(200 * (1 - ef["r"] / 1000)))
                for k, dr in enumerate((0, 26, 52)):
                    r = ef["r"] - dr
                    if r > 10:
                        pygame.draw.ellipse(camada, (*cor, max(0, alfa - k * 60)),
                                            (self.x - r, CHAO - 110 - r * 0.45, r * 2, r * 0.9 + 110), 5 - k)
                tela.blit(camada, (0, 0))
            elif ef["tipo"] == "CAI":
                if ef["fase"] == "mira" or ef["y"] < CHAO - 60:  # a sombra avisando onde vai cair
                    k = min(1.0, ef["t"] / 40)
                    w = int(30 + 40 * k)
                    camada = pygame.Surface((w * 2, 24), pygame.SRCALPHA)
                    pygame.draw.ellipse(camada, (0, 0, 0, int(70 + 80 * k)), (0, 0, w * 2, 24))
                    tela.blit(camada, (ef["x"] - w, CHAO - 12))
                    if ef["fase"] == "mira" and ef["t"] >= 40 and (ef["t"] // 3) % 2:  # travou: pisca vermelho
                        pygame.draw.ellipse(tela, (255, 70, 60), (ef["x"] - w, CHAO - 12, w * 2, 24), 2)
                if ef["fase"] == "cai":
                    cfg["caindo"](tela, ef["x"], ef["y"], t)
                elif cfg.get("ja_no_alto"):  # (o saco de areia já está lá em cima: anda pelo alto até o alvo)
                    cfg["caindo"](tela, ef["x"], cfg.get("altura", 60), t)
                else:  # subindo do objeto (a bolha / as fichas saindo da máquina)
                    sobe = CHAO - 110 - ef["t"] * 9
                    if sobe > -60:
                        cfg["caindo"](tela, self.x, sobe, t)
            elif ef["tipo"] == "CHAO":
                cor = cfg.get("cor", BRANCO)
                x0, x1 = sorted((ef["x0"], ef["x"]))
                if self.cenario == "LABORATÓRIO":  # raio correndo pelo chão
                    pts = []
                    n = max(2, int((x1 - x0) / 18))
                    for k in range(n + 1):
                        px = x0 + (x1 - x0) * k / n
                        py = CHAO - 6 - (10 if (k + t // 2) % 2 else 0)
                        pts.append((px, py))
                    pygame.draw.lines(tela, cor, False, pts, 3)
                    pygame.draw.lines(tela, BRANCO, False, pts, 1)
                else:  # água / lama espalhando no chão
                    pygame.draw.rect(tela, cor, (x0, CHAO - 5, x1 - x0, 7), border_radius=3)
                    fx = ef["x"]
                    pygame.draw.ellipse(tela, cor, (fx - 26, CHAO - 26, 52, 30))  # a "onda" na frente
        for p in self.particulas:
            pygame.draw.circle(tela, p[5], (int(p[0]), int(p[1])), max(1, int(p[6] * min(1, p[4] / 10))))
        if self.clarao > 0:  # explosão / jackpot / caldeirão: um clarão em volta
            k = self.clarao / 20
            camada = pygame.Surface((220, 220), pygame.SRCALPHA)
            cor = (255, 200, 80) if self.cfg.get("explode") else (255, 240, 160)
            pygame.draw.circle(camada, (*cor, int(160 * k)), (110, 110), int(60 + 50 * (1 - k)))
            x = getattr(self, "ef_explosao", (self.x, 0))[0] if self.cfg.get("explode") else self.x
            tela.blit(camada, (x - 110, CHAO - 170))
