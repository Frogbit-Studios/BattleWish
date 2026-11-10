"""BOT ESPERTO (v4.0, pedido do Gomes): o cérebro que o Computador usa por cima do jeito antigo.

O que ele faz (quanto mais difícil, mais ele faz direito):
  1. PUNE O SPAM: percebe quando você fica apertando sem parar, segura a defesa, tenta parry/rolamento
     e, quando você CANSA (stamina zerou) ou termina um golpe perto dele, entra com um COMBO de verdade.
  2. JOGA BEM OS DIFÍCEIS: cada lutador tem os combos dele (os mesmos do treino de combos, todos testados)
     e uns papéis por especial (anti-aéreo, fura-guarda, chegar perto, punir), com dicas pros difíceis.
  3. APRENDE COM VOCÊ: conta o que você mais faz (pular, defender em pé ou agachado, atirar de longe, rolar)
     e muda a resposta: mais anti-aéreo, mais rasteira, mais pulo por cima, mais fura-guarda...
  4. VARIA O JEITO: cada round (e às vezes no meio) escolhe um estilo: AGRESSIVO, DEFENSIVO, DE LONGE ou CONTRA-ATAQUE.
  E cuida da PRÓPRIA STAMINA: não fica sem fôlego à toa.
"""
import random

import stamina
from config import *  # noqa: F401,F403
from golpes import GOLPES
from lutador import Entrada, PADRAO

# quanto o bot "sabe jogar" em cada nível (chance de fazer a coisa certa quando vê a chance)
HABILIDADE = {"FÁCIL": 0.12, "MÉDIO": 0.45, "DIFÍCIL": 0.85}
APRENDE = {"FÁCIL": False, "MÉDIO": True, "DIFÍCIL": True}
# combos que cada nível usa (índices da lista de combos do lutador: 0 = O BÁSICO ... 4 = COMBO AÉREO)
COMBOS_NIVEL = {"FÁCIL": (0,), "MÉDIO": (0, 1, 2), "DIFÍCIL": (0, 2, 3, 4)}
ESTILOS = ("AGRESSIVO", "DEFENSIVO", "DE LONGE", "CONTRA-ATAQUE")
LIVRE = ("parado", "andando", "agachado", "defendendo")
SPAM_JANELA = 150   # quadros que ele olha pra trás pra ver se você está spammando
SPAM_GOLPES = 5     # tantos golpes nessa janela = spam

# DICAS dos lutadores difíceis (o resto ele descobre sozinho pelos golpes)
DICAS = {
    "SPHYRUS": dict(anti="Q", fura_guarda="SHIFT", punir="R", chegar="SHIFT"),
    "KUN": dict(anti="Q", punir="R", chegar="SHIFT"),
}


def _papeis(ficha):
    """Descobre pra que serve cada especial do lutador olhando os números do golpe."""
    nome = ficha.get("nome_base", ficha["nome"])
    golpes = ficha.get("golpes", PADRAO)
    papeis = {}
    perto = []
    for b in ("E", "Q", "R", "SHIFT"):
        g = GOLPES.get(golpes.get(b, ""), None)
        if not g:
            continue
        if g.get("imbloqueavel"):
            papeis.setdefault("fura_guarda", b)
        if (g.get("sobe") or g.get("lanca")) and g.get("ini", 99) <= 10:
            papeis.setdefault("anti", b)
        if not g.get("proj") and g.get("ia") in ("perto", "medio", "contra") and g.get("ini", 99) <= 12:
            perto.append((g.get("dano", 0), b))
        if g.get("ia") == "contra":
            papeis.setdefault("contra", b)
    if perto:
        papeis.setdefault("punir", max(perto)[1])
    papeis.update(DICAS.get(nome, {}))
    return papeis


class Cerebro:
    def __init__(self, nivel):
        self.nivel = nivel if nivel in HABILIDADE else "MÉDIO"
        self.hab = HABILIDADE[self.nivel]
        self.q = 0
        self.estilo = "AGRESSIVO"         # (sorteia de verdade no 1º quadro da luta: criar o bot não mexe no sorteio)
        self.estilo_t = 0
        self.rounds_vistos = None
        self.ataques_dele = []           # quadros em que ele começou um golpe
        self.golpe_visto = None
        self.estado_dele = None
        self.aberto_t = 0                # há quantos quadros ele está "aberto" (cansado / terminando golpe)
        self.combo = None                # combo em andamento: dict(botoes, i, espera)
        self.papeis = None
        self.lutador = None
        # o que ele aprendeu de você (vai esquecendo devagar)
        self.m = dict(pulos=0.0, def_pe=0.0, def_baixo=0.0, tiros=0.0, rolou=0.0, spam=0.0)

    # ------------------------------------------------------------ olhar
    def observar(self, eu, ele, jogo):
        self.q += 1
        if self.lutador is not eu.f:
            self.lutador, self.papeis = eu.f, _papeis(eu.mutado or eu.f)
        rounds = tuple(getattr(jogo, "vitorias", (0, 0)))
        if rounds != self.rounds_vistos:  # ROUND NOVO: estilo novo
            self.rounds_vistos = rounds
            self.trocar_estilo()
        self.estilo_t += 1
        if self.estilo_t > 900 and random.random() < 0.002:  # às vezes muda no meio do round
            self.trocar_estilo()
        if self.q % 60 == 0:  # esquece devagar (o que você fez há muito tempo vale menos)
            for k in self.m:
                self.m[k] *= 0.93
        # golpe novo dele?
        gid = (getattr(ele, "golpe_id", 0), ele.nome_golpe) if ele.estado == "ataque" else None
        if gid and gid != self.golpe_visto:
            self.golpe_visto = gid
            g = ele.golpe or {}
            if not g.get("ultimate"):
                self.ataques_dele.append(self.q)
            if g.get("aereo"):
                self.m["pulos"] += 1
            if g.get("proj"):
                self.m["tiros"] += 1
        if ele.estado != self.estado_dele:
            if ele.estado == "prepulo":
                self.m["pulos"] += 0.6
            elif ele.estado == "defendendo":
                self.m["def_baixo" if ele.agachado_def else "def_pe"] += 1
            elif ele.estado == "rolando":
                self.m["rolou"] += 1
            self.estado_dele = ele.estado
        self.ataques_dele = [t for t in self.ataques_dele if self.q - t < SPAM_JANELA]
        if self.spammando():
            self.m["spam"] += 0.02
        # ele está aberto pra levar um combo?
        self.aberto_t = self.aberto_t + 1 if self.aberto(ele) else 0

    def trocar_estilo(self):
        antes = self.estilo
        opcoes = [e for e in ESTILOS if e != antes] if self.nivel != "FÁCIL" else ["AGRESSIVO", "DEFENSIVO"]
        if APRENDE[self.nivel] and self.m["spam"] > 1:
            opcoes += ["CONTRA-ATAQUE"] * 2  # você spamma: ele joga mais no contra-ataque
        if APRENDE[self.nivel] and self.m["tiros"] > 4:
            opcoes += ["AGRESSIVO"]          # você fica atirando de longe: ele vem pra cima
        self.estilo = random.choice(opcoes)
        self.estilo_t = 0

    def spammando(self):
        return len(self.ataques_dele) >= SPAM_GOLPES

    @staticmethod
    def aberto(ele):
        if getattr(ele, "cansado", False) and ele.no_chao():
            return True
        if ele.estado in ("tonto",):
            return True
        if ele.estado == "ataque" and ele.golpe and not ele.golpe.get("ultimate"):
            g = ele.golpe
            fim_ativo = max(b for _, b in (g.get("janelas") or ((g["ini"], g["ini"] + g["ativo"]),)))
            falta = g["total"] - ele.t
            return ele.t >= fim_ativo and falta >= 6 and not g.get("logica")
        return False

    # ------------------------------------------------------------ ajudas
    def pode(self, eu, b):
        """Pode usar o especial b agora (tem, recarregou, tem fôlego)?"""
        if not b:
            return False
        nome = (eu.mutado or eu.f).get("golpes", PADRAO).get(b)
        g = GOLPES.get(nome or "", None)
        if not g or not stamina.pode_especial(eu, b):
            return False
        return eu.stamina >= stamina.custo(nome, g) * 0.9 or not stamina.ligado(eu)

    def alcance(self, eu):
        return 92 * eu.s

    def escolher_combo(self, eu):
        import combos
        lista = combos.combos_de(eu.mutado or eu.f)
        ok = []
        for i in COMBOS_NIVEL[self.nivel]:
            if i >= len(lista):
                continue
            c = lista[i]
            if combos.de_longe(c["passos"][0]):
                continue
            esp = [p for p in c["botoes"] if p in ("E", "Q", "R", "SHIFT")]
            if all(self.pode(eu, b) for b in esp):
                ok.append(c)
        if not ok:
            return None
        custo = sum(stamina.custo(p, GOLPES.get(p, {})) for p in ok[-1]["passos"] if p in GOLPES)
        if stamina.ligado(eu) and eu.stamina < custo * 0.8:
            ok = ok[:1]  # pouca stamina: só o básico
        return dict(botoes=list(random.choice(ok)["botoes"]), i=0, espera=0)

    def tocar_combo(self, eu, ele):
        """Aperta o próximo passo do combo quando o golpe de agora já acertou."""
        c = self.combo
        if c["i"] >= len(c["botoes"]):
            self.combo = None
            return None
        passo = c["botoes"][c["i"]]
        frente = 6 if ele.x > eu.x else 4
        if c["i"] > 0:
            if eu.estado == "ataque" and not eu.acertou:
                if eu.t > eu.golpe["ini"] + eu.golpe["ativo"] + 2:
                    self.combo = None  # errou: o combo caiu
                return Entrada(5)
            if eu.estado in ("parado", "andando", "agachado") and passo not in ("ar_soco", "ar_chute"):
                c["espera"] += 1
                if c["espera"] > 3:
                    self.combo = None  # passou a hora
                    return None
            if eu.estado == "ataque" and eu.t < eu.golpe["ini"] + 1:
                return Entrada(5)
        if passo in ("ar_soco", "ar_chute"):
            if eu.no_chao() and eu.estado == "ataque":
                return Entrada(8)  # segura CIMA: pulo de perseguição
            if eu.no_chao():
                self.combo = None
                return None
            if eu.perseguindo or abs(ele.y - eu.y) > 90 or abs(ele.x - eu.x) > 110:
                return Entrada(5)
        c["i"] += 1
        c["espera"] = 0
        if passo in ("soco", "chute", "ar_soco", "ar_chute"):
            return Entrada(5, soco=passo.endswith("soco"), chute=passo.endswith("chute"))
        if passo in ("ag_soco", "ag_chute"):
            return Entrada(2, soco=passo == "ag_soco", chute=passo == "ag_chute")
        return Entrada(5 if abs(ele.x - eu.x) < 400 else frente, especial=passo)

    # ------------------------------------------------------------ decidir
    def urgente(self, eu, ele, jogo, reacao):
        """Antes de tudo: combo em andamento, cansado, PUNIR e CONTRA O SPAM. Entrada ou None."""
        frente = 6 if ele.x > eu.x else 4
        tras = 10 - frente
        dist = abs(ele.x - eu.x)
        livre = eu.estado in LIVRE

        if self.combo is not None:
            if eu.estado in ("golpeado", "voando", "caido", "tonto", "defendendo"):
                self.combo = None
            else:
                e = self.tocar_combo(eu, ele)
                if e is not None:
                    return e

        g_dele = ele.golpe if ele.estado == "ataque" else None
        baixo = bool(g_dele and g_dele.get("nivel") == "baixo")

        # ---- CANSADO: só defende (e torce) ----
        if getattr(eu, "cansado", False):
            return Entrada(tras - 3 if baixo else tras) if random.random() < self.hab + 0.1 else Entrada(5)

        # ---- 1. PUNIR: ele cansou ou terminou um golpe perto de mim ----
        if livre and self.aberto_t >= max(1, reacao // 2):
            cansou = getattr(ele, "cansado", False)
            if dist > self.alcance(eu) and cansou:
                if random.random() < self.hab + 0.15:
                    return Entrada(frente)  # corre pra cima de quem cansou
            elif dist <= self.alcance(eu) and random.random() < self.hab * (1.0 if cansou else 0.6):
                punir = self.papeis.get("punir")
                if not cansou and punir and self.pode(eu, punir) and random.random() < 0.4:
                    return Entrada(5, especial=punir)
                self.combo = self.escolher_combo(eu)
                if self.combo:
                    return self.tocar_combo(eu, ele)
                return Entrada(5, soco=True)

        # ---- 2. CONTRA O SPAM: segura a defesa, às vezes rola pra fora ----
        if livre and self.spammando() and g_dele and dist < 200 and random.random() < self.hab:
            if eu.no_chao() and random.random() < 0.06 * self.hab and eu.estado != "defendendo":
                return Entrada(tras, soco=True, chute=True)  # ROLA pra trás (sai do canto)
            return Entrada(tras - 3 if baixo else tras)

        return None

    def neutro(self, eu, ele, jogo):
        """Na hora de pensar o que fazer (nada urgente): stamina, o que aprendeu, estilo. Entrada ou None."""
        frente = 6 if ele.x > eu.x else 4
        tras = 10 - frente
        dist = abs(ele.x - eu.x)
        g_dele = ele.golpe if ele.estado == "ataque" else None
        # ---- 3. CUIDA DA PRÓPRIA STAMINA ----
        if stamina.ligado(eu) and eu.stamina < 28 and random.random() < self.hab:
            return Entrada(tras if dist < 160 else 5)  # se afasta pra respirar
        aprende = APRENDE[self.nivel]

        # ---- 4. APRENDEU COM VOCÊ ----
        if aprende and dist < 160 and not g_dele:
            # você defende muito EM PÉ: rasteira
            if self.m["def_pe"] > 3 and self.m["def_pe"] > self.m["def_baixo"] * 2 and random.random() < 0.05 * self.hab:
                if dist > self.alcance(eu) * 0.9:
                    return Entrada(frente)
                return Entrada(frente - 3, chute=True)
            # você defende muito AGACHADO: pula por cima com chute
            if self.m["def_baixo"] > 3 and self.m["def_baixo"] > self.m["def_pe"] and random.random() < 0.03 * self.hab:
                return Entrada(frente + 3)
            # você só fica defendendo: fura-guarda
            fg = self.papeis.get("fura_guarda")
            if ele.estado == "defendendo" and fg and self.pode(eu, fg) and random.random() < 0.08 * self.hab:
                return Entrada(5, especial=fg)
        # você pula muito: espera embaixo com o anti-aéreo
        if aprende and not ele.no_chao() and dist < 170 and self.m["pulos"] > 2:
            anti = self.papeis.get("anti")
            if anti and self.pode(eu, anti) and random.random() < 0.25 * self.hab:
                return Entrada(5, especial=anti)
        # você fica atirando de longe: chega perto (pulo ou especial de chegar)
        if aprende and dist > 260 and self.m["tiros"] > 3 and random.random() < 0.1 * self.hab:
            chegar = self.papeis.get("chegar")
            if chegar and self.pode(eu, chegar) and random.random() < 0.5:
                return Entrada(5, especial=chegar)
            return Entrada(frente + 3)

        # ---- 5. ESTILO DO ROUND ----
        if self.estilo == "AGRESSIVO" and dist > 120 and random.random() < 0.5 * self.hab:
            return Entrada(frente)
        if self.estilo == "DEFENSIVO" and dist < 140 and not g_dele and random.random() < 0.25 * self.hab:
            return Entrada(tras)
        if self.estilo == "DE LONGE":
            if dist < 200 and random.random() < 0.3 * self.hab:
                return Entrada(tras)
        if self.estilo == "CONTRA-ATAQUE" and dist < 150 and not g_dele and random.random() < 0.4 * self.hab:
            return Entrada(tras)  # fica na defesa esperando você errar
        return None

    # o jeito antigo pergunta isso:
    def mult_anti(self):
        return 1 + min(3.0, self.m["pulos"] * 0.4) if APRENDE[self.nivel] else 1

    def mult_parry(self):
        return 1 + (1.5 if self.spammando() and APRENDE[self.nivel] else 0)

    def mult_longe(self):
        return {"DE LONGE": 2.0, "AGRESSIVO": 0.5}.get(self.estilo, 1.0)
