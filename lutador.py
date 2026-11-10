"""O lutador: como ele se mexe, ataca, defende e apanha. E o desenho do palito."""
import math

import pygame

from config import *  # noqa: F401,F403
import habilidades as hab
import pecas
import som
import stamina  # (v4.0: STAMINA e RECARGA dos especiais, contra o spam)
from golpes import GOLPES, POSES, misturar, suave
import provocacao  # noqa: F401  (registra o golpe "provocar")

LIVRE = ("parado", "andando", "agachado")
# COMBOS: depois de um golpe normal ACERTAR, dá pra emendar estes (até 3 seguidos)
CADEIA = {"soco": ("soco", "chute"), "ag_soco": ("ag_soco", "ag_chute", "soco"),
          "chute": (), "ag_chute": (), "ar_soco": ("ar_soco", "ar_chute"), "ar_chute": ()}
CADEIA_MAX = 3
CADEIA_AR = 5          # no ar dá pra emendar mais (combo aéreo)
MALABAR_MAX = 12       # depois de tantos golpes no ar, o outro cai (sem combo infinito)
ESPELHO = {1: 3, 3: 1, 4: 6, 6: 4, 7: 9, 9: 7}
PADRAO = {"E": "bola", "Q": "subida", "R": "giro", "SHIFT": "avanco", "Z": "ultimate"}


class Entrada:
    """O que o jogador (ou o computador) está apertando neste quadro.
    dir segue o teclado numérico: 5 = nada, 6 = direita, 4 = esquerda, 8 = cima, 2 = baixo, 3 = baixo+direita...
    especial = qual botão de especial: "E", "Q", "R", "SHIFT" ou "Z"."""

    def __init__(self, dir=5, soco=False, chute=False, especial=None):
        self.dir, self.soco, self.chute, self.especial = dir, soco, chute, especial
        self.segura_ult = False  # ainda segurando o Z (o Cannan carrega a ultimate)
        self.provoca = False     # apertou T (provocação)
        self.barra = False       # segurando o botão de BARRA (F / LT): especial EX
        self.barra_toque = False  # apertou o botão de BARRA agora: ESCAPE de combo
        self.troca = False       # TRIO: apertou o botão de troca (G / R3)
        self.lobo = False        # TAMER: apertou X (troca a cor do lobo)


class Projetil:
    def __init__(self, dono, x, y, dir, golpe):
        self.dono, self.x, self.y = dono, x, y
        self.golpe = golpe
        self.vx = golpe["vel"] * dir
        self.raio = golpe["raio"]
        self.vivo = True
        self.t = 0
        self.ex = getattr(dono, "ex", False)          # saiu de um especial EX (bate mais forte)
        self.nome_golpe = dono.nome_golpe              # (pros desafios de combo: de qual golpe saiu)
        self.ativacao = getattr(dono, "golpe_id", 0)

    def rect(self):
        return pygame.Rect(self.x - self.raio, self.y - self.raio, self.raio * 2, self.raio * 2)

    def update(self):
        self.t += 1
        self.x += self.vx
        if self.x < -40 or self.x > LARGURA + 40:
            self.vivo = False

    def desenhar(self, tela):
        if self.golpe.get("desenho_proj"):
            return self.golpe["desenho_proj"](self, tela)
        cor = self.dono.f["cor_poder"]
        for i in range(4):  # rastro
            r = self.raio - i * self.raio // 5
            x = self.x - self.vx * i * 1.6
            pygame.draw.circle(tela, tuple(c // (i + 1) for c in cor), (int(x), int(self.y)), max(3, r))
        r = self.raio + math.sin(self.t * 0.6) * 2
        pygame.draw.circle(tela, cor, (int(self.x), int(self.y)), int(r))
        pygame.draw.circle(tela, BRANCO, (int(self.x), int(self.y)), int(r * 0.5))


class Lutador:
    def __init__(self, ficha, x, dir):
        self.f = ficha
        self.s = ficha["tam"]
        self.poses = dict(POSES)
        self.poses.update(ficha.get("poses", {}))  # cada personagem pode ter o próprio jeito de ficar parado, andar...
        self.extra = {}                             # coisas do personagem que duram a luta toda (ex: munição)
        self.disfarce = None                        # ficha de outro lutador (o Trafo se transformando)
        self.dano_combo_vista = 0
        self.mutado = None                          # Trafo com MUTAÇÃO: a ficha do oponente que ele virou
        self.entrada_t = None                       # quadro da entrada (começo da luta), ou None
        self.esconde = False                        # entrada: ainda não apareceu
        self.cortar_chao = False                    # entrada: parte embaixo do chão não aparece (Trafo saindo da terra)
        self.cortar_acima = None                    # entrada: acima dessa altura não aparece (Finn se materializando)
        self.x, self.y = float(x), float(CHAO)
        self.vx = self.vy = 0.0
        self.dir = dir
        self.vida = self.vida_max = ficha["vida"]
        self.vida_vista = self.vida  # a barra vermelha que desce devagar
        self.estado, self.t = "parado", 0
        self.golpe = self.nome_golpe = None
        self.acertou = False
        self.ja_atacou = False
        self.stun = 0
        self.inv = 0
        self.r = 5
        self.combo = 0
        self.projetil = None
        self.agachado_def = False
        self.barra = 0
        self.pediu_ultimate = False  # a partida escurece a tela quando isso liga
        # coisas que os golpes especiais usam
        self.angulo = 0.0          # corpo girado (radianos), em volta do quadril
        self.giro_voo = 0.0        # rodopiando enquanto voa
        self.vira = False          # desenha virado pro outro lado (rodopio)
        self.sobrepor = {}         # pontos da pose trocados pelo golpe (ex: braço esticado)
        self.pose_espera = None    # ENTRADA: a pose em que ele fica esperando a vez de falar (ex: Rib com o selo de mão)
        self.feixe = None          # laser: ((x1, y1), (x2, y2)) quando está machucando
        self.bonus_parede = 0      # dano extra se bater na parede voando
        self.memo = {}             # anotações do golpe especial em andamento
        self.ex = False            # o golpe de agora é um especial EX
        self.regras = set()        # MODOS MALUCOS ligados nesta luta (a partida preenche)
        self.pisca = 0             # brilho extra (olho carregando, etc.)
        # só pra animação (não muda o jogo)
        self.pose_vista = None     # a pose que aparece na tela: vai "deslizando" até a pose certa
        self.passo = 0.0           # em que parte da caminhada ele está
        self.pouso = 0             # amortecida quando cai do pulo
        self.tremor_hit = 0        # treme quando apanha
        self.rastro = []           # fotos dos últimos quadros (rastro nos golpes rápidos)
        self.pulo_r = 8
        self.guarda = GUARDA_MAX   # gasta defendendo; zerou = guarda quebrada (fica tonto)
        self.guarda_espera = 0     # quadros desde a última defesa (depois de um tempo a guarda volta)
        self.r_antes = 5           # direção do quadro anterior (pra saber quando TOCOU pra frente)
        self.parry_frente = 0      # quadros que o parry de cima/meio está "ligado"
        self.parry_baixo = 0       # quadros que o parry de baixo está ligado
        self.parry_trava = 0       # tocou e errou: espera um pouco (não dá pra ficar apertando sem parar)
        self.buffer = None         # soco/chute apertado um tiquinho antes da hora
        self.buffer_t = 0
        self.cadeia = 0            # quantos golpes normais já emendou
        self.malabar = False       # jogado pra cima: dá pra continuar batendo nele no ar
        self.malabar_n = 0         # quantos golpes já levou no ar
        self.quica = False         # chute pra baixo: quica no chão e continua no combo
        self.combo_ar = False      # está fazendo combo aéreo (pode atacar de novo no mesmo pulo)
        self.perseguindo = 0       # quadros do pulo de perseguição teleguiado
        self.provocou = 0          # provocações completas neste round
        self.tomou_ult = False     # levou ultimate neste round
        self.acertou_ult = False   # acertou a ultimate neste round
        self.acertou_ult2 = False  # ...e a 2ª ULTIMATE (pro troféu PODER MÁXIMO)
        self.voo_forte = False     # saiu voando de um golpe forte (pode atravessar pra outro cenário)
        self.invisivel = 0         # PODER MÁGICO (Finn): quadros que ainda fica invisível
        self.as_t = 0              # ÁS NA MANGA (Kun): quadros contando até o ás acender
        self.as_ativo = 0          # ÁS NA MANGA: quadros que o ás ainda fica aceso
        stamina.iniciar(self)      # STAMINA (v4.0): ataques gastam; zerou = CANSADO

    # ------------------------------------------------------------ ajudas
    def no_chao(self):
        return self.y >= CHAO

    def rel(self, d):
        """Transforma a direção da tela em direção 'pra frente/pra trás' do lutador."""
        return d if self.dir == 1 else ESPELHO.get(d, d)

    def mudar(self, estado):
        if estado == "prepulo":
            self.pulos = getattr(self, "pulos", 0) + 1  # (ESTATÍSTICAS / MISSÕES: quantas vezes pulou)
        self.estado, self.t = estado, 0
        self.angulo = self.giro_voo = 0.0
        self.vira = False
        self.sobrepor = {}
        self.feixe = None
        self.pisca = 0
        self.superaquecido = False  # Cannan cansado depois da ultimate (fumaça no lugar das estrelas)
        self.ex = False             # o golpe de agora é EX (o comecar liga depois de chamar o mudar)
        self.voo_forte = False

    def encher(self, quanto):
        if quanto > 0:
            quanto *= self.f.get("barra_mult", 1.0)  # alguns personagens enchem a ultimate mais devagar
            if "so_ultimate" in self.regras:
                quanto *= 5  # MODO MALUCO: SÓ ULTIMATE
        self.barra = max(0, min(BARRA_TOTAL if self.tem_ult2() else BARRA_MAX, self.barra + quanto))

    def tem_ult2(self):
        return bool(self.golpe_do_botao("Z2"))

    def bonus_amarelo(self, quanto):
        """Jogada boa (combo de 5+, choque vencido, objeto usado): enche a parte AMARELA (se a azul já encheu)."""
        if self.barra >= BARRA_MAX and self.tem_ult2():
            self.barra = min(BARRA_TOTAL, self.barra + quanto)

    def golpe_do_botao(self, botao):
        return (self.mutado or self.f).get("golpes", PADRAO).get(botao)

    def mutar(self, ficha):
        """MUTAÇÃO: vira o oponente (aparência, golpes e habilidade dele) até o fim do round."""
        self.mutado = ficha
        self.disfarce = ficha
        self.poses = dict(POSES)
        self.poses.update(ficha.get("poses", {}))
        self.flash_mutacao = 30
        som.tocar("puf")

    def comecar(self, nome, pagar=False):
        g = GOLPES[nome]
        if self.extra.get("nadando"):
            return False  # NATAÇÃO (Sphyrus): nadando ele não ataca
        if g.get("pode") and not g["pode"](self):
            return False
        if g.get("ultimate2"):
            if self.barra < BARRA_TOTAL:
                return False  # a amarela ainda não encheu
        elif g.get("ultimate"):
            if self.barra < BARRA_MAX:
                return False  # barra ainda não encheu
        elif g.get("proj") and not g.get("varios") and self.projetil and self.projetil.vivo:
            return False  # só uma bola por vez
        if pagar:  # STAMINA: golpe pedido pelo jogador paga (EX paga 25% a mais)
            vai_ex = (g.get("especial") and not g.get("ultimate") and getattr(self, "ex_pedido", False)
                      and self.barra >= EX_CUSTO and nome != "provocar")
            if not stamina.pagar(self, nome, g, vai_ex):
                return False
        if g.get("ultimate"):
            self.barra = 0 if g.get("ultimate2") else max(0, self.barra - BARRA_MAX)  # (a 1ª gasta só a azul)
            self.pediu_ultimate = True
            som.tocar("ultimate")
        elif g.get("som"):
            som.tocar(g["som"])
        elif not g.get("especial"):
            som.tocar("vento", 0.7)
        self.mudar("ataque")
        self.golpe, self.nome_golpe = g, nome
        self.golpe_id = getattr(self, "golpe_id", 0) + 1  # cada vez que começa um golpe, um número novo
        if (g.get("especial") and not g.get("ultimate") and getattr(self, "ex_pedido", False)
                and self.barra >= EX_CUSTO and nome != "provocar"):  # ESPECIAL EX: gasta 1/4 da barra
            self.barra -= EX_CUSTO
            self.ex = True
            self.flash_ex = 26
            som.tocar("carga", 0.7)
            self.preparar_ex(nome)
        self.acertou = False
        self.memo = {}
        self.inv = max(g.get("inv", 0), 3 if g.get("ultimate2") else 0)
        if g.get("aereo"):
            self.ja_atacou = True
        elif self.no_chao():
            self.vx = 0
        return True

    def tentar_especial(self, botao):
        if botao == "Z" and getattr(self, "ex_pedido", False) and self.barra >= BARRA_TOTAL and self.tem_ult2():
            botao = "Z2"  # EX + ULTIMATE (M3 2x + Z / LT + RT) com a amarela cheia = 2ª ULTIMATE
        nome = self.golpe_do_botao(botao) if botao else None
        self.botao_pedido = botao
        if not nome or not stamina.pode_especial(self, botao):  # RECARGA: o especial ainda não voltou
            return False
        if self.comecar(nome, pagar=True):
            stamina.usou_especial(self, botao, GOLPES[nome])
            return True
        return False

    def janelas(self):
        g = self.golpe
        return g.get("janelas") or ((g["ini"], g["ini"] + g["ativo"]),)

    # ------------------------------------------------------------ a cada quadro
    def update(self, e, outro, jogo):
        e = hab.trocar_controles(self, e)  # CONTROLES TROCADOS (Bola de Eco do Nocturnus)
        self.entrada_atual = e
        lento = hab.mult_ataque(self)
        if lento < 1 and self.estado == "ataque":  # ATAQUE MAIS LENTO (Fúria do Sumô): o golpe fica 1 quadro parado
            self._freia = getattr(self, "_freia", 0.0) + (1 - lento)
            calmo = not (e.soco or e.chute or e.especial or e.provoca or e.barra_toque or e.troca or e.lobo)
            if self._freia >= 1 and calmo:  # (só num quadro sem aperto novo: não perde botão)
                self._freia -= 1
                self.animar()
                return
        self._update(e, outro, jogo)
        rapido = hab.mult_ataque(self)
        if rapido > 1 and self.estado == "ataque":  # LOBO PRETO: o ataque roda mais rápido (um passo a mais às vezes)
            self._acelera = getattr(self, "_acelera", 0.0) + (rapido - 1)
            if self._acelera >= 1:
                self._acelera -= 1
                calmo = Entrada(e.dir)  # (sem apertar nada de novo no passo extra)
                calmo.segura_ult = getattr(e, "segura_ult", False)
                self._update(calmo, outro, jogo)
        self.animar()

    def animar(self):
        """Só visual: a pose da tela desliza até a pose certa (fica com quadros entre os quadros)."""
        alvo = self.pose_atual()
        if self.pose_vista is None or self.estado == "agarrado":
            self.pose_vista = alvo
        elif self.sobrepor:  # pose escolhida na mão (entrada, vitória, provocação): DESLIZA até ela, sem pulo seco
            self.pose_vista = misturar(self.pose_vista, alvo, 0.32)
        else:
            if self.estado == "ataque" and self.t <= 2:
                k = 0.85  # golpe começa seco (não fica "socando de dentro da defesa")
            elif self.estado == "ataque":
                k = 0.6
            elif self.estado in ("golpeado", "voando", "defendendo", "tonto"):
                k = 0.5
            else:
                k = 0.3
            self.pose_vista = misturar(self.pose_vista, alvo, k)
        if self.pouso > 0:
            self.pouso -= 1
        g = self.golpe if self.estado == "ataque" else None
        ativo = g and any(a <= self.t < b for a, b in self.janelas())
        rapido = abs(self.vx) > 6.5 or (g and abs(self.vy) > 9) or (g and g.get("ultimate") and self.angulo)
        if rapido:
            self.rastro.append((self.x, self.y, self.pose_vista, self.angulo, self.vira))
            del self.rastro[:-7]
        elif self.rastro:
            self.rastro.pop(0)

    def _update(self, e, outro, jogo):
        self.t += 1
        stamina.passo(self)
        self.ex_pedido = bool(getattr(e, "barra", False))  # segurando a BARRA: o próximo especial sai EX
        if getattr(e, "barra_toque", False) and self.pode_escapar():
            self.escapar(outro, jogo)
            return
        f = self.mutado or self.f
        if getattr(e, "lobo", False) and f.get("tecla_x"):  # TAMER: X troca o lobo
            f["tecla_x"](self)
        if getattr(self, "ex_cadeia", False) and self.estado == "ataque" and outro.estado == "golpeado":
            outro.stun = max(outro.stun, 12)  # EX de Q/R: os pedaços emendam (o outro não escapa no meio)
        for ficha in (self.f, self.mutado):
            if ficha and ficha.get("todo_quadro"):
                ficha["todo_quadro"](self, jogo)
        if hasattr(jogo, "L"):
            ult2.todo_quadro(self, jogo)  # (golem, lobisomem, marujos, caçada, fornalha da 2ª ultimate)
        self.guarda_espera += 1
        if getattr(self, "ult_recente", 0) > 0:
            self.ult_recente -= 1
        if self.invisivel > 0:
            self.invisivel -= 1
        if hab.relogio_as(self):  # ÁS NA MANGA acendeu!
            som.tocar("confirma", 0.6)
        if self.guarda_espera > GUARDA_VOLTA_DEPOIS and self.estado != "tonto":
            self.guarda = min(GUARDA_MAX, self.guarda + GUARDA_VOLTA)
        if self.inv > 0:
            self.inv -= 1
        if self.estado == "ataque" and self.golpe.get("ultimate2"):
            self.inv = max(self.inv, 2)  # 2ª ULTIMATE: ninguém interrompe, do começo ao fim
        self.r = self.rel(e.dir)
        est = self.estado
        # ---- parry: TOCAR pra frente (ou pra baixo) bem na hora ----
        for nome in ("parry_frente", "parry_baixo"):
            v = getattr(self, nome)
            if v > 0:
                setattr(self, nome, v - 1)
                if v == 1:
                    self.parry_trava = PARRY_TRAVA  # passou a janela sem nada: trava um pouquinho
        if self.parry_trava > 0:
            self.parry_trava -= 1
        elif est in LIVRE and self.no_chao():
            tocou_frente = self.r == 6 and self.r_antes not in (6, 3, 9)
            tocou_baixo = self.r == 2 and self.r_antes not in (1, 2, 3)
            if (tocou_frente or tocou_baixo) and (self.parry_frente or self.parry_baixo):
                # tocou de novo com o parry ligado = tá só apertando sem parar: perde e trava
                self.parry_frente = self.parry_baixo = 0
                self.parry_trava = PARRY_TRAVA
            elif tocou_frente:
                self.parry_frente = PARRY_JANELA * hab.mult_parry(self)
            elif tocou_baixo:
                self.parry_baixo = PARRY_JANELA * hab.mult_parry(self)
        self.r_antes = self.r
        # ---- ROLAMENTO: M1 + M2 juntos (pra frente segurando FRENTE; senão pra trás) ----
        self.quadros = getattr(self, "quadros", 0) + 1
        if getattr(self, "rola_espera", 0) > 0:
            self.rola_espera -= 1
        if e.soco or e.chute:
            outro_botao = "chute" if e.soco else "soco"
            junto = (e.soco and e.chute) or (getattr(self, "ultimo_botao", (None, -99))[0] == outro_botao
                                               and self.quadros - self.ultimo_botao[1] <= ROLA_JANELA)
            self.ultimo_botao = ("soco" if e.soco else "chute", self.quadros)
            if junto and self.pode_rolar():
                self.rolar(self.r in (6, 9, 3))
                self.buffer, self.buffer_t = None, 0
                return self.fisica(jogo)
        # ---- guarda o botão apertado um pouquinho antes da hora ----
        if e.soco or e.chute:
            self.buffer, self.buffer_t = ("soco" if e.soco else "chute"), BUFFER_BOTAO
        elif self.buffer_t > 0:
            self.buffer_t -= 1
            if self.buffer_t == 0:
                self.buffer = None

        if est == "agarrado":
            return  # quem agarrou controla tudo (agarrão, ultimate que sempre acerta)

        if est in LIVRE and stamina.preso(self) and self.no_chao():
            # CANSADO (stamina zerou): não anda, não pula, não ataca até encher. Só defende parado.
            if self.no_chao() and abs(outro.x - self.x) > 2:
                self.dir = 1 if outro.x > self.x else -1
                self.r = self.rel(e.dir)
            self.vx = 0
            self.buffer, self.buffer_t = None, 0
            quer = "agachado" if self.r in (1, 2, 3) else "parado"
            if est != quer:
                self.mudar(quer)
        elif est in LIVRE:
            if self.no_chao() and abs(outro.x - self.x) > 2:
                self.dir = 1 if outro.x > self.x else -1  # sempre de frente pro outro
                self.r = self.rel(e.dir)
            r = self.r
            self.cadeia = 0
            if self.tentar_especial(e.especial):
                pass
            elif getattr(e, "provoca", False) and self.no_chao():
                self.comecar("provocar")
            elif self.buffer:
                botao, self.buffer, self.buffer_t = self.buffer, None, 0
                self.comecar(("ag_" if r in (1, 2, 3) else "") + botao, pagar=True)
            elif r in (7, 8, 9):
                self.pulo_r = r
                self.vx = 0
                self.mudar("prepulo")  # agachadinha antes de pular
            elif r in (1, 2, 3):
                if est != "agachado":
                    self.mudar("agachado")
                self.vx = 0
            elif r in (4, 6):
                if est != "andando":
                    self.mudar("andando")
                self.vx = self.f["vel"] * hab.mult_vel(self) * self.dir * (1 if r == 6 else -0.75)
                self.passo += abs(self.vx) * 0.014 * (1 if r == 6 else -1)
            else:
                if est != "parado":
                    self.mudar("parado")
                self.vx = 0

        elif est == "ataque":
            g = self.golpe
            # golpe normal que acertou pode ser "cancelado" num especial (combo!)
            if not g.get("especial") and not g.get("aereo") and self.acertou and e.especial:
                if self.tentar_especial(e.especial):
                    return self.fisica(jogo)
            # ...ou num outro golpe normal (soco -> soco -> chute)
            limite = (CADEIA_AR if g.get("aereo") else CADEIA_MAX) + hab.cadeia_extra(self)
            if (not g.get("especial") and self.acertou and self.buffer and self.t >= g["ini"] + 1
                    and self.cadeia < limite - 1):
                prefixo = "ar_" if g.get("aereo") else "ag_" if self.r in (1, 2, 3) and self.no_chao() else ""
                prox = prefixo + self.buffer
                if prox in CADEIA.get(self.nome_golpe, ()):
                    self.buffer, self.buffer_t = None, 0
                    self.cadeia += 1
                    if self.comecar(prox, pagar=True):
                        return self.fisica(jogo)
            # jogou o outro pra cima e acertou: aperta pra CIMA e pula atrás dele (pulo de perseguição)
            if (g.get("lanca") or g.get("lanca_depois")) and self.acertou and self.r in (7, 8, 9) and self.no_chao() \
                    and outro.estado == "voando" and outro.malabar:
                self.vy = -PULO_PERSEGUE
                self.ja_atacou = False
                self.cadeia = 0
                self.mudar("pulando")
                self.perseguindo = 22  # vai "teleguiado" até ficar do ladinho dele no ar
                self.pose_vista = misturar(self.pose_vista or self.poses["pulo"], self.poses["pulo_sobe"], 0.6)
                return self.fisica(jogo)
            for a, _ in self.janelas():
                if self.t == a:
                    self.acertou = False  # golpe de vários socos: cada um pode acertar
            if g.get("logica"):
                # golpe especial com regras próprias (fica no arquivo do personagem)
                if g["logica"](self, outro, jogo) == "fim":
                    self.terminar_golpe()
                return
            if self.t == g["ini"]:
                if g.get("ao_usar"):
                    g["ao_usar"](self, jogo)
                if g.get("proj"):
                    self.projetil = Projetil(self, self.x + 58 * self.s * self.dir, self.y - 84 * self.s, self.dir, g)
                    jogo.projeteis.append(self.projetil)
                if g.get("sobe"):
                    self.vy = g["sobe"]
            if g.get("avanca") and self.t < g["ini"] + g["ativo"]:
                self.vx = g["avanca"] * self.dir
            elif self.no_chao():
                self.vx *= 0.6
            if self.t >= g["total"]:
                self.terminar_golpe()

        elif est == "prepulo":
            if self.t >= 4:
                self.vy = -self.f["pulo"]
                self.vx = {7: -1, 8: 0, 9: 1}[self.pulo_r] * 3.8 * self.dir
                som.tocar("pulo")
                self.ja_atacou = False
                self.mudar("pulando")

        elif est == "pulando":
            if self.perseguindo > 0:
                self.perseguindo -= 1
                lado = 1 if outro.x >= self.x else -1
                alvo_x = outro.x - lado * 46 * self.s
                alvo_y = outro.y - 22 * self.s  # um pouquinho acima dele
                self.vx = (alvo_x - self.x) / 5
                self.vy = (alvo_y - self.y) / 5 - GRAVIDADE
                self.dir = lado
                if math.hypot(alvo_x - self.x, alvo_y - self.y) < 14 or outro.estado != "voando":
                    self.perseguindo = 0
                    self.vx, self.vy = outro.vx, min(outro.vy, 0) - 2
            if not self.ja_atacou and self.buffer:
                botao, self.buffer, self.buffer_t = self.buffer, None, 0
                self.comecar("ar_" + botao, pagar=True)

        elif est == "tonto":  # guarda quebrada ou paralisado: não faz nada por um tempinho
            self.vx *= 0.8
            if self.t >= getattr(self, "tonto_tempo", TONTO_TEMPO):
                self.tonto_tempo = TONTO_TEMPO
                self.paralisado = False
                self.congelado = False
                self.guarda = GUARDA_MAX
                self.mudar("parado")

        elif est in ("golpeado", "defendendo"):
            self.stun -= 1
            self.vx *= 0.82
            if self.stun <= 0:
                self.combo = 0
                self.mudar("agachado" if self.r in (1, 2, 3) else "parado")

        elif est == "voando":
            self.angulo += self.giro_voo

        elif est == "rolando":
            k = self.t / ROLA_TEMPO
            self.vx = self.rola_lado * ROLA_VEL * (1 - 0.6 * k)
            self.angulo = k * math.tau * (1 if self.rola_lado == self.dir else -1)
            if self.t >= ROLA_TEMPO:
                self.angulo = 0
                self.vx = 0
                self.rola_espera = ROLA_ESPERA
                self.mudar("parado")

        elif est == "caido":
            self.vx = 0
            if self.t > 45 and self.vida > 0:
                self.mudar("levantando")
                self.inv = 30

        elif est == "levantando":
            if self.t >= 16:
                self.mudar("parado")

        elif est == "vitoria" and self.f.get("vitoria"):  # pose de vitória de cada personagem
            self.f["vitoria"](self, self.t, jogo)

        self.fisica(jogo)

    def pode_rolar(self):
        """Dá pra rolar: no chão, livre (ou começando um soco/chute normal) e sem estar nadando."""
        if not self.no_chao() or getattr(self, "rola_espera", 0) > 0 or self.extra.get("nadando")                 or stamina.preso(self):
            return False
        if self.estado in LIVRE:
            return True
        return (self.estado == "ataque" and self.nome_golpe in ("soco", "chute", "ag_soco", "ag_chute")
                and self.t <= ROLA_JANELA + 2 and not self.acertou)

    def rolar(self, pra_frente):
        """ROLAMENTO / ESQUIVA: rola pra frente ou pra trás, invencível um instante."""
        self.golpe = None
        self.mudar("rolando")
        self.rola_lado = self.dir if pra_frente else -self.dir
        self.inv = max(self.inv, ROLA_INV)
        self.extra.pop("esq_perfeita", None)  # (cada rolamento pode dar UMA esquiva perfeita)
        self.rolou = getattr(self, "rolou", 0) + 1
        som.tocar("vento", 0.4)

    def tem_tinta(self):
        return bool(self.f.get("sombra") or self.f.get("tinta") or self.f.get("fantasma"))

    def aplicar_tinta(self, sup, branco):
        """SOMBRA (tudo escuro e roxo) ou OURO (estátua dourada): pinta o desenho inteiro do lutador."""
        if self.f.get("sombra") or self.f.get("tinta") == "sombra":
            _tingir(sup, (70, 50, 110), pygame.BLEND_RGB_MULT)
        elif self.f.get("tinta") == "ouro" and not branco:
            self.pintar_ouro(sup)
        elif self.f.get("tinta") == "holo" and not branco:
            self.pintar_holo(sup)
        if self.f.get("fantasma"):  # FANTASMA (Cráquen): meio transparente (bem mais quando está intangível)
            _tingir(sup, (255, 255, 255, self.extra.get("alfa", 200)), pygame.BLEND_RGBA_MULT)

    def pintar_holo(self, peq):
        """Roupa HOLOGRÁFICA (álbum completo): as cores viram ARCO-ÍRIS que vai passando, com a sombra do desenho."""
        w, h = peq.get_size()
        arco = _arco_iris(w + h, h)
        cor = pygame.Surface((w, h))
        cor.blit(arco, (-((self.t * 2) % h) - h // 2, 0))
        luz = pygame.transform.grayscale(peq)
        _tingir(luz, (70, 70, 70), pygame.BLEND_RGB_ADD)  # (clareia: o arco-íris aparece bem)
        cor.blit(luz, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        fase = (self.t * 4) % 200  # o reflexo branco passando
        if fase < 70:
            x = (fase / 70) * (w + h) - h
            pygame.draw.polygon(cor, (255, 255, 255), [(x, h), (x + 5, h), (x + 5 + h, 0), (x + h, 0)])
        mascara = pygame.mask.from_surface(peq, 10)
        res = pygame.Surface((w, h), pygame.SRCALPHA)
        mascara.to_surface(res, setsurface=cor.convert_alpha(res), unsetcolor=(0, 0, 0, 0))
        peq.fill((0, 0, 0, 0))
        peq.blit(res, (0, 0))

    def pintar_ouro(self, peq):
        """Roupa LENDÁRIA: tira as cores (fica cinza), pinta de dourado e passa um brilho de vez em quando."""
        cinza = pygame.transform.grayscale(peq)
        _tingir(cinza, (255, 206, 90), pygame.BLEND_RGB_MULT)
        _tingir(cinza, (60, 40, 0), pygame.BLEND_RGB_ADD)
        fase = (self.t * 3) % 240  # o brilho passando na diagonal
        if fase < 90:
            w, h = peq.get_size()
            faixa = pygame.Surface((w, h), pygame.SRCALPHA)
            x = (fase / 90) * (w + h) - h
            pygame.draw.polygon(faixa, (255, 255, 230, 150), [(x, h), (x + 8, h), (x + 8 + h, 0), (x + h, 0)])
            faixa.blit(peq, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)  # (só onde tem lutador)
            cinza.blit(faixa, (0, 0))
        peq.fill((0, 0, 0, 0))
        peq.blit(cinza, (0, 0))

    def pode_escapar(self):
        """ESCAPE de combo: apanhando (não preso em ultimate), com meia barra."""
        return (self.estado in ("golpeado", "voando", "tonto") and self.vida > 0 and self.barra >= ESCAPE_CUSTO
                and not getattr(self, "paralisado", False))

    def escapar(self, outro, jogo):
        """Gasta meia barra, se solta do combo e empurra quem estava batendo."""
        self.barra -= ESCAPE_CUSTO
        self.mudar("parado" if self.no_chao() else "pulando")
        self.ja_atacou = True
        self.vx = 0
        self.malabar, self.malabar_n, self.quica = False, 0, False
        self.inv = ESCAPE_INV
        self.stun = 0
        self.flash_escape = 24
        if outro.estado not in ("agarrado", "caido"):
            sinal = 1 if outro.x > self.x else -1
            outro.golpe = None
            outro.mudar("golpeado")
            outro.stun = 16
            outro.vx = sinal * 9
            outro.combo = 0
        jogo.tremer(10)
        som.tocar("parry")
        som.tocar("explosao", 0.4)

    def preparar_ex(self, nome):
        """O EX muda conforme o botão (a regra do Gomes):
        E = mais projéteis (ou 1,5x se não for tiro)   R = o dobro de ataques
        Q = rasteira + soco + o Q (joga pra cima)      SHIFT = dash pra frente e outro pra trás"""
        b = getattr(self, "botao_pedido", None)
        self.ex_botao = b
        self.ex_dano = b == "E"            # (se o E for de perto, bate 1,5x; se for tiro, os tiros viram 3)
        self.ex_fila = []
        self.ex_cadeia = b in ("Q", "R")
        if b == "R":
            self.ex_fila = [nome]          # faz de novo
        elif b == "SHIFT":
            self.ex_fila = ["ex_volta"]    # e volta
        elif b == "Q":                     # começa pela rasteira, depois soco, depois o Q
            self.ex_fila = ["soco", nome]
            self.golpe, self.nome_golpe = GOLPES["ex_rasteira"], "ex_rasteira"

    def terminar_golpe(self):
        fila = getattr(self, "ex_fila", None)
        if fila and self.estado == "ataque":  # EX: emenda o próximo pedaço
            prox = fila.pop(0)
            b, cadeia = self.ex_botao, self.ex_cadeia
            self.ex_pedido = False
            if self.comecar(prox):
                self.ex, self.ex_botao, self.ex_cadeia, self.ex_fila = True, b, cadeia, fila
                self.ex_dano = False
                return
        self.ex_fila = []
        self.ex_cadeia = False
        self.golpe = None
        if self.no_chao():
            self.mudar("parado")
        else:
            self.mudar("pulando")
            self.ja_atacou = not self.combo_ar  # no combo aéreo pode continuar batendo

    def fisica(self, jogo):
        if self.y < CHAO or self.vy < 0:
            leve = self.estado == "voando" and self.malabar and self.malabar_n > 0 and not self.quica
            lua = 0.42 if "lua" in self.regras else 1  # MODO MALUCO: GRAVIDADE DA LUA
            if self.estado == "voando" and getattr(self, "parede_sobe", False) and self.t < 50:
                lua = 0  # (chute do Tamer: voa reto até bater na parede)
            self.vy += GRAVIDADE * (0.62 if leve else 1) * lua
        self.x += self.vx
        self.y += self.vy
        if self.y >= CHAO:
            caiu = self.vy > 0
            self.y, self.vy = CHAO, 0
            self.combo_ar = False
            self.perseguindo = 0
            if caiu:
                if self.estado == "pulando":
                    self.mudar("parado")
                    self.vx = 0
                    self.pouso = 8
                    if self.pose_vista:
                        self.pose_vista = misturar(self.pose_vista, self.poses["pouso"], 0.6)
                elif self.estado == "voando" and self.quica:  # bateu no chão e QUICA (dá pra continuar o combo)
                    self.quica = False
                    if hasattr(jogo, "destruicao"):
                        jogo.destruicao().chao(self.x, 0.4, jogo.t_total)
                    self.vy = -8.5
                    self.y = CHAO - 1
                    self.vx *= 0.4
                    jogo.tremer(12)
                    jogo.poeira(self.x)
                    jogo.parada = max(jogo.parada, 4)
                elif self.estado == "voando":
                    som.tocar("queda")
                    if hasattr(jogo, "destruicao"):  # CENÁRIO QUE QUEBRA: caiu forte, racha o chão ali
                        jogo.destruicao().chao(self.x, 1.0 if self.voo_forte else 0.4, jogo.t_total)
                    self.mudar("caido")
                    self.malabar, self.malabar_n, self.quica = False, 0, False
                    self.vx = 0
                    jogo.tremer(6)
                    jogo.poeira(self.x)
                elif self.estado == "ataque":
                    if self.golpe and self.golpe.get("aereo"):
                        self.golpe = None
                        self.mudar("parado")
                    self.vx = 0
        if self.x < PAREDE_E or self.x > PAREDE_D:
            lado = 1 if self.x > PAREDE_D else -1
            self.x = max(PAREDE_E, min(PAREDE_D, self.x))
            if self.estado == "voando" and hasattr(jogo, "transicao_parede") and jogo.transicao_parede(self, lado):
                return  # atravessou a parede: TRANSIÇÃO DE CENÁRIO!
            if self.estado == "voando" and self.bonus_parede:  # jogado na parede: dói mais!
                if hasattr(jogo, "destruicao"):  # CENÁRIO QUE QUEBRA: racha a parede onde ele bateu
                    forca = 1.0 if self.voo_forte else min(1.0, 0.4 + self.bonus_parede / 12)
                    jogo.destruicao().parede(lado, self.y - 60 * self.s, forca, jogo.t_total)
                self.vida = max(0, self.vida - self.bonus_parede)
                self.bonus_parede = 0
                self.vx = -self.vx * 0.35
                if getattr(self, "parede_sobe", False):  # bateu na parede e SOBE (dá pra continuar batendo)
                    self.parede_sobe = False
                    self.vy = -13
                    self.malabar, self.malabar_n = True, 0
                jogo.tremer(12)
                jogo.faisca(self.x, self.y - 60 * self.s, False)
                jogo.parada = max(jogo.parada, 6)

    # ------------------------------------------------------------ caixas
    def caixa_golpe(self):
        """Onde o golpe machuca agora (ou None)."""
        if self.estado != "ataque" or self.acertou:
            return None
        g = self.golpe
        caixa = self.memo.get("caixa", g["caixa"])
        if not caixa or not any(a <= self.t < b for a, b in self.janelas()):
            return None
        x1, y1, x2, y2 = (v * self.s for v in caixa)
        esq, dir_ = (self.x + x1, self.x + x2) if self.dir == 1 else (self.x - x2, self.x - x1)
        return pygame.Rect(esq, self.y - y2, dir_ - esq, y2 - y1)

    def contato(self, corpo):
        """Se o golpe encostou nesse corpo, devolve o ponto do encontro."""
        if self.estado != "ataque" or self.acertou:
            return None
        if self.feixe:
            linha = corpo.clipline(*self.feixe)
            return linha[0] if linha else None
        cg = self.caixa_golpe()
        if cg and cg.colliderect(corpo):
            return cg.clip(corpo).center
        return None

    def corpo(self):
        """Onde ele pode ser acertado (ou None se não pode)."""
        if self.estado == "voando" and self.malabar and self.malabar_n < getattr(self, "malabar_lim", MALABAR_MAX) \
                and self.inv == 0:
            return pygame.Rect(self.x - 26 * self.s, self.y - 104 * self.s, 52 * self.s, 104 * self.s)
        if self.estado in ("caido", "voando", "agarrado") or self.inv > 0:
            return None
        s = self.s
        baixo = self.estado == "agachado" or (self.estado == "defendendo" and self.agachado_def) \
            or (self.estado == "ataque" and self.golpe["base"] == "agachado")
        if not self.no_chao():
            topo, fundo = 108, 10
        elif baixo:
            topo, fundo = 80, 0
        else:
            topo, fundo = 122, 0
        topo *= self.f.get("altura", 1.0)  # personagem mais baixinho (ex: o Rib, agachadinho)
        if baixo and self.no_chao():
            topo *= hab.altura_agachado(self)  # CONEXÃO TERRESTRE: agachado fica bem menor
        meia = 22 * s * hab.largura(self)      # POSTURA NINJA: mais fininho
        return pygame.Rect(self.x - meia, self.y - topo * s, meia * 2, (topo - fundo) * s)

    # ------------------------------------------------------------ apanhar
    def pode_defender(self, g):
        if g.get("imbloqueavel"):
            return False  # vem de baixo da terra: não dá pra defender, só pular
        r = self.r
        pode = (self.no_chao() and self.estado in ("parado", "andando", "agachado", "defendendo")
                and r in (4, 1))
        if pode and g["nivel"] == "baixo" and r != 1:
            return False
        if pode and g["nivel"] == "alto" and r == 1:
            return False
        return pode

    def levar(self, dano, atacante, g):
        """Tira vida e enche as barras (já com as habilidades de quem bate e de quem apanha)."""
        if atacante:
            dano *= hab.mult_causa(atacante, g)
        dano *= hab.mult_recebe(self, atacante, g)
        if "um_golpe" in self.regras and dano > 0:
            dano = max(dano, self.vida)  # MODO MALUCO: UM GOLPE MATA
        if atacante and atacante is not self and dano > 0:
            dano += hab.bonus_causa(atacante)  # ÁS NA MANGA: +5 em cada ataque
        if atacante and atacante is not self and hab.queima_quem_bate(self, atacante, g):
            atacante.vida = max(0, atacante.vida - hab.ACIDO_DANO)  # SANGUE ÁCIDO: bateu de perto, queimou
            atacante.flash_acido = 16
        self.vida = max(0, self.vida - dano)
        if g and g.get("ultimate") and atacante and atacante is not self:
            self.tomou_ult = atacante.acertou_ult = True
            if g.get("ultimate2"):
                atacante.acertou_ult2 = True
            self.ult_recente = 120  # voando de ultimate não vira transição de cenário
        if g and g.get("ultimate") and "mutacao" in hab.ativas(self) and not self.mutado and atacante \
                and atacante is not self:
            self.mutar(atacante.mutado or atacante.f)
        self.encher(dano * BARRA_APANHAR)
        if atacante and not g.get("ultimate"):
            atacante.encher(dano * BARRA_BATER)

    def voar(self, sinal, vx, vy):
        """Sai voando (vy positivo = pra cima)."""
        malabar, n = self.malabar, self.malabar_n
        self.mudar("voando")
        self.malabar, self.malabar_n = malabar, n
        self.vy = -vy
        self.vx = sinal * vx

    def pode_parry(self, g):
        if g.get("imbloqueavel") or not self.no_chao() or self.estado not in LIVRE:
            return False
        if g["nivel"] == "baixo":
            return self.parry_baixo > 0
        return self.parry_frente > 0

    def receber(self, g, sinal, atacante, forca):
        """Levou um golpe. sinal = pra que lado ele é empurrado. Devolve 'parry', 'def', 'quebrou', 'hit' ou 'esquiva'."""
        if hab.substituicao(self, g, atacante):  # SUBSTITUIÇÃO (Rib): o golpe pega num tronco
            return "esquiva"
        if self.extra.get("intangivel") and not g.get("ultimate") and not hab.sente_tudo(atacante):
            # INTANGÍVEL (Cráquen): o golpe ATRAVESSA (menos do Sphyrus com ELETRORRECEPÇÃO)
            import craquen
            craquen.atravessar_golpe(self)
            return "def"
        if self.pode_parry(g):  # PARRY! não leva nada e fica livre na hora
            self.parry_frente = self.parry_baixo = 0
            self.parry_trava = 0
            self.vx = 0
            self.guarda = min(GUARDA_MAX, self.guarda + 15)
            if self.estado == "andando":
                self.mudar("parado")
            self.parry_brilho = 12
            return "parry"
        if self.pode_defender(g):
            self.guarda -= g.get("guarda_custo", GUARDA_POR_GOLPE + g["dano"] * GUARDA_POR_DANO)
            self.guarda_espera = 0
            if self.guarda <= 0:  # QUEBROU A GUARDA!
                self.guarda = 0
                self.mudar("tonto")
                self.golpe = None
                self.vx = sinal * 3
                self.tremor_hit = 10
                self.quebrou = True  # a partida mostra o efeito
                return "quebrou"
            self.agachado_def = self.r == 1
            self.mudar("defendendo")
            self.tremor_hit = 4
            self.stun = g["defe"]
            self.vx = sinal * g["emp"] * 1.2
            # defendendo ainda tira um pouco (especial pode até nocautear; golpe normal não)
            dano = g["dano"] * forca * (DEFESA_DANO_ESPECIAL if g.get("especial") else DEFESA_DANO)
            self.vida = max(0 if g.get("especial") else 1, self.vida - dano)
            self.encher(10)
            return "def"

        if self.estado == "tonto":
            self.guarda = GUARDA_MAX  # apanhou tonto: acorda com a guarda cheia
        if self.estado in ("golpeado", "voando", "tonto"):
            if atacante:
                atacante.combo += 1
                if atacante.combo == 5:
                    atacante.bonus_amarelo(BONUS_COMBO)
        elif atacante:
            atacante.combo = 1
        if atacante and "poder_magico" in hab.ativas(atacante) and atacante.invisivel <= 0                 and atacante.combo >= hab.limite_combo(atacante, COMBO_MAXIMO):
            atacante.invisivel = INVISIVEL_TEMPO  # PODER MÁGICO: combo máximo = some!
            atacante.flash_invisivel = 24
            som.tocar("puf")
        escala = 1
        if atacante and not g.get("especial"):
            escala = max(0.4, 1 - 0.1 * (atacante.combo - 1))  # combo longo de soco/chute tira menos por golpe
        self.levar(g["dano"] * forca * escala, atacante, g)
        self.ex_fila = []  # (apanhou: perde o resto do EX)
        if hab.armadura(self, g) and self.vida > 0:  # PESO PESADO: nem se mexe
            self.tremor_hit = 6
            return "hit"
        self.golpe = None
        self.tremor_hit = 9
        if self.pose_vista:  # reage na hora, mesmo com a tela congelada
            self.pose_vista = misturar(self.pose_vista, self.poses["golpeado"], 0.75)
        no_ar = not self.no_chao()
        if atacante:  # MAESTRIA DE COMBATE de quem bate deixa o combo no ar mais longo
            self.malabar_lim = hab.limite_combo(atacante, MALABAR_MAX)
        atacante_no_ar = atacante is not None and not atacante.no_chao() and atacante.estado != "agarrado"
        if self.vida <= 0:
            self.voar(sinal, 4, 9)
        elif g.get("lanca"):  # JOGA PRA CIMA
            self.voar(sinal, 1.2, g["lanca"])
            self.malabar, self.malabar_n = True, 0
        elif no_ar and atacante_no_ar and g.get("aereo"):
            self.malabar = True
            self.malabar_n += 1
            if g is GOLPES["ar_chute"] and self.malabar_n >= 2:  # CHUTE PRA BAIXO: quica no chão
                self.voar(sinal, 2, -17)
                self.quica = True
            else:  # combo aéreo: os dois ficam flutuando juntos (o atacante acompanha a distância)
                self.voar(sinal, 0.5, 4.5)
                atacante.vy = min(atacante.vy, -6.2)  # quem bate fica um pouco ACIMA (pra dar o chute pra baixo)
                atacante.vx = self.vx + (self.x - sinal * 46 * atacante.s - atacante.x) / 10
                atacante.ja_atacou = False
                atacante.combo_ar = True
        elif no_ar and self.malabar:  # já estava no ar (quicando): o golpe do chão levanta um tiquinho
            self.malabar_n += 1
            self.voar(sinal, 2, 7)
        elif g.get("derruba") or no_ar:
            vx, vy = g.get("voo", (4, 9))
            self.voar(sinal, vx, vy)
            self.parede_sobe = bool(g.get("parede_sobe"))  # (chute do Tamer: bate na parede e sobe)
            self.voo_forte = g["dano"] >= 10 or bool(g.get("ultimate"))
            self.bonus_parede = g.get("parede", 0)
            self.giro_voo = g.get("giro_voo", 0) * sinal
            self.malabar = False
        elif g.get("paralisa"):  # PARALISADO: fica travado um tempão
            self.mudar("tonto")
            self.tonto_tempo = g["paralisa"]
            self.paralisado = True
            self.vx = sinal * g["emp"]
        else:
            self.mudar("golpeado")
            self.stun = g["hit"]
            self.vx = sinal * g["emp"]
            if atacante and atacante.extra.get("fornalha", 0) > 0:  # MODO FORNALHA (Magnus): queima e PRENDE
                self.stun += hab.FORNALHA_PRENDE
        if atacante and "nevasca" in hab.ativas(atacante):  # NEVASCA (Frigantus)
            hab.nevasca(self)
        return "hit"

    # ------------------------------------------------------------ desenho
    def pose_atual(self):
        est, t = self.estado, self.t
        if est == "ataque":
            g = self.golpe
            quadros = self.memo.get("quadros") or g.get("quadros")
            if quadros:
                p = pose_quadros(quadros, t, self.poses)
            else:
                base, alvo = self.poses[g["base"]], self.poses[g["pose"]]
                if t < g["ini"]:
                    p = misturar(base, alvo, suave(t / g["ini"]))
                elif t < g["ini"] + g["ativo"]:
                    p = alvo
                else:
                    p = misturar(alvo, base, suave(min(1, (t - g["ini"] - g["ativo"]) / g["rec"])))
        elif est == "defendendo":
            p = self.poses["ag_defesa" if self.agachado_def else "defesa"]
        elif est == "tonto":
            balanco = (math.sin(self.t * 0.15) + 1) / 2
            p = misturar(self.poses["golpeado"], self.poses["pouso"], 0.3 + 0.4 * balanco)
        elif est in ("golpeado", "agarrado"):
            p = self.poses["golpeado" if est == "golpeado" else "voando"]
        elif est == "pulando":
            if self.vy < 0:
                p = misturar(self.poses["pulo"], self.poses["pulo_sobe"], min(1, -self.vy / 10))
            else:
                p = misturar(self.poses["pulo"], self.poses["pulo_desce"], min(1, self.vy / 10))
        elif est == "prepulo":
            p = self.poses["prepulo"]
        elif est == "rolando":
            p = self.poses["pulo"]  # todo encolhido
        elif est in ("voando", "caido", "agachado", "vitoria"):
            p = self.poses[est]
        elif est == "levantando":
            p = misturar(self.poses["agachado"], self.poses["parado"], suave(t / 16))
        elif est == "parado" and self.pose_espera and self.pose_espera in self.poses:  # esperando pra falar
            p = dict(self.poses[self.pose_espera])
            b = math.sin(self.t * 0.07)
            for k in ("qd", "pc", "cb"):
                p[k] = (p[k][0], p[k][1] + b * 1.2)
        else:
            if est == "andando":
                p = pose_quadros(CAMINHADA, self.passo % 1, self.poses)
            else:  # respirando: o corpo sobe e desce, os joelhos dobram um tiquinho
                p = dict(self.poses["parado"])
                b = math.sin(self.t * 0.07)
                for k in ("qd", "pc", "cb", "ct", "mt", "cf", "mf"):
                    p[k] = (p[k][0], p[k][1] + b * (1.2 if k == "qd" else 2.0))
                for k in ("jt", "jf"):
                    p[k] = (p[k][0] + b * 0.8, p[k][1] + b * 0.5)
            if self.pouso > 0:
                p = misturar(p, self.poses["pouso"], self.pouso / 8 * 0.7)
        if self.sobrepor:
            p = dict(p)
            p.update(self.sobrepor)
        return p

    def lado(self):
        return -self.dir if self.vira else self.dir

    def ponto(self, p, k):
        """Onde fica na tela o ponto k da pose p (com o giro do corpo)."""
        s, d = self.s, self.lado()
        x, y = self.x + p[k][0] * s * d, self.y - p[k][1] * s
        if self.angulo:
            cx, cy = self.x, self.y - 50 * s
            c, sn = math.cos(self.angulo * d), math.sin(self.angulo * d)
            x, y = cx + (x - cx) * c - (y - cy) * sn, cy + (x - cx) * sn + (y - cy) * c
        return (int(x), int(y))

    def desenhar(self, tela):
        g = self.golpe if self.estado == "ataque" else None
        if g and g.get("efeito_atras"):
            g["efeito_atras"](self, tela)
        self.desenhar_atras(tela)
        p = self.pose_vista or self.pose_atual()
        desenho = (self.disfarce or self.f).get("desenho", desenhar_palito)  # disfarce: o Trafo vira outro lutador
        if self.rastro:
            self.desenhar_rastro(tela, desenho)
        x_real = self.x
        if self.tremor_hit > 0:
            self.x += (2 if self.tremor_hit % 2 else -2) * min(3, self.tremor_hit)
        if self.estado == "ataque" and self.nome_golpe == "giro" and self.t >= self.golpe["ini"]:
            self.vira = (self.t // 5) % 2 == 1  # rodopio
        branco = self.estado in ("golpeado", "voando") and self.t < 6  # pisca branco quando apanha
        if self.inv > 0 and self.estado == "parado" and (self.t // 3) % 2:
            branco = True
        # sombra no chão
        chao = getattr(self, "chao_sombra", CHAO)
        sombra = max(10, int(34 - (chao - self.y) * 0.08))
        if self.y > -50:
            pygame.draw.ellipse(tela, (25, 25, 35), (self.x - sombra, chao - 5, sombra * 2, 10))
        pecas.usar_troca((self.disfarce or self.f).get("troca"))  # roupa alternativa
        pecas.CABECAO = 2.0 if "cabecoes" in self.regras else 1.0
        try:
            if self.tem_tinta():  # SOMBRA / OURO: desenha numa camada separada e pinta ela
                # (só o pedaço em volta do corpo, pelos pontos da pose + uma folga grande: pintar ou varrer a
                # tela inteira todo quadro pesava ~13 ms)
                pts = [self.ponto(p, k) for k in p]
                xs, ys = [q[0] for q in pts], [q[1] for q in pts]
                if "lobo_x" in self.extra:  # (o lobo do Tamer também é desenhado junto)
                    xs.append(self.extra["lobo_x"])
                m = int(90 * self.s)
                r = pygame.Rect(min(xs) - m, min(ys) - m, max(xs) - min(xs) + 2 * m, max(ys) - min(ys) + 2 * m)
                r = r.clip(tela.get_rect())
                if r.w > 0 and r.h > 0:  # (camada da tela toda guardada, mas recortada em r: as posições não mudam)
                    camada = _camada_tinta(tela.get_size())
                    camada.set_clip(r)
                    try:
                        desenho(self, camada, p, branco)
                    finally:
                        camada.set_clip(None)
                    pedaco = camada.subsurface(r)
                    self.aplicar_tinta(pedaco, branco)
                    tela.blit(pedaco, r.topleft)
                    camada.fill((0, 0, 0, 0), r)
            else:
                desenho(self, tela, p, branco)
        finally:
            pecas.usar_troca(None)
            pecas.CABECAO = 1.0
        self.x = x_real
        if g and g.get("efeito"):
            g["efeito"](self, tela)

    def tem_atras(self):
        return bool((self.entrada_t is not None and self.f.get("entrada_atras"))
                    or (self.estado == "vitoria" and self.f.get("vitoria_atras")))

    def desenhar_atras(self, tela):
        """Coisas da entrada/vitória que ficam ATRÁS do lutador (trono, sofá, cápsula...)."""
        if self.entrada_t is not None and self.f.get("entrada_atras"):
            self.f["entrada_atras"](self, tela, self.entrada_t)
        if self.estado == "vitoria" and self.f.get("vitoria_atras"):
            self.f["vitoria_atras"](self, tela, self.t)

    def desenhar_px(self, baixo, peq, grande, px):
        """Desenho pra PIXEL ART: o corpo vai direto na imagem pequena (peq, 1/px do tamanho);
        sombra e rastro vão direto no fundo pequeno; os efeitos dos golpes vão na imagem grande."""
        import corpo
        g = self.golpe if self.estado == "ataque" else None
        if g and g.get("efeito_atras"):
            g["efeito_atras"](self, grande)
        p = self.pose_vista or self.pose_atual()
        desenho = (self.disfarce or self.f).get("desenho", desenhar_palito)  # disfarce: o Trafo vira outro lutador
        guarda = (self.x, self.y, self.s)
        self.x, self.y, self.s = self.x / px, self.y / px, self.s / px
        corpo.BORDA = 1.0
        pecas.usar_troca((self.disfarce or self.f).get("troca"))  # roupa alternativa
        pecas.CABECAO = 2.0 if "cabecoes" in self.regras else 1.0
        try:
            chao = CHAO / px
            sombra = max(5, int((34 - (CHAO - guarda[1]) * 0.08) / px))
            if guarda[1] > -50 and not self.invisivel:
                pygame.draw.ellipse(baixo, (25, 25, 35), (self.x - sombra, chao - 5 / px, sombra * 2, 10 / px))
            if self.rastro and not self.invisivel:
                self.rastro = [(x / px, y / px, pose, ang, vira) for x, y, pose, ang, vira in self.rastro]
                self.desenhar_rastro(baixo, desenho)
                self.rastro = [(x * px, y * px, pose, ang, vira) for x, y, pose, ang, vira in self.rastro]
            if self.estado == "ataque" and self.nome_golpe == "giro" and self.t >= self.golpe["ini"]:
                self.vira = (self.t // 5) % 2 == 1  # rodopio
            branco = self.estado in ("golpeado", "voando") and self.t < 6
            if self.inv > 0 and self.estado == "parado" and (self.t // 3) % 2:
                branco = True
            if self.tremor_hit > 0:
                self.x += (2 if self.tremor_hit % 2 else -2) * min(3, self.tremor_hit) / px
            if not self.esconde:
                desenho(self, peq, p, branco)
                self.aplicar_tinta(peq, branco)
            if self.cortar_chao:  # o que está embaixo da terra não aparece
                chao_px = int(CHAO / px) + 1
                peq.fill((0, 0, 0, 0), (0, chao_px, peq.get_width(), peq.get_height() - chao_px))
            if self.invisivel:  # PODER MÁGICO: quase não dá pra ver (só um vulto tremendo)
                k = min(1.0, self.invisivel / 15, (INVISIVEL_TEMPO - self.invisivel) / 15)
                a = int(255 - (255 - (18 + 14 * ((self.t // 3) % 2))) * k)
                _tingir(peq, (255, 255, 255, a), pygame.BLEND_RGBA_MULT)
            if self.cortar_acima is not None:  # ainda se materializando: de cima não aparece
                peq.fill((0, 0, 0, 0), (0, 0, peq.get_width(), max(0, int(self.cortar_acima / px))))
        finally:
            self.x, self.y, self.s = guarda
            corpo.BORDA = 1.6
            pecas.usar_troca(None)
            pecas.CABECAO = 1.0
        if g and g.get("efeito"):
            g["efeito"](self, grande)
        if self.entrada_t is not None and self.f.get("entrada_efeito"):
            self.f["entrada_efeito"](self, grande, self.entrada_t)
        if self.estado == "vitoria" and self.f.get("vitoria_efeito"):
            self.f["vitoria_efeito"](self, grande, self.t)
        self.desenhar_habilidade(grande)
        if self.f.get("desenhar_sempre"):  # coisas do personagem que ficam no cenário (ex: poças de ácido)
            self.f["desenhar_sempre"](self, grande)
        ult2.desenhar_vivo(self, grande)
        if self.estado == "tonto" and getattr(self, "congelado", False):
            self.desenhar_gelo(grande)
        elif self.estado == "tonto" and getattr(self, "paralisado", False):
            self.desenhar_gosma(grande)
        elif self.estado == "tonto" and getattr(self, "superaquecido", False) and self.f.get("cansado_efeito"):
            self.f["cansado_efeito"](self, grande)
        elif self.estado == "tonto":
            self.desenhar_estrelas(grande)
        if getattr(self, "cansado", False) and self.estado in LIVRE:  # CANSADO: suor pingando
            p = self.pose_vista or self.pose_atual()
            cx, cy = self.ponto(p, "cb")
            stamina.desenhar_cansado(grande, self, self.t, cx, cy - 20 * self.s)

    def efeito_habilidade(self):
        """Tem algum desenho de habilidade aparecendo agora? (ás, fumaça do Maquinário, brilhos)"""
        return (hab.bonus_causa(self) or getattr(self, "flash_invisivel", 0) > 0 or bool(self.extra.get("pocas"))
                or bool(self.extra.get("tela_toda"))  # (efeito longe dele: armadilhas do Silvanus, nuvem do Nocturnus)
                or getattr(self, "flash_ex", 0) > 0 or getattr(self, "flash_escape", 0) > 0
                or self.extra.get("lobo_flash", 0) > 0
                or (self.ex and self.estado == "ataque")
                or getattr(self, "flash_acido", 0) > 0
                or getattr(self, "flash_mutacao", 0) > 0
                or ult2.vivo(self)
                or ("maquinario" in hab.ativas(self) and hab.ligada(self, "maquinario")))

    def desenhar_habilidade(self, tela):
        if "maquinario" in hab.ativas(self) and hab.ligada(self, "maquinario"):  # fumaça e faísca
            p = self.pose_vista or self.pose_atual()
            x, y = self.ponto(p, "pc")
            k = (self.t * 3) % 40
            pygame.draw.circle(tela, (170, 170, 170), (int(x - 10 * self.dir), int(y - k)), int((6 + k * 0.3) * self.s / 1.4))
            if (self.t // 3) % 5 == 0:
                pygame.draw.line(tela, (255, 220, 120), (x, y), (x + 12 * self.dir, y - 10), 2)
        if hab.bonus_causa(self):  # ÁS NA MANGA aceso: um ás dourado girando em cima da cabeça
            p = self.pose_vista or self.pose_atual()
            x, y = self.ponto(p, "cb")
            y -= 50 * self.s
            w = 9 * self.s * max(0.2, abs(math.cos(self.t * 0.12)))
            h = 13 * self.s
            from max10 import brilho
            brilho(tela, (int(x), int(y)), int(22 * self.s), (255, 210, 80), 110)
            pygame.draw.rect(tela, (255, 220, 90), (x - w - 2, y - h - 2, 2 * w + 4, 2 * h + 4), border_radius=3)
            pygame.draw.rect(tela, (250, 248, 236), (x - w, y - h, 2 * w, 2 * h), border_radius=2)
            if w > 3 * self.s:
                pygame.draw.circle(tela, (210, 40, 40), (int(x), int(y)), max(2, int(3 * self.s)))
            if self.as_ativo < 60 and (self.t // 4) % 2:  # piscando quando está pra acabar
                pygame.draw.rect(tela, (255, 255, 255), (x - w, y - h, 2 * w, 2 * h), 2, border_radius=2)
        if self.ex and self.estado == "ataque":  # ESPECIAL EX: brilho dourado em volta
            p = self.pose_vista or self.pose_atual()
            x, y = self.ponto(p, "pc")
            from max10 import brilho
            brilho(tela, (int(x), int(y)), int((38 + 4 * math.sin(self.t * 0.6)) * self.s), (255, 200, 60), 70)
        if getattr(self, "flash_ex", 0) > 0:
            self.flash_ex -= 1
            p = self.pose_vista or self.pose_atual()
            x, y = self.ponto(p, "cb")
            from efeitos import texto_grande
            texto_grande(tela, "EX!", 26, (255, 210, 70), (x, y - 40 * self.s - (26 - self.flash_ex)), contorno=(60, 30, 0))
        if getattr(self, "flash_escape", 0) > 0:  # ESCAPE: onda azul saindo do corpo
            self.flash_escape -= 1
            p = self.pose_vista or self.pose_atual()
            x, y = self.ponto(p, "pc")
            r = int((24 - self.flash_escape) * 7 * self.s)
            pygame.draw.circle(tela, (130, 210, 255), (int(x), int(y)), max(4, r), 4)
            pygame.draw.circle(tela, (230, 245, 255), (int(x), int(y)), max(2, r // 2), 2)
        if getattr(self, "flash_acido", 0) > 0:  # SANGUE ÁCIDO: queimou a mão de quem bateu
            self.flash_acido -= 1
            p = self.pose_vista or self.pose_atual()
            for k in ("mf", "mt"):
                x, y = self.ponto(p, k)
                u = 16 - self.flash_acido
                pygame.draw.circle(tela, (150, 230, 60), (int(x), int(y + u * 1.5)), max(2, int(4 - u * 0.2)))
                pygame.draw.circle(tela, (210, 210, 200), (int(x + 4), int(y - u * 2)), max(1, int(5 - u * 0.3)), 1)
        if getattr(self, "flash_invisivel", 0) > 0:  # PODER MÁGICO: estouro roxo quando some
            self.flash_invisivel -= 1
            p = self.pose_vista or self.pose_atual()
            x, y = self.ponto(p, "pc")
            k = 24 - self.flash_invisivel
            for i in range(10):
                a = i * math.tau / 10 + k * 0.1
                d = (20 + k * 5) * self.s
                pygame.draw.circle(tela, (200, 140, 255), (int(x + math.cos(a) * d), int(y + math.sin(a) * d)), 3)
        if getattr(self, "flash_mutacao", 0) > 0:  # brilho da mutação
            self.flash_mutacao -= 1
            p = self.pose_vista or self.pose_atual()
            x, y = self.ponto(p, "pc")
            r = int((40 + (30 - self.flash_mutacao) * 4) * self.s / 1.4)
            pygame.draw.circle(tela, (230, 200, 90), (int(x), int(y)), r, 3)
            pygame.draw.circle(tela, (255, 245, 200), (int(x), int(y)), r // 2, 2)

    def congelar(self, quadros):
        """CONGELADO (Frigantus): preso num bloco de gelo, sem fazer nada."""
        self.mudar("tonto")
        self.golpe = None
        self.tonto_tempo = quadros
        self.congelado = True
        self.vx = 0

    def desenhar_gelo(self, tela):
        """Congelado: um bloco de gelo azulado em volta do corpo, com brilho."""
        p = self.pose_vista or self.pose_atual()
        pts = [self.ponto(p, k) for k in p]
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        r = pygame.Rect(min(xs) - 10, min(ys) - 10, max(xs) - min(xs) + 20, max(ys) - min(ys) + 14)
        bloco = pygame.Surface(r.size, pygame.SRCALPHA)
        bloco.fill((170, 225, 255, 110))
        pygame.draw.rect(bloco, (230, 248, 255, 200), bloco.get_rect(), 3)
        pygame.draw.line(bloco, (255, 255, 255, 200), (6, 8), (r.w * 0.4, 4), 3)
        pygame.draw.line(bloco, (255, 255, 255, 140), (8, 16), (14, r.h * 0.5), 2)
        tela.blit(bloco, r.topleft)

    def desenhar_gosma(self, tela):
        """Paralisado: coberto de baba amarela e com uns raiozinhos."""
        p = self.pose_vista or self.pose_atual()
        for k, ox in (("cb", -6), ("pc", 8), ("qd", -4), ("mf", 0)):
            x, y = self.ponto(p, k)
            pingo = (self.t * 2 + ox * 3) % 30
            pygame.draw.circle(tela, (210, 220, 120), (int(x + ox * self.s), int(y)), int(7 * self.s))
            pygame.draw.circle(tela, (210, 220, 120), (int(x + ox * self.s), int(y + pingo * self.s)), int(3 * self.s))
        if (self.t // 4) % 2:
            cx, cy = self.ponto(p, "cb")
            for i in range(3):
                a = self.t * 0.3 + i * 2.1
                pygame.draw.line(tela, (255, 255, 160), (cx, cy - 20 * self.s),
                                 (cx + math.cos(a) * 30 * self.s, cy - 20 * self.s + math.sin(a) * 18 * self.s), 2)

    def desenhar_estrelas(self, tela):
        p = self.pose_vista or self.pose_atual()
        cx, cy = self.ponto(p, "cb")
        cy -= 26 * self.s
        for i in range(3):
            a = self.t * 0.12 + i * math.tau / 3
            x, y = cx + math.cos(a) * 26 * self.s, cy + math.sin(a) * 7 * self.s
            pts = [(x + math.cos(k * math.pi / 5 - math.pi / 2) * (8 if k % 2 == 0 else 3.5),
                    y + math.sin(k * math.pi / 5 - math.pi / 2) * (8 if k % 2 == 0 else 3.5)) for k in range(10)]
            pygame.draw.polygon(tela, (255, 230, 80), pts)
            pygame.draw.polygon(tela, (120, 80, 0), pts, 2)

    def desenhar_rastro(self, tela, desenho):
        """Fantasmas dos últimos quadros, ficando transparentes."""
        if getattr(self, "_sup_rastro", None) is None or self._sup_rastro.get_size() != tela.get_size():
            self._sup_rastro = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        guarda = (self.x, self.y, self.angulo, self.vira)
        sup = self._sup_rastro
        for i in (0, len(self.rastro) // 2):
            if i >= len(self.rastro) - 1:
                continue
            x, y, pose, ang, vira = self.rastro[i]
            self.x, self.y, self.angulo, self.vira = x, y, ang, vira
            desenho(self, sup, pose, False)
        # vira uma mancha lisa de uma cor (não aparece braço nem perna do fantasma)
        m = 280 * self.s
        r = pygame.Rect(self.x - m - 200 * self.s, self.y - m - 200 * self.s, m * 2 + 400 * self.s,
                        m + 400 * self.s).clip(sup.get_rect())
        if r.w:
            mancha = pygame.mask.from_surface(sup.subsurface(r)).to_surface(
                setcolor=(*self.f["cor_poder"], 70), unsetcolor=(0, 0, 0, 0))
            tela.blit(mancha, r.topleft)
            sup.fill((0, 0, 0, 0), r)
        self.x, self.y, self.angulo, self.vira = guarda


CAMINHADA = [(0, "andar1"), (0.25, "andar2"), (0.5, "andar3"), (0.75, "andar4"), (1.0, "andar1")]


def pose_quadros(quadros, t, poses=POSES):
    """quadros = [(quadro, pose), ...]. Mistura suave entre o quadro-chave de antes e o de depois."""
    def pega(pz):
        return poses[pz] if isinstance(pz, str) else pz
    if t <= quadros[0][0]:
        return pega(quadros[0][1])
    for (t1, p1), (t2, p2) in zip(quadros, quadros[1:]):
        if t1 <= t < t2:
            return misturar(pega(p1), pega(p2), suave((t - t1) / (t2 - t1)))
    return pega(quadros[-1][1])


def desenhar_palito(l, tela, p, branco):
    s = l.s
    cor = BRANCO if branco else l.f["cor"]
    escura = BRANCO if branco else tuple(int(c * 0.55) for c in l.f["cor"])

    def P(k):
        return l.ponto(p, k)

    larg = max(3, int(6 * s))
    for c, pts in ((escura, ("pt", "jt", "qd")), (escura, ("pc", "ct", "mt")),
                   (cor, ("qd", "pc")),
                   (cor, ("pf", "jf", "qd")), (cor, ("pc", "cf", "mf"))):
        pygame.draw.lines(tela, c, False, [P(k) for k in pts], larg)
        for k in pts:
            pygame.draw.circle(tela, c, P(k), larg // 2)
    pygame.draw.circle(tela, escura, P("mt"), int(6 * s))
    pygame.draw.circle(tela, cor, P("mf"), int(7 * s))
    cx, cy = P("cb")
    pygame.draw.circle(tela, cor, (cx, cy), int(14 * s))
    # olhinho, pra saber pra onde ele olha
    pygame.draw.circle(tela, PRETO, (cx + int(6 * s * l.lado()), cy - int(2 * s)), max(2, int(3 * s)))


import ult2  # noqa: E402  (as 2ª ultimates: no fim pra não dar import circular)


_ARCOS = {}


def _arco_iris(w, h):
    """Faixas diagonais com as cores do arco-íris (guardado: só cria uma vez por tamanho)."""
    chave = (w, h)
    if chave not in _ARCOS:
        sup = pygame.Surface((w + h, h))
        cores = [(255, 90, 90), (255, 180, 70), (255, 240, 90), (110, 240, 120), (90, 200, 255), (150, 110, 255),
                 (240, 110, 230)]
        faixa = max(3, h // 24)
        for i in range(0, w + 2 * h, faixa):
            c = cores[(i // faixa) % len(cores)]
            pygame.draw.polygon(sup, c, [(i - h, h), (i - h + faixa, h), (i + faixa, 0), (i, 0)])
        _ARCOS[chave] = sup
    return _ARCOS[chave]


_CAMADAS = {}


def _camada_tinta(tam):
    """A camada transparente da TINTA (uma por tamanho de tela, reaproveitada: sempre volta limpa)."""
    if tam not in _CAMADAS:
        _CAMADAS[tam] = pygame.Surface(tam, pygame.SRCALPHA)
    return _CAMADAS[tam]


_TINTAS = {}


def _tingir(sup, cor, flag):
    """Pinta a imagem inteira com uma cor (MULT/ADD) usando BLIT de uma cor lisa guardada: é umas 25 vezes
    mais rápido que o fill com special_flags (que pesava ~3,5 ms por lutador todo quadro)."""
    w, h = sup.get_size()
    if len(cor) == 4:  # (alfa arredondado de 16 em 16: no máximo 17 imagens guardadas por cor)
        cor = (*cor[:3], min(255, int(round(cor[3] / 16)) * 16))
    chave = (cor, len(cor) == 4)
    lisa = _TINTAS.get(chave)
    if lisa is None or lisa.get_width() < w or lisa.get_height() < h:
        tam = (max(w, LARGURA, lisa.get_width() if lisa else 0), max(h, ALTURA, lisa.get_height() if lisa else 0))
        lisa = pygame.Surface(tam, pygame.SRCALPHA) if len(cor) == 4 else pygame.Surface(tam)
        lisa.fill(cor)
        _TINTAS[chave] = lisa
    sup.blit(lisa, (0, 0), (0, 0, w, h), special_flags=flag)
