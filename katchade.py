"""KATCHADE: o LOUVA-A-DEUS-ORQUÍDEA guerreiro ("Catch" + "Blade": pega a presa com a lâmina) — 19º lutador,
criado pelo Gomes pra v4.0. Tema: PACIÊNCIA e CONTRA-ATAQUE (o lutador que pune quem fica spammando).

Aparência: louva-a-deus-orquídea de pé — BRANCO e ROSA como uma flor, cabeça triangular com olhos grandes
verde-claros, antenas, PÉTALAS rosas nas pernas (o louva-a-deus-orquídea de verdade tem), abdômen de pétala
pra trás, asas dobradas nas costas. Os braços são FOICES (com serrinha) dobradas na frente do peito, em pose de reza.
  E      CORTE CRUZADO: as duas foices em X, rápido, de perto
  Q      BOTE: salta e AGARRA com as foices, joga pra cima
  R      POSTURA DE ORAÇÃO: fica rezando; se te baterem de perto, desvia e corta de volta
  SHIFT  ASAS: voo curto pra frente (ou pra trás segurando TRÁS)
  Z      ULTIMATE: DANÇA DAS FOICES — some camuflado na flor e corta de vários lados
  Passivas (H): CAMUFLAGEM / FOICES AFIADAS
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from corpo import cabeca_eixos, eixos, frente_do_pe, mais
from golpes import GOLPES, misturar, proporcionar, suave  # noqa: F401
from pecas import Peca

POSES_KATCHADE = {
    # de pé, meio curvado pra frente, as FOICES dobradas na frente do peito (reza)
    "parado": dict(pt=(-18, 0), jt=(-12, 30), pf=(18, 0), jf=(22, 30), qd=(0, 56), pc=(8, 90), cb=(14, 108),
                   ct=(20, 74), mt=(32, 92), cf=(24, 72), mf=(36, 90)),
    "andar1": dict(pt=(-24, 2), jt=(-14, 30), pf=(22, 0), jf=(24, 30), qd=(0, 54), pc=(8, 88), cb=(16, 104),
                   ct=(20, 72), mt=(32, 90), cf=(24, 70), mf=(36, 88)),
    "andar2": dict(pt=(-6, 8), jt=(0, 32), pf=(8, 0), jf=(14, 30), qd=(0, 58), pc=(8, 92), cb=(16, 108),
                   ct=(20, 76), mt=(32, 94), cf=(24, 74), mf=(36, 92)),
    "andar3": dict(pt=(22, 0), jt=(24, 30), pf=(-24, 2), jf=(-14, 30), qd=(0, 54), pc=(8, 88), cb=(16, 104),
                   ct=(20, 72), mt=(32, 90), cf=(24, 70), mf=(36, 88)),
    "andar4": dict(pt=(8, 0), jt=(14, 30), pf=(-6, 8), jf=(0, 32), qd=(0, 58), pc=(8, 92), cb=(16, 108),
                   ct=(20, 76), mt=(32, 94), cf=(24, 74), mf=(36, 92)),
    # E: CORTE CRUZADO (as duas foices abertas pra cima... e cruzam pra baixo em X)
    "k_abre": dict(pt=(-20, 0), jt=(-14, 28), pf=(20, 0), jf=(24, 28), qd=(0, 54), pc=(6, 90), cb=(12, 108),
                   ct=(18, 100), mt=(30, 122), cf=(24, 98), mf=(40, 118)),
    "k_cruza": dict(pt=(-24, 0), jt=(-16, 28), pf=(24, 0), jf=(30, 28), qd=(2, 52), pc=(14, 86), cb=(22, 100),
                    ct=(32, 84), mt=(62, 62), cf=(34, 78), mf=(64, 92)),
    # R: POSTURA DE ORAÇÃO (bem reto, foices juntinhas em cima, imóvel)
    "k_reza": dict(pt=(-14, 0), jt=(-10, 30), pf=(14, 0), jf=(16, 30), qd=(0, 58), pc=(4, 94), cb=(8, 112),
                   ct=(14, 84), mt=(18, 112), cf=(16, 84), mf=(20, 112)),
    # Q: BOTE (agacha... e salta com as foices abertas pra frente)
    "k_agacha": dict(pt=(-22, 0), jt=(-8, 20), pf=(22, 0), jf=(32, 22), qd=(0, 34), pc=(14, 64), cb=(24, 78),
                     ct=(26, 56), mt=(36, 72), cf=(30, 54), mf=(40, 70)),
    "k_salto": dict(pt=(-24, 10), jt=(-10, 26), pf=(4, 6), jf=(14, 26), qd=(0, 48), pc=(16, 80), cb=(28, 94),
                    ct=(34, 84), mt=(60, 96), cf=(36, 80), mf=(62, 88)),
    "k_segura": dict(pt=(-20, 0), jt=(-12, 28), pf=(20, 0), jf=(24, 28), qd=(0, 54), pc=(10, 88), cb=(18, 104),
                     ct=(30, 82), mt=(46, 76), cf=(32, 78), mf=(48, 70)),
    "k_lanca": dict(pt=(-20, 0), jt=(-14, 28), pf=(20, 0), jf=(24, 28), qd=(0, 56), pc=(6, 92), cb=(10, 110),
                    ct=(22, 106), mt=(34, 132), cf=(26, 104), mf=(40, 128)),
    # SHIFT: ASAS (corpo deitado pra frente, pernas pra trás)
    "k_asas": dict(pt=(-30, 14), jt=(-14, 24), pf=(-20, 6), jf=(-4, 22), qd=(0, 40), pc=(22, 64), cb=(36, 76),
                   ct=(32, 56), mt=(46, 70), cf=(34, 54), mf=(48, 66)),
    # provocação: limpa a foice (passa uma na outra)
    "k_limpa": dict(pt=(-18, 0), jt=(-12, 30), pf=(18, 0), jf=(22, 30), qd=(0, 56), pc=(8, 90), cb=(16, 106),
                    ct=(18, 80), mt=(34, 84), cf=(22, 92), mf=(30, 110)),
}
proporcionar(POSES_KATCHADE)

PALETA = {
    "k": (74, 30, 66), "w": (255, 242, 248), "W": (242, 200, 222), "p": (250, 160, 202), "P": (222, 102, 160),
    "m": (184, 52, 126), "e": (255, 206, 232), "E": (206, 120, 178), "o": (64, 26, 60), "n": (255, 255, 255),
    "l": (248, 238, 255), "L": (196, 166, 228), "s": (150, 74, 140), "a": (255, 222, 240), "A": (240, 176, 214),
}
# as patas de TRÁS: em vez de escurecer pro cinza, ficam num rosa mais fundo
PALETA_TRAS = {k: (tuple(int(c * 0.72 + r * 0.28) for c, r in zip(v, (196, 92, 150))) if k != "k" else v)
               for k, v in PALETA.items()}
S_REF = 1.3 / 3


def _m(linhas, w):
    return [linha.ljust(w, ".")[:w] for linha in linhas]


def _peca(linhas, w, a, b, estica=True):
    """A peça normal e a gêmea rosa-escura (pra quando ela fica atrás)."""
    mapa = _m(linhas, w)
    return Peca(mapa, PALETA, a=a, b=b, estica=estica), Peca(mapa, PALETA_TRAS, a=a, b=b, estica=estica)


#   k contorno roxo  w W branco-rosado  p P rosa de pétala  m magenta  e E olho rosa-pérola (cone)  o pupila  n brilho
#   l L lâmina lilás  s espinhos  a A asa
CABECA, _ = _peca([
    "..........k.......",
    ".........kek......",
    "........keeEk.....",
    ".......kenneEk....",
    "......keneeeEk....",
    ".....keeeooeEEk...",
    "....kkeeeooeEEk...",
    "...kwwkeeeeEEk....",
    "..kwwwwkEEEEkwk...",
    ".kWwwwwwkkkkwwwk..",
    "kWwwwwwwwwwwwwwk..",
    ".kWwwwwwwwwwwppk..",
    "..kWwwwwwwwwpPk...",
    "...kkWwwwwwpmk....",
    ".....kkWwpPmk.....",
    ".......kkkkk......",
], 18, a=(5, 12), b=(5, 2), estica=False)

TRONCO, _ = _peca([
    "..kkkk..",
    ".kpwwPk.",
    "kpPwwPpk",
    ".kwwwWk.",
    "..kwWk..",
    "..kpWk..",
    "..kwWk..",
    "..kwPk..",
    "..kwWk..",
    ".kwwwWk.",
    ".kpppPk.",
    "kwwwwwWk",
    "kpppppPk",
    "kwwwwwWk",
    ".kkkkkk.",
], 8, a=(3, 13), b=(3, 1))

ABDOMEN, _ = _peca([
    "...kkkkkkk........",
    "..kwppwppwkkkk....",
    ".kwPpwPpwPpwwwkk..",
    "kwwpwwpwwpwwppwwk.",
    "kwwPwwPwwPwwPPwwwk",
    "kWWPWWPWWPWWWWWWk.",
    ".kWWWWWWWWWWWkkk..",
    "..kkkkkkkkkkk.....",
], 18, a=(1, 4), b=(17, 4))

ASA, _ = _peca([
    "..kkkkkkk.........",
    ".kaaAaaaakkkkk....",
    "kaAaaaAaaaAaaakk..",
    "kaaaAaaaAaaaAaaak.",
    ".kaaaaaaaaaAaaak..",
    "..kkkkkkkkkkkkk...",
], 18, a=(1, 3), b=(16, 3))

BRACO, BRACO_T = _peca([
    ".kkk.",
    "kwwWk",
    "kwpWk",
    "kwwWk",
    "kwpWk",
    "kwwWk",
    ".kkk.",
], 5, a=(2, 0), b=(2, 6))

ANTEBRACO, ANTEBRACO_T = _peca([
    ".kkkk..",
    "kwwwWk.",
    "kwpwWsk",
    "kwwwWk.",
    "kwpwWsk",
    "kwwwWk.",
    "kwpwWsk",
    "kwwwWk.",
    ".kkkk..",
], 7, a=(2, 0), b=(2, 8))

FOICE, FOICE_T = _peca([
    "..kkk...............",
    ".kwwwkkkkkk.........",
    "kwwwwlllllLkkkk.....",
    "kwwwwllllllllLLkk...",
    ".kwwklllllllllLLLk..",
    "..kkksksksksksskLLk.",
    "......k.k.k.k.kk.kLk",
    "..................kk",
], 20, a=(2, 3), b=(17, 3), estica=False)

COXA, COXA_T = _peca([
    "..kkkk......",
    ".kwwwWk.....",
    ".kwwwWkkkk..",
    ".kwwwWpppPk.",
    ".kwwwWppppPk",
    ".kwwwWpwwpPk",
    ".kwwwWppppPk",
    ".kwwwWpppPk.",
    ".kwwwWkkPk..",
    "..kwWk..kk..",
    "..kkkk......",
], 12, a=(3, 0), b=(3, 10))

CANELA, CANELA_T = _peca([
    ".kkk....",
    "kwwWk...",
    "kwwWkkk.",
    "kwwWpPPk",
    "kwwWpPk.",
    "kwwWkk..",
    ".kwWk...",
    ".kwWk...",
    ".kpPk...",
    ".kkk....",
], 8, a=(2, 0), b=(2, 9))

PE, PE_T = _peca([
    ".kkk....",
    "kwwWkkk.",
    "kwwppPmk",
    ".kkkkkk.",
], 8, a=(1, 1), b=(6, 1), estica=False)


def desenhar_katchade(l, tela, p, branco):
    esc = l.s / S_REF
    d = l.lado()
    espelho = d < 0
    var = "branco" if branco else "normal"

    def P(k):
        return l.ponto(p, k)

    def perna(pe, joelho, tras):
        q, j, e = P("qd"), P(joelho), P(pe)
        (CANELA_T if tras else CANELA).desenhar(tela, j, e, esc, espelho, var)
        fr, _ = frente_do_pe(j, e, d)
        (PE_T if tras else PE).desenhar(tela, e, mais(e, fr, 7), esc, espelho, var)
        (COXA_T if tras else COXA).desenhar(tela, q, j, esc, espelho, var)

    aberta = (l.estado == "ataque" and l.nome_golpe not in ("katch_reza", "katch_asas", "provocar")) \
        or l.estado == "vitoria"  # atacando: a foice ABRE pra frente

    def braco(cot, mao, tras):
        o, c, m = P("pc"), P(cot), P(mao)
        dm, _ = eixos(c, m)
        (ANTEBRACO_T if tras else ANTEBRACO).desenhar(tela, c, m, esc, espelho, var)
        (BRACO_T if tras else BRACO).desenhar(tela, o, c, esc, espelho, var)
        foice = FOICE_T if tras else FOICE
        if aberta:
            foice.desenhar(tela, m, mais(m, dm, 10 * l.s), esc, espelho, var)
        else:  # dobrada pra baixo, encostada no braço (o jeito do louva-a-deus de verdade)
            foice.desenhar(tela, m, mais(c, (0, 1), 4 * l.s), esc, not espelho, var)

    q, c, cb = P("qd"), P("pc"), P("cb")
    tronco_dir, _ = eixos(q, c)
    tras = (-d, 0)
    if ((l.estado == "ataque" and l.nome_golpe == "katch_asas") or l.extra.get("entrando_asas")) and not branco:
        bate = math.sin(l.t * 1.3)
        for k in (0, 1):
            ang = -math.pi / 2 - d * (0.5 + 0.35 * bate + k * 0.3)
            ponta_asa = (c[0] + math.cos(ang) * 44 * l.s, c[1] + math.sin(ang) * 44 * l.s)
            ASA.desenhar(tela, c, ponta_asa, esc, espelho, "normal")
    braco("ct", "mt", True)
    perna("pt", "jt", True)
    # o ABDÔMEN de pétala sai do quadril pra trás e um pouco pra cima; as ASAS dobradas por cima dele
    ponta = mais(mais(q, tras, 30 * l.s), tronco_dir, 12 * l.s)
    ABDOMEN.desenhar(tela, mais(q, tronco_dir, 2 * l.s), ponta, esc, not espelho, var)
    ASA.desenhar(tela, mais(mais(q, tronco_dir, 14 * l.s), tras, 2 * l.s), mais(ponta, tronco_dir, 3 * l.s), esc,
                 not espelho, var)
    perna("pf", "jf", False)
    TRONCO.desenhar(tela, q, c, esc, espelho, var)
    u, _ = cabeca_eixos(c, cb, d)
    pescoco = mais(cb, u, -3 * l.s)  # o PESCOÇO comprido (protórax) do louva-a-deus
    pygame.draw.line(tela, (150, 150, 160) if branco else PALETA["k"], c, pescoco, max(3, int(7 * l.s)))
    pygame.draw.line(tela, (245, 245, 250) if branco else PALETA["w"], c, pescoco, max(1, int(4 * l.s)))
    na_cabeca = CABECA.desenhar(tela, cb, mais(cb, u, 10), esc, espelho, var)
    if l.f.get("estilo") == "samurai":  # roupa ESPADACHIM ERRANTE
        roupa_samurai(l, tela, p, na_cabeca, branco)
    # ANTENAS finas saindo da testa, balançando um pouquinho
    if na_cabeca:
        base = na_cabeca(12, 9)
        for k, (ang, comp) in enumerate(((-2.0, 26), (-2.3, 22))):
            a = ang + math.sin(l.t * 0.08 + k) * 0.08
            dx = math.cos(a) * comp * l.s * (1 if d > 0 else -1)
            dy = math.sin(a) * comp * l.s
            meio = (base[0] + dx * 0.5, base[1] + dy * 0.55 - 3 * l.s)
            ponta_a = (base[0] + dx, base[1] + dy)
            cor = (150, 150, 160) if branco else PALETA["k"]
            pygame.draw.lines(tela, cor, False, [base, meio, ponta_a], max(1, int(1.6 * l.s)))
    braco("cf", "mf", False)


# =====================================================================
# os GOLPES
# =====================================================================
def outro_de(l, jogo):
    return jogo.L[1] if jogo.L[0] is l else jogo.L[0]


def _registra(nome, **g):
    g.setdefault("base", "parado")
    g.setdefault("pose", "parado")
    g.setdefault("caixa", None)
    g.setdefault("especial", True)
    g["total"] = g.get("total", g["ini"] + g["ativo"] + g.get("rec", 0))
    GOLPES[nome] = g


def acerto(jogo, l, outro, nome):
    import inazumaneko  # (o mesmo acerto "de lógica" do Inazumaneko: conta combo, treino, parry, faísca...)
    return inazumaneko.acerto(jogo, l, outro, nome)


def pode_pegar(outro):
    return outro.inv <= 0 and outro.estado not in ("caido", "voando", "agarrado", "levantando") and outro.vida > 0


# ---- E: CORTE CRUZADO (as duas foices em X: 2 cortes rápidos) ----
_registra("katch_corte", ini=7, ativo=8, rec=13, janelas=((7, 10), (11, 14)), caixa=(10, 44, 98, 126),
          dano=6, hit=16, defe=10, emp=3, nivel="medio", ia="perto", som="shuriken",
          quadros=[(0, "parado"), (5, "k_abre"), (8, "k_cruza"), (15, "k_cruza"), (28, "parado")])

# ---- Q: BOTE (salta e AGARRA com as foices; corta e joga pra cima). Agarrão: não dá pra defender, só pular/fugir ----
B_PULA = 8
B_SEGURA = 14   # quadros segurando antes de jogar pra cima


def bote(l, outro, jogo):
    t = l.t
    m = l.memo
    if "pegou" in m:
        u = t - m["pegou"]
        l.vx = 0
        outro.x = max(PAREDE_E, min(PAREDE_D, l.x + l.dir * 52 * l.s))
        outro.y = l.y
        if u == 5:  # corta segurando
            outro.levar(4 * l.f["forca"], l, GOLPES["katch_bote_corte"])
            outro.vida = max(1, outro.vida)
            outro.tremor_hit = 6
            jogo.faisca(outro.x, outro.y - 70 * outro.s, False, False)
            som.tocar("soco", 0.6)
        l.sobrepor = dict(POSES_KATCHADE["k_segura"] if u < B_SEGURA - 3 else POSES_KATCHADE["k_lanca"])
        if u == B_SEGURA:  # e JOGA PRA CIMA (dá pra continuar no ar: segura CIMA)
            outro.sobrepor = {}
            outro.mudar("golpeado")  # (continua no combo: não "solta" parado)
            outro.stun = 6
            acerto(jogo, l, outro, "katch_bote_lanca")
            som.tocar("shuriken")
        l.fisica(jogo)
        if u >= B_SEGURA + 16:
            l.sobrepor = {}
            return "fim"
        return
    if t == B_PULA:
        l.vy = -9.5
        l.vx = 9.5 * l.dir
        som.tocar("pulo")
    if t > B_PULA and "errou" not in m:
        perto = abs(outro.x - l.x) < 66 * l.s and abs(outro.y - l.y) < 100 * l.s
        if perto and pode_pegar(outro) and not outro.extra.get("intangivel"):
            import habilidades as hab
            if hab.substituicao(outro, GOLPES["katch_bote_corte"], l):  # (o Rib substitui, o Inaz contra-ataca...)
                m["errou"] = t
            else:
                m["pegou"] = t
                import ult2
                ult2.pega(outro, "golpeado")
                l.acertou = True
                som.tocar("parry", 0.6)
                l.vy = max(l.vy, 0)
        elif l.no_chao() and t > B_PULA + 3:
            m["errou"] = t  # caiu no chão sem pegar: fica ABERTO
    l.fisica(jogo)
    if "errou" in m:
        l.vx *= 0.6
        if t - m["errou"] >= 20 and l.no_chao():
            return "fim"
    if t > 120:
        return "fim"


_registra("katch_bote", ini=B_PULA, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", logica=bote, lanca_depois=True,
          ia="medio", quadros=[(0, "parado"), (B_PULA - 2, "k_agacha"), (B_PULA + 3, "k_salto"), (60, "k_salto")])
GOLPES["katch_bote"]["total"] = 9999
GOLPES["katch_bote_corte"] = dict(dano=4, hit=10, defe=6, emp=1, nivel="medio", especial=True)
GOLPES["katch_bote_lanca"] = dict(dano=8, hit=24, defe=10, emp=2, nivel="medio", especial=True, lanca=17)

# ---- R: POSTURA DE ORAÇÃO (fica rezando; golpe de perto que vier = desvia e corta de volta) ----
R_INI, R_JANELA, R_ABERTO = 4, 36, 22
R_REVIDA = 5


def reza_pega(l, g, atacante):
    """Chamado quando um golpe ia pegar nele (habilidades.substituicao): True = pegou na oração (o golpe não acerta)."""
    if l.estado != "ataque" or l.nome_golpe != "katch_reza" or "pegou" in l.memo:
        return False
    if not (R_INI <= l.t < R_INI + R_JANELA):
        return False
    if not g or g.get("proj") or g.get("ultimate") or g.get("ultimate2") or atacante is None or atacante is l:
        return False  # (tiro e ultimate passam: o ponto fraco dele)
    l.memo["pegou"] = l.t
    l.inv = max(l.inv, 26)
    return True


def reza(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    if "pegou" in m:
        u = t - m["pegou"]
        if u == 1:
            som.tocar("parry")
            jogo.faisca(l.x + 24 * l.s * l.dir, l.y - 90 * l.s, False, True)
            if abs(outro.x - l.x) > 64 * l.s:  # aparece colado nele
                l.x = max(PAREDE_E, min(PAREDE_D, outro.x - l.dir * 56 * l.s))
        if u == R_REVIDA:
            acerto(jogo, l, outro, "katch_revide")
            som.tocar("shuriken", 0.9)
        P_ = POSES_KATCHADE
        if u < 3:
            l.sobrepor = dict(P_["k_abre"])
        elif u < R_REVIDA + 10:
            l.sobrepor = misturar(P_["k_abre"], P_["k_cruza"], suave(min(1, (u - 3) / 3)))
        else:
            l.sobrepor = misturar(P_["k_cruza"], P_["parado"], suave(min(1, (u - R_REVIDA - 10) / 10)))
        l.fisica(jogo)
        if u >= R_REVIDA + 22:
            l.sobrepor = {}
            return "fim"
        return
    l.fisica(jogo)
    if t >= R_INI + R_JANELA + R_ABERTO:  # ninguém bateu: fica aberto e volta
        return "fim"


def petala(tela, x, y, giro, s, cor=(250, 160, 202)):
    pts = []
    for k, r in ((0, 5), (1, 2.4), (2, 5), (3, 2.4)):
        a = giro + k * math.pi / 2
        pts.append((x + math.cos(a) * r * s * 1.4, y + math.sin(a) * r * s))
    pygame.draw.polygon(tela, cor, pts)
    pygame.draw.polygon(tela, (184, 52, 126), pts, 1)


def reza_efeito(l, tela):
    """Pétalas rosas girando devagar em volta dele enquanto reza (o aviso pro outro: NÃO BATE!)."""
    if "pegou" in l.memo or not (R_INI <= l.t < R_INI + R_JANELA):
        return
    for k in range(5):
        a = l.t * 0.07 + k * math.tau / 5
        x = l.x + math.cos(a) * 34 * l.s
        y = l.y - 70 * l.s + math.sin(a) * 40 * l.s
        petala(tela, x, y, a * 2, l.s)


_registra("katch_reza", ini=R_INI, ativo=R_JANELA, rec=R_ABERTO, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          logica=reza, efeito=reza_efeito, ia="contra",
          quadros=[(0, "parado"), (R_INI, "k_reza"), (R_INI + R_JANELA, "k_reza"),
                   (R_INI + R_JANELA + R_ABERTO, "parado")])
GOLPES["katch_reza"]["total"] = 9999
GOLPES["katch_revide"] = dict(dano=14, hit=24, defe=12, emp=4, nivel="medio", especial=True, derruba=True, voo=(6, 8))

# ---- SHIFT: ASAS (voo curto pra frente; segurando TRÁS voa pra trás) ----
A_SOLTA, A_FIM = 3, 26


def asas(l, outro, jogo):
    t = l.t
    if t <= A_SOLTA and l.r in (4, 1, 7):
        l.memo["tras"] = True  # (segurou TRÁS em algum momento antes de soltar)
    if t == A_SOLTA:
        l.memo["lado"] = -l.dir if l.memo.get("tras") else l.dir
        l.vy = -6
        l.inv = max(l.inv, 8)
        som.tocar("vento", 0.8)
    if A_SOLTA <= t < A_FIM - 6:
        l.vx = 10.5 * l.memo["lado"]
        l.vy -= GRAVIDADE * 0.55  # plana
    elif t >= A_FIM - 6:
        l.vx *= 0.7
    l.fisica(jogo)
    if t >= A_FIM and l.no_chao():
        return "fim"
    if t > 70:
        return "fim"


_registra("katch_asas", ini=A_SOLTA, ativo=1, rec=A_FIM - A_SOLTA, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          logica=asas, ia="medio",
          quadros=[(0, "parado"), (A_SOLTA, "k_asas"), (A_FIM - 4, "k_asas"), (A_FIM, "parado")])
GOLPES["katch_asas"]["total"] = 9999

# ---- Z: ULTIMATE — DANÇA DAS FOICES (some camuflado na flor; aparece de vários lados cortando) ----
U_SOME = 26          # quadros sumindo
U_ALCANCE = 520
U_CORTES = 6
U_INTERVALO = 9
U_CORTE, U_FINAL = 5, 15


def ultimate(l, outro, jogo):
    t = l.t
    m = l.memo
    m["tela_toda"] = True
    import ult2
    l.vx = 0
    if t < U_SOME:
        l.invisivel = max(l.invisivel, 4)  # some (a flor fecha)
        if t == 2:
            som.tocar("vento", 0.6)
        l.fisica(jogo)
        return
    if t == U_SOME:
        if abs(outro.x - l.x) < U_ALCANCE * l.s and pode_pegar(outro):
            m["pegou"] = t
            ult2.pega(outro, "golpeado")
        else:
            m["errou"] = t
            l.invisivel = 0
    if "errou" in m:
        l.fisica(jogo)
        return "fim" if t - m["errou"] > 24 else None
    u = t - m["pegou"]
    ult2.camera(jogo, 1.25, outro.x, outro.y - 80 * outro.s)
    k, f = divmod(u, U_INTERVALO)
    if k < U_CORTES:
        if f == 0:  # aparece de um lado e corta
            lado = 1 if k % 2 == 0 else -1
            if k >= 4:
                lado = random.choice((-1, 1))
            l.x = max(PAREDE_E, min(PAREDE_D, outro.x - lado * 62 * l.s))
            l.y = CHAO - (40 * l.s if k in (2, 5) else 0)
            l.dir = lado
            l.invisivel = 0
            ult2.bate(l, outro, jogo, U_CORTE * l.f["forca"], "katch_ult_corte")
            m.setdefault("rastros", []).append((l.x, l.y, lado, t))
            som.tocar("shuriken", 0.7)
        l.sobrepor = dict(POSES_KATCHADE["k_cruza" if f < 5 else "k_abre"])
        l.vy = 0
    elif u == U_CORTES * U_INTERVALO + 6:  # o FINAL: X gigante
        l.y = CHAO
        l.dir = 1 if outro.x >= l.x else -1
        l.x = max(PAREDE_E, min(PAREDE_D, outro.x - l.dir * 60 * l.s))
        l.sobrepor = dict(POSES_KATCHADE["k_cruza"])
        ult2.bate(l, outro, jogo, U_FINAL * l.f["forca"], "katch_ult_final", ultimo=True, forte=True)
        ult2.solta(outro, l.dir * 7, -11)
        m["x_final"] = (outro.x, outro.y - 70 * outro.s, t)
        som.tocar("explosao", 0.8)
    l.fisica(jogo)
    if u >= U_CORTES * U_INTERVALO + 34:
        l.sobrepor = {}
        l.y = min(l.y, CHAO)
        return "fim"


def ultimate_efeito(l, tela):
    """Os riscos rosas dos cortes no ar e o X gigante no final. (Só desenho.)"""
    m = l.memo
    for x, y, lado, t0 in m.get("rastros", ()):
        idade = l.t - t0
        if idade > 14:
            continue
        a = max(0, 255 - idade * 18)
        sup = pygame.Surface((int(140 * l.s), int(140 * l.s)), pygame.SRCALPHA)
        w, h = sup.get_size()
        pygame.draw.line(sup, (255, 190, 230, a), (0, h * 0.2), (w, h * 0.8), max(2, int(5 * l.s)))
        pygame.draw.line(sup, (255, 255, 255, a), (0, h * 0.2), (w, h * 0.8), max(1, int(2 * l.s)))
        tela.blit(sup, (x + lado * 40 * l.s - w / 2, y - 80 * l.s - h / 2))
    xf = m.get("x_final")
    if xf:
        idade = l.t - xf[2]
        if idade < 26:
            r = (30 + idade * 6) * l.s
            a = max(0, 255 - idade * 10)
            sup = pygame.Surface((int(r * 2 + 8), int(r * 2 + 8)), pygame.SRCALPHA)
            c = r + 4
            for cor, larg in (((255, 160, 210, a), 9), ((255, 255, 255, a), 3)):
                pygame.draw.line(sup, cor, (c - r, c - r), (c + r, c + r), max(1, int(larg * l.s)))
                pygame.draw.line(sup, cor, (c - r, c + r), (c + r, c - r), max(1, int(larg * l.s)))
            tela.blit(sup, (xf[0] - c, xf[1] - c))
    if l.t < U_SOME:  # pétalas subindo enquanto ele some
        for k in range(6):
            fase = (l.t * 2 + k * 11) % 40
            petala(tela, l.x + math.sin(k * 2.1 + l.t * 0.1) * 26 * l.s, l.y - fase * 3 * l.s, k + l.t * 0.2, l.s)


_registra("katch_ultimate", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", ultimate=True,
          logica=ultimate, efeito=ultimate_efeito, ia="ultimate", ia_alcance=U_ALCANCE - 60,
          quadros=[(0, "parado"), (6, "k_reza"), (U_SOME, "k_reza")])
GOLPES["katch_ultimate"]["total"] = 9999
GOLPES["katch_ult_corte"] = dict(dano=U_CORTE, hit=30, defe=12, emp=1, nivel="medio", especial=True, ultimate=True)
GOLPES["katch_ult_final"] = dict(dano=U_FINAL, hit=30, defe=12, emp=6, nivel="medio", especial=True, ultimate=True,
                                 derruba=True)

GOLPES_KATCHADE = {"E": "katch_corte", "Q": "katch_bote", "R": "katch_reza", "SHIFT": "katch_asas",
                   "Z": "katch_ultimate"}
NOMES = {"E": "corte cruzado", "Q": "bote (agarra e joga pra cima)", "R": "postura de oração (contra-ataque)",
         "SHIFT": "asas (voo curto)", "Z": "DANÇA DAS FOICES"}
PROVOCACAO_QUADROS = [(0, "parado"), (8, "k_limpa"), (20, "k_reza"), (34, "k_limpa"), (50, "k_reza"), (68, "parado")]


# =====================================================================
# PASSIVAS (H na seleção)
#   CAMUFLAGEM      parado 2 s: fica meio transparente (some na flor); o próximo golpe bate +30%
#   FOICES AFIADAS  golpe que acerta deixa um CORTE brilhando: tira mais um pouquinho por 2 s (sem sangue)
# =====================================================================
CAMUFLA_ESPERA = 120
CAMUFLA_DANO = 1.3
CORTE_TEMPO = 120
CORTE_DANO = 5.0       # no total, espalhado nos 2 s


def todo_quadro(l, jogo):
    import habilidades as hab
    hs = hab.ativas(l)
    x = l.extra
    if hasattr(jogo, "L"):
        l._jogo_L = jogo.L  # (pro desenho do corte no outro)
        cicatriz_quadro(jogo)
    if "camuflagem" in hs:
        parado = l.estado in ("parado", "agachado") and abs(l.vx) < 0.1 and l.no_chao()
        x["parado_t"] = x.get("parado_t", 0) + 1 if parado else 0
        if x["parado_t"] >= CAMUFLA_ESPERA and l.vida > 0:
            if not x.get("camuflado"):
                som.tocar("vento", 0.3)
            x["camuflado"] = True
            l.invisivel = max(l.invisivel, 3)
        if x.get("camuflado") and l.estado == "ataque":  # saiu da camuflagem atacando: esse golpe bate +30%
            x["camufla_id"] = l.golpe_id
            x["camuflado"] = False
        elif x.get("camuflado") and not parado:
            x["camuflado"] = False
        if x.get("camufla_id") is not None and (l.estado != "ataque" or l.golpe_id != x["camufla_id"]):
            x["camufla_id"] = None
    if "foices_afiadas" in hs and hasattr(jogo, "L"):
        outro = outro_de(l, jogo)
        if l.estado == "ataque" and l.acertou and x.get("corte_id") != l.golpe_id \
                and outro.estado in ("golpeado", "voando", "agarrado", "tonto") and outro.vida > 0:
            x["corte_id"] = l.golpe_id
            outro.extra["corte"] = CORTE_TEMPO
        c = outro.extra.get("corte", 0)
        if c > 0:
            outro.extra["corte"] = c - 1
            if outro.vida > 1:
                outro.vida = max(1, outro.vida - CORTE_DANO / CORTE_TEMPO)


def desenhar_sempre(l, tela):
    """O CORTE brilhando em quem levou (FOICES AFIADAS) e a CICATRIZ do CORTE VERTICAL (por cima do outro)."""
    for o in getattr(l, "_jogo_L", ()):
        if o is not l:
            desenhar_cicatriz(tela, o)
        c = o.extra.get("corte", 0) if o is not l else 0
        if c <= 0:
            continue
        a = int(200 * min(1, c / 30))
        brilha = (o.t // 4) % 2
        sup = pygame.Surface((int(40 * o.s), int(40 * o.s)), pygame.SRCALPHA)
        w, h = sup.get_size()
        cor = (255, 255, 255, a) if brilha else (255, 150, 210, a)
        pygame.draw.line(sup, cor, (w * 0.15, h * 0.2), (w * 0.85, h * 0.8), max(2, int(3 * o.s)))
        tela.blit(sup, (o.x - w / 2, o.y - 80 * o.s - h / 2))


# =====================================================================
# Z2: 2ª ULTIMATE — CORTE VERTICAL (ideia do Gomes): um corte só, de cima pra baixo, que deixa uma CICATRIZ:
# quem levou fica com MENOS RESISTÊNCIA (leva +15% de dano) e MAIS LENTO (-15%) até o FIM DA PARTIDA.
# =====================================================================
V_FOCO = 44          # quadros concentrando (as foices sobem, as pétalas param no ar)
V_ALCANCE = 640
V_CORTE = V_FOCO + 10
V_DANO = 35
CICATRIZ_DANO = 1.15   # leva 15% a mais
CICATRIZ_VEL = 0.85    # anda 15% mais devagar


def marcar(jogo, o):
    """Guarda na PARTIDA (o lutador é recriado a cada round): esse aí tem a cicatriz até o fim."""
    if not hasattr(jogo, "cicatrizes"):
        jogo.cicatrizes = set()
    jogo.cicatrizes.add(o.f.get("nome_base", o.f["nome"]))
    o.extra["cicatriz"] = True


def cicatriz_quadro(jogo):
    """Todo quadro (round novo): quem está marcado continua marcado."""
    for o in getattr(jogo, "L", ()):
        if o.f.get("nome_base", o.f["nome"]) in getattr(jogo, "cicatrizes", ()):
            o.extra["cicatriz"] = True


def corte_vertical(l, outro, jogo):
    t = l.t
    m = l.memo
    m["tela_toda"] = True
    import ult2
    l.vx = 0
    if t < V_FOCO:
        ult2.camera(jogo, 1.35, l.x, l.y - 90 * l.s)
        l.sobrepor = misturar(POSES_KATCHADE["k_reza"], POSES_KATCHADE["k_lanca"], suave(min(1, t / 20)))
        if t == 2:
            som.tocar("carga", 0.9)
        l.fisica(jogo)
        return
    if t == V_FOCO:
        if abs(outro.x - l.x) < V_ALCANCE * l.s and pode_pegar(outro):
            m["pegou"] = t
            ult2.pega(outro, "golpeado")
            l.dir = 1 if outro.x >= l.x else -1
            m["de"] = l.x
            l.x = max(PAREDE_E, min(PAREDE_D, outro.x - l.dir * 46 * l.s))  # aparece na frente dele, lá em cima
            l.y = CHAO - 120 * l.s
            l.vy = 0
            som.tocar("vento", 0.9)
        else:
            m["errou"] = t
            l.sobrepor = {}
    if "errou" in m:
        l.fisica(jogo)
        return "fim" if t - m["errou"] > 24 else None
    ult2.camera(jogo, 1.2, outro.x, outro.y - 90 * outro.s)
    if t < V_CORTE:  # lá no alto, foices pra cima... e DESCE
        l.sobrepor = dict(POSES_KATCHADE["k_lanca"])
        l.y = min(CHAO, l.y + 12 * l.s)
        return
    if t == V_CORTE:
        l.y = CHAO
        l.sobrepor = dict(POSES_KATCHADE["k_cruza"])
        m["linha"] = (outro.x, t)
        som.tocar("shuriken")
        jogo.tremer(6)
    if t == V_CORTE + 26:  # o silêncio... e o corte ABRE
        ult2.bate(l, outro, jogo, V_DANO * l.f["forca"], "katch_corte_vertical", ultimo=True, forte=True)
        marcar(jogo, outro)
        ult2.solta(outro, l.dir * 5, -8)
        som.tocar("explosao", 0.8)
    if t >= V_CORTE + 56:
        l.sobrepor = {}
        return "fim"


def corte_vertical_efeito(l, tela):
    """A risca vertical gigante (branca e rosa) que aparece e depois ABRE com o brilho."""
    m = l.memo
    if l.t < V_FOCO:  # pétalas paradas no ar em volta (o mundo para)
        for k in range(8):
            a = k * math.tau / 8 + 0.3
            petala(tela, l.x + math.cos(a) * 60 * l.s, l.y - 80 * l.s + math.sin(a) * 50 * l.s, a, l.s)
    lin = m.get("linha")
    if not lin:
        return
    x, t0 = lin
    u = l.t - t0
    if u > 50:
        return
    alto = CHAO - 200 * l.s
    if u < 26:  # a risca fina (ainda não abriu)
        a = 255 if u < 4 else 200
        pygame.draw.line(tela, (255, 255, 255), (x, alto), (x, CHAO), max(1, int(2 * l.s)))
        if u < 4:
            pygame.draw.line(tela, (255, 170, 220), (x, alto - 30), (x, CHAO + 10), max(2, int(6 * l.s)))
        return
    k = u - 26
    larg = int((6 + k * 1.5) * l.s)
    a = max(0, 255 - k * 10)
    sup = pygame.Surface((larg * 2 + 4, int(CHAO - alto) + 40), pygame.SRCALPHA)
    w = sup.get_width()
    pygame.draw.rect(sup, (255, 160, 214, a), (w / 2 - larg, 0, larg * 2, sup.get_height()))
    pygame.draw.rect(sup, (255, 255, 255, a), (w / 2 - larg / 3, 0, larg * 2 / 3, sup.get_height()))
    tela.blit(sup, (x - w / 2, alto - 20))


GOLPES["katch_corte_vertical"] = dict(dano=V_DANO, hit=30, defe=12, emp=4, nivel="medio", especial=True,
                                      ultimate=True, ultimate2=True, derruba=True)


def desenhar_cicatriz(tela, o):
    """A cicatriz rosa vertical brilhando no peito de quem levou o CORTE VERTICAL."""
    if not o.extra.get("cicatriz"):
        return
    brilho = 160 + int(60 * math.sin(o.t * 0.08))
    cor = (255, 150, 210, brilho)
    sup = pygame.Surface((int(10 * o.s), int(46 * o.s)), pygame.SRCALPHA)
    pygame.draw.line(sup, cor, (sup.get_width() / 2, 0), (sup.get_width() / 2, sup.get_height()), max(2, int(3 * o.s)))
    tela.blit(sup, (o.x - sup.get_width() / 2, o.y - 100 * o.s))


# =====================================================================
# ENTRADA: desce PLANANDO de uma folha de grama gigante, pousa na POSTURA DE ORAÇÃO, as pétalas caem em volta
# =====================================================================
EN_POUSA, EN_ABRE, EN_FIM = 34, 70, 100


def entrada(l, t, jogo):
    x0 = l.extra.setdefault("entrada_x", l.x)
    P_ = POSES_KATCHADE
    if t < EN_POUSA:  # planando de cima, com as asas
        k = t / EN_POUSA
        l.y = CHAO - (1 - suave(k)) * 330 * l.s
        l.x = x0 - l.dir * (1 - k) * 120 * l.s
        l.sobrepor = dict(P_["k_asas"])
        l.extra["entrando_asas"] = True
        if t == 2:
            som.tocar("vento", 0.6)
    elif t == EN_POUSA:
        l.y, l.x = CHAO, x0
        l.extra["entrando_asas"] = False
        som.tocar("terra", 0.5)
        for _ in range(16):  # as pétalas levantando no pouso
            jogo.faiscas.append([l.x + random.uniform(-40, 40), CHAO - random.uniform(0, 20), random.uniform(-3, 3),
                                 random.uniform(-5, -1), random.randint(30, 50),
                                 random.choice(((250, 160, 202), (255, 226, 240), (222, 102, 160))), 4])
    if t >= EN_POUSA:
        if t < EN_ABRE:
            l.sobrepor = misturar(P_["k_agacha"], P_["k_reza"], suave(min(1, (t - EN_POUSA) / 16)))
        elif t < EN_ABRE + 12:  # abre as foices de uma vez (*shing*)
            if t == EN_ABRE:
                som.tocar("shuriken", 0.8)
            l.sobrepor = misturar(P_["k_reza"], P_["k_abre"], suave((t - EN_ABRE) / 6))
        else:
            l.sobrepor = misturar(P_["k_abre"], P_["parado"], suave(min(1, (t - EN_ABRE - 12) / 14)))
    if t >= EN_FIM:
        l.sobrepor = {}
    l.t += 1


def entrada_efeito(l, tela, t):
    """Pétalas caindo devagar em volta dele (desde o começo)."""
    for k in range(10):
        fase = (t * 1.6 + k * 23) % 160
        x = l.extra.get("entrada_x", l.x) + math.sin(k * 1.9 + t * 0.05) * (50 + k * 6) * l.s
        petala(tela, x, CHAO - 260 * l.s + fase * 1.6 * l.s, k + t * 0.1, l.s)


# =====================================================================
# VITÓRIA: junta as foices em ORAÇÃO, faz uma REVERÊNCIA... e cai uma chuva de pétalas
# =====================================================================
VI_REZA, VI_CURVA, VI_VOLTA = 10, 46, 90


def vitoria(l, t, jogo):
    P_ = POSES_KATCHADE
    curvado = dict(P_["k_reza"], pc=(14, 84), cb=(26, 94), mt=(28, 100), mf=(30, 100), ct=(22, 78), cf=(24, 78))
    if t < VI_REZA:
        l.sobrepor = misturar(P_["parado"], P_["k_reza"], suave(t / VI_REZA))
    elif t < VI_CURVA:
        l.sobrepor = dict(P_["k_reza"])
    elif t < VI_VOLTA:
        l.sobrepor = misturar(P_["k_reza"], curvado, suave(min(1, (t - VI_CURVA) / 14)))
    else:
        l.sobrepor = misturar(curvado, P_["k_reza"], suave(min(1, (t - VI_VOLTA) / 16)))
    if t == VI_CURVA:
        som.tocar("blip", 0.5)
    if VI_REZA <= t < VI_VOLTA + 40 and t % 3 == 0:  # a chuva de pétalas
        jogo.faiscas.append([l.x + random.uniform(-180, 180), CHAO - 300, random.uniform(-0.6, 0.6),
                             random.uniform(1.0, 2.0), random.randint(90, 140),
                             random.choice(((250, 160, 202), (255, 226, 240), (222, 102, 160))), 4])


# =====================================================================
# ROUPA "ESPADACHIM ERRANTE" (samurai, inspirada no Musashi): faixa branca na testa com as pontas voando
# e um quimono índigo por cima do corpo (as foices viram AÇO pela troca de cor)
# =====================================================================
def roupa_samurai(l, tela, p, cabeca, branco):
    if branco:
        return
    from inazumaneko import em_pixel
    esc = l.s / S_REF
    c, q = l.ponto(p, "pc"), l.ponto(p, "qd")
    d = l.lado()
    pontos = [c, q] + ([cabeca(2, 7), cabeca(13, 7)] if cabeca else [])
    k_ = PALETA["k"]

    def desenho(sup, Q, e):
        # (tudo em pixels do sprite: 1 = um quadradinho)
        C, Qd = Q(c), Q(q)
        dx, dy = Qd[0] - C[0], Qd[1] - C[1]
        comp = max(1.0, math.hypot(dx, dy))
        ux, uy = dx / comp, dy / comp      # do peito pro quadril
        nx, ny = -uy, ux                   # pro lado

        def pt(f, lado):
            return (C[0] + dx * f + nx * lado, C[1] + dy * f + ny * lado)
        # o QUIMONO índigo (estreito no peito, abre embaixo, que nem saia de hakama)
        corpo = [pt(-0.05, -4), pt(-0.05, 4), pt(0.75, 5), pt(1.12, 7), pt(1.12, -7), pt(0.75, -5)]
        pygame.draw.polygon(sup, k_, corpo)
        dentro = [pt(0.0, -3), pt(0.0, 3), pt(0.74, 4), pt(1.06, 6), pt(1.06, -6), pt(0.74, -4)]
        pygame.draw.polygon(sup, (58, 62, 112), dentro)
        pygame.draw.line(sup, (40, 42, 80), pt(0.05, 1), pt(1.05, 3))
        # a GOLA branca cruzada
        pygame.draw.line(sup, (240, 236, 226), pt(0.0, -3), pt(0.42, 1))
        pygame.draw.line(sup, (240, 236, 226), pt(0.0, 3), pt(0.42, -1))
        # a FAIXA preta na cintura
        pygame.draw.line(sup, (24, 22, 30), pt(0.72, -5), pt(0.72, 5), 2)
        if not cabeca:
            return
        # a FAIXA na testa (hachimaki) com as duas pontas voando pra trás
        a, b = Q(cabeca(2, 7)), Q(cabeca(13, 7))
        pygame.draw.line(sup, k_, a, b, 3)
        pygame.draw.line(sup, (244, 240, 232), a, b, 1)
        for n in (0, 1):
            balanca = math.sin(l.t * 0.15 + n * 1.3) * 1.5
            ponta = (a[0] - d * (7 + n * 2), a[1] + 2 + n * 3 + balanca)
            meio = ((a[0] + ponta[0]) / 2, (a[1] + ponta[1]) / 2 - 1)
            pygame.draw.lines(sup, k_, False, [a, meio, ponta], 3)
            pygame.draw.lines(sup, (244, 240, 232), False, [a, meio, ponta], 1)

    em_pixel(tela, esc, pontos, desenho)
