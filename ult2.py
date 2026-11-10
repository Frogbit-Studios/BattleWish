"""As 2ª ULTIMATES (criadas pelo Gomes, uma por lutador). Saem com a barra AMARELA cheia: M3 + C
(ou M3 2x + Z / LT + RT). Regra dele: ~1,5x a 1ª, com uma cena mais épica — é difícil de pegar, então é FORTE.

  MAX-10   CHUVA DE MÍSSEIS: 12 mini-mísseis teleguiados + explosão final (45)
  RIB      KAGE BUNSHIN: 5 clones juntam as mãos e viram uma SHURIKEN GIGANTE (50)
  TRAFO    BRAÇOS DE TERRA saindo em lugares aleatórios perto do adversário (24 x 1,5, dá pra fugir de alguns)
  KING RIP ESPÍRITO DO DOJO: um DRAGÃO DE ENERGIA AZUL dá a volta na tela e atravessa o adversário (55)
  CANNAN   A MINIGUN: cai do céu e ele desce o pipoco (55), mas o coice tira 10 dele
  FINN     GOLEM DE PEDRA: soco de 15 e fica 15 s ajudando nos especiais (6 cada)
  KUN      TSUNAMI DE CARTAS: engole, corta e prensa na parede (55)
  TROMOS   CAÇADA NO ESCURO: apaga a luz; ele vê (verde) e bate +5 por golpe por 10 s
  TAI      TERREMOTO: 3 pisões que deixam tonto + 1 gigante que joga longe (60)
  TAMER    LUA CHEIA: o lobo vira LOBISOMEM e luta junto por 10 s
  JOHN     A RAVINA: some na fumaça, cai numa ravina enorme e volta saindo da cartola (55)
  CRÁQUEN  com água: O KRAKEN DESPERTA (60) / sem água: TRIPULAÇÃO FANTASMA (5 marujos, 1 hit a cada 5 s)
  MAGNUS   MODO FORNALHA: 10 s em chamas, cada golpe queima e PRENDE
  SPHYRUS  uma por passiva: NATAÇÃO = O ANCESTRAL (65) / ELETRORRECEPÇÃO = CARDUME (60) / FRENESI = TORNADO (60)
  RIBBAT   não tem ("NÃO PRECISA")
Tudo que muda a luta acontece no passo (igual nos dois PCs do online); o desenho só desenha.
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from golpes import GOLPES, suave
from lutador import Projetil
from max10 import brilho, fumaca

AGUA = ("PÂNTANO", "NAVIO FANTASMA", "PRAIA DA ILHA")
VEEM_NO_ESCURO = ("MAGNUS", "MAX-10", "TAMER", "TROMOS", "TRAFO", "SPHYRUS")  # (bicho, mutante ou robô)
TEMPO_BUFF = 10 * FPS


def nome_de(l):
    return l.f.get("nome_base", l.f["nome"]).replace("SOMBRA DO ", "")


def outro_de(l, jogo):
    return jogo.L[1] if jogo.L[0] is l else jogo.L[0]


def pode_pegar(o, alto=90):
    return o.inv <= 0 and o.estado not in ("caido", "voando", "agarrado") and o.y > CHAO - alto


def pega(o, pose="golpeado"):
    o.mudar("agarrado")
    o.golpe = None
    o.sobrepor = dict(o.poses[pose])
    o.vx = o.vy = 0


def solta(o, vx, vy):
    o.sobrepor = {}
    o.esconde = False
    o.mudar("voando")
    o.vx, o.vy = vx, vy


def bate(l, o, jogo, dano, nome, ultimo=False, forte=False):
    """Hit de ultimate em quem está preso (só o último pode nocautear)."""
    o.levar(dano, l, GOLPES[nome])
    if not ultimo:
        o.vida = max(1, o.vida)
    o.tremor_hit = 6
    jogo.faisca(o.x + random.uniform(-12, 12), o.y - 50 * o.s, False, forte or ultimo)
    som.tocar("ko" if ultimo else "soco", 0.6 if ultimo else 0.45)
    if ultimo:
        jogo.tremer(14)


def acerta(l, o, jogo, nome):
    """Acerto normal (passa pela defesa, parry...)."""
    res = o.receber(GOLPES[nome], 1 if o.x >= l.x else -1, l, l.f["forca"])
    if res == "hit":
        jogo.faisca(o.x, o.y - 50 * o.s, False, True)
    return res


def _dano(nome, dano, **k):
    g = dict(dano=dano, hit=30, defe=12, emp=3, nivel="medio", especial=True, ultimate=True, ultimate2=True)
    g.update(k)
    GOLPES[nome] = g


def _registra(nome, logica, efeito=None, quadros=None, **k):
    g = dict(base="parado", pose="parado", caixa=None, especial=True, ultimate=True, ultimate2=True, ini=1, ativo=1,
             rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", logica=logica, ia="ultimate2",
             quadros=quadros or [(0, "parado")])
    if efeito:
        g["efeito"] = efeito
    g.update(k)
    g["total"] = 9999
    GOLPES[nome] = g


def tela_toda(l):
    l.memo["tela_toda"] = True


def camera(jogo, zoom, x, y):
    """Pede a câmera de cinema (faixas pretas + zoom) neste quadro. (Faz parte da luta: igual nos dois PCs.)"""
    if hasattr(jogo, "camera_alvo"):
        jogo.camera_alvo = (zoom, max(LARGURA / (2 * zoom), min(LARGURA - LARGURA / (2 * zoom), x)),
                            max(ALTURA / (2 * zoom), min(ALTURA - ALTURA / (2 * zoom), y)))


def impacto(jogo, quadros=10, tremor=16, clarao=0):
    """O golpe forte: congela um instante, treme e (se pedir) pisca branco."""
    if hasattr(jogo, "parada"):
        jogo.parada = max(jogo.parada, quadros)
    jogo.tremer(tremor)
    if clarao and hasattr(jogo, "clarao"):
        jogo.clarao = max(jogo.clarao, clarao)


# =====================================================================
# A APRESENTAÇÃO da 2ª ultimate (faixa dourada com o retrato e o nome) — só desenho
# =====================================================================
_retratos = {}


def nome_ult2(l, jogo):
    nome = nome_de(l)
    if nome == "SPHYRUS":
        import habilidades as hab
        hs = hab.ativas(l)
        return "TORNADO DE LÂMINAS" if "frenesi" in hs else "CARDUME" if "eletro" in hs else "O ANCESTRAL"
    if nome == "CRÁQUEN":
        cena = getattr(jogo, "cena", None)
        return "O KRAKEN DESPERTA" if cena and cena.nome in AGUA else "TRIPULAÇÃO FANTASMA"
    return NOMES.get(nome, "2ª ULTIMATE")


def desenhar_cartao(tela, l, jogo, k):
    from efeitos import texto, texto_grande
    from selecao import retrato
    entra = suave(min(1, k / 0.16))
    sai = suave(max(0, (k - 0.86) / 0.14))
    desloca = -LARGURA * (1 - entra) + LARGURA * 1.2 * sai
    yc, h = ALTURA // 2 - 6, 150
    ouro, ouro_esc, fundo = (255, 206, 70), (170, 110, 20), (18, 12, 8)
    camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    faixa = [(desloca - 40, yc - h // 2 + 24), (desloca + LARGURA + 40, yc - h // 2),
             (desloca + LARGURA + 40, yc + h // 2 - 24), (desloca - 40, yc + h // 2)]
    pygame.draw.polygon(camada, (*fundo, 235), faixa)
    t = getattr(jogo, "t_total", 0)
    for i in range(16):  # os riscos de velocidade correndo dentro da faixa
        x = (i * 97 + t * 26) % (LARGURA + 200) - 100 + desloca
        y = yc - h // 2 + 30 + (i * 37) % (h - 60)
        pygame.draw.line(camada, (*ouro_esc, 110), (x, y), (x + 120, y - 6), 2)
    tela.blit(camada, (0, 0))
    for dy, borda in ((-1, faixa[:2]), (1, faixa[2:])):  # as bordas douradas
        pygame.draw.line(tela, ouro, borda[0], borda[1], 6)
        pygame.draw.line(tela, (255, 245, 200), borda[0], borda[1], 2)
    # o retrato (encaixa entrando)
    nome = nome_de(l)
    if nome not in _retratos:
        _retratos[nome] = retrato(l.f, 132)
    rx = int(80 + desloca)
    ry = yc - 66
    pygame.draw.rect(tela, ouro, (rx - 5, ry - 5, 142, 142), border_radius=8)
    tela.blit(_retratos[nome], (rx, ry))
    pygame.draw.rect(tela, (40, 26, 6), (rx, ry, 132, 132), 3)
    # os textos
    tx = int(560 + desloca)
    if k > 0.08:
        texto(tela, "2ª ULTIMATE", 20, ouro, (tx, yc - 46))
    if k > 0.14:
        soco = 1 + 0.3 * max(0.0, 1 - (k - 0.14) / 0.08)  # o nome entra "batendo"
        titulo = nome_ult2(l, jogo)
        tam = 52 if len(titulo) <= 16 else 40 if len(titulo) <= 22 else 32
        texto_grande(tela, titulo + "!", tam, (255, 226, 110), (tx, yc + 6), soco, contorno=(70, 30, 0))
        texto(tela, nome, 18, (230, 220, 200), (tx, yc + 50))
    if k > 0.94:  # clarão no fim (e a ultimate sai)
        branco = pygame.Surface((LARGURA, ALTURA))
        branco.fill((255, 250, 230))
        branco.set_alpha(int(255 * (k - 0.94) / 0.06))
        tela.blit(branco, (0, 0))


# =====================================================================
# EXPLOSÃO (usada por várias): bola de fogo em camadas + onda de choque + pedacinhos
# =====================================================================
def explosao(tela, x, y, u, tam=1.0, semente=0):
    """Explosão de verdade: bolotas de fogo irregulares que viram fumaça subindo (u = quadros desde o BUM)."""
    dura = 22 + int(8 * tam)
    if u < 0 or u > dura:
        return
    k = u / dura
    rnd = random.Random(int(x) * 7 + int(y) * 13 + semente)
    if u < 3:  # o clarão
        brilho(tela, (int(x), int(y)), int(38 * tam), (255, 240, 170), 150)
    if u < 10:  # a onda de choque
        pygame.draw.circle(tela, (255, 240, 210), (int(x), int(y)), int((20 + u * 9) * tam), max(1, int(3 - u / 4)))
    for i in range(9):
        a = rnd.uniform(0, math.tau)
        d = rnd.uniform(0.2, 0.9) * 26 * tam * suave(min(1, u / 6))
        px, py = x + math.cos(a) * d, y + math.sin(a) * d * 0.7 - u * (0.8 + rnd.random()) * tam
        r = (rnd.uniform(12, 22) * tam) * (0.6 + 0.6 * suave(min(1, u / 5)))
        if k < 0.45:  # fogo: amarelo no meio, laranja e vermelho por fora
            q = k / 0.45
            fora = i % 3
            cor = ((255, int(225 - 90 * q), int(70 - 60 * q)), (255, int(140 - 70 * q), 20),
                   (int(220 - 40 * q), int(60 - 30 * q), 20))[fora]
        else:  # fumaça escurecendo e sumindo
            q = (k - 0.45) / 0.55
            c = int(120 - 50 * q)
            cor = (c, c - 6, c - 10)
            r *= 1 + q * 0.6
        pygame.draw.circle(tela, cor, (int(px), int(py)), max(1, int(r * (1 - 0.6 * max(0, k - 0.8) / 0.2))))
    for i in range(5):  # faíscas voando
        a = rnd.uniform(-math.pi, 0)
        d = (12 + u * 6) * tam
        if u < 14:
            pygame.draw.circle(tela, (255, 220, 120), (int(x + math.cos(a) * d), int(y + math.sin(a) * d + u * u * 0.12)),
                               max(1, int(2.5 * tam)))


# =====================================================================
# MAX-10: CHUVA DE MÍSSEIS
# =====================================================================
class Missil(Projetil):
    """Sobe, some lá em cima e cai do céu TELEGUIADO no adversário (deixa um rastro de fumaça)."""

    def __init__(self, dono, x, y, alvo, k, golpe):
        super().__init__(dono, x, y, dono.dir, golpe)
        self.alvo = alvo
        self.k = k
        self.fase = "sobe"
        self.espera = 0
        self.vx = random.uniform(-2.5, 2.5) + dono.dir * 1.5
        self.vy = -15
        self.raio = golpe["raio"]
        self.rastro = []
        self.grande = golpe.get("final", False)

    def update(self):
        self.t += 1
        self.rastro = (self.rastro + [(self.x, self.y)])[-14:]
        if self.fase == "sobe":
            self.vy -= 0.3
            self.x += self.vx
            self.y += self.vy
            if self.y < -60:  # sumiu lá em cima: espera a vez dele de cair
                self.fase, self.espera, self.rastro = "espera", 2 + self.k * 3, []
        elif self.fase == "espera":
            self.espera -= 1
            if self.espera <= 0:
                lado = (-1) ** self.k
                self.x = self.alvo.x + lado * (40 + (self.k % 4) * 30) + self.dono.dir * 30
                self.y = -40
                self.fase = "desce"
                self.vx, self.vy = 0, 12
        else:  # cai TELEGUIADO
            ax, ay = self.alvo.x, self.alvo.y - 50 * self.alvo.s
            dx, dy = ax - self.x, ay - self.y
            d = math.hypot(dx, dy) or 1
            v = 11 if self.grande else 15
            self.vx += (dx / d * v - self.vx) * 0.09
            self.vy += (dy / d * v - self.vy) * 0.09
            self.x += self.vx
            self.y += self.vy
            if self.y >= CHAO - 6:  # errou: explode no chão
                self.vivo = False
                boom(self.dono, self.x, CHAO - 6, self.grande)
        if self.t > 400:
            self.vivo = False

    def rect(self):
        if self.fase != "desce":  # (subindo e esperando não acerta ninguém)
            return pygame.Rect(-999, -999, 1, 1)
        return super().rect()

    def desenhar(self, tela):
        if self.fase == "espera":
            return
        n = len(self.rastro)
        g = 1.4 if self.grande else 1
        for i, (x, y) in enumerate(self.rastro):  # o rastro de fumaça
            k = i / max(1, n)
            c = int(150 + 80 * k)
            pygame.draw.circle(tela, (c, c, c), (int(x), int(y)), max(2, int((2 + 6 * (1 - k)) * g)))
        a = math.atan2(self.vy, self.vx)
        c, s = math.cos(a), math.sin(a)
        comp = 30 if self.grande else 20
        w = 6 if self.grande else 4
        cauda = (self.x - c * comp, self.y - s * comp)
        chama = 8 + (self.t % 3) * 4
        fogo = (cauda[0] - c * chama, cauda[1] - s * chama)
        brilho(tela, (int(cauda[0]), int(cauda[1])), 12 if self.grande else 8, (255, 170, 60), 160)
        pygame.draw.line(tela, (255, 220, 120), cauda, fogo, w)
        for lado in (-1, 1):  # as aletas
            pygame.draw.polygon(tela, (40, 40, 48), [(cauda[0] - s * lado * w * 1.6, cauda[1] + c * lado * w * 1.6),
                                                     (cauda[0] + c * 6, cauda[1] + s * 6), cauda])
        pygame.draw.line(tela, (24, 24, 30), cauda, (self.x, self.y), w + 3)
        pygame.draw.line(tela, (225, 228, 236), cauda, (self.x, self.y), w)
        ponta = (200, 30, 30) if self.grande else (230, 60, 40)
        pygame.draw.circle(tela, ponta, (int(self.x), int(self.y)), max(2, w // 2 + 1))


def boom(dono, x, y, grande=False):
    """Guarda a explosão pra desenhar (o desenho só lê)."""
    if dono.estado == "ataque" and dono.nome_golpe == "max_ult2":
        dono.memo.setdefault("booms", []).append((dono.t, x, y, grande))


def missil_acertou(dono, alvo, jogo, res):
    boom(dono, alvo.x, alvo.y - 50 * alvo.s, False)
    som.tocar("explosao", 0.4)


def final_acertou(dono, alvo, jogo, res):
    boom(dono, alvo.x, alvo.y - 50 * alvo.s, True)
    if dono.estado == "ataque" and dono.nome_golpe == "max_ult2":
        dono.memo["final_acertou"] = dono.t
    impacto(jogo, 12, 24, 5)
    som.tocar("ko", 0.8)
    som.tocar("explosao")


M_ABRE, M_N, M_CADA = 22, 12, 3


def ombros(l):
    """Onde ficam os dois lançadores (em cima dos ombros, no espaço da pose)."""
    p = l.pose_vista or l.pose_atual()
    pcx, pcy = p["pc"]
    return [(pcx - 8, pcy + 6), (pcx + 6, pcy + 8)]


def max_ult2(l, outro, jogo):
    t = l.t
    m = l.memo
    tela_toda(l)
    l.vx = 0
    l.fisica(jogo)
    if t < M_ABRE:  # abre os lançadores (câmera nele)
        camera(jogo, 1.4, l.x, l.y - 80 * l.s)
        if t == 2:
            som.tocar("carga", 0.8)
        if t == 12:
            som.tocar("defesa", 0.6)  # (clack!)
        return
    k = (t - M_ABRE) // M_CADA
    lanca = (t - M_ABRE) % M_CADA == 0 and k < M_N
    if t < M_ABRE + M_N * M_CADA + 10:
        camera(jogo, 1.15, l.x + l.dir * 60, l.y - 120 * l.s)
    else:
        camera(jogo, 1.2, (l.x + outro.x) / 2 + l.dir * 40, outro.y - 90 * outro.s)
    if lanca:
        final = k == M_N - 1
        lado = k % 2
        sx, sy = ombros(l)[lado]
        x, y = l.x + l.dir * sx * l.s, l.y - (sy + 18) * l.s
        nome = "max_missil_final" if final else "max_missil"
        jogo.projeteis.append(Missil(l, x, y, outro, k, GOLPES[nome]))
        som.tocar("foguete", 0.5 if final else 0.3)
        fumaca(jogo, x, y + 6, 5, (200, 200, 206), 2.5, 0.4)
        m["clarao"] = (t, lado)
        if final:
            m["ultimo_saiu"] = t
    if "ultimo_saiu" in m:
        fim = max([m["ultimo_saiu"] + 40, m.get("final_acertou", -99) + 34] +
                  [b[0] + 24 for b in m.get("booms", [])])
        vivo = any(isinstance(p, Missil) and p.vivo and p.dono is l for p in jogo.projeteis)
        if (t >= fim and not vivo) or t > m["ultimo_saiu"] + 200:
            return "fim"


def max_ult2_atras(l, tela):
    """Os lançadores saindo de trás dos ombros e abrindo a tampa."""
    t = l.t
    sobe = suave(min(1, t / 10))
    abre = suave(min(1, max(0, (t - 8) / 8)))
    if "ultimo_saiu" in l.memo:
        u = t - l.memo["ultimo_saiu"]
        sobe *= 1 - suave(min(1, max(0, (u - 20) / 12)))
        abre *= 1 - suave(min(1, max(0, (u - 10) / 10)))
    if sobe <= 0.01:
        return
    s = l.s
    for lado, (sx, sy) in enumerate(ombros(l)):
        bx, by = l.x + l.dir * sx * s, l.y - (sy - 2 + 10 * sobe) * s
        w, h = 13 * s, 14 * s
        caixa = pygame.Rect(0, 0, w, h)
        caixa.midbottom = (int(bx), int(by + h * 0.4))
        pygame.draw.rect(tela, (20, 20, 26), caixa.inflate(4, 4), border_radius=3)
        pygame.draw.rect(tela, (120, 124, 134), caixa, border_radius=3)
        pygame.draw.line(tela, (230, 190, 40), (caixa.x + 2, caixa.bottom - 4), (caixa.right - 2, caixa.bottom - 4), 2)
        for i in range(3):  # os tubos
            cx = caixa.x + (i + 0.5) * w / 3
            pygame.draw.circle(tela, (30, 30, 36), (int(cx), caixa.y + 5), max(2, int(2.6 * s)))
            if abre > 0.5:
                pygame.draw.circle(tela, (255, 80, 50), (int(cx), caixa.y + 5), max(1, int(1.6 * s)))
        ang = abre * 2.0  # a tampa abrindo pra trás
        dx, dy = -l.dir * math.sin(ang) * w, -math.cos(ang) * w * 0.3
        tampa = [(caixa.x, caixa.y), (caixa.right, caixa.y), (caixa.right + dx, caixa.y + dy - 3),
                 (caixa.x + dx, caixa.y + dy - 3)]
        pygame.draw.polygon(tela, (90, 94, 104), tampa)
        pygame.draw.polygon(tela, (20, 20, 26), tampa, 2)


def max_ult2_efeito(l, tela):
    t = l.t
    m = l.memo
    cl = m.get("clarao")
    if cl and t - cl[0] < 4:  # o clarão do disparo
        sx, sy = ombros(l)[cl[1]]
        brilho(tela, (int(l.x + l.dir * sx * l.s), int(l.y - (sy + 22) * l.s)), int(18 * l.s), (255, 220, 140), 200)
    for t0, x, y, grande in m.get("booms", []):
        explosao(tela, x, y, t - t0, 2.2 if grande else 0.8)


_dano("max_missil", 3, hit=16, defe=6, emp=1, proj=True, raio=10, vel=13, varios=True, atravessa=True,
      ao_acertar=missil_acertou, sem_parada=True)
_dano("max_missil_final", 12, hit=30, emp=4, proj=True, raio=16, vel=13, varios=True, atravessa=True, final=True,
      derruba=True, voo=(8, 12), ao_acertar=final_acertou)
_registra("max_ult2", max_ult2, max_ult2_efeito,
          [(0, "parado"), (6, "m_agacha"), (M_ABRE - 2, "m_agacha"), (M_ABRE + 4, "vitoria"),
           (M_ABRE + M_N * M_CADA + 6, "vitoria"), (M_ABRE + M_N * M_CADA + 20, "m_alcanca"), (9999, "m_alcanca")],
          efeito_atras=max_ult2_atras)


# =====================================================================
# RIB: KAGE BUNSHIN + SHURIKEN GIGANTE
# =====================================================================
R_SELO, R_POOF, R_PULA, R_RODA, R_SOLTA = 10, (12, 15, 18, 21, 24), 30, 48, 70
R_VEL = 10
R_MOI, R_MOI_HITS = 5, 5
CLONES_X = (-120, -60, 60, 120, 180)


def desenha_shuriken(tela, x, y, r, ang, cor=(196, 204, 220), brilha=0):
    if brilha:
        brilho(tela, (int(x), int(y)), int(r * 1.15), (190, 230, 255), min(70, brilha // 2))
    pts = []
    for i in range(8):
        a = ang + i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.3
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    pygame.draw.polygon(tela, (20, 20, 28), [(x + (px - x) * 1.08, y + (py - y) * 1.08) for px, py in pts])
    pygame.draw.polygon(tela, cor, pts)
    for i in range(0, 8, 2):  # o fio da lâmina (o lado claro)
        a = ang + i * math.pi / 4
        pygame.draw.line(tela, (250, 252, 255), (x + math.cos(a) * r * 0.3, y + math.sin(a) * r * 0.3),
                         (x + math.cos(a) * r * 0.95, y + math.sin(a) * r * 0.95), max(1, int(r * 0.06)))
    pygame.draw.circle(tela, (20, 20, 28), (int(x), int(y)), max(2, int(r * 0.17)))
    pygame.draw.circle(tela, (120, 128, 140), (int(x), int(y)), max(1, int(r * 0.1)))


def rib_centro(l):
    return l.x + l.dir * 70 * l.s, CHAO - 210


def rib_ult2(l, outro, jogo):
    t = l.t
    m = l.memo
    tela_toda(l)
    l.vx = 0
    l.fisica(jogo)
    cx, cy = rib_centro(l)
    if t < R_PULA:  # selo de mão e os clones aparecendo (câmera nele)
        camera(jogo, 1.3, l.x + l.dir * 30, l.y - 70 * l.s)
        if t in R_POOF:
            i = R_POOF.index(t)
            fumaca(jogo, l.x + l.dir * CLONES_X[i], CHAO - 40, 10, (235, 235, 245), 3, -1.2)
            som.tocar("puf", 0.6)
        return
    if t < R_SOLTA:  # no alto, de mãos dadas em roda, e a shuriken gigante nascendo no meio
        camera(jogo, 1.0, LARGURA / 2, ALTURA / 2 - 30)
        if t == R_PULA:
            som.tocar("pulo")
        if t == R_RODA:
            som.tocar("carga")
        if t > R_RODA and t % 6 == 0:
            som.tocar("vento", 0.4)
        return
    if t == R_SOLTA:  # LÁ VAI!
        m["sh"] = [cx, cy]
        som.tocar("shuriken")
        som.tocar("vento")
        for i in range(5):
            a = i * math.tau / 5
            fumaca(jogo, cx + math.cos(a) * 70, cy + math.sin(a) * 40, 5, (235, 235, 245), 2, -0.5)
    if "sh" in m and "pegou" not in m:
        alvo = (outro.x, outro.y - 60 * outro.s)
        sx, sy = m["sh"]
        if "mira" not in m:  # desce reto na direção do peito dele (dá pra pular por cima no último instante)
            d = math.hypot(alvo[0] - sx, alvo[1] - sy) or 1
            m["mira"] = ((alvo[0] - sx) / d * R_VEL, (alvo[1] - sy) / d * R_VEL)
        vx, vy = m["mira"]
        if sy > CHAO - 70:
            vy = 0
        m["sh"] = [sx + vx, min(CHAO - 60, sy + vy)]
        camera(jogo, 1.15, m["sh"][0], m["sh"][1])
        if abs(outro.x - m["sh"][0]) < 46 and abs((outro.y - 60 * outro.s) - m["sh"][1]) < 60 and pode_pegar(outro, 400):
            m["pegou"] = t
            pega(outro)
            som.tocar("quebra", 0.6)
        elif not (PAREDE_E - 120 < m["sh"][0] < PAREDE_D + 120):
            m["errou"] = t
            m.pop("sh")
    if "pegou" in m:  # MÓI: a shuriken fica girando em cima dele
        u = t - m["pegou"]
        m["sh"] = [outro.x, outro.y - 60 * outro.s]
        camera(jogo, 1.35, outro.x, outro.y - 70 * outro.s)
        if u % R_MOI == 0 and u // R_MOI < R_MOI_HITS:
            bate(l, outro, jogo, 6, "rib_moendo")
        if u == R_MOI * R_MOI_HITS + 6:  # e explode
            bate(l, outro, jogo, 20, "rib_moendo", ultimo=True)
            impacto(jogo, 10, 20, 4)
            solta(outro, l.dir * 9, -11)
            fumaca(jogo, outro.x, outro.y - 60, 16, (235, 235, 245), 5, -1)
            m["explodiu"] = t
            m.pop("sh")
    fim = m.get("explodiu", m.get("errou"))
    if fim is not None and t - fim > 30:
        return "fim"


def rib_ult2_efeito(l, tela):
    t = l.t
    m = l.memo
    p_selo = l.poses.get("r_selo") or l.poses["parado"]
    p_pulo = l.poses.get("pulo") or l.poses["parado"]
    cx, cy = rib_centro(l)
    guarda = l.x, l.y, l.angulo
    try:
        for i, dx in enumerate(CLONES_X):  # os 5 clones
            if t < R_POOF[i] or t >= R_SOLTA:
                continue
            chao_x = max(PAREDE_E + 10, min(PAREDE_D - 10, guarda[0] + l.dir * dx))
            if t < R_PULA:
                l.x, l.y, pose = chao_x, CHAO, p_selo
            else:
                u = t - R_PULA
                if u < R_RODA - R_PULA:  # o pulo até a roda
                    k = suave(u / (R_RODA - R_PULA))
                    a = i * math.tau / 5 - math.pi / 2
                    rx, ry = cx + math.cos(a) * 115, cy + math.sin(a) * 62 + 50
                    l.x = chao_x + (rx - chao_x) * k
                    l.y = CHAO + (ry - CHAO) * k - math.sin(k * math.pi) * 90
                else:  # a roda girando
                    v = t - R_RODA
                    a = i * math.tau / 5 - math.pi / 2 + v * v * 0.004 + v * 0.05
                    l.x, l.y = cx + math.cos(a) * 115, cy + math.sin(a) * 62 + 50
                pose = p_pulo
            l.f["desenho"](l, tela, pose, False)
    finally:
        l.x, l.y, l.angulo = guarda
    if R_RODA <= t < R_SOLTA:  # a shuriken nascendo no meio da roda
        k = suave((t - R_RODA) / (R_SOLTA - R_RODA))
        v = t - R_RODA
        desenha_shuriken(tela, cx, cy + 6, 14 + 46 * k, v * v * 0.01 + v * 0.1, brilha=int(60 + 120 * k))
        for i in range(5):  # as linhas de energia das mãos pro meio
            a = i * math.tau / 5 - math.pi / 2 + v * v * 0.004 + v * 0.05
            pygame.draw.line(tela, (160, 220, 255), (cx + math.cos(a) * 100, cy + math.sin(a) * 54 + 6), (cx, cy + 6), 2)
    if "sh" in m:
        sx, sy = m["sh"]
        ang = t * 0.9
        if "pegou" not in m:  # as linhas de vento atrás dela
            vx, vy = m.get("mira", (0, 0))
            n = math.hypot(vx, vy) or 1
            for k in (-1, 0, 1):
                ox, oy = -vy / n * k * 30, vx / n * k * 30
                pygame.draw.line(tela, (210, 235, 255), (sx + ox - vx * 4, sy + oy - vy * 4),
                                 (sx + ox - vx * 9, sy + oy - vy * 9), 2)
        desenha_shuriken(tela, sx, sy, 60, ang, brilha=110)
        if "pegou" in m and (t // 2) % 2:  # faíscas moendo
            for k in range(4):
                a = t * 1.3 + k * 1.6
                pygame.draw.line(tela, (255, 230, 150), (sx, sy), (sx + math.cos(a) * 70, sy + math.sin(a) * 70), 2)


_dano("rib_moendo", 6, hit=40, emp=0)
_registra("rib_ult2", rib_ult2, rib_ult2_efeito,
          [(0, "parado"), (4, "r_selo"), (R_PULA, "r_selo"), (R_PULA + 6, "r_puxa_ar"), (R_SOLTA - 4, "r_puxa_ar"),
           (R_SOLTA, "r_arremesso"), (R_SOLTA + 20, "r_arremesso"), (R_SOLTA + 30, "parado")])


# =====================================================================
# TRAFO: BRAÇOS DE TERRA
# =====================================================================
T_ENFIA, T_BRACOS, T_CADA, T_AVISO = 20, 20, 5, 10
T_GIGANTE = T_ENFIA + T_BRACOS * T_CADA + 18


def trafo_ult2(l, outro, jogo):
    t = l.t
    m = l.memo
    tela_toda(l)
    l.vx = 0
    l.fisica(jogo)
    m.setdefault("bracos", [])
    if t < T_ENFIA:  # enfia os braços no chão (câmera nele)
        camera(jogo, 1.35, l.x, l.y - 50 * l.s)
        if t == T_ENFIA - 6:
            som.tocar("terra")
            jogo.tremer(10)
            fumaca(jogo, l.x + l.dir * 30, CHAO - 4, 10, (130, 100, 70), 3, -1)
        return
    camera(jogo, 1.15, (l.x + outro.x) / 2 + (outro.x - l.x) * 0.2, CHAO - 110)
    k = (t - T_ENFIA) // T_CADA
    if (t - T_ENFIA) % T_CADA == 0 and k < T_BRACOS:  # marca onde o braço vai sair (dá pra fugir)
        x = max(PAREDE_E, min(PAREDE_D, outro.x + random.uniform(-30, 30)))  # (bem perto: difícil fugir)
        m["bracos"].append([x, t + T_AVISO, random.random() < 0.5])
    for b in m["bracos"]:
        if t == b[1]:  # SAI DO CHÃO
            fumaca(jogo, b[0], CHAO - 4, 6, (140, 105, 70), 3, -1.6)
            som.tocar("soco", 0.35)
            if abs(outro.x - b[0]) < 38 and outro.no_chao() and outro.inv <= 0 \
                    and outro.estado not in ("caido", "voando", "agarrado"):
                acerta(l, outro, jogo, "trafo_braco")
    if t == T_GIGANTE - T_AVISO - 6:
        m["gigante_x"] = outro.x
    if t == T_GIGANTE:  # o BRAÇÃO gigante
        x = m.get("gigante_x", outro.x)
        som.tocar("terra")
        impacto(jogo, 6, 20)
        fumaca(jogo, x, CHAO - 4, 18, (140, 105, 70), 6, -2.5)
        if abs(outro.x - x) < 60 and outro.inv <= 0 and outro.y > CHAO - 120 and outro.estado != "agarrado":
            acerta(l, outro, jogo, "trafo_bracao")
    if t >= T_GIGANTE + 34:
        return "fim"


def braco_de_terra(tela, x, alto, s, gigante=False, garra=0.0, lado=1):
    """Um braço de pedra saindo do chão (alto = quanto já saiu)."""
    if alto <= 2:
        return
    w = (30 if gigante else 13) * s
    base_y = CHAO + 4
    topo_y = base_y - alto
    pedra, escura, borda = (128, 96, 64), (92, 66, 42), (34, 22, 12)
    torto = lado * (10 if gigante else 4) * s
    corpo = [(x - w * 0.7, base_y), (x - w * 0.5 + torto, topo_y + w * 0.6), (x + w * 0.5 + torto, topo_y + w * 0.6),
             (x + w * 0.7, base_y)]
    pygame.draw.polygon(tela, borda, [(px + (2 if px > x else -2), py) for px, py in corpo])
    pygame.draw.polygon(tela, pedra, corpo)
    for i in range(4):  # as rachaduras e manchas da pedra
        yy = base_y - alto * (0.2 + i * 0.2)
        if yy > topo_y + w * 0.6:
            pygame.draw.line(tela, escura, (x - w * 0.3 + torto * 0.5, yy), (x + w * 0.2 + torto * 0.5, yy - 5 * s), 2)
    # a mão com 3 garras abrindo/fechando
    mx, my = x + torto, topo_y + w * 0.5
    pygame.draw.circle(tela, borda, (int(mx), int(my)), int(w * 0.62))
    pygame.draw.circle(tela, pedra, (int(mx), int(my)), int(w * 0.55))
    for i in (-1, 0, 1):
        a = -math.pi / 2 + i * (0.45 + 0.35 * garra)
        ponta = (mx + math.cos(a) * w * 1.25, my + math.sin(a) * w * 1.25)
        meio = (mx + math.cos(a) * w * 0.5, my + math.sin(a) * w * 0.5)
        pygame.draw.line(tela, borda, meio, ponta, max(3, int(w * 0.32)))
        pygame.draw.line(tela, (176, 150, 118), meio, ponta, max(2, int(w * 0.2)))


def trafo_ult2_efeito(l, tela):
    t = l.t
    m = l.memo
    if T_ENFIA - 8 <= t:  # as rachaduras saindo dele pelo chão
        k = min(1, (t - T_ENFIA + 8) / 20)
        x0 = l.x + l.dir * 30 * l.s
        x1 = x0 + l.dir * 420 * k
        pts = [(x0 + (x1 - x0) * i / 10, CHAO + 2 + (6 if i % 2 else -2)) for i in range(11)]
        if t < T_GIGANTE + 30:
            pygame.draw.lines(tela, (40, 26, 14), False, pts, 3)
    for x, t_sai, lado in m.get("bracos", []):
        u = t - t_sai
        if -T_AVISO <= u < 0:  # o aviso: poeira tremendo e a rachadura
            tremor = math.sin(t * 2.3) * 3
            pygame.draw.ellipse(tela, (60, 40, 22), (x - 22 + tremor, CHAO - 4, 44, 10))
            pygame.draw.line(tela, (30, 18, 8), (x - 16, CHAO + 1), (x + 16, CHAO + 3), 2)
        elif 0 <= u < 22:
            alto = (min(1, u / 3) * (1 - max(0, (u - 12) / 10))) * 78 * l.s
            braco_de_terra(tela, x, alto, l.s, garra=min(1, u / 6), lado=lado and 1 or -1)
    gx = m.get("gigante_x")
    if gx is not None:
        u = t - T_GIGANTE
        if -T_AVISO - 6 <= u < 0:
            r = 40 + (u + T_AVISO + 6) * 2
            pygame.draw.ellipse(tela, (60, 40, 22), (gx - r, CHAO - 6, r * 2, 14))
        elif 0 <= u < 34:
            alto = (min(1, u / 4) * (1 - max(0, (u - 22) / 12))) * 230 * l.s
            braco_de_terra(tela, gx, alto, l.s, gigante=True, garra=min(1, u / 8))


_dano("trafo_braco", 2.5, hit=18, defe=6, emp=1, imbloqueavel=True)
_dano("trafo_bracao", 10, hit=36, emp=4, imbloqueavel=True, lanca=17)
_registra("trafo_ult2", trafo_ult2, trafo_ult2_efeito,
          [(0, "parado"), (8, "t_terra"), (T_GIGANTE + 20, "t_terra"), (T_GIGANTE + 34, "parado")])


# =====================================================================
# KING RIP: ESPÍRITO DO DOJO (o dragão azul)
# =====================================================================
K_GIRA, K_SAI, K_VOLTA, K_PASSA = 34, 14, 64, 22
K_HITS = 3


def dragao_pos(l, u):
    """Onde está a cabeça do dragão (u = quadros desde que saiu do nunchaku)."""
    bx, by = l.x + l.dir * 10 * l.s, l.y - 140 * l.s
    if u < K_SAI:  # sobe saindo do círculo
        k = suave(u / K_SAI)
        return bx, by - 160 * k
    u -= K_SAI
    cx, cy = LARGURA / 2, 150
    if u < K_VOLTA:  # dá a volta por cima da tela (bem alto: não passa no adversário)
        a = -math.pi / 2 - l.dir * (u / K_VOLTA) * math.tau * 0.85
        k = min(1, u / 10)
        x0, y0 = bx, by - 160
        x1, y1 = cx + math.cos(a) * 360, cy + math.sin(a) * 90
        return x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
    k = (u - K_VOLTA) / K_PASSA  # e mergulha reto ATRAVESSANDO o peito do adversário
    alvo = l.memo.get("alvo_dragao", (LARGURA / 2, CHAO - 80))
    a = -math.pi / 2 - l.dir * 0.85 * math.tau
    x0, y0 = cx + math.cos(a) * 360, cy + math.sin(a) * 90
    return x0 + (alvo[0] - x0) * k * 1.4, y0 + (alvo[1] - y0) * k * 1.4


def king_ult2(l, outro, jogo):
    t = l.t
    m = l.memo
    tela_toda(l)
    l.vx = 0
    l.fisica(jogo)
    if t < K_GIRA:  # gira o nunchaku tão rápido que vira um círculo de energia
        camera(jogo, 1.35, l.x, l.y - 110 * l.s)
        if t % 5 == 0:
            som.tocar("vento", 0.3 + t / K_GIRA * 0.4)
        return
    u = t - K_GIRA
    if u == 0:
        som.tocar("uivo", 0.8)
        som.tocar("ultimate", 0.5)
        jogo.tremer(8)
    if u == K_SAI + K_VOLTA - 1:
        m["alvo_dragao"] = (outro.x, outro.y - 60 * outro.s)
    x, y = dragao_pos(l, u)
    m["rastro"] = (m.get("rastro", []) + [(x, y)])[-34:]
    if u < K_SAI + K_VOLTA:
        camera(jogo, 1.0, LARGURA / 2, ALTURA / 2)
    else:
        camera(jogo, 1.25, outro.x, outro.y - 70 * outro.s)
    if u >= K_SAI + K_VOLTA and "pegou" not in m and "errou" not in m:
        if abs(outro.x - x) < 50 and abs((outro.y - 60 * outro.s) - y) < 70 and pode_pegar(outro, 400):
            m["pegou"] = t
            pega(outro)
        elif u >= K_SAI + K_VOLTA + K_PASSA:
            m["errou"] = t
    if "pegou" in m:  # o dragão passa por DENTRO dele: 3 mordidas e o arremesso
        v = t - m["pegou"]
        if v in (0, 5, 10):
            bate(l, outro, jogo, 10, "king_dragao")
        if v == 16:
            bate(l, outro, jogo, 25, "king_dragao", ultimo=True)
            impacto(jogo, 12, 22, 5)
            solta(outro, l.dir * 11, -12)
            m["acabou"] = t
    fim = m.get("acabou", m.get("errou"))
    if fim is not None and t - fim > 26:
        return "fim"


def desenha_dragao(tela, pts, t):
    """O dragão chinês azul: corpo contínuo afinando até a cauda, crina, chifres, bigodes e a boca aberta."""
    n = len(pts)
    if n < 3:
        return
    for i in range(0, n, 3):  # o brilho em volta
        brilho(tela, (int(pts[i][0]), int(pts[i][1])), int(14 + i * 0.9), (60, 140, 255), 50)
    for camada, (cor, extra) in enumerate((((10, 30, 90), 5), ((50, 120, 240), 0), ((170, 225, 255), -9))):
        for i in range(n - 1):
            w = 5 + 26 * (i / n) ** 0.8 + extra
            if w > 1:
                pygame.draw.line(tela, cor, pts[i], pts[i + 1], int(w))
                pygame.draw.circle(tela, cor, (int(pts[i + 1][0]), int(pts[i + 1][1])), int(w / 2))
    for i in range(4, n - 2, 3):  # a crina nas costas
        (x0, y0), (x1, y1) = pts[i - 1], pts[i + 1]
        a = math.atan2(y1 - y0, x1 - x0)
        w = 4 + 22 * (i / n) ** 0.8
        bx, by = pts[i][0] - math.sin(a) * w * 0.5, pts[i][1] + math.cos(a) * w * 0.5
        tip = (bx - math.sin(a) * 12 - math.cos(a) * 8, by + math.cos(a) * 12 - math.sin(a) * 8)
        pygame.draw.polygon(tela, (230, 245, 255), [(bx - math.cos(a) * 5, by - math.sin(a) * 5), tip,
                                                   (bx + math.cos(a) * 5, by + math.sin(a) * 5)])
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    a = math.atan2(y1 - y0, x1 - x0)
    c, s = math.cos(a), math.sin(a)

    def P(f, u):
        f, u = f * 1.4, u * 1.4
        return (x1 + c * f - s * u, y1 + s * f + c * u)

    abre = 0.5 + 0.5 * math.sin(t * 0.4)
    queixo = [P(-6, 6), P(30, 10 + abre * 8), P(26, 16 + abre * 8), P(-4, 14)]
    pygame.draw.polygon(tela, (10, 30, 90), queixo)
    pygame.draw.polygon(tela, (70, 140, 240), [(x + (P(8, 10)[0] - x) * 0.1, y + (P(8, 10)[1] - y) * 0.1) for x, y in queixo])
    cabeca = [P(-14, -12), P(10, -16), P(38, -6), P(42, 4), P(14, 6), P(-14, 12)]
    pygame.draw.polygon(tela, (10, 30, 90), cabeca)
    pygame.draw.polygon(tela, (90, 170, 255), [(x + (P(10, -2)[0] - x) * 0.12, y + (P(10, -2)[1] - y) * 0.12) for x, y in cabeca])
    for k in range(5):  # os dentes
        pygame.draw.line(tela, (255, 255, 255), P(16 + k * 5, 5), P(17 + k * 5, 10), 2)
    for lado in (-1, 1):  # os chifres (galhados)
        base = P(-6, -12)
        pt = P(-30, -30 + lado * 6)
        pygame.draw.line(tela, (230, 240, 255), base, pt, 4)
        pygame.draw.line(tela, (230, 240, 255), P(-18, -20 + lado * 3), P(-20, -34 + lado * 3), 3)
    for lado, fase in ((1, 0), (-1, 1.5)):  # os bigodes compridos
        bpts = [P(30 - k * 7, 4 + k * 2 + math.sin(t * 0.3 + k * 0.8 + fase) * 5 * lado) for k in range(7)]
        pygame.draw.lines(tela, (230, 245, 255), False, bpts, 2)
    olho = P(14, -6)
    brilho(tela, (int(olho[0]), int(olho[1])), 9, (255, 255, 200), 200)
    pygame.draw.circle(tela, (255, 255, 230), (int(olho[0]), int(olho[1])), 4)


def king_ult2_efeito(l, tela):
    t = l.t
    m = l.memo
    cx, cy = l.x + l.dir * 10 * l.s, l.y - 140 * l.s
    if t < K_GIRA + 8:  # o nunchaku virando um círculo de energia
        k = min(1, t / K_GIRA)
        r = int((22 + 30 * k) * l.s)
        brilho(tela, (int(cx), int(cy)), int(r * 1.3), (80, 160, 255), int(30 + 50 * k))
        for i in range(4):  # arcos de movimento (borrão)
            a0 = t * (0.5 + k) + i * math.pi / 2
            rect = pygame.Rect(0, 0, r * 2, r * 0.8 * 2)
            rect.center = (int(cx), int(cy))
            pygame.draw.arc(tela, (200, 235, 255), rect, a0, a0 + 1.2, 3)
        for i in range(8):  # energia vindo pro círculo
            a = i * 0.785 + t * 0.1
            d = 120 * (1 - (t * 3 + i * 20) % 60 / 60) + r
            pygame.draw.circle(tela, (150, 210, 255), (int(cx + math.cos(a) * d), int(cy + math.sin(a) * d * 0.7)), 3)
        if t >= K_GIRA:  # o estouro quando o dragão sai
            u = t - K_GIRA
            brilho(tela, (int(cx), int(cy)), int(40 + u * 8), (220, 240, 255), max(0, 130 - u * 18))
    if m.get("rastro") and "acabou" not in m:
        desenha_dragao(tela, m["rastro"], t)
    elif "acabou" in m and t - m["acabou"] < 10:  # o dragão some numa explosão de luz azul
        u = t - m["acabou"]
        x, y = m["rastro"][-1]
        brilho(tela, (int(x), int(y)), int(40 + u * 14), (120, 190, 255), max(0, 220 - u * 22))


_dano("king_dragao", 10, hit=40, emp=2)
_registra("king_ult2", king_ult2, king_ult2_efeito,
          [(0, "parado"), (6, "k_gira"), (K_GIRA, "k_gira"), (K_GIRA + 6, "k_bastao"), (9999, "k_bastao")])


# =====================================================================
# CANNAN: A MINIGUN
# =====================================================================
C_RADIO, C_CAI, C_GIRA, C_TIROS, C_CADA = 26, 34, 14, 30, 2
C_COICE = 10
C_INI = C_RADIO + C_CAI + C_GIRA
C_FIM = C_INI + C_TIROS * C_CADA


def maos(l):
    p = l.pose_vista or l.pose_atual()
    a, b = l.ponto(p, "mf"), l.ponto(p, "mt")
    return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2


def cannan_ult2(l, outro, jogo):
    t = l.t
    m = l.memo
    tela_toda(l)
    l.vx = 0
    if t < C_RADIO:  # chama no radinho (câmera nele)
        camera(jogo, 1.4, l.x, l.y - 90 * l.s)
        if t in (4, 14):
            som.tocar("blip", 0.6)
    elif t < C_RADIO + C_CAI:  # a minigun cai do céu de paraquedas
        camera(jogo, 1.1, l.x + l.dir * 40, l.y - 160 * l.s)
        if t == C_RADIO + C_CAI - 1:
            som.tocar("queda", 0.7)
            jogo.tremer(6)
            fumaca(jogo, l.x + l.dir * 30, l.y - 40, 6, (200, 200, 200), 2, -0.5)
    elif t < C_INI:  # os canos começam a girar
        camera(jogo, 1.3, l.x + l.dir * 50, l.y - 80 * l.s)
        if t % 3 == 0:
            som.tocar("carga", 0.3 + (t - C_RADIO - C_CAI) / C_GIRA * 0.4)
    elif t < C_FIM:  # DESCE O PIPOCO
        camera(jogo, 1.15, (l.x + outro.x) / 2, l.y - 80 * l.s)
        k = (t - C_INI) // C_CADA
        if (t - C_INI) % C_CADA == 0:
            hx, hy = maos(l)
            y = hy + random.uniform(-4, 4)
            nome = "cannan_minigun_final" if k == C_TIROS - 1 else "cannan_minigun_bala"
            jogo.projeteis.append(Projetil(l, hx + l.dir * 70 * l.s, y, l.dir, GOLPES[nome]))
            som.tocar("tiro", 0.35)
            l.vida = max(1, l.vida - C_COICE / C_TIROS)  # o coice tira dele também
            l.x -= l.dir * 0.8
            jogo.faiscas.append([hx - l.dir * 6, hy - 6, -l.dir * random.uniform(1.5, 3), random.uniform(-4, -2), 26,
                                 (230, 190, 70), 3])  # a cápsula voando
            if k % 4 == 0:
                fumaca(jogo, hx + l.dir * 70 * l.s, hy, 1, (190, 190, 196), 1.5, -0.6)
        jogo.tremer(2)
    else:  # esquentou: soltando vapor
        camera(jogo, 1.3, l.x + l.dir * 50, l.y - 80 * l.s)
        if t % 4 == 0:
            hx, hy = maos(l)
            fumaca(jogo, hx + l.dir * 60 * l.s, hy - 6, 1, (220, 220, 226), 1, -1.2)
    l.fisica(jogo)
    if t >= C_FIM + 36:
        return "fim"


def desenha_minigun(tela, l, x, y, giro, quente=0.0):
    """A minigun nas mãos: corpo, os 6 canos (3 aparecem girando), a alça e a fita de balas."""
    s, d = l.s, l.dir
    corpo = pygame.Rect(0, 0, 34 * s, 14 * s)
    corpo.center = (int(x), int(y))
    pygame.draw.rect(tela, (16, 16, 20), corpo.inflate(4, 4), border_radius=4)
    pygame.draw.rect(tela, (76, 80, 88), corpo, border_radius=4)
    pygame.draw.line(tela, (120, 124, 134), corpo.topleft, corpo.topright, 2)
    frente = x + d * 17 * s
    for i in range(3):  # os canos girando (sobem e descem um pouco)
        oy = math.sin(giro + i * 2.1) * 4 * s
        cor = tuple(int(c + (255 - c) * quente * (0.4 + 0.6 * (i == 1))) if j == 0 else int(c * (1 - quente * 0.4))
                    for j, c in enumerate((70, 72, 78)))
        pygame.draw.line(tela, (16, 16, 20), (frente, y + oy), (frente + d * 40 * s, y + oy), max(3, int(5 * s)))
        pygame.draw.line(tela, cor, (frente, y + oy), (frente + d * 40 * s, y + oy), max(2, int(3 * s)))
    boca = pygame.Rect(0, 0, 8 * s, 14 * s)
    boca.center = (int(frente + d * 40 * s), int(y))
    pygame.draw.rect(tela, (40, 42, 48), boca, border_radius=3)
    pygame.draw.rect(tela, (16, 16, 20), boca, 2, border_radius=3)
    alca = [(x - d * 6 * s, y - 7 * s), (x - d * 2 * s, y - 16 * s), (x + d * 10 * s, y - 16 * s), (x + d * 12 * s, y - 7 * s)]
    pygame.draw.lines(tela, (30, 30, 36), False, alca, max(2, int(3 * s)))
    for i in range(6):  # a fita de balas
        bx = x - d * (14 + i * 4) * s
        by = y + 6 * s + i * 2.5 * s + math.sin(giro * 0.5 + i) * 1.5
        pygame.draw.rect(tela, (200, 160, 50), (bx - 2 * s, by, 3 * s, 6 * s))


def cannan_ult2_efeito(l, tela):
    from efeitos import fonte
    t = l.t
    s = l.s
    if t < C_RADIO:  # o radinho na mão e o balão
        p = l.pose_vista or l.pose_atual()
        mx, my = l.ponto(p, "mf")
        r = pygame.Rect(0, 0, 8 * s, 14 * s)
        r.center = (int(mx), int(my - 4 * s))
        pygame.draw.rect(tela, (30, 34, 30), r, border_radius=2)
        pygame.draw.line(tela, (30, 34, 30), (r.right - 2, r.top), (r.right - 2, r.top - 10 * s), 2)
        pygame.draw.circle(tela, (255, 60, 40) if (t // 4) % 2 else (90, 20, 20), (r.centerx, r.top + 3), 2)
        if t > 8:
            img = fonte(15).render("Base, manda a ENCOMENDA. Câmbio!", True, (20, 16, 30))
            caixa = img.get_rect(midbottom=(int(l.x), int(l.y - 150 * s)))
            caixa.clamp_ip(pygame.Rect(4, 4, LARGURA - 8, ALTURA - 8))
            pygame.draw.rect(tela, (12, 10, 20), caixa.inflate(22, 16), border_radius=10)
            pygame.draw.rect(tela, (250, 248, 236), caixa.inflate(18, 12), border_radius=9)
            tela.blit(img, caixa)
        return
    if t < C_RADIO + C_CAI:  # caindo de paraquedas
        k = (t - C_RADIO) / C_CAI
        hx, hy = maos(l)
        x = hx + l.dir * 10 * s + math.sin(t * 0.2) * 8 * (1 - k)
        y = -60 + (hy + 60) * suave(k)
        if k < 0.92:
            topo = (x, y - 90 * s)
            pygame.draw.ellipse(tela, (16, 16, 20), (topo[0] - 44 * s, topo[1] - 22 * s, 88 * s, 44 * s))
            pygame.draw.ellipse(tela, (90, 120, 70), (topo[0] - 42 * s, topo[1] - 20 * s, 84 * s, 40 * s))
            pygame.draw.rect(tela, (90, 120, 70), (topo[0] - 44 * s, topo[1], 88 * s, 22 * s))
            for fx in (-38, -12, 12, 38):
                pygame.draw.line(tela, (220, 220, 210), (topo[0] + fx * s, topo[1]), (x, y - 8 * s), 1)
        desenha_minigun(tela, l, x, y, 0)
        return
    hx, hy = maos(l)
    x = hx + l.dir * 6 * s
    girando = t - C_RADIO - C_CAI
    giro = girando * girando * 0.02 if t < C_INI else t * 1.6 if t < C_FIM else t * 1.6 * max(0, 1 - (t - C_FIM) / 30)
    quente = 0 if t < C_INI + 20 else min(1, (t - C_INI - 20) / 30) * (1 - max(0, (t - C_FIM - 10) / 30))
    desenha_minigun(tela, l, x, hy, giro, quente)
    if C_INI <= t < C_FIM and t % 2 == 0:  # o clarão na boca dos canos
        ponta = (int(x + l.dir * 64 * s), int(hy))
        brilho(tela, ponta, int(22 * s), (255, 220, 120), 200)
        pts = [ponta, (ponta[0] + l.dir * 26 * s, ponta[1] - 8 * s), (ponta[0] + l.dir * 34 * s, ponta[1]),
               (ponta[0] + l.dir * 26 * s, ponta[1] + 8 * s)]
        pygame.draw.polygon(tela, (255, 240, 170), pts)


def desenha_bala_tracante(p, tela):
    d = 1 if p.vx > 0 else -1
    pygame.draw.line(tela, (255, 200, 80), (p.x - d * 34, p.y), (p.x, p.y), 3)
    pygame.draw.line(tela, (255, 255, 230), (p.x - d * 14, p.y), (p.x, p.y), 2)


_dano("cannan_minigun_bala", 55 / C_TIROS, hit=10, defe=5, emp=1, proj=True, raio=6, vel=20, varios=True,
      guarda_custo=4, desenho_proj=desenha_bala_tracante, sem_parada=True)
_dano("cannan_minigun_final", 55 / C_TIROS, hit=30, emp=5, proj=True, raio=6, vel=20, varios=True, derruba=True,
      voo=(9, 8), desenho_proj=desenha_bala_tracante)
_registra("cannan_ult2", cannan_ult2, cannan_ult2_efeito,
          [(0, "parado"), (4, "c_continencia"), (C_RADIO - 2, "c_continencia"), (C_RADIO + 4, "parado"),
           (C_RADIO + C_CAI - 6, "c_canhao"), (C_FIM + 20, "c_canhao"), (C_FIM + 34, "parado")])


# =====================================================================
# FINN: O GOLEM DE PEDRA (fica 15 s ajudando)
# =====================================================================
G_CIRCULO, G_SOBE, G_SOCO = 16, 40, 58
GOLEM_TEMPO = 15 * FPS
GOLEM_ALCANCE = 200
RUNA = (90, 230, 255)


def golem_x(l):
    return max(PAREDE_E, min(PAREDE_D, l.x + l.dir * 84 * l.s))


def finn_ult2(l, outro, jogo):
    t = l.t
    tela_toda(l)
    l.vx = 0
    l.fisica(jogo)
    gx = golem_x(l)
    if t < G_CIRCULO:  # ergue o cajado (câmera nele)
        camera(jogo, 1.35, l.x, l.y - 90 * l.s)
        if t == 4:
            som.tocar("carga", 0.7)
        return
    if t < G_SOBE:  # o círculo de runas no chão e as pedras subindo
        camera(jogo, 1.2, (l.x + gx) / 2, l.y - 80 * l.s)
        if t % 6 == 0:
            som.tocar("terra", 0.4)
            jogo.tremer(4)
        return
    if t == G_SOBE:  # O GOLEM SAI DO CHÃO
        l.extra["golem"] = GOLEM_TEMPO
        l.extra["golem_acao"] = ("sobe", 0)
        som.tocar("terra")
        impacto(jogo, 4, 14)
        fumaca(jogo, gx, CHAO - 4, 16, (140, 130, 120), 5, -1.5)
    camera(jogo, 1.15, (l.x + outro.x) / 2, l.y - 90 * l.s)
    if t == G_SOCO - 10:
        l.extra["golem_acao"] = ("soco", 0)
        som.tocar("vento")
    if t == G_SOCO:  # e já chega com um SOCO
        if abs(outro.x - gx) < GOLEM_ALCANCE + 40 and outro.inv <= 0:
            if acerta(l, outro, jogo, "golem_soco") == "hit":
                impacto(jogo, 10, 18, 3)
    if t >= G_SOCO + 24:
        return "fim"


def golem_ajuda(l, o, jogo):
    """O golem entra junto nos especiais do Finn (E, Q, R, SHIFT)."""
    botao = getattr(l, "botao_pedido", None)
    if botao not in ("E", "Q", "R", "SHIFT"):
        return
    l.extra["golem_acao"] = (botao, 0)
    if abs(o.x - golem_x(l)) > GOLEM_ALCANCE or o.inv > 0 or o.estado in ("caido", "agarrado"):
        return
    pra_finn = 1 if l.x > o.x else -1
    if botao == "E":  # chuta na direção da bola de fogo (pro lado do Finn)
        res = o.receber(GOLPES["golem_chute"], pra_finn, l, 1.0)
        if res == "hit":
            o.vx = pra_finn * 9
    elif botao == "Q":
        o.receber(GOLPES["golem_joga"], -pra_finn, l, 1.0)
    elif botao == "R":
        o.receber(GOLPES["golem_segura"], -pra_finn, l, 1.0)
    else:
        o.receber(GOLPES["golem_empurra"], -pra_finn, l, 1.0)
    jogo.faisca(o.x, o.y - 50 * o.s, False, True)
    jogo.tremer(8)
    som.tocar("soco", 0.7)


def _pedra(tela, pts, cor, borda=(28, 24, 22)):
    pygame.draw.polygon(tela, borda, pts)
    meio = (sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts))
    pygame.draw.polygon(tela, cor, [(x + (meio[0] - x) * 0.1, y + (meio[1] - y) * 0.1) for x, y in pts])
    claro = tuple(min(255, c + 26) for c in cor)
    pygame.draw.polygon(tela, claro, [(x + (meio[0] - x) * 0.55, y + (meio[1] - y) * 0.55 - 2) for x, y in pts[:3]] +
                        [(meio[0], meio[1] - 2)])


def _bloco(tela, pts, cor, borda=(28, 24, 22), luz=0.18):
    """Uma pedra lisa e arredondada (golem novo): contorno, cor, um brilho em cima e sombra embaixo."""
    pygame.draw.polygon(tela, borda, pts)
    meio = (sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts))
    pygame.draw.polygon(tela, cor, [(x + (meio[0] - x) * 0.08, y + (meio[1] - y) * 0.08) for x, y in pts])
    claro = tuple(min(255, int(c + (255 - c) * luz)) for c in cor)
    topo = sorted(pts, key=lambda q: q[1])[:3]
    pygame.draw.polygon(tela, claro, [(x + (meio[0] - x) * 0.45, y + (meio[1] - y) * 0.45) for x, y in topo] +
                        [(meio[0], meio[1] - 2)])


def _oval(cx, cy, rx, ry, n=14, giro=0.0):
    return [(cx + math.cos(giro + k * math.tau / n) * rx, cy + math.sin(giro + k * math.tau / n) * ry) for k in range(n)]


def desenha_golem(l, tela, x=None, afunda=0.0):
    """O GOLEM DE PEDRA (2ª ult do Finn; remodel do Gomes: inspirado num golem gigante antigo).
    Corpo redondo e maciço, FAIXA/SELO no peito, olhos em FENDA brilhando, braços grossos com 3 dedos,
    pernas curtas, rachaduras com luz. MOVIMENTO FLUIDO: respira, balança o peso no passo (a fase vem da
    posição dele), braços pendulam com atraso e o soco puxa pra trás antes de esticar.
    (x = onde, se não for do lado do Finn; afunda 0..1 = entrando na terra.) Só desenho: não muda estado."""
    acao, u = l.extra.get("golem_acao", ("", 99))
    s = l.s * 1.9
    chao = CHAO
    do_lado = x is None
    x = golem_x(l) if do_lado else x
    d = l.dir
    resta = l.extra.get("golem", 0) if do_lado else 999
    t = l.t + resta
    sai = min(1, u / 18) if acao == "sobe" else 1
    some = min(1, resta / 30)
    y0 = chao + (1 - sai) * 150 * s + (1 - some) * 150 * s + afunda * 170 * s
    pedra, escura, funda = (128, 122, 114), (96, 90, 84), (70, 66, 62)
    acende = 0.6 + 0.4 * math.sin(t * 0.15)
    runa = tuple(int(c * acende) for c in RUNA) if (resta > 60 or (resta // 6) % 2) else (30, 70, 80)
    # --- os relógios do movimento (só leitura) ---
    respira = math.sin(t * 0.07) * 1.8                     # o peito sobe e desce
    fase = (x / (26 * s)) % math.tau                         # o passo vem de onde ele está (anda junto com o Finn)
    anda = min(1.0, abs(math.sin(fase)) * 1.2) if do_lado else 0.0
    peso = math.sin(fase) * 3.0                              # o corpo balança de um pé pro outro
    sobe_pe = (max(0.0, math.sin(fase)) * 5, max(0.0, -math.sin(fase)) * 5)
    pendulo = math.sin(fase - 0.9) * 6 + math.sin(t * 0.05) * 1.5   # braços com atraso
    golpe = acao in ("soco", "E", "SHIFT") and u < 22
    sobe_braco = acao == "Q" and u < 18
    segura = acao == "R" and u < 30
    if golpe:  # ANTECIPAÇÃO: puxa pra trás (0..7) e estica (7..13), depois volta
        puxa = suave(min(1, u / 7)) if u < 7 else 1 - suave(min(1, (u - 7) / 3))
        estica = suave(min(1, max(0, u - 7) / 4)) * (1 - suave(max(0, (u - 14) / 8)))
    else:
        puxa, estica = 0.0, 0.0
    inclina = (-4 * puxa + 6 * estica) if golpe else peso * 0.4  # o corpo vai junto com o soco

    def P(fx, fy):  # (fx pra frente, fy pra cima) em "unidades de golem"
        return (x + d * (fx + inclina * fy / 80) * s, y0 - fy * s)

    # --- pernas curtas e grossas (a de trás levanta no passo) ---
    for k, fx in enumerate((-10, 10)):
        lev = sobe_pe[k]
        perna = [P(fx - 9, lev), P(fx - 10, 14 + lev), P(fx - 6, 24), P(fx + 7, 24), P(fx + 10, 14 + lev), P(fx + 9, lev)]
        _bloco(tela, perna, escura if k == 0 else pedra)
        pygame.draw.line(tela, (28, 24, 22), P(fx - 9, lev), P(fx + 10, lev), max(2, int(2 * s)))  # a sola
    # --- braço de trás (pendula) ---
    ombro_t = P(-20, 66 + respira)
    mao_t = P(-30 - pendulo * 0.6, 30 + respira * 0.5)
    pygame.draw.line(tela, (28, 24, 22), ombro_t, mao_t, int(14 * s) + 4)
    pygame.draw.line(tela, escura, ombro_t, mao_t, int(14 * s))
    _bloco(tela, _oval(mao_t[0], mao_t[1], 9 * s, 8 * s), escura)
    # --- o CORPO: um pedregulho redondo e maciço ---
    cx, cy = P(0, 50 + respira * 0.6)
    corpo = _oval(cx, cy, 31 * s, 30 * s + respira * 0.3 * s, n=16)
    _bloco(tela, corpo, pedra, luz=0.22)
    # rachaduras com luz saindo
    for a, b, c in (((-20, 66), (-12, 58), (-16, 48)), ((16, 34), (10, 42), (18, 48)), ((-4, 28), (2, 36), (-2, 40))):
        pts = [P(a[0], a[1] + respira * 0.6), P(b[0], b[1] + respira * 0.6), P(c[0], c[1] + respira * 0.6)]
        pygame.draw.lines(tela, (28, 24, 22), False, pts, max(2, int(2.4 * s)))
        pygame.draw.lines(tela, runa, False, pts, max(1, int(1.0 * s)))
    # a FAIXA/SELO atravessando o peito, com o selo de runa no meio
    faixa = [P(-26, 66 + respira), P(-20, 72 + respira), P(26, 40 + respira), P(20, 34 + respira)]
    pygame.draw.polygon(tela, (28, 24, 22), faixa)
    pygame.draw.polygon(tela, funda, [(q[0] + (cx - q[0]) * 0.06, q[1] + (cy - q[1]) * 0.06) for q in faixa])
    selo = P(0, 53 + respira)
    brilho(tela, (int(selo[0]), int(selo[1])), int(16 * s), RUNA, int(70 * acende))
    pygame.draw.circle(tela, (28, 24, 22), (int(selo[0]), int(selo[1])), max(3, int(6.5 * s)))
    pygame.draw.circle(tela, runa, (int(selo[0]), int(selo[1])), max(2, int(5 * s)), max(1, int(1.6 * s)))
    pygame.draw.lines(tela, runa, False, [P(-3, 56 + respira), P(3, 53 + respira), P(-2, 50 + respira)], max(1, int(1.4 * s)))
    # --- a CABEÇA: um capacete de pedra com os olhos em FENDA ---
    hx, hy = P(4, 84 + respira)
    cab = _oval(hx, hy, 13 * s, 11 * s, n=12)
    _bloco(tela, cab, pedra, luz=0.25)
    crista = [P(-2, 93 + respira), P(4, 100 + respira), P(10, 93 + respira)]
    _bloco(tela, crista, escura)
    for k, fx in enumerate((1, 10)):  # os olhos: fendas inclinadas (bravo), brilhando
        a, b = P(fx - 3, 86 + respira + (1 if k else -1)), P(fx + 3, 84 + respira + (-1 if k else 1))
        brilho(tela, (int((a[0] + b[0]) / 2), int((a[1] + b[1]) / 2)), int(6 * s), RUNA, int(140 * acende))
        pygame.draw.line(tela, (28, 24, 22), a, b, max(3, int(3.4 * s)))
        pygame.draw.line(tela, runa, a, b, max(2, int(1.8 * s)))
    # --- o braço da frente: grosso, mão de 3 dedos (soco com antecipação / pra cima / segurando) ---
    ombro = P(20, 64 + respira)
    if sobe_braco:
        k = suave(min(1, u / 6)) * (1 - suave(max(0, (u - 10) / 8)))
        mao = P(28, 40 + 52 * k)
    elif segura:
        mao = P(52, 46 + math.sin(t * 0.3) * 2)
    elif golpe:
        mao = P(30 - 18 * puxa + 50 * estica, 40 + 6 * puxa + 8 * estica)
    else:
        mao = P(30 + pendulo * 0.6, 32 + respira * 0.5)
    cotovelo = ((ombro[0] + mao[0]) / 2 - d * 2 * s, (ombro[1] + mao[1]) / 2 + 7 * s)
    for a, b, w in ((ombro, cotovelo, 16), (cotovelo, mao, 13)):
        pygame.draw.line(tela, (28, 24, 22), a, b, int(w * s) + 4)
        pygame.draw.line(tela, pedra, a, b, int(w * s))
    _bloco(tela, _oval(mao[0], mao[1], 11 * s, 10 * s), pedra, luz=0.25)
    for k in (-1, 0, 1):  # os 3 dedos
        dedo = (mao[0] + d * 10 * s, mao[1] + k * 6 * s)
        pygame.draw.line(tela, (28, 24, 22), (mao[0] + d * 4 * s, mao[1] + k * 5 * s), dedo, max(3, int(5 * s)))
        pygame.draw.line(tela, escura, (mao[0] + d * 4 * s, mao[1] + k * 5 * s), dedo, max(2, int(3.4 * s)))
    if estica > 0.6 and golpe:  # o deslocamento de ar do soco
        pygame.draw.circle(tela, (230, 240, 255), (int(mao[0] + d * 18 * s), int(mao[1])), int(16 * s), 2)
    # --- poeirinha e rachadura no chão no passo (só desenho) ---
    if do_lado and anda > 0.6 and sai >= 1 and afunda == 0:
        for k in range(3):
            px = x + d * (-10 + k * 10) * s + math.sin(t * 0.3 + k) * 3
            pygame.draw.circle(tela, (150, 140, 128), (int(px), int(chao - 3 - k)), max(1, int(2 * s)))
    for i in range(4):  # pedrinhas flutuando em volta (devagar)
        a = t * 0.03 + i * 1.6
        px, py = P(math.cos(a) * 40, 58 + math.sin(a * 1.3) * 26)
        pygame.draw.circle(tela, escura, (int(px), int(py)), max(2, int(3 * s)))


def desenha_vivo_finn(l, tela):
    if l.extra.get("golem", 0) > 0:
        desenha_golem(l, tela)


def finn_ult2_efeito(l, tela):
    t = l.t
    if G_CIRCULO <= t < G_SOBE + 20:  # o círculo de runas no chão
        gx = golem_x(l)
        k = min(1, (t - G_CIRCULO) / 10) * (1 - max(0, (t - G_SOBE) / 20))
        r = 70 * l.s
        caixa = pygame.Rect(0, 0, r * 2, r * 0.5)
        caixa.center = (int(gx), int(CHAO))
        brilho(tela, caixa.center, int(r), RUNA, int(80 * k))
        pygame.draw.ellipse(tela, RUNA, caixa, 3)
        pygame.draw.ellipse(tela, RUNA, caixa.inflate(-24, -6), 2)
        for i in range(8):  # as runas girando no círculo
            a = t * 0.08 + i * math.tau / 8
            px, py = gx + math.cos(a) * r * 0.85, CHAO + math.sin(a) * r * 0.21
            pygame.draw.line(tela, (220, 250, 255), (px - 4, py - 3), (px + 4, py + 3), 2)
        if t < G_SOBE:  # pedras subindo do chão pro meio do círculo
            for i in range(6):
                a = i * 1.05
                h = ((t * 4 + i * 23) % 70)
                pygame.draw.circle(tela, (110, 104, 98), (int(gx + math.cos(a) * r * 0.6), int(CHAO - h)), 4)
    if t < G_SOBE:  # o cajado brilhando
        p = l.pose_vista or l.pose_atual()
        mx, my = l.ponto(p, "mf")
        brilho(tela, (int(mx), int(my - 40 * l.s)), int(20 * l.s), RUNA, 160)


_dano("golem_soco", 15, hit=30, emp=4, derruba=True, voo=(8, 9))
_dano("golem_chute", 6, hit=24, emp=2, ultimate=False, ultimate2=False)
_dano("golem_joga", 6, hit=24, emp=1, lanca=15, ultimate=False, ultimate2=False)
_dano("golem_segura", 6, hit=50, emp=0, ultimate=False, ultimate2=False)
_dano("golem_empurra", 6, hit=24, emp=4, derruba=True, voo=(14, 4), parede=4, ultimate=False, ultimate2=False)
_registra("finn_ult2", finn_ult2, finn_ult2_efeito,
          [(0, "parado"), (4, "f_ult"), (G_SOBE + 6, "f_ult"), (G_SOBE + 16, "f_ult_lanca"), (G_SOCO + 12, "f_ult_lanca"),
           (G_SOCO + 24, "parado")])


# =====================================================================
# KUN: TSUNAMI DE CARTAS
# =====================================================================
K_MOSTRA, K_VIRA, K_VEL = 30, 14, 8
K_CORTES = 8
K_ALTURA = 290


def onda_altura(atras):
    """A altura da onda a 'atras' pixels da frente (crista alta logo atrás da frente, baixando lá atrás)."""
    if atras < 0:
        return 0
    if atras < 70:
        return K_ALTURA * suave(atras / 70) * 0.85 + 30
    return max(0, K_ALTURA - (atras - 70) * 0.9)


def kun_ult2(l, outro, jogo):
    t = l.t
    m = l.memo
    tela_toda(l)
    l.vx = 0
    l.fisica(jogo)
    if t < K_MOSTRA:  # mostra UMA carta pro adversário (câmera na carta)
        camera(jogo, 1.45, l.x + l.dir * 50 * l.s, l.y - 100 * l.s)
        if t == K_VIRA:
            som.tocar("confirma", 0.7)
        return
    if t == K_MOSTRA:  # a carta estoura e vira a onda
        m["frente"] = l.x + l.dir * 40
        som.tocar("explosao", 0.5)
        som.tocar("vento")
        jogo.tremer(10)
    parede = PAREDE_D if l.dir > 0 else PAREDE_E
    f = m["frente"] + l.dir * K_VEL
    chegou = (f - parede) * l.dir >= 0
    m["frente"] = parede if chegou else f
    camera(jogo, 1.1, m["frente"] - l.dir * 120, CHAO - 130)
    if t % 10 == 0:
        som.tocar("vento", 0.4)
    if "pegou" not in m:
        if abs(outro.x - m["frente"]) < 34 and pode_pegar(outro, 140):
            m["pegou"] = t
            pega(outro)
            som.tocar("lingua")
        elif chegou:
            m.setdefault("fim", t)
    if "pegou" in m:
        u = t - m["pegou"]
        outro.x = max(PAREDE_E + 10, min(PAREDE_D - 10, m["frente"] - l.dir * 16))
        outro.y = CHAO - 40 - math.sin(u * 0.3) * 6
        if u % 5 == 2 and u // 5 < K_CORTES:  # as cartas cortando lá dentro
            bate(l, outro, jogo, 4, "kun_onda")
            m.setdefault("cortes", []).append(t)
        if chegou and "prensou" not in m:  # PRENSA NA PAREDE
            m["prensou"] = t
            bate(l, outro, jogo, 23, "kun_onda", ultimo=True)
            impacto(jogo, 14, 24, 5)
            solta(outro, -l.dir * 6, -9)
            m["fim"] = t
    if "fim" in m and t - m["fim"] > 34:
        return "fim"


def kun_ult2_efeito(l, tela):
    import kun
    t = l.t
    m = l.memo
    s = l.s
    if t < K_MOSTRA + 4:  # a carta mostrada (vira pra frente e brilha)
        x, y = l.x + l.dir * 52 * s, l.y - 104 * s
        larg = math.cos(min(1, t / K_VIRA) * math.pi)  # de costas -> de frente
        larg = -larg if t < K_VIRA else abs(larg)
        if t >= K_VIRA:
            brilho(tela, (int(x), int(y)), int(40 * s), (255, 230, 150), 140)
        kun.carta(tela, (x, y), 0.08 * math.sin(t * 0.2), 4.2 * s / 1.36, larg if t < K_VIRA else 1,
                  brilha=t >= K_VIRA, l=l)
        if t >= K_MOSTRA:  # estourando
            u = t - K_MOSTRA
            for i in range(14):
                a = i * 0.45
                kun.carta(tela, (x + math.cos(a) * u * 22, y + math.sin(a) * u * 14), a + u, 1.8 * s / 1.36, 1, l=l)
        return
    f = m.get("frente")
    if f is None:
        return
    d = l.dir
    rnd = random.Random(3)
    base = max(0, abs(f - (l.x + d * 40)))
    for i in range(170):  # as cartas da onda: andam pela face da onda, sobem e passam por cima da crista
        atras = rnd.uniform(0, min(base + 40, 360))
        fase = (rnd.random() + t * 0.02 * (1.5 - atras / 360)) % 1.0
        h = onda_altura(atras)
        if h <= 4:
            continue
        x = f - d * atras + d * fase * 30 * (atras < 70)
        y = CHAO - h * fase ** 0.6
        if atras < 70 and fase > 0.7:  # a crista enrolando pra frente
            k = (fase - 0.7) / 0.3
            x += d * k * 40
            y -= math.sin(k * math.pi) * 34
        ang = t * 0.25 * (1 if i % 2 else -1) + i
        kun.carta(tela, (x, y), ang, (1.6 + rnd.random() * 0.8) * s / 1.36, math.cos(t * 0.3 + i),
                  brilha=(i % 13 == 0), l=l)
    for i in range(6):  # a espuma de cartas voando na frente
        a = t * 0.3 + i
        x = f + d * (10 + (t * 5 + i * 17) % 40)
        y = CHAO - K_ALTURA * 0.7 + math.sin(a) * 40
        kun.carta(tela, (x, y), a * 2, 1.4 * s / 1.36, 1, l=l)
    for tc in m.get("cortes", []):  # os cortes brancos lá dentro
        u = t - tc
        if 0 <= u < 5:
            alvo = getattr(l, "_alvo_marujos", None)
            if alvo is not None:
                cx, cy = alvo.x, alvo.y - 50 * alvo.s
                a = tc * 1.7
                pygame.draw.line(tela, (255, 255, 255), (cx - math.cos(a) * 50, cy - math.sin(a) * 50),
                                 (cx + math.cos(a) * 50, cy + math.sin(a) * 50), 4 - u // 2)
    pr = m.get("prensou")
    if pr is not None and t - pr < 26:  # as cartas explodindo na parede
        u = t - pr
        alvo = getattr(l, "_alvo_marujos", None)
        cx = alvo.x if alvo else f
        for i in range(16):
            a = i * 0.39
            kun.carta(tela, (cx + math.cos(a) * u * 14, CHAO - 120 + math.sin(a) * u * 10), a + u * 0.5,
                      1.8 * s / 1.36, 1, l=l)


_dano("kun_onda", 4, hit=30, emp=2)
_registra("kun_ult2", kun_ult2, kun_ult2_efeito,
          [(0, "parado"), (4, "k_lanca"), (K_MOSTRA + 4, "k_lanca"), (K_MOSTRA + 14, "k_vitoria"), (9999, "k_vitoria")])


# =====================================================================
# TROMOS: CAÇADA NO ESCURO
# =====================================================================
X_RUGE, X_QUEBRA, X_FIM = 14, 30, 56
LAMPADA_Y = 120


def xeno_ult2(l, outro, jogo):
    t = l.t
    m = l.memo
    tela_toda(l)
    l.vx = 0
    l.fisica(jogo)
    if t < X_QUEBRA:
        camera(jogo, 1.2, (l.x + LARGURA / 2) / 2, (l.y - 80 + LAMPADA_Y) / 2)
    if t == X_RUGE:
        som.tocar("uivo", 0.6)
    if t == X_QUEBRA:  # a cauda arrebenta a lâmpada
        som.tocar("quebra")
        jogo.tremer(8)
        l.extra["cacada"] = TEMPO_BUFF
        for i in range(10):  # os cacos de vidro caindo (com faísca)
            jogo.faiscas.append([LARGURA / 2 + random.uniform(-14, 14), LAMPADA_Y + 20, random.uniform(-3, 3),
                                 random.uniform(-2, 2), random.randint(30, 50), (220, 240, 255), 3])
            jogo.faiscas.append([LARGURA / 2, LAMPADA_Y + 20, random.uniform(-4, 4), random.uniform(-3, 1),
                                 random.randint(8, 16), (255, 230, 120), 3])
    if t >= X_FIM:
        return "fim"


def xeno_ult2_efeito(l, tela):
    t = l.t
    x0, y0 = LARGURA / 2, 0
    if t <= X_QUEBRA:  # a lâmpada pendurada balançando
        ang = math.sin(t * 0.25) * 0.25 * (1 + t / X_QUEBRA)
        lx, ly = x0 + math.sin(ang) * LAMPADA_Y, LAMPADA_Y
        pygame.draw.line(tela, (30, 30, 34), (x0, y0), (lx, ly), 2)
        brilho(tela, (int(lx), int(ly + 16)), 120, (255, 240, 180), 70)
        cupula = [(lx - 22, ly + 14), (lx - 8, ly), (lx + 8, ly), (lx + 22, ly + 14)]
        pygame.draw.polygon(tela, (60, 64, 70), cupula)
        pygame.draw.polygon(tela, (20, 20, 24), cupula, 2)
        pygame.draw.circle(tela, (255, 250, 220), (int(lx), int(ly + 16)), 7)
    if X_RUGE <= t < X_QUEBRA + 6:  # a cauda subindo como chicote até a lâmpada
        k = min(1, (t - X_RUGE) / (X_QUEBRA - X_RUGE))
        bx, by = l.x - l.dir * 20 * l.s, l.y - 50 * l.s
        tx, ty = bx + (x0 - bx) * k, by + (LAMPADA_Y + 10 - by) * k
        pts = []
        for i in range(12):
            u = i / 11
            onda = math.sin(u * 6 + t * 0.6) * 18 * (1 - u) * (1 - k * 0.6)
            pts.append((bx + (tx - bx) * u + onda, by + (ty - by) * u - math.sin(u * math.pi) * 60))
        for i in range(len(pts) - 1):
            w = int(9 - i * 0.6)
            pygame.draw.line(tela, (14, 14, 18), pts[i], pts[i + 1], w + 3)
            pygame.draw.line(tela, (60, 64, 76), pts[i], pts[i + 1], max(1, w))
        ponta = pts[-1]
        pygame.draw.polygon(tela, (200, 200, 210), [ponta, (ponta[0] - 6, ponta[1] + 10), (ponta[0] + 6, ponta[1] + 10)])
    if X_QUEBRA <= t < X_QUEBRA + 8:  # o estouro da lâmpada
        u = t - X_QUEBRA
        brilho(tela, (int(x0), int(LAMPADA_Y + 16)), 40 + u * 10, (255, 250, 220), max(0, 220 - u * 28))


def desenhar_escuro(partida, tela):
    """CAÇADA NO ESCURO: cada PC desenha o SEU escuro (quem é o Tromos vê verde; o outro quase não vê nada)."""
    cacador = next((l for l in partida.L if l.extra.get("cacada", 0) > 0), None)
    if not cacador:
        return
    from efeitos import texto
    lados = partida.lados_humanos()
    resta = cacador.extra["cacada"]
    passou = TEMPO_BUFF - resta
    entra = min(1, resta / 20)
    if passou < 24:  # a luz piscando 3 vezes antes de apagar de vez
        entra = 0.0 if (passou // 4) % 2 == 0 and passou < 20 else min(1, passou / 24)
    t = getattr(partida, "t_total", 0)
    if lados and partida.L[lados[0]] is cacador:  # VISÃO NOTURNA
        verde = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        verde.fill((20, 255, 80, int(80 * entra)))
        tela.blit(verde, (0, 0))
        linhas = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        for y in range(t % 4, ALTURA, 4):
            pygame.draw.line(linhas, (0, 30, 0, int(110 * entra)), (0, y), (LARGURA, y), 1)
        for i in range(10, 0, -1):  # a borda escura (vinheta)
            pygame.draw.rect(linhas, (0, 20, 0, int(22 * entra)), (0, 0, LARGURA, ALTURA), i * 8)
        tela.blit(linhas, (0, 0))
        if entra > 0.5:
            texto(tela, "VISÃO NOTURNA", 15, (140, 255, 150), (LARGURA - 90, ALTURA - 52))
            texto(tela, f"{resta // FPS + 1} s", 15, (140, 255, 150), (LARGURA - 90, ALTURA - 34))
        return
    eu = partida.L[lados[0]] if lados else None
    escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    escuro.fill((0, 0, 8, int((238 if eu is not None else 150) * entra)))
    if eu is not None:  # só um pouquinho em volta de você (bicho, mutante e robô veem mais)
        r = 150 if nome_de(eu) in VEEM_NO_ESCURO else 80
        cx, cy = int(eu.x), int(eu.y - 60 * eu.s)
        for i in range(6, 0, -1):
            pygame.draw.circle(escuro, (0, 0, 8, int(238 * entra * (i / 6))), (cx, cy), int(r * (0.5 + i / 12)))
        pygame.draw.circle(escuro, (0, 0, 0, 0), (cx, cy), int(r * 0.5))
    tela.blit(escuro, (0, 0))
    if entra > 0.5 and (t // 3) % 7:  # os olhos amarelos dele no escuro
        ex, ey = cacador.x + cacador.dir * 22 * cacador.s, cacador.y - 86 * cacador.s
        for ox in (-5, 5):
            brilho(tela, (int(ex + ox), int(ey)), 7, (255, 210, 40), 160)
            pygame.draw.circle(tela, (255, 230, 90), (int(ex + ox), int(ey)), 2)


_registra("xeno_ult2", xeno_ult2, xeno_ult2_efeito,
          [(0, "parado"), (4, "x_vitoria"), (X_RUGE, "x_vitoria"), (X_RUGE + 4, "x_rabada"), (X_QUEBRA + 6, "x_rabada"),
           (X_FIM, "parado")])


# =====================================================================
# TAI: TERREMOTO
# =====================================================================
TAI_SAL = 18
TAI_PISOES = (44, 72, 100)
TAI_PULA, TAI_CAI = 118, 146


def tai_pisao(l, outro, jogo, ultimo):
    som.tocar("terra", 1.0 if ultimo else 0.75)
    som.tocar("queda", 0.8)
    impacto(jogo, 8 if ultimo else 4, 26 if ultimo else 14, 4 if ultimo else 0)
    fumaca(jogo, l.x - 40, CHAO - 4, 10 if ultimo else 5, (170, 150, 120), 4, -0.8)
    fumaca(jogo, l.x + 40, CHAO - 4, 10 if ultimo else 5, (170, 150, 120), 4, -0.8)
    if ultimo:
        for i in range(12):  # pedras voando
            jogo.faiscas.append([l.x + random.uniform(-120, 120), CHAO - 4, random.uniform(-4, 4),
                                 random.uniform(-11, -5), random.randint(30, 45), (110, 92, 70), 6])
    l.memo.setdefault("ondas", []).append((l.t, ultimo))
    if outro.no_chao() and outro.inv <= 0 and outro.estado not in ("caido", "voando", "agarrado"):
        if ultimo:
            acerta(l, outro, jogo, "tai_terremoto_final")
        elif acerta(l, outro, jogo, "tai_terremoto") == "hit":
            outro.mudar("tonto")
            outro.tonto_tempo = 26
            outro.vy = -4


def tai_ult2(l, outro, jogo):
    t = l.t
    tela_toda(l)
    l.vx = 0
    meio = (l.x + outro.x) / 2
    if t < TAI_SAL:  # o ritual: joga o sal
        camera(jogo, 1.35, l.x, l.y - 90 * l.s)
        if t == 8:
            som.tocar("vento", 0.5)
            for i in range(14):
                jogo.faiscas.append([l.x + l.dir * 20, l.y - 120 * l.s, random.uniform(-3, 3) + l.dir * 2,
                                     random.uniform(-7, -3), random.randint(30, 44), (250, 250, 250), 3])
    for i, tp in enumerate(TAI_PISOES):
        if tp - 18 <= t < tp:  # levanta a perna (zoom nele)
            camera(jogo, 1.3, l.x, l.y - 80 * l.s)
            l.sobrepor = dict(l.poses.get("t_shiko") or l.poses["parado"])
        if tp <= t < tp + 10:  # PISA (a câmera abre)
            camera(jogo, 1.05, meio, CHAO - 120)
            l.sobrepor = dict(l.poses.get("t_pisao") or l.poses["parado"])
        if t == tp:
            tai_pisao(l, outro, jogo, False)
    if TAI_PULA - 10 <= t < TAI_PULA:  # agacha pro pulão
        l.sobrepor = dict(l.poses.get("t_pisao") or l.poses["parado"])
        camera(jogo, 1.25, l.x, l.y - 70 * l.s)
    if TAI_PULA <= t < TAI_CAI:  # o PULÃO
        k = (t - TAI_PULA) / (TAI_CAI - TAI_PULA)
        l.y = CHAO - math.sin(k * math.pi) * 230
        l.sobrepor = dict(l.poses.get("t_shiko") or l.poses["parado"])
        camera(jogo, 1.0, meio, CHAO - 180)
    if t == TAI_CAI:  # CAI COM OS DOIS PÉS
        l.y = CHAO
        l.sobrepor = dict(l.poses.get("t_pisao") or l.poses["parado"])
        tai_pisao(l, outro, jogo, True)
    if t > TAI_CAI:
        camera(jogo, 1.1, meio, CHAO - 120)
    l.fisica(jogo) if not (TAI_PULA <= t < TAI_CAI) else None
    if t >= TAI_CAI + 36:
        l.sobrepor = {}
        return "fim"


def tai_ult2_efeito(l, tela):
    t = l.t
    for t0, ultimo in l.memo.get("ondas", []):
        u = t - t0
        if u < 0 or u > 40:
            continue
        g = 1.8 if ultimo else 1.0
        for lado in (-1, 1):  # a onda de tremor correndo pelo chão
            x = l.x + lado * u * 22 * g
            alto = max(0, (16 - u * 0.4) * g)
            if alto > 0:
                pygame.draw.polygon(tela, (150, 128, 96), [(x - 30 * g, CHAO + 2), (x, CHAO - alto), (x + 30 * g, CHAO + 2)])
                pygame.draw.lines(tela, (60, 44, 28), False, [(x - 30 * g, CHAO + 2), (x, CHAO - alto),
                                                              (x + 30 * g, CHAO + 2)], 2)
        if u < 30:  # as rachaduras saindo do pé
            rnd = random.Random(t0)
            for i in range(5 if ultimo else 3):
                comp = (60 + rnd.uniform(0, 80)) * g * min(1, u / 6)
                lado = rnd.choice((-1, 1))
                pts = [(l.x, CHAO)]
                for j in range(1, 6):
                    pts.append((l.x + lado * comp * j / 5, CHAO + 2 + rnd.uniform(-3, 5)))
                pygame.draw.lines(tela, (40, 28, 16), False, pts, 3 if ultimo else 2)
        if ultimo and u < 14:
            brilho(tela, (int(l.x), int(CHAO)), int(80 + u * 14), (255, 230, 170), max(0, 160 - u * 12))
    alvo = getattr(l, "_alvo_marujos", None)
    if alvo is not None and alvo.estado == "tonto":  # as estrelinhas de tonto
        for i in range(3):
            a = t * 0.2 + i * math.tau / 3
            sx, sy = alvo.x + math.cos(a) * 22, alvo.y - 140 * alvo.s + math.sin(a) * 6
            pygame.draw.polygon(tela, (255, 230, 90), [(sx, sy - 5), (sx + 2, sy - 1), (sx + 6, sy), (sx + 2, sy + 2),
                                                       (sx, sy + 6), (sx - 2, sy + 2), (sx - 6, sy), (sx - 2, sy - 1)])


_dano("tai_terremoto", 5, hit=30, defe=0, emp=0)  # (3 x 5 + 30 = 45; pedido do Gomes: dá pra defender)
_dano("tai_terremoto_final", 30, hit=40, emp=8, derruba=True, voo=(14, 13))
_registra("tai_ult2", tai_ult2, tai_ult2_efeito, [(0, "parado"), (4, "t_sal"), (TAI_SAL, "t_sal"), (TAI_SAL + 6, "parado")])


# =====================================================================
# TAMER: LUA CHEIA (o lobo vira LOBISOMEM)
# =====================================================================
LOBISOMEM_CADA = 50
L_LUA, L_VIRA = 30, 64
LOBI_ATAQUE = 26  # quadros do bote (vai, arranha e volta)


def tamer_ult2(l, outro, jogo):
    t = l.t
    tela_toda(l)
    l.vx = 0
    l.fisica(jogo)
    lx = l.extra.get("lobo_x", l.x - l.dir * 46)
    if t < L_LUA:  # aponta pro céu: a lua cheia sobe
        camera(jogo, 1.05, LARGURA / 2, ALTURA / 2 - 40)
        if t == 6:
            som.tocar("carga", 0.6)
    elif t < L_VIRA:  # o lobo se transformando (câmera nele)
        camera(jogo, 1.4, lx, CHAO - 90)
        if t == L_LUA + 4:
            som.tocar("uivo", 0.9)
        if t % 6 == 0:
            jogo.tremer(4)
    if t == L_VIRA:
        l.extra["lobisomem"] = TEMPO_BUFF
        som.tocar("uivo")
        impacto(jogo, 6, 14, 3)
        fumaca(jogo, lx, CHAO - 40, 12, (80, 80, 96), 4, -1)
    if t >= L_VIRA + 18:
        return "fim"


def tamer_ult2_efeito(l, tela):
    t = l.t
    sobe = suave(min(1, t / L_LUA))
    some = 1 - suave(max(0, (t - L_VIRA - 4) / 14))
    k = sobe * some
    if k <= 0:
        return
    escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    escuro.fill((4, 6, 30, int(170 * k)))
    tela.blit(escuro, (0, 0))
    lua = (LARGURA // 2, int(260 - 160 * sobe))
    brilho(tela, lua, int(140 * k), (230, 240, 255), int(150 * k))
    pygame.draw.circle(tela, (246, 246, 232), lua, int(56 * k))
    for dx, dy, r in ((-18, -12, 9), (14, 10, 12), (-6, 20, 6), (22, -18, 5)):  # crateras
        pygame.draw.circle(tela, (220, 220, 204), (lua[0] + int(dx * k), lua[1] + int(dy * k)), max(1, int(r * k)))
    if L_LUA <= t < L_VIRA + 6:  # o feixe de luar no lobo
        lx = l.extra.get("lobo_x", l.x - l.dir * 46)
        feixe = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        pygame.draw.polygon(feixe, (220, 235, 255, int(60 * k)), [(lua[0] - 30, lua[1]), (lua[0] + 30, lua[1]),
                                                                  (lx + 70, CHAO), (lx - 70, CHAO)])
        tela.blit(feixe, (0, 0))
        u = t - L_LUA
        for i in range(3):  # o uivo (ondas de som)
            r = (u * 6 + i * 26) % 80 + 10
            pygame.draw.circle(tela, (220, 230, 255), (int(lx + l.dir * 10), int(CHAO - 110)), r, 2)


def desenha_lobisomem(tela, x, chao, escala, d, t, ataque=0.0, cresce=1.0):
    """O LOBISOMEM em pé: pernas de lobo dobradas, peitão, braços compridos com garras, focinho e olhos vermelhos.
    (escala = o tamanho do Tamer na tela: o lobisomem fica uns 30% mais alto que ele)"""
    s = escala * 1.5 * cresce
    pelo, escuro, claro, borda = (78, 70, 78), (50, 44, 52), (130, 120, 126), (14, 12, 16)
    curva = 8 * ataque  # (no bote ele se joga pra frente)

    def P(fx, fy):
        return (x + d * (fx + curva * fy / 100) * s, chao - fy * s)

    def osso(a, b, w, cor):
        pygame.draw.line(tela, borda, a, b, int((w + 3) * s))
        pygame.draw.line(tela, cor, a, b, int(w * s))
        pygame.draw.circle(tela, borda, (int(b[0]), int(b[1])), int((w + 3) * s / 2))
        pygame.draw.circle(tela, cor, (int(b[0]), int(b[1])), int(w * s / 2))

    respira = math.sin(t * 0.12) * 1.5
    # cauda
    osso(P(-14, 54), P(-30, 44 + math.sin(t * 0.2) * 4), 6, escuro)
    # perna de trás e braço de trás
    osso(P(-6, 56), P(4, 36), 11, escuro)
    osso(P(4, 36), P(-6, 14), 7, escuro)
    osso(P(-6, 14), P(2, 0), 5, escuro)
    osso(P(8, 96 + respira), P(-4, 74), 8, escuro)
    osso(P(-4, 74), P(4, 54), 6, escuro)
    # o corpo (peitão curvado pra frente)
    tronco = [P(-14, 50), P(-16, 76), P(-4, 104 + respira), P(18, 108 + respira), P(26, 90), P(14, 58), P(0, 48)]
    pygame.draw.polygon(tela, borda, tronco)
    pygame.draw.polygon(tela, pelo, [(px + (P(4, 78)[0] - px) * 0.08, py + (P(4, 78)[1] - py) * 0.08) for px, py in tronco])
    pygame.draw.polygon(tela, claro, [P(6, 62), P(18, 86), P(12, 96), P(4, 76)])  # a barriga mais clara
    for fx, fy in ((-12, 100), (-6, 106), (0, 110)):  # tufos de pelo nas costas
        pygame.draw.polygon(tela, escuro, [P(fx, fy + respira), P(fx - 8, fy + 8 + respira), P(fx + 2, fy + 2 + respira)])
    # a perna da frente (dobrada pra trás, de lobo)
    osso(P(4, 56), P(16, 36), 12, pelo)
    osso(P(16, 36), P(4, 14), 8, pelo)
    osso(P(4, 14), P(14, 0), 6, pelo)
    # a cabeça de lobo
    hx, hy = 24, 112 + respira
    abre = ataque * 6
    cab = [P(hx - 10, hy - 4), P(hx - 8, hy + 8), P(hx + 4, hy + 10), P(hx + 16, hy + 4), P(hx + 24, hy),
           P(hx + 24, hy - 4), P(hx + 6, hy - 6)]
    pygame.draw.polygon(tela, borda, cab)
    pygame.draw.polygon(tela, pelo, [(px + (P(hx + 6, hy + 2)[0] - px) * 0.1, py + (P(hx + 6, hy + 2)[1] - py) * 0.1)
                                     for px, py in cab])
    queixo = [P(hx, hy - 6), P(hx + 20, hy - 6 - abre), P(hx + 14, hy - 10 - abre), P(hx, hy - 10)]
    pygame.draw.polygon(tela, escuro, queixo)
    for i in range(4):  # os dentes
        tx = hx + 8 + i * 4
        pygame.draw.polygon(tela, (240, 240, 230), [P(tx, hy - 5), P(tx + 2, hy - 5), P(tx + 1, hy - 8)])
    for ox in (-2, 4):  # as orelhas
        pygame.draw.polygon(tela, borda, [P(hx + ox - 4, hy + 8), P(hx + ox - 6, hy + 22), P(hx + ox + 3, hy + 9)])
        pygame.draw.polygon(tela, escuro, [P(hx + ox - 3, hy + 9), P(hx + ox - 5, hy + 19), P(hx + ox + 1, hy + 9)])
    pygame.draw.circle(tela, borda, P(hx + 24, hy - 2), max(2, int(2.6 * s)))  # o nariz
    olho = P(hx + 8, hy + 4)
    brilho(tela, (int(olho[0]), int(olho[1])), int(8 * s), (255, 40, 30), 170)
    pygame.draw.circle(tela, (255, 70, 50), (int(olho[0]), int(olho[1])), max(2, int(2.2 * s)))
    # o braço da frente (arranhando no bote)
    ombro = P(12, 98 + respira)
    if ataque > 0:
        cot = P(30, 104 - 30 * ataque)
        mao = P(48, 110 - 60 * ataque)
    else:
        cot = P(24, 78)
        mao = P(34, 64)
    osso(ombro, cot, 10, pelo)
    osso(cot, mao, 8, pelo)
    for i in (-1, 0, 1):  # as garras
        a = math.atan2(mao[1] - cot[1], mao[0] - cot[0]) + i * 0.4
        pygame.draw.line(tela, (240, 236, 220), mao, (mao[0] + math.cos(a) * 9 * s, mao[1] + math.sin(a) * 9 * s),
                         max(2, int(2 * s)))


def lobisomem_passo(l, o, jogo):
    """A cada pouco o lobisomem dá um bote no adversário (vai, arranha e volta)."""
    x = l.extra
    if x.get("lobisomem", 0) <= 0:
        x.pop("lobi_ataque", None)
        return
    if "lobi_ataque" in x:
        x["lobi_ataque"] += 1
        if x["lobi_ataque"] == 10 and o.inv <= 0 and o.estado not in ("caido", "agarrado"):
            if abs(o.x - x.get("lobi_de", l.x)) < 280:
                acerta(l, o, jogo, "lobisomem_garra")
                som.tocar("uivo", 0.3)
        if x["lobi_ataque"] >= LOBI_ATAQUE:
            x.pop("lobi_ataque")
    elif x["lobisomem"] % LOBISOMEM_CADA == 0 and abs(o.x - l.x) < 300:
        x["lobi_ataque"] = 0
        x["lobi_de"] = x.get("lobo_x", l.x)
        x["lobi_ate"] = o.x - (1 if o.x > x["lobi_de"] else -1) * 50


def lobisomem_onde(l):
    """Onde o lobisomem está (no mundo) e o quanto está atacando (0 a 1)."""
    x = l.extra
    base = x.get("lobo_x", l.x - l.dir * 46)
    if "lobi_ataque" not in x:
        return base, 0.0, None
    u = x["lobi_ataque"]
    ida = suave(min(1, u / 8)) * (1 - suave(max(0, (u - 14) / 12)))
    de, ate = x.get("lobi_de", base), x.get("lobi_ate", base)
    garra = min(1, max(0, (u - 6) / 4)) * (1 - max(0, (u - 14) / 6))
    return de + (ate - de) * ida, garra, 1 if ate > de else -1


_dano("lobisomem_garra", 5, hit=22, defe=8, emp=3, ultimate=False, ultimate2=False)
_registra("tamer_ult2", tamer_ult2, tamer_ult2_efeito,
          [(0, "parado"), (4, "t_aponta"), (L_LUA, "t_aponta"), (L_LUA + 6, "t_grito"), (L_VIRA + 10, "t_grito"),
           (L_VIRA + 18, "parado")])


# =====================================================================
# JOHN: A RAVINA
# =====================================================================
J_MAGICA, J_AFUNDA, J_CAI, J_BATE, J_VOLTA = 22, 18, 62, 10, 22
J_PEGA = J_MAGICA
J_QUEDA = J_PEGA + J_AFUNDA            # começa a cena da queda
J_CHAO = J_QUEDA + J_CAI               # BUM lá no fundo
J_SAI = J_CHAO + J_BATE + J_VOLTA      # sai da cartola
ROXO = (170, 90, 230)


def john_ult2(l, outro, jogo):
    t = l.t
    m = l.memo
    tela_toda(l)
    l.vx = 0
    l.fisica(jogo)
    if t < J_MAGICA:  # "Abracadabra!" (câmera nos dois)
        camera(jogo, 1.2, (l.x + outro.x) / 2, l.y - 90 * l.s)
        if t == 6:
            som.tocar("carga", 0.6)
        return
    if t == J_PEGA:
        if pode_pegar(outro) and abs(outro.x - l.x) < 460:  # abre o portal embaixo dele
            m["pegou"] = t
            m["portal_x"] = outro.x
            pega(outro, "golpeado")
            outro.cortar_chao = True
            som.tocar("puf")
        else:
            m["errou"] = t
    if "errou" in m:
        return "fim" if t - m["errou"] > 18 else None
    outro.inv = 2
    if t < J_QUEDA:  # afundando no portal
        k = (t - J_PEGA) / J_AFUNDA
        outro.y = CHAO + suave(k) * 150 * outro.s
        camera(jogo, 1.35, m["portal_x"], CHAO - 60)
        return
    if t == J_QUEDA:
        outro.esconde = True
        outro.cortar_chao = False
        som.tocar("vento")
    if t == J_CHAO:  # BUM lá no fundo da ravina
        bate(l, outro, jogo, 40, "john_ravina")
        som.tocar("queda")
        som.tocar("ko", 0.5)
        jogo.tremer(18)
    if t == J_SAI:  # e sai da CARTOLA, tonto
        outro.esconde = False
        outro.sobrepor = {}
        outro.x = max(PAREDE_E, min(PAREDE_D, l.x + l.dir * 70 * l.s))
        outro.y = CHAO
        outro.inv = 0
        bate(l, outro, jogo, 15, "john_ravina", ultimo=True)
        if outro.vida > 0:
            outro.mudar("tonto")
            outro.tonto_tempo = 60
        fumaca(jogo, l.x + l.dir * 30, l.y - 120 * l.s, 14, ROXO, 4, -1)
        som.tocar("puf")
        som.tocar("confirma", 0.5)
    if t > J_SAI:
        camera(jogo, 1.2, (l.x + outro.x) / 2, l.y - 80 * l.s)
    if t >= J_SAI + 30:
        return "fim"


def balao(tela, txt, pos):
    from efeitos import fonte
    img = fonte(16).render(txt, True, (20, 16, 30))
    caixa = img.get_rect(midbottom=(int(pos[0]), int(pos[1])))
    caixa.clamp_ip(pygame.Rect(4, 4, LARGURA - 8, ALTURA - 8))
    pygame.draw.rect(tela, (12, 10, 20), caixa.inflate(22, 16), border_radius=10)
    pygame.draw.rect(tela, (250, 248, 236), caixa.inflate(18, 12), border_radius=9)
    tela.blit(img, caixa)


def john_ult2_efeito(l, tela):
    t = l.t
    m = l.memo
    s = l.s
    alvo = getattr(l, "_ravina_alvo", None)
    if t < J_MAGICA + 4:  # o balão e as faíscas da varinha até ele
        if t > 4:
            balao(tela, "Abracadabra!", (l.x, l.y - 150 * s))
        if alvo is not None and t > 8:
            p = l.pose_vista or l.pose_atual()
            mx, my = l.ponto(p, "mf")
            for i in range(6):
                k = ((t * 0.08 + i / 6) % 1.0)
                x = mx + (alvo.x - mx) * k
                y = my + (alvo.y - 60 * alvo.s - my) * k - math.sin(k * math.pi) * 40
                pygame.draw.circle(tela, (230, 200, 255), (int(x), int(y)), 3)
    if "pegou" in m and t < J_QUEDA + 4:  # o PORTAL roxo no chão
        k = min(1, (t - J_PEGA) / 6) * (1 - max(0, (t - J_QUEDA) / 4))
        px = m["portal_x"]
        r = 70 * k * s
        caixa = pygame.Rect(0, 0, r * 2, r * 0.45)
        caixa.center = (int(px), int(CHAO))
        pygame.draw.ellipse(tela, (20, 6, 30), caixa)
        for i in range(4):  # o redemoinho
            a = t * 0.4 + i * 1.57
            pygame.draw.arc(tela, ROXO, caixa.inflate(-i * 10, -i * 3), a, a + 2.2, 3)
        brilho(tela, (int(px), int(CHAO)), int(r * 1.2), ROXO, 90)
    if "pegou" in m and J_QUEDA <= t < J_CHAO + J_BATE + 6:
        desenha_ravina(l, tela, t - J_QUEDA, alvo)
    if J_SAI - 8 <= t < J_SAI + 14 and "pegou" in m:  # a cartola virada na mão: ele sai de dentro
        p = l.pose_vista or l.pose_atual()
        hx, hy = l.ponto(p, "mf")
        aba = pygame.Rect(0, 0, 30 * s, 6 * s)
        aba.center = (int(hx), int(hy - 4 * s))
        copa = pygame.Rect(0, 0, 20 * s, 18 * s)
        copa.midtop = aba.center
        pygame.draw.rect(tela, (20, 18, 24), copa, border_radius=3)
        pygame.draw.ellipse(tela, (20, 18, 24), aba)
        pygame.draw.ellipse(tela, (60, 30, 90), aba.inflate(-8, -2))
        if t < J_SAI:
            brilho(tela, aba.center, int(30 * s), ROXO, 160)


def desenha_ravina(l, tela, u, alvo):
    """A cena da queda: a tela toda vira a ravina, ele caindo lá no meio, cada vez menor, até o BUM."""
    tela.fill((26, 12, 40))
    queda = u * 26
    fundo_sobe = max(0, u - (J_CAI - 26)) / 26  # o fundo da ravina aparecendo
    for i in range(14):  # as paredes de pedra passando pra cima
        for lado in (-1, 1):
            y = (i * 64 - queda) % (ALTURA + 128) - 64
            x = LARGURA / 2 + lado * (250 + math.sin(i * 1.7) * 50 + (y / ALTURA) * -40)
            cor = (64 - i % 3 * 8, 44, 82 - i % 3 * 8)
            pts = [(x, y), (x + lado * 420, y - 10), (x + lado * 420, y + 74), (x + lado * 18, y + 66)]
            pygame.draw.polygon(tela, cor, pts)
            pygame.draw.polygon(tela, (16, 8, 24), pts, 3)
    escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    for k in range(8):  # mais escuro lá embaixo
        escuro.fill((0, 0, 0, 18 * k), (0, ALTURA - (k + 1) * 50, LARGURA, 50))
    tela.blit(escuro, (0, 0))
    for i in range(22):  # os riscos de vento
        x = (i * 53) % LARGURA
        y = (i * 97 - queda * 2.2) % ALTURA
        pygame.draw.line(tela, (150, 120, 190), (x, y), (x, y + 46), 2)
    for i in range(10):  # faíscas roxas da mágica
        x = LARGURA / 2 + math.sin(u * 0.2 + i) * 160
        y = (i * 61 - queda * 1.5) % ALTURA
        pygame.draw.circle(tela, (220, 180, 255), (int(x), int(y)), 2)
    if fundo_sobe > 0:  # o chão lá do fundo chegando
        y0 = ALTURA - suave(fundo_sobe) * 150
        pygame.draw.polygon(tela, (50, 34, 40), [(0, ALTURA), (0, y0 + 30), (300, y0), (660, y0 + 10), (LARGURA, y0 + 34),
                                                 (LARGURA, ALTURA)])
        pygame.draw.lines(tela, (20, 12, 16), False, [(0, y0 + 30), (300, y0), (660, y0 + 10), (LARGURA, y0 + 34)], 3)
    if alvo is not None and u < J_CAI:  # ele caindo, girando e ficando menor
        guarda = (alvo.x, alvo.y, alvo.angulo, alvo.esconde, getattr(alvo, "chao_sombra", CHAO), alvo.s)
        try:
            k = u / J_CAI
            alvo.x = LARGURA / 2 + math.sin(u * 0.1) * 40
            alvo.y = ALTURA * 0.42 + k * k * ALTURA * 0.45
            alvo.s = guarda[5] * (1.4 - 0.7 * k)
            alvo.angulo = u * 0.28
            alvo.esconde = False
            alvo.chao_sombra = ALTURA + 400
            alvo.desenhar(tela)
        finally:
            alvo.x, alvo.y, alvo.angulo, alvo.esconde, alvo.chao_sombra, alvo.s = guarda
    if u >= J_CAI:  # BUM
        v = u - J_CAI
        cx, cy = LARGURA / 2, ALTURA - 120
        explosao(tela, cx, cy, v * 2, 2.0)
        from efeitos import texto_grande
        texto_grande(tela, "BUM!", 64, (255, 230, 120), (int(cx), int(cy - 120)), 1 + max(0, 4 - v) * 0.15,
                     contorno=(60, 20, 0))


_dano("john_ravina", 40, hit=30, emp=2)
_registra("john_ult2", john_ult2, john_ult2_efeito,
          [(0, "parado"), (4, "j_magica"), (J_MAGICA, "j_magica"), (J_MAGICA + 6, "j_magica_b"), (J_QUEDA, "j_magica_b"),
           (J_SAI - 10, "j_tira"), (J_SAI + 14, "j_tira"), (J_SAI + 26, "j_agradece"), (9999, "j_agradece")])


# =====================================================================
# CRÁQUEN: O KRAKEN DESPERTA (com água) / TRIPULAÇÃO FANTASMA (sem água)
# =====================================================================
KR_POCO, KR_PEGA, KR_SOBE = 12, 30, 22
KR_BATIDAS = (78, 104, 134)
KR_FIM = KR_BATIDAS[-1] + 34
MARUJO_CADA = 5 * FPS
MARUJO_VOA = 24
M_SAEM = 54  # quadros dos marujos aparecendo e correndo pra fora
KRAKEN, KRAKEN_ESC, VENTOSA = (120, 52, 84), (60, 20, 40), (240, 190, 200)


def craquen_ult2(l, outro, jogo):
    t = l.t
    m = l.memo
    tela_toda(l)
    l.vx = 0
    l.fisica(jogo)
    cena = getattr(jogo, "cena", None)
    if t == 1:
        m["kraken"] = bool(cena) and cena.nome in AGUA
        som.tocar("terra", 0.8)
    if not m["kraken"]:  # TRIPULAÇÃO FANTASMA
        camera(jogo, 1.2, l.x + l.dir * 60, l.y - 80 * l.s)
        if t in (10, 16, 22, 28, 34):
            som.tocar("puf", 0.5)
        if t == M_SAEM - 6:
            l.extra["marujos"] = [MARUJO_CADA * (k + 1) for k in range(5)]
            som.tocar("vento")
        if t >= M_SAEM:
            return "fim"
        return
    if t < KR_PEGA:  # o redemoinho embaixo dele
        if t == KR_POCO:
            m["poco_x"] = outro.x
            som.tocar("lingua", 0.5)
        camera(jogo, 1.25, outro.x, CHAO - 80)
        if t % 6 == 0:
            jogo.tremer(4)
        return
    if t == KR_PEGA:
        if pode_pegar(outro, 120) and abs(outro.x - m.get("poco_x", outro.x)) < 80:
            m["pegou"] = t
            pega(outro)
            som.tocar("terra")
            fumaca(jogo, outro.x, CHAO - 4, 14, (190, 230, 240), 5, -2)
        else:
            m["errou"] = t
    if "errou" in m:
        return "fim" if t - m["errou"] > 24 else None
    if "pegou" not in m:
        return
    px = m["poco_x"]
    outro.x = px
    camera(jogo, 1.0, px, CHAO - 170)
    alto = 0.0
    for i, tb in enumerate(KR_BATIDAS):
        ini = (KR_PEGA + KR_SOBE) if i == 0 else KR_BATIDAS[i - 1] + 4
        if ini <= t < tb - 6:  # levanta bem alto
            alto = suave((t - ini) / max(1, tb - 6 - ini)) * 230
        elif tb - 6 <= t < tb:  # e desce com tudo
            alto = 230 * (1 - (t - tb + 6) / 6)
        if t == tb:  # BATE NO CHÃO
            ultimo = i == len(KR_BATIDAS) - 1
            bate(l, outro, jogo, 30 if ultimo else 15, "craquen_kraken", ultimo=ultimo)
            impacto(jogo, 10 if ultimo else 6, 24 if ultimo else 16, 4 if ultimo else 0)
            fumaca(jogo, px, CHAO - 4, 16, (190, 230, 240), 6, -2.5)
            som.tocar("queda")
            if ultimo:
                solta(outro, l.dir * 9, -11)
    if KR_PEGA <= t < KR_PEGA + KR_SOBE:
        alto = suave((t - KR_PEGA) / KR_SOBE) * 60
    if "pegou" in m and t < KR_BATIDAS[-1]:
        outro.y = CHAO - alto
        m["alto"] = alto
    if t >= KR_FIM:
        return "fim"


def tentaculo(tela, base, ponta, w, t, fase=0.0, enrola=0.0):
    """Um tentáculo gigante: grosso na base, fino na ponta, ventosas embaixo, ondulando."""
    pts = []
    n = 16
    for i in range(n + 1):
        u = i / n
        x = base[0] + (ponta[0] - base[0]) * u + math.sin(u * 5 + t * 0.15 + fase) * 26 * (1 - u) * u * 2
        y = base[1] + (ponta[1] - base[1]) * u
        if enrola > 0 and u > 0.75:  # a ponta enrolando
            a = (u - 0.75) / 0.25 * math.pi * 1.6 * enrola + fase
            x += math.cos(a) * 20 * enrola
            y += math.sin(a) * 14 * enrola
        pts.append((x, y))
    for camada, (cor, extra) in enumerate(((KRAKEN_ESC, 5), (KRAKEN, 0))):
        for i in range(n):
            larg = max(3, w * (1 - i / n * 0.8) + extra)
            pygame.draw.line(tela, cor, pts[i], pts[i + 1], int(larg))
            pygame.draw.circle(tela, cor, (int(pts[i + 1][0]), int(pts[i + 1][1])), int(larg / 2))
    for i in range(1, n, 2):  # as ventosas
        larg = w * (1 - i / n * 0.8)
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        a = math.atan2(y1 - y0, x1 - x0)
        vx, vy = x0 - math.sin(a) * larg * 0.3, y0 + math.cos(a) * larg * 0.3
        pygame.draw.circle(tela, VENTOSA, (int(vx), int(vy)), max(2, int(larg * 0.16)))
        pygame.draw.circle(tela, KRAKEN_ESC, (int(vx), int(vy)), max(1, int(larg * 0.08)))


def craquen_ult2_efeito(l, tela):
    m = l.memo
    t = l.t
    if not m.get("kraken"):
        if t < M_SAEM:  # os 5 marujos fantasmas saindo do chão e correndo pra fora
            for k in range(5):
                t0 = 10 + k * 6
                if t < t0:
                    continue
                u = t - t0
                sobe = min(1, u / 10)
                x = l.x + l.dir * (40 + k * 26) + (l.dir if k % 2 else -l.dir) * max(0, u - 14) ** 1.6
                y = CHAO - 40 * sobe
                desenha_marujo(tela, x, y, l.dir if k % 2 else -l.dir, t + k * 7, alfa=int(170 * sobe))
        return
    px = m.get("poco_x")
    if px is None:
        return
    fecha = 1 - suave(max(0, (t - KR_BATIDAS[-1] - 10) / 20))
    abre = min(1, (t - KR_POCO) / 10) * fecha
    if abre > 0:  # o redemoinho escuro no chão
        r = 120 * abre
        caixa = pygame.Rect(0, 0, r * 2, r * 0.38)
        caixa.center = (int(px), int(CHAO + 2))
        pygame.draw.ellipse(tela, (10, 30, 44), caixa)
        for i in range(5):
            a = t * 0.3 + i * 1.2
            pygame.draw.arc(tela, (80, 170, 200), caixa.inflate(-i * 18, -i * 6), a, a + 2.0, 2)
        for i in range(5):  # bolhas
            bx = px + math.sin(i * 2.1 + t * 0.1) * r * 0.6
            pygame.draw.circle(tela, (200, 240, 250), (int(bx), int(CHAO - (t * 2 + i * 19) % 40)), 4, 1)
    if "pegou" not in m:
        return
    u = t - m["pegou"]
    if u < 40 or t > KR_BATIDAS[-1]:  # o OLHO gigante do kraken espiando do redemoinho
        k = min(1, u / 12) * fecha
        ex, ey = px - l.dir * 90, CHAO + 10 - 40 * k
        pygame.draw.ellipse(tela, KRAKEN_ESC, (ex - 46 * k, ey - 26 * k, 92 * k, 52 * k))
        pygame.draw.ellipse(tela, (255, 200, 40), (ex - 34 * k, ey - 18 * k, 68 * k, 36 * k))
        pygame.draw.ellipse(tela, (20, 10, 6), (ex - 5 * k, ey - 16 * k, 10 * k, 32 * k))
    alto = m.get("alto", 0)
    sai = min(1, u / 10) * fecha
    if sai <= 0:
        return
    corpo_y = CHAO - alto - 50
    for lado, fase in ((-1, 0.0), (1, 1.7)):  # os dois tentáculos segurando ele
        base = (px + lado * 70, CHAO + 30)
        ponta = (px + lado * 18, corpo_y - 40 * sai)
        tentaculo(tela, base, (base[0] + (ponta[0] - base[0]) * sai, base[1] + (ponta[1] - base[1]) * sai),
                  44, t, fase, enrola=sai)


def desenha_marujo(tela, x, y, d, t, alfa=170):
    """Um marujo fantasma: chapéu pirata, cara de caveira, sabre e o rabo de fumaça."""
    sup = pygame.Surface((70, 90), pygame.SRCALPHA)
    cor = (170, 240, 220, alfa)
    escuro = (20, 50, 50, alfa)
    pygame.draw.polygon(sup, cor, [(20, 30), (50, 30), (54, 62), (44, 76 + math.sin(t * 0.3) * 4), (35, 66),
                                   (26, 82 + math.sin(t * 0.3 + 1) * 4), (16, 62)])  # o corpo de fumaça
    pygame.draw.circle(sup, cor, (35, 26), 14)  # a cabeça
    pygame.draw.circle(sup, escuro, (30, 25), 4)
    pygame.draw.circle(sup, escuro, (41, 25), 4)
    pygame.draw.line(sup, escuro, (29, 34), (41, 34), 2)
    pygame.draw.polygon(sup, (40, 30, 30, alfa), [(16, 16), (35, 6), (54, 16), (35, 13)])  # o chapéu
    pygame.draw.line(sup, (220, 230, 240, alfa), (52, 46), (66, 26), 3)  # o sabre
    pygame.draw.line(sup, (90, 70, 40, alfa), (49, 50), (54, 44), 4)
    if d < 0:
        sup = pygame.transform.flip(sup, True, False)
    tela.blit(sup, (x - 35, y - 45))


def marujos_passo(l, o, jogo):
    marujos = l.extra.get("marujos")
    if not marujos:
        return
    for i in range(len(marujos)):
        marujos[i] -= 1
        if marujos[i] == 0:  # o marujo fantasma volta e dá UM golpe de sabre
            if o.inv <= 0 and o.estado not in ("caido", "agarrado"):
                acerta(l, o, jogo, "marujo_hit")
                som.tocar("puf", 0.5)
    l.extra["marujos"] = [v for v in marujos if v > -10]


def desenha_marujos(l, tela):
    marujos = l.extra.get("marujos")
    if not marujos:
        return
    alvo = getattr(l, "_alvo_marujos", None)
    for v in marujos:
        if -8 <= v < MARUJO_VOA and alvo is not None:  # voando de volta pra bater (e o corte)
            k = 1 - max(0, v) / MARUJO_VOA
            de = PAREDE_E - 60 if alvo.x > LARGURA / 2 else PAREDE_D + 60
            x = de + (alvo.x - de) * k
            y = alvo.y - 70 * alvo.s - math.sin(k * math.pi) * 60
            desenha_marujo(tela, x, y, 1 if alvo.x > de else -1, v)
            if v <= 0:
                pygame.draw.arc(tela, (230, 255, 245), (alvo.x - 50, alvo.y - 130 * alvo.s, 100, 100), 0.4, 2.6, 4)


_dano("craquen_kraken", 15, hit=40, emp=2)
_dano("marujo_hit", 10, hit=22, defe=10, emp=3, ultimate=False, ultimate2=False)
_registra("craquen_ult2", craquen_ult2, craquen_ult2_efeito,
          [(0, "parado"), (4, "q_comanda"), (KR_FIM - 20, "q_comanda"), (KR_FIM, "q_ri"), (9999, "q_ri")])


# =====================================================================
# MAGNUS: MODO FORNALHA
# =====================================================================
F_ABRE, F_EXPLODE, F_FIM = 22, 30, 54


def magnus_ult2(l, outro, jogo):
    import magnus
    t = l.t
    tela_toda(l)
    l.vx = 0
    l.fisica(jogo)
    if t < F_EXPLODE:
        camera(jogo, 1.4, l.x, l.y - 60 * l.s)
    if t == 4:
        som.tocar("defesa", 0.6)  # (as placas destravando)
    if 6 <= t < F_EXPLODE and t % 3 == 0:  # vapor saindo das frestas
        fumaca(jogo, l.x - l.dir * 10 * l.s, l.y - 70 * l.s, 2, (200, 200, 206), 1.5, -1.6)
    if t == F_ABRE:
        som.tocar("carga", 0.8)
    if t == F_EXPLODE:  # FORNALHA ACESA
        l.extra["fornalha"] = TEMPO_BUFF
        som.tocar("explosao")
        som.tocar("ultimate", 0.6)
        impacto(jogo, 10, 20, 4)
        for i in range(24):
            a = i * math.tau / 24
            jogo.faiscas.append([l.x + math.cos(a) * 20, l.y - 50 * l.s + math.sin(a) * 20, math.cos(a) * 7,
                                 math.sin(a) * 5 - 2, random.randint(16, 26), (255, random.randint(90, 200), 30), 6])
    if t > F_EXPLODE:
        camera(jogo, 1.15, l.x, l.y - 70 * l.s)
        if t % 2 == 0:
            magnus.chama(jogo, l.x + random.uniform(-40, 40) * l.s, l.y - random.uniform(20, 80) * l.s, 2, 1.4)
    if t >= F_FIM:
        return "fim"


def costas_magnus(l):
    """Pontos das costas do Magnus (na tela), do quadril até o peito."""
    import magnus
    p = l.pose_vista or l.pose_atual()
    e = magnus.esqueleto(l, p)
    H, C = e["quadril"], e["peito"]
    pts = []
    for k in range(4):
        u = 0.15 + k * 0.25
        x, y = H[0] + (C[0] - H[0]) * u, H[1] + (C[1] - H[1]) * u + 12
        pts.append(l.ponto({"o": (x, y)}, "o"))
    return pts


def magnus_ult2_efeito(l, tela):
    t = l.t
    s = l.s
    if t < F_EXPLODE + 4:  # as placas das costas abrindo (fogo por dentro)
        abre = suave(min(1, max(0, (t - 4) / (F_ABRE - 4))))
        for i, (x, y) in enumerate(costas_magnus(l)):
            brilho(tela, (int(x), int(y)), int((10 + 10 * abre) * s), (255, 140, 40), int(160 * abre))
            ang = abre * 1.1
            w = 9 * s
            placa = [(x - w, y), (x + w, y), (x + w - l.dir * math.sin(ang) * 8 * s, y - 12 * s * math.cos(ang * 0.5)),
                     (x - w - l.dir * math.sin(ang) * 8 * s, y - 12 * s * math.cos(ang * 0.5))]
            pygame.draw.polygon(tela, (14, 14, 18), placa)
            pygame.draw.polygon(tela, (140, 146, 158), [(px + (x - px) * 0.15, py + (y - 6 * s - py) * 0.15) for px, py in placa])
    if F_EXPLODE <= t < F_EXPLODE + 14:  # a explosão de fogo
        explosao(tela, l.x, l.y - 50 * s, (t - F_EXPLODE) * 2, 1.6)


def fornalha_passo(l, jogo):
    if l.extra.get("fornalha", 0) > 0:
        import magnus
        for _ in range(3):  # o corpo pegando fogo (costas e cauda)
            k = random.random()
            x = l.x - l.dir * (k * 90 - 20) * l.s
            y = l.y - (60 - k * 25 + random.uniform(-8, 8)) * l.s
            magnus.chama(jogo, x, y, 1, 1.6)


_registra("magnus_ult2", magnus_ult2, magnus_ult2_efeito,
          [(0, "parado"), (4, "m_fareja"), (F_ABRE, "m_fareja"), (F_EXPLODE - 4, "m_ruge"), (F_FIM - 8, "m_ruge"),
           (F_FIM, "parado")])


# =====================================================================
# SPHYRUS: uma 2ª ultimate por passiva
# =====================================================================
S_MAR = 18


def sphyrus_ult2(l, outro, jogo):
    import habilidades as hab
    t = l.t
    m = l.memo
    tela_toda(l)
    if t == 1:
        hs = hab.ativas(l)
        m["tipo"] = "frenesi" if "frenesi" in hs else "eletro" if "eletro" in hs else "natacao"
        som.tocar("terra", 0.8)
    tipo = m["tipo"]
    if tipo == "natacao":
        return ancestral(l, outro, jogo)
    if tipo == "eletro":
        return cardume(l, outro, jogo)
    return tornado(l, outro, jogo)


A_SOBE, A_ABERTO, A_MORDE, A_AFUNDA, A_VOLTA = 56, 70, 84, 104, 116


def ancestral(l, o, jogo):
    """O ANCESTRAL: o chão vira mar e um MOSASSAURO GIGANTE (o avô dele) sobe por baixo, abocanha e afunda."""
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    m["mar"] = min(1, t / S_MAR) if t < A_VOLTA else max(0, 1 - (t - A_VOLTA) / 20)
    if t < S_MAR:
        camera(jogo, 1.3, l.x, l.y - 80 * l.s)
    if t == S_MAR:
        if pode_pegar(o):
            m["pegou"] = t
            m["x"] = o.x
            pega(o)
        else:
            m["errou"] = t
    if "errou" in m:
        m["mar"] = max(0, 1 - (t - m["errou"]) / 20)
        return "fim" if t - m["errou"] > 24 else None
    if "pegou" not in m:
        return
    camera(jogo, 1.0, m["x"], CHAO - 170)
    if S_MAR < t < A_SOBE and t % 8 == 0:  # a sombra enorme passando embaixo d'água
        jogo.tremer(5)
        som.tocar("terra", 0.4)
    if t == A_SOBE:  # ELE SOBE
        som.tocar("terra")
        impacto(jogo, 4, 22)
        fumaca(jogo, m["x"], CHAO - 4, 24, (210, 236, 255), 9, -4)
    if A_SOBE <= t < A_MORDE:  # o adversário sobe junto com a água, entre as mandíbulas
        o.y = CHAO - suave(min(1, (t - A_SOBE) / (A_ABERTO - A_SOBE))) * 70
    if t == A_MORDE:  # CHOMP
        bate(l, o, jogo, 50, "sphyrus_ancestral")
        impacto(jogo, 12, 26, 5)
        o.esconde = True
        som.tocar("ko")
    if t == A_AFUNDA:
        fumaca(jogo, m["x"], CHAO - 4, 20, (210, 236, 255), 8, -3)
        som.tocar("puf")
    if t == A_VOLTA:  # e cospe ele de volta
        o.esconde = False
        o.y = CHAO - 40
        bate(l, o, jogo, 15, "sphyrus_ancestral", ultimo=True)
        solta(o, -l.dir * 5, -15)
        fumaca(jogo, o.x, CHAO - 4, 14, (210, 236, 255), 6, -3)
    if t >= A_VOLTA + 26:
        return "fim"


def mosassauro(tela, x, sobe, abre, d, t, mega=False):
    """A cabeça GIGANTE saindo do mar de boca pra cima (sobe 0..1 = quanto já saiu; abre 0..1).
    mega = roupa MEGALODONTE: vira um megalodonte gigante (cinza, olho preto)."""
    if sobe <= 0:
        return
    inclina = 0.22 * d
    fx, fy = math.sin(inclina), -math.cos(inclina)  # pra cima
    nx, ny = math.cos(inclina), math.sin(inclina)   # pro lado
    comp = 330 * sobe
    junta = (x - nx * 10, CHAO + 60)

    def P(ao_longo, ao_lado, lado, ang):
        px = ao_longo * fx + ao_lado * lado * nx
        py = ao_longo * fy + ao_lado * lado * ny
        a = lado * ang
        return (junta[0] + px * math.cos(a) - py * math.sin(a), junta[1] + px * math.sin(a) + py * math.cos(a))

    forma = [(0, 0), (0.08, 78), (0.45, 70), (0.82, 34), (0.97, 12), (1.0, 0)]
    abertura = 0.1 + 0.55 * abre
    # o céu da boca (vermelho escuro) entre as mandíbulas
    boca = [P(f * comp, 4, 1, abertura) for f in (0.1, 0.5, 0.95)] + [P(f * comp, 4, -1, abertura) for f in (0.95, 0.5, 0.1)]
    pygame.draw.polygon(tela, (90, 16, 26), boca)
    cores = ((-1, (214, 212, 204), (70, 70, 66)), (1, (74, 78, 88), (14, 16, 20))) if mega else         ((-1, (206, 206, 140), (70, 70, 40)), (1, (96, 118, 142), (14, 18, 26)))
    for lado, cor, cor_borda in cores:
        pts = [P(a * comp, b, lado, abertura) for a, b in forma]
        pygame.draw.polygon(tela, cor_borda, pts)
        pygame.draw.polygon(tela, cor, [(px + (pts[2][0] - px) * 0.06, py + (pts[2][1] - py) * 0.06) for px, py in pts])
        for fila, tam in ((0, 1.0), (1, 0.6)):  # DUAS fileiras de dentes
            for i in range(12):
                a = (0.12 + i * 0.07 + fila * 0.035) * comp
                if a > comp * 0.95:
                    continue
                base1 = P(a, 4 + fila * 10, lado, abertura)
                base2 = P(a + 12, 4 + fila * 10, lado, abertura)
                ponta = P(a + 6, -16 * tam + fila * 10, lado, abertura)
                pygame.draw.polygon(tela, (245, 244, 230) if fila == 0 else (210, 208, 190), [base1, ponta, base2])
        if lado == 1:  # escamas, a listra clara e o OLHO
            for i in range(6):
                c = P((0.2 + i * 0.11) * comp, 50 - i * 5, 1, abertura)
                pygame.draw.arc(tela, (34, 46, 62), (c[0] - 12, c[1] - 6, 24, 12), 0, 3.14, 2)
            pygame.draw.lines(tela, (96, 116, 140), False, [P(f * comp, 64 - f * 50, 1, abertura) for f in (0.1, 0.4, 0.7, 0.9)], 4)
            olho = P(0.22 * comp, 46, 1, abertura)
            if mega:  # olho preto de tubarão
                pygame.draw.circle(tela, (8, 8, 10), (int(olho[0]), int(olho[1])), 9)
                pygame.draw.circle(tela, (120, 120, 126), (int(olho[0] - 3), int(olho[1] - 3)), 2)
                continue
            brilho(tela, (int(olho[0]), int(olho[1])), 30, (255, 210, 40), 160)
            pygame.draw.circle(tela, (14, 18, 26), (int(olho[0]), int(olho[1])), 13)
            pygame.draw.circle(tela, (255, 214, 40), (int(olho[0]), int(olho[1])), 10)
            pygame.draw.ellipse(tela, (14, 10, 6), (olho[0] - 2, olho[1] - 9, 4, 18))
    # a água espirrando em volta
    rnd = random.Random(int(sobe * 10))
    for i in range(26):
        k = (t * 0.06 + i / 26) % 1.0
        dx = rnd.uniform(-1, 1) * 140
        h = (1 - (k - 0.5) ** 2 * 4) * 180 * sobe
        pygame.draw.circle(tela, (225, 245, 255), (int(x + dx * (0.5 + k)), int(CHAO - h)), max(2, int(6 * (1 - k))))


def ancestral_efeito(l, tela):
    import sphyrus
    m = l.memo
    if m.get("mar", 0) > 0:
        sphyrus.mar_efeito(l, tela)
    t = l.t
    if "pegou" not in m:
        return
    x = m["x"]
    if S_MAR < t < A_SOBE:  # a sombra gigante embaixo d'água, rodando
        k = (t - S_MAR) / (A_SOBE - S_MAR)
        sx = x + math.cos(k * math.tau) * 160
        sombra = pygame.Surface((300, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 10, 30, 120), (0, 0, 300, 60))
        tela.blit(sombra, (sx - 150, CHAO - 10))
    if A_SOBE <= t < A_VOLTA:
        if t < A_ABERTO:
            sobe, abre = suave((t - A_SOBE) / (A_ABERTO - A_SOBE)), 1.0
        elif t < A_MORDE - 4:
            sobe, abre = 1.0, 1.0
        elif t < A_MORDE:
            sobe, abre = 1.0, 1 - (t - A_MORDE + 4) / 4
        else:
            sobe, abre = 1 - suave((t - A_MORDE) / (A_VOLTA - A_MORDE)), 0.0
        mosassauro(tela, x, sobe, abre, -l.dir, t, l.f.get("estilo") == "megalodonte")
        if t == A_MORDE or t == A_MORDE + 1:
            from efeitos import texto_grande
            texto_grande(tela, "CHOMP!", 60, (255, 240, 200), (int(x), CHAO - 360), 1.2, contorno=(40, 10, 10))
CD_SAI, CD_TUBAROES, CD_CADA, CD_MARTELO = 20, 12, 3, 96


class Tubarao(Projetil):
    """Um tubarão-martelo do cardume: nada ondulando, deixando bolhas."""

    def __init__(self, dono, x, y, golpe, k):
        super().__init__(dono, x, y, dono.dir, golpe)
        self.y0 = y
        self.k = k
        self.bolhas = []

    def update(self):
        self.t += 1
        self.x += self.vx
        self.y = self.y0 + math.sin(self.t * 0.18 + self.k) * 22
        if self.t % 3 == 0:
            self.bolhas = (self.bolhas + [(self.x - self.vx * 3, self.y, self.t)])[-8:]
        if self.x < -120 or self.x > LARGURA + 120:
            self.vivo = False


def desenha_tubarao(p, tela):
    d = 1 if p.vx > 0 else -1
    x, y = p.x, p.y
    g = 2.5
    for bx, by, bt in getattr(p, "bolhas", []):  # as bolhas
        r = 2 + (p.t - bt) * 0.3
        pygame.draw.circle(tela, (210, 240, 255), (int(bx), int(by - (p.t - bt) * 1.2)), int(r), 1)
    sob = math.sin(p.t * 0.5) * 3  # o rabo batendo
    corpo = [(x + d * 20 * g, y), (x + d * 8 * g, y - 7 * g), (x - d * 12 * g, y - 5 * g),
             (x - d * 22 * g, y - 13 * g + sob), (x - d * 18 * g, y + sob * 0.3), (x - d * 22 * g, y + 9 * g + sob),
             (x - d * 12 * g, y + 4 * g), (x + d * 8 * g, y + 6 * g)]
    pygame.draw.polygon(tela, (16, 20, 28), corpo)
    pygame.draw.polygon(tela, (104, 118, 138), [(px + (x - px) * 0.08, py + (y - py) * 0.08) for px, py in corpo])
    pygame.draw.polygon(tela, (200, 204, 150), [(x + d * 16 * g, y + 2 * g), (x - d * 10 * g, y + 3 * g),
                                                 (x + d * 6 * g, y + 5 * g)])  # a barriga
    pygame.draw.polygon(tela, (70, 80, 98), [(x - d * 2 * g, y - 6 * g), (x - d * 8 * g, y - 15 * g),
                                              (x - d * 10 * g, y - 5 * g)])  # a barbatana
    pygame.draw.line(tela, (16, 20, 28), (x + d * 17 * g, y - 9 * g), (x + d * 17 * g, y + 8 * g), int(4 * g))  # o martelo
    pygame.draw.line(tela, (80, 94, 112), (x + d * 17 * g, y - 8 * g), (x + d * 17 * g, y + 7 * g), int(2.4 * g))
    pygame.draw.line(tela, (80, 200, 255), (x - d * 12 * g, y), (x + d * 6 * g, y), 2)
    for oy in (-8, 7):  # os olhos amarelos nas pontas do martelo
        pygame.draw.circle(tela, (255, 214, 40), (int(x + d * 17 * g), int(y + oy * g)), 3)


def cardume(l, o, jogo):
    """CARDUME: um cardume de tubarões-martelo atravessa a tela mordendo e ele fecha com a MARTELADA."""
    t = l.t
    m = l.memo
    l.fisica(jogo)
    if t < CD_SAI:
        camera(jogo, 1.3, l.x, l.y - 80 * l.s)
        return
    camera(jogo, 1.05, (l.x + o.x) / 2, CHAO - 120)
    k = (t - CD_SAI) // CD_CADA
    if (t - CD_SAI) % CD_CADA == 0 and k < CD_TUBAROES:
        x = (PAREDE_E - 100 - (k % 3) * 40) if l.dir > 0 else (PAREDE_D + 100 + (k % 3) * 40)
        y = CHAO - 50 - (k % 3) * 38
        jogo.projeteis.append(Tubarao(l, x, y, GOLPES["sphyrus_tubarao"], k))
        if k % 3 == 0:
            som.tocar("vento", 0.4)
    if t == CD_MARTELO - 10 and o.estado in ("golpeado", "tonto") and o.inv <= 0:
        m["salta"] = t
        som.tocar("terra", 0.6)
    if "salta" in m and t < CD_MARTELO:  # corre até ele
        l.x += ((o.x - l.dir * 46 * l.s) - l.x) * 0.35
    if t == CD_MARTELO and "salta" in m:  # A MARTELADA
        acerta(l, o, jogo, "sphyrus_martelada_final")
        impacto(jogo, 12, 22, 4)
        fumaca(jogo, l.x, CHAO - 4, 10, (210, 236, 255), 4, -2)
    if t > CD_MARTELO:
        camera(jogo, 1.2, o.x, o.y - 80 * o.s)
    if t >= CD_MARTELO + 30:
        return "fim"


T_PUXA, T_CORTES = 14, 20


def tornado(l, o, jogo):
    """TORNADO DE LÂMINAS: gira com as asinhas abertas, vira um tornado, puxa e corta umas 20 vezes."""
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    l.vira = (t // 3) % 2 == 1 if t >= 6 else False  # rodopiando
    if t < T_PUXA:
        camera(jogo, 1.35, l.x, l.y - 80 * l.s)
        return
    camera(jogo, 1.1, l.x, CHAO - 150)
    if t % 6 == 0:
        som.tocar("vento", 0.5)
    if "pegou" not in m:
        if t > T_PUXA + 70:
            l.vira = False
            return "fim"
        dx = l.x - o.x
        if abs(dx) < 280 and o.no_chao() and o.inv <= 0 and o.estado not in ("caido", "voando", "agarrado"):
            o.x += (1 if dx > 0 else -1) * 5  # puxa pro tornado
            if abs(dx) < CORPO * (l.s + o.s) + 12:
                m["pegou"] = t
                pega(o)
                som.tocar("lingua", 0.5)
        return
    u = t - m["pegou"]
    o.x = l.x + math.sin(u * 0.5) * 30
    o.y = CHAO - min(1, u / 20) * 110 - math.sin(u * 0.2) * 10
    o.angulo = u * 0.35
    if u % 4 == 2 and u // 4 < T_CORTES:
        bate(l, o, jogo, 3, "sphyrus_tornado", ultimo=u // 4 == T_CORTES - 1)
        m.setdefault("cortes", []).append(t)
    if u >= T_CORTES * 4 + 4:
        o.angulo = 0
        solta(o, l.dir * 8, -13)
        impacto(jogo, 8, 18, 3)
        l.vira = False
        return "fim"


def tornado_efeito(l, tela):
    t = l.t
    if t < 6:
        return
    k = min(1, (t - 6) / 14)
    cx = l.x
    camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    for i in range(14):  # o funil: anéis cada vez mais largos subindo, girando
        y = CHAO - 10 - i * 22 * k
        r = (30 + i * 11) * k
        a0 = t * 0.45 + i * 0.6
        caixa = pygame.Rect(0, 0, r * 2, r * 0.42)
        caixa.center = (int(cx + math.sin(t * 0.1 + i * 0.4) * i * 1.5), int(y))
        pygame.draw.ellipse(camada, (210, 225, 240, 40), caixa)
        pygame.draw.arc(camada, (240, 248, 255, 190), caixa, a0, a0 + 2.4, 3)
        pygame.draw.arc(camada, (170, 200, 230, 150), caixa, a0 + 3.1, a0 + 4.6, 2)
    tela.blit(camada, (0, 0))
    for i in range(10):  # as lâminas (vermelhas da Frenesi) girando no vento
        a = t * 0.5 + i * 0.63
        r = 50 + (i % 4) * 26
        y = CHAO - 40 - (i * 29) % 220 * k
        x = cx + math.cos(a) * r
        pygame.draw.arc(tela, (255, 60, 60) if i % 2 else (255, 255, 255),
                        (x - 18, y - 8, 36, 16), a, a + 1.6, 3)
    for i in range(8):  # poeira e folhas sendo puxadas
        a = t * 0.3 + i * 0.8
        d = 260 - ((t * 6 + i * 40) % 240)
        pygame.draw.circle(tela, (180, 160, 120), (int(cx + math.cos(a) * d), int(CHAO - 6 - (260 - d) * 0.4)), 3)
    for tc in l.memo.get("cortes", []):  # os cortes nele
        u = t - tc
        alvo = getattr(l, "_alvo_ancestral", None)
        if 0 <= u < 4 and alvo is not None:
            a = tc * 2.1
            ax, ay = alvo.x, alvo.y - 50 * alvo.s
            pygame.draw.line(tela, (255, 255, 255), (ax - math.cos(a) * 46, ay - math.sin(a) * 46),
                             (ax + math.cos(a) * 46, ay + math.sin(a) * 46), 4 - u)


def sphyrus_ult2_efeito(l, tela):
    tipo = l.memo.get("tipo")
    if tipo == "natacao":
        ancestral_efeito(l, tela)
    elif tipo == "frenesi":
        tornado_efeito(l, tela)


_dano("sphyrus_ancestral", 50, hit=40, emp=2)
_dano("sphyrus_tubarao", 32 / CD_TUBAROES, hit=26, defe=6, emp=1, proj=True, raio=30, vel=13, varios=True,
      desenho_proj=desenha_tubarao, sem_parada=True)
_dano("sphyrus_martelada_final", 28, hit=36, emp=4, lanca=19)
_dano("sphyrus_tornado", 3, hit=30, emp=1)
_registra("sphyrus_ult2", sphyrus_ult2, sphyrus_ult2_efeito, [(0, "parado"), (4, "s_ruge"), (S_MAR, "s_ruge"),
                                                             (S_MAR + 8, "parado")])


# =====================================================================
# Quem tem qual (os golpes "Z2" de cada ficha)
# =====================================================================
ULT2 = {"MAX-10": "max_ult2", "RIB": "rib_ult2", "TRAFO": "trafo_ult2", "KING RIP": "king_ult2",
        "CANNAN": "cannan_ult2", "FINN": "finn_ult2", "KUN": "kun_ult2", "TROMOS": "xeno_ult2", "TAI": "tai_ult2",
        "TAMER": "tamer_ult2", "JOHN": "john_ult2", "CRÁQUEN": "craquen_ult2", "MAGNUS": "magnus_ult2",
        "SPHYRUS": "sphyrus_ult2", "FRIGANTUS": "frigantus_ult2", "INAZUMANEKO": "inaz_ult2",
        "NOCTURNUS": "noct_ult2", "SILVANUS": "silv_ult2", "KATCHADE": "katch_ult2"}
NOMES = {"MAX-10": "CHUVA DE MÍSSEIS", "RIB": "SHURIKEN GIGANTE", "TRAFO": "BRAÇOS DE TERRA",
         "KING RIP": "ESPÍRITO DO DOJO", "CANNAN": "A MINIGUN", "FINN": "GOLEM DE PEDRA", "KUN": "TSUNAMI DE CARTAS",
         "TROMOS": "CAÇADA NO ESCURO", "TAI": "TERREMOTO", "TAMER": "LUA CHEIA", "JOHN": "A RAVINA",
         "CRÁQUEN": "KRAKEN / TRIPULAÇÃO FANTASMA", "MAGNUS": "MODO FORNALHA", "SPHYRUS": "ANCESTRAL / CARDUME / TORNADO",
         "FRIGANTUS": "ERA DO GELO", "INAZUMANEKO": "MIL CORTES",
         "NOCTURNUS": "CANÇÃO DE NINAR", "SILVANUS": "CHUVA DE SEMENTES", "KATCHADE": "CORTE VERTICAL"}


def ligar(fichas):
    for f in fichas:
        nome = ULT2.get(f["nome"])
        if nome and "golpes" in f and "Z2" not in f["golpes"]:
            f["golpes"] = dict(f["golpes"], Z2=nome)
            f.setdefault("nomes", {})
            f["nomes"] = dict(f["nomes"], Z2=NOMES[f["nome"]])


# =====================================================================
# O que fica rodando depois que a ultimate acabou (golem, lobisomem, marujos, caçada, fornalha)
# =====================================================================
def todo_quadro(l, jogo):
    x = l.extra
    if x.get("prov_vis") and not (l.estado == "ataque" and l.nome_golpe == "provocar"):
        l.sobrepor = {}  # (apanhou no meio da provocação da loja: desfaz a pose / o sumiço)
        l.esconde = False
        x.pop("prov_vis", None)
        x.pop("lobo_some", None)
    o = outro_de(l, jogo)
    l._alvo_ancestral = l._alvo_marujos = l._ravina_alvo = l._alvo_kraken = o  # (pros desenhos)
    for k in ("golem", "lobisomem", "cacada", "fornalha", "neve_t"):
        if x.get(k, 0) > 0:
            x[k] -= 1
    if x.get("neve") and x.get("neve_t", 0) <= 0:
        x["neve"] = 0
    acao = x.get("golem_acao")
    if acao:
        x["golem_acao"] = (acao[0], acao[1] + 1)
    if x.get("golem", 0) > 0 and l.estado == "ataque" and l.t == 1 and l.golpe and l.golpe.get("especial") \
            and not l.golpe.get("ultimate"):
        golem_ajuda(l, o, jogo)
    lobisomem_passo(l, o, jogo)
    marujos_passo(l, o, jogo)
    fornalha_passo(l, jogo)


def vivo(l):
    """Tem alguma coisa da 2ª ultimate aparecendo (pra a tela desenhar)?"""
    x = l.extra
    return any(x.get(k, 0) > 0 for k in ("golem", "lobisomem", "fornalha", "cacada")) or bool(x.get("marujos"))


def desenhar_vivo(l, tela):
    desenha_vivo_finn(l, tela)
    desenha_marujos(l, tela)
    x = l.extra
    if x.get("lobi_ataque", -1) in range(9, 15):  # os riscos da garrada do lobisomem
        alvo = getattr(l, "_alvo_marujos", None)
        if alvo is not None:
            for k in range(3):
                ax = alvo.x - 20 + k * 10
                pygame.draw.line(tela, (255, 255, 255), (ax, alvo.y - 110 * alvo.s), (ax + 18, alvo.y - 50 * alvo.s), 3)
    if x.get("fornalha", 0) > 0:  # em chamas
        brilho(tela, (int(l.x), int(l.y - 50 * l.s)), int(80 * l.s), (255, 120, 30), 110)
