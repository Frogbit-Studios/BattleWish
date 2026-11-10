"""FINISH (v2.0, ideia aprovada pelo Gomes): a luta acabou com uma ULTIMATE? Aparece "FINISH!", a câmera chega
perto e o vencedor faz uma cena curtinha e engraçada própria dele (sem sangue, só zoeira). Depois, a vitória.

Cada lutador tem: passo(v, d, t, jogo)  -> mexe no vencedor (v) e no derrotado (d); t = quadro do FINISH
                  desenhar(v, d, tela, t) -> os efeitos (o t continua depois que acaba: o "resultado" fica na tela)
                  some = o derrotado some (vira outra coisa) a partir do quadro tal
Tudo só mexe em posição/pose/desenho, depois que a luta já acabou (no ONLINE sai igual nos dois PCs)."""
import math

import pygame

import som
from config import *  # noqa: F401,F403
from golpes import misturar, suave

DURACAO = 170
TEXTO = 34  # quadros do "FINISH!" grandão no começo


def ponto_do_caido(d, k):
    """Onde está um pedaço (k = 'pc' peito, 'cb' cabeça...) do derrotado deitado."""
    return d.ponto(d.poses["caido"], k)


def pose(l, nome, alvo=None, k=1.0):
    """Põe o lutador numa pose dele (ou mistura com outra)."""
    p = l.poses.get(nome) or l.poses["vitoria"]
    if alvo:
        p = misturar(p, l.poses.get(alvo) or l.poses["parado"], k)
    l.sobrepor = dict(p)


def contorno(tela, cor, pts, w=2):
    pygame.draw.polygon(tela, (12, 10, 18), pts)
    meio = (sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts))
    pygame.draw.polygon(tela, cor, [(x + (meio[0] - x) * 0.12, y + (meio[1] - y) * 0.12) for x, y in pts])


def poeira(jogo, x, n=10):
    from max10 import fumaca
    fumaca(jogo, x, CHAO - 4, n, (180, 170, 150), 4, -0.6)


def puf(jogo, x, y, n=12, cor=(220, 220, 236)):
    from max10 import fumaca
    fumaca(jogo, x, y, n, cor, 5, -1)


# =====================================================================
# MAX-10: RECICLAGEM (escaneia, vira cubo de ferro-velho, chuta pra longe)
# =====================================================================
def max_passo(v, d, t, jogo):
    pose(v, "especial" if t < 60 else "chute" if 100 <= t < 116 else "parado")
    if t == 10:
        som.tocar("laser", 0.6)
    if t == 60:  # virou cubo de ferro-velho
        d.esconde = True
        puf(jogo, d.x, CHAO - 20, 14, (170, 170, 180))
        som.tocar("quebra", 0.7)
    if t == 104:
        som.tocar("chute")


def max_desenhar(v, d, tela, t):
    s = d.s
    if t < 60:  # o scanner vermelho passando
        y = CHAO - 10 - (t * 3 % 120) * s
        pygame.draw.line(tela, (255, 40, 40), (d.x - 50 * s, y), (d.x + 50 * s, y), 2)
        pygame.draw.line(tela, (255, 160, 150), (v.x + v.dir * 30 * v.s, v.y - 100 * v.s), (d.x, y), 1)
        return
    lado = max(10, 34 * s * (1 - min(1, (t - 60) / 30)) + 14 * s)
    x, y = d.x, CHAO - lado / 2
    if t >= 104:  # chutado pra longe (com arco)
        k = (t - 104) / 40
        x += v.dir * 700 * k
        y -= math.sin(min(1, k) * math.pi) * 160
    r = pygame.Rect(0, 0, lado, lado)
    r.center = (int(x), int(y))
    pygame.draw.rect(tela, (12, 10, 18), r.inflate(4, 4))
    pygame.draw.rect(tela, (120, 122, 132), r)
    pygame.draw.line(tela, (80, 82, 92), r.topleft, r.bottomright, 2)
    pygame.draw.line(tela, (160, 162, 172), (r.x, r.centery), (r.right, r.centery), 2)


# =====================================================================
# RIB: CHUVA DE SHURIKEN (prende no chão) + selo de mão
# =====================================================================
def rib_passo(v, d, t, jogo):
    pose(v, "r_selo")
    if 20 <= t < 70 and t % 10 == 0:
        som.tocar("shuriken", 0.5)


def rib_desenhar(v, d, tela, t):
    s = d.s
    for i in range(5):
        cai = 20 + i * 10
        if t < cai:
            continue
        x = d.x + (i - 2) * 22 * s
        y = min(CHAO - 4, -40 + (t - cai) * 30)
        a = (t - cai) * 0.8 if y < CHAO - 4 else 0.6
        for k in range(4):
            ang = a + k * math.pi / 2
            pts = [(x, y), (x + math.cos(ang) * 9, y + math.sin(ang) * 9), (x + math.cos(ang + 0.6) * 4,
                                                                            y + math.sin(ang + 0.6) * 4)]
            pygame.draw.polygon(tela, (200, 204, 214), pts)
        pygame.draw.circle(tela, (40, 40, 50), (int(x), int(y)), 2)


# =====================================================================
# TRAFO: ENTERRADO (afunda na terra, fica um montinho) + uivo
# =====================================================================
def trafo_passo(v, d, t, jogo):
    pose(v, "t_agacha" if t < 60 else "t_uivo")
    if 20 <= t < 70:
        d.cortar_chao = True
        d.y = CHAO + (t - 20) * 2.2 * d.s
        if t % 6 == 0:
            poeira(jogo, d.x, 3)
    if t == 70:
        d.esconde = True
        som.tocar("uivo")


def trafo_desenhar(v, d, tela, t):
    if t < 60:
        return
    s = d.s
    pygame.draw.ellipse(tela, (12, 10, 18), (d.x - 40 * s, CHAO - 16 * s, 80 * s, 30 * s))
    pygame.draw.ellipse(tela, (110, 76, 44), (d.x - 38 * s, CHAO - 14 * s, 76 * s, 26 * s))
    pygame.draw.line(tela, (60, 40, 24), (d.x - 6 * s, CHAO - 12 * s), (d.x - 6 * s, CHAO - 30 * s), 3)  # a plaquinha
    pygame.draw.rect(tela, (200, 170, 120), (d.x - 18 * s, CHAO - 40 * s, 24 * s, 12 * s))


# =====================================================================
# KING RIP: HORA DO CHÁ (senta em cima e toma um chazinho)
# =====================================================================
def king_passo(v, d, t, jogo):
    peito = ponto_do_caido(d, "pc")
    if t < 30:
        v.x += (peito[0] - v.x) * 0.15
        pose(v, "parado")
    else:
        v.x = peito[0]
        v.y = peito[1] + 16 * v.s
        pose(v, "k_agacha")
        if t == 30:
            som.tocar("queda", 0.6)


def king_desenhar(v, d, tela, t):
    if t < 36:
        return
    p = v.pose_vista or v.pose_atual()
    m = v.ponto(p, "mf")
    s = v.s
    pygame.draw.rect(tela, (12, 10, 18), (m[0] - 6 * s, m[1] - 9 * s, 12 * s, 10 * s))
    pygame.draw.rect(tela, (240, 240, 236), (m[0] - 5 * s, m[1] - 8 * s, 10 * s, 8 * s))  # a xícara
    pygame.draw.circle(tela, (240, 240, 236), (int(m[0] + 6 * s), int(m[1] - 4 * s)), max(2, int(3 * s)), 2)
    for i in range(3):  # o vapor
        k = ((t * 0.04) + i / 3) % 1
        x = m[0] + math.sin(k * 6 + i) * 4 * s
        pygame.draw.circle(tela, (230, 230, 240), (int(x), int(m[1] - 12 * s - k * 30 * s)), max(1, int(3 * s * (1 - k))))


# =====================================================================
# CANNAN: ENTREGA AÉREA (continência, caixa de paraquedas cai em cima)
# =====================================================================
def cannan_passo(v, d, t, jogo):
    pose(v, "c_continencia")
    if t == 84:
        d.esconde = True
        poeira(jogo, d.x, 14)
        jogo.tremer(10)
        som.tocar("queda")


def cannan_desenhar(v, d, tela, t):
    s = d.s
    y = min(CHAO, -120 + t * 7)
    caixa = pygame.Rect(0, 0, 70 * s, 54 * s)
    caixa.midbottom = (int(d.x), int(y))
    if y < CHAO:  # o paraquedas
        pygame.draw.arc(tela, (240, 240, 240), (caixa.centerx - 60 * s, caixa.y - 100 * s, 120 * s, 70 * s), 0,
                        math.pi, 4)
        for x in (caixa.x, caixa.right):
            pygame.draw.line(tela, (200, 200, 200), (x, caixa.y), (caixa.centerx, caixa.y - 66 * s), 1)
    pygame.draw.rect(tela, (12, 10, 18), caixa.inflate(4, 4))
    pygame.draw.rect(tela, (110, 120, 70), caixa)
    pygame.draw.line(tela, (70, 80, 40), caixa.topleft, caixa.bottomright, 3)
    pygame.draw.line(tela, (70, 80, 40), caixa.topright, caixa.bottomleft, 3)


# =====================================================================
# FINN: VIROU SAPO (brilho de magia, puf, um sapinho no lugar)
# =====================================================================
def finn_passo(v, d, t, jogo):
    pose(v, "f_vitoria" if t > 20 else "f_carrega")
    if t == 60:
        d.esconde = True
        puf(jogo, d.x, CHAO - 30, 18, (200, 160, 255))
        som.tocar("puf")
    if t > 70 and t % 24 == 0:
        som.tocar("lingua", 0.3)


def finn_desenhar(v, d, tela, t):
    s = d.s
    if t < 60:  # as estrelinhas em volta do derrotado
        for i in range(8):
            a = t * 0.2 + i * math.tau / 8
            x, y = d.x + math.cos(a) * 50 * s, CHAO - 30 * s + math.sin(a) * 20 * s
            pygame.draw.circle(tela, (255, 230, 120), (int(x), int(y)), 3)
        return
    s *= 1.6  # (um sapinho bem visível)
    pulo = abs(math.sin(t * 0.13)) * 14 * s if t % 48 < 24 else 0  # o sapinho pulando
    x, y = d.x, CHAO - 8 * s - pulo
    pygame.draw.ellipse(tela, (12, 10, 18), (x - 14 * s, y - 12 * s, 28 * s, 18 * s))
    pygame.draw.ellipse(tela, (90, 170, 70), (x - 12 * s, y - 10 * s, 24 * s, 14 * s))
    for k in (-1, 1):
        pygame.draw.circle(tela, (12, 10, 18), (int(x + k * 6 * s), int(y - 10 * s)), max(2, int(4.4 * s)))
        pygame.draw.circle(tela, (250, 250, 240), (int(x + k * 6 * s), int(y - 10 * s)), max(1, int(3.4 * s)))
        pygame.draw.circle(tela, (12, 10, 18), (int(x + k * 6 * s), int(y - 10 * s)), max(1, int(1.4 * s)))


# =====================================================================
# KUN: PRO BARALHO (o derrotado vira uma carta e voa pra mão dele)
# =====================================================================
def kun_passo(v, d, t, jogo):
    pose(v, "k_brinca" if t < 80 else "k_vitoria")
    if t == 50:
        d.esconde = True
        puf(jogo, d.x, CHAO - 30, 10)
        som.tocar("shuriken")


def kun_desenhar(v, d, tela, t):
    if t < 50:
        return
    import kun
    k = min(1.0, (t - 50) / 40)
    p = v.pose_vista or v.pose_atual()
    m = v.ponto(p, "mf")
    x = d.x + (m[0] - d.x) * suave(k)
    y = CHAO - 30 + (m[1] - CHAO + 30) * suave(k) - math.sin(k * math.pi) * 80
    kun.carta(tela, (x, y), (1 - k) * 8, (3.4 - 1.6 * k) * d.s / 1.36 * 1.4, 1, brilha=True)


# =====================================================================
# TROMOS (o antigo Xenomorph): O CASULO (gosma preta cobrindo o derrotado)
# =====================================================================
def xeno_passo(v, d, t, jogo):
    pose(v, "x_vitoria")
    if t == 10:
        som.tocar("lingua", 0.5)
    if t == 70:
        d.esconde = True


def xeno_desenhar(v, d, tela, t):
    s = d.s
    k = min(1.0, t / 70)
    alto = (14 + 26 * k) * s
    larg = 70 * s
    r = pygame.Rect(0, 0, larg, alto)
    r.midbottom = (int(d.x), int(CHAO))
    pygame.draw.ellipse(tela, (12, 10, 18), r.inflate(6, 6))
    pygame.draw.ellipse(tela, (36, 40, 50), r)
    for i in range(4):  # as gotas brilhando
        gx = r.x + (i + 0.5) * larg / 4
        pygame.draw.circle(tela, (90, 100, 120), (int(gx), int(r.y + alto * 0.35 + (i % 2) * 6)), max(1, int(2 * s)))


# =====================================================================
# TAI: A SENTADA (pula e senta em cima)
# =====================================================================
def tai_passo(v, d, t, jogo):
    if t < 24:
        pose(v, "t_shiko")
    elif t < 44:  # o pulo
        k = (t - 24) / 20
        peito = ponto_do_caido(d, "pc")
        v.x += (peito[0] - v.x) * 0.2
        v.y = CHAO - math.sin(k * math.pi) * 140 - 4 * v.s * k
        pose(v, "t_senta")
    else:
        peito = ponto_do_caido(d, "pc")
        v.x, v.y = peito[0], CHAO - 4 * v.s
        pose(v, "t_senta")
        if t == 44:
            jogo.tremer(18)
            poeira(jogo, d.x, 18)
            som.tocar("queda")
            som.tocar("ko", 0.5)


def tai_desenhar(v, d, tela, t):
    if 44 <= t < 70:
        texto_tela(tela, "PLOFT!", (d.x, CHAO - 150), (255, 230, 120))


def texto_tela(tela, txt, pos, cor):
    from efeitos import texto_grande
    texto_grande(tela, txt, 28, cor, (int(pos[0]), int(pos[1])))


# =====================================================================
# TAMER: UIVO DA ALCATEIA (3 lobos chegam e uivam em volta)
# =====================================================================
def tamer_passo(v, d, t, jogo):
    pose(v, "t_grito" if t > 50 else "parado")
    if t == 50:
        som.tocar("uivo")


def tamer_desenhar(v, d, tela, t):
    import tamer
    s = d.s
    for i, (lado, perto) in enumerate(((-1, -90), (1, 90), (1, 40))):
        k = min(1.0, t / 40)
        x = d.x + lado * 600 * (1 - suave(k)) + perto * s * 0.7
        tamer.desenha_lobo(tela, x, CHAO, s / (1.36 / 3) * 1.0, -lado, "uiva" if k >= 1 else "corre", t + i * 9, "cinza")


# =====================================================================
# JOHN: SUMIU! (a caixa mágica cai em cima, abre vazia e sai um coelho)
# =====================================================================
def john_passo(v, d, t, jogo):
    pose(v, "j_tira" if t < 90 else "j_agradece")
    if t == 40:
        d.esconde = True
        som.tocar("queda", 0.5)
    if t == 90:
        puf(jogo, d.x, CHAO - 50, 16, (170, 90, 230))
        som.tocar("puf")


def john_desenhar(v, d, tela, t):
    import john
    s = d.s
    y = min(CHAO, -60 + t * 12)
    caixa = pygame.Rect(0, 0, 60 * s, 90 * s)
    caixa.midbottom = (int(d.x), int(y))
    if t < 90:
        pygame.draw.rect(tela, (12, 10, 18), caixa.inflate(6, 6), border_radius=4)
        pygame.draw.rect(tela, (100, 40, 150), caixa, border_radius=4)
        for k in range(3):
            pygame.draw.circle(tela, (240, 200, 70), (caixa.centerx, int(caixa.y + 20 * s + k * 24 * s)), max(2, int(3 * s)))
    else:  # abriu: vazia! e sai um coelho
        k = min(1.0, (t - 90) / 30)
        john.desenha_coelho(tela, d.x + v.dir * 0 + (-v.dir) * 80 * s * k, CHAO, s * 1.4, -v.dir, t, 0.6)


# =====================================================================
# RIBBAT: REI DA CABEÇA (pula na cabeça do derrotado, ganha coroinha)
# =====================================================================
def ribbat_passo(v, d, t, jogo):
    cabeca = ponto_do_caido(d, "cb")
    if t < 30:
        k = t / 30
        v.x += (cabeca[0] - v.x) * 0.2
        v.y = CHAO - math.sin(k * math.pi) * 90 - (CHAO - cabeca[1] + 6 * d.s) * k
    else:
        v.x, v.y = cabeca[0], cabeca[1] - 6 * d.s
        if t == 30:
            som.tocar("lingua", 0.5)


def ribbat_desenhar(v, d, tela, t):
    if t < 34:
        return
    import chapeus_ribbat
    chapeus_ribbat.desenhar(tela, "coroa", v.x, v.y, v.lado(), v.s * 0.84)


def craquen_passo(v, d, t, jogo):
    pose(v, "q_comanda" if t < 90 else "q_ri")
    if 30 <= t < 90:
        d.cortar_chao = True
        d.y = CHAO + (t - 30) * 1.8 * d.s
    if t == 30:
        som.tocar("terra")
    if t == 90:
        d.esconde = True
        som.tocar("ultimate", 0.5)


def craquen_desenhar(v, d, tela, t):
    import craquen
    if t >= 100:
        return
    for i, dx in enumerate((-50, 0, 50)):  # 3 tentáculos agarrando e puxando pra baixo
        k = min(1.0, t / 25) if t < 70 else max(0.0, 1 - (t - 70) / 30)
        x0 = d.x + dx * d.s
        alto = 90 * d.s * k
        pts = [(x0 - 8 * d.s, CHAO), (x0 + math.sin(t * 0.3 + i) * 10 * d.s, CHAO - alto), (x0 + 8 * d.s, CHAO)]
        pygame.draw.polygon(tela, (20, 10, 26), pts)
        pygame.draw.polygon(tela, (120, 60, 130), [(x + (x0 - x) * 0.25, y) for x, y in pts])
    pygame.draw.ellipse(tela, (10, 30, 40), (d.x - 70 * d.s, CHAO - 8 * d.s, 140 * d.s, 16 * d.s))  # o redemoinho


# =====================================================================
# MAGNUS: TOSTADO! (cospe fogo em cima do derrotado e sobra só um montinho fumegando)
# =====================================================================
def magnus_passo(v, d, t, jogo):
    import magnus
    pose(v, "m_ruge" if t < 20 else "m_atira")
    if t == 20:
        som.tocar("explosao", 0.6)
    if 20 <= t < 80 and t % 2 == 0:
        x = d.x + (math.sin(t * 0.7) * 30) * d.s
        magnus.chama(jogo, x, CHAO - 10, 3, 1.6)
    if t == 80:
        d.esconde = True
        puf(jogo, d.x, CHAO - 20, 16, (80, 80, 86))
    if t > 80 and t % 12 == 0:
        puf(jogo, d.x, CHAO - 14, 2, (110, 110, 116))


def magnus_desenhar(v, d, tela, t):
    s = d.s
    if 20 <= t < 80:  # o jato de fogo
        p = v.pose_vista or v.pose_atual()
        boca = v.ponto(p, "cb")
        for i in range(10):
            k = i / 9
            x = boca[0] + (d.x - boca[0]) * k
            y = boca[1] + (CHAO - 30 - boca[1]) * k + math.sin(t * 0.8 + i) * 6
            pygame.draw.circle(tela, (255, int(200 - 120 * k), 40), (int(x), int(y)), max(3, int((5 + 10 * k) * s)))
    if t >= 80:  # o montinho tostado
        r = pygame.Rect(0, 0, 60 * s, 22 * s)
        r.midbottom = (int(d.x), int(CHAO))
        pygame.draw.ellipse(tela, (12, 10, 10), r.inflate(6, 6))
        pygame.draw.ellipse(tela, (40, 34, 30), r)
        for i in range(3):  # brasinhas
            pygame.draw.circle(tela, (255, 120 + 40 * ((t // 6 + i) % 2), 40),
                               (int(r.x + (i + 0.6) * r.w / 3.4), int(r.y + r.h * 0.4)), max(1, int(2 * s)))
        if t < 120:
            texto_tela(tela, "TOSTADO!", (d.x, CHAO - 150), (255, 160, 60))


# =====================================================================
# SPHYRUS: VIROU ISCA! (desce um anzol, fisga o derrotado e puxa lá pra cima)
# =====================================================================
ISCA_DESCE, ISCA_SOBE = 40, 110


def sphyrus_passo(v, d, t, jogo):
    pose(v, "s_ruge" if t < 30 or t > ISCA_SOBE else "parado")
    if t == 8:
        som.tocar("terra", 0.6)
    if t == ISCA_DESCE:
        som.tocar("lingua", 0.6)
    if ISCA_DESCE < t < ISCA_SOBE:  # puxado pro alto, pendurado no anzol
        d.y = CHAO - (t - ISCA_DESCE) ** 1.4 * 1.1
    if t == ISCA_SOBE:
        d.esconde = True


def sphyrus_desenhar(v, d, tela, t):
    s = d.s
    if t < ISCA_DESCE:
        y = (CHAO - 60 * s) * t / ISCA_DESCE
    elif t < ISCA_SOBE:
        y = d.y - 60 * s
    else:
        y = -40
    x = d.x
    pygame.draw.line(tela, (230, 230, 230), (x, 0), (x, y), 2)  # a linha de pesca
    pygame.draw.arc(tela, (180, 180, 190), (x - 10 * s, y - 2, 20 * s, 22 * s), math.pi, 2 * math.pi + 0.6, 3)  # o anzol
    pygame.draw.line(tela, (180, 180, 190), (x, y - 6), (x, y + 10 * s), 3)
    if ISCA_DESCE < t < ISCA_SOBE + 50:
        texto_tela(tela, "VIROU ISCA!", (v.x, CHAO - 170), (140, 220, 255))


# =====================================================================
# FRIGANTUS: SOTERRADO! (a avalanche cobre ele e só a MÃO fica de fora, tremendo)
# =====================================================================
def frigantus_passo(v, d, t, jogo):
    pose(v, "fr_peito_a" if (t // 6) % 2 and t < 30 else "fr_peito_b" if t < 30 else "fr_ruge")
    if t == 30:
        som.tocar("terra")
        som.tocar("explosao", 0.5)
        jogo.tremer(18)
    if t == 54:
        d.esconde = True


def frigantus_desenhar(v, d, tela, t):
    if t < 30:
        return
    k = suave(min(1, (t - 30) / 24))
    x = d.x
    rnd = __import__("random").Random(3)
    for i in range(18):  # o monte de neve caindo e cobrindo
        bx = x + rnd.uniform(-90, 90)
        by = CHAO - 20 - rnd.uniform(0, 50) - (1 - k) * 300
        r = rnd.uniform(22, 40)
        pygame.draw.circle(tela, (240, 244, 252) if i % 3 else (210, 222, 238), (int(bx), int(min(CHAO - 10, by))), int(r))
    if t >= 54:  # só a mão de fora, tremendo
        mx = x + 10 + math.sin(t * 1.4) * 2
        my = CHAO - 70
        pygame.draw.line(tela, (60, 50, 50), (mx, my + 26), (mx, my), 9)
        for k2 in (-1, 0, 1):
            pygame.draw.line(tela, (60, 50, 50), (mx, my), (mx + k2 * 6, my - 10), 4)
        if t < 120:
            texto_tela(tela, "SOTERRADO!", (d.x, CHAO - 170), (200, 240, 255))


# =====================================================================
# INAZUMANEKO: CORTE DE CABELO! (passa num relâmpago, embainha a espada... *clic*... e o derrotado fica CARECA)
# =====================================================================
INAZ_PASSA, INAZ_CLIC = 24, 50


def inazumaneko_passo(v, d, t, jogo):
    if t < INAZ_PASSA:
        pose(v, "i_respira" if t < 14 else "i_saca")
    elif t == INAZ_PASSA:  # o PASSO: atravessa pro outro lado num piscar de olhos
        v.x = d.x + (d.x - v.x) * 0.6 + (70 if d.x > v.x else -70)
        v.x = max(PAREDE_E, min(PAREDE_D, v.x))
        v.dir = 1 if d.x > v.x else -1
        pose(v, "i_passo")
        som.tocar("vento", 0.8)
    elif t < INAZ_CLIC:
        pose(v, "i_passo", "i_embainha", suave(min(1, (t - INAZ_PASSA) / 20)))
    else:
        pose(v, "i_embainha", "i_curva", suave(min(1, (t - INAZ_CLIC) / 14)))
    if t == INAZ_CLIC:
        som.tocar("defesa", 0.6)
        jogo.tremer(6)


def inazumaneko_desenhar(v, d, tela, t):
    if INAZ_PASSA <= t < INAZ_PASSA + 6:  # o RISCO do corte relâmpago
        u = (t - INAZ_PASSA) / 6
        pygame.draw.line(tela, (230, 245, 255), (d.x - 120, CHAO - 50 - 40 * u), (d.x + 120, CHAO - 70 + 40 * u), 4)
    if t >= INAZ_CLIC:
        cb = ponto_do_caido(d, "cb")
        s = d.s
        careca = pygame.Rect(0, 0, 18 * s, 13 * s)  # a cabeça CARECA, brilhando
        careca.center = (int(cb[0]), int(cb[1] - 2 * s))
        pygame.draw.ellipse(tela, (16, 14, 20), careca.inflate(4, 4))
        pygame.draw.ellipse(tela, (236, 204, 172), careca)
        if (t // 8) % 3 == 0:
            pygame.draw.circle(tela, (255, 255, 255), (careca.x + int(careca.w * 0.3), careca.y + int(careca.h * 0.3)), max(2, int(2 * s)))
        rnd = __import__("random").Random(5)
        for i in range(10):  # os fios de CABELO caindo devagar, balançando
            u = min(1, (t - INAZ_CLIC) / 50)
            x = cb[0] + rnd.uniform(-30, 30) + math.sin(t * 0.1 + i) * 8
            y = cb[1] - 60 + u * (60 + rnd.uniform(0, 20))
            pygame.draw.line(tela, (60, 40, 30), (x, y), (x + 6, y + 3), 2)
        if t < 120:
            texto_tela(tela, "CORTE DE CABELO!", (d.x, CHAO - 150), (230, 245, 255))


# =====================================================================
# NOCTURNUS: PENDURADO! (a nuvem de morcegos carrega o derrotado e pendura ele de cabeça pra baixo, lá no alto)
# =====================================================================
NOCT_PEGA, NOCT_SOBE = 30, 90


def nocturnus_passo(v, d, t, jogo):
    pose(v, "n_grito" if t < NOCT_PEGA else "n_ri")
    if t == 4:
        som.tocar("vento", 0.7)
    if NOCT_PEGA <= t < NOCT_SOBE:  # sobe carregado pelos morcegos
        d.y = CHAO - (t - NOCT_PEGA) ** 1.3 * 2.4
    if t == NOCT_SOBE:
        d.esconde = True


def _morceguinho(tela, x, y, t, i):
    asa = 5 if (t // 3 + i) % 2 else -3
    pygame.draw.polygon(tela, (20, 14, 28), [(x - 10, y - asa), (x - 3, y - 2), (x, y + 2), (x + 3, y - 2), (x + 10, y - asa),
                                             (x + 4, y + 2), (x, y + 5), (x - 4, y + 2)])
    pygame.draw.circle(tela, (255, 70, 70), (int(x - 1), int(y)), 1)
    pygame.draw.circle(tela, (255, 70, 70), (int(x + 2), int(y)), 1)


def nocturnus_desenhar(v, d, tela, t):
    rnd = __import__("random").Random(9)
    if t < NOCT_SOBE:  # a NUVEM de morcegos chegando e cobrindo o derrotado
        k = min(1, t / NOCT_PEGA)
        for i in range(22):
            ax, ay = rnd.uniform(-400, 400), rnd.uniform(-300, -60)
            cx = d.x + rnd.uniform(-40, 40) + math.sin(t * 0.3 + i) * 10
            cy = d.y - 50 + rnd.uniform(-40, 30) + math.cos(t * 0.25 + i) * 8
            _morceguinho(tela, ax + (cx - ax) * k + d.x * (1 - k) * 0, ay * (1 - k) + cy * k, t, i)
    else:  # lá no alto: o CASULO pendurado de cabeça pra baixo, balançando (com os pezinhos pra cima)
        x = d.x + math.sin(t * 0.06) * 10
        pygame.draw.line(tela, (60, 50, 70), (d.x, 40), (x, 90), 2)
        casulo = pygame.Rect(0, 0, 34, 70)
        casulo.midtop = (int(x), 88)
        pygame.draw.ellipse(tela, (16, 10, 22), casulo.inflate(4, 4))
        pygame.draw.ellipse(tela, (60, 44, 80), casulo)
        for i in range(3):  # os morcegos que ficaram em volta
            _morceguinho(tela, x + (i - 1) * 30, 80 + math.sin(t * 0.2 + i) * 6, t, i)
        if t < 150:
            texto_tela(tela, "PENDURADO!", (d.x, 220), (200, 160, 255))


# =====================================================================
# SILVANUS: ADUBO! (as raízes saem da terra, abraçam o derrotado e puxam ele pra baixo... e no lugar nasce uma FLOR)
# =====================================================================
SILV_RAIZ, SILV_PUXA, SILV_SOME, SILV_BROTA = 16, 40, 92, 104


def silvanus_passo(v, d, t, jogo):
    pose(v, "s_raizes" if t < SILV_SOME else "s_ergue")
    if t == SILV_RAIZ:
        som.tocar("terra", 0.8)
        poeira(jogo, d.x, 6)
    if SILV_PUXA <= t < SILV_SOME:  # puxado pra dentro da terra, aos trancos
        d.cortar_chao = True
        u = (t - SILV_PUXA) / (SILV_SOME - SILV_PUXA)
        d.y = CHAO + (u ** 1.4) * 60 * d.s + (3 if (t // 4) % 2 else 0)
        if t % 8 == 0:
            poeira(jogo, d.x, 3)
    if t == SILV_SOME:
        d.esconde = True
        som.tocar("queda", 0.5)
    if t == SILV_BROTA:
        som.tocar("blip", 0.6)


def _raiz_curva(tela, base, ponta, curva, grosso):
    pts = []
    for i in range(9):
        k = i / 8
        x = base[0] + (ponta[0] - base[0]) * k
        y = base[1] + (ponta[1] - base[1]) * k - math.sin(k * math.pi) * curva
        pts.append((x, y))
    pygame.draw.lines(tela, (40, 26, 16), False, pts, grosso + 4)
    pygame.draw.lines(tela, (112, 78, 46), False, pts, grosso)
    pygame.draw.lines(tela, (150, 110, 70), False, pts[:5], max(1, grosso // 3))


def silvanus_desenhar(v, d, tela, t):
    s = d.s
    meio = d.extra.setdefault("adubo_x", ponto_do_caido(d, "pc")[0])  # (o meio do corpo deitado)
    if SILV_RAIZ <= t < SILV_SOME:  # as RAÍZES saindo da terra e abraçando o derrotado (e afundando junto)
        cresce = suave(min(1, (t - SILV_RAIZ) / (SILV_PUXA - SILV_RAIZ)))
        if t >= SILV_PUXA:
            cresce *= 1 - suave((t - SILV_PUXA) / (SILV_SOME - SILV_PUXA))
        corpo_y = min(CHAO - 4, d.y - 18 * s)
        for i, (dx, lado) in enumerate(((-60, 1), (-25, 1), (10, -1), (45, -1), (-45, -1), (70, -1))):
            base = (meio + dx * s - lado * 40 * s, CHAO + 4)
            ponta = (base[0] + lado * 80 * s * cresce, corpo_y + (CHAO - corpo_y) * (1 - cresce))
            _raiz_curva(tela, base, ponta, (40 + i * 6) * s * cresce, max(3, int((7 - i % 3) * s / 1.4)))
    if t >= SILV_PUXA:  # o MONTINHO de terra fofa (adubada)
        k = min(1, (t - SILV_PUXA) / 30)
        pygame.draw.ellipse(tela, (30, 20, 12), (meio - 50 * s, CHAO - 14 * s * k - 4, 100 * s, 28 * s * k + 8))
        pygame.draw.ellipse(tela, (96, 66, 38), (meio - 46 * s, CHAO - 12 * s * k - 2, 92 * s, 24 * s * k + 4))
        for i in range(5):
            pygame.draw.circle(tela, (70, 48, 28), (int(meio + (i - 2) * 16 * s), int(CHAO - 4 * s * k)), max(1, int(2 * s)))
    if t >= SILV_BROTA:  # a FLOR nascendo no lugar: o broto sobe, as folhas abrem e a flor desabrocha
        u = suave(min(1, (t - SILV_BROTA) / 30))
        s *= 1.6  # (a flor é grandona)
        abre = suave(max(0, min(1, (t - SILV_BROTA - 22) / 16)))
        topo = (meio, CHAO - 12 * s - 70 * s * u)
        pygame.draw.line(tela, (20, 40, 16), (meio, CHAO - 10 * s), topo, max(3, int(5 * s)))
        pygame.draw.line(tela, (80, 160, 60), (meio, CHAO - 10 * s), topo, max(2, int(3 * s)))
        for lado in (-1, 1):  # as duas folhinhas
            fy = CHAO - 12 * s - 34 * s * u
            pts = [(meio, fy), (meio + lado * 26 * s * u, fy - 14 * s * u), (meio + lado * 10 * s * u, fy - 4 * s * u)]
            if u > 0.1:
                contorno(tela, (90, 180, 70), pts)
        if abre > 0:
            for i in range(6):  # as pétalas (rosa) e o miolo (amarelo)
                a = i * math.tau / 6 + t * 0.01
                px, py = topo[0] + math.cos(a) * 12 * s * abre, topo[1] + math.sin(a) * 12 * s * abre
                pygame.draw.circle(tela, (16, 12, 20), (int(px), int(py)), int(9 * s * abre) + 2)
                pygame.draw.circle(tela, (250, 130, 190), (int(px), int(py)), max(1, int(9 * s * abre)))
            pygame.draw.circle(tela, (16, 12, 20), (int(topo[0]), int(topo[1])), int(7 * s * abre) + 2)
            pygame.draw.circle(tela, (255, 220, 80), (int(topo[0]), int(topo[1])), max(1, int(7 * s * abre)))


# =====================================================================
# KATCHADE: FLOR FECHADA! (pétalas gigantes saem do chão em volta do derrotado e FECHAM nele, que nem um botão
# de flor; depois o botão balança... e solta umas pétalas)
# =====================================================================
KAT_BROTA, KAT_FECHA, KAT_PRONTO = 14, 50, 80


def katchade_passo(v, d, t, jogo):
    pose(v, "k_reza")
    if t == KAT_BROTA:
        som.tocar("terra", 0.6)
        poeira(jogo, d.x, 6)
    if t == KAT_FECHA:
        som.tocar("puf", 0.7)
    if t >= KAT_FECHA + 8:
        d.esconde = True  # (já está dentro do botão)
    if t == KAT_PRONTO:
        som.tocar("blip", 0.6)


def katchade_desenhar(v, d, tela, t):
    if t < KAT_BROTA:
        return
    s = d.s
    if t < KAT_FECHA or "flor_x" not in d.extra:  # (segue o corpo até fechar: ele ainda pode estar escorregando)
        d.extra["flor_x"] = (ponto_do_caido(d, "pc")[0] + ponto_do_caido(d, "qd")[0]) / 2
    meio = d.extra["flor_x"]
    sobe = suave(min(1, (t - KAT_BROTA) / 22))
    fecha = suave(max(0, min(1, (t - KAT_BROTA - 16) / (KAT_FECHA - KAT_BROTA - 16))))
    balanca = math.sin(t * 0.12) * 4 * s if t >= KAT_PRONTO else 0
    alto = 110 * s * sobe
    # o caule e as folhas
    pygame.draw.line(tela, (30, 60, 26), (meio, CHAO + 4), (meio + balanca, CHAO - 14 * s), max(4, int(8 * s)))
    for lado in (-1, 1):
        pts = [(meio, CHAO - 4), (meio + lado * 70 * s * sobe, CHAO - 22 * s * sobe), (meio + lado * 30 * s, CHAO - 2)]
        contorno(tela, (80, 150, 66), pts)
    # as 5 pétalas: abertas (deitadas pros lados) -> fechadas (em pé, juntinhas formando o botão)
    for k, lado in enumerate((-1.0, -0.55, 0.0, 0.55, 1.0)):
        ang_aberta = lado * 1.35
        ang = ang_aberta * (1 - fecha) + lado * 0.18 * fecha
        larg = (34 if k != 2 else 40) * s
        base = (meio + lado * 18 * s * (1 - fecha) + balanca, CHAO - 10 * s)
        dx, dy = math.sin(ang), -math.cos(ang)
        ponta = (base[0] + dx * alto, base[1] + dy * alto)
        nx, ny = -dy, dx
        pts = [base, (base[0] + dx * alto * 0.5 + nx * larg / 2, base[1] + dy * alto * 0.5 + ny * larg / 2), ponta,
               (base[0] + dx * alto * 0.5 - nx * larg / 2, base[1] + dy * alto * 0.5 - ny * larg / 2)]
        cor = (246, 170, 206) if k % 2 == 0 else (230, 130, 182)
        contorno(tela, cor, pts)
        pygame.draw.line(tela, (255, 226, 240), base, ((base[0] + ponta[0]) / 2, (base[1] + ponta[1]) / 2),
                         max(1, int(2 * s)))
    if t >= KAT_PRONTO and (t // 10) % 3 == 0:  # pétalas soltando do botão
        for k in range(3):
            u = (t + k * 7) % 30
            x = meio + (k - 1) * 20 * s + math.sin(t * 0.1 + k) * 10 * s
            y = CHAO - alto + u * 3 * s
            pygame.draw.circle(tela, (250, 160, 202), (int(x), int(y)), max(2, int(3 * s)))


FINISHES = {
    "MAX-10": dict(passo=max_passo, desenhar=max_desenhar, nome="RECICLADO!"),
    "RIB": dict(passo=rib_passo, desenhar=rib_desenhar, nome="PRESO NO CHÃO!"),
    "TRAFO": dict(passo=trafo_passo, desenhar=trafo_desenhar, nome="ENTERRADO!"),
    "KING RIP": dict(passo=king_passo, desenhar=king_desenhar, nome="HORA DO CHÁ!"),
    "CANNAN": dict(passo=cannan_passo, desenhar=cannan_desenhar, nome="ENTREGA AÉREA!"),
    "FINN": dict(passo=finn_passo, desenhar=finn_desenhar, nome="VIROU SAPO!"),
    "KUN": dict(passo=kun_passo, desenhar=kun_desenhar, nome="PRO BARALHO!"),
    "TROMOS": dict(passo=xeno_passo, desenhar=xeno_desenhar, nome="CASULO!"),
    "TAI": dict(passo=tai_passo, desenhar=tai_desenhar, nome="SENTADA!"),
    "TAMER": dict(passo=tamer_passo, desenhar=tamer_desenhar, nome="UIVO DA ALCATEIA!"),
    "JOHN": dict(passo=john_passo, desenhar=john_desenhar, nome="SUMIU!"),
    "RIBBAT": dict(passo=ribbat_passo, desenhar=ribbat_desenhar, nome="REI DA CABEÇA!"),
    "CRÁQUEN": dict(passo=craquen_passo, desenhar=craquen_desenhar, nome="PRO FUNDO DO MAR!"),
    "MAGNUS": dict(passo=magnus_passo, desenhar=magnus_desenhar, nome="TOSTADO!"),
    "SPHYRUS": dict(passo=sphyrus_passo, desenhar=sphyrus_desenhar, nome="VIROU ISCA!"),
    "FRIGANTUS": dict(passo=frigantus_passo, desenhar=frigantus_desenhar, nome="SOTERRADO!"),
    "INAZUMANEKO": dict(passo=inazumaneko_passo, desenhar=inazumaneko_desenhar, nome="CORTE DE CABELO!"),
    "NOCTURNUS": dict(passo=nocturnus_passo, desenhar=nocturnus_desenhar, nome="PENDURADO!"),
    "SILVANUS": dict(passo=silvanus_passo, desenhar=silvanus_desenhar, nome="ADUBO!"),
    "KATCHADE": dict(passo=katchade_passo, desenhar=katchade_desenhar, nome="FLOR FECHADA!"),
}


def de(l):
    return FINISHES.get(l.f.get("nome_base", l.f["nome"]).replace("SOMBRA DO ", ""))
