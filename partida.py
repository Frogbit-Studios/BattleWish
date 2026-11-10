"""Uma partida: rounds, tempo, quem acertou quem, barras de vida e efeitos."""
import math
import random

import pygame

from config import *  # noqa: F401,F403
import habilidades as hab
import save
import som
import stamina
import ult2
from golpes import GOLPES
from efeitos import Cenario, Impactos, fonte, mistura_cor, moeda, texto, texto_grande, texto_moedas
from lutador import Entrada, Lutador

_cenario = None


def cenario():
    """O fundo parado (pros menus)."""
    global _cenario
    if _cenario is None:
        _cenario = Cenario()
    return _cenario.fundo


class Partida:
    def __init__(self, ficha1, ficha2, ctrl1, ctrl2, treino=False, cenario_nome=None, trio=None):
        self.trio = trio      # TRIO: ([3 fichas do lado 1], [3 fichas do lado 2]) — troca no meio da luta
        self.regras = set()   # MODOS MALUCOS ligados (o luta.py preenche)
        if trio:
            ficha1, ficha2 = trio[0][0], trio[1][0]
        self.treino = treino  # MODO TREINO: sem tempo, sem K.O., a vida volta depois de cada combo
        self.arcade = False   # no Arcade o texto do fim muda
        self.ultimo_combo = None  # (golpes, dano) do último combo, pra mostrar no treino
        self.golpes_treino = 0    # golpes que acertaram no boneco desde que a vida voltou
        self.fichas = (ficha1, ficha2)
        self.ctrl = (ctrl1, ctrl2)
        self.vitorias = [0, 0]
        self.round = 1
        self.vencedor = None  # 0, 1 ou "empate" quando a partida acaba
        self.rounds = ROUNDS_PRA_VENCER
        self.vida_inicial = None   # Sobrevivência: começa com a vida que sobrou da luta anterior
        self.sobrevivencia = None  # Sobrevivência: quantos já derrubou antes desta luta
        self.ultima_arcade = False # última luta do Arcade (vale bônus)
        self.combo_max = 0         # maior combo do jogador nesta partida
        self.perfects = 0          # rounds que o jogador venceu sem perder vida
        self.quase = 0             # rounds que venceu com 75% de vida ou mais (sem ser perfect)
        self.premio = None         # moedas ganhas: (itens, nível, multiplicador, total, desafios cumpridos)
        self.stats = dict(parrys=0, quebras=0, ults=0, ults2=0, tomou_ult=False, provocacoes=0, transicoes=0,  # pros desafios
                          choques=0, objetos=0, golpes=0, por_golpe={})  # (v2.0: estatísticas e missões do dia)
        import cenarios
        self.cena = cenarios.cenario(cenario_nome or ficha2.get("cenario", "TEMPLO"))  # luta na casa do adversário
        import objetos
        import clima
        self.objetos = objetos.criar(self.cena.nome)  # CENÁRIO INTERATIVO (v2.0): a coisa do cenário que reage a golpe
        import natal
        self.meia = natal.criar(self)  # NATAL: a meia escondida desse cenário (ou None)
        self.clima = clima.criar(self.cena.nome)      # CLIMA (v2.0): o cenário muda no meio da luta (do round 2)
        self.impactos = Impactos()
        self.t_total = 0
        import estilo
        self.estilos = [estilo.Estilo(), estilo.Estilo()]  # RANKING DE ESTILO (v3.0): um por LADO, a luta inteira
        self.novo_round()

    def novo_round(self):
        if hasattr(self, "objetos"):
            self.objetos.resetar()
            self.clima.resetar()
        self.L = [Lutador(self.fichas[0], 330, 1), Lutador(self.fichas[1], 630, -1)]
        if self.trio:  # TRIO: os 3 de cada lado (só um de cada luta por vez)
            self.equipes = [[Lutador(f, 330 if i == 0 else 630, 1 if i == 0 else -1) for f in self.trio[i]]
                            for i in (0, 1)]
            self.ativo = [0, 0]
            self.troca_espera = [0, 0]
            self.L = [self.equipes[0][0], self.equipes[1][0]]
        for l in self.todos():
            l.regras = self.regras
            if l.f.get("nome_base", l.f["nome"]) in getattr(self, "cicatrizes", ()):
                l.extra["cicatriz"] = True  # CORTE VERTICAL (Katchade): a cicatriz fica até o fim da partida
        if getattr(self, "vida_inicial", None) is not None:
            self.L[0].vida = self.L[0].vida_vista = self.vida_inicial
        self.vida_comeco = self.L[0].vida
        self.transicao_feita = False  # transição de cenário: uma vez por round
        self.projeteis = []
        self.faiscas = []
        self.fase, self.tf = ("luta" if self.treino else "intro"), 0
        if self.round == 1 and not self.treino:  # primeiro round: cada um faz a sua ENTRADA
            self.fase = "entrada"
            for l in self.L:
                l.extra["entrada_x"] = l.x
                l.entrada_t = 0
        self.ultimo_hit = 0
        self.tempo = TEMPO_ROUND * FPS
        self.parada = 0
        self.tremor = 0
        self.combo_txt = None  # (lado, numero, quadros)
        self.msg = ""
        self.escuro = 0        # quadros de tela escura (ultimate)
        self.quem_ultimate = None
        self.clarao = 0        # tela branca (K.O.)
        self.cutscene = None   # cena de anime de algum ultimate (a luta para enquanto passa)
        self.cena_loja = None  # CUTSCENE DA LOJA (entrada/vitória cara do jogador)
        self.camera = [1.0, LARGURA / 2, ALTURA / 2]  # zoom e centro (cutscene)
        self.camera_alvo = None                        # um golpe pede zoom: (zoom, x, y)
        self.cinema = 0.0                              # faixas pretas de cinema (0 a 1)
        self.quebra_txt = None  # (lado, quadros) "GUARDA QUEBRADA!"
        self.parry_txt = None   # (lado, quadros) "PARRY!"
        self.esquiva_txt = None  # (lado, quadros) "ESQUIVA PERFEITA!"
        self.choque = None      # CHOQUE (v2.0): os dois apertando botão rápido
        self.choque_txt = None  # (texto, quem venceu ou None, quadros)

    # ------------------------------------------------------------ efeitos
    def tremer(self, n):
        self.tremor = max(self.tremor, n)

    def poeira(self, x):
        for _ in range(10):
            self.faiscas.append([x, CHAO - 4, random.uniform(-3, 3), random.uniform(-2.5, -0.5), 24, (150, 130, 110)])

    def faisca(self, x, y, defendeu, forte=False):
        cor = (140, 200, 255) if defendeu else AMARELO
        self.impactos.novo(x, y, "def" if defendeu else "forte" if forte else "hit")
        for _ in range(6 if defendeu else 14 if forte else 9):
            a = random.uniform(0, math.tau)
            v = random.uniform(2, 8)
            self.faiscas.append([x, y, math.cos(a) * v, math.sin(a) * v, random.randint(10, 18), cor, 3])

    # ------------------------------------------------------------ um quadro
    def passo(self, bruto):
        self._passo(bruto)
        if not hasattr(self, "narrador"):
            import narrador
            self.narrador = narrador.Narrador()  # NARRADOR: frases grandes nos momentos épicos (só lê a luta)
        self.narrador.passo(self)

    def _passo(self, bruto):
        if getattr(self, "cena_loja", None):  # CUTSCENE DA LOJA (vitória/entrada cara): tudo para enquanto passa
            self.cena_loja.passo()
            if self.cena_loja.acabou:
                self.cena_loja = None
            return
        """bruto = (teclado, mouse) do pygame, ou None nos testes."""
        self.tf += 1
        self.t_total += 1
        if getattr(self, "semente", None) is not None:  # ONLINE: o sorteio é igual nos dois PCs
            random.seed(self.semente * 1000003 + self.t_total)
        # câmera: vai deslizando até o que o golpe pediu (ou volta pro normal)
        alvo = self.camera_alvo or (1.0, LARGURA / 2, ALTURA / 2)
        for i in range(3):
            self.camera[i] += (alvo[i] - self.camera[i]) * 0.14
        self.cinema += ((1.0 if self.camera_alvo else 0.0) - self.cinema) * 0.15
        self.camera_alvo = None
        if self.fase == "ko" and self.tf < 75 and getattr(self, "ko_quem", None) is not None:
            l = self.L[self.ko_quem]  # K.O.: zoom em quem caiu (junto com a câmera lenta)
            self.camera_alvo = (1.35, l.x, l.y - 60 * l.s)
        self.impactos.update()
        if self.clarao > 0:
            self.clarao -= 1
        for l in self.L:
            if l.tremor_hit > 0:
                l.tremor_hit -= 1
        for f in self.faiscas:
            f[0] += f[2]
            f[1] += f[3]
            f[3] += 0.3
            f[4] -= 1
        self.faiscas = [f for f in self.faiscas if f[4] > 0]
        if self.tremor > 0:
            self.tremor -= 1
        if self.combo_txt:
            lado, n, q = self.combo_txt
            self.combo_txt = (lado, n, q - 1) if q > 1 else None
        if self.quebra_txt:
            lado, q = self.quebra_txt
            self.quebra_txt = (lado, q - 1) if q > 1 else None
        if self.choque_txt:
            txt, quem, q = self.choque_txt
            self.choque_txt = (txt, quem, q - 1) if q > 1 else None
        if self.parry_txt:
            lado, q = self.parry_txt
            self.parry_txt = (lado, q - 1) if q > 1 else None
        if self.esquiva_txt:
            lado, q = self.esquiva_txt
            self.esquiva_txt = (lado, q - 1) if q > 1 else None

        if self.fase == "entrada":
            self.passo_entrada()
            return
        if self.fase == "falas":
            self.passo_falas()
            return
        if self.fase == "finish":
            self.passo_finish()
            return
        for l in self.L:  # (segurança) entrada acabou: nada dela fica na tela
            if l.entrada_t is not None:
                l.entrada_t = None
                l.esconde = l.cortar_chao = False
                l.cortar_acima = None
        if self.cutscene:  # passando a cena: a luta fica parada
            self.cutscene.passo()
            if self.cutscene.acabou:
                self.cutscene = None
            return
        if self.fase == "fim":
            return
        if self.fase == "intro" and self.tf == 1:
            som.tocar("round", 0.8)
        if self.fase == "intro" and self.tf == 70:
            som.tocar("lutem", 0.8)
        if self.fase == "intro" and self.tf >= 110:
            self.fase, self.tf = "luta", 0
        if self.escuro > 0:
            self.escuro -= 1
            return
        if self.choque:  # CHOQUE: tudo congelado, os dois apertando botão
            ents = [self.ctrl[i].ler(bruto, self.L[i], self.L[1 - i], self) for i in (0, 1)]
            self.choque.passo(ents)
            if self.choque.acabou:
                self.choque = None
            return
        if self.parada > 0:
            self.parada -= 1
            return
        if self.fase == "ko" and self.tf < 70 and self.tf % 3:
            return  # câmera lenta no K.O.

        ents = [Entrada(), Entrada()]
        if self.fase == "luta":
            ents = [self.ctrl[i].ler(bruto, self.L[i], self.L[1 - i], self) for i in (0, 1)]
            for e in self.estilos:
                e.passo(self.t_total)
        for i in (0, 1):
            lento = self.L[i].extra.get("lento", 0)
            if lento > 0:  # ESQUIVA PERFEITA: em câmera lenta (anda 1 quadro sim, 1 não; o botão apertado espera)
                self.L[i].extra["lento"] = lento - 1
                guardada = self.L[i].extra.pop("ent_guardada", None)
                if lento % 2:
                    e = ents[i]
                    if e.soco or e.chute or e.especial or e.provoca:
                        self.L[i].extra["ent_guardada"] = e
                    continue
                if guardada and not (ents[i].soco or ents[i].chute or ents[i].especial):
                    ents[i] = guardada
            self.L[i].update(ents[i], self.L[1 - i], self)
            if self.L[i].pediu_ultimate:  # momento épico: tudo para e a tela escurece
                self.L[i].pediu_ultimate = False
                ult2_ = bool(self.L[i].golpe and self.L[i].golpe.get("ultimate2"))
                self.escuro, self.quem_ultimate = (ULT2_PAUSA if ult2_ else ULTIMATE_PAUSA), self.L[i]
                self.escuro_max = self.escuro
        if self.trio and self.fase == "luta":
            self.passo_trio(ents)
        self.ex_tiros()
        self.empurrar()
        if self.tentar_choque():
            return
        for i in (0, 1):
            self.checar_golpe(self.L[i], self.L[1 - i])
        self.checar_projeteis()
        if getattr(self, "meia", None) and self.meia.cenario == self.cena.nome:
            self.meia.passo(self)  # NATAL: golpe do jogador pega a meia
        self.passo_objetos()
        self.combo_max = max(self.combo_max, self.L[0].combo)
        self.sentir()

        if self.treino:
            self.passo_treino()
            if getattr(self, "combos", None):
                self.combos.passo(self)
        elif self.fase == "luta":
            self.tempo -= 1
            if any(self.perdeu(i) for i in (0, 1)):
                self.fase, self.tf = "ko", 0
                self.msg = "K.O.!"
                self.ko_quem = next(i for i in (0, 1) if self.perdeu(i))
                self.preparar_finish()
                som.tocar("ko")
                self.tremer(16)
                self.clarao = 8
            elif self.tempo <= 0:
                self.fase, self.tf = "ko", 0
                self.msg = "TEMPO!"
        elif self.fase == "ko":
            for i, (l, o) in enumerate(((self.L[0], self.L[1]), (self.L[1], self.L[0]))):
                if self.vida_lado(i) > self.vida_lado(1 - i) and l.estado == "parado" and self.tf > 90:
                    if getattr(self, "finish_pendente", False):  # a luta acabou com ULTIMATE: FINISH!
                        self.comecar_finish(l, o)
                        return
                    l.mudar("vitoria")
                    self.cena_da_loja(i, "vitoria")
            if self.tf > 240:
                self.terminar_round()

    def cena_da_loja(self, i, tipo):
        """CUTSCENE da loja: só do JOGADOR (gente, fora do online), só uma vez, e a vitória só na que FECHA a luta."""
        import cenas_loja
        l = self.L[i]
        if getattr(self, "lado_humano", None) is not None or getattr(self, "assistindo", False) or self.treino:
            return
        if i not in self.lados_humanos() or (tipo, i) in getattr(self, "cenas_vistas", set()):
            return
        if tipo == "vitoria" and self.vitorias[i] + 1 < self.rounds:
            return
        cena = cenas_loja.criar(l.f, tipo, self.L[1 - i].f, self.cena.nome)
        if cena:
            self.cenas_vistas = getattr(self, "cenas_vistas", set()) | {(tipo, i)}
            self.cena_loja = cena
            if tipo == "entrada":
                l.extra["entrada_cena"] = True  # (na arena ele já aparece pronto, no lugar)

    def passo_entrada(self):
        """As entradas dos personagens (Max chega voando, Rib faz Kawarimi, Trafo sai da terra...)."""
        if not getattr(self, "_cena_entrada_vista", False):  # (no 1º quadro da entrada: a CUTSCENE da loja, se tiver)
            self._cena_entrada_vista = True
            for i in (0, 1):
                self.cena_da_loja(i, "entrada")
            if self.cena_loja:
                return
        if self.tf >= DURACAO_ENTRADA:
            for l in self.L:
                l.entrada_t = None
                l.esconde = l.cortar_chao = False
                l.cortar_acima = None
                l.sobrepor = {}
                l.angulo, l.vira = 0, False
                l.x, l.y = l.extra.get("entrada_x", l.x), CHAO
                l.mudar("parado")
            self.fase, self.tf = "intro", 0
            self.comecar_falas()
            return
        for l in self.L:
            l.entrada_t = self.tf
            entrada = l.f.get("entrada")
            if l.extra.get("entrada_cena"):  # (já viu a cutscene: fica parado no lugar)
                l.x, l.y = l.extra.get("entrada_x", l.x), CHAO
                l.esconde, l.sobrepor = False, {}
                l.t += 1
            elif entrada:
                entrada(l, self.tf, self)
            else:
                l.t += 1
            l.animar()

    # ---- FINISH (v2.0): a luta acabou com ULTIMATE -> cena de finalização do vencedor ----
    def preparar_finish(self):
        import finish
        self.finish_pendente = False
        if self.treino or self.trio:
            return
        perdedor = self.L[self.ko_quem]
        venc = 1 - self.ko_quem
        ultima = self.vitorias[venc] + 1 >= self.rounds  # (só no K.O. que acaba a luta)
        self.finish_pendente = ultima and getattr(perdedor, "ult_recente", 0) > 0 and finish.de(self.L[venc]) is not None

    def comecar_finish(self, v, d):
        import finish
        self.finish_pendente = False
        self.finish = (v, d, finish.de(v))
        self.finish_ini = self.t_total
        self.fase, self.tf = "finish", 0
        v.mudar("parado")
        v.sobrepor = {}
        d.mudar("caido")  # (o derrotado fica deitado no chão durante a cena)
        d.sobrepor, d.vx, d.vy, d.y, d.angulo = {}, 0, 0, CHAO, 0
        d.pose_vista = None
        som.tocar("ultimate")
        self.tremer(10)

    def passo_finish(self):
        import finish
        v, d, fn = self.finish
        fn["passo"](v, d, self.tf, self)
        v.x = max(PAREDE_E, min(PAREDE_D, v.x))  # (sentar/pular em cima de quem caiu na parede: não sai da tela)
        for l in (v, d):
            l.t += 1
            l.animar()
        self.camera_alvo = (1.25, (v.x + d.x) / 2, CHAO - 90)
        if self.tf >= finish.DURACAO:  # acabou: agora sim a pose de vitória
            v.sobrepor = {}
            v.y = CHAO
            v.mudar("vitoria")
            self.fase, self.tf = "ko", 200
            self.cena_da_loja(self.L.index(v), "vitoria")

    def desenhar_finish(self, tela):
        import finish
        if not getattr(self, "finish", None):
            return
        v, d, fn = self.finish
        t = self.t_total - self.finish_ini
        fn["desenhar"](v, d, tela, t)
        if self.fase == "finish":
            if t < finish.TEXTO + 50:
                esc = 1 + max(0, (14 - t) / 14) * 1.2
                texto_grande(tela, "FINISH!", 64, (255, 70, 60), (LARGURA // 2, 130), esc, contorno=(40, 0, 0))
            if 30 < t < finish.DURACAO:
                texto_grande(tela, fn["nome"], 30, (255, 230, 120), (LARGURA // 2, 186), contorno=(40, 20, 0))

    # ---- FALAS NA ENTRADA (v2.0): cada um chega, fica na pose de espera, fala e vai pra pose de luta ----
    FALA_INICIO, FALA_INTERVALO, FALA_DEPOIS = 12, 10, 24

    def comecar_falas(self):
        """Sorteia a conversa e põe os dois na pose de espera. (O sorteio usa o random da luta: no ONLINE
        os dois PCs sorteiam a mesma conversa, e o tempo de cada fala sai igual.)"""
        import falas
        if getattr(self, "sem_falas", False):
            return
        self.falas_luta = falas.dialogo(self.L[0].f, self.L[1].f)
        if not self.falas_luta:
            return
        for l in self.L:
            l.pose_espera = l.f.get("espera", "vitoria")
        self.fase, self.tf = "falas", 0

    def tempos_falas(self):
        """[(lado, texto, começa, termina)] de cada fala, em quadros."""
        t = self.FALA_INICIO
        tempos = []
        for lado, txt in self.falas_luta:
            dur = min(170, 46 + len(txt) * 2)
            tempos.append((lado, txt, t, t + dur))
            t += dur + self.FALA_INTERVALO
        return tempos

    def passo_falas(self):
        tempos = self.tempos_falas()
        for lado, _, _, fim in tempos:
            if self.tf == fim:  # falou: agora fica na pose de luta
                self.L[lado].pose_espera = None
        for l in self.L:
            l.t += 1
            l.animar()
        if self.tf >= tempos[-1][3] + self.FALA_DEPOIS:
            self.terminar_falas()

    def terminar_falas(self):
        for l in self.L:
            l.pose_espera = None
            l.t = 0
        self.fase, self.tf = "intro", 0

    def pular_entrada(self):
        """ENTER: pula a entrada e as falas (vai direto pro ROUND 1). A CUTSCENE DA LOJA não pula (o Gomes pediu)."""
        if getattr(self, "cena_loja", None):
            return
        if self.fase == "entrada":
            self.tf = DURACAO_ENTRADA
            self.sem_falas = True
            self.passo_entrada()
        elif self.fase == "falas":
            self.terminar_falas()

    def desenhar_falas(self, tela):
        from selecao import balao
        for lado, txt, comeca, termina in self.tempos_falas():
            if comeca <= self.tf < termina + 4:
                l = self.L[lado]
                topo = l.y - (l.f.get("altura", 1.0) * 120 + 18) * l.s
                balao(tela, txt, lado, (self.tf - comeca) * 2, alvo=(l.x, topo))

    def passo_treino(self):
        """Treino: ninguém morre; quando o combo acaba, a vida volta e guarda o resultado."""
        for l in self.L:
            if l.vida <= 0:
                l.vida = 1
            if l.dano_combo_vista != l.vida_max - l.vida and l.vida < l.vida_max:
                l.dano_combo_vista = l.vida_max - l.vida
        alvo, atacante = self.L[1], self.L[0]
        livre = alvo.estado in ("parado", "andando", "agachado", "defendendo")
        if livre and alvo.vida < alvo.vida_max and self.tf - self.ultimo_hit > 50:
            self.ultimo_combo = (max(1, self.golpes_treino), alvo.vida_max - alvo.vida)
            self.golpes_treino = 0
            for l in self.L:
                l.vida = l.vida_vista = l.vida_max
                l.dano_combo_vista = 0
        if self.L[0].vida < self.L[0].vida_max and self.L[0].estado in ("parado", "andando", "agachado") \
                and self.tf - self.ultimo_hit > 50:
            self.L[0].vida = self.L[0].vida_max

    def terminar_round(self):
        a, b = self.vida_lado(0), self.vida_lado(1)
        eu = self.L[0]
        self.stats["ults"] += eu.acertou_ult
        self.stats["ults2"] += eu.acertou_ult2
        self.stats["tomou_ult"] |= eu.tomou_ult
        self.stats["provocacoes"] += eu.provocou
        if a > b and a >= self.vida_comeco:
            self.perfects += 1  # PERFECT: venceu o round sem perder nada de vida
        elif a > b and a >= self.L[0].vida_max * QUASE_VIDA:
            self.quase += 1     # QUASE PERFECT
        if a >= b:
            self.vitorias[0] += 1
        if b >= a:
            self.vitorias[1] += 1  # empate no tempo: os dois ganham o round
        v1, v2 = (v >= self.rounds for v in self.vitorias)
        if v1 or v2:
            self.vencedor = "empate" if v1 and v2 else (0 if v1 else 1)
            self.fase, self.tf = "fim", 0
            self.pagar()
            self.dar_maestria()
            import estatisticas
            import missoes
            import perfil
            estatisticas.registrar(self)
            import rivais
            rivais.registrar(self)
            self.missoes_feitas = missoes.avancar(self)     # MISSÕES DO DIA cumpridas nessa luta
            self.trofeus_ganhos = perfil.trofeus_novos()    # TROFÉUS que saíram agora
            import eventos
            self.doces_ganhos = eventos.ganhar_doces(self)  # HALLOWEEN: +3 ganhando, +1 perdendo
            import figurinhas
            self.figurinha_ganha = figurinhas.sortear_da_luta(self)  # ÁLBUM: às vezes sai uma figurinha
        else:
            self.round += 1
            self.novo_round()

    def controles(self):
        """O controle de videogame de cada lado (ou None), pra vibrar."""
        if hasattr(self, "controles_vibra"):
            return self.controles_vibra
        return [getattr(c, "controle", None) for c in self.ctrl]

    def sentir(self):
        """VIBRAÇÃO: quem perdeu vida sente o controle tremer (mais forte quanto maior o dano)."""
        import controle_video
        import save
        cs = self.controles() if save.d().get("vibrar", True) else [None, None]  # (CONFIGURAÇÕES: vibração)
        antes = getattr(self, "_vidas", None)
        self._vidas = [l.vida for l in self.L]
        if not antes or not any(cs):
            return
        for i, l in enumerate(self.L):
            perdeu = antes[i] - l.vida
            if perdeu > 0.01:
                forca, ms = ((0.25, 70) if perdeu < 3 else (0.5, 130) if perdeu < 10 else (0.8, 220) if perdeu < 25
                             else (1.0, 450))
                controle_video.vibrar(cs[i], forca, ms)
                if perdeu >= 8:  # quem bateu sente um pouquinho também
                    controle_video.vibrar(cs[1 - i], 0.35, 90)
        for i, l in enumerate(self.L):
            if getattr(l, "_vibrou_ult", False) != (l.estado == "ataque" and bool(l.golpe and l.golpe.get("ultimate"))):
                l._vibrou_ult = not getattr(l, "_vibrou_ult", False)
                if l._vibrou_ult:
                    controle_video.vibrar(cs[i], 0.6, 300)  # soltou a ultimate
        if self.fase == "ko" and not getattr(self, "_vibrou_ko", False):
            self._vibrou_ko = True
            for c in cs:
                controle_video.vibrar(c, 1.0, 600)  # K.O.!

    def ex_tiros(self):
        """EX do E: cada tiro novo vira 3 (em fila) e maiores."""
        import copy
        novos = []
        for p in self.projeteis:
            if getattr(p, "ex_visto", False):
                continue
            p.ex_visto = True
            d = p.dono
            if not (getattr(p, "ex", False) and getattr(d, "ex_botao", None) == "E"):
                continue
            d.ex_dano = False  # (é tiro: não precisa do 1,5x)
            p.raio = int(p.raio * 1.5)
            sinal = 1 if getattr(p, "vx", 0) >= 0 else -1
            for k in (1, 2):
                c = copy.copy(p)
                c.x -= sinal * 46 * k
                c.ex_visto = True
                novos.append(c)
        self.projeteis.extend(novos)

    # ------------------------------------------------------------ TRIO
    def todos(self):
        return [m for eq in self.equipes for m in eq] if self.trio else list(self.L)

    def perdeu(self, i):
        if self.trio:
            return all(m.vida <= 0 for m in self.equipes[i])
        return self.L[i].vida <= 0

    def vida_lado(self, i):
        return sum(max(0, m.vida) for m in self.equipes[i]) if self.trio else self.L[i].vida

    def passo_trio(self, ents):
        for i in (0, 1):
            if self.troca_espera[i] > 0:
                self.troca_espera[i] -= 1
            l = self.L[i]
            vivos = [m for m in self.equipes[i] if m is not l and m.vida > 0]
            for m in self.equipes[i]:  # quem está esperando fora recupera um pouquinho
                if m is not l and 0 < m.vida < m.vida_max:
                    m.vida = m.vida_vista = min(m.vida_max, m.vida + 0.025)
            if not vivos:
                continue
            if l.vida <= 0 and l.estado == "caido" and l.t > 30:
                self.trocar(i, forcado=True)  # caiu: entra o próximo
                continue
            from controles import Computador
            cpu_quer = isinstance(self.ctrl[i], Computador) and l.vida < 25 and random.random() < 0.01 and \
                any(m.vida > l.vida + 20 for m in vivos)
            if (getattr(ents[i], "troca", False) or cpu_quer) and self.troca_espera[i] == 0 and l.no_chao() \
                    and l.estado in ("parado", "andando", "agachado"):
                self.trocar(i)

    def trocar(self, i, forcado=False):
        """TRIO: sai o de agora, entra o próximo pulando com uma voadora."""
        eq, velho = self.equipes[i], self.L[i]
        n = len(eq)
        for k in range(1, n):
            j = (self.ativo[i] + k) % n
            if eq[j].vida > 0:
                break
        else:
            return
        novo = eq[j]
        for _ in range(8):  # puf onde o velho estava
            a = random.uniform(0, math.tau)
            self.faiscas.append([velho.x, velho.y - 60, math.cos(a) * 4, math.sin(a) * 4, 18, (220, 220, 235), 6])
        som.tocar("puf")
        novo.x = max(PAREDE_E, min(PAREDE_D, velho.x - velho.dir * 40))
        novo.y, novo.vx, novo.vy = CHAO - 240, velho.dir * 3, 0
        novo.dir = velho.dir
        novo.barra = velho.barra  # a barra é do time
        novo.mudar("pulando")
        novo.ja_atacou = False
        novo.inv = 30
        novo.regras = self.regras
        if not forcado:
            novo.comecar("ar_chute")  # entra dando uma voadora (o "ataque do parceiro")
        velho.sobrepor = {}
        velho.rastro = []
        self.ativo[i] = j
        self.L[i] = novo
        self.troca_espera[i] = 180

    def desenhar_trio(self, tela):
        """Os 3 retratinhos de cada time, embaixo da vida."""
        from selecao import retrato
        if not hasattr(self, "_retratos"):
            self._retratos = {}
        for i in (0, 1):
            for k, m in enumerate(self.equipes[i]):
                chave = (m.f["nome"], m.f.get("roupa"))
                if chave not in self._retratos:
                    self._retratos[chave] = retrato(m.f, 30)
                x = 34 + k * 38 if i == 0 else LARGURA - 34 - 30 - k * 38
                y = 96
                r = pygame.Rect(x, y, 30, 30)
                tela.blit(self._retratos[chave], r.topleft)
                ativo = m is self.L[i]
                pygame.draw.rect(tela, (255, 220, 70) if ativo else (20, 14, 24), r, 2)
                if m.vida <= 0:
                    escuro = pygame.Surface((30, 30), pygame.SRCALPHA)
                    escuro.fill((0, 0, 0, 160))
                    tela.blit(escuro, r.topleft)
                    pygame.draw.line(tela, (230, 60, 50), r.topleft, r.bottomright, 3)
                    pygame.draw.line(tela, (230, 60, 50), r.topright, r.bottomleft, 3)
                else:
                    pygame.draw.rect(tela, (40, 20, 24), (x, y + 32, 30, 4))
                    pygame.draw.rect(tela, (255, 220, 90), (x, y + 32, int(30 * m.vida / m.vida_max), 4))
            if self.troca_espera[i] == 0 and any(m.vida > 0 and m is not self.L[i] for m in self.equipes[i]):
                import controle_video
                txt = f"{controle_video.nome('troca')} troca"
                texto(tela, txt, 12, (150, 220, 255), (34 + 60 if i == 0 else LARGURA - 34 - 60, 142))

    def destruicao(self):
        """CENÁRIO QUE QUEBRA (v3.0): as marcas deste cenário (continuam de um round pro outro; trocou de cenário =
        começa inteiro de novo). Quem bate na parede ou cai forte no chão racha ali (só desenho)."""
        import destruicao
        if getattr(self, "_destr_de", None) != self.cena.nome:
            self._destr, self._destr_de = destruicao.Destruicao(self.cena.nome), self.cena.nome
        return self._destr

    def estilo_hit(self, atacante, alvo, nome):
        """RANKING DE ESTILO: quem bateu sobe (variando os golpes), quem apanhou desce. (Roda nos 2 PCs: sem sorteio.)"""
        if self.fase != "luta" or self.treino:
            return
        if atacante in self.L and nome:
            self.estilos[self.L.index(atacante)].acertou(nome, self.t_total)
        if alvo in self.L:
            self.estilos[self.L.index(alvo)].apanhou()

    def registrar_hit(self, atacante, nome, ativacao):
        """O jogador (lado 0) acertou alguém com esse golpe (desafios de combo, estatísticas e missões)."""
        if atacante is self.L[0] and nome:
            self.stats["golpes"] += 1
            self.stats["por_golpe"][nome] = self.stats["por_golpe"].get(nome, 0) + 1
        if getattr(self, "combos", None) and atacante is self.L[0]:
            self.combos.acertou(nome, ativacao, atacante.combo)

    def transicao_parede(self, l, lado):
        """Alguém bateu voando na parede. Se foi forte, atravessa pro cenário vizinho!"""
        import transicao
        if self.fase != "luta" or self.cutscene or self.transicao_feita or l.vida <= 0 or l.malabar:
            return False
        if self.cena.nome not in transicao.DESTINOS or getattr(l, "parede_sobe", False):
            return False
        if not (abs(l.vx) >= transicao.VEL_MINIMA or l.voo_forte):
            return False
        atacante = self.L[1] if l is self.L[0] else self.L[0]
        if getattr(l, "ult_recente", 0) or (atacante.estado == "ataque" and atacante.golpe
                                              and atacante.golpe.get("ultimate")):
            return False  # ultimate já é forte o bastante: não vira transição
        self.transicao_feita = not self.treino  # no treino dá pra fazer de novo
        if atacante is self.L[0]:
            self.stats["transicoes"] += 1
        self.cutscene = transicao.Transicao(self, l, atacante, lado)
        return True

    def resumo(self):
        """O que aconteceu na partida (pros desafios)."""
        venceu = self.vencedor == 0
        n = self.sobrevivencia
        f0 = self.L[0].f if self.trio else self.fichas[0]
        return dict(self.stats, venceu=venceu, personagem=f0.get("nome_base", f0["nome"]),
                    nivel=getattr(self.ctrl[1], "nivel", None), combo=self.combo_max,
                    bom=venceu and (self.perfects + self.quase) > 0, sobrev=(n + venceu) if n is not None else 0,
                    perfects=self.perfects, pulos=getattr(self.L[0], "pulos", 0) if not self.trio else
                    sum(getattr(m, "pulos", 0) for m in self.equipes[0]),
                    rounds=self.round, vida=self.vida_lado(0), adversario=self.L[1].f.get("nome_base", self.L[1].f["nome"]),
                    cenario=self.cena.nome, regras=sorted(self.regras),
                    modo=("trio" if self.trio else "torneio" if getattr(self, "torneio", False) else
                          "sobrevivencia" if self.sobrevivencia is not None else
                          "online" if getattr(self, "online", False) else "luta"))

    def enfeites_evento(self):
        """Os enfeites do evento de hoje (pela data do PC), ou None. Só desenho."""
        if not hasattr(self, "_enfeites"):
            import eventos
            self._enfeites = eventos.criar()
        return self._enfeites

    def periodo_atual(self):
        """DIA / PÔR DO SOL / NOITE do cenário (sorteado uma vez por cenário; no online, igual nos dois PCs)."""
        import periodo
        if getattr(self, "_periodo_de", None) != self.cena.nome:
            self._periodo_de = self.cena.nome
            base = getattr(self, "semente", None)
            if base is None:
                base = getattr(self, "_periodo_sorte", None) or random.Random().randrange(1, 10 ** 6)
                self._periodo_sorte = base
            rng = random.Random(base * 31 + sum(ord(c) for c in self.cena.nome))  # (nunca mexe no random da luta)
            self.periodo = periodo.criar(self.cena.nome, rng)
        return self.periodo

    def lados_humanos(self):
        """Quem é gente de verdade nessa luta (o ONLINE diz qual lado é o deste PC)."""
        from controles import Jogador
        if getattr(self, "lado_humano", None) is not None:
            return [self.lado_humano]
        return [i for i in (0, 1) if isinstance(self.ctrl[i], Jogador)]

    def dar_maestria(self):
        """MAESTRIA (v2.0): quem jogou ganha pontos com o lutador que usou (no TRIO, os 3)."""
        import maestria
        self.maestria_info = []
        if self.treino or getattr(self, "assistindo", False):
            return
        for i in self.lados_humanos():
            pts = maestria.pontos_da_luta(self, i)
            if pts <= 0:
                continue
            fichas = [m.f for m in self.equipes[i]] if self.trio else [self.L[i].f]
            for f in fichas:
                antes, depois = maestria.ganhar(f, pts)
                premio = maestria.premio_do_nivel(depois) if depois > antes else ""
                self.maestria_info.append((i, f, pts, depois, premio))

    def desenhar_conquistas(self, tela):
        """No fim da luta: MISSÃO CUMPRIDA e TROFÉU NOVO (em cima, embaixo das barras de vida)."""
        linhas = [(f"MISSÃO CUMPRIDA! {txt}", f"+{m} moedas  +{xp} maestria", (150, 230, 255))
                  for txt, m, xp in getattr(self, "missoes_feitas", None) or []]
        linhas += [(f"TROFÉU: {nome}!", "", (255, 220, 90)) for nome in getattr(self, "trofeus_ganhos", None) or []]
        if not linhas:
            return
        k = min(1.0, self.tf / 20)
        r = pygame.Rect(LARGURA // 2 - 300, 96 - int((1 - k) * 60), 600, 12 + 26 * len(linhas))
        caixa = pygame.Surface(r.size, pygame.SRCALPHA)
        caixa.fill((14, 10, 26, 220))
        tela.blit(caixa, r.topleft)
        pygame.draw.rect(tela, (255, 210, 90), r, 2, border_radius=8)
        for i, (txt, extra, cor) in enumerate(linhas):
            y = r.y + 19 + i * 26
            texto(tela, txt, 15, cor, (r.centerx - (60 if extra else 0), y))
            if extra:
                texto(tela, extra, 13, (255, 220, 90), (r.right - 90, y))

    def desenhar_maestria(self, tela):
        """No fim da luta: a barrinha de maestria de cada lutador (e o prêmio, se subiu de nível)."""
        import maestria
        if self.premio:  # logo embaixo da caixa das moedas
            itens, _, _, _, cumpridos = self.premio
            y = 302 + 20 + (max(1, len(itens)) + len(cumpridos) + 2) * 21 + 30
        else:
            y = 330
        y = min(y, ALTURA - 24 - 34 * (len(self.maestria_info) - 1))  # (TRIO: 3 barrinhas, tem que caber)
        for lado, f, pts, nivel, premio in self.maestria_info:
            n, xp, prox = maestria.progresso(f)
            nome = f.get("nome_base", f["nome"])
            x = LARGURA // 2
            k = min(1.0, self.tf / 50)
            if premio and (self.tf // 10) % 2:
                texto(tela, f"{nome} SUBIU PRO NÍVEL {n}!  ganhou: {premio}", 16, (255, 230, 90), (x, y - 14))
            else:
                texto(tela, f"MAESTRIA {nome}: NÍVEL {n}   +{round(pts * k)}", 14, (220, 220, 235), (x, y - 14))
            r = pygame.Rect(x - 150, y, 300, 10)
            pygame.draw.rect(tela, (14, 10, 26), r.inflate(4, 4), border_radius=4)
            cheio = 1.0 if not prox else xp / prox
            cor = maestria.moldura(f) or (120, 200, 255)
            pygame.draw.rect(tela, cor, (r.x, r.y, int(r.w * cheio), r.h), border_radius=4)
            y += 34

    def pagar(self):
        """Moedas! Só quando é você contra o computador (no treino e no CPU x CPU não vale)."""
        from controles import Computador, Jogador
        if self.treino or not isinstance(self.ctrl[0], Jogador) or not isinstance(self.ctrl[1], Computador):
            return
        if self.regras:
            return  # com MODO MALUCO ligado não ganha moeda
        venceu = self.vencedor == 0
        itens = []
        if venceu:
            itens.append(("VITÓRIA", MOEDAS_VITORIA))
        if self.perfects:
            itens.append(("PERFECT" + (f" x{self.perfects}" if self.perfects > 1 else ""), MOEDAS_PERFECT * self.perfects))
        if self.quase:
            itens.append(("QUASE PERFECT" + (f" x{self.quase}" if self.quase > 1 else ""), MOEDAS_QUASE * self.quase))
        sobrou = int(self.L[0].vida // MOEDAS_VIDA)
        if sobrou > 0:
            itens.append((f"VIDA QUE SOBROU ({int(self.L[0].vida)})", sobrou))
        if self.combo_max >= hab.limite_combo(self.L[0], COMBO_MAXIMO):
            itens.append(("COMBO MÁXIMO", MOEDAS_COMBO))
        if self.ultima_arcade and venceu:
            itens.append(("ARCADE COMPLETO", MOEDAS_ARCADE))
        bonus, rotulo = self.estilos[0].moedas_bonus()  # RANKING DE ESTILO: a maior letra que ele alcançou
        if bonus > 0:
            itens.append((rotulo, bonus))
        if self.sobrevivencia is not None and not venceu and save.novo_recorde(self.sobrevivencia):
            itens.append(("RECORDE NOVO", MOEDAS_RECORDE))
        nivel = self.ctrl[1].nivel
        mult = MOEDAS_MULT.get(nivel, 1)
        import rivais
        if venceu and rivais.sao_rivais(self.fichas[0], self.fichas[1]):  # RIVAL DERROTADO: moedas em dobro
            mult *= rivais.MULT_MOEDAS
            nivel = f"{nivel} + RIVAL DERROTADO"
        total = round(sum(v for _, v in itens) * mult)
        import desafios
        cumpridos = desafios.atualizar(self.resumo())  # desafios valem sem multiplicador
        self.premio = (itens, nivel, mult, total, cumpridos)
        save.ganhar(total + sum(v for _, v in cumpridos))

    def empurrar(self):
        a, b = self.L
        if "agarrado" in (a.estado, b.estado) or a.y < 0 or b.y < 0:
            return
        if "rolando" in (a.estado, b.estado):
            return  # ROLAMENTO: passa pelo outro
        if any(l.extra.get("nadando") or (l.estado == "ataque" and l.memo.get("so_barbatana")) for l in (a, b)):
            return  # SPHYRUS embaixo da terra (nadando/mergulho): passa por baixo do outro
        if abs(a.y - b.y) > 90:
            return  # um tá pulando por cima do outro
        minimo = CORPO * a.s + CORPO * b.s
        dx = b.x - a.x
        if abs(dx) >= minimo:
            return
        lado = 1 if dx > 0 else (-1 if dx < 0 else a.dir)
        sobra = minimo - abs(dx)
        a.x -= lado * sobra / 2
        b.x += lado * sobra / 2
        for l, o, s in ((a, b, -lado), (b, a, lado)):
            if l.x < PAREDE_E or l.x > PAREDE_D:  # na parede: empurra o outro
                l.x = max(PAREDE_E, min(PAREDE_D, l.x))
                o.x = l.x - s * minimo

    def passo_objetos(self):
        import clima
        import objetos
        if getattr(self, "combos", None):
            return  # (nos desafios de combo o objeto atrapalhava)
        if not self.treino or objetos.LIGADO_NO_TREINO:
            self.objetos.passo(self)
        if not self.treino or clima.LIGADO_NO_TREINO:
            self.clima.passo(self)

    def tentar_choque(self):
        """Os dois acertaram golpe forte no mesmo quadro? CHOQUE!"""
        import choque
        if self.fase != "luta" or self.choque or self.treino:
            return False
        a, b = self.L
        ca, cb = a.corpo(), b.corpo()
        if not (ca and cb and choque.forte(a) and choque.forte(b)):
            return False
        pa, pb = a.contato(cb), b.contato(ca)
        if not (pa and pb):
            return False
        self.choque = choque.Choque(self, ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2))
        return True

    def corpo_esquivando(self, b):
        """Rolando bem no comecinho (invencível): onde o golpe IA pegar (pra ESQUIVA PERFEITA), ou None."""
        if b.estado != "rolando" or b.t > ESQ_JANELA or b.extra.get("esq_perfeita"):
            return None
        inv, b.inv = b.inv, 0
        c = b.corpo()
        b.inv = inv
        return c

    def esquiva_perfeita(self, b, a):
        """ESQUIVA PERFEITA (v3.0): rolou no último instante. O tempo fica lento SÓ pro oponente (~1 s)."""
        b.extra["esq_perfeita"] = True
        a.extra["lento"] = ESQ_LENTO
        a.extra.pop("ent_guardada", None)
        self.esquiva_txt = (self.L.index(b) if b in self.L else 0, 70)
        som.tocar("parry", 0.6)
        som.tocar("vento", 0.7)
        if b is self.L[0]:
            self.stats["esquivas"] = self.stats.get("esquivas", 0) + 1

    def checar_golpe(self, a, b):
        cb = b.corpo()
        if not cb and a.estado == "ataque" and not a.acertou:
            quase = self.corpo_esquivando(b)
            if quase and a.contato(quase):
                self.esquiva_perfeita(b, a)
        ponto = a.contato(cb) if cb else None
        if not ponto:
            return
        a.acertou = True
        self.ultimo_hit = self.tf
        g = a.memo.get("g_hit", a.golpe)
        if getattr(a, "ex", False) and getattr(a, "ex_dano", False):  # EX de E que não é tiro: bate 1,5x
            g = dict(g, dano=g["dano"] * EX_DANO)
        sinal = 1 if b.x > a.x else -1
        res = b.receber(g, sinal, a, a.f["forca"])
        if res == "esquiva":  # (substituição: não aconteceu nada)
            return
        if res == "hit":
            self.estilo_hit(a, b, a.nome_golpe)
        if res == "hit" and b is self.L[1]:
            self.golpes_treino += 1
            self.registrar_hit(a, a.nome_golpe, getattr(a, "golpe_id", 0))
        if res == "quebrou":
            self.guarda_quebrada(b, ponto)
            return
        if res == "parry":
            self.parry(b, ponto)
            return
        self.som_do_golpe(res, g)
        self.faisca(ponto[0], ponto[1], res == "def", g["dano"] >= 10)
        self.parada = PARADA_GOLPE if res == "hit" else 4
        if g["dano"] <= 3:
            self.parada = 3  # soquinho rápido: congela pouco
        if res == "hit":
            self.tremer(5 if g["dano"] < 8 else 9 if g["dano"] < 20 else 16)
            if a.combo >= 2:
                self.combo_txt = (self.L.index(a), a.combo, 70)

    def som_do_golpe(self, res, g):
        if res == "def":
            som.tocar("defesa", 0.7)
        elif g["dano"] >= 15:
            som.tocar("explosao", 0.8)
            som.tocar("chute")
        elif g["dano"] >= 7:
            som.tocar("chute")
        else:
            som.tocar("soco")

    def parry(self, l, ponto):
        som.tocar("parry")
        if l is self.L[0]:
            self.stats["parrys"] += 1
        """Parry: tudo congela um tiquinho, brilho azul-branco, e quem deu parry fica livre primeiro."""
        self.parada = PARRY_PARADA
        self.impactos.novo(ponto[0], ponto[1], "def")
        for _ in range(16):
            a = random.uniform(0, math.tau)
            v = random.uniform(4, 9)
            self.faiscas.append([ponto[0], ponto[1], math.cos(a) * v, math.sin(a) * v, random.randint(10, 18),
                                 random.choice(((255, 255, 255), (150, 220, 255))), 3])
        self.parry_txt = (self.L.index(l), 60)

    def guarda_quebrada(self, l, ponto):
        """Vidro azul estourando + texto."""
        som.tocar("quebra")
        if l is self.L[1]:
            self.stats["quebras"] += 1
        self.parada = 14
        self.tremer(12)
        self.impactos.novo(ponto[0], ponto[1], "forte")
        for _ in range(26):
            a = random.uniform(0, math.tau)
            v = random.uniform(3, 10)
            self.faiscas.append([ponto[0], ponto[1], math.cos(a) * v, math.sin(a) * v - 2,
                                 random.randint(18, 30), random.choice(((140, 210, 255), (220, 240, 255))), 4])
        self.quebra_txt = (self.L.index(l), 80)

    def checar_projeteis(self):
        for p in self.projeteis:
            p.update()
        ps = self.projeteis
        for i, p in enumerate(ps):  # bola contra bola: as duas somem
            for q in ps[i + 1:]:
                bum = p.golpe.get("bumerangue") or q.golpe.get("bumerangue")  # o nunchaku não some no choque
                if p.vivo and q.vivo and p.dono is not q.dono and not bum and p.rect().colliderect(q.rect()):
                    fica_p, fica_q = p.golpe.get("atravessa"), q.golpe.get("atravessa")  # o Mini Sol passa por cima
                    if (self.fase == "luta" and not self.treino and not self.choque and not (fica_p or fica_q)
                            and p.golpe.get("especial") and q.golpe.get("especial")):
                        import choque  # CHOQUE DE TIROS: cabo de guerra de poder no meio da tela!
                        do0 = p if p.dono is self.L[0] else q
                        self.choque = choque.Choque(self, ((p.x + q.x) / 2, (p.y + q.y) / 2),
                                                    tiros=(do0, q if do0 is p else p))
                        return
                    p.vivo = bool(fica_p) and not fica_q
                    q.vivo = bool(fica_q) and not fica_p
                    self.faisca((p.x + q.x) / 2, p.y, False)
        for p in ps:
            if not p.vivo:
                continue
            alvo = self.L[1] if p.dono is self.L[0] else self.L[0]
            c = alvo.corpo()
            if not c:
                quase = self.corpo_esquivando(alvo)
                if quase and p.rect().colliderect(quase) and getattr(p, "pode_acertar", True):
                    self.esquiva_perfeita(alvo, p.dono)
            if c and p.rect().colliderect(c) and getattr(p, "pode_acertar", True):
                if p.golpe.get("bumerangue"):
                    p.pode_acertar = False  # bate e continua (acerta de novo na volta)
                else:
                    p.vivo = False
                self.ultimo_hit = self.tf
                res = alvo.receber(p.golpe, 1 if p.vx > 0 else -1, p.dono, p.dono.f["forca"])
                if res == "esquiva":  # (substituição: o projétil pegou no tronco e some)
                    p.vivo = False
                    continue
                if res == "hit":
                    self.estilo_hit(p.dono, alvo, getattr(p, "nome_golpe", None) or "tiro")
                if res == "hit" and alvo is self.L[1]:
                    self.golpes_treino += 1
                    self.registrar_hit(p.dono, getattr(p, "nome_golpe", None), ("proj", getattr(p, "ativacao", 0)))
                if p.golpe.get("ao_acertar"):
                    p.golpe["ao_acertar"](p.dono, alvo, self, res)
                if res == "quebrou":
                    self.guarda_quebrada(alvo, (p.x, p.y))
                    continue
                if res == "parry":
                    self.parry(alvo, (p.x, p.y))
                    continue
                self.som_do_golpe(res, p.golpe)
                self.faisca(p.x, p.y, res == "def", p.golpe["dano"] >= 10)
                if not p.golpe.get("sem_parada"):  # (rajada de minigun/mísseis: não congela a cada tiro)
                    self.parada = PARADA_GOLPE if res == "hit" else 4
                if res == "hit":
                    self.tremer(16 if p.golpe is GOLPES["ultimate"] else 3 if p.golpe.get("sem_parada") else 8)
        self.projeteis = [p for p in ps if p.vivo]

    # ------------------------------------------------------------ desenho
    def desenhar(self, tela):
        if getattr(self, "cena_loja", None):
            self.cena_loja.desenhar(tela)
            return
        if self.cutscene:
            self.cutscene.desenhar(tela)
            return
        if self.desenhar_replay(tela):
            return
        self.desenhar_luta(tela)
        self.gravar_replay(tela)
        self.desenhar_finish(tela)
        self.desenhar_brilho_mestre(tela)
        if self.choque:
            self.choque.desenhar(tela)
        q = self.quem_ultimate
        if self.escuro and q is not None and q.golpe and q.golpe.get("ultimate2"):  # 2ª ULTIMATE: a apresentação
            ult2.desenhar_cartao(tela, q, self, 1 - self.escuro / getattr(self, "escuro_max", ULT2_PAUSA))
        if self.treino and getattr(self, "ver_caixas", False):
            self.desenhar_caixas(tela)
        if getattr(self, "assistindo", False) and self.fase not in ("fim",):
            texto(tela, "TORNEIO: assistindo   (ENTER pula pro resultado)", 14, (220, 220, 235), (LARGURA // 2, ALTURA - 12))

    # ---- REPLAY (v2.0): os últimos 2 segundos antes do K.O. final, em câmera lenta ----
    REPLAY_QUADROS = 66   # guardados (um a cada 2 desenhos: ~2 segundos)
    REPLAY_LENTO = 3      # cada quadro do replay fica 3 desenhos na tela

    def gravar_replay(self, tela):
        """Só desenho: guarda uma foto pequena da tela (não mexe em nada da luta)."""
        if self.treino or getattr(self, "assistindo", False):
            return
        if not (self.fase == "luta" or (self.fase == "ko" and self.tf < 45)):
            return
        if not hasattr(self, "replay"):
            import collections
            self.replay = collections.deque(maxlen=self.REPLAY_QUADROS)
            self._rq = 0
        self._rq += 1
        if self._rq % 2 == 0:
            self.replay.append(pygame.transform.scale(tela, (LARGURA // 3, ALTURA // 3)))  # (pequena: pouca memória)

    def replay_tocando(self):
        return (self.fase == "fim" and self.msg == "K.O.!" and len(getattr(self, "replay", ())) > 20
                and not getattr(self, "replay_visto", False))

    def pular_replay(self):
        self.replay_visto = True

    def desenhar_replay(self, tela):
        if not self.replay_tocando():
            return False
        self.replay_i = getattr(self, "replay_i", 0) + 1
        k = self.replay_i // self.REPLAY_LENTO
        if k >= len(self.replay):
            self.replay_visto = True
            return False
        tela.blit(pygame.transform.scale(self.replay[k], (LARGURA, ALTURA)), (0, 0))
        faixa = pygame.Surface((LARGURA, 44), pygame.SRCALPHA)  # (só embaixo: em cima ficam as barras de vida)
        faixa.fill((0, 0, 0, 160))
        tela.blit(faixa, (0, ALTURA - 44))
        if (self.replay_i // 15) % 2:
            pygame.draw.circle(tela, (230, 40, 40), (30, ALTURA - 22), 9)
        texto_grande(tela, "REPLAY", 26, BRANCO, (96, ALTURA - 22), contorno=(40, 0, 0))
        texto(tela, "câmera lenta", 14, (220, 220, 235), (LARGURA // 2, ALTURA - 22))
        texto(tela, "ENTER pula", 13, (220, 220, 230), (LARGURA - 60, ALTURA - 22))
        return True

    def desenhar_brilho_mestre(self, tela):
        """MAESTRIA nível 10: quem joga com o lutador ganha um brilho dourado na pose de vitória."""
        import maestria
        for i in self.lados_humanos():
            l = self.L[i]
            if l.estado == "vitoria" and maestria.brilho_na_vitoria(l.f):
                maestria.desenhar_brilho_vitoria(tela, l.x, CHAO, self.t_total, l.s / l.f["tam"])

    def pular_pro_fim(self):
        """Assistindo os computadores: roda o resto da luta sem desenhar e arruma a tela do resultado
        (as barras de vida e os brilhos param onde a luta parou, nada fica congelado)."""
        for _ in range(FPS * 60 * 6):
            if self.fase == "fim":
                break
            self.passo(None)
        self.faiscas = []
        for l in self.L:
            l.vida_vista = l.vida
            for nome in ("flash_ex", "flash_escape", "flash_acido", "flash_invisivel", "flash_mutacao"):
                if hasattr(l, nome):
                    setattr(l, nome, 0)

    def desenhar_caixas(self, tela):
        """MODO TREINO (tecla H): azul = onde pode apanhar, vermelho = onde o golpe acerta, laranja = tiros."""
        camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        for l in self.L:
            c = l.corpo()
            if c:
                pygame.draw.rect(camada, (60, 140, 255, 70), c)
                pygame.draw.rect(camada, (120, 190, 255, 230), c, 2)
            g = l.caixa_golpe()
            if g:
                pygame.draw.rect(camada, (255, 40, 40, 90), g)
                pygame.draw.rect(camada, (255, 90, 90, 255), g, 2)
            if l.feixe:
                pygame.draw.line(camada, (255, 60, 60, 255), l.feixe[0], l.feixe[1], 3)
        for p in self.projeteis:
            r = p.rect()
            pygame.draw.rect(camada, (255, 160, 40, 90), r)
            pygame.draw.rect(camada, (255, 190, 80, 255), r, 2)
        tela.blit(camada, (0, 0))
        texto(tela, "CAIXAS LIGADAS (H desliga):  azul = apanha   vermelho = acerta   laranja = tiro", 13,
              (220, 230, 255), (LARGURA // 2, 208))

    def desenhar_luta(self, tela):
        """Tudo é desenhado normal e depois vira PIXEL ART: reduz a imagem (cada bloquinho de
        PIXEL x PIXEL vira 1 ponto) e amplia de volta sem borrar. Lutadores ganham contorno de 1 pixel."""
        lw, lh = LARGURA // PIXEL, ALTURA // PIXEL
        if not hasattr(self, "mundo"):
            self.mundo = pygame.Surface((LARGURA, ALTURA))
            self.camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            self.camada_peq = pygame.Surface((lw, lh), pygame.SRCALPHA)
            self.escurecer = pygame.Surface((lw, lh), pygame.SRCALPHA)
        camada = self.camada
        baixo = self.cena.desenhar_pequeno(self.t_total, PIXEL)
        per = self.periodo_atual()
        per.pintar_fundo(baixo, self.t_total)  # DIA E NOITE (só desenho)
        self.destruicao().desenhar(baixo, self.t_total, PIXEL)  # CENÁRIO QUE QUEBRA: rachaduras, buracos, entulho
        camada.fill((0, 0, 0, 0))

        tela_toda = pygame.Rect(0, 0, LARGURA, ALTURA)

        def area(lutadores):
            """Pedaço da tela onde esses lutadores (e os golpes deles) estão, pelos pontos do corpo."""
            r = None
            for l in lutadores:
                if l.feixe or l.extra.get("tronco") or l.extra.get("tela_toda") or l.y < -200 or l.rastro or (l.estado == "ataque" and l.memo.get("tela_toda")) \
                        or l.f.get("tela_toda"):
                    return tela_toda
                p = l.pose_vista or l.pose_atual()
                pts = [l.ponto(p, k) for k in p]
                xs, ys = [q[0] for q in pts], [q[1] for q in pts]
                m = 70 * l.s
                mx = 230 * l.s if l.estado == "ataque" and l.memo.get("pegou") else m
                rl = pygame.Rect(min(xs) - mx, min(ys) - m, max(xs) - min(xs) + 2 * mx, max(ys) - min(ys) + 2 * m)
                rl.union_ip(pygame.Rect(l.x - 40, CHAO - 10, 80, 20))  # sombra
                r = rl if r is None else r.union(rl)
            return r.clip(tela_toda) if r else pygame.Rect(0, 0, 0, 0)

        def passa(contorno, r):
            """Joga o que foi desenhado na camada pra imagem pixelada (só o pedaço r)."""
            if r.w <= 0 or r.h <= 0:
                return
            x0, y0 = r.x // PIXEL * PIXEL, r.y // PIXEL * PIXEL
            x1 = min(LARGURA, -(-r.right // PIXEL) * PIXEL)
            y1 = min(ALTURA, -(-r.bottom // PIXEL) * PIXEL)
            r = pygame.Rect(x0, y0, x1 - x0, y1 - y0)
            if contorno or not EFEITOS_DUROS:
                peq = pygame.transform.smoothscale(camada.subsurface(r), (r.w // PIXEL, r.h // PIXEL))
            else:  # os EFEITOS em pixel art de verdade: cada bloquinho pega uma cor só (borda dura, sem borrão)...
                peq = pygame.transform.scale(camada.subsurface(r), (r.w // PIXEL, r.h // PIXEL))
                try:  # ...e o brilho em DEGRAUS (4 níveis de transparência), igual pixel art, em vez de degradê liso
                    import numpy
                    alfa = pygame.surfarray.pixels_alpha(peq)
                    alfa[:] = numpy.where(alfa < 40, 0, (alfa.astype(numpy.uint16) + 42) // 85 * 85).clip(0, 255)
                    del alfa
                except ImportError:
                    pass
            pos = (x0 // PIXEL, y0 // PIXEL)
            if contorno:
                mascara = pygame.mask.from_surface(peq, 90)
                silhueta = mascara.to_surface(setcolor=(16, 10, 20, 255), unsetcolor=(0, 0, 0, 0))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    baixo.blit(silhueta, (pos[0] + dx, pos[1] + dy))
                limpo = pygame.Surface(peq.get_size(), pygame.SRCALPHA)
                mascara.to_surface(limpo, setsurface=peq, unsetcolor=(0, 0, 0, 0))
                peq = limpo
            baixo.blit(peq, pos)
            camada.fill((0, 0, 0, 0), r)

        # os ENFEITES DO EVENTO (Halloween: teias e abóboras) e o objeto do cenário (atrás dos lutadores)
        en = self.enfeites_evento()
        if en:
            en.desenhar_fundo(camada, self.t_total)
        self.objetos.desenhar(camada)
        meia = getattr(self, "meia", None)
        if meia and meia.cenario == self.cena.nome:
            meia.desenhar(camada)
        self.clima.desenhar(camada)
        passa(False, tela_toda if self.clima.ativo or en or meia else self.objetos.area())
        # quem passa por trás vem primeiro; quem está atacando fica na frente
        import natal
        gorro = natal.gorro_ligado()
        ordem = sorted(self.L, key=lambda l: (not getattr(l, "atras", False), l.estado == "ataque"))
        for l in ordem:
            if self.escuro and l is self.quem_ultimate:

                k = 1 - self.escuro / getattr(self, "escuro_max", ULTIMATE_PAUSA)
                self.escurecer.fill((0, 0, 20, int(190 * min(1, k * 4))))
                baixo.blit(self.escurecer, (0, 0))
                cor = (255, 200, 60) if l.golpe and l.golpe.get("ultimate2") else l.f["cor_poder"]
                cx, cy = l.x, l.y - 60 * l.s
                for i in range(3):  # anéis de energia fechando nele
                    r = int(220 * (1 - k) + 40 + i * 30) % 260 + 30
                    pygame.draw.circle(camada, cor, (int(cx), int(cy)), r, 3)
                for i in range(12):  # riscos de velocidade
                    a = i * math.tau / 12 + self.t_total * 0.05
                    r1, r2 = 330 - k * 150, 420
                    pygame.draw.line(camada, (255, 255, 255), (cx + math.cos(a) * r1, cy + math.sin(a) * r1),
                                     (cx + math.cos(a) * r2, cy + math.sin(a) * r2), 3)
                passa(False, tela_toda)
            if l.tem_atras():  # trono, sofá, cápsula... vão pro fundo ANTES do corpo
                l.desenhar_atras(camada)
                passa(False, tela_toda)
            # cada lutador vira um sprite separado, desenhado direto pequeno, com contorno de 1 pixel
            peq = self.camada_peq
            l.desenhar_px(baixo, peq, camada, PIXEL)
            r = area([l])
            r = pygame.Rect(r.x // PIXEL, r.y // PIXEL, -(-r.w // PIXEL) + 1, -(-r.h // PIXEL) + 1).clip(peq.get_rect())
            if r.w > 0 and r.h > 0:
                pedaco = peq.subsurface(r)
                mascara = pygame.mask.from_surface(pedaco, 90)
                silhueta = mascara.to_surface(setcolor=(16, 10, 20, 255), unsetcolor=(0, 0, 0, 0))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    baixo.blit(silhueta, (r.x + dx, r.y + dy))
                baixo.blit(pedaco, r.topleft)
                peq.fill((0, 0, 0, 0), r)
            if gorro and not l.esconde:  # NATAL: o GORRINHO (se ele ligou nas configurações)
                natal.desenhar_gorro(l, camada)
                passa(False, area([l]))
            if self.fase == "entrada" or l.estado == "vitoria":
                passa(False, tela_toda)
            elif (l.estado == "ataque" and l.golpe and l.golpe.get("efeito")) or l.estado == "tonto"                     or l.efeito_habilidade():
                passa(False, tela_toda if l.feixe or l.y < -200 or l.estado == "ataque" or l.extra.get("pocas")
                      or l.extra.get("tela_toda") or ult2.vivo(l) else area([l]))
        # efeitos por cima (sem contorno)
        for p in self.projeteis:
            p.desenhar(camada)
        for f in self.faiscas:
            tam = f[6] * min(1, f[4] / 12) if len(f) > 6 else f[4] // 4
            pygame.draw.circle(camada, f[5], (int(f[0]), int(f[1])), max(2, int(tam)))
        self.impactos.desenhar(camada)
        pts = [(p.x, p.y) for p in self.projeteis] + [(f[0], f[1]) for f in self.faiscas] + \
            [(i[0], i[1]) for i in self.impactos.lista]
        if pts:
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            m = 140
            passa(False, pygame.Rect(min(xs) - m, min(ys) - m, max(xs) - min(xs) + 2 * m,
                                     max(ys) - min(ys) + 2 * m).clip(tela_toda))
        self.cena.desenhar_frente(baixo, self.t_total, PIXEL)
        per.pintar_tudo(baixo)  # (os lutadores também ficam no tom do período: ninguém "brilha" no escuro)

        ox = oy = 0
        if self.tremor:
            ox = random.randint(-self.tremor, self.tremor) // 2 // PIXEL * PIXEL
            oy = random.randint(-self.tremor, self.tremor) // 2 // PIXEL * PIXEL
        zoom, cx, cy = self.camera
        if zoom > 1.01:  # cutscene: amplia um pedaço da tela
            w, h = lw / zoom, lh / zoom
            x = max(0, min(lw - w, cx / PIXEL - w / 2))
            y = max(0, min(lh - h, cy / PIXEL - h / 2))
            baixo = baixo.subsurface(pygame.Rect(int(x), int(y), int(w), int(h)))
        if ox or oy:  # tremendo: amplia numa imagem guardada (não cria uma nova todo quadro)
            if not hasattr(self, "_grande"):
                self._grande = pygame.Surface((LARGURA, ALTURA))
            pygame.transform.scale(baixo, (LARGURA, ALTURA), self._grande)
            tela.fill(PRETO)
            tela.blit(self._grande, (ox, oy))
        else:
            pygame.transform.scale(baixo, (LARGURA, ALTURA), tela)  # amplia direto na tela
        self.clima.desenhar_frente(tela, self)  # (chuva, folhas, mar... na tela grande: a chuva fininha não some)
        if en and zoom <= 1.01:
            en.desenhar_frente(tela, self.t_total)  # (morcegos, fantasminha, neblina)
        ult2.desenhar_escuro(self, tela)  # CAÇADA NO ESCURO (Tromos): cada PC desenha o seu escuro
        for i, l in enumerate(self.L):  # EFEITOS DE TELA (Nocturnus: cego, enjoo, os Zzz do sono)
            if l.f.get("efeito_tela"):
                l.f["efeito_tela"](l, self.L[1 - i], tela, self)
        if self.cinema > 0.02:  # faixas pretas de cinema
            faixa = int(62 * self.cinema)
            tela.fill(PRETO, (0, 0, LARGURA, faixa))
            tela.fill(PRETO, (0, ALTURA - faixa, LARGURA, faixa))
        if self.clarao:
            if not hasattr(self, "_branco"):
                self._branco = pygame.Surface((LARGURA, ALTURA))
                self._branco.fill(BRANCO)
            self._branco.set_alpha(int(255 * self.clarao / 8))
            tela.blit(self._branco, (0, 0))
        if getattr(self, "narrador", None):
            self.narrador.desenhar(tela)
        if self.fase == "falas":
            self.desenhar_falas(tela)
        if self.fase in ("entrada", "falas") and not getattr(self, "online", False):
            texto(tela, "ENTER pula", 13, (220, 220, 230), (LARGURA - 60, ALTURA - 14))
        elif self.cinema < 0.5:
            self.hud(tela)

    def barra_vida(self, tela, i, l):
        larg, alt, y = 372, 22, 26
        x = 34 if i == 0 else LARGURA - 34 - larg
        inc = 10  # inclinação das pontas

        def forma(x0, w):  # paralelogramo (cresce pro meio da tela)
            if i == 0:
                return [(x0 + inc, y), (x0 + w + inc, y), (x0 + w, y + alt), (x0, y + alt)]
            return [(x0 - inc, y), (x0 + w - inc, y), (x0 + w, y + alt), (x0, y + alt)]

        pygame.draw.polygon(tela, (20, 14, 24), [(px + (-4 if k in (0, 3) else 4), py + (-4 if k < 2 else 4))
                                                   for k, (px, py) in enumerate(forma(x, larg))])
        pygame.draw.polygon(tela, (60, 20, 30), forma(x, larg))
        for valor, cor1, cor2 in ((l.vida_vista, (230, 60, 50), (160, 20, 30)),
                                  (max(0, l.vida), (255, 236, 90), (255, 150, 30))):
            w = int(larg * valor / l.vida_max)
            if w <= 0:
                continue
            perigo = valor == l.vida and l.vida < 25 and (self.t_total // 8) % 2
            if perigo:
                cor1, cor2 = (255, 120, 80), (230, 40, 30)
            x0 = x + larg - w if i == 0 else x
            pts = forma(x0, w)
            pygame.draw.polygon(tela, cor2, pts)
            topo = [pts[0], pts[1], ((pts[1][0] + pts[2][0]) / 2, y + alt * 0.45), ((pts[0][0] + pts[3][0]) / 2, y + alt * 0.45)]
            pygame.draw.polygon(tela, cor1, topo)
            pygame.draw.line(tela, (255, 255, 230), pts[0], pts[1], 2)
        pygame.draw.polygon(tela, (240, 200, 110), forma(x, larg), 2)
        # barrinha da guarda (azul), embaixo da vida
        gw = int(larg * 0.55 * l.guarda / GUARDA_MAX)
        gx = x + larg - int(larg * 0.55) if i == 0 else x
        pygame.draw.rect(tela, (20, 14, 24), (gx - 2, y + alt + 1, int(larg * 0.55) + 4, 7))
        if gw > 0:
            cor_g = (255, 120, 90) if l.guarda < 35 else (120, 200, 255)
            pygame.draw.rect(tela, cor_g, (gx + (int(larg * 0.55) - gw if i == 0 else 0), y + alt + 2, gw, 5))
        # STAMINA (v4.0): barrinha verde embaixo da guarda
        stamina.desenhar_barra(tela, l, gx, y + alt + 9, int(larg * 0.55), i, self.t_total)
        # nome
        nome = fonte(17).render(l.f["nome"], True, BRANCO)
        sombra = fonte(17).render(l.f["nome"], True, PRETO)
        nx = x if i == 0 else x + larg - nome.get_width()
        tela.blit(sombra, (nx + 2, y + alt + 12))
        tela.blit(nome, (nx, y + alt + 10))
        # habilidades (acendem quando estão fazendo efeito)
        hy = y + alt + 30
        for h in hab.ativas(l):
            ligada = hab.ligada(l, h)
            cor = (255, 220, 90) if ligada and (h != "maquinario" or (self.t_total // 10) % 2) else (150, 150, 170)
            img = fonte(12).render(hab.HABILIDADES[h]["nome"], True, cor)
            tela.blit(img, (x if i == 0 else x + larg - img.get_width(), hy))
            hy += 14
        # rounds ganhos (estrelinhas)
        for k in range(ROUNDS_PRA_VENCER):
            cx = x + larg - 14 - k * 24 if i == 0 else x + 14 + k * 24
            cy = y + alt + 22
            ganho = self.vitorias[i] > k
            pts = [(cx + math.cos(a * math.pi / 5 - math.pi / 2) * (9 if a % 2 == 0 else 4),
                    cy + math.sin(a * math.pi / 5 - math.pi / 2) * (9 if a % 2 == 0 else 4)) for a in range(10)]
            pygame.draw.polygon(tela, (255, 214, 60) if ganho else (60, 50, 60), pts)
            pygame.draw.polygon(tela, PRETO, pts, 2)

    def barra_ultimate(self, tela, i, l):
        bw, bh = 230, 14
        x = 34 if i == 0 else LARGURA - 34 - bw
        y = ALTURA - 32
        cheia = l.barra >= BARRA_MAX
        pygame.draw.rect(tela, (10, 10, 20), (x - 3, y - 3, bw + 6, bh + 6), border_radius=4)
        w = int(bw * min(l.barra, BARRA_MAX) / BARRA_MAX)
        # a parte AMARELA (2ª ULTIMATE): metade do tamanho, em cima da azul, enchendo depois que a azul encheu
        aw, ah = bw // 2, 7
        ax = x if i == 0 else x + bw - aw
        ay = y - ah - 5
        amarela_cheia = l.barra >= BARRA_TOTAL
        if l.tem_ult2():
            pygame.draw.rect(tela, (10, 10, 20), (ax - 2, ay - 2, aw + 4, ah + 4), border_radius=3)
            wa = int(aw * max(0, l.barra - BARRA_MAX) / BARRA_AMARELA)
            if wa > 0:
                pulso = (math.sin(self.t_total * 0.3) + 1) / 2 if amarela_cheia else 0
                cor_a = mistura_cor((255, 200, 30), (255, 250, 200), pulso)
                pygame.draw.rect(tela, cor_a, (ax if i == 0 else ax + aw - wa, ay, wa, ah), border_radius=2)
        elif cheia and l.f.get("nome_base", l.f["nome"]) == "RIBBAT":  # (o Ribbat não precisa de 2ª ultimate)
            texto(tela, "NÃO PRECISA", 12, (255, 220, 90), (ax + aw // 2, ay + 3))
        x0 = x if i == 0 else x + bw - w
        if w > 0:
            pulso = (math.sin(self.t_total * 0.25) + 1) / 2 if cheia else 0
            cor = mistura_cor((60, 160, 255), (230, 250, 255), pulso)
            pygame.draw.rect(tela, cor, (x0, y, w, bh), border_radius=3)
            pygame.draw.rect(tela, (200, 240, 255), (x0, y, w, 4), border_radius=2)
        for k in range(1, 4):  # divisões
            pygame.draw.line(tela, (10, 10, 20), (x + bw * k // 4, y), (x + bw * k // 4, y + bh), 2)
        if cheia:
            esc = 1 + 0.08 * math.sin(self.t_total * 0.25)
            if amarela_cheia:
                texto_grande(tela, "ULTIMATE 2!", 18, (255, 200, 40), (x + bw // 2, y - 31), esc)
            elif not l.tem_ult2() or l.barra < BARRA_MAX + BARRA_AMARELA // 4:
                texto_grande(tela, "ULTIMATE!", 18, (255, 230, 90), (x + bw // 2, y - 31), esc)
        mun = l.extra.get("municao")
        if mun:  # munição do personagem (ex: shurikens do Rib)
            n, total, bloqueado = mun
            for k in range(total):
                mx = x + 8 + k * 18 if i == 0 else x + bw - 8 - k * 18
                my = y - 14
                cheia = k < n and not bloqueado
                cor = (220, 225, 235) if cheia else (70, 70, 80)
                pts = [(mx + math.cos(a * math.pi / 4 + self.t_total * 0.05 * cheia) * (7 if a % 2 == 0 else 2.5),
                        my + math.sin(a * math.pi / 4 + self.t_total * 0.05 * cheia) * (7 if a % 2 == 0 else 2.5))
                       for a in range(8)]
                pygame.draw.polygon(tela, cor, pts)
                pygame.draw.polygon(tela, PRETO, pts, 1)
            if bloqueado:
                texto(tela, bloqueado, 13, (255, 150, 120), (x + bw // 2 if i == 0 else x + bw // 2, y - 30))
        armado = getattr(self.ctrl[i], "armado", 0)
        if armado:  # rodinha armada: um anel que vai fechando em cima do lutador
            cx, cy = int(l.x), int(l.y - 150 * l.s)
            pygame.draw.circle(tela, PRETO, (cx, cy), 6 + armado // 5, 4)
            pygame.draw.circle(tela, AMARELO, (cx, cy), 6 + armado // 5, 2)

    def hud(self, tela):
        lento = max(l.extra.get("lento", 0) for l in self.L)
        if lento > 0:  # ESQUIVA PERFEITA: o mundo fica azulado enquanto o oponente está em câmera lenta
            if not hasattr(self, "_tinta_lenta"):
                self._tinta_lenta = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            self._tinta_lenta.fill((90, 200, 255, int(46 * min(1, lento / 12))))
            tela.blit(self._tinta_lenta, (0, 0))
        if getattr(self, "meia", None):  # NATAL: "MEIA DE NATAL! 5/17" / "GORRINHO LIBERADO!"
            self.meia.desenhar_aviso(tela)
        if self.trio:
            self.desenhar_trio(tela)
        if self.regras:  # MODOS MALUCOS ligados
            import malucos
            texto(tela, malucos.nomes(self.regras), 12, (255, 200, 120), (LARGURA // 2, 80))
        for i, l in enumerate(self.L):
            if l.vida_vista > l.vida:
                l.vida_vista = max(l.vida, l.vida_vista - 0.6)
            self.barra_vida(tela, i, l)
            self.barra_ultimate(tela, i, l)
            # RECARGA dos especiais (v4.0): as letrinhas do lado da barra da ultimate
            stamina.desenhar_recargas(tela, l, 34 + 230 + 12 if i == 0 else LARGURA - 34 - 230 - 12, ALTURA - 34,
                                      i, fonte)
        import musica  # o RADINHO tocando a música (pequenininho, embaixo do nome do jogador 1)
        musica.desenhar_radio(tela, 36, 104, musica.nome_de(som.MUSICA_LUTA), self.t_total, 2)
        if not self.treino:  # o RANKING DE ESTILO (a letra) de cada lado
            self.estilos[0].desenhar(tela, 90, 158, self.t_total, 1)
            self.estilos[1].desenhar(tela, LARGURA - 90, 158, self.t_total, -1)
        # relógio
        pygame.draw.rect(tela, (20, 14, 24), (LARGURA // 2 - 38, 14, 76, 56), border_radius=10)
        pygame.draw.rect(tela, (240, 200, 110), (LARGURA // 2 - 38, 14, 76, 56), 3, border_radius=10)
        if self.treino and getattr(self, "combos", None):
            texto(tela, "∞", 36, BRANCO, (LARGURA // 2, 40))
            self.combos.desenhar(tela)
        elif self.treino:
            texto(tela, "∞", 36, BRANCO, (LARGURA // 2, 40))
            modo = getattr(self.ctrl[1], "modo", "")
            texto(tela, f"MODO TREINO   boneco: {modo}", 18, AMARELO, (LARGURA // 2, 128))
            texto(tela, "1 parado  2 defende  3 pula  4 agachado  5 luta     P enche a ultimate     H caixas     ESC sai",
                  13, BRANCO, (LARGURA // 2, 150))
            alvo = self.L[1]
            agora = alvo.vida_max - alvo.vida
            if agora > 0:
                texto_grande(tela, f"{self.golpes_treino} GOLPES  {agora:.0f} DE DANO", 20, (255, 230, 120),
                             (LARGURA // 2, 186))
            elif self.ultimo_combo:
                g, d = self.ultimo_combo
                texto(tela, f"último combo: {g} golpes, {d:.0f} de dano", 16, (220, 220, 230), (LARGURA // 2, 186))
        else:
            segundos = max(0, math.ceil(self.tempo / FPS))
            texto(tela, str(segundos), 36, (255, 90, 70) if segundos <= 10 else BRANCO, (LARGURA // 2, 42))

        if self.combo_txt and not getattr(self, "combos", None):  # (nos desafios de combo já tem os passos)
            lado, n, q = self.combo_txt
            esc = 1 + max(0, (q - 60) / 10) * 0.6  # entra grandão e assenta
            texto_grande(tela, f"{n} GOLPES!", 30, (255, 220, 70), (190 if lado == 0 else LARGURA - 190, 150), esc)
        if self.quebra_txt:
            lado, q = self.quebra_txt
            esc = 1 + max(0, (q - 70) / 10) * 0.5
            texto_grande(tela, "GUARDA QUEBRADA!", 30, (140, 210, 255), (LARGURA // 2, 160), esc, contorno=(10, 20, 50))
        if self.choque_txt:
            txt, quem, q = self.choque_txt
            esc = 1 + max(0, (q - 70) / 10) * 0.6
            x = LARGURA // 2 if quem is None else (190 if quem == 0 else LARGURA - 190)
            texto_grande(tela, txt, 30, (255, 230, 90), (x, 150), esc, contorno=(60, 20, 0))
        if self.esquiva_txt:
            lado, q = self.esquiva_txt
            esc = 1 + max(0, (q - 60) / 10) * 0.6
            texto_grande(tela, "ESQUIVA PERFEITA!", 30, (180, 255, 230), (190 if lado == 0 else LARGURA - 190, 120), esc,
                         contorno=(10, 50, 40))
        if self.parry_txt:
            lado, q = self.parry_txt
            esc = 1 + max(0, (q - 50) / 10) * 0.6
            texto_grande(tela, "PARRY!", 34, (210, 240, 255), (190 if lado == 0 else LARGURA - 190, 150), esc,
                         contorno=(20, 40, 80))
        meio = (LARGURA // 2, 230)
        if self.fase == "intro":
            if self.tf < 70:
                k = min(1, self.tf / 14)
                nome = f"LUTA {self.sobrevivencia + 1}" if self.sobrevivencia is not None else f"ROUND {self.round}"
                texto_grande(tela, nome, 64, BRANCO, meio, 2.6 - 1.6 * k, int(255 * k))
            else:
                k = min(1, (self.tf - 70) / 8)
                texto_grande(tela, "LUTEM!", 84, (255, 220, 60), meio, 0.4 + 0.6 * k + 0.15 * (1 - k))
        elif self.fase == "ko":
            k = min(1, self.tf / 10)
            texto_grande(tela, self.msg, 96, (255, 70, 50), meio, 3 - 2 * k, int(255 * k))
        elif self.fase == "fim":
            k = min(1, self.tf / 15)
            if self.vencedor == "empate":
                texto_grande(tela, "EMPATE!", 70, (255, 220, 60), (LARGURA // 2, 200), 0.5 + 0.5 * k)
            else:
                texto_grande(tela, f"{self.fichas[self.vencedor]['nome']} VENCEU!", 54, (255, 220, 60),
                             (LARGURA // 2, 200), 0.5 + 0.5 * k)
            if getattr(self, "online", False):
                msg = ""  # (o modo online escreve a própria mensagem)
            elif getattr(self, "torneio", False):
                msg = "ENTER: volta pra chave do torneio"
            elif self.sobrevivencia is not None:
                if self.vencedor == 0:
                    msg = f"DERRUBOU {self.sobrevivencia + 1}!   ENTER: próxima luta (a vida volta um pouco)"
                else:
                    msg = f"FIM! Você derrubou {self.sobrevivencia}   RECORDE: {save.recorde()}   ENTER: de novo   ESC: menu"
            elif self.arcade:
                msg = "ENTER: próxima luta" if self.vencedor == 0 else "CONTINUAR?   ENTER: tentar de novo     ESC: menu"
            else:
                msg = "ENTER: revanche     ESC: menu"
            texto(tela, msg, 22 if len(msg) < 60 else 18, BRANCO, (LARGURA // 2, 280))
            if self.premio:
                self.desenhar_premio(tela)
            if getattr(self, "maestria_info", None):
                self.desenhar_maestria(tela)
            self.desenhar_conquistas(tela)
            if getattr(self, "figurinha_ganha", None) and self.tf < 200:  # a FIGURINHA que saiu (girando)
                import figurinhas
                figurinhas.desenhar_ganho(tela, self.figurinha_ganha, self.tf)

    def desenhar_premio(self, tela):
        """O quadro das moedas que ganhou (e os desafios cumpridos)."""
        itens, nivel, mult, total, cumpridos = self.premio
        doces = getattr(self, "doces_ganhos", 0)
        linhas = max(1, len(itens)) + len(cumpridos) + 2 + (1 if doces else 0)
        r = pygame.Rect(LARGURA // 2 - 230, 302, 460, 20 + linhas * 21)
        caixa = pygame.Surface(r.size, pygame.SRCALPHA)
        caixa.fill((14, 10, 26, 215))
        tela.blit(caixa, r.topleft)
        pygame.draw.rect(tela, (255, 210, 90), r, 2, border_radius=8)
        y = r.y + 18
        for nome, v in itens:
            texto(tela, nome, 15, BRANCO, (r.centerx - 60, y))
            texto(tela, f"+{v}", 15, (255, 220, 90), (r.right - 60, y))
            y += 21
        if not itens:
            texto(tela, "nada dessa vez... tenta um QUASE PERFECT!", 14, (200, 200, 210), (r.centerx, y))
            y += 21
        cor = (120, 230, 120) if mult > 1 else (255, 140, 110) if mult < 1 else (220, 220, 230)
        texto(tela, f"{nivel}  x{mult:g}", 15, cor, (r.centerx, y))
        y += 21
        for nome, v in cumpridos:
            texto(tela, f"DESAFIO! {nome}", 13, (150, 230, 255), (r.centerx - 40, y))
            texto(tela, f"+{v}", 15, (255, 220, 90), (r.right - 40, y))
            y += 21
        if doces:  # HALLOWEEN: os doces da luta
            from efeitos import doce
            texto(tela, "HALLOWEEN!", 14, (255, 150, 50), (r.centerx - 60, y))
            doce(tela, (r.right - 84, y), 9, self.tf)
            texto(tela, f"+{doces}", 15, (255, 150, 50), (r.right - 52, y))
            y += 21
        k = min(1.0, self.tf / 40)
        geral = total + sum(v for _, v in cumpridos)
        texto_moedas(tela, f"+{round(geral * k)}", r.centerx + 40, y + 2, self.tf, 21)
