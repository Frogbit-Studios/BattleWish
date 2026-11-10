"""CENÁRIO QUE MUDA NO MEIO DA LUTA (v2.x, pedido do Gomes): a partir do 2º round (ou depois de 45 s de luta,
pro trio/sobrevivência que têm 1 round só) cada cenário ganha um EVENTO:

  TEMPLO            CHUVA            o chão molha: quem para de andar ainda escorrega um pouquinho
  PÂNTANO           MARÉ ALTA        a água sobe: andando fica mais devagar
  FERRO-VELHO       ÍMÃ GIGANTE      o ímã do guindaste passa e puxa quem está embaixo
  TOCA              DESMORONAMENTO   pedras caem do teto (a sombra avisa)
  DOJO              LANTERNAS APAGAM fica escuro, só os lutadores iluminados
  CAMPO DE BATALHA  BOMBARDEIO       bombas caem do céu (a sombra avisa)
  TORRE DO MAGO     GRAVIDADE MÁGICA o pulo fica mais alto e mais lento
  CASSINO           CHUVA DE FICHAS  fichas caem do teto: pegar uma enche a ULTIMATE
  LABORATÓRIO       APAGÃO           a luz cai e o chão dá choque (um pedaço pisca antes)
  ARENA DE SUMÔ     TAMBORES         a plateia bate os tambores: a cada batida os dois enchem a ULTIMATE
  SELVA             VENTANIA         o vento empurra pra um lado (e vira de tempos em tempos)
  VILA DOS SAPOS    CHUVA DE SAPOS   sapinhos caem do céu (só pra rir)
  TEATRO DE MÁGICA  HOLOFOTE         o holofote segue quem está ganhando (só visual)
  NAVIO FANTASMA    TEMPESTADE       o navio balança e todo mundo desliza de um lado pro outro
  CERCADO DO DESERTO TEMPESTADE DE AREIA  o vento de areia empurra (e vira) e a tela fica amarelada
  PRAIA DA ILHA     ONDAS GIGANTES   de tempos em tempos uma onda atravessa a tela e arrasta quem está no chão
                                      (a espuma avisa 1 s antes; pular escapa)

ONLINE: o estado só muda no passo(); usa só o random global (a partida dá seed a cada quadro). O desenho só lê.
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from efeitos import texto_grande

EVENTO_ROUND = 2          # o evento começa nesse round...
EVENTO_SEGUNDOS = 45      # ...ou depois de tantos segundos de luta no round (trio/sobrevivência: 1 round só)
LIGADO_NO_TREINO = False
SUBIDA = 90               # quadros pro evento chegar na força toda
AVISO = 150               # quadros do texto "COMEÇOU A CHOVER!"

SOLTOS = ("parado", "andando", "agachado", "defendendo", "pulando", "prepulo")  # (quem o vento/balanço empurra)

PEDRA = dict(dano=6, nivel="alto", defe=12, emp=2, hit=18, derruba=True, voo=(2, 5), especial=True, proj=True)
BOMBA = dict(dano=8, nivel="alto", defe=14, emp=3, hit=20, derruba=True, voo=(4, 9), especial=True, proj=True)
CHOQUE = dict(dano=4, nivel="baixo", defe=8, emp=1, hit=8, paralisa=25, especial=True, proj=True, imbloqueavel=True)

EVENTOS = {
    "TEMPLO": ("CHUVA", "COMEÇOU A CHOVER!"),
    "PÂNTANO": ("MARE", "A MARÉ ESTÁ SUBINDO!"),
    "FERRO-VELHO": ("IMA", "O ÍMÃ GIGANTE LIGOU!"),
    "TOCA": ("PEDRAS", "A TOCA ESTÁ DESMORONANDO!"),
    "DOJO": ("ESCURO", "AS LANTERNAS APAGARAM!"),
    "CAMPO DE BATALHA": ("BOMBAS", "BOMBARDEIO!"),
    "TORRE DO MAGO": ("GRAVIDADE", "GRAVIDADE MÁGICA!"),
    "CASSINO": ("FICHAS", "CHUVA DE FICHAS!"),
    "LABORATÓRIO": ("APAGAO", "APAGÃO NO LABORATÓRIO!"),
    "ARENA DE SUMÔ": ("TAMBORES", "A PLATEIA ESTÁ AGITADA!"),
    "SELVA": ("VENTO", "VENTANIA!"),
    "VILA DOS SAPOS": ("SAPOS", "CHOVENDO SAPOS!"),
    "TEATRO DE MÁGICA": ("HOLOFOTE", "O SHOW VAI COMEÇAR!"),
    "NAVIO FANTASMA": ("BALANCO", "TEMPESTADE NO MAR!"),
    "CERCADO DO DESERTO": ("AREIA", "TEMPESTADE DE AREIA!"),
    "PRAIA DA ILHA": ("ONDAS", "ONDAS GIGANTES!"),
    "MONTANHA NEVADA": ("NEVASCA", "NEVASCA!"),
    "MONTE KARASUMA": ("VENTO", "VENTO DA MONTANHA!"),
    "CAVERNA DOS MORCEGOS": ("REVOADA", "REVOADA DE MORCEGOS!"),
    "FLORESTA ANTIGA": ("VENTO", "A FLORESTA ESTÁ SUSSURRANDO!"),
    "CAMPO GIGANTE": ("VENTO", "VENTANIA NO CAMPO!"),
}


def criar(nome_do_cenario):
    ev = EVENTOS.get(nome_do_cenario)
    return Clima(nome_do_cenario, *ev) if ev else Nada()


class Nada:
    nome = ""
    ativo = False

    def passo(self, partida):
        pass

    def desenhar(self, tela):
        pass

    def desenhar_frente(self, tela, partida=None):
        pass

    def resetar(self):
        pass


class Clima:
    def __init__(self, cenario, tipo, aviso):
        self.cenario = cenario
        self.tipo = tipo
        self.nome = aviso
        self.t = 0
        self.resetar()

    def resetar(self):
        """Começo de round: o evento volta a esperar (ele confere o round e o tempo sozinho)."""
        self.ativo = False
        self.forca = 0.0
        self.aviso = 0
        self.k = 0                # quadros desde que começou
        self.antes = [None, None] # x de cada lutador no quadro passado
        self.desliza = [0.0, 0.0] # CHUVA: quanto ainda escorrega
        self.perigos = []         # PEDRAS/BOMBAS/FICHAS: dict(x, y, vy, fase, t, ...)
        self.zona = None          # APAGÃO: (x, largura, quadros, aceso)
        self.ima_x = LARGURA / 2
        self.vento = 1
        self.batida = 0           # TAMBORES: quadros desde a última batida (desenho)
        self.particulas = []      # [x, y, vx, vy, vida, cor, tam]
        self.lider = None         # HOLOFOTE: quem está ganhando
        self.onda = None          # ONDAS GIGANTES: dict(x, aviso) da onda atravessando

    # ------------------------------------------------------------ lógica (só aqui o estado muda)
    def deve_comecar(self, p):
        if p.fase != "luta":
            return False
        passou = TEMPO_ROUND * FPS - getattr(p, "tempo", TEMPO_ROUND * FPS)
        return p.round >= EVENTO_ROUND or passou >= EVENTO_SEGUNDOS * FPS

    def passo(self, p):
        self.t += 1
        if p.treino and not LIGADO_NO_TREINO:
            return
        for q in self.particulas:
            q[0] += q[2]
            q[1] += q[3]
            leve = (q[6] == 4 and self.tipo in ("VENTO", "AREIA")) or (q[6] == 7 and self.tipo == "SAPOS") \
                or (q[6] == 11 and self.tipo == "REVOADA")
            q[3] += (math.sin(self.t * 0.3 + q[0] * 0.01) * 0.3 if q[6] == 11 else 0.03) if leve else \
                0.0 if (q[6] == 9 and self.tipo == "NEVASCA") else 0.25  # (folha/sapo/neve devagar; morcego voa ondulando)
            q[4] -= 1
        self.particulas = [q for q in self.particulas if q[4] > 0]
        if self.batida:
            self.batida += 1
        if not self.ativo:
            if self.deve_comecar(p):
                self.ativo = True
                self.aviso = AVISO
                som.tocar("vento" if self.tipo not in ("TAMBORES", "BOMBAS") else "explosao", 0.6)
            else:
                return
        self.k += 1
        self.forca = min(1.0, self.k / SUBIDA)
        if self.aviso:
            self.aviso -= 1
        if p.fase != "luta":
            self.antes = [l.x for l in p.L]
            return
        getattr(self, "passo_" + self.tipo.lower(), lambda p: None)(p)
        self.andar_perigos(p)
        for l in p.L:
            l.x = max(PAREDE_E, min(PAREDE_D, l.x))
        self.antes = [l.x for l in p.L]

    def empurrar(self, p, quanto):
        """Empurra quem está solto (não no meio de golpe, apanhando ou caído)."""
        for l in p.L:
            if l.estado in SOLTOS:
                l.x += quanto * self.forca

    def passo_chuva(self, p):  # escorrega: quem para de andar ainda desliza um pouco
        for i, l in enumerate(p.L):
            if self.antes[i] is None:
                continue
            dx = l.x - self.antes[i]
            if l.estado == "andando" and l.no_chao():
                self.desliza[i] = dx * 0.7 * self.forca
            elif l.estado in ("parado", "agachado", "defendendo") and l.no_chao() and abs(self.desliza[i]) > 0.1:
                l.x += self.desliza[i]
                self.desliza[i] *= 0.88
            else:
                self.desliza[i] = 0.0

    def passo_mare(self, p):  # anda mais devagar dentro d'água
        for i, l in enumerate(p.L):
            if self.antes[i] is not None and l.estado == "andando" and l.no_chao():
                l.x -= (l.x - self.antes[i]) * 0.35 * self.forca

    def passo_ima(self, p):  # o ímã vai e volta lá em cima e puxa quem está embaixo
        self.ima_x = LARGURA / 2 + math.sin(self.k / 170) * 330
        for l in p.L:
            d = self.ima_x - l.x
            if abs(d) < 150 and l.estado in SOLTOS:
                l.x += (1.3 if d > 0 else -1.3) * self.forca
                if self.k % 9 == 0:
                    self.particulas.append([l.x, l.y - 40, random.uniform(-1, 1), -2, 18, (190, 200, 220), 2])

    def passo_gravidade(self, p):  # pulo de lua: a gravidade fica bem mais fraca no ar
        for l in p.L:
            if not l.no_chao() and (l.estado == "pulando" or (l.estado == "ataque" and l.vy > -30)):
                l.vy -= GRAVIDADE * 0.4 * self.forca
                if self.k % 6 == 0:
                    self.particulas.append([l.x, l.y, random.uniform(-1, 1), 0.5, 22, (200, 160, 255), 3])

    def passo_revoada(self, p):  # o BANDO de morcegos atravessando a caverna (só aparência: escurece)
        if self.k % 4 == 0:
            de = random.choice((-20, LARGURA + 20))
            self.particulas.append([de, random.uniform(70, CHAO - 60), (1 if de < 0 else -1) * random.uniform(6, 10),
                                    random.uniform(-0.8, 0.8), 160, (20, 14, 28), 11])

    def passo_vento(self, p):
        if self.k % 480 == 0:  # o vento vira
            self.vento = -self.vento
        self.empurrar(p, 0.9 * self.vento)
        if self.k % 3 == 0:
            self.particulas.append([0 if self.vento > 0 else LARGURA, random.uniform(150, CHAO - 10),
                                    self.vento * random.uniform(9, 14), random.uniform(-1, 1), 90,
                                    random.choice(((70, 140, 60), (110, 170, 70), (150, 120, 60))), 4])

    def passo_areia(self, p):  # TEMPESTADE DE AREIA: vento mais forte que o da selva, com areia na tela
        if self.k % 420 == 0:
            self.vento = -self.vento
        self.empurrar(p, 1.1 * self.vento)
        if self.k % 2 == 0:
            self.particulas.append([0 if self.vento > 0 else LARGURA, random.uniform(120, CHAO),
                                    self.vento * random.uniform(12, 18), random.uniform(-0.5, 0.5), 80,
                                    random.choice(((220, 190, 130), (200, 170, 110))), 4])

    ONDA_CADA, ONDA_AVISO, ONDA_VEL = 420, 60, 16  # (quadros entre ondas, quadros de aviso, px por quadro)

    def passo_ondas(self, p):  # ONDAS GIGANTES: a espuma avisa, a onda atravessa e arrasta quem está no chão
        q = self.k % self.ONDA_CADA
        if q == self.ONDA_CADA - self.ONDA_AVISO:
            self.onda = dict(x=LARGURA + 120.0, aviso=self.ONDA_AVISO)
            som.tocar("vento", 0.5)
        o = getattr(self, "onda", None)
        if not o:
            return
        if o["aviso"] > 0:
            o["aviso"] -= 1
            return
        antes = o["x"]
        o["x"] -= self.ONDA_VEL
        for l in p.L:  # quem está no chão quando a frente da onda passa é arrastado um pedaço
            if l.estado in SOLTOS and l.no_chao() and o["x"] - 60 < l.x < antes + 40:
                l.x -= self.ONDA_VEL * 0.55 * self.forca
        if self.k % 2 == 0:
            self.particulas.append([o["x"] + random.uniform(-20, 60), CHAO - random.uniform(10, 120),
                                    random.uniform(-6, -2), random.uniform(-3, 0), 26, (230, 245, 255), 4])
        if o["x"] < -260:
            self.onda = None

    def passo_nevasca(self, p):  # NEVASCA: neve até o joelho, todo mundo anda mais devagar
        for i, l in enumerate(p.L):
            if self.antes[i] is not None and l.estado == "andando" and l.no_chao():
                l.x -= (l.x - self.antes[i]) * 0.3 * self.forca
        if self.k % 2 == 0:
            self.particulas.append([random.uniform(-40, LARGURA), -10, random.uniform(2.5, 4.5),
                                    random.uniform(2.5, 4), 160, (245, 248, 255), 9])  # (tam 9 = floco)

    def passo_balanco(self, p):  # o navio balança: todo mundo desliza pro lado que abaixou
        self.empurrar(p, 1.2 * math.sin(self.k * math.tau / 300))

    def passo_tambores(self, p):  # a cada batida os dois enchem um pouco a ULTIMATE
        if self.k % 240 == 120:
            self.batida = 1
            p.tremer(4)
            som.tocar("queda", 0.5)
            for l in p.L:
                l.encher(25)

    def passo_apagao(self, p):  # um pedaço do chão pisca e depois dá choque
        if self.zona is None and self.k % 200 == 100:
            alvo = random.choice(p.L)
            self.zona = [max(PAREDE_E, min(PAREDE_D - 160, alvo.x - 80 + random.uniform(-60, 60))), 160, 0, False]
        if self.zona is not None:
            z = self.zona
            z[2] += 1
            if z[2] == 50:  # ZAP!
                z[3] = True
                som.tocar("laser", 0.6)
                for l in p.L:
                    c = l.corpo()
                    if c and l.no_chao() and z[0] <= l.x <= z[0] + z[1]:
                        self.acertar(p, l, CHOQUE, (l.x, CHAO - 20))
            if z[2] >= 64:
                self.zona = None

    def passo_pedras(self, p):
        self.cair(p, 210, "pedra")

    def passo_bombas(self, p):
        self.cair(p, 170, "bomba")

    def passo_fichas(self, p):
        if self.k % 70 == 35:
            self.perigos.append(dict(tipo="ficha", x=random.uniform(PAREDE_E + 30, PAREDE_D - 30), y=-30.0,
                                     vy=2.0, fase="cai", t=0, giro=random.uniform(0, 6)))

    def passo_sapos(self, p):
        if self.k % 25 == 0:
            self.particulas.append([random.uniform(40, LARGURA - 40), -20, random.uniform(-1.5, 1.5), 1, 120,
                                    (80, 170, 70), 7])

    def passo_holofote(self, p):
        v0, v1 = (p.vida_lado(i) if hasattr(p, "vida_lado") else p.L[i].vida for i in (0, 1))
        self.lider = None if abs(v0 - v1) < 1 else (0 if v0 > v1 else 1)

    def passo_escuro(self, p):
        pass

    def cair(self, p, cada, tipo):
        """PEDRAS/BOMBAS: escolhe alguém, a sombra persegue um pouco, trava e cai."""
        if self.k % cada == cada // 2:
            alvo = random.choice(p.L)
            self.perigos.append(dict(tipo=tipo, x=alvo.x, y=-60.0, vy=0.0, fase="mira", t=0, alvo=p.L.index(alvo)))

    def andar_perigos(self, p):
        for h in self.perigos:
            h["t"] += 1
            if h["fase"] == "mira":
                alvo = p.L[h["alvo"]]
                if h["t"] < 30:
                    h["x"] += (alvo.x - h["x"]) * 0.1
                if h["t"] >= 45:
                    h["fase"], h["vy"] = "cai", 5.0
                continue
            h["vy"] += 0.9 if h["tipo"] != "ficha" else 0.15
            h["vy"] = min(h["vy"], 22 if h["tipo"] != "ficha" else 5)
            h["y"] += h["vy"]
            h["giro"] = h.get("giro", 0) + 0.2
            r = pygame.Rect(h["x"] - 26, h["y"] - 26, 52, 52)
            for l in p.L:
                c = l.corpo()
                if not c or not r.colliderect(c):
                    continue
                if h["tipo"] == "ficha":  # pegou a ficha: enche a ULTIMATE
                    l.encher(80)
                    som.tocar("blip", 0.6)
                    self.poeira(h["x"], h["y"], (255, 220, 90), 10)
                else:
                    self.acertar(p, l, PEDRA if h["tipo"] == "pedra" else BOMBA, r.clip(c).center)
                    self.explodir(p, h)
                h["fim"] = True
                break
            if not h.get("fim") and h["y"] >= CHAO - 20:
                if h["tipo"] == "ficha":
                    self.poeira(h["x"], CHAO - 6, (255, 220, 90), 5)
                else:
                    self.explodir(p, h)
                h["fim"] = True
        self.perigos = [h for h in self.perigos if not h.get("fim")]

    def explodir(self, p, h):
        if h["tipo"] == "bomba":
            som.tocar("explosao", 0.7)
            p.tremer(10)
            self.poeira(h["x"], CHAO - 20, (255, 160, 60), 22)
        else:
            som.tocar("queda", 0.6)
            p.tremer(6)
            self.poeira(h["x"], CHAO - 20, (130, 100, 70), 14)

    def acertar(self, p, alvo, g, ponto):
        sinal = 1 if alvo.dir < 0 else -1  # (empurra pra trás de onde ele olha)
        res = alvo.receber(g, sinal, None, 1.0)
        p.ultimo_hit = p.tf
        if res == "quebrou":
            p.guarda_quebrada(alvo, ponto)
        elif res == "parry":
            p.parry(alvo, ponto)
        else:
            p.som_do_golpe(res, g)
            p.faisca(ponto[0], ponto[1], res == "def", g["dano"] >= 8)
            p.parada = PARADA_GOLPE if res == "hit" else 4
        return res

    def poeira(self, x, y, cor, n):
        for _ in range(n):
            a = random.uniform(0, math.tau)
            v = random.uniform(2, 6)
            self.particulas.append([x, y, math.cos(a) * v, math.sin(a) * v - 2, random.randint(12, 24), cor,
                                    random.randint(3, 6)])

    # ------------------------------------------------------------ desenho (só lê o estado)
    def desenhar(self, tela):
        """Atrás dos lutadores: água/ímã/sombras dos perigos/chão do apagão."""
        if not self.ativo:
            return
        f, t = self.forca, self.t
        if self.tipo == "MARE":  # a água subindo no chão
            h = int(26 * f)
            agua = pygame.Surface((LARGURA, h + 10), pygame.SRCALPHA)
            agua.fill((60, 120, 150, 120))
            for x in range(0, LARGURA, 40):
                pygame.draw.arc(agua, (170, 220, 240, 160), (x + (t % 40) - 40, 0, 40, 12), 0, math.pi, 2)
            tela.blit(agua, (0, CHAO - h))
        elif self.tipo == "IMA":
            x = int(self.ima_x)
            pygame.draw.line(tela, (40, 36, 36), (x, 0), (x, 120), 3)
            pygame.draw.rect(tela, (170, 40, 40), (x - 36, 120, 72, 22), border_radius=6)
            pygame.draw.rect(tela, (200, 200, 210), (x - 36, 136, 16, 10))
            pygame.draw.rect(tela, (200, 200, 210), (x + 20, 136, 16, 10))
            if (t // 6) % 2:
                for k in range(3):
                    pygame.draw.arc(tela, (160, 200, 255), (x - 40 - k * 14, 150 + k * 10, 80 + k * 28, 30), 3.4, 6.0, 2)
        elif self.tipo == "APAGAO" and self.zona is not None:
            x0, w, q, aceso = self.zona
            if aceso:
                pts = [(x0 + w * i / 10, CHAO - 4 - (12 if (i + t) % 2 else 0)) for i in range(11)]
                pygame.draw.lines(tela, (170, 240, 255), False, pts, 4)
                pygame.draw.lines(tela, BRANCO, False, pts, 1)
            elif (q // 5) % 2:
                pygame.draw.rect(tela, (255, 230, 80), (x0, CHAO - 6, w, 8), border_radius=3)
        for h in self.perigos:  # a sombra avisando
            if h["tipo"] == "ficha":
                continue
            k = min(1.0, h["t"] / 30)
            w = int(26 + 34 * k)
            som_ = pygame.Surface((w * 2, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(som_, (0, 0, 0, int(60 + 90 * k)), (0, 0, w * 2, 20))
            tela.blit(som_, (h["x"] - w, CHAO - 10))
            if h["fase"] == "mira" and h["t"] >= 30 and (h["t"] // 3) % 2:
                pygame.draw.ellipse(tela, (255, 70, 60), (h["x"] - w, CHAO - 10, w * 2, 20), 2)

    def desenhar_frente(self, tela, partida=None):
        """Na frente dos lutadores: chuva, escuro, perigos caindo, folhas, sapos, holofote e o aviso."""
        if not self.ativo:
            return
        f, t = self.forca, self.t
        if self.tipo in ("CHUVA", "BALANCO"):  # chuva (inclinada na tempestade)
            inc = 6 if self.tipo == "CHUVA" else int(10 * math.sin(self.k * math.tau / 300)) + 4
            n = int(70 * f)
            for i in range(n):
                x = (i * 137 + t * 3) % (LARGURA + 60) - 30
                y = (i * 89 + t * 15) % ALTURA
                pygame.draw.line(tela, (170, 190, 230), (x, y), (x - inc, y + 16), 1)
        if self.tipo in ("ESCURO", "APAGAO", "REVOADA"):  # escuro com luz em volta dos lutadores
            escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            escuro.fill((0, 0, 12, int((150 if self.tipo == "ESCURO" else 100 if self.tipo == "REVOADA" else 120) * f)))
            if partida is not None:
                for l in partida.L:
                    for r, a in ((130, 0), (100, 0)):
                        pygame.draw.circle(escuro, (0, 0, 12, a), (int(l.x), int(l.y - 70)), r)
            if self.tipo == "APAGAO" and (t // 90) % 5 == 0 and (t // 4) % 2:  # a luz piscando de vez em quando
                escuro.fill((0, 0, 0, 0))
            tela.blit(escuro, (0, 0))
        if self.tipo == "AREIA":  # a tela amarelada da tempestade
            nuvem = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            nuvem.fill((210, 170, 100, int(70 * f)))
            for i in range(40):
                x = (i * 173 + t * 14 * self.vento) % (LARGURA + 80) - 40
                y = (i * 97) % ALTURA
                pygame.draw.line(nuvem, (235, 205, 150, int(110 * f)), (x, y), (x - 30 * self.vento, y + 2), 2)
            tela.blit(nuvem, (0, 0))
        o = getattr(self, "onda", None) if self.tipo == "ONDAS" else None
        if o:  # a espuma avisando (do lado direito) e depois o paredão de água atravessando
            agua = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            if o["aviso"] > 0:
                if (o["aviso"] // 6) % 2:
                    pygame.draw.rect(agua, (230, 245, 255, 160), (LARGURA - 70, CHAO - 14, 70, 14), border_radius=6)
            else:
                x = o["x"]
                onda = [(x + 320, CHAO), (x + 320, CHAO - 50), (x + 200, CHAO - 110), (x + 100, CHAO - 165),
                        (x + 30, CHAO - 190), (x - 30, CHAO - 175), (x - 55, CHAO - 140), (x - 30, CHAO - 120),
                        (x - 5, CHAO - 135), (x + 15, CHAO - 100), (x + 5, CHAO - 50), (x - 20, CHAO)]
                pygame.draw.polygon(agua, (40, 115, 160, int(160 * f)), onda)          # o corpo da onda
                pygame.draw.polygon(agua, (70, 160, 200, int(150 * f)),                 # a parte de dentro, mais clara
                                    [(x + 300, CHAO), (x + 260, CHAO - 60), (x + 150, CHAO - 120), (x + 70, CHAO - 150),
                                     (x + 40, CHAO - 110), (x + 50, CHAO - 50), (x + 30, CHAO)])
                for k in range(7):  # a crista de espuma enrolando
                    ang = math.pi * (0.15 + k * 0.13)
                    cx, cy = x + 10 + math.cos(ang) * 42, CHAO - 150 - math.sin(ang) * 38
                    pygame.draw.circle(agua, (235, 248, 255, int(220 * f)), (int(cx), int(cy)), 13 - k)
                for k in range(8):  # a espuma no pé da onda
                    pygame.draw.circle(agua, (225, 242, 255, int(180 * f)), (int(x - 15 + k * 14), CHAO - 6 - (k % 2) * 6), 9)
            tela.blit(agua, (0, 0))
        if self.tipo == "NEVASCA":  # a tela esbranquiçada e a neve acumulando no chão
            branco = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            branco.fill((235, 240, 250, int(60 * f)))
            pygame.draw.rect(branco, (245, 248, 255, int(150 * f)), (0, CHAO - int(10 * f), LARGURA, 14))
            tela.blit(branco, (0, 0))
        if self.tipo == "HOLOFOTE" and partida is not None and self.lider is not None:
            l = partida.L[self.lider]
            luz = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            pygame.draw.polygon(luz, (255, 245, 200, int(55 * f)),
                                [(LARGURA / 2 - 20, 0), (LARGURA / 2 + 20, 0), (l.x + 90, CHAO), (l.x - 90, CHAO)])
            pygame.draw.ellipse(luz, (255, 245, 200, int(70 * f)), (l.x - 90, CHAO - 14, 180, 28))
            tela.blit(luz, (0, 0))
        if self.tipo == "BALANCO":  # o mar subindo e descendo na frente
            sobe = math.sin(self.k * math.tau / 300) * 14
            for camada, (cor, dy) in enumerate((((30, 60, 70), 0), ((40, 90, 100), 10))):
                pts = [(x, ALTURA - 18 + dy + sobe * (1 if camada else -1) + math.sin(x / 50 + t * 0.08) * 6)
                       for x in range(0, LARGURA + 40, 40)]
                pygame.draw.polygon(tela, cor, pts + [(LARGURA, ALTURA), (0, ALTURA)])
        if self.tipo == "TAMBORES" and 0 < self.batida < 20:  # onda da batida
            r = 40 + self.batida * 20
            anel = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            pygame.draw.circle(anel, (255, 200, 120, max(0, 160 - self.batida * 8)), (LARGURA // 2, CHAO + 40), r, 4)
            tela.blit(anel, (0, 0))
        for h in self.perigos:
            if h["fase"] != "cai":
                continue
            x, y = int(h["x"]), int(h["y"])
            if h["tipo"] == "pedra":
                pygame.draw.polygon(tela, (90, 70, 56), [(x - 20, y - 6), (x - 6, y - 22), (x + 16, y - 16),
                                                         (x + 22, y + 6), (x + 2, y + 20), (x - 16, y + 14)])
                pygame.draw.polygon(tela, (130, 104, 80), [(x - 12, y - 6), (x - 2, y - 16), (x + 10, y - 10),
                                                           (x + 4, y + 2)])
            elif h["tipo"] == "bomba":
                pygame.draw.ellipse(tela, (50, 56, 50), (x - 12, y - 24, 24, 40))
                pygame.draw.polygon(tela, (80, 90, 80), [(x - 12, y - 24), (x + 12, y - 24), (x, y - 34)])
                pygame.draw.circle(tela, (255, 200, 60) if (t // 3) % 2 else (255, 90, 40), (x, y + 18), 4)
            else:  # ficha do cassino girando
                w = max(6, int(abs(math.cos(h["giro"])) * 26))
                cor = ((220, 40, 40), (40, 120, 220), (40, 160, 60))[int(h["x"]) % 3]
                pygame.draw.ellipse(tela, cor, (x - w // 2, y - 13, w, 26))
                pygame.draw.ellipse(tela, (250, 250, 250), (x - w // 2 + 2, y - 9, max(2, w - 4), 18), 2)
        for q in self.particulas:
            if self.tipo == "SAPOS" and q[6] == 7:  # sapinho caindo
                x, y = int(q[0]), int(q[1])
                pygame.draw.ellipse(tela, (70, 160, 60), (x - 9, y - 6, 18, 12))
                pygame.draw.circle(tela, (240, 240, 230), (x - 4, y - 6), 3)
                pygame.draw.circle(tela, (240, 240, 230), (x + 4, y - 6), 3)
                pygame.draw.circle(tela, (20, 20, 20), (x - 4, y - 6), 1)
                pygame.draw.circle(tela, (20, 20, 20), (x + 4, y - 6), 1)
            elif self.tipo == "NEVASCA" and q[6] == 9:  # floco de neve
                pygame.draw.circle(tela, q[5], (int(q[0]), int(q[1])), 3)
            elif self.tipo == "AREIA" and q[6] == 4:  # grão de areia voando
                pygame.draw.line(tela, q[5], (int(q[0]), int(q[1])), (int(q[0] - q[2]), int(q[1])), 2)
            elif self.tipo == "REVOADA" and q[6] == 11:  # MORCEGO voando (batendo as asas)
                x, y = int(q[0]), int(q[1])
                asa = 6 if (self.t // 3 + x) % 2 else -3
                pygame.draw.polygon(tela, q[5], [(x - 14, y - asa), (x - 4, y - 2), (x, y + 3), (x + 4, y - 2), (x + 14, y - asa),
                                                 (x + 6, y + 2), (x, y + 6), (x - 6, y + 2)])
                pygame.draw.circle(tela, (255, 70, 70), (x - 2, y), 1)
                pygame.draw.circle(tela, (255, 70, 70), (x + 2, y), 1)
            elif self.tipo == "VENTO" and q[6] == 4:  # folha voando
                pygame.draw.ellipse(tela, q[5], (int(q[0]) - 6, int(q[1]) - 3, 12, 6))
            else:
                pygame.draw.circle(tela, q[5], (int(q[0]), int(q[1])), max(1, int(q[6] * min(1, q[4] / 10))))
        if self.aviso:
            k = self.aviso / AVISO
            esc = 1.0 + 0.3 * max(0.0, (k - 0.85) / 0.15)
            texto_grande(tela, self.nome, 34, (255, 230, 120), (LARGURA // 2, 150), esc,
                         alfa=int(255 * min(1, self.aviso / 30)), contorno=(40, 20, 0))
