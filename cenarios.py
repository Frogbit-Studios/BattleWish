"""Os cenários. Cada personagem tem a sua casa:
  TEMPLO      (o de sempre)
  PÂNTANO     do Rib: noite, lua, água com vitória-régia, vaga-lumes
  FERRO-VELHO do Max-10: fumaça laranja, carros velhos, guindaste, faíscas de solda
  TOCA        do Trafo: caverna, raízes, cogumelos que brilham, gotas pingando

Todo cenário tem: fundo (desenhado uma vez), desenhar_pequeno (fundo + coisas que mexem, já na pixel art)
e desenhar_frente (coisas que ficam na frente dos lutadores).
"""
import math
import random

import pygame

from config import *  # noqa: F401,F403
from efeitos import Cenario as Templo
from efeitos import mistura_cor


def _degrade(sup, rect, c1, c2):
    x, y, w, h = rect
    for i in range(h):
        sup.fill(mistura_cor(c1, c2, i / max(1, h - 1)), (x, y + i, w, 1))


def _brilho(sup, pos, raio, cor, alfa):
    camada = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
    for i in range(6, 0, -1):
        pygame.draw.circle(camada, (*cor, int(alfa * (1 - i / 7))), (raio, raio), int(raio * i / 6))
    sup.blit(camada, (pos[0] - raio, pos[1] - raio))


class Base:
    nome = ""

    def __init__(self):
        self.fundo = self._fundo()
        self._px = None

    def desenhar_pequeno(self, t, px):
        if self._px != px:
            self._px = px
            self._fundo_peq = pygame.transform.smoothscale(self.fundo, (LARGURA // px, ALTURA // px))
            self._tela_peq = pygame.Surface((LARGURA // px, ALTURA // px))
        tela = self._tela_peq
        tela.blit(self._fundo_peq, (0, 0))
        self.animar(tela, t, px)
        return tela

    def animar(self, tela, t, px):
        pass

    def desenhar_frente(self, tela, t, px=1):
        pass


# =====================================================================
# PÂNTANO (Rib)
# =====================================================================
class Pantano(Base):
    nome = "PÂNTANO"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, 400), (14, 26, 34), (60, 92, 80))
        _brilho(sup, (720, 150), 150, (220, 240, 200), 70)
        pygame.draw.circle(sup, (226, 236, 200), (720, 150), 56)
        pygame.draw.circle(sup, (206, 218, 182), (700, 136), 10)
        pygame.draw.circle(sup, (206, 218, 182), (738, 168), 7)
        rng = random.Random(21)
        for camada, (cor, base, alt) in enumerate((((30, 52, 50), 410, 220), ((18, 36, 34), 420, 260))):
            for _ in range(7):  # árvores com musgo pendurado
                x = rng.uniform(-40, LARGURA + 40)
                h = alt * rng.uniform(0.7, 1.1)
                pygame.draw.polygon(sup, cor, [(x - 14, base), (x - 6, base - h), (x + 6, base - h), (x + 14, base)])
                for _ in range(5):
                    cx, cy = x + rng.uniform(-60, 60), base - h + rng.uniform(-10, 40)
                    pygame.draw.circle(sup, cor, (int(cx), int(cy)), int(rng.uniform(24, 44)))
                    for _ in range(3):  # musgo
                        mx = cx + rng.uniform(-30, 30)
                        pygame.draw.line(sup, mistura_cor(cor, (70, 100, 60), 0.4), (mx, cy), (mx, cy + rng.uniform(30, 70)), 3)
        # água atrás do píer
        _degrade(sup, (0, 400, LARGURA, CHAO - 400), (40, 66, 56), (22, 40, 36))
        for _ in range(9):  # vitórias-régias
            x, y = rng.uniform(0, LARGURA), rng.uniform(412, CHAO - 14)
            r = rng.uniform(14, 26)
            pygame.draw.ellipse(sup, (52, 110, 54), (x - r, y - r * 0.32, r * 2, r * 0.64))
            pygame.draw.polygon(sup, (40, 66, 56), [(x, y), (x + r, y - 2), (x + r, y + 3)])
            if rng.random() < 0.4:
                pygame.draw.circle(sup, (236, 170, 200), (int(x - r * 0.3), int(y - 4)), 5)
        # píer de madeira
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (112, 84, 56), (64, 46, 32))
        for k in range(1, 6):
            y = CHAO + (ALTURA - CHAO) * (k / 6) ** 1.4
            pygame.draw.line(sup, (54, 38, 26), (0, y), (LARGURA, y), 2)
        for x in range(30, LARGURA, 160):  # postes
            pygame.draw.rect(sup, (70, 50, 32), (x, CHAO - 26, 14, 30))
            pygame.draw.rect(sup, (40, 28, 18), (x, CHAO - 26, 14, 30), 2)
        pygame.draw.line(sup, (150, 116, 80), (0, CHAO), (LARGURA, CHAO), 3)
        névoa = pygame.Surface((LARGURA, 80), pygame.SRCALPHA)
        for y in range(80):
            névoa.fill((180, 210, 190, int(40 * math.sin(y / 80 * math.pi))), (0, y, LARGURA, 1))
        sup.blit(névoa, (0, 360))
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(5)
        self.vaga = [[rng.uniform(0, LARGURA), rng.uniform(180, 460), rng.uniform(0, math.tau)] for _ in range(22)]
        self.taboas = [(rng.uniform(0, 140) if i % 2 else rng.uniform(LARGURA - 140, LARGURA), rng.uniform(0.8, 1.3))
                       for i in range(12)]

    def animar(self, tela, t, px):
        for i in range(5):  # ondinhas na água
            y = (412 + i * 14) / px
            x = ((t * 0.6 + i * 170) % (LARGURA + 200) - 100) / px
            pygame.draw.line(tela, (90, 130, 110), (x, y), (x + 40 / px, y), 1)
        for v in self.vaga:  # vaga-lumes
            v[2] += 0.04
            x = v[0] + math.sin(v[2] * 1.3) * 20
            y = v[1] + math.cos(v[2]) * 12
            if math.sin(v[2] * 3) > -0.2:
                pygame.draw.circle(tela, (230, 255, 140), (int(x / px), int(y / px)), max(1, 3 // px))

    def desenhar_frente(self, tela, t, px=1):
        for x, e in self.taboas:  # taboas balançando nos cantos
            vento = math.sin(t * 0.04 + x * 0.03) * 6 * e
            topo = (x + vento, ALTURA - 120 * e)
            pygame.draw.line(tela, (40, 70, 36), (x / px, ALTURA / px), (topo[0] / px, topo[1] / px), max(1, 3 // px))
            pygame.draw.ellipse(tela, (96, 64, 36), (topo[0] / px - 3 / px, topo[1] / px - 4, max(2, 7 // px), 9))


# =====================================================================
# FERRO-VELHO (Max-10)
# =====================================================================
class FerroVelho(Base):
    nome = "FERRO-VELHO"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (70, 44, 40), (220, 130, 70))
        _brilho(sup, (240, 300), 170, (255, 180, 100), 90)
        rng = random.Random(8)
        for x in (90, 160, 820):  # chaminés
            pygame.draw.rect(sup, (60, 40, 38), (x, 170, 26, 260))
            pygame.draw.rect(sup, (150, 60, 40), (x, 190, 26, 10))
        pygame.draw.rect(sup, (54, 38, 36), (40, 300, 220, 140))  # fábrica
        for i in range(6):
            pygame.draw.rect(sup, (230, 170, 80), (56 + i * 34, 330, 14, 18))
        # guindaste
        pygame.draw.line(sup, (40, 30, 30), (620, CHAO), (620, 120), 10)
        for y in range(130, CHAO, 30):
            pygame.draw.line(sup, (40, 30, 30), (614, y), (626, y + 30), 3)
        pygame.draw.line(sup, (40, 30, 30), (560, 130), (900, 130), 10)
        # pilhas de carros velhos
        for base, n in ((CHAO - 4, 4), (CHAO - 48, 3)):
            for i in range(n):
                x = 300 + i * 90 + (20 if base < CHAO - 10 else 0) + rng.uniform(-10, 10)
                cor = rng.choice(((110, 60, 50), (70, 80, 90), (120, 100, 50), (60, 70, 60)))
                pygame.draw.rect(sup, cor, (x, base - 44, 84, 40), border_radius=6)
                pygame.draw.rect(sup, mistura_cor(cor, (0, 0, 0), 0.5), (x + 14, base - 58, 50, 18), border_radius=4)
                pygame.draw.rect(sup, (30, 24, 24), (x, base - 44, 84, 40), 2, border_radius=6)
                for rx in (x + 16, x + 66):
                    pygame.draw.circle(sup, (24, 20, 20), (int(rx), int(base - 4)), 9)
        for i in range(4):  # tambores de óleo
            x = 760 + i * 34
            pygame.draw.rect(sup, (60, 90, 120) if i % 2 else (140, 60, 40), (x, CHAO - 40, 28, 40))
            pygame.draw.line(sup, (20, 20, 20), (x, CHAO - 26), (x + 28, CHAO - 26), 2)
        # cerca de arame
        for x in range(0, LARGURA, 18):
            pygame.draw.line(sup, (90, 70, 60), (x, 380), (x + 30, CHAO - 50), 1)
            pygame.draw.line(sup, (90, 70, 60), (x + 30, 380), (x, CHAO - 50), 1)
        # chão de concreto
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (120, 112, 104), (70, 66, 62))
        for _ in range(8):  # manchas de óleo
            x, y = rng.uniform(0, LARGURA), rng.uniform(CHAO + 10, ALTURA - 10)
            pygame.draw.ellipse(sup, (54, 50, 50), (x, y, rng.uniform(30, 80), rng.uniform(6, 14)))
        for x in range(0, LARGURA, 40):  # faixa amarela e preta
            pygame.draw.polygon(sup, (220, 180, 40), [(x, CHAO), (x + 20, CHAO), (x + 30, CHAO + 8), (x + 10, CHAO + 8)])
        pygame.draw.line(sup, (40, 36, 34), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def animar(self, tela, t, px):
        for i, x in enumerate((90, 160, 820)):  # fumaça das chaminés
            for k in range(4):
                u = (t * 0.6 + k * 30 + i * 13) % 120
                pygame.draw.circle(tela, (110, 90, 86), (int((x + 13 + u * 0.6) / px), int((170 - u) / px)),
                                   max(2, int((8 + u * 0.18) / px)))
        a = math.sin(t * 0.03) * 0.25  # gancho balançando
        topo = (840, 130)
        ponta = (topo[0] + math.sin(a) * 150, topo[1] + math.cos(a) * 150)
        pygame.draw.line(tela, (30, 24, 24), (topo[0] / px, topo[1] / px), (ponta[0] / px, ponta[1] / px), 1)
        pygame.draw.rect(tela, (60, 60, 64), (ponta[0] / px - 14 / px, ponta[1] / px, 28 / px, 12 / px))
        if (t // 20) % 2:  # luz de alerta piscando
            pygame.draw.circle(tela, (255, 60, 40), (int(620 / px), int(116 / px)), max(2, 6 // px))
        if (t // 3) % 7 < 3:  # faíscas de solda
            rng = random.Random(t // 3)
            for _ in range(6):
                pygame.draw.line(tela, (255, 230, 150), (int(470 / px), int(400 / px)),
                                 (int((470 + rng.uniform(-30, 30)) / px), int((400 + rng.uniform(-30, 10)) / px)), 1)


# =====================================================================
# TOCA (Trafo)
# =====================================================================
class Toca(Base):
    nome = "TOCA"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (26, 18, 14), (70, 48, 30))
        rng = random.Random(3)
        for x in (160, 520, 800):  # luz entrando por buracos no teto
            luz = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            pygame.draw.polygon(luz, (255, 230, 170, 30), [(x - 20, 0), (x + 20, 0), (x + 120, CHAO), (x - 40, CHAO)])
            sup.blit(luz, (0, 0))
            pygame.draw.ellipse(sup, (200, 190, 150), (x - 24, -8, 48, 16))
        for cor, base in (((44, 30, 22), 360), ((34, 24, 18), 420)):  # pedras do fundo
            pts = [(0, CHAO)] + [(x, base - 50 * abs(math.sin(x * 0.011 + base))) for x in range(0, LARGURA + 30, 30)] + \
                [(LARGURA, CHAO)]
            pygame.draw.polygon(sup, cor, pts)
        pygame.draw.rect(sup, (20, 14, 10), (0, 0, LARGURA, 40))  # teto
        for _ in range(26):  # raízes penduradas
            x = rng.uniform(0, LARGURA)
            pts = [(x, 30)]
            for k in range(1, 6):
                pts.append((pts[-1][0] + rng.uniform(-8, 8), 30 + k * rng.uniform(12, 26)))
            pygame.draw.lines(sup, (70, 50, 30), False, pts, 3)
        for _ in range(10):  # ossinhos e pedras
            x = rng.uniform(0, LARGURA)
            pygame.draw.ellipse(sup, (90, 80, 70), (x, CHAO - 8, rng.uniform(14, 30), 10))
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (96, 70, 44), (52, 36, 24))
        for _ in range(60):  # pedrinhas no chão
            pygame.draw.circle(sup, (70, 52, 36), (int(rng.uniform(0, LARGURA)), int(rng.uniform(CHAO + 6, ALTURA))),
                               int(rng.uniform(1, 4)))
        pygame.draw.line(sup, (120, 90, 60), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(9)
        self.cogumelos = [(rng.uniform(20, LARGURA - 20), rng.choice(((80, 220, 200), (140, 240, 120))), rng.uniform(0.7, 1.3))
                          for _ in range(9)]
        self.gotas = [(rng.uniform(0, LARGURA), rng.uniform(0, 200)) for _ in range(7)]

    def animar(self, tela, t, px):
        for x, cor, e in self.cogumelos:  # cogumelos que brilham
            pulso = 0.6 + 0.4 * math.sin(t * 0.05 + x)
            y = CHAO - 2
            r = 10 * e
            pygame.draw.circle(tela, mistura_cor((40, 30, 20), cor, pulso * 0.5),
                               (int(x / px), int((y - 14 * e) / px)), max(2, int(r * 1.8 / px)))
            pygame.draw.line(tela, (200, 190, 160), (x / px, y / px), (x / px, (y - 14 * e) / px), max(1, int(3 * e / px)))
            pygame.draw.ellipse(tela, mistura_cor((60, 60, 50), cor, pulso),
                                (int((x - r) / px), int((y - 14 * e - r * 0.6) / px), max(2, int(2 * r / px)),
                                 max(2, int(r / px))))
        for x, fase in self.gotas:  # gotas pingando do teto
            u = (t * 4 + fase * 3) % 600
            if u < CHAO - 40:
                pygame.draw.line(tela, (150, 190, 220), (x / px, (40 + u) / px), (x / px, (46 + u) / px), 1)


# =====================================================================
# DOJO (King Rip)
# =====================================================================
class Dojo(Base):
    nome = "DOJO"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (70, 44, 30), (120, 80, 52))
        pygame.draw.rect(sup, (50, 30, 20), (0, 0, LARGURA, 60))  # viga do teto
        for x in range(0, LARGURA, 120):
            pygame.draw.rect(sup, (40, 24, 16), (x, 0, 18, CHAO))  # pilares
        for i, x in enumerate((140, 380, 620)):  # portas de papel (shoji) com luz atrás
            pygame.draw.rect(sup, (236, 222, 180), (x, 120, 180, 280))
            for k in range(1, 4):
                pygame.draw.line(sup, (90, 60, 40), (x + k * 45, 120), (x + k * 45, 400), 4)
            for k in range(1, 6):
                pygame.draw.line(sup, (90, 60, 40), (x, 120 + k * 47), (x + 180, 120 + k * 47), 4)
            pygame.draw.rect(sup, (60, 36, 24), (x, 120, 180, 280), 8)
        for x, cor in ((70, (150, 30, 30)), (880, (30, 50, 120))):  # estandartes com símbolo
            pygame.draw.rect(sup, cor, (x - 30, 70, 60, 200))
            pygame.draw.circle(sup, (230, 210, 150), (x, 150), 20, 4)
            pygame.draw.line(sup, (230, 210, 150), (x - 12, 150), (x + 12, 150), 4)
        # suporte de armas (bastões e nunchakus)
        pygame.draw.rect(sup, (60, 36, 24), (820, 300, 110, 10))
        pygame.draw.rect(sup, (60, 36, 24), (820, 380, 110, 10))
        for k in range(4):
            pygame.draw.line(sup, (160, 110, 60), (830 + k * 26, 290), (836 + k * 26, CHAO - 4), 5)
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (176, 150, 96), (120, 96, 60))  # tatame
        for x in range(0, LARGURA, 120):
            pygame.draw.line(sup, (100, 80, 50), (x, CHAO), (x - 60, ALTURA), 3)
        pygame.draw.line(sup, (60, 40, 26), (0, CHAO), (LARGURA, CHAO), 4)
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(6)
        self.po = [[rng.uniform(140, 800), rng.uniform(120, 420), rng.uniform(0, math.tau)] for _ in range(30)]

    def animar(self, tela, t, px):
        for x in (110, 850):  # lanternas tremeluzindo
            a = 0.7 + 0.3 * math.sin(t * 0.2 + x)
            pygame.draw.circle(tela, mistura_cor((120, 60, 20), (255, 190, 90), a), (int(x / px), int(300 / px)),
                               max(2, 10 // px))
        for p in self.po:  # pozinho flutuando na luz
            p[2] += 0.02
            x = p[0] + math.sin(p[2]) * 16
            y = (p[1] - t * 0.15) % 300 + 120
            tela.set_at((int(x / px), int(y / px)), (250, 236, 200))


# =====================================================================
# CAMPO DE BATALHA (Cannan)
# =====================================================================
class CampoBatalha(Base):
    nome = "CAMPO DE BATALHA"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (40, 40, 46), (150, 110, 80))  # céu de fumaça no fim da tarde
        _brilho(sup, (700, 330), 200, (255, 150, 80), 70)  # incêndio lá longe
        rng = random.Random(12)
        for cor, base, amp in (((70, 62, 58), 380, 40), ((56, 50, 46), 420, 26)):  # morros e ruínas
            pts = [(0, CHAO)] + [(x, base - amp * abs(math.sin(x * 0.009 + base))) for x in range(0, LARGURA + 30, 30)] + \
                [(LARGURA, CHAO)]
            pygame.draw.polygon(sup, cor, pts)
        for x, h in ((120, 90), (300, 60), (760, 110)):  # prédios destruídos
            pts = [(x, 420), (x, 420 - h), (x + 20, 420 - h + 14), (x + 34, 420 - h - 6), (x + 60, 420 - h + 20), (x + 60, 420)]
            pygame.draw.polygon(sup, (44, 40, 40), pts)
            for k in range(3):
                pygame.draw.rect(sup, (26, 24, 26), (x + 8 + k * 18, 420 - h + 30, 8, 10))
        for x in (230, 620):  # holofotes
            pygame.draw.rect(sup, (40, 40, 44), (x - 4, CHAO - 90, 8, 90))
            pygame.draw.rect(sup, (60, 60, 66), (x - 14, CHAO - 104, 28, 16))
        # sacos de areia e arame farpado
        for i in range(LARGURA // 34 + 1):
            for fila, y in ((0, CHAO - 14), (1, CHAO - 28)):
                x = i * 34 + fila * 17 - 10
                if fila and i % 3 == 0:
                    continue
                pygame.draw.ellipse(sup, (140, 120, 80), (x, y, 36, 16))
                pygame.draw.ellipse(sup, (90, 76, 50), (x, y, 36, 16), 2)
        for x in range(0, LARGURA, 22):
            pygame.draw.line(sup, (90, 86, 80), (x, CHAO - 44), (x + 22, CHAO - 40), 1)
            pygame.draw.line(sup, (90, 86, 80), (x + 10, CHAO - 46), (x + 12, CHAO - 38), 1)
        for x in range(40, LARGURA, 180):
            pygame.draw.line(sup, (60, 50, 40), (x, CHAO - 50), (x, CHAO - 28), 3)
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (96, 84, 64), (54, 46, 36))  # terra
        for _ in range(9):  # crateras
            x, y = rng.uniform(0, LARGURA), rng.uniform(CHAO + 10, ALTURA - 12)
            w = rng.uniform(40, 90)
            pygame.draw.ellipse(sup, (44, 38, 30), (x, y, w, w * 0.22))
            pygame.draw.ellipse(sup, (110, 98, 76), (x, y, w, w * 0.22), 2)
        for _ in range(30):  # cápsulas de bala no chão
            pygame.draw.rect(sup, (190, 160, 70), (rng.uniform(0, LARGURA), rng.uniform(CHAO + 6, ALTURA - 4), 3, 2))
        pygame.draw.line(sup, (40, 34, 28), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(4)
        self.cinzas = [[rng.uniform(0, LARGURA), rng.uniform(0, CHAO), rng.uniform(0, math.tau)] for _ in range(26)]

    def animar(self, tela, t, px):
        for x, fase in ((230, 0.0), (620, 2.0)):  # luz dos holofotes varrendo o céu
            a = -math.pi / 2 + math.sin(t * 0.012 + fase) * 0.6
            topo = (x, CHAO - 100)
            luz = [(topo[0] / px, topo[1] / px)]
            for d in (-0.08, 0.08):
                luz.append(((topo[0] + math.cos(a + d) * 600) / px, (topo[1] + math.sin(a + d) * 600) / px))
            camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(camada, (255, 240, 200, 26), luz)
            tela.blit(camada, (0, 0))
        ciclo = t % 170  # explosão lá longe
        if ciclo < 26:
            rng = random.Random(t // 170)
            x, y = rng.uniform(80, LARGURA - 80), rng.uniform(330, 400)
            r = (6 + ciclo * 1.6) / px
            cor = mistura_cor((255, 230, 140), (120, 80, 60), ciclo / 26)
            pygame.draw.circle(tela, cor, (int(x / px), int(y / px)), max(2, int(r)))
        for c in self.cinzas:  # cinzas caindo
            c[2] += 0.03
            x = (c[0] + math.sin(c[2]) * 20 + t * 0.2) % LARGURA
            y = (c[1] + t * 0.4) % CHAO
            tela.set_at((int(x / px), int(y / px)), (200, 190, 180) if int(c[0]) % 3 else (255, 150, 80))


# =====================================================================
# TORRE DO MAGO (Finn)
# =====================================================================
class TorreMago(Base):
    nome = "TORRE DO MAGO"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (30, 22, 46), (62, 48, 80))  # parede de pedra
        rng = random.Random(21)
        for y in range(0, CHAO, 26):  # tijolos de pedra
            off = 0 if (y // 26) % 2 else 30
            for x in range(-30 + off, LARGURA, 60):
                c = rng.randint(-6, 6)
                pygame.draw.rect(sup, (48 + c, 38 + c, 66 + c), (x + 2, y + 2, 56, 22))
        # janelão redondo com o céu de noite e a lua
        cx, cy, r = LARGURA // 2, 190, 120
        pygame.draw.circle(sup, (20, 26, 60), (cx, cy), r)
        for _ in range(40):
            a, d = rng.uniform(0, math.tau), rng.uniform(0, r - 10)
            sup.set_at((int(cx + math.cos(a) * d), int(cy + math.sin(a) * d)), (230, 230, 255))
        _brilho(sup, (cx + 40, cy - 30), 70, (220, 220, 255), 70)
        pygame.draw.circle(sup, (236, 236, 220), (cx + 40, cy - 30), 30)
        pygame.draw.circle(sup, (210, 210, 196), (cx + 32, cy - 36), 6)
        pygame.draw.circle(sup, (60, 46, 30), (cx, cy), r, 14)
        pygame.draw.line(sup, (60, 46, 30), (cx - r, cy), (cx + r, cy), 8)
        pygame.draw.line(sup, (60, 46, 30), (cx, cy - r), (cx, cy + r), 8)
        # estantes de livros nos lados
        for x0 in (30, LARGURA - 230):
            pygame.draw.rect(sup, (70, 44, 26), (x0, 120, 200, 300))
            for k in range(4):
                y = 140 + k * 70
                x = x0 + 10
                while x < x0 + 186:
                    w = rng.randint(8, 16)
                    h = rng.randint(40, 56)
                    cor = rng.choice(((140, 40, 40), (40, 80, 140), (60, 120, 60), (150, 120, 40), (90, 50, 120)))
                    pygame.draw.rect(sup, cor, (x, y + 56 - h, w, h))
                    x += w + 2
                pygame.draw.rect(sup, (50, 30, 18), (x0, y + 56, 200, 8))
        # mesa com a bola de cristal
        pygame.draw.rect(sup, (80, 50, 30), (640, CHAO - 70, 120, 12))
        pygame.draw.rect(sup, (60, 36, 20), (650, CHAO - 58, 10, 58))
        pygame.draw.rect(sup, (60, 36, 20), (740, CHAO - 58, 10, 58))
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (70, 58, 84), (40, 32, 50))  # chão de pedra
        for x in range(0, LARGURA, 80):
            pygame.draw.line(sup, (34, 28, 44), (x, CHAO), (x - 40, ALTURA), 2)
        # tapete com círculo mágico
        pygame.draw.ellipse(sup, (90, 30, 50), (LARGURA // 2 - 260, CHAO + 8, 520, 40))
        pygame.draw.ellipse(sup, (200, 160, 80), (LARGURA // 2 - 240, CHAO + 12, 480, 32), 2)
        pygame.draw.line(sup, (30, 24, 40), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(5)
        self.velas = [(rng.uniform(260, 700), rng.uniform(250, 380), rng.uniform(0, math.tau)) for _ in range(7)]

    def animar(self, tela, t, px):
        for x, y, f in self.velas:  # velas flutuando
            yy = y + math.sin(t * 0.03 + f) * 8
            pygame.draw.rect(tela, (236, 228, 200), (int(x / px), int(yy / px), max(1, 6 // px), max(2, 18 // px)))
            chama = (255, 200, 90) if (t // 6 + int(f * 10)) % 3 else (255, 240, 160)
            pygame.draw.circle(tela, chama, (int((x + 3) / px), int((yy - 4) / px)), max(1, 4 // px))
        pulso = 0.5 + 0.5 * math.sin(t * 0.05)  # bola de cristal brilhando
        cor = mistura_cor((90, 60, 160), (200, 160, 255), pulso)
        pygame.draw.circle(tela, cor, (int(700 / px), int((CHAO - 88) / px)), max(3, int(20 / px)))
        pygame.draw.circle(tela, (240, 230, 255), (int(694 / px), int((CHAO - 94) / px)), max(1, int(4 / px)))


# =====================================================================
# CASSINO (Kun)
# =====================================================================
class Cassino(Base):
    nome = "CASSINO"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (36, 10, 22), (80, 24, 36))
        for x in range(0, LARGURA, 48):  # cortinas vermelhas
            pygame.draw.rect(sup, (110, 20, 34), (x, 0, 30, 300))
            pygame.draw.rect(sup, (80, 12, 24), (x + 30, 0, 18, 300))
        pygame.draw.rect(sup, (200, 160, 70), (0, 296, LARGURA, 8))  # faixa dourada
        # letreiro com os naipes
        pygame.draw.rect(sup, (20, 8, 16), (LARGURA // 2 - 170, 160, 340, 80), border_radius=14)
        pygame.draw.rect(sup, (255, 210, 90), (LARGURA // 2 - 170, 160, 340, 80), 4, border_radius=14)
        f = pygame.font.SysFont("arialblack,arial", 48, bold=True)
        for i, (naipe, cor) in enumerate((("♠", (240, 240, 250)), ("♥", (255, 70, 90)), ("♦", (255, 70, 90)),
                                          ("♣", (240, 240, 250)))):
            img = f.render(naipe, True, cor)
            sup.blit(img, img.get_rect(center=(LARGURA // 2 - 120 + i * 80, 200)))
        # máquinas caça-níquel no fundo
        for x in (40, 120, 760, 840):
            pygame.draw.rect(sup, (60, 50, 70), (x, 320, 70, 140), border_radius=8)
            pygame.draw.rect(sup, (20, 16, 24), (x + 10, 344, 50, 30))
            for k in range(3):
                pygame.draw.rect(sup, (240, 230, 200), (x + 13 + k * 16, 348, 13, 22))
            pygame.draw.line(sup, (200, 200, 210), (x + 70, 360), (x + 82, 330), 3)
            pygame.draw.circle(sup, (220, 40, 40), (x + 82, 328), 6)
        # mesas de carta (verde)
        for x in (300, 560):
            pygame.draw.ellipse(sup, (20, 14, 16), (x - 4, 386, 108, 34))
            pygame.draw.ellipse(sup, (30, 110, 60), (x, 388, 100, 28))
            pygame.draw.rect(sup, (60, 30, 20), (x + 44, 414, 12, CHAO - 414))
            for k in range(3):
                pygame.draw.rect(sup, (240, 240, 236), (x + 22 + k * 20, 394, 12, 16))
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (120, 24, 36), (60, 10, 20))  # carpete vermelho
        for x in range(0, LARGURA, 40):
            pygame.draw.circle(sup, (160, 120, 50), (x + 20, CHAO + 24), 4)
        pygame.draw.line(sup, (200, 160, 70), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def animar(self, tela, t, px):
        for i, x in enumerate((160, 800)):  # lustres balançando
            a = math.sin(t * 0.02 + i) * 0.05
            topo = (x, 0)
            base = (x + math.sin(a) * 100, math.cos(a) * 100)
            pygame.draw.line(tela, (60, 50, 40), (topo[0] / px, 0), (base[0] / px, base[1] / px), 1)
            for k in range(5):
                bx = base[0] + (k - 2) * 14
                brilha = (t // 8 + k + i) % 4 != 0
                pygame.draw.circle(tela, (255, 230, 160) if brilha else (200, 160, 90),
                                   (int(bx / px), int((base[1] + 6) / px)), max(1, int(4 / px) + 1))
        for i, x in enumerate((40, 120, 760, 840)):  # luzinhas das máquinas
            for k in range(5):
                acesa = (t // 6 + k + i * 2) % 5 == 0
                cor = (255, 220, 80) if acesa else (90, 70, 40)
                pygame.draw.rect(tela, cor, (int((x + 6 + k * 13) / px), int(326 / px), max(1, int(6 / px)),
                                             max(1, int(6 / px))))


# =====================================================================
# LABORATÓRIO (Xenomorph) — o salão de contenção do jogo de terror do Gomes
# =====================================================================
class Laboratorio(Base):
    nome = "LABORATÓRIO"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (10, 18, 22), (24, 40, 44))
        rng = random.Random(31)
        for x in range(0, LARGURA, 64):  # placas de metal da parede
            pygame.draw.rect(sup, (20, 32, 36), (x + 2, 60, 60, CHAO - 60))
            pygame.draw.line(sup, (40, 58, 62), (x + 2, 60), (x + 2, CHAO), 2)
        pygame.draw.rect(sup, (14, 22, 26), (0, 0, LARGURA, 60))  # teto com canos
        for y in (18, 40):
            pygame.draw.line(sup, (50, 62, 66), (0, y), (LARGURA, y), 8)
        # tanques de contenção (um quebrado)
        for i, x in enumerate((140, 380, 620, 840)):
            quebrado = i == 2
            pygame.draw.rect(sup, (40, 50, 54), (x - 50, 140, 100, 18))
            pygame.draw.rect(sup, (40, 50, 54), (x - 50, CHAO - 40, 100, 40))
            vidro = pygame.Surface((90, CHAO - 198), pygame.SRCALPHA)
            vidro.fill((60, 160, 120, 40 if quebrado else 90))
            sup.blit(vidro, (x - 45, 158))
            if not quebrado:
                pygame.draw.rect(sup, (90, 200, 150), (x - 45, 220, 90, CHAO - 260))
                pygame.draw.ellipse(sup, (20, 40, 34), (x - 20, 260, 40, 90))  # um vulto lá dentro
            else:
                for _ in range(6):  # vidro estourado
                    a = rng.uniform(0, math.tau)
                    pygame.draw.line(sup, (170, 220, 210), (x, 300), (x + math.cos(a) * 46, 300 + math.sin(a) * 60), 2)
            pygame.draw.rect(sup, (110, 140, 140), (x - 45, 158, 90, CHAO - 198), 3)
        for _ in range(9):  # gosma preta (resina) nas paredes
            x = rng.uniform(0, LARGURA)
            pts = [(x, 60)]
            for k in range(1, 6):
                pts.append((x + rng.uniform(-24, 24), 60 + k * rng.uniform(20, 50)))
            pygame.draw.lines(sup, (6, 8, 10), False, pts, rng.randint(6, 14))
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (40, 50, 52), (18, 24, 26))  # chão de grade
        for x in range(0, LARGURA, 24):
            pygame.draw.line(sup, (26, 34, 36), (x, CHAO), (x - 30, ALTURA), 2)
        pygame.draw.ellipse(sup, (60, 110, 30), (600, CHAO + 14, 120, 16))  # poça de ácido velha
        pygame.draw.line(sup, (70, 90, 92), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def animar(self, tela, t, px):
        a = t * 0.05  # luz de alarme girando
        cx, cy = 480, 52
        camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        for lado in (0, math.pi):
            ang = a + lado
            pts = [(cx / px, cy / px), ((cx + math.cos(ang - 0.18) * 700) / px, (cy + abs(math.sin(ang - 0.18)) * 500) / px),
                   ((cx + math.cos(ang + 0.18) * 700) / px, (cy + abs(math.sin(ang + 0.18)) * 500) / px)]
            pygame.draw.polygon(camada, (255, 40, 30, 22), pts)
        tela.blit(camada, (0, 0))
        pygame.draw.circle(tela, (255, 60, 40) if (t // 10) % 2 else (140, 20, 20), (int(cx / px), int(cy / px)),
                           max(2, int(8 / px)))
        for i, x in enumerate((140, 380, 840)):  # bolhas subindo nos tanques
            for k in range(3):
                u = ((t * 1.5 + k * 40 + i * 17) % 120) / 120
                pygame.draw.circle(tela, (170, 240, 200), (int((x - 20 + k * 20) / px), int((CHAO - 50 - u * 180) / px)),
                                   1)
        if (t // 7) % 23 == 0:  # luz piscando (falhando)
            escuro = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
            escuro.fill((0, 0, 0, 90))
            tela.blit(escuro, (0, 0))


# =====================================================================
# ARENA DE SUMÔ (Tai)
# =====================================================================
class ArenaSumo(Base):
    nome = "ARENA DE SUMÔ"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (40, 24, 20), (90, 56, 40))
        rng = random.Random(17)
        for fila, (y, cor) in enumerate(((250, (50, 34, 30)), (300, (64, 42, 36)), (350, (78, 52, 42)))):  # plateia
            for x in range(-10, LARGURA + 20, 26):
                xx = x + (13 if fila % 2 else 0) + rng.uniform(-3, 3)
                pygame.draw.circle(sup, cor, (int(xx), y), 11)
                pygame.draw.rect(sup, cor, (xx - 12, y + 6, 24, 30), border_radius=6)
        # o teto pendurado (tsuriyane) com as borlas coloridas nos cantos
        pygame.draw.polygon(sup, (60, 40, 30), [(160, 60), (800, 60), (860, 110), (100, 110)])
        pygame.draw.rect(sup, (120, 30, 40), (110, 110, 740, 14))
        for x, cor in ((130, (40, 120, 60)), (330, (220, 220, 220)), (630, (200, 40, 40)), (830, (30, 30, 30))):
            pygame.draw.line(sup, (90, 70, 50), (x, 124), (x, 190), 2)
            pygame.draw.polygon(sup, cor, [(x - 10, 190), (x + 10, 190), (x + 6, 230), (x - 6, 230)])
        for x in (60, 900):  # estandartes
            pygame.draw.rect(sup, (230, 210, 170), (x - 18, 130, 36, 160))
            for k in range(4):
                pygame.draw.rect(sup, (30, 24, 20), (x - 8, 150 + k * 34, 16, 18))
        # o ringue de barro (dohyo) com a corda em círculo
        pygame.draw.polygon(sup, (180, 150, 110), [(40, CHAO), (920, CHAO), (LARGURA, ALTURA), (0, ALTURA)])
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (200, 170, 126), (150, 120, 86))
        pygame.draw.ellipse(sup, (230, 220, 190), (110, CHAO + 4, 740, 48), 6)  # a corda (tawara)
        for x in (420, 540):  # as linhas brancas do começo
            pygame.draw.line(sup, (250, 250, 250), (x, CHAO + 20), (x, CHAO + 34), 4)
        pygame.draw.line(sup, (120, 90, 60), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def animar(self, tela, t, px):
        rng = random.Random(t // 8)
        for _ in range(4):  # flashes de câmera na plateia
            if rng.random() < 0.5:
                x, y = rng.uniform(0, LARGURA), rng.choice((250, 300, 350))
                pygame.draw.circle(tela, (255, 255, 240), (int(x / px), int(y / px)), max(1, int(3 / px)))
        for x in (130, 330, 630, 830):  # borlas balançando
            a = math.sin(t * 0.04 + x) * 3
            pygame.draw.line(tela, (200, 180, 120), (int((x + a) / px), int(230 / px)), (int((x + a * 2) / px),
                                                                                         int(244 / px)), 1)


# =====================================================================
# SELVA (Tamer)
# =====================================================================
class Selva(Base):
    nome = "SELVA"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (40, 80, 60), (120, 170, 110))
        rng = random.Random(41)
        # cachoeira lá no fundo
        pygame.draw.polygon(sup, (60, 90, 70), [(560, 40), (760, 40), (790, CHAO - 60), (530, CHAO - 60)])
        for k in range(8):
            x = 580 + k * 24
            pygame.draw.line(sup, (200, 230, 240), (x, 50), (x + rng.uniform(-6, 6), CHAO - 70), 6)
        pygame.draw.ellipse(sup, (220, 240, 250), (500, CHAO - 90, 320, 50))
        for cor, base, amp in (((46, 92, 54), 300, 60), ((34, 74, 42), 380, 40)):  # morros de mato
            pts = [(0, CHAO)] + [(x, base - amp * abs(math.sin(x * 0.012 + base))) for x in range(0, LARGURA + 30, 30)] + \
                [(LARGURA, CHAO)]
            pygame.draw.polygon(sup, cor, pts)
        for x in (40, 200, 860):  # troncos grandes
            pygame.draw.rect(sup, (70, 50, 34), (x, 0, 46, CHAO))
            pygame.draw.rect(sup, (90, 66, 44), (x + 6, 0, 12, CHAO))
            for _ in range(6):  # copa
                cx, cy = x + 23 + rng.uniform(-90, 90), rng.uniform(-20, 90)
                pygame.draw.circle(sup, rng.choice(((30, 80, 40), (40, 100, 50), (26, 66, 34))), (int(cx), int(cy)),
                                   int(rng.uniform(50, 80)))
        for _ in range(14):  # cipós
            x = rng.uniform(0, LARGURA)
            pts = [(x, 0)]
            for k in range(1, 8):
                pts.append((x + math.sin(k * 0.9) * 10, k * rng.uniform(30, 45)))
            pygame.draw.lines(sup, (50, 110, 50), False, pts, 3)
        for _ in range(20):  # folhagem perto do chão
            x = rng.uniform(0, LARGURA)
            for k in range(5):
                a = -math.pi / 2 + (k - 2) * 0.5
                pygame.draw.line(sup, (40, 120, 50), (x, CHAO), (x + math.cos(a) * 40, CHAO + math.sin(a) * 40), 6)
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (94, 72, 46), (54, 40, 26))  # chão de terra
        pygame.draw.rect(sup, (70, 130, 160), (0, CHAO + 30, LARGURA, 18))  # riozinho
        pygame.draw.line(sup, (120, 180, 200), (0, CHAO + 32), (LARGURA, CHAO + 32), 2)
        pygame.draw.line(sup, (40, 90, 40), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(8)
        self.passaros = [[rng.uniform(0, LARGURA), rng.uniform(40, 160), rng.uniform(0.6, 1.4)] for _ in range(4)]
        self.vagalumes = [(rng.uniform(0, LARGURA), rng.uniform(200, CHAO - 20), rng.uniform(0, math.tau)) for _ in range(14)]

    def animar(self, tela, t, px):
        for k in range(10):  # a água da cachoeira descendo
            y = (t * 4 + k * 40) % (CHAO - 120) + 50
            pygame.draw.line(tela, (240, 250, 255), (int((585 + k * 18) / px), int(y / px)),
                             (int((585 + k * 18) / px), int((y + 14) / px)), 1)
        for p in self.passaros:  # passarinhos voando
            p[0] = (p[0] + p[2]) % (LARGURA + 40)
            asa = 4 if (t // 6) % 2 else -2
            x, y = p[0] / px, p[1] / px
            pygame.draw.lines(tela, (30, 40, 30), False, [(x - 4, y + asa / px), (x, y), (x + 4, y + asa / px)], 1)
        for x, y, f in self.vagalumes:  # bichinhos brilhando
            if math.sin(t * 0.08 + f) > 0.3:
                tela.set_at((int((x + math.sin(t * 0.02 + f) * 20) / px), int(y / px)), (230, 255, 150))


# =====================================================================
# VILA DOS SAPOS (secreta: código ULTRA-MEGA-VILLAGE) — a vila do jogo do Ribbat
# =====================================================================
def _casinha(s, x, base, k=1.0):
    """Casinha de folha da Vila dos Sapos (igual à do jogo do Ribbat, quadrinhos.py)."""
    pygame.draw.ellipse(s, (60, 130, 66), (x - 34 * k, base - 50 * k, 68 * k, 70 * k))
    pygame.draw.ellipse(s, (90, 170, 80), (x - 28 * k, base - 46 * k, 50 * k, 40 * k))
    pygame.draw.rect(s, (60, 130, 66), (x - 34 * k, base - 16 * k, 68 * k, 16 * k))
    pygame.draw.ellipse(s, (50, 34, 22), (x - 10 * k, base - 26 * k, 20 * k, 30 * k))
    pygame.draw.line(s, (40, 100, 50), (x, base - 50 * k), (x + 6 * k, base - 60 * k), max(1, int(3 * k)))


def _bandeirinha(s, x, y, k, t):
    """A bandeira verde da Vila dos Sapos, com a vitória-régia (igual à do jogo do Ribbat)."""
    onda = math.sin(t * 0.1) * 3 * k
    pts = [(x, y), (x + 34 * k, y + 2 * k + onda), (x + 32 * k, y + 22 * k + onda), (x, y + 20 * k)]
    pygame.draw.polygon(s, (96, 196, 84), pts)
    pygame.draw.polygon(s, (40, 112, 50), pts, max(1, int(2 * k)))
    cx, cy = x + 16 * k, y + 11 * k + onda / 2
    pygame.draw.circle(s, (230, 245, 160), (int(cx), int(cy)), max(1, int(6 * k)))
    pygame.draw.line(s, (96, 196, 84), (cx, cy), (cx + 6 * k, cy - 4 * k), max(1, int(2 * k)))


class VilaSapos(Base):
    nome = "VILA DOS SAPOS"
    BANDEIRAS = ((150, 300), (470, 270), (790, 300))  # (x, topo do mastro)

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (150, 200, 240), (255, 220, 170))  # manhã
        _brilho(sup, (820, 90), 90, (255, 240, 170), 120)
        pygame.draw.circle(sup, (255, 236, 150), (820, 90), 40)
        rng = random.Random(23)
        for _ in range(5):  # nuvenzinhas
            x, y = rng.uniform(0, LARGURA), rng.uniform(40, 170)
            for i in range(4):
                pygame.draw.circle(sup, (250, 246, 240), (int(x + i * 22), int(y + (i % 2) * 6)), 18)
        for x in range(-20, LARGURA + 40, 34):  # a floresta lá longe
            alt = 150 + (x * 53 % 60)
            pygame.draw.polygon(sup, (70, 120, 90), [(x - 30, CHAO - 90), (x, CHAO - 90 - alt * 0.6), (x + 30, CHAO - 90)])
        pts = [(0, CHAO)] + [(x, CHAO - 110 - 26 * math.sin(x * 0.01)) for x in range(0, LARGURA + 40, 40)] + [(LARGURA, CHAO)]
        pygame.draw.polygon(sup, (110, 180, 96), pts)  # morrinho de grama
        for x, k in ((70, 1.6), (300, 1.2), (620, 1.4), (900, 1.8)):  # as casinhas de folha
            _casinha(sup, x, CHAO - 34, k)
        for x, topo in self.BANDEIRAS:  # mastros (as bandeiras balançam no animar)
            pygame.draw.line(sup, (230, 220, 190), (x, CHAO - 30), (x, topo), 4)
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (96, 170, 84), (70, 130, 66))  # o chão de grama
        pygame.draw.line(sup, (60, 120, 56), (0, CHAO), (LARGURA, CHAO), 3)
        pygame.draw.rect(sup, (60, 120, 160), (0, CHAO + 26, LARGURA, ALTURA - CHAO - 26))  # o lago na frente
        pygame.draw.line(sup, (140, 200, 230), (0, CHAO + 28), (LARGURA, CHAO + 28), 2)
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(5)
        self.regias = [(rng.uniform(0, LARGURA), CHAO + rng.uniform(36, 52), rng.uniform(60, 110), rng.uniform(0, 6))
                       for _ in range(7)]
        self.libelulas = [[rng.uniform(0, LARGURA), rng.uniform(220, 400), rng.uniform(0, 6)] for _ in range(3)]

    def animar(self, tela, t, px):
        for x, topo in self.BANDEIRAS:
            _bandeirinha(tela, (x + 2) / px, topo / px, 1.3 / px, t + x)
        for x, y, w, f in self.regias:  # vitórias-régias boiando
            y += math.sin(t * 0.05 + f) * 2
            pygame.draw.ellipse(tela, (70, 140, 76), ((x - w / 2) / px, (y - w * 0.12) / px, w / px, w * 0.24 / px))
            pygame.draw.polygon(tela, (60, 120, 160), [(x / px, y / px), ((x + w / 2) / px, (y - w * 0.06) / px),
                                                       ((x + w / 2) / px, (y + w * 0.06) / px)])
        for b in self.libelulas:  # libélulas
            b[2] += 0.03
            x = (b[0] + t * 0.8) % (LARGURA + 60) - 30
            y = b[1] + math.sin(b[2] * 2) * 20
            pygame.draw.line(tela, (60, 140, 200), ((x - 6) / px, y / px), ((x + 6) / px, y / px), max(1, 2 // px))
            if (t // 2) % 2:
                pygame.draw.line(tela, (220, 240, 255), (x / px, (y - 4) / px), (x / px, (y + 4) / px), 1)


# =====================================================================
# TEATRO DE MÁGICA (John): palco, cortina vermelha, holofotes, caixas de mágica e a plateia no escuro
# =====================================================================
class Teatro(Base):
    nome = "TEATRO DE MÁGICA"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (22, 12, 34), (48, 26, 62))  # a parede do fundo do palco
        rng = random.Random(77)
        for _ in range(40):  # estrelinhas pintadas no pano de fundo
            x, y = rng.uniform(140, LARGURA - 140), rng.uniform(70, CHAO - 150)
            pygame.draw.circle(sup, (120, 90, 160), (int(x), int(y)), rng.choice((1, 1, 2)))
        pygame.draw.circle(sup, (220, 210, 150), (LARGURA // 2, 150), 44)  # a lua de papelão
        pygame.draw.circle(sup, (48, 26, 62), (LARGURA // 2 + 18, 140), 40)
        # a caixa de mágica (estrelas) e a caixa de serrar, no fundo do palco
        caixa = pygame.Rect(190, CHAO - 170, 70, 170)
        pygame.draw.rect(sup, (16, 8, 24), caixa.inflate(6, 6), border_radius=6)
        pygame.draw.rect(sup, (90, 40, 140), caixa, border_radius=6)
        for k in range(5):
            cx, cy = caixa.x + 18 + (k % 2) * 34, caixa.y + 22 + k * 30
            pygame.draw.polygon(sup, (240, 200, 70), [(cx + 7 * math.cos(a * math.pi / 5 - math.pi / 2) * (1 if a % 2 == 0 else 0.45),
                                                       cy + 7 * math.sin(a * math.pi / 5 - math.pi / 2) * (1 if a % 2 == 0 else 0.45))
                                                      for a in range(10)])
        serra = pygame.Rect(LARGURA - 330, CHAO - 70, 150, 50)
        pygame.draw.rect(sup, (16, 8, 24), serra.inflate(6, 6), border_radius=4)
        pygame.draw.rect(sup, (170, 40, 50), serra, border_radius=4)
        pygame.draw.line(sup, (230, 230, 236), (serra.centerx, serra.y - 30), (serra.centerx, serra.bottom + 4), 4)
        for x in (serra.x + 8, serra.right - 18):
            pygame.draw.rect(sup, (16, 8, 24), (x, serra.bottom, 10, 20))
        # as cortinas vermelhas nos lados (com dobras) e a bambinela em cima
        for lado in (0, 1):
            for k in range(7):
                x = (k * 20) if lado == 0 else LARGURA - 140 + k * 20
                cor = (150, 20, 30) if k % 2 else (190, 34, 44)
                pygame.draw.rect(sup, cor, (x, 0, 20, CHAO + 4))
            borda = 140 if lado == 0 else LARGURA - 140
            pygame.draw.line(sup, (90, 10, 18), (borda, 0), (borda, CHAO), 4)
            pygame.draw.circle(sup, (230, 190, 70), (borda + (-8 if lado == 0 else 8), CHAO - 230), 9)  # a corda dourada
        pygame.draw.rect(sup, (170, 26, 38), (0, 0, LARGURA, 56))
        for x in range(0, LARGURA, 40):  # a bambinela ondulada com franja dourada
            pygame.draw.ellipse(sup, (170, 26, 38), (x - 4, 36, 48, 40))
            pygame.draw.arc(sup, (230, 190, 70), (x - 4, 36, 48, 40), math.pi, 2 * math.pi, 3)
        # o palco (tábuas de madeira) e a beirada
        _degrade(sup, (0, CHAO, LARGURA, 26), (120, 70, 40), (84, 46, 24))
        for x in range(0, LARGURA, 60):
            pygame.draw.line(sup, (70, 38, 20), (x, CHAO), (x - 20, CHAO + 26), 2)
        pygame.draw.rect(sup, (40, 20, 12), (0, CHAO + 26, LARGURA, 6))
        for x in range(30, LARGURA, 90):  # luzinhas da ribalta
            pygame.draw.circle(sup, (255, 230, 150), (x, CHAO + 29), 3)
        # a plateia no escuro (cabeças), lá embaixo
        sup.fill((10, 6, 14), (0, CHAO + 32, LARGURA, ALTURA - CHAO - 32))
        self.cabecas = [(x + rng.uniform(-10, 10), CHAO + 50 + rng.uniform(0, 14), rng.uniform(0, 6))
                        for x in range(10, LARGURA, 34)]
        return sup

    def __init__(self):
        super().__init__()
        self.holofotes = [(260, 0.7, 0.0), (LARGURA - 260, 0.5, 2.0)]

    def animar(self, tela, t, px):
        luz = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        for x0, vel, fase in self.holofotes:  # os holofotes passeando pelo palco
            alvo = LARGURA / 2 + math.sin(t * 0.01 * vel + fase) * 300
            pygame.draw.polygon(luz, (255, 240, 200, 26), [(x0 / px - 6, 0), (x0 / px + 6, 0),
                                                           ((alvo + 90) / px, CHAO / px), ((alvo - 90) / px, CHAO / px)])
            pygame.draw.ellipse(luz, (255, 240, 200, 40), ((alvo - 90) / px, (CHAO - 10) / px, 180 / px, 20 / px))
        tela.blit(luz, (0, 0))
        for x, y, f in self.cabecas:  # a plateia mexendo a cabeça
            yy = y + math.sin(t * 0.05 + f) * 2
            pygame.draw.circle(tela, (28, 20, 36), (int(x / px), int(yy / px)), max(2, int(12 / px)))


# =====================================================================
# NAVIO FANTASMA (Cráquen): noite, lua verde, mar, névoa, convés de madeira e velas rasgadas
# =====================================================================
class NavioFantasma(Base):
    nome = "NAVIO FANTASMA"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, 330), (8, 20, 26), (30, 64, 70))
        _brilho(sup, (720, 110), 110, (150, 255, 170), 90)
        pygame.draw.circle(sup, (190, 250, 190), (720, 110), 48)  # a lua verde
        pygame.draw.circle(sup, (160, 220, 160), (704, 98), 9)
        pygame.draw.circle(sup, (160, 220, 160), (736, 124), 6)
        rng = random.Random(13)
        for _ in range(50):
            pygame.draw.circle(sup, (140, 200, 190), (int(rng.uniform(0, LARGURA)), int(rng.uniform(0, 250))), 1)
        _degrade(sup, (0, 300, LARGURA, 60), (20, 50, 60), (12, 34, 44))  # o mar lá no fundo
        # o mastro e as velas rasgadas
        pygame.draw.rect(sup, (50, 36, 26), (LARGURA // 2 - 10, 20, 20, CHAO - 20))
        pygame.draw.rect(sup, (70, 50, 34), (LARGURA // 2 - 6, 20, 6, CHAO - 20))
        pygame.draw.rect(sup, (50, 36, 26), (LARGURA // 2 - 170, 70, 340, 10))
        for y0, larg, alt in ((80, 300, 120), (230, 240, 90)):
            vela = [(LARGURA // 2 - larg // 2, y0), (LARGURA // 2 + larg // 2, y0),
                    (LARGURA // 2 + larg // 2 - 14, y0 + alt), (LARGURA // 2 + 40, y0 + alt - 20),
                    (LARGURA // 2 + 10, y0 + alt + 6), (LARGURA // 2 - 50, y0 + alt - 26),
                    (LARGURA // 2 - larg // 2 + 10, y0 + alt)]
            pygame.draw.polygon(sup, (170, 180, 160), vela)
            pygame.draw.polygon(sup, (110, 120, 104), vela, 3)
            pygame.draw.circle(sup, (40, 50, 50), (LARGURA // 2, y0 + alt // 2), 18)  # a caveira da vela
            pygame.draw.circle(sup, (170, 180, 160), (LARGURA // 2 - 6, y0 + alt // 2 - 3), 4)
            pygame.draw.circle(sup, (170, 180, 160), (LARGURA // 2 + 6, y0 + alt // 2 - 3), 4)
        for x0 in (60, LARGURA - 60):  # as cordas
            pygame.draw.line(sup, (90, 76, 54), (x0, CHAO - 40), (LARGURA // 2, 30), 2)
        # a amurada (corrimão) no fundo e o convés
        pygame.draw.rect(sup, (60, 42, 28), (0, CHAO - 70, LARGURA, 12))
        for x in range(10, LARGURA, 50):
            pygame.draw.rect(sup, (54, 38, 26), (x, CHAO - 60, 10, 60))
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (96, 66, 42), (54, 36, 22))
        for x in range(0, LARGURA, 70):
            pygame.draw.line(sup, (60, 40, 24), (x, CHAO), (x - 10, ALTURA), 2)
        pygame.draw.line(sup, (40, 26, 16), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(21)
        self.nevoa = [[rng.uniform(0, LARGURA), rng.uniform(CHAO - 140, CHAO + 20), rng.uniform(0.3, 0.9),
                       rng.uniform(60, 140)] for _ in range(9)]
        self.lanternas = (120, LARGURA - 120)

    def animar(self, tela, t, px):
        for x in self.lanternas:  # as lanternas com fogo verde
            y = CHAO - 110
            pygame.draw.line(tela, (40, 30, 20), (x / px, (y - 30) / px), (x / px, y / px), 1)
            r = (9 + math.sin(t * 0.3 + x) * 2) / px
            pygame.draw.circle(tela, (120, 255, 150), (int(x / px), int((y + 10) / px)), max(1, int(r)))
            pygame.draw.rect(tela, (30, 24, 18), ((x - 8) / px, (y + 2) / px, 16 / px, 18 / px), 1)
        for i in range(4):  # as ondinhas do mar
            x = ((t * 0.5 + i * 260) % (LARGURA + 100)) - 50
            pygame.draw.line(tela, (60, 110, 120), (x / px, (315 + i * 9) / px), ((x + 40) / px, (315 + i * 9) / px), 1)
        camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        for n in self.nevoa:  # a névoa passando
            n[0] = (n[0] + n[2]) % (LARGURA + 300)
            pygame.draw.ellipse(camada, (170, 230, 220, 34), ((n[0] - 150) / px, n[1] / px, n[3] * 2 / px, n[3] * 0.5 / px))
        tela.blit(camada, (0, 0))


# =====================================================================
# CERCADO DO DESERTO (Magnus): o cercado da base militar onde ele morava (tipo os do Jurassic Park),
# com deserto, um OÁSIS lá atrás (o coqueiro do oásis é um objeto, em x=790) e a cerca elétrica arrebentada
# =====================================================================
class CercadoDeserto(Base):
    nome = "CERCADO DO DESERTO"
    OASIS = 790

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, 300), (90, 160, 220), (250, 210, 150))  # céu quente
        _brilho(sup, (180, 90), 100, (255, 240, 180), 120)
        pygame.draw.circle(sup, (255, 246, 210), (180, 90), 40)  # o sol
        # as dunas lá longe
        for cor, alt, fase in (((222, 176, 120), 250, 0.0), ((210, 160, 100), 280, 1.7)):
            pts = [(x, alt + math.sin(x * 0.006 + fase) * 22) for x in range(0, LARGURA + 20, 20)]
            pygame.draw.polygon(sup, cor, [(0, CHAO)] + pts + [(LARGURA, CHAO)])
        # a base militar lá no fundo (torre de vigia, galpão, antena)
        pygame.draw.rect(sup, (150, 140, 120), (40, 214, 150, 60))
        pygame.draw.polygon(sup, (120, 112, 96), [(36, 216), (115, 196), (194, 216)])
        pygame.draw.rect(sup, (96, 90, 78), (98, 240, 30, 34))
        for x0 in (232, 262):
            pygame.draw.line(sup, (90, 84, 74), (x0, 270), (247, 168), 3)
        pygame.draw.rect(sup, (110, 102, 90), (230, 150, 36, 22))
        pygame.draw.line(sup, (80, 76, 70), (70, 214), (70, 170), 2)
        # o OÁSIS (a água e o mato em volta; o coqueiro é um objeto por cima)
        o = self.OASIS
        pygame.draw.ellipse(sup, (120, 150, 80), (o - 150, CHAO - 66, 300, 44))
        pygame.draw.ellipse(sup, (60, 140, 170), (o - 120, CHAO - 58, 240, 30))
        pygame.draw.ellipse(sup, (120, 200, 220), (o - 80, CHAO - 52, 120, 10))
        for k in range(9):  # o capim do oásis
            x = o - 140 + k * 35
            pygame.draw.line(sup, (70, 120, 50), (x, CHAO - 40), (x - 6, CHAO - 66), 3)
            pygame.draw.line(sup, (90, 140, 60), (x + 4, CHAO - 40), (x + 10, CHAO - 62), 3)
        # a CERCA ELÉTRICA alta (com um buraco arrebentado: foi por onde ele fugiu)
        buraco = (430, 560)
        for x in range(30, LARGURA, 150):
            if buraco[0] - 10 < x < buraco[1]:  # (o poste do buraco foi arrancado)
                continue
            pygame.draw.rect(sup, (70, 72, 78), (x, CHAO - 210, 14, 210))
            pygame.draw.rect(sup, (110, 112, 120), (x + 2, CHAO - 210, 4, 210))
            pygame.draw.rect(sup, (230, 190, 40), (x - 2, CHAO - 216, 18, 8))
        for i in range(7):
            y = CHAO - 200 + i * 26
            for a, b in ((0, buraco[0]), (buraco[1], LARGURA)):
                pygame.draw.line(sup, (54, 56, 60), (a, y), (b, y), 2)
            pygame.draw.line(sup, (54, 56, 60), (buraco[0], y), (buraco[0] + 20 + i * 4, y + 30), 2)  # fios soltos
            pygame.draw.line(sup, (54, 56, 60), (buraco[1], y), (buraco[1] - 16 - i * 3, y + 34), 2)
        # a placa de aviso
        pygame.draw.rect(sup, (230, 190, 40), (300, CHAO - 150, 96, 56))
        pygame.draw.rect(sup, (40, 30, 20), (300, CHAO - 150, 96, 56), 3)
        from efeitos import texto
        texto(sup, "PERIGO", 16, (160, 20, 20), (348, CHAO - 136))
        texto(sup, "EXPERIMENTO 13", 11, (40, 30, 20), (348, CHAO - 112))
        # o chão de areia com pegadas de raptor
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (226, 184, 124), (184, 140, 86))
        pygame.draw.line(sup, (160, 120, 70), (0, CHAO), (LARGURA, CHAO), 3)
        for k in range(6):
            x, y = 470 + k * 60, CHAO + 18 + (k % 2) * 16
            for a in (-0.5, 0, 0.5):
                pygame.draw.line(sup, (170, 128, 78), (x, y), (x + 12 * math.cos(a), y + 12 * math.sin(a)), 3)
        return sup

    def animar(self, tela, t, px):
        if (t // 6) % 2:  # a luz vermelha da torre piscando
            pygame.draw.circle(tela, (255, 50, 40), (int(248 / px), int(146 / px)), max(1, int(4 / px)))
        if t % 90 < 8:  # faísca nos fios arrebentados da cerca
            x, y = 430 + 30, CHAO - 150
            for k in range(4):
                a = t * 1.7 + k * 1.6
                pygame.draw.line(tela, (180, 230, 255), (x / px, y / px),
                                 ((x + math.cos(a) * 14) / px, (y + math.sin(a) * 14) / px), 1)
        for k in range(3):  # o brilho da água do oásis
            x = self.OASIS - 60 + ((t * 0.4 + k * 50) % 120)
            pygame.draw.line(tela, (220, 250, 255), (x / px, (CHAO - 46 + k * 4) / px), ((x + 10) / px, (CHAO - 46 + k * 4) / px), 1)


# =====================================================================
# PRAIA DA ILHA (Sphyrus): a praia com o laboratório de onde ele fugiu lá no fundo; o mar fica à DIREITA
# (as ondas gigantes do clima vêm de lá) e o espaço em x=180 é da boia salva-vidas (objeto)
# =====================================================================
class PraiaIlha(Base):
    nome = "PRAIA DA ILHA"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, 300), (80, 170, 230), (200, 236, 250))  # céu
        _brilho(sup, (760, 80), 90, (255, 250, 210), 120)
        pygame.draw.circle(sup, (255, 252, 230), (760, 80), 34)  # o sol
        for cx, cy, w in ((160, 70, 120), (420, 50, 160), (620, 110, 100)):  # nuvens
            for k in range(3):
                pygame.draw.ellipse(sup, (250, 252, 255), (cx + k * w // 4, cy - (k % 2) * 10, w // 2, 30))
        # a ILHA lá no fundo com o LABORATÓRIO no morro
        pygame.draw.polygon(sup, (70, 120, 70), [(120, 300), (230, 190), (330, 170), (450, 200), (560, 300)])
        pygame.draw.polygon(sup, (90, 140, 80), [(170, 300), (260, 210), (340, 196), (420, 220), (500, 300)])
        pygame.draw.rect(sup, (200, 204, 208), (276, 150, 110, 52))  # o prédio
        pygame.draw.rect(sup, (150, 156, 164), (276, 150, 110, 52), 3)
        pygame.draw.rect(sup, (170, 176, 184), (300, 128, 40, 24))
        for i in range(4):  # janelas
            pygame.draw.rect(sup, (60, 90, 120), (286 + i * 25, 162, 14, 10))
        pygame.draw.rect(sup, (40, 40, 48), (340, 178, 22, 24))  # o portão arrombado
        pygame.draw.line(sup, (150, 156, 164), (340, 178), (330, 202), 3)
        pygame.draw.line(sup, (120, 120, 130), (366, 128), (366, 92), 2)  # antena
        pygame.draw.circle(sup, (220, 60, 60), (366, 92), 3)
        for x0 in (400, 430, 460):  # o tanque de água (de onde ele saiu)
            pygame.draw.line(sup, (120, 130, 140), (x0, 202), (x0 + 6, 188), 2)
        pygame.draw.ellipse(sup, (140, 200, 220), (396, 176, 76, 16))
        # o MAR (à direita) e a areia
        _degrade(sup, (0, 300, LARGURA, 70), (40, 140, 200), (60, 170, 210))
        pygame.draw.polygon(sup, (226, 206, 150), [(0, 330), (420, 330), (600, 370), (620, CHAO), (0, CHAO)])
        pygame.draw.polygon(sup, (70, 180, 210), [(600, 370), (LARGURA, 340), (LARGURA, CHAO), (640, CHAO)])
        for k in range(5):  # a espuma na beira
            y = 380 + k * 22
            pygame.draw.line(sup, (240, 250, 255), (612 + k * 4, y), (680 + k * 6, y - 4), 3)
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (232, 212, 156), (196, 172, 116))
        pygame.draw.line(sup, (170, 146, 96), (0, CHAO), (LARGURA, CHAO), 3)
        rng = random.Random(14)
        for _ in range(30):  # conchinhas e pedrinhas
            x, y = rng.uniform(0, LARGURA), rng.uniform(CHAO + 8, ALTURA - 6)
            pygame.draw.circle(sup, rng.choice(((250, 230, 220), (180, 160, 120), (240, 200, 190))), (int(x), int(y)), 2)
        # uma placa caída do laboratório na areia
        pygame.draw.polygon(sup, (200, 200, 200), [(470, CHAO - 6), (540, CHAO - 14), (544, CHAO - 2), (474, CHAO + 4)])
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(15)
        self.gaivotas = [[rng.uniform(0, LARGURA), rng.uniform(60, 160), rng.uniform(0.5, 1.1)] for _ in range(3)]

    def animar(self, tela, t, px):
        for i in range(4):  # as ondinhas do mar
            x = 640 + ((t * 0.7 + i * 80) % 300)
            y = 360 + i * 24
            pygame.draw.line(tela, (230, 248, 255), (x / px, y / px), ((x + 30) / px, (y - 2) / px), 1)
        for g in self.gaivotas:  # gaivotas
            g[0] = (g[0] + g[2]) % (LARGURA + 40)
            asa = math.sin(t * 0.25 + g[1]) * 4
            x, y = g[0] / px, g[1] / px
            pygame.draw.lines(tela, (60, 60, 70), False, [(x - 6 / px, y - asa / px), (x, y), (x + 6 / px, y - asa / px)], 1)
        if (t // 20) % 2:  # a luz da antena do laboratório
            pygame.draw.circle(tela, (255, 80, 80), (int(366 / px), int(92 / px)), max(1, int(3 / px)))


# =====================================================================
# MONTANHA NEVADA (Frigantus): uma montanha MUITO alta, toda nevada, com pinheiros e neve caindo
# (o espaço em x=790 é da placa PERIGO: AVALANCHE, que é um objeto)
# =====================================================================
class MontanhaNevada(Base):
    nome = "MONTANHA NEVADA"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, 320), (120, 170, 220), (220, 236, 250))  # céu frio
        # o PICO enorme lá atrás (passa do alto da tela)
        pico = [(80, 330), (330, 70), (430, -40), (520, 40), (640, 120), (900, 330)]
        pygame.draw.polygon(sup, (150, 166, 190), pico)
        neve = [(250, 160), (330, 70), (430, -40), (520, 40), (590, 92), (540, 120), (480, 96), (420, 130),
                (370, 110), (310, 150)]
        pygame.draw.polygon(sup, (246, 250, 255), neve)
        pygame.draw.line(sup, (200, 214, 232), (430, -40), (420, 130), 3)
        # as montanhas do meio
        for cor, pts in (((170, 186, 208), [(-40, 330), (140, 190), (300, 330)]),
                         ((176, 192, 214), [(620, 330), (820, 170), (1000, 330)])):
            pygame.draw.polygon(sup, cor, pts)
            topo = pts[1]
            pygame.draw.polygon(sup, (246, 250, 255), [(topo[0] - 50, topo[1] + 56), topo, (topo[0] + 50, topo[1] + 56),
                                                       (topo[0] + 10, topo[1] + 44), (topo[0] - 16, topo[1] + 52)])
        # a encosta de neve e os pinheiros
        _degrade(sup, (0, 300, LARGURA, CHAO - 300), (226, 236, 248), (200, 214, 234))
        rnd = random.Random(31)
        for i in range(16):
            x = rnd.uniform(0, LARGURA)
            if 700 < x < 880:
                continue  # (lugar da placa)
            base = rnd.uniform(330, CHAO - 50)
            h = rnd.uniform(40, 90) * (0.6 + (base - 300) / 300)
            for k in range(3):  # o pinheiro em camadas, com neve em cima
                y = base - k * h * 0.28
                w = h * (0.42 - k * 0.1)
                pygame.draw.polygon(sup, (34, 70, 56), [(x - w, y), (x, y - h * 0.5), (x + w, y)])
                pygame.draw.polygon(sup, (240, 246, 252), [(x - w * 0.4, y - h * 0.32), (x, y - h * 0.5), (x + w * 0.4, y - h * 0.32)])
            pygame.draw.rect(sup, (70, 50, 34), (x - 3, base, 6, 10))
        # o chão de neve
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (244, 248, 255), (206, 218, 236))
        pygame.draw.line(sup, (180, 196, 220), (0, CHAO), (LARGURA, CHAO), 3)
        for i in range(12):  # montinhos e pegadas
            x = rnd.uniform(0, LARGURA)
            pygame.draw.ellipse(sup, (224, 232, 246), (x, CHAO + rnd.uniform(6, 40), 60, 12))
        return sup

    def __init__(self):
        super().__init__()
        rnd = random.Random(32)
        self.flocos = [[rnd.uniform(0, LARGURA), rnd.uniform(0, ALTURA), rnd.uniform(0.6, 1.6), rnd.uniform(0, 6)]
                       for _ in range(70)]

    def animar(self, tela, t, px):
        for f in self.flocos:  # a neve caindo
            f[1] = (f[1] + f[2]) % ALTURA
            x = (f[0] + math.sin(t * 0.03 + f[3]) * 12) % LARGURA
            pygame.draw.circle(tela, (255, 255, 255), (int(x / px), int(f[1] / px)), max(1, int(2 / px)))


# =====================================================================
# MONTE KARASUMA (Inazumaneko, v3.0): o alto de uma montanha SEM neve, acima das nuvens, onde fica o CAMPO DE
# TREINAMENTO dele: o chão de terra batida, os bonecos de palha cortados, a cerca de bambu, o portal vermelho,
# os estandartes e as árvores de folha vermelha (as folhas caindo)
# =====================================================================
class MonteKarasuma(Base):
    nome = "MONTE KARASUMA"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, 300), (96, 150, 210), (250, 214, 170))  # céu de fim de tarde, bem alto
        _brilho(sup, (700, 150), 90, (255, 240, 200), 120)
        pygame.draw.circle(sup, (255, 246, 214), (700, 150), 34)  # o sol
        # os PICOS de rocha lá longe (montanhas pontudas, sem neve)
        for cor, pts in (((140, 130, 150), [(-40, 300), (90, 150), (160, 210), (240, 120), (360, 300)]),
                         ((150, 138, 156), [(560, 300), (690, 180), (760, 230), (860, 110), (1000, 300)])):
            pygame.draw.polygon(sup, cor, pts)
            for i in range(len(pts) - 2):  # (o lado da sombra)
                a, b = pts[i + 1], pts[i + 2]
                if b[1] > a[1]:
                    pygame.draw.polygon(sup, tuple(int(v * 0.82) for v in cor), [a, b, (a[0] + 10, 300)])
        # o MAR DE NUVENS (estamos acima delas)
        rnd = random.Random(41)
        for i in range(22):
            x = rnd.uniform(-60, LARGURA)
            y = rnd.uniform(250, 300)
            pygame.draw.ellipse(sup, (252, 236, 226), (x, y, rnd.uniform(90, 180), rnd.uniform(26, 44)))
        _degrade(sup, (0, 290, LARGURA, 20), (250, 232, 222), (240, 220, 210))
        # o CUME onde fica o campo (a rocha verde-musgo, com degraus)
        topo = [(0, 330), (120, 310), (260, 318), (420, 300), (600, 312), (780, 302), (960, 320), (960, CHAO), (0, CHAO)]
        pygame.draw.polygon(sup, (92, 112, 80), topo)
        _degrade(sup, (0, 340, LARGURA, CHAO - 340), (104, 124, 88), (84, 96, 70))
        for i in range(14):  # as pedras da encosta
            x, y = rnd.uniform(0, LARGURA), rnd.uniform(330, CHAO - 60)
            pygame.draw.ellipse(sup, (120, 120, 112), (x, y, rnd.uniform(24, 60), rnd.uniform(10, 22)))
        # as ÁRVORES de folha vermelha (bordos) dos lados
        for x, base, h in ((70, CHAO - 40, 170), (900, CHAO - 50, 150), (230, 330, 90), (820, 326, 80)):
            pygame.draw.line(sup, (70, 44, 34), (x, base), (x - 6, base - h * 0.6), max(4, int(h / 14)))
            pygame.draw.line(sup, (70, 44, 34), (x - 4, base - h * 0.4), (x + h * 0.25, base - h * 0.7), max(3, int(h / 20)))
            for k in range(7):
                a = k * math.tau / 7
                pygame.draw.circle(sup, (200 - k % 3 * 20, 50 + k % 2 * 20, 40),
                                   (int(x + math.cos(a) * h * 0.26), int(base - h * 0.72 + math.sin(a) * h * 0.18)), int(h * 0.2))
        # o PORTAL vermelho (torii) no fundo do campo
        tx, tb = 480, CHAO - 120
        for dx in (-70, 70):
            pygame.draw.rect(sup, (60, 20, 20), (tx + dx - 9, tb - 120, 18, 124))
            pygame.draw.rect(sup, (200, 50, 40), (tx + dx - 7, tb - 118, 14, 120))
        pygame.draw.polygon(sup, (60, 20, 20), [(tx - 112, tb - 132), (tx + 112, tb - 132), (tx + 100, tb - 120), (tx - 100, tb - 120)])
        pygame.draw.polygon(sup, (40, 30, 30), [(tx - 118, tb - 142), (tx + 118, tb - 142), (tx + 110, tb - 132), (tx - 110, tb - 132)])
        pygame.draw.rect(sup, (200, 50, 40), (tx - 92, tb - 108, 184, 10))
        pygame.draw.rect(sup, (40, 30, 30), (tx - 14, tb - 132, 28, 24))  # a plaquinha do meio (sem letras)
        pygame.draw.rect(sup, (220, 190, 110), (tx - 10, tb - 128, 20, 16))
        # os ESTANDARTES (bandeiras compridas com o símbolo do raio)
        for bx in (300, 660):
            pygame.draw.line(sup, (60, 40, 30), (bx, CHAO), (bx, CHAO - 210), 5)
            pygame.draw.rect(sup, (40, 30, 70), (bx + 3, CHAO - 206, 30, 110))
            pygame.draw.polygon(sup, (250, 210, 70), [(bx + 22, CHAO - 190), (bx + 12, CHAO - 158), (bx + 20, CHAO - 158),
                                                      (bx + 10, CHAO - 126), (bx + 26, CHAO - 166), (bx + 18, CHAO - 166)])
        # a CERCA DE BAMBU no fundo do campo
        for i in range(30):
            x = 120 + i * 24
            if 400 < x < 560:
                continue  # (o portal)
            pygame.draw.rect(sup, (150, 160, 80), (x, CHAO - 70, 9, 70))
            pygame.draw.line(sup, (110, 120, 56), (x, CHAO - 46), (x + 9, CHAO - 46), 2)
        pygame.draw.line(sup, (110, 120, 56), (120, CHAO - 60), (840, CHAO - 60), 4)
        # os BONECOS DE PALHA de treino (cortados em diagonal)
        for bx, alto in ((170, 96), (360, 80), (610, 88)):
            pygame.draw.line(sup, (90, 60, 30), (bx, CHAO), (bx, CHAO - alto - 20), 5)
            pygame.draw.rect(sup, (200, 170, 90), (bx - 12, CHAO - alto, 24, alto - 6), border_radius=6)
            for k in range(3):
                pygame.draw.line(sup, (150, 110, 50), (bx - 12, CHAO - alto + 14 + k * 20), (bx + 12, CHAO - alto + 14 + k * 20), 3)
            pygame.draw.line(sup, (90, 50, 30), (bx - 14, CHAO - alto + 8), (bx + 14, CHAO - alto + 30), 2)  # o corte
        # o CHÃO de terra batida do campo (com as marcas de passos e as pedras da borda)
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (176, 146, 106), (130, 104, 74))
        pygame.draw.line(sup, (96, 74, 50), (0, CHAO), (LARGURA, CHAO), 3)
        for i in range(16):
            x = rnd.uniform(0, LARGURA)
            pygame.draw.ellipse(sup, (150, 122, 86), (x, CHAO + rnd.uniform(8, 44), rnd.uniform(30, 70), 8))
        for x in range(0, LARGURA, 64):  # as pedras da borda
            pygame.draw.ellipse(sup, (120, 112, 100), (x + rnd.uniform(-6, 6), CHAO - 6, 40, 12))
        return sup

    def __init__(self):
        super().__init__()
        rnd = random.Random(42)
        self.folhas = [[rnd.uniform(0, LARGURA), rnd.uniform(0, ALTURA), rnd.uniform(0.5, 1.2), rnd.uniform(0, 6)]
                       for _ in range(26)]

    def animar(self, tela, t, px):
        for f in self.folhas:  # as FOLHAS VERMELHAS caindo, girando
            f[1] = (f[1] + f[2]) % ALTURA
            x = (f[0] + math.sin(t * 0.025 + f[3]) * 30 + t * 0.3) % LARGURA
            a = t * 0.08 + f[3]
            r = max(1, int(4 / px))
            cx, cy = x / px, f[1] / px
            pygame.draw.polygon(tela, (210, 70, 40), [(cx + math.cos(a) * r * 1.6, cy + math.sin(a) * r * 0.6),
                                                      (cx - math.sin(a) * r * 0.6, cy + math.cos(a) * r),
                                                      (cx - math.cos(a) * r * 1.6, cy - math.sin(a) * r * 0.6),
                                                      (cx + math.sin(a) * r * 0.6, cy - math.cos(a) * r)])


# =====================================================================
# CAVERNA DOS MORCEGOS (Nocturnus, v3.0): uma caverna funda e escura — estalactites no teto com MORCEGOS pendurados
# (balançando, piscando os olhinhos), CRISTAIS ROXOS brilhando nas paredes, poças que refletem, e a luz fraquinha
# que entra por uma fresta lá no alto
# =====================================================================
class CavernaMorcegos(Base):
    nome = "CAVERNA DOS MORCEGOS"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, ALTURA), (14, 10, 24), (40, 28, 52))
        rnd = random.Random(51)
        # a FRESTA lá no alto (o feixe de luz da lua entrando)
        pygame.draw.polygon(sup, (60, 70, 110), [(560, 0), (610, 0), (700, CHAO), (470, CHAO)])
        _brilho(sup, (585, 10), 60, (150, 170, 230), 120)
        # as PAREDES de rocha do fundo (camadas)
        for cor, base_y, n in (((34, 26, 46), 260, 9), ((46, 34, 58), 330, 7)):
            pts = [(0, ALTURA), (0, base_y)]
            for i in range(n + 1):
                pts.append((i * LARGURA / n, base_y + rnd.uniform(-60, 40)))
            pts += [(LARGURA, base_y), (LARGURA, ALTURA)]
            pygame.draw.polygon(sup, cor, pts)
        # os CRISTAIS ROXOS (aglomerados brilhando nas paredes)
        for cx, cy, tam in ((110, 330, 1.2), (300, 380, 0.8), (720, 360, 1.0), (880, 300, 1.3), (500, 400, 0.6)):
            _brilho(sup, (cx, cy - 20 * tam), int(70 * tam), (170, 90, 230), 90)
            for k in range(5):
                a = -math.pi / 2 + (k - 2) * 0.35
                h = (40 + (k % 2) * 22) * tam
                bx, by = cx + (k - 2) * 9 * tam, cy
                pts = [(bx - 7 * tam, by), (bx + math.cos(a) * h - 4 * tam, by + math.sin(a) * h),
                       (bx + math.cos(a) * (h + 10 * tam), by + math.sin(a) * (h + 10 * tam)),
                       (bx + math.cos(a) * h + 4 * tam, by + math.sin(a) * h), (bx + 7 * tam, by)]
                pygame.draw.polygon(sup, (120, 60, 180), pts)
                pygame.draw.polygon(sup, (200, 150, 255), pts[1:4])
        # o TETO com as ESTALACTITES
        pygame.draw.rect(sup, (20, 14, 30), (0, 0, LARGURA, 50))
        for i in range(24):
            x = i * 42 + rnd.uniform(-10, 10)
            h = rnd.uniform(40, 130)
            pygame.draw.polygon(sup, (30, 22, 42), [(x - 18, 40), (x + 18, 40), (x + 2, 40 + h)])
            pygame.draw.polygon(sup, (44, 34, 58), [(x - 6, 40), (x + 4, 40), (x + 2, 40 + h * 0.8)])
        # as ESTALAGMITES no chão (dos lados)
        for x, h in ((40, 110), (90, 70), (870, 120), (930, 80), (250, 50), (760, 60)):
            pygame.draw.polygon(sup, (36, 28, 48), [(x - 26, CHAO), (x + 26, CHAO), (x + 3, CHAO - h)])
            pygame.draw.polygon(sup, (54, 42, 68), [(x - 6, CHAO), (x + 6, CHAO), (x + 2, CHAO - h * 0.8)])
        # o CHÃO de pedra úmida, com as POÇAS refletindo
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (52, 42, 62), (26, 20, 34))
        pygame.draw.line(sup, (70, 58, 84), (0, CHAO), (LARGURA, CHAO), 3)
        for x, w in ((180, 120), (620, 160), (420, 80)):
            pygame.draw.ellipse(sup, (40, 50, 90), (x, CHAO + 14, w, 16))
            pygame.draw.ellipse(sup, (90, 110, 170), (x + w * 0.2, CHAO + 17, w * 0.4, 4))
        for i in range(14):  # as pedrinhas
            pygame.draw.ellipse(sup, (66, 56, 78), (rnd.uniform(0, LARGURA), CHAO + rnd.uniform(6, 48), rnd.uniform(10, 26), 6))
        return sup

    def __init__(self):
        super().__init__()
        rnd = random.Random(52)
        self.morcegos = [(rnd.uniform(30, LARGURA - 30), rnd.uniform(44, 70), rnd.uniform(0, 6)) for _ in range(9)]
        self.gotas = [[rnd.uniform(0, LARGURA), rnd.uniform(0, 300), rnd.uniform(0, 200)] for _ in range(6)]

    def animar(self, tela, t, px):
        for x, y, f in self.morcegos:  # os MORCEGOS pendurados no teto (de cabeça pra baixo, balançando)
            bx = x + math.sin(t * 0.04 + f) * 2
            cx, cy = bx / px, y / px
            r = max(1, 5 / px)
            pygame.draw.line(tela, (20, 14, 26), (cx, cy - 6 / px), (cx, cy), max(1, int(1 / px)))
            pygame.draw.ellipse(tela, (16, 10, 22), (cx - r, cy, r * 2, r * 2.6))
            if (t // 40 + int(f * 10)) % 7:  # os olhinhos (às vezes piscam)
                pygame.draw.circle(tela, (255, 70, 70), (int(cx - r * 0.4), int(cy + r * 1.9)), max(1, int(1 / px)))
                pygame.draw.circle(tela, (255, 70, 70), (int(cx + r * 0.4), int(cy + r * 1.9)), max(1, int(1 / px)))
        for g in self.gotas:  # as GOTAS pingando do teto
            u = (t + g[2]) % 160
            if u < 60:
                pygame.draw.circle(tela, (150, 170, 220), (int(g[0] / px), int((90 + u * (CHAO - 90) / 60) / px)), max(1, int(2 / px)))


# =====================================================================
# FLORESTA ANTIGA (Silvanus, v3.0): árvores GIGANTES (troncos largos com raízes enormes), RAIOS DE SOL entrando
# pela copa, e RUÍNAS cobertas de musgo (um arco quebrado e pilares) com RUNAS que brilham devagar
# =====================================================================
RUNAS_FLORESTA = ((392, 300), (568, 300), (480, 236), (120, 462), (790, 457))  # (onde as runas acendem)


def _runa(sup, x, y, tam, cor, larg=2):
    """Uma runa simples (traços retos, tipo letra antiga)."""
    pygame.draw.line(sup, cor, (x, y - tam), (x, y + tam), larg)
    pygame.draw.line(sup, cor, (x, y - tam * 0.4), (x + tam * 0.6, y - tam), larg)
    pygame.draw.line(sup, cor, (x, y + tam * 0.1), (x - tam * 0.6, y - tam * 0.5), larg)


class FlorestaAntiga(Base):
    nome = "FLORESTA ANTIGA"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (150, 190, 120), (34, 66, 44))  # a luz verde-dourada lá de cima
        rnd = random.Random(61)
        # as árvores do FUNDO (troncos enormes, apagados pela névoa)
        for x, w, cor in ((60, 70, (92, 124, 92)), (250, 54, (96, 128, 96)), (700, 60, (92, 124, 92)),
                          (900, 80, (88, 120, 88)), (470, 40, (100, 134, 100))):
            pygame.draw.rect(sup, cor, (x - w / 2, 0, w, CHAO))
            pygame.draw.polygon(sup, cor, [(x - w / 2 - 30, CHAO), (x - w / 2, CHAO - 60), (x + w / 2, CHAO - 60),
                                           (x + w / 2 + 30, CHAO)])
        # a COPA (folhagem lá no alto, escura, com buracos de luz)
        for i in range(30):
            cx, cy = rnd.uniform(-40, LARGURA + 40), rnd.uniform(-30, 70)
            pygame.draw.circle(sup, (30, 62, 36), (int(cx), int(cy)), int(rnd.uniform(40, 80)))
        for i in range(10):
            pygame.draw.circle(sup, (44, 84, 46), (int(rnd.uniform(0, LARGURA)), int(rnd.uniform(40, 100))),
                               int(rnd.uniform(26, 50)))
        # as RUÍNAS: o ARCO de pedra quebrado no meio, os pilares e os blocos caídos (tudo com musgo)
        pedra, sombra, musgo = (128, 132, 116), (88, 92, 80), (70, 120, 52)
        for px_, topo in ((392, 220), (568, 250)):  # os dois pilares do arco
            pygame.draw.rect(sup, sombra, (px_ - 34, topo, 68, CHAO - topo))
            pygame.draw.rect(sup, pedra, (px_ - 28, topo, 56, CHAO - topo))
            for k in range(int((CHAO - topo) / 36)):  # as pedras (as juntas)
                pygame.draw.line(sup, sombra, (px_ - 28, topo + k * 36), (px_ + 28, topo + k * 36), 2)
        for cor, r_fora, r_dentro in ((sombra, 122, 82), (pedra, 116, 88)):  # o ARCO (quebrou antes de chegar no pilar direito)
            fora = [(480 + math.cos(a) * r_fora, 232 - math.sin(a) * r_fora * 0.8) for a in
                    [math.pi - k * (math.pi - 0.75) / 16 for k in range(17)]]
            dentro = [(480 + math.cos(a) * r_dentro, 232 - math.sin(a) * r_dentro * 0.8) for a in
                      [0.75 + k * (math.pi - 0.75) / 16 for k in range(17)]]
            quebra = [(fora[-1][0] - 4, fora[-1][1] + 8), (fora[-1][0] + 6, fora[-1][1] + 16)]  # a ponta lascada
            pygame.draw.polygon(sup, cor, fora + quebra + dentro)
        for k in range(1, 6):  # as juntas das pedras do arco
            a = math.pi - k * (math.pi - 0.75) / 6
            pygame.draw.line(sup, sombra, (480 + math.cos(a) * 88, 232 - math.sin(a) * 70),
                             (480 + math.cos(a) * 116, 232 - math.sin(a) * 93), 2)
        for x, y, w, h in ((340, 214, 110, 16), (520, 246, 90, 12), (370, 300, 40, 50), (600, 330, 30, 60)):  # o musgo
            pygame.draw.ellipse(sup, musgo, (x, y, w, h))
        for x, w, h in ((120, 70, 40), (790, 64, 50), (660, 40, 22)):  # os blocos caídos
            pygame.draw.rect(sup, sombra, (x - w / 2, CHAO - h, w, h), border_radius=6)
            pygame.draw.rect(sup, pedra, (x - w / 2 + 4, CHAO - h + 4, w - 8, h - 8), border_radius=4)
            pygame.draw.ellipse(sup, musgo, (x - w / 2, CHAO - h - 6, w, 14))
        for x, y in RUNAS_FLORESTA:  # as runas apagadas (o brilho é no animar)
            _runa(sup, x, y, 12, (80, 96, 80), 3)
        # as ÁRVORES GIGANTES da frente (dos lados), com RAÍZES enormes
        for x, w, lado in ((-10, 150, 1), (LARGURA + 10, 170, -1)):
            casca, escura, clara = (78, 58, 40), (50, 36, 26), (104, 80, 56)
            pygame.draw.rect(sup, escura, (x - w / 2, 0, w, CHAO))
            pygame.draw.rect(sup, casca, (x - w / 2 + 8, 0, w - 16, CHAO))
            for k in range(5):  # as rugas da casca
                gx = x - w / 2 + 20 + k * (w - 40) / 4
                pygame.draw.line(sup, escura, (gx, 0), (gx + rnd.uniform(-10, 10), CHAO), 3)
            pygame.draw.line(sup, clara, (x + lado * (w / 2 - 14), 0), (x + lado * (w / 2 - 14), CHAO), 4)
            for k in range(3):  # as raízes saindo pro chão
                rx = x + lado * (w / 2 + 10 + k * 46)
                pygame.draw.polygon(sup, escura, [(x + lado * (w / 2 - 20), CHAO - 120 + k * 30), (rx + lado * 40, CHAO),
                                                  (rx - lado * 10, CHAO)])
                pygame.draw.polygon(sup, casca, [(x + lado * (w / 2 - 20), CHAO - 112 + k * 30), (rx + lado * 30, CHAO),
                                                 (rx, CHAO)])
            for k in range(4):  # musgo no tronco
                pygame.draw.ellipse(sup, musgo, (x - w / 2 + rnd.uniform(0, w - 40), rnd.uniform(100, 400), 40, 16))
        # os RAIOS DE SOL entrando pela copa (faixas de luz transparentes)
        luz = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        for x0, larg in ((300, 60), (470, 40), (640, 80), (760, 34)):
            pygame.draw.polygon(luz, (255, 240, 170, 44), [(x0, 0), (x0 + larg, 0), (x0 + larg - 150, CHAO),
                                                          (x0 - 190, CHAO)])
        sup.blit(luz, (0, 0))
        # o CHÃO da floresta: terra escura com musgo, samambaias e cogumelos
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (60, 92, 44), (30, 46, 26))
        pygame.draw.line(sup, (90, 132, 60), (0, CHAO), (LARGURA, CHAO), 3)
        for i in range(26):  # tufos de musgo
            pygame.draw.ellipse(sup, (76, 120, 52), (rnd.uniform(0, LARGURA), CHAO + rnd.uniform(4, 44),
                                                     rnd.uniform(16, 40), 8))
        for x in (40, 230, 330, 620, 720, 930):  # as samambaias
            for k in range(5):
                a = math.pi + 0.35 + k * 0.6
                pygame.draw.line(sup, (54, 104, 46), (x, CHAO + 2), (x + math.cos(a) * 34, CHAO + 2 + math.sin(a) * 26), 4)
        for x, cor in ((260, (200, 70, 50)), (276, (220, 90, 60)), (700, (230, 200, 140)), (850, (200, 70, 50))):  # cogumelos
            pygame.draw.rect(sup, (230, 224, 200), (x - 2, CHAO - 12, 5, 12))
            pygame.draw.ellipse(sup, cor, (x - 9, CHAO - 18, 19, 10))
            pygame.draw.circle(sup, (250, 246, 230), (x - 3, CHAO - 14), 2)
        return sup

    def __init__(self):
        super().__init__()
        rnd = random.Random(62)
        self.poeira = [[rnd.uniform(200, 800), rnd.uniform(60, CHAO - 20), rnd.uniform(0, 6)] for _ in range(26)]
        self.folhas = [[rnd.uniform(0, LARGURA), rnd.uniform(0, ALTURA), rnd.uniform(0.5, 1.1), rnd.uniform(0, 6)]
                       for _ in range(6)]

    def animar(self, tela, t, px):
        for i, (x, y) in enumerate(RUNAS_FLORESTA):  # as RUNAS acendendo e apagando devagar (uma de cada vez)
            k = max(0.0, math.sin(t * 0.025 - i * 1.3))
            if k > 0.05:
                cor = (int(80 + 120 * k), int(96 + 159 * k), int(80 + 120 * k))
                pygame.draw.circle(tela, mistura_cor((70, 90, 70), (120, 220, 140), k), (int(x / px), int(y / px)),
                                   max(1, int(17 / px)), max(1, int(2 / px)))  # o círculo de luz em volta
                _runa(tela, x / px, y / px, 12 / px, cor, max(1, int(3 / px)))
        for p in self.poeira:  # o PÓ DE LUZ flutuando dentro dos raios de sol
            x = p[0] + math.sin(t * 0.01 + p[2]) * 30
            y = (p[1] - t * 0.15) % (CHAO - 60) + 40
            if (t // 20 + int(p[2] * 7)) % 5:
                pygame.draw.circle(tela, (255, 246, 190), (int(x / px), int(y / px)), max(1, int(2 / px)))
        for f in self.folhas:  # as FOLHAS caindo devagar, girando
            f[1] = (f[1] + f[2]) % ALTURA
            x = (f[0] + math.sin(t * 0.02 + f[3]) * 40) % LARGURA
            a = t * 0.06 + f[3]
            r = max(1, int(4 / px))
            cx, cy = x / px, f[1] / px
            pygame.draw.polygon(tela, (110, 160, 60), [(cx + math.cos(a) * r * 1.6, cy + math.sin(a) * r * 0.6),
                                                       (cx - math.sin(a) * r * 0.6, cy + math.cos(a) * r),
                                                       (cx - math.cos(a) * r * 1.6, cy - math.sin(a) * r * 0.6),
                                                       (cx + math.sin(a) * r * 0.6, cy - math.cos(a) * r)])


# =====================================================================
# CAMPO GIGANTE (Katchade, v4.0, ideia do Gomes): a luta é do tamanho de um INSETO — folhas de grama GIGANTES
# balançando, trevos do tamanho de guarda-chuva, um DENTE-DE-LEÃO enorme soltando sementes, gotas de orvalho
# brilhando, uma joaninha e uma formiga lá no fundo, e a ORQUÍDEA rosa gigante (a casa do Katchade) no meio
# =====================================================================
LAMINAS_CAMPO = [  # (x da base, altura, curva, largura, cor) — as folhas de grama da FRENTE que balançam
    (18, 470, 70, 34, (74, 150, 60)), (96, 380, -50, 26, (92, 170, 70)), (870, 450, -80, 32, (70, 144, 56)),
    (930, 360, 40, 26, (96, 176, 72)), (300, 210, 30, 18, (104, 182, 80)), (650, 240, -36, 20, (100, 178, 76)),
]


def _lamina(sup, x, h, curva, larg, cor, balanco=0.0, escala=1.0):
    """Uma folha de grama gigante: base larga no chão, sobe curvando e termina pontuda."""
    pts_e, pts_d = [], []
    n = 10
    for k in range(n + 1):
        f = k / n
        dx = (curva + balanco) * f * f
        y = CHAO - h * f
        w = larg * (1 - f) ** 0.8 / 2
        pts_e.append(((x + dx - w) / escala, y / escala))
        pts_d.append(((x + dx + w) / escala, y / escala))
    pygame.draw.polygon(sup, mistura_cor(cor, (20, 40, 20), 0.35), pts_e + pts_d[::-1])
    meio = [((a[0] + b[0]) / 2, a[1]) for a, b in zip(pts_e, pts_d)]
    pygame.draw.polygon(sup, cor, pts_e[:-1] + meio[::-1][1:])
    pygame.draw.lines(sup, mistura_cor(cor, (230, 255, 200), 0.3), False, meio[:-1], max(1, int(2 / escala)))


class CampoGigante(Base):
    nome = "CAMPO GIGANTE"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (150, 210, 250), (214, 238, 220))  # o céu claro de manhã
        rnd = random.Random(91)
        # nuvens fofas
        for cx, cy, r in ((150, 70, 34), (190, 62, 40), (230, 74, 30), (700, 50, 30), (740, 44, 38), (780, 56, 28)):
            pygame.draw.circle(sup, (250, 252, 255), (cx, cy), r)
        # o MATO lá do fundo (silhuetas de folhas gigantes, apagadas pela distância)
        for i in range(34):
            x = rnd.uniform(-20, LARGURA + 20)
            _lamina(sup, x, rnd.uniform(220, 380), rnd.uniform(-60, 60), rnd.uniform(16, 30),
                    mistura_cor((110, 170, 110), (190, 226, 210), rnd.uniform(0.3, 0.6)))
        # o DENTE-DE-LEÃO gigante (caule fino, a bola branca de sementes lá em cima)
        dx, dy = 790, 120
        pygame.draw.line(sup, (96, 150, 70), (dx + 30, CHAO), (dx, dy), 8)
        for k in range(46):
            a = k * math.tau / 46
            r = 58 + (k % 3) * 4
            pygame.draw.line(sup, (236, 240, 236), (dx, dy), (dx + math.cos(a) * r, dy + math.sin(a) * r), 2)
            pygame.draw.circle(sup, (255, 255, 255), (int(dx + math.cos(a) * r), int(dy + math.sin(a) * r)), 4)
        pygame.draw.circle(sup, (200, 190, 150), (dx, dy), 10)
        # a JOANINHA numa folha do fundo
        jx, jy = 200, 250
        _lamina(sup, 190, CHAO - 238, 30, 26, (110, 176, 90))
        pygame.draw.ellipse(sup, (210, 40, 40), (jx - 18, jy - 12, 36, 24))
        pygame.draw.line(sup, (30, 20, 20), (jx, jy - 12), (jx, jy + 12), 2)
        for px_, py_ in ((-9, -4), (8, -3), (-6, 6), (7, 6)):
            pygame.draw.circle(sup, (30, 20, 20), (jx + px_, jy + py_), 3)
        pygame.draw.circle(sup, (30, 20, 20), (jx + 18, jy), 7)
        # a ORQUÍDEA gigante no meio (a casa do Katchade): 5 pétalas rosas e o miolo
        ox, oy = 470, 230
        pygame.draw.line(sup, (80, 140, 64), (ox - 10, CHAO), (ox, oy + 40), 12)
        pygame.draw.ellipse(sup, (80, 150, 66), (ox - 110, CHAO - 120, 100, 40))  # folhas da orquídea
        pygame.draw.ellipse(sup, (70, 140, 60), (ox + 4, CHAO - 104, 110, 38))
        for k in range(5):
            a = -math.pi / 2 + k * math.tau / 5
            cx, cy = ox + math.cos(a) * 52, oy + math.sin(a) * 44
            pygame.draw.ellipse(sup, (214, 102, 160), (cx - 46, cy - 34, 92, 68))
            pygame.draw.ellipse(sup, (246, 170, 206), (cx - 40, cy - 28, 80, 56))
            pygame.draw.ellipse(sup, (255, 226, 240), (cx - 22, cy - 14, 44, 28))
        pygame.draw.circle(sup, (184, 52, 126), (ox, oy), 26)
        pygame.draw.circle(sup, (255, 210, 90), (ox, oy), 14)
        pygame.draw.circle(sup, (255, 240, 170), (ox - 4, oy - 4), 5)
        # TREVOS gigantes (do tamanho de guarda-chuva)
        for tx, ty, tam in ((330, CHAO - 150, 40), (620, CHAO - 130, 36)):
            pygame.draw.line(sup, (70, 130, 56), (tx, CHAO), (tx, ty), 6)
            for k in range(3):
                a = -math.pi / 2 + (k - 1) * 2.1
                cx, cy = tx + math.cos(a) * tam * 0.8, ty + math.sin(a) * tam * 0.5
                pygame.draw.circle(sup, (60, 132, 52), (int(cx), int(cy)), tam)
                pygame.draw.circle(sup, (88, 168, 70), (int(cx), int(cy)), tam - 5)
                pygame.draw.arc(sup, (160, 220, 140), (cx - tam * 0.6, cy - tam * 0.6, tam * 1.2, tam * 1.2), 0.5, 2.4, 3)
        # o CHÃO: terra com pedrinhas (do tamanho de pedregulho pra um inseto) e raízes
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (122, 92, 58), (70, 50, 32))
        pygame.draw.line(sup, (96, 160, 70), (0, CHAO), (LARGURA, CHAO), 4)
        for i in range(18):
            x, y = rnd.uniform(0, LARGURA), CHAO + rnd.uniform(8, 50)
            r = rnd.uniform(6, 16)
            pygame.draw.ellipse(sup, (150, 140, 128), (x - r, y - r * 0.6, r * 2, r * 1.2))
            pygame.draw.ellipse(sup, (186, 178, 166), (x - r * 0.6, y - r * 0.5, r, r * 0.5))
        for i in range(30):  # brotinhos de grama no chão
            x = rnd.uniform(0, LARGURA)
            pygame.draw.line(sup, (90, 160, 70), (x, CHAO + 2), (x + rnd.uniform(-6, 6), CHAO - rnd.uniform(8, 20)), 3)
        return sup

    def __init__(self):
        super().__init__()
        rnd = random.Random(92)
        self.sementes = [[rnd.uniform(0, LARGURA), rnd.uniform(40, CHAO), rnd.uniform(0.3, 0.8), rnd.uniform(0, 6)]
                         for _ in range(12)]
        self.orvalho = [(rnd.uniform(60, 900), rnd.uniform(200, CHAO - 40), rnd.uniform(0, 6)) for _ in range(9)]

    def animar(self, tela, t, px):
        # a FORMIGA andando lá no fundo, na linha do chão
        fx = (t * 0.6) % (LARGURA + 120) - 60
        fy = CHAO - 6
        for k in range(3):
            pygame.draw.circle(tela, (40, 26, 22), (int((fx - k * 9) / px), int(fy / px)), max(1, int((5 - k) / px)))
        for k in range(3):
            perna = math.sin(t * 0.4 + k) * 3
            pygame.draw.line(tela, (40, 26, 22), ((fx - 9 + k * 5) / px, fy / px),
                             ((fx - 11 + k * 5 + perna) / px, (fy + 6) / px), 1)
        # as SEMENTES do dente-de-leão voando (paraquedinhas)
        for s in self.sementes:
            s[0] = (s[0] + s[2]) % (LARGURA + 40)
            y = s[1] + math.sin(t * 0.02 + s[3]) * 18
            x = s[0] - 20
            pygame.draw.line(tela, (230, 230, 220), (x / px, y / px), (x / px, (y + 8) / px), 1)
            for k in range(5):
                a = -math.pi + k * math.pi / 4
                pygame.draw.line(tela, (255, 255, 255), (x / px, y / px),
                                 ((x + math.cos(a) * 6) / px, (y + math.sin(a) * 4) / px), 1)
        # as GOTAS DE ORVALHO brilhando
        for x, y, f in self.orvalho:
            k = max(0.0, math.sin(t * 0.04 + f))
            r = max(1, int(4 / px))
            pygame.draw.circle(tela, (190, 230, 255), (int(x / px), int(y / px)), r)
            if k > 0.7:
                pygame.draw.circle(tela, (255, 255, 255), (int(x / px - r * 0.3), int(y / px - r * 0.3)), max(1, r // 2))
        # as FOLHAS DE GRAMA da frente balançando no vento
        for i, (x, h, curva, larg, cor) in enumerate(LAMINAS_CAMPO):
            _lamina(tela, x, h, curva, larg, cor, math.sin(t * 0.03 + i * 1.7) * 14, px)


SECRETOS = {"VILA DOS SAPOS": "ULTRA-MEGA-VILLAGE"}  # cenário: código que libera


def disponiveis():
    """Os cenários que dá pra escolher (os secretos só depois do código)."""
    import codigos
    return [n for n in CENARIOS if n not in SECRETOS or codigos.ativo(SECRETOS[n])]


Templo.nome = "TEMPLO"
CENARIOS = {"TEMPLO": Templo, "PÂNTANO": Pantano, "FERRO-VELHO": FerroVelho, "TOCA": Toca, "DOJO": Dojo,
            "CAMPO DE BATALHA": CampoBatalha, "TORRE DO MAGO": TorreMago, "CASSINO": Cassino, "LABORATÓRIO": Laboratorio, "ARENA DE SUMÔ": ArenaSumo, "SELVA": Selva,
            "VILA DOS SAPOS": VilaSapos, "TEATRO DE MÁGICA": Teatro,
            "NAVIO FANTASMA": NavioFantasma, "CERCADO DO DESERTO": CercadoDeserto,
            "PRAIA DA ILHA": PraiaIlha, "MONTANHA NEVADA": MontanhaNevada, "MONTE KARASUMA": MonteKarasuma,
            "CAVERNA DOS MORCEGOS": CavernaMorcegos, "FLORESTA ANTIGA": FlorestaAntiga,
            "CAMPO GIGANTE": CampoGigante}
_prontos = {}


def cenario(nome):
    """Pega o cenário pelo nome (desenha o fundo uma vez só e guarda)."""
    if nome not in _prontos:
        _prontos[nome] = CENARIOS[nome]()
    return _prontos[nome]
