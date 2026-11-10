"""RIVAIS (v2.x, pedido do Gomes): cada lutador tem um rival. Quando os dois se enfrentam:
tela "RIVAIS!" no VS (com o lema da rivalidade), falas próprias (no falas.py) e MOEDAS EM DOBRO pra quem vencer.
Quem escolheu as duplas foi o Gomes. O MAX-10 é rival do MAGNUS (o 13, dino-robô de fogo).
As vitórias contra o rival ficam no save: save.d()["rivais"] = {nome do lutador: vitórias contra o rival}.
"""
import math

import pygame

import save
from config import *  # noqa: F401,F403
from efeitos import texto, texto_grande

MULT_MOEDAS = 2  # vencer o rival paga o dobro

# (um, outro, lema)
DUPLAS = [
    ("JOHN", "KUN", "TRUQUE CONTRA TRUQUE"),
    ("TAMER", "CRÁQUEN", "FERA CONTRA FERA"),
    ("TROMOS", "TRAFO", "MUTANTE CONTRA MUTANTE"),
    ("CANNAN", "KING RIP", "SOLDADO CONTRA MESTRE"),
    ("TAI", "RIB", "GIGANTE CONTRA PEQUENO"),
    ("MAX-10", "MAGNUS", "MÁQUINA CONTRA MÁQUINA"),
    ("FINN", "CRÁQUEN", "MAGIA CONTRA MALDIÇÃO"),   # (o CRÁQUEN tem DOIS rivais: TAMER e FINN)
    ("MAGNUS", "SPHYRUS", "PREDADOR CONTRA PREDADOR"),  # (o MAGNUS também tem 2: MAX-10 e SPHYRUS)
    ("INAZUMANEKO", "RIB", "SAMURAI CONTRA NINJA"),
    ("NOCTURNUS", "SPHYRUS", "IRMÃOS DE LABORATÓRIO"),
    ("KATCHADE", "INAZUMANEKO", "LÂMINA CONTRA LÂMINA"),  # (v4.0: o INAZUMANEKO tem 2 rivais: RIB e KATCHADE)
    ("SILVANUS", "TAMER", "GUARDIÃ CONTRA CAÇADOR"),  # (o TAMER tem 2 rivais: CRÁQUEN e SILVANUS)  # (v3.0: o SPHYRUS tem 2 rivais: MAGNUS e NOCTURNUS)  # (v3.0: o RIB tem 2 rivais: TAI e INAZUMANEKO)
]
_RIVAIS = {}
_LEMA = {}
for _a, _b, _lema in DUPLAS:
    _RIVAIS.setdefault(_a, []).append(_b)
    _RIVAIS.setdefault(_b, []).append(_a)
    _LEMA[frozenset((_a, _b))] = _lema


def _nome(x):
    """Aceita o nome ou a ficha (roupa e Sombra contam como o lutador de verdade)."""
    if isinstance(x, dict):
        x = x.get("nome_base", x.get("nome", ""))
    return x[len("SOMBRA DO "):] if x.startswith("SOMBRA DO ") else x


def rivais_de(lutador):
    """Todos os rivais (a maioria tem 1; o CRÁQUEN tem 2)."""
    return list(_RIVAIS.get(_nome(lutador), []))


def rival_de(lutador):
    """O (primeiro) rival, ou None."""
    r = _RIVAIS.get(_nome(lutador))
    return r[0] if r else None


def sao_rivais(a, b):
    return _nome(a) != _nome(b) and _nome(b) in _RIVAIS.get(_nome(a), [])


def lema(a, b):
    """'TRUQUE CONTRA TRUQUE' (ou "" se não são rivais)."""
    return _LEMA.get(frozenset((_nome(a), _nome(b))), "")


# ---- vitórias contra o rival (pros TROFÉUS) ----
def _tabela():
    t = save.d().get("rivais")
    if not isinstance(t, dict):
        t = save.d()["rivais"] = {}
    return t


def registrar(partida):
    """Fim da luta: se o jogador (lado 0) venceu o RIVAL dele, conta no save. Devolve True se contou."""
    import estatisticas
    if not estatisticas.conta(partida) or partida.vencedor != 0:
        return False
    eu, ele = partida.fichas
    if partida.trio:  # TRIO: quem estava lutando no fim
        eu, ele = partida.L[0].f, partida.L[1].f
    if not sao_rivais(eu, ele):
        return False
    t = _tabela()
    n = _nome(eu)
    t[n] = t.get(n, 0) + 1
    save.salvar()
    return True


def vitorias(nome=None):
    """Vitórias contra o rival: de um lutador, ou de todos somados (nome=None)."""
    t = _tabela()
    if nome is not None:
        return t.get(_nome(nome), 0)
    return sum(v for v in t.values() if isinstance(v, int))


# ---- desenho (a partida/selecao chamam; só lê, não muda nada) ----
def desenhar_faixa(tela, a, b, t, y=None):
    """A faixa 'RIVAIS!' com o lema, entrando com tremidinha e raios (pra tela de VS)."""
    if not sao_rivais(a, b):
        return
    y = ALTURA // 2 + 120 if y is None else y
    k = min(1.0, t / 18)  # entra crescendo
    faixa = pygame.Surface((LARGURA, 84), pygame.SRCALPHA)
    faixa.fill((20, 0, 0, int(170 * k)))
    tela.blit(faixa, (0, y - 42))
    for lado in (-1, 1):  # raios dos dois lados
        x0 = LARGURA // 2 + lado * 190
        pts = []
        for i in range(6):
            pts.append((x0 + lado * i * 26, y - 30 + (i % 2) * 34 + int(math.sin(t * 0.7 + i) * 4)))
        if (t // 4) % 3:
            pygame.draw.lines(tela, (255, 230, 120), False, pts, 4)
            pygame.draw.lines(tela, (255, 255, 255), False, pts, 1)
    treme = int(math.sin(t * 1.3) * 3) if t < 40 else 0
    texto_grande(tela, "RIVAIS!", 46, (255, 70, 50), (LARGURA // 2 + treme, y - 8), 0.6 + 0.4 * k,
                 contorno=(50, 0, 0))
    if t > 12:
        texto(tela, lema(a, b), 16, (255, 230, 150), (LARGURA // 2, y + 26))
