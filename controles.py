"""Quem controla cada lutador: o teclado ou o computador."""
import random

import pygame

from config import *  # noqa: F401,F403
from golpes import GOLPES
import habilidades as hab
from ult2 import VEEM_NO_ESCURO
from lutador import PADRAO, Entrada


class Jogador:
    """Você: WASD pra andar, mouse pra bater, rodinha (M3) + tecla pros especiais.
    Também funciona com CONTROLE DE VIDEOGAME (controle_video.py). No 2 JOGADORES, o jogador 2 é só o controle."""

    def __init__(self, controle="primeiro", teclado=True):
        import controle_video
        if controle == "primeiro":
            controle = controle_video.CONTROLES[0] if controle_video.CONTROLES else None
        self.controle = controle
        self.teclado = teclado
        self.antes_c = {}
        self.antes = {"soco": True, "chute": True}  # o clique que começou a luta não vira soco
        self.armado = 0        # quadros que ainda dá pra soltar especial (rodinha)
        self.m3_antes = False  # a rodinha estava apertada no quadro passado?
        self.desde_solta = 999  # quadros desde que soltou a rodinha
        self.ex_armado = False  # deu TOQUE E SEGURA na rodinha: o especial sai EX
        self.guardado = None   # especial apertado, esperando o lutador ficar livre
        self.guardado_t = 0

    def ler(self, bruto, eu, ele, jogo):
        if not self.teclado:  # (jogador 2: só o controle)
            return self.ler_controle(Entrada(), Entrada())
        keys, mouse = bruto
        h = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        v = (keys[pygame.K_w] or keys[pygame.K_UP]) - (keys[pygame.K_s] or keys[pygame.K_DOWN])
        d = 5 + h + 3 * v
        # só conta no quadro em que aperta (segurar não fica socando)
        agora = {"soco": mouse[MOUSE_SOCO - 1], "chute": mouse[MOUSE_CHUTE - 1], ULTIMATE: keys[ULTIMATE],
                 PROVOCA: keys[PROVOCA], BARRA_TECLA: keys[BARRA_TECLA], TROCA_TECLA: keys[TROCA_TECLA],
                 pygame.K_x: keys[pygame.K_x], ULTIMATE2: keys[ULTIMATE2]}
        for k in ESPECIAIS:
            agora[k] = keys[k]
        novo = {k: bool(a) and not self.antes.get(k) for k, a in agora.items()}
        self.antes = agora

        m3 = bool(mouse[MOUSE_ARMAR - 1])
        apertou_m3 = m3 and not self.m3_antes
        if apertou_m3:  # toque e segura (clique duplo na rodinha) = EX
            self.ex_armado = self.desde_solta <= DUPLO_M3
        if m3:
            self.desde_solta = 0 if not self.m3_antes else self.desde_solta
        elif self.m3_antes:
            self.desde_solta = 0
        else:
            self.desde_solta += 1
        self.m3_antes = m3
        duplo = apertou_m3 and self.ex_armado
        if m3:
            self.armado = JANELA_M3
        elif self.armado > 0:
            self.armado -= 1
        if not self.armado:
            self.ex_armado = False
        ex_agora = self.ex_armado  # (guardado antes do especial "gastar" a rodinha)
        if getattr(jogo, "choque", None):  # CHOQUE: nenhum especial fica guardado pra sair depois
            self.armado = self.guardado_t = 0
        if self.armado:
            esp = "Z" if novo[ULTIMATE] else "Z2" if novo[ULTIMATE2] else next((n for k, n in ESPECIAIS.items() if novo[k]), None)
            if esp:
                self.armado = 0
                self.guardado, self.guardado_t = esp, 8
        # o especial fica "guardado" uns quadros, pra sair mesmo se apertou um tiquinho antes da hora
        esp = None
        if self.guardado_t > 0:
            self.guardado_t -= 1
            esp = self.guardado
        e = Entrada(d, novo["soco"], novo["chute"], esp)
        e.segura_ult = bool(keys[ULTIMATE])
        e.provoca = novo[PROVOCA]
        e.barra = bool(keys[BARRA_TECLA]) or ex_agora  # (F ainda funciona também)
        e.barra_toque = novo[BARRA_TECLA] or duplo  # apanhando: clique duplo na rodinha = ESCAPE
        e.troca = novo[TROCA_TECLA]
        e.lobo = novo[pygame.K_x]
        return self.ler_controle(e, e) if self.controle is not None else e

    def ler_controle(self, e, teclado):
        """Junta o que está apertado no controle de videogame com o teclado."""
        import controle_video
        try:
            st = controle_video.estado(self.controle)
        except Exception:  # (controle desligou no meio)
            return teclado
        novo = {k: st[k] and not self.antes_c.get(k)
                for k in ("soco", "chute", "E", "Q", "R", "SHIFT", "Z", "provoca", "barra", "troca", "lobo")}
        self.antes_c = st
        if st["h"] or st["v"]:
            e.dir = 5 + st["h"] + 3 * st["v"]
        e.soco = e.soco or novo["soco"]
        e.chute = e.chute or novo["chute"]
        e.segura_ult = getattr(e, "segura_ult", False) or st["Z"]
        e.provoca = getattr(e, "provoca", False) or novo["provoca"]
        e.barra = getattr(e, "barra", False) or st["barra"]
        e.barra_toque = getattr(e, "barra_toque", False) or novo["barra"]
        e.troca = getattr(e, "troca", False) or novo["troca"]
        e.lobo = getattr(e, "lobo", False) or novo["lobo"]
        esp = next((b for b in ("E", "Q", "R", "SHIFT", "Z") if novo[b]), None)
        if esp:  # no controle o especial sai direto (sem segurar nada)
            self.guardado, self.guardado_t = esp, 8
        if self.guardado_t > 0 and not self.teclado:
            self.guardado_t -= 1
            e.especial = self.guardado
        elif esp:
            e.especial = esp
        return e


PARRY_BOT_ESPERA = 180  # o computador tenta parry no máximo 1 vez a cada 3 segundos


class Computador:
    # (chance de defender quando vê o golpe, quadros parado pensando, tempo de reação em quadros)
    # O tempo de reação é como o de gente: soco e chute rápidos chegam antes dela conseguir reagir.
    NIVEIS = {"FÁCIL": (0.35, 26, 22), "MÉDIO": (0.6, 14, 15), "DIFÍCIL": (0.85, 6, 10)}
    # quanto tempo (quadros) ela espera pra usar o MESMO especial de novo (não fica spammando)
    RECARGA = {"FÁCIL": 480, "MÉDIO": 330, "DIFÍCIL": 220}
    BOTOES = ("E", "Q", "R", "SHIFT", "Z")

    def __init__(self, nivel="MÉDIO"):
        self.chance, self.atraso, self.reacao = self.NIVEIS[nivel]
        self.ja_pensou = None  # o último golpe/bola que ela já decidiu se ia defender (decide uma vez só)
        self.nivel = nivel
        self.usou = {}         # botão de especial -> quadro em que usou por último
        self.relogio = 0
        self.parry = {"FÁCIL": 0.0, "MÉDIO": 0.04, "DIFÍCIL": 0.12}[nivel]  # (o Gomes: "o bot dá MUITO parry")
        self.parry_espera = 0  # depois de tentar um parry, espera um tempo pra tentar de novo
        self.plano = []
        self.espera = 0
        self.segurando = 5
        import ia
        self.cerebro = ia.Cerebro(nivel)  # BOT ESPERTO (v4.0): pune spam, aprende com você, varia o estilo

    @staticmethod
    def botao(eu, tipo):
        """Qual botão do meu personagem faz um golpe desse tipo (longe, perto, medio, anti, ultimate)?"""
        opcoes = [b for b, n in eu.f.get("golpes", PADRAO).items() if GOLPES[n].get("ia") == tipo]
        return random.choice(opcoes) if opcoes else None

    ESCAPE = {"FÁCIL": 0.0, "MÉDIO": 0.02, "DIFÍCIL": 0.06}  # chance (por quadro) de escapar de um combo longo

    # CHOQUE: chance de apertar por quadro (uma criança clica uns 6-8 por segundo = 0,10-0,13 por quadro)
    APERTA_CHOQUE = {"FÁCIL": 0.08, "MÉDIO": 0.11, "DIFÍCIL": 0.14}

    def ler(self, keys, eu, ele, jogo):
        self.relogio += 1
        self.parry_espera -= 1
        if getattr(jogo, "choque", None):  # CHOQUE: aperta botão o mais rápido que der
            return Entrada(5, random.random() < self.APERTA_CHOQUE.get(self.nivel, 0.15))
        self.cerebro.observar(eu, ele, jogo)
        g_dele = ele.golpe if ele.estado == "ataque" else None
        no_normal = g_dele is not None and not g_dele.get("especial")  # (escapar NO MEIO de especial é paia: só de soco/chute)
        if (eu.estado in ("golpeado", "voando") and ele.combo >= 4 and eu.barra >= ESCAPE_CUSTO and no_normal
                and random.random() < self.ESCAPE[self.nivel]):
            e = Entrada(5)
            e.barra_toque = True  # ESCAPE de combo!
            return e
        # jogou o outro pra cima? pula atrás e faz combo aéreo (soco, soco, chute pra baixo)
        g = eu.golpe if eu.estado == "ataque" else None
        if (g and (g.get("lanca") or g.get("lanca_depois")) and eu.acertou and ele.estado == "voando"
                and ele.malabar and not self.plano and random.random() < self.chance):
            self.plano = [(8, None)] * 4  # pulo de perseguição
        # no ar, do lado dele: soco, soco... e o chute pra baixo no final
        if (eu.estado == "pulando" and not eu.no_chao() and not eu.ja_atacou and eu.perseguindo == 0
                and ele.estado == "voando" and ele.malabar and abs(ele.x - eu.x) < 120):
            return Entrada(5, chute=ele.malabar_n >= 3, soco=ele.malabar_n < 3)
        if self.plano:
            d, b = self.plano.pop(0)
            if b in self.BOTOES:
                return Entrada(d, especial=b)
            return Entrada(d, b == "s", b == "c")
        urgente = self.cerebro.urgente(eu, ele, jogo, self.reacao)  # combo, cansaço, punir, spam
        if urgente is not None:
            return urgente

        frente = 6 if ele.x > eu.x else 4
        tras = 10 - frente
        dist = abs(ele.x - eu.x)
        livre = eu.estado in ("parado", "andando", "agachado", "defendendo")

        def esp(tipo):
            b = self.botao(eu, tipo)
            recarga = self.RECARGA[self.nivel] if tipo == "longe" else self.RECARGA[self.nivel] // 3
            if tipo != "ultimate" and not self.cerebro.pode(eu, b):
                return Entrada(self.segurando)  # (recarga do jogo ou sem stamina)
            if not b or self.relogio - self.usou.get(b, -9999) < recarga:
                return Entrada(self.segurando)  # ainda recarregando: faz outra coisa
            self.usou[b] = self.relogio
            e = Entrada(5, especial=b)
            e.barra = eu.barra >= 600 and random.random() < 0.3  # às vezes sai EX
            return e

        # ---- defesa: só reage depois do tempo de reação, e decide UMA vez por golpe ----
        bola = next((p for p in jogo.projeteis if p.dono is ele and abs(p.x - eu.x) < 240
                     and (p.x - eu.x) * p.vx < 0 and p.t >= self.reacao), None)
        atacando = ele.estado == "ataque"
        carregando = (atacando and ele.golpe.get("ia") in ("longe", "ultimate")
                      and not ele.golpe.get("proj") and ele.t >= self.reacao)
        ataque = atacando and dist < 190 and self.reacao <= ele.t < ele.golpe["ini"] + ele.golpe["ativo"]
        visto = None
        if bola:
            visto = id(bola)
        elif ataque or carregando:
            visto = (ele.nome_golpe, jogo.tf - ele.t)  # este golpe, que começou neste quadro
        if visto is not None and visto != self.ja_pensou and livre:
            self.ja_pensou = visto
            ve_tudo = "eletro" in hab.ativas(eu)  # ELETRORRECEPÇÃO: vê até quem está invisível
            chance = self.chance * (0.25 if getattr(ele, "invisivel", 0) > 0 and not ve_tudo else 1)  # invisível: quase não vê
            if ele.extra.get("cacada", 0) > 0 and eu.f.get("nome_base", eu.f["nome"]) not in VEEM_NO_ESCURO:
                chance *= 0.4  # CAÇADA NO ESCURO: quase não vê o Tromos
            if random.random() >= chance:
                return Entrada(self.segurando)  # não deu tempo / não viu
        else:
            bola = ataque = carregando = False
        if livre and (bola or ataque or carregando):
            b = self.botao(eu, "contra") if ataque else None  # CONTRA-ATAQUE (Inazumaneko): reage ao golpe de perto
            if b and not ele.golpe.get("proj") and random.random() < 0.5:
                self.usou[b] = self.relogio
                return Entrada(5, especial=b)
            if ataque and self.parry_espera <= 0 and random.random() < self.parry * self.cerebro.mult_parry():  # tenta o parry
                self.parry_espera = PARRY_BOT_ESPERA
                baixo = ele.golpe["nivel"] == "baixo"
                falta = max(0, ele.golpe["ini"] - ele.t - 3 + random.randint(-4, 4))  # às vezes erra o tempo
                self.plano = [(5, None)] * falta + [(2 if baixo else frente, None)] + [(5, None)] * 10
            elif (bola or carregando) and random.random() < 0.3:
                self.plano = [(frente + 3, None)] + [(5, None)] * 14 + [(5, "c")]  # pula por cima
            else:
                baixo = ataque and ele.golpe["nivel"] == "baixo"
                self.plano = [(tras - 3 if baixo else tras, None)] * 16
            return Entrada(5)

        # ---- anti-aéreo: ele pulou em cima de mim ----
        pulou_perto = not ele.no_chao() and ele.y > 0 and dist < 150 and ele.t >= self.reacao
        if livre and pulou_perto and random.random() < self.chance * 0.15 * self.cerebro.mult_anti():
            b = self.botao(eu, "anti")
            if b:
                return Entrada(5, especial=b)

        if self.espera > 0:
            self.espera -= 1
            return Entrada(self.segurando)
        self.espera = self.atraso + random.randint(0, self.atraso)
        self.segurando = 5

        if not livre:
            return Entrada(5)
        neutro = self.cerebro.neutro(eu, ele, jogo)  # estilo do round, o que aprendeu, a própria stamina
        if neutro is not None:
            if not (neutro.soco or neutro.chute or neutro.especial):
                self.segurando = neutro.dir
            return neutro
        if eu.barra >= BARRA_TOTAL and eu.tem_ult2() and dist < 600 and random.random() < 0.3:
            return Entrada(5, especial="Z2")  # 2ª ULTIMATE (a amarela encheu)
        gz = GOLPES.get(eu.f.get("golpes", PADRAO).get("Z", ""), {})
        alcance_z = gz.get("ia_alcance", 600)  # (ultimate só de perto: Corte Samurai do Inazumaneko)
        if eu.barra >= BARRA_MAX and dist < alcance_z and random.random() < (0.15 if eu.tem_ult2() else 0.3):  # (às vezes espera a amarela)
            return esp("ultimate")
        if eu.barra >= BARRA_MAX and alcance_z < 600 and dist >= alcance_z:
            self.segurando = frente  # (chega perto pra soltar a ultimate)
        x = random.random()
        if dist > 280:
            if x < 0.25 * self.cerebro.mult_longe():
                return esp("longe")
            self.segurando = frente
        elif dist > 110:
            if x < 0.15:
                self.plano = [(frente + 3, None)] + [(5, None)] * 16 + [(5, "c")]
            elif x < 0.3:
                return esp("longe")
            elif x < 0.42:
                return esp("medio")
            elif x < 0.5:
                self.segurando = tras
            else:
                self.segurando = frente
        else:
            if x < 0.18:
                return Entrada(5, soco=True)
            if x < 0.3:
                return Entrada(5, chute=True)
            if x < 0.42:
                return Entrada(frente - 3, chute=True)  # rasteira
            if x < 0.52:
                b = self.botao(eu, "medio")
                if random.random() < 0.5:
                    self.plano = [(5, "s")] + [(5, None)] * 5 + [(5, "s")] + [(5, None)] * 5 + [(5, "c")]  # soco, soco, chute
                else:
                    self.plano = [(5, "s")] + [(5, None)] * 5 + [(5, b)]  # soco + especial (combo)
                return Entrada(5)
            if x < 0.6 and self.botao(eu, "perto"):
                return esp("perto")
            if x < 0.72:
                self.segurando = tras
            elif x < 0.82:
                self.segurando = tras - 3  # fica agachado defendendo
            else:
                return Entrada(5, chute=True)
        return Entrada(self.segurando)


class BonecoTreino:
    """O parceiro do modo treino. Teclas 1 a 5 trocam o que ele faz."""
    MODOS = ["PARADO", "DEFENDE", "PULA", "AGACHADO", "LUTA"]

    def __init__(self):
        self.modo = "PARADO"
        self.t = 0
        self.cpu = Computador("FÁCIL")

    def ler(self, keys, eu, ele, jogo):
        self.t += 1
        frente = 6 if ele.x > eu.x else 4
        tras = 10 - frente
        if self.modo == "DEFENDE":  # defende tudo (agachado contra golpe baixo)
            vindo = any(pr.dono is ele for pr in jogo.projeteis)
            if (ele.estado == "ataque" and ele.golpe) or vindo:
                baixo = ele.estado == "ataque" and ele.golpe and ele.golpe.get("nivel") == "baixo"
                return Entrada(tras - 3 if baixo else tras)
            return Entrada(5)
        if self.modo == "PULA":
            return Entrada(8 if self.t % 50 < 3 else 5)
        if self.modo == "AGACHADO":
            return Entrada(2)
        if self.modo == "LUTA":
            return self.cpu.ler(keys, eu, ele, jogo)
        return Entrada(5)
