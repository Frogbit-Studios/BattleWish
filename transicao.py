"""TRANSIÇÃO DE CENÁRIO (estilo Injustice): golpe forte joga o adversário na parede,
ele atravessa, sai voando e cai no cenário vizinho. Tira dano extra e só acontece uma vez por round."""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from efeitos import texto, texto_grande

# de onde pra onde (os cenários são vizinhos)
DESTINOS = {"FERRO-VELHO": "CAMPO DE BATALHA", "CAMPO DE BATALHA": "FERRO-VELHO", "DOJO": "TEMPLO",
            "TEMPLO": "DOJO", "PÂNTANO": "TOCA", "TOCA": "PÂNTANO", "TORRE DO MAGO": "TEMPLO", "CASSINO": "DOJO", "LABORATÓRIO": "CAMPO DE BATALHA", "ARENA DE SUMÔ": "DOJO", "SELVA": "PÂNTANO", "VILA DOS SAPOS": "PÂNTANO",
            "TEATRO DE MÁGICA": "CASSINO", "NAVIO FANTASMA": "PÂNTANO",
            "CERCADO DO DESERTO": "CAMPO DE BATALHA", "PRAIA DA ILHA": "NAVIO FANTASMA",
            "MONTANHA NEVADA": "TOCA", "MONTE KARASUMA": "TEMPLO",
            "CAVERNA DOS MORCEGOS": "TOCA", "FLORESTA ANTIGA": "SELVA",
            "CAMPO GIGANTE": "FLORESTA ANTIGA"}
DANO = 12
VEL_MINIMA = 6         # voando mais rápido que isso (ou de golpe forte) atravessa a parede
BATE, VOA, FIM = 22, 58, 90
GOLPE = dict(dano=DANO, nivel="medio", ia="perto", transicao=True)


class Transicao:
    def __init__(self, partida, vitima, atacante, lado):
        self.p, self.vitima, self.atacante, self.lado = partida, vitima, atacante, lado
        self.t = 0
        self.ponto = (vitima.x + lado * 20, vitima.y - 60 * vitima.s)
        self.destino = DESTINOS.get(partida.cena.nome, partida.cena.nome)
        rng = random.Random()
        self.cacos = [[self.ponto[0], self.ponto[1] + rng.uniform(-60, 60), lado * rng.uniform(2, 12),
                       rng.uniform(-9, 2), rng.uniform(4, 12), rng.choice(((120, 110, 100), (90, 80, 70), (160, 150, 130)))]
                      for _ in range(40)]
        self.rachaduras = []
        for _ in range(9):
            a = rng.uniform(0, math.tau)
            pts = [self.ponto]
            for _ in range(4):
                a += rng.uniform(-0.5, 0.5)
                d = rng.uniform(20, 46)
                pts.append((pts[-1][0] + math.cos(a) * d, pts[-1][1] + math.sin(a) * d))
            self.rachaduras.append(pts)
        from lutador import Lutador
        self.voador = Lutador(vitima.f, 0, -lado)  # o grandão rodopiando no meio da viagem
        self.voador.disfarce = vitima.disfarce
        self.voador.s = vitima.f["tam"] * 1.25
        self.voador.estado = "voando"
        self.voador.chao_sombra = 100_000
        self.rng = rng

    @property
    def acabou(self):
        return self.t >= FIM

    def passo(self):
        self.t += 1
        p = self.p
        if self.t == 1:
            som.tocar("quebra")
            som.tocar("explosao")
            p.tremer(20)
        for c in self.cacos:
            c[0] += c[2]
            c[1] += c[3]
            c[3] += 0.35
        if self.t == VOA:  # chegou no cenário novo
            import cenarios
            p.cena = cenarios.cenario(self.destino)
            import clima
            import objetos
            p.objetos = objetos.criar(p.cena.nome)  # (o cenário novo tem o objeto e o clima dele)
            p.clima = clima.criar(p.cena.nome)
            v, a = self.vitima, self.atacante
            v.mudar("caido")
            v.x, v.y, v.vx, v.vy = LARGURA / 2 + self.lado * 170, CHAO, 0, 0
            v.malabar = v.quica = False
            v.rastro, a.rastro = [], []
            v.pose_vista = a.pose_vista = None
            a.golpe = None
            a.mudar("parado")
            a.x, a.y, a.vx, a.vy = LARGURA / 2 - self.lado * 100, CHAO, 0, 0
            a.dir = self.lado
            p.projeteis = []
            v.levar(DANO, a, GOLPE)
            som.tocar("queda")
            p.tremer(14)
            p.poeira(v.x)

    # ------------------------------------------------------------ desenho
    def desenhar(self, tela):
        t = self.t
        if t < BATE:  # a parede rachando
            self.p.desenhar_luta(tela)
            k = min(1, t / 6)
            for pts in self.rachaduras:
                n = 1 + int(k * (len(pts) - 1))
                pygame.draw.lines(tela, (20, 16, 14), False, pts[:n + 1], 5)
                pygame.draw.lines(tela, (240, 230, 210), False, pts[:n + 1], 2)
            self.desenhar_cacos(tela)
            if t < 5:
                branco = pygame.Surface((LARGURA, ALTURA))
                branco.fill(BRANCO)
                branco.set_alpha(230 - t * 40)
                tela.blit(branco, (0, 0))
            texto_grande(tela, "CRASH!", 90, (255, 220, 70), (LARGURA // 2, 160), 1 + max(0, 8 - t) * 0.08,
                         contorno=(60, 20, 0))
        elif t < VOA:  # voando entre os cenários
            u = (t - BATE) / (VOA - BATE)
            tela.fill((14, 10, 22))
            for i in range(22):  # riscos de velocidade
                y = (i * 53 + t * 7) % ALTURA
                x = ((i * 97 - t * 40 * self.lado) % (LARGURA + 300)) - 150
                pygame.draw.line(tela, (70, 60, 100), (x, y), (x + 220 * self.lado, y), 3)
            v = self.voador
            v.t = t
            v.angulo = t * 0.35 * self.lado
            v.x = LARGURA / 2 - self.lado * 380 + self.lado * 760 * u
            v.y = 400 - math.sin(u * math.pi) * 90
            v.desenhar(tela)
            for c in self.cacos:
                pygame.draw.rect(tela, c[5], (LARGURA / 2 - self.lado * (300 - u * 700) + (c[1] % 60) * self.lado,
                                              c[1] % ALTURA, c[4], c[4]))
            texto(tela, f">> {self.destino} >>" if self.lado > 0 else f"<< {self.destino} <<", 30, (255, 220, 70),
                  (LARGURA // 2, 70))
        else:  # chegou: o cenário novo aparece
            self.p.desenhar_luta(tela)
            k = (t - VOA) / (FIM - VOA)
            if k < 0.5:
                preto = pygame.Surface((LARGURA, ALTURA))
                preto.fill((0, 0, 0))
                preto.set_alpha(int(255 * (1 - k * 2)))
                tela.blit(preto, (0, 0))
            texto_grande(tela, f"+{DANO}", 40, (255, 120, 80), (self.vitima.x, self.vitima.y - 150 - k * 30),
                         contorno=(40, 0, 0))

    def desenhar_cacos(self, tela):
        for c in self.cacos:
            pygame.draw.rect(tela, (20, 16, 14), (c[0] - 1, c[1] - 1, c[4] + 2, c[4] + 2))
            pygame.draw.rect(tela, c[5], (c[0], c[1], c[4], c[4]))
