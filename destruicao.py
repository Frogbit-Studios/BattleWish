"""CENÁRIO QUE QUEBRA (v3.0, escolha do Gomes): as PANCADAS deixam marca no mapa, ONDE aconteceram.
Arremessou alguém na PAREDE: aquela parte racha (bater de novo no mesmo lugar faz crescer; forte = buraco/rasgo,
e cai alguma coisa do alto ali perto). Alguém CAIU forte no CHÃO: o chão racha ali (forte = cratera + entulho).
Cada mapa quebra do SEU jeito (KITS: tipo de rachadura, entulho e o que cai). É SÓ DESENHO.

Como usar (o partida):
    d = destruicao.Destruicao(nome_do_cenario)         # uma vez por luta (e quando trocar de cenário)
    d.parede(lado, y, forca, t) / d.chao(x, forca, t)   # nas pancadas (forca 0..1)
    d.desenhar(tela_pequena, t, px)                      # depois do fundo, antes dos lutadores
"""
import hashlib
import math
import random

import pygame

from config import CHAO, LARGURA, PAREDE_D, PAREDE_E

# =====================================================================
# OS KITS DE CADA MAPA (pedido do Gomes: cada cenário quebra do SEU jeito)
#   racha:   o tipo da rachadura ("pedra", "madeira", "terra", "gelo", "vidro")
#   entulho: o que vai juntando no chão
#   caem:    o que CAI do alto (e fica no chão)          de: altura de onde cai (0 = topo da tela)
#   fundo:   "buraco" (parede quebra), "rasgo" (papel/cortina rasga), "cratera" (céu aberto: o CHÃO é que afunda)
# =====================================================================
KITS = {
    "TEMPLO": dict(racha="pedra", entulho=("telha", "pedra"), caem=("telha", "lanterna"), de=0.35, fundo="cratera"),
    "PÂNTANO": dict(racha="madeira", entulho=("madeira", "terra"), caem=("galho",), de=0.1, fundo="cratera"),
    "FERRO-VELHO": dict(racha="pedra", entulho=("sucata", "pneu"), caem=("sucata", "pneu"), de=0.25, fundo="cratera"),
    "TOCA": dict(racha="terra", entulho=("terra", "pedra"), caem=("terra", "raiz"), de=0.0, fundo="buraco"),
    "DOJO": dict(racha="madeira", entulho=("madeira", "papel"), caem=("pergaminho", "papel"), de=0.15, fundo="rasgo"),
    "CAMPO DE BATALHA": dict(racha="terra", entulho=("saco", "pedra"), caem=("pedra",), de=0.0, fundo="cratera"),
    "TORRE DO MAGO": dict(racha="pedra", entulho=("livro", "pedra"), caem=("livro", "pocao"), de=0.35, fundo="buraco"),
    "CASSINO": dict(racha="madeira", entulho=("ficha", "carta"), caem=("carta", "ficha"), de=0.05, fundo="rasgo"),
    "LABORATÓRIO": dict(racha="vidro", entulho=("vidro", "sucata"), caem=("vidro",), de=0.0, fundo="buraco"),
    "ARENA DE SUMÔ": dict(racha="madeira", entulho=("madeira", "terra"), caem=("bandeirola",), de=0.35, fundo="rasgo"),
    "SELVA": dict(racha="terra", entulho=("folha", "galho"), caem=("galho", "folha"), de=0.0, fundo="cratera"),
    "VILA DOS SAPOS": dict(racha="terra", entulho=("terra", "folha"), caem=("folha",), de=0.3, fundo="cratera"),
    "TEATRO DE MÁGICA": dict(racha="madeira", entulho=("madeira", "carta"), caem=("holofote", "carta"), de=0.0,
                             fundo="rasgo"),
    "NAVIO FANTASMA": dict(racha="madeira", entulho=("madeira",), caem=("tabua",), de=0.2, fundo="buraco"),
    "CERCADO DO DESERTO": dict(racha="terra", entulho=("areia", "madeira"), caem=("tabua",), de=0.55, fundo="cratera"),
    "PRAIA DA ILHA": dict(racha="terra", entulho=("areia", "concha"), caem=("coco", "folha"), de=0.2, fundo="cratera"),
    "MONTANHA NEVADA": dict(racha="gelo", entulho=("neve", "gelo"), caem=("neve", "pingente"), de=0.1,
                            fundo="cratera"),
    "MONTE KARASUMA": dict(racha="pedra", entulho=("pedra", "folha_vermelha"), caem=("folha_vermelha", "lanterna"),
                           de=0.4, fundo="cratera"),
    "CAVERNA DOS MORCEGOS": dict(racha="pedra", entulho=("pedra", "cristal"), caem=("estalactite", "cristal"), de=0.0,
                                 fundo="buraco"),
    "CAMPO GIGANTE": dict(racha="terra", entulho=("terra", "folha"), caem=("folha",), de=0.0, fundo="cratera"),
    "FLORESTA ANTIGA": dict(racha="pedra", entulho=("pedra", "galho"), caem=("galho", "folha"), de=0.05,
                            fundo="buraco"),
}
KIT_PADRAO = dict(racha="pedra", entulho=("pedra",), caem=("pedra",), de=0.0, fundo="buraco")

RACHA_COR = {  # (a linha, o brilho da beirada)
    "pedra": ((18, 14, 18), None), "madeira": ((40, 22, 12), (150, 110, 70)), "terra": ((34, 22, 14), None),
    "gelo": ((90, 150, 200), (240, 250, 255)), "vidro": ((220, 240, 255), (255, 255, 255)),
}

# as PEÇAS em pixel (mapinha + cores) — o que cai e o que fica no chão
_C = {"k": (18, 14, 18)}
PECAS = {
    "pedra": ([".kkk.", "kpppk", "kpPpk", ".kkk."], {"p": None, "P": None}),  # (cor do próprio mapa)
    "madeira": (["kkkkkkk", "kmMmmMk", "kkkkkkk"], {"m": (120, 80, 44), "M": (160, 112, 64)}),
    "tabua": (["kkkkkkkkk", "kmmMmmmMk", "kmmmmMmmk", "kkkkkkkkk"], {"m": (110, 74, 42), "M": (150, 104, 60)}),
    "galho": (["k.....k..", ".k...k.kk", "..kkkkk..", ".....k..."], {}),
    "raiz": (["kk.....", "..kk...", "....kkk"], {}),
    "terra": ([".kk.", "kttk", ".kk."], {"t": (96, 66, 40)}),
    "telha": (["kkkkk", "krRrk", "kkkkk"], {"r": (150, 60, 50), "R": (190, 90, 70)}),
    "lanterna": ([".kk.", "kyyk", "kyYk", "kyyk", ".kk."], {"y": (230, 80, 60), "Y": (255, 220, 120)}),
    "sucata": (["kkk..", "kgGk.", ".kgkk", "..kk."], {"g": (110, 116, 124), "G": (170, 176, 184)}),
    "pneu": ([".kkk.", "kk.kk", "k...k", "kk.kk", ".kkk."], {}),
    "papel": (["kkkk", "kwwk", "kkkk"], {"w": (236, 228, 200)}),
    "pergaminho": (["kkkkk", "kwwwk", "kWwWk", "kkkkk"], {"w": (236, 220, 170), "W": (180, 60, 50)}),
    "saco": ([".kkkk.", "ksSssk", "kssSsk", ".kkkk."], {"s": (170, 150, 100), "S": (200, 180, 130)}),
    "livro": (["kkkk", "kbbk", "kbBk", "kkkk"], {"b": (160, 50, 60), "B": (230, 200, 120)}),
    "pocao": ([".k.", "kvk", "kvk", ".k."], {"v": (120, 230, 140)}),
    "ficha": ([".kk.", "kfFk", ".kk."], {"f": (220, 40, 40), "F": (250, 250, 250)}),
    "carta": (["kkk", "kwk", "krk", "kkk"], {"w": (250, 250, 250), "r": (220, 40, 40)}),
    "vidro": (["..k", ".kv", "kvk"], {"v": (190, 230, 255)}),
    "bandeirola": (["kkk", "kRk", "kRk", ".k."], {"R": (200, 50, 60)}),
    "folha": ([".k", "kg"], {"g": (90, 170, 70)}),
    "folha_vermelha": ([".k", "kr"], {"r": (210, 60, 50)}),
    "holofote": (["kkkk", "kggk", "kyyk", "kkkk"], {"g": (90, 90, 100), "y": (255, 240, 170)}),
    "areia": ([".kkk.", "kaAak"], {"a": (210, 180, 120), "A": (236, 210, 150)}),
    "concha": ([".k.", "kck", "kck"], {"c": (250, 210, 200)}),
    "coco": ([".kk.", "kbbk", ".kk."], {"b": (110, 74, 40)}),
    "neve": ([".www.", "wwwww"], {"w": (240, 246, 255)}),
    "gelo": (["..k", ".ki", "kik"], {"i": (180, 230, 250)}),
    "pingente": (["kik", "kik", ".k."], {"i": (200, 240, 255)}),
    "estalactite": (["kpppk", ".kpk.", ".kpk.", "..k.."], {"p": (70, 60, 80)}),
    "cristal": ([".k.", "kvk", "kvk", ".k."], {"v": (190, 120, 255)}),
}


def _peca(nome, cor_mapa=None):
    """A peça em pixel (Surface pequena, 2x), com a cor do mapa nas peças que não têm cor própria."""
    mapa, cores = PECAS.get(nome, PECAS["pedra"])
    sup = pygame.Surface((len(mapa[0]), len(mapa)), pygame.SRCALPHA)
    for j, linha in enumerate(mapa):
        for i, c in enumerate(linha):
            if c == ".":
                continue
            if c == "k":
                cor = _C["k"]
            else:
                cor = cores.get(c)
                if cor is None:  # (pedra: a cor do mapa, e o brilho um pouco mais claro)
                    base = cor_mapa or (110, 104, 100)
                    cor = _mais_claro(base) if c.isupper() else base
            sup.set_at((i, j), cor)
    return pygame.transform.scale(sup, (sup.get_width() * 2, sup.get_height() * 2))


MAX_MARCAS = 14   # (no máximo tantas marcas no mapa: as mais velhas e fracas somem)
JUNTA = 50        # (pancada a menos disso de uma marca = a MESMA marca cresce)


class Destruicao:
    """As marcas que as PANCADAS deixaram no cenário (pedido do Gomes: tem que ter CAUSA).
      parede(lado, y, forca, t) — alguém foi ARREMESSADO na parede (lado -1 esquerda / 1 direita) na altura y
      chao(x, forca, t)         — alguém CAIU forte no chão em x
    forca 0..1 (uma pancada boa ~0.5; ultimate/golpe forte ~1). Bater de novo no mesmo lugar faz a marca CRESCER.
    Só desenho; as marcas nascem de coisas que aconteceram na luta (iguais nos dois PCs)."""

    def __init__(self, nome):
        self.semente = int(hashlib.md5(str(nome).encode()).hexdigest()[:8], 16)
        self.kit = KITS.get(nome, KIT_PADRAO)
        self.marcas = []
        self._pecas = {}

    # ---- as pancadas ----
    def _marca(self, tipo, x, y, forca, t):
        for m in self.marcas:
            if m["tipo"] == tipo and abs(m["x"] - x) < JUNTA and abs(m["y"] - y) < JUNTA:
                m["forca"] = min(2.0, m["forca"] + forca)  # a MESMA marca cresce
                m["t"] = t
                if forca >= 0.4:
                    m["caiu"].append(t)  # (mais uma coisa cai do alto)
                return
        semente = (self.semente + int(x) * 31 + int(y) * 7 + len(self.marcas) * 101) & 0xFFFFFFF
        self.marcas.append(dict(tipo=tipo, x=x, y=y, forca=min(2.0, forca), t=t, t0=t, semente=semente,
                                caiu=[t] if forca >= 0.4 else []))
        if len(self.marcas) > MAX_MARCAS:
            self.marcas.remove(min(self.marcas, key=lambda m: (m["forca"], m["t"])))

    def parede(self, lado, y, forca, t):
        x = PAREDE_E - 30 if lado < 0 else PAREDE_D + 30
        if self.kit["fundo"] == "cratera":  # (céu aberto: não tem parede de verdade — racha o CHÃO ali na beirada)
            self._marca("chao", max(0, min(LARGURA, x + (40 if lado < 0 else -40))), CHAO, forca, t)
            return
        self._marca("parede", max(0, min(LARGURA, x)), y, forca, t)

    def chao(self, x, forca, t):
        self._marca("chao", x, CHAO, forca, t)

    # ---- o desenho ----
    def _img(self, nome, tela, onde):
        if nome not in self._pecas:
            self._pecas[nome] = _peca(nome, _cor_pedra(tela, onde) if nome == "pedra" else None)
        return self._pecas[nome]

    def desenhar(self, tela, t, px=1):
        """Desenha as marcas na tela PEQUENA (px = quantos pixels da tela grande por pixel)."""
        linha_cor, brilho = RACHA_COR.get(self.kit["racha"], RACHA_COR["pedra"])
        chao = CHAO / px
        for m in self.marcas:
            rnd = random.Random(m["semente"])
            f = m["forca"]
            cresce = min(1.0, (t - m["t0"]) / 6)  # (a rachadura "corre" rapidinho quando nasce)
            cx, cy = m["x"] / px, m["y"] / px
            if m["tipo"] == "parede":
                lado = 1 if m["x"] < LARGURA / 2 else -1  # (a rachadura entra pro meio da tela)
                cx = (PAREDE_E - 20) / px if lado > 0 else (PAREDE_D + 20) / px
                n_rachas = 2 + int(f * 3)
                for r in range(n_rachas):
                    ang = (rnd.uniform(-1.1, 1.1) if lado > 0 else math.pi + rnd.uniform(-1.1, 1.1))
                    self._racha(tela, rnd, (cx, cy), ang, (5 + f * 9) * cresce, linha_cor, brilho, px)
                if f >= 0.7:  # BURACO (ou RASGO) no meio da batida
                    self._buraco(tela, rnd, cx + lado * 3, cy, 3 + f * 4, linha_cor)
            else:  # CHÃO
                n_rachas = 2 + int(f * 2)
                for r in range(n_rachas):
                    ang = 0.0 if r % 2 else math.pi
                    self._racha(tela, rnd, (cx, chao + 1), ang + rnd.uniform(-0.25, 0.25), (6 + f * 10) * cresce,
                                linha_cor, brilho, px, achatado=True)
                if f >= 0.6:  # CRATERA
                    w = (6 + f * 8) * cresce
                    pygame.draw.ellipse(tela, _claro(tela, (cx, chao + 2)), (cx - w / 2 - 1, chao - 2, w + 2, 5))
                    pygame.draw.ellipse(tela, (16, 12, 14), (cx - w / 2, chao - 1, w, 3))
                for i in range(int(f * 3)):  # ENTULHO em volta (as peças do kit)
                    nome = self.kit["entulho"][i % len(self.kit["entulho"])]
                    img = self._img(nome, tela, (cx, chao - 6))
                    ex = cx + rnd.uniform(-12, 12) - img.get_width() / 2
                    tela.blit(img, (int(ex), int(chao - img.get_height() + 1)))
            for k, tc in enumerate(m["caiu"][:4]):  # o que CAIU do alto ali perto (e ficou no chão)
                nome = self.kit["caem"][(m["semente"] + k) % len(self.kit["caem"])]
                img = self._img(nome, tela, (cx, chao - 6))
                x = (cx + (12 + k * 9) * (1 if m["tipo"] == "parede" and m["x"] < LARGURA / 2 else -1)
                     if m["tipo"] == "parede" else cx + (k - 1.5) * 10)
                u = (t - tc) / 26
                topo = self.kit.get("de", 0) * chao
                if u < 0:
                    continue
                if u < 1:
                    y = topo + (chao - topo) * u * u
                    img = pygame.transform.rotate(img, 90 * int(u * 4))
                else:
                    y = chao
                tela.blit(img, (int(x - img.get_width() / 2), int(y - img.get_height() + 1)))

    @staticmethod
    def _racha(tela, rnd, ini, ang, comp, cor, brilho, px, achatado=False):
        """Uma rachadura em zigue-zague saindo de ini (em pixels pequenos), com um galhinho."""
        x, y = ini
        pts = [(x, y)]
        passos = max(2, int(comp / 3))
        for _ in range(passos):
            ang2 = ang + rnd.uniform(-0.6, 0.6)
            d = rnd.uniform(2, 4)
            x, y = x + math.cos(ang2) * d, y + math.sin(ang2) * d * (0.25 if achatado else 1)
            pts.append((x, y))
        if len(pts) > 1:
            claro = brilho or _claro(tela, pts[0])
            pygame.draw.lines(tela, claro, False, [(a + 1, b + 1) for a, b in pts], 1)
            pygame.draw.lines(tela, cor, False, pts, 1)
            if len(pts) > 3:
                gx, gy = pts[len(pts) // 2]
                a = ang + rnd.choice((-1, 1)) * 1.1
                pygame.draw.line(tela, cor, (gx, gy), (gx + math.cos(a) * 3, gy + math.sin(a) * 3 * (0.3 if achatado else 1)))

    def _buraco(self, tela, rnd, cx, cy, r, cor):
        rasgo = self.kit["fundo"] == "rasgo"
        lados = 11 if rasgo else 8
        pts = []
        for k in range(lados):
            a = k / lados * math.tau
            rr = r * (rnd.uniform(0.4, 1.3) if rasgo else rnd.uniform(0.6, 1.1))
            pts.append((cx + math.cos(a) * rr * (0.7 if rasgo else 1), cy + math.sin(a) * rr * (1.3 if rasgo else 0.85)))
        pygame.draw.polygon(tela, _claro(tela, (cx, cy)), [(x + 1, y + 1) for x, y in pts])
        pygame.draw.polygon(tela, (12, 9, 14), pts)
        if not rasgo:
            pygame.draw.polygon(tela, cor if self.kit["racha"] != "vidro" else (18, 14, 18), pts, 1)


def _pega(tela, p):
    x = max(0, min(tela.get_width() - 1, int(p[0])))
    y = max(0, min(tela.get_height() - 1, int(p[1])))
    return tela.get_at((x, y))[:3]


def _claro(tela, p):
    """Um tom mais CLARO que o fundo naquele lugar (a beirada iluminada da rachadura)."""
    return _mais_claro(_pega(tela, p))


def _mais_claro(c):
    return tuple(min(255, int(v * 1.35 + 18)) for v in c)


def _cor_pedra(tela, p):
    """A cor da pedra: o fundo do mapa naquele lugar, puxado pro cinza."""
    c = _pega(tela, p)
    m = sum(c) / 3
    return tuple(int(v * 0.55 + m * 0.45) for v in c)
