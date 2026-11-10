"""DESAFIOS DE COMBO (tipo os Trials do Street Fighter): cada lutador tem uma lista de combos pra aprender,
do fácil pro difícil. Os passos acendem conforme você acerta; se o combo cair, volta pro começo.
Completou pela primeira vez: ganha moedas. TAB = o computador mostra como faz."""
import pygame

import save
import som
from config import *  # noqa: F401,F403
import controle_video
from efeitos import desenhar_botao, texto, texto_grande, texto_moedas
from lutador import Entrada

ROTULOS = {"soco": "M1", "chute": "M2", "ag_soco": "S + M1", "ag_chute": "S + M2", "ar_soco": "NO AR: M1",
           "ar_chute": "NO AR: M2"}
DICA_AR = "depois do Q, segura CIMA pra pular atrás dele"

# (nome, passos, moedas, dica) — passos: golpe normal ou botão de especial (E, Q, R, SHIFT)
PADRAO = [
    ("O BÁSICO", ["soco", "soco", "chute"], 10, "aperta M1, M1, M2 bem no ritmo"),
    ("AGACHADO", ["ag_soco", "ag_soco", "ag_chute"], 10, "segura S o tempo todo"),
    ("CANCELA NO ESPECIAL", ["soco", "soco", "R"], 20, "o soco acertou? já aperta o especial"),
    ("PRO ALTO", ["soco", "Q"], 20, "soco e já cancela no Q"),
    ("COMBO AÉREO", ["soco", "Q", "ar_soco", "ar_soco", "ar_chute"], 40, DICA_AR),
]
# trocas pra quem tem golpes diferentes (todos testados: dá pra fazer de verdade)
TROCAS = {
    "MAX-10": {2: ("CANCELA NO ESPECIAL", ["soco", "chute", "R"], 20, "soco, chute e já aperta o R"),
               3: ("VOOZINHO", ["soco", "soco", "SHIFT"], 20, "dois socos e cancela no voo"),
               4: ("AGACHADO + VOO", ["ag_soco", "ag_soco", "SHIFT"], 30, "segura S nos socos e cancela no voo")},
    "TRAFO": {2: ("CANCELA NO ESPECIAL", ["soco", "chute", "E"], 20, "o chute acertou? já solta o linguão"),
              3: ("PULÃO", ["soco", "soco", "SHIFT"], 20, "dois socos e cancela no pulão"),
              4: ("PARALISA E VOA", ["chute", "E", "ar_soco", "ar_chute"], 40, "o linguão paralisa: pula (W) e bate no ar")},
    "SPHYRUS": {4: ("MARTELADA COMPLETA", ["soco", "chute", "Q"], 40, "soco, chute e a martelada pra cima")},
    "FRIGANTUS": {2: ("CANCELA NO ESPECIAL", ["soco", "chute", "SHIFT"], 20, "soco, chute e já escorrega de barriga")},
    "KATCHADE": {2: ("CORTE CRUZADO", ["soco", "soco", "E"], 20, "dois socos e já cruza as foices"),
                 3: ("BOTE", ["soco", "Q"], 20, "o soco acertou? salta e agarra com as foices")},
    "SILVANUS": {2: ("SEMENTE NA CARA", ["soco", "soco", "E"], 20, "dois socos e já cospe a semente nele"),
                 3: ("CUSPE RÁPIDO", ["soco", "chute", "E"], 20, "soco, chute e cospe (o Q é armadilha: fica no chão)"),
                 4: ("JARDIM DE PANCADA", ["soco", "soco", "R"], 40, "dois socos e as plantinhas brotam embaixo dele")},
    "NOCTURNUS": {2: ("ABRAÇO DAS ASAS", ["soco", "soco", "Q"], 20, "dois socos e já fecha as asas (paralisa)"),
                  4: ("MORDIDA DA NUVEM", ["soco", "chute", "R"], 40, "soco, chute e a nuvem de morcegos morde ele")},
    "INAZUMANEKO": {3: ("PASSO RELÂMPAGO", ["soco", "soco", "SHIFT"], 20, "dois socos e atravessa cortando"),
                    4: ("DANÇA DA TEMPESTADE", ["soco", "chute", "R"], 40, "soco, chute e já solta a dança trovejante")},
    "TAMER": {4: ("SELVAGEM", ["soco", "chute", "SHIFT"], 40, "soco, chute e já monta no lobo")},
    "RIBBAT": {2: ("SAPO AGACHADO", ["ag_soco", "ag_soco", "SHIFT"], 20, "segura S nos socos e vai de investida"),
               3: ("INVESTIDA", ["soco", "soco", "SHIFT"], 20, "dois socos e cancela na investida"),
               4: ("SAPO SUPREMO", ["chute", "SHIFT"], 40, "o chute acertou? INVESTIDA!")},
    "JOHN": {2: ("CANCELA NO ESPECIAL", ["soco", "chute", "R"], 20, "soco, chute e já solta o crocodilo"),
             3: ("PRO ALTO", ["chute", "Q"], 20, "o chute segura mais tempo: dá tempo do teleporte")},
    "KUN": {3: ("PRO ALTO", ["chute", "Q"], 20, "o chute segura mais tempo: dá tempo da carta"),
            4: ("SHORYUKEN COMPLETO", ["soco", "chute", "Q"], 40, "soco, chute e shoryuken")},
}

FEITO_ESPERA = 110  # quadros mostrando "COMPLETO!" antes de ir pro próximo


def combos_de(ficha):
    nome = ficha.get("nome_base", ficha["nome"])
    lista = list(PADRAO)
    for i, troca in TROCAS.get(nome, {}).items():
        lista[i] = troca
    golpes = ficha.get("golpes", {})
    nomes = ficha.get("nomes", {})
    saida = []
    for titulo, passos, moedas, dica in lista:
        resolvidos = [golpes.get(p, p) for p in passos]
        rotulos = [ROTULOS.get(p) or f"M3+{p}" for p in passos]
        detalhes = [nomes.get(p, "") if p in golpes else "" for p in passos]
        saida.append(dict(titulo=titulo, passos=resolvidos, botoes=passos, rotulos=rotulos, detalhes=detalhes,
                          moedas=moedas, dica=dica))
    return saida


def de_longe(nome_golpe):
    """Golpe que sai de longe (tiro, laser, magia de média distância)? Aí o boneco começa longe."""
    from golpes import GOLPES
    g = GOLPES.get(nome_golpe, {})
    return bool(g.get("proj") or g.get("ia") == "longe" or nome_golpe == "finn_levita")


def feitos(nome):
    return save.d().setdefault("combos", {}).setdefault(nome, [])


class TreinoCombos:
    """Fica dentro da partida de treino e acompanha os acertos do jogador no boneco."""

    def __init__(self, ficha):
        self.ficha = ficha
        self.nome = ficha.get("nome_base", ficha["nome"])
        self.lista = combos_de(ficha)
        self.i = 0
        self.demo = False
        self.jogador = None
        self.t = 0
        self.limpar()

    @property
    def atual(self):
        return self.lista[self.i]

    def limpar(self):
        self.feito = 0
        self.ultimo = None
        self.completo_t = 0
        self.caiu_t = 0
        self.premio = None
        self.demo_t = 0

    def trocar(self, partida, passo):
        self.parar_demo(partida)
        self.i = (self.i + passo) % len(self.lista)
        self.limpar()
        self.arrumar(partida)

    def arrumar(self, partida):
        """Coloca os dois pertinho, prontos pro combo."""
        eu, boneco = partida.L
        for l, x in ((eu, 330), (boneco, 600 if de_longe(self.atual["passos"][0]) else 400)):
            l.mudar("parado")
            l.golpe = None
            l.x, l.y, l.vx, l.vy = x, CHAO, 0, 0
            l.vida = l.vida_max
            l.combo = 0
        eu.dir, boneco.dir = 1, -1
        eu.barra = BARRA_MAX
        partida.projeteis = []
        for l in (eu, boneco):  # (treino de combo: sem STAMINA nem RECARGA, pra repetir à vontade)
            l.regras.add("sem_cansaco")

    # ---- acertos ----
    def acertou(self, nome, ativacao, combo):
        if self.completo_t:
            return
        if ativacao == self.ultimo:
            return  # o mesmo golpe acertando de novo (golpe de vários hits conta uma vez só)
        self.ultimo = ativacao
        passos = self.atual["passos"]
        if combo <= 1 and self.feito:
            self.feito = 0  # começou outro combo
        if nome == passos[self.feito]:
            self.feito += 1
        elif nome == passos[0]:
            self.feito = 1
        elif self.feito:
            self.feito = 0
            self.caiu_t = 50
        if self.feito == len(passos):
            self.completou()

    def completou(self):
        self.completo_t = 1
        som.tocar("ultimate", 0.7)
        if self.demo:
            return
        lista = feitos(self.nome)
        if self.i not in lista:
            lista.append(self.i)
            self.premio = self.atual["moedas"]
            save.ganhar(self.premio)  # (já salva)

    def passo(self, partida):
        self.t += 1
        alvo = partida.L[1]
        if self.caiu_t > 0:
            self.caiu_t -= 1
        if self.completo_t:
            self.completo_t += 1
            if self.completo_t > FEITO_ESPERA:
                self.parar_demo(partida)
                if self.i < len(self.lista) - 1:
                    self.trocar(partida, 1)
                else:
                    self.limpar()
                    self.arrumar(partida)
            return
        if self.feito and alvo.no_chao() and alvo.estado in ("parado", "andando", "agachado", "defendendo"):
            self.feito = 0  # o boneco se soltou: o combo caiu
            self.caiu_t = 50
        if self.demo:
            self.demo_t += 1
            if self.demo_t > 480:
                self.parar_demo(partida)

    # ---- demonstração ----
    def comecar_demo(self, partida):
        if self.demo:
            return
        self.limpar()
        self.arrumar(partida)
        self.demo = True
        self.jogador = partida.ctrl[0]
        partida.ctrl = (BotCombo(self), partida.ctrl[1])

    def parar_demo(self, partida):
        if self.demo:
            self.demo = False
            partida.ctrl = (self.jogador, partida.ctrl[1])
            if hasattr(self.jogador, "antes"):
                self.jogador.antes = {"soco": True, "chute": True}

    # ---- desenho ----
    def desenhar(self, tela):
        c = self.atual
        n = len(self.lista)
        feitos_aqui = feitos(self.nome)
        marca = "  ✔" if self.i in feitos_aqui else ""
        texto(tela, f"COMBO {self.i + 1}/{n}: {c['titulo']}{marca}", 20, AMARELO, (LARGURA // 2, 118))
        k = len(c["passos"])
        w = 120
        x0 = LARGURA // 2 - (k * w + (k - 1) * 14) // 2
        for j in range(k):
            r = pygame.Rect(x0 + j * (w + 14), 138, w, 50)
            feito = j < self.feito or self.completo_t
            cor_fundo = (40, 120, 70) if feito else (30, 26, 48)
            borda = (120, 255, 150) if feito else (255, 220, 70) if j == self.feito else (90, 80, 130)
            pygame.draw.rect(tela, cor_fundo, r, border_radius=8)
            pygame.draw.rect(tela, borda, r, 3, border_radius=8)
            b = c["botoes"][j]
            if controle_video.no_controle():  # no controle: o botão colorido (com "BAIXO" ou "NO AR" se precisar)
                base = b.replace("ag_", "").replace("ar_", "")
                extra = "BAIXO +" if b.startswith("ag_") else "NO AR" if b.startswith("ar_") else ""
                if extra:
                    texto(tela, extra, 10, (220, 220, 235), (r.centerx, r.y + 9))
                desenhar_botao(tela, controle_video.nome(base), (r.centerx, r.y + (22 if extra else 18)), 20)
            else:
                texto(tela, c["rotulos"][j], 16, BRANCO, (r.centerx, r.y + 18))
            if c["detalhes"][j]:
                img = pygame.font.SysFont("arial", 11, bold=True).render(c["detalhes"][j][:20], True, (210, 210, 225))
                tela.blit(img, img.get_rect(center=(r.centerx, r.y + 38)))
            if j < k - 1:
                texto(tela, ">", 18, (200, 200, 220), (r.right + 7, r.centery))
        if self.completo_t:
            esc = 1 + max(0, (14 - self.completo_t) / 10)
            texto_grande(tela, "COMBO COMPLETO!", 38, (120, 255, 150), (LARGURA // 2, 232), esc, contorno=(10, 40, 20))
            if self.premio:
                texto_moedas(tela, f"+{self.premio}", LARGURA // 2 + 40, 270, self.t, 22)
        elif self.caiu_t:
            texto_grande(tela, "O COMBO CAIU!", 30, (255, 120, 100), (LARGURA // 2, 232), contorno=(40, 10, 10))
        else:
            texto(tela, "dica: " + c["dica"], 15, (220, 220, 235), (LARGURA // 2, 208))
        if self.demo:
            texto(tela, "DEMONSTRAÇÃO (o computador está mostrando)", 16, (150, 220, 255), (LARGURA // 2, 300))
        texto(tela, "N próximo   B anterior   TAB demonstração   ESC pausa", 13, BRANCO, (LARGURA // 2, ALTURA - 52))


class BotCombo:
    """Faz o combo sozinho (pra demonstração e pros testes)."""

    def __init__(self, treino):
        self.tr = treino

    def ler(self, bruto, eu, ele, jogo):
        tr = self.tr
        if tr.completo_t:
            return Entrada()
        passo = tr.atual["botoes"][tr.feito] if tr.feito < len(tr.atual["botoes"]) else None
        if passo is None:
            return Entrada()
        frente = 6 if ele.x > eu.x else 4
        dist = abs(ele.x - eu.x)
        livre = eu.estado in ("parado", "andando", "agachado")
        longe = de_longe(tr.atual["passos"][tr.feito])
        if tr.feito == 0 and livre and not longe and dist > 90:
            return Entrada(frente)  # chega perto
        if passo in ("ar_soco", "ar_chute"):
            if eu.no_chao():
                return Entrada(8)  # pula atrás dele (pulo de perseguição)
            if eu.perseguindo or abs(ele.y - eu.y) > 90 or dist > 110:
                return Entrada(5)
            return Entrada(5, soco=passo == "ar_soco", chute=passo == "ar_chute")
        if passo in ("soco", "chute"):
            return Entrada(5, soco=passo == "soco", chute=passo == "chute")
        if passo in ("ag_soco", "ag_chute"):
            return Entrada(2, soco=passo == "ag_soco", chute=passo == "ag_chute")
        return Entrada(5, especial=passo)
