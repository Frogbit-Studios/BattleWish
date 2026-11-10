"""BATTLE WISH (Desejo de Batalha) — o jogo de luta do Gomes. Rode este arquivo pra jogar."""
import gc
import os
import random
import sys

import pygame

from config import *  # noqa: F401,F403
from controles import BonecoTreino, Computador, Jogador
from lutador import Lutador
from partida import Partida, cenario, texto
import som
from abertura import Abertura, logo
from selecao import TelaCenario, TelaSelecao, TelaVS
from historia import ABERTURA, FINAIS, Creditos, Quadrinho, final_generico
from personagens import CORES_BONECO, PERSONAGENS, boneco, disponiveis, sombra
import controle_video
import roupas
import save
from efeitos import texto_grande, texto_moedas
from loja import TelaLoja

# o menu em 2 colunas: as lutas na esquerda, o resto na direita
# (ARCADE e CPU x CPU saíram do menu: pedido do Gomes, "ninguém quer assistir PC batalhando")
MODOS = ["1 JOGADOR", "2 JOGADORES", "REI DA ARENA", "TRIO", "TORNEIO", "ONLINE", "SOBREVIVÊNCIA", "MODOS MALUCOS",
         "MODO TREINO", "COMBOS", "LOJA", "DESAFIOS", "CÓDIGOS", "COMO JOGAR", "PERFIL", "CONFIGURAÇÕES", "SAIR"]
if __import__("eventos").tem_conteudo() == "HALLOWEEN":  # EVENTO: o PASSE aparece no menu (antes do SAIR)
    MODOS.insert(len(MODOS) - 1, "PASSE DO HALLOWEEN")
POR_COLUNA = 9
(UM, DOIS, REI, TRIO, TORNEIO, ONLINE, SOBREV, MALUCOS, TREINO, COMBOS, LOJA, DESAFIOS, CODIGOS, COMOJOGAR,
 PERFIL, CONFIG) = range(16)
ARCADE, CPU = -1, -2  # (fora do menu: o código deles ficou guardado)
COM_REGRAS = (UM, DOIS, REI, TRIO, TORNEIO, CPU, TREINO)  # onde os MODOS MALUCOS valem
PAUSA = ["CONTINUAR", "MODO FOTO", "RECOMEÇAR", "MENU PRINCIPAL"]
SOBREV_VOLTA = 30  # quanto de vida volta entre uma luta e outra na Sobrevivência
COM_NIVEL = (UM, CPU, TRIO, TORNEIO)  # modos que têm dificuldade
NIVEIS = list(Computador.NIVEIS)

class Jogo:
    def __init__(self):
        pygame.init()
        som.aplicar_volumes()  # (os volumes das CONFIGURAÇÕES)
        # SCALED: a tela cresce junto quando fica em tela cheia (F11), sem borrar a pixel art
        try:
            self.tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.SCALED)
        except pygame.error:  # computador sem suporte (ou rodando os testes): janela normal
            self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Battle Wish")
        try:  # o ícone da janela (o mesmo do .exe)
            pasta = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
            pygame.display.set_icon(pygame.image.load(os.path.join(pasta, "battlewish_icone.png")))
        except (pygame.error, FileNotFoundError):
            pass
        self.relogio = pygame.time.Clock()
        self.acumulado = 1 / FPS
        self.fundo = cenario()
        self.tela_atual = "abertura"
        self.abertura = Abertura(PERSONAGENS)
        self.t_menu = 0
        self.opcao = 0
        self.nivel = 1
        self.partida = None
        self.escolha = [0, 1]
        self.escolhendo = 0
        self.cor_boneco = 0
        self.pausado = False
        self.opcao_pausa = 0
        self.lista = PERSONAGENS
        save.carregar()
        import eventos
        self.doces_viraram = eventos.converter_sobras()  # o Halloween acabou: os doces que sobraram viram moedas
        self.doces_viraram_t = 400 if self.doces_viraram else 0
        controle_video.iniciar()

    # ------------------------------------------------------------ telas
    def rect_modo(self, i):
        col, lin = divmod(i, POR_COLUNA)
        return pygame.Rect((290 if col == 0 else 670) - 170, 175 + lin * 32 - 14, 340, 28)

    def titulo(self, tecla):
        col, lin = divmod(self.opcao, POR_COLUNA)
        n_col = min(POR_COLUNA, len(MODOS) - col * POR_COLUNA)  # (a coluna da direita tem um a menos)
        if tecla in (pygame.K_UP, pygame.K_w):
            self.opcao = col * POR_COLUNA + (lin - 1) % n_col
        elif tecla in (pygame.K_DOWN, pygame.K_s):
            self.opcao = col * POR_COLUNA + (lin + 1) % n_col
        elif tecla in (pygame.K_LEFT, pygame.K_a) and self.opcao in COM_NIVEL:
            self.nivel = (self.nivel - 1) % len(NIVEIS)
        elif tecla in (pygame.K_RIGHT, pygame.K_d) and self.opcao in COM_NIVEL:
            self.nivel = (self.nivel + 1) % len(NIVEIS)
        elif tecla in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):  # troca de coluna
            self.opcao = min(len(MODOS) - 1, (1 - col) * POR_COLUNA + lin)
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE, "clique"):
            if MODOS[self.opcao] == "SAIR":
                self.sair()
            self.modo = self.opcao
            self.escolhendo = 0
            self.lista = PERSONAGENS
            if self.modo == CPU:  # computador x computador: sorteia e vai pro VS
                self.escolha = [random.randrange(len(PERSONAGENS)) for _ in range(2)]
                self.cenario_nome = None
                self.ir_pro_vs()
            elif self.modo == LOJA:
                self.loja = TelaLoja(PERSONAGENS)
                self.tela_atual = "loja"
            elif self.modo == ONLINE:
                from online import Online
                self.online = Online()
                self.tela_atual = "online"
            elif self.modo == DESAFIOS:
                from desafios import TelaDesafios
                self.tdesafios = TelaDesafios()
                self.tela_atual = "desafios"
            elif self.modo == MALUCOS:
                from malucos import TelaMalucos
                self.tmalucos = TelaMalucos()
                self.tela_atual = "malucos"
            elif self.modo == TRIO:
                self.trio_meus = []
                self.lista = disponiveis()
                self.sel = TelaSelecao(self.lista, so_um=True, titulo="TRIO: ESCOLHA O 1º LUTADOR")
                self.tela_atual = "escolha"
            elif self.modo == COMOJOGAR:
                from como_jogar import TelaComoJogar
                self.tcomo = TelaComoJogar()
                self.tela_atual = "como"
            elif MODOS[self.modo].startswith("PASSE DO"):
                from passe import TelaPasse
                self.tpasse = TelaPasse()
                self.tela_atual = "passe"
            elif self.modo == PERFIL:
                from perfil import TelaPerfil
                self.tperfil = TelaPerfil()
                self.tela_atual = "perfil"
            elif self.modo == CONFIG:
                from configuracoes import TelaConfiguracoes
                self.tconfig = TelaConfiguracoes()
                self.tela_atual = "config"
            elif self.modo == CODIGOS:
                from codigos import TelaCodigos
                self.tcodigos = TelaCodigos()
                self.tela_atual = "codigos"
            elif self.modo in (DOIS, REI) and not controle_video.CONTROLES:
                self.aviso_t = 180  # precisa de um controle pro jogador 2
            elif self.modo == REI:  # REI DA ARENA: os nomes da turma
                import reiarena
                self.tnomes = reiarena.TelaNomes(getattr(self, "rei_nomes", None))
                self.tela_atual = "rei_nomes"
            else:
                self.lista = disponiveis()  # (com os secretos desbloqueados)
                self.sel = TelaSelecao(self.lista, so_um=self.modo in (TREINO, ARCADE, SOBREV, COMBOS, TORNEIO),
                                       rotulo2="2P" if self.modo == DOIS else "CPU")
                self.tela_atual = "escolha"

    def depois_da_selecao(self):
        self.escolha = [i if i is not None else 0 for i in self.sel.escolhido]
        if self.modo == ARCADE:  # Arcade: quadrinho da abertura e depois as lutas em sequência
            eu = self.lista[self.escolha[0]]
            rivais = [f for f in PERSONAGENS if f["nome"] != eu["nome"]]
            self.fila = rivais + [sombra(eu)]
            self.fila_i = 0
            self.quadrinho = Quadrinho(ABERTURA)
            self.depois_quadrinho = "arcade_luta"
            self.tela_atual = "quadrinho"
        elif self.modo == COMBOS:  # desafios de combo: direto pro treino com a lista de combos
            self.comecar()
        elif self.modo == TRIO:  # TRIO: escolhe 3 (um de cada vez)
            self.trio_meus.append(self.lista[self.escolha[0]])
            if len(self.trio_meus) < 3:
                n = len(self.trio_meus) + 1
                self.sel = TelaSelecao(self.lista, so_um=True, titulo=f"TRIO: ESCOLHA O {n}º LUTADOR")
                return
            self.trio_cpu = random.sample(PERSONAGENS, 3)
            self.cenario_nome = None
            self.ir_pro_vs()
        elif self.modo == TORNEIO:  # TORNEIO: monta a chave
            from torneio import Torneio
            self.torneio = Torneio(roupas.vestir(self.lista[self.escolha[0]]), PERSONAGENS, NIVEIS[self.nivel])
            self.tela_atual = "torneio"
        elif self.modo == SOBREV:  # Sobrevivência: um atrás do outro até cair
            self.sobrev = {"n": 0, "vida": None, "ultimo": None}
            self.sobrev_proxima()
        elif self.modo == TREINO:  # treino: agora escolhe a cor do boneco
            self.escolhendo = 1
            self.tela_atual = "cor"
        else:  # agora o cenário (começa na casa do adversário)
            if self.modo == REI:  # (lembra o lutador de cada um)
                rei, desafiante = self.arena.proxima_luta()
                self.arena.lutador[rei], self.arena.lutador[desafiante] = self.escolha[0], self.escolha[1]
            self.tcen = TelaCenario(self.lista[self.escolha[1]].get("cenario", "TEMPLO"))
            self.tela_atual = "cenario"

    def ir_pro_vs(self):
        self.vs = TelaVS(*self.fichas_da_luta())
        self.tela_atual = "vs"

    def fichas_da_luta(self):
        if self.modo == TRIO:
            return roupas.vestir(self.trio_meus[0]), roupas.vestir(self.trio_cpu[0], "padrao")
        if self.modo == TORNEIO:
            if getattr(self, "assistindo", False):  # luta de computadores do torneio
                return self.torneio.fichas_cpu()
            meu, dele, _ = self.torneio.fichas_da_luta()
            return meu, dele
        if self.modo == ARCADE:
            f1, f2 = self.lista[self.escolha[0]], self.fila[self.fila_i]
        elif self.modo == SOBREV:
            f1, f2 = self.lista[self.escolha[0]], self.sobrev["rival"]
        elif self.modo == COMBOS:
            return roupas.vestir(self.lista[self.escolha[0]]), boneco(self.cor_boneco)
        else:
            f1, f2 = (self.lista[i] for i in self.escolha)
        # você usa a roupa que escolheu; o computador usa a original (no espelho, uma diferente da sua)
        f1 = roupas.vestir(f1) if self.modo != CPU else roupas.vestir(f1, "padrao")
        sel = getattr(self, "sel", None)  # (a roupa que você escolheu pro adversário na seleção, com Q/E)
        f2 = roupas.vestir(f2, sel.roupa_bot.get(f2["nome"], "padrao") if sel else "padrao")
        if f1["nome"] == f2["nome"] and f1["roupa"] == f2["roupa"]:
            f2 = roupas.outra(f2, f1["roupa"])
        return f1, f2

    def sobrev_proxima(self):
        """Sobrevivência: sorteia o próximo adversário (nunca o mesmo duas vezes seguidas)."""
        opcoes = [f for f in PERSONAGENS if f["nome"] != self.sobrev["ultimo"]]
        rival = random.choice(opcoes)
        self.sobrev["rival"], self.sobrev["ultimo"] = rival, rival["nome"]
        self.cenario_nome = None
        self.ir_pro_vs()

    def sobrev_nivel(self):
        n = self.sobrev["n"]
        return "FÁCIL" if n < 2 else "MÉDIO" if n < 5 else "DIFÍCIL"

    def arcade_proxima(self):
        """Depois de vencer: próxima luta, ou o final + créditos."""
        self.fila_i += 1
        if self.fila_i >= len(self.fila):
            nome = self.lista[self.escolha[0]]["nome"]
            self.quadrinho = Quadrinho(FINAIS.get(nome) or final_generico(nome))  # personagem novo: final simples
            self.depois_quadrinho = "creditos"
            self.tela_atual = "quadrinho"
            som.musica("menu")
        else:
            self.cenario_nome = None
            self.ir_pro_vs()

    def desenhar_titulo(self):
        t = self.tela
        import eventos
        if not eventos.desenhar_menu(t, self.t_menu):  # (EVENTO: o fundo de Halloween, com a aranhinha)
            t.blit(self.fundo, (0, 0))
        if not hasattr(self, "vitrine"):  # o LUTADOR FAVORITO lutando contra a sombra dele, atrás das opções
            import vitrine
            self.vitrine = vitrine.Vitrine()
        self.vitrine.passo()
        self.vitrine.desenhar(t)
        logo(t, (LARGURA // 2, 80), 0.58, self.t_menu)
        self.t_menu += 1
        texto_moedas(t, save.moedas(), LARGURA - 22, 26, self.t_menu, 22)
        if eventos.tem_conteudo() == eventos.HALLOWEEN:  # o saldo de DOCES
            from efeitos import doce
            doce(t, (LARGURA - 92, 74), 8, self.t_menu)
            texto(t, f"{eventos.doces()} doces", 15, (255, 160, 60), (LARGURA - 44, 74))
        if self.doces_viraram_t > 0:
            self.doces_viraram_t -= 1
            texto(t, f"O Halloween acabou: seus {self.doces_viraram // eventos.MOEDAS_POR_DOCE} doces viraram "
                     f"{self.doces_viraram} moedas!", 18, (255, 170, 70), (LARGURA // 2, 140))
        if save.recorde():
            texto(t, f"recorde da Sobrevivência: {save.recorde()}", 13, (220, 220, 230), (LARGURA - 120, 52))
        for i, m in enumerate(MODOS):
            sel = i == self.opcao
            txt = m
            if i in COM_NIVEL:
                txt += f"  < {NIVEIS[self.nivel]} >"
            texto(t, ("> " if sel else "") + txt, 25 if sel else 20, AMARELO if sel else BRANCO,
                  self.rect_modo(i).center)
        if getattr(self, "aviso_t", 0) > 0:
            self.aviso_t -= 1
            texto(t, "2 JOGADORES: conecte um controle de videogame pro jogador 2", 16, (255, 140, 120),
                  (LARGURA // 2, 460))
        else:
            n = len(controle_video.CONTROLES)
            extra = f"   controles: {n}" if n else ""
            texto(t, "WASD escolhe   A/D dificuldade   ENTER confirma   F11 tela cheia   (dúvidas? COMO JOGAR)" + extra, 15,
                  BRANCO, (LARGURA // 2, 460))
        if not hasattr(self, "selo_frogbit"):  # assinatura do estúdio, no canto
            try:
                pasta = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
                self.selo_frogbit = pygame.image.load(os.path.join(pasta, "frogbit_selo_2x.png")).convert_alpha()
            except (pygame.error, FileNotFoundError):
                self.selo_frogbit = None
        if self.selo_frogbit:
            t.blit(self.selo_frogbit, (12, ALTURA - self.selo_frogbit.get_height() - 10))

    def escolher(self, tecla):
        """Treino: escolhe a cor do boneco."""
        if tecla in (pygame.K_a, pygame.K_LEFT):
            self.cor_boneco = (self.cor_boneco - 1) % len(CORES_BONECO)
        elif tecla in (pygame.K_d, pygame.K_RIGHT):
            self.cor_boneco = (self.cor_boneco + 1) % len(CORES_BONECO)
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE, "clique"):
            self.comecar()

    def desenhar_escolha(self):
        t = self.tela
        t.blit(self.fundo, (0, 0))
        nome, _, _ = CORES_BONECO[self.cor_boneco]
        texto(t, "COR DO BONECO DE TREINO", 40, AMARELO, (LARGURA // 2, 60))
        b = getattr(self, "_vitrine_boneco", None)
        if b is None or b.f["cor"] != CORES_BONECO[self.cor_boneco][1]:
            b = self._vitrine_boneco = Lutador(boneco(self.cor_boneco), 0, 1)
        b.x, b.y = LARGURA // 2, 340
        b.chao_sombra = 340
        b.t += 1
        b.desenhar(t)
        texto(t, f"< {nome} >", 30, BRANCO, (LARGURA // 2, 380))
        texto(t, "A/D troca a cor   ENTER ou clique começa o treino", 18, BRANCO, (LARGURA // 2, 430))

    def comecar(self):
        self._comecar()
        if self.partida and self.modo in COM_REGRAS:  # MODOS MALUCOS
            import malucos
            self.partida.regras.update(malucos.ligadas())

    def _comecar(self):
        self.pausado = False
        self.partida = None
        gc.collect()  # solta a memória da luta anterior antes de criar outra
        f1, f2 = self.fichas_da_luta()
        nivel = NIVEIS[self.nivel]
        if self.modo == ARCADE:  # cada luta mais difícil (a Sombra é no difícil)
            nivel = NIVEIS[min(len(NIVEIS) - 1, self.fila_i)]
            self.partida = Partida(f1, f2, Jogador(), Computador(nivel))
            self.partida.arcade = True
            self.partida.ultima_arcade = self.fila_i == len(self.fila) - 1
            self.tela_atual = "luta"
            som.musica("luta")
            return
        if self.modo == COMBOS:  # treino com a lista de combos pra aprender
            from combos import TreinoCombos
            p = self.partida = Partida(f1, f2, Jogador(), BonecoTreino(), treino=True)
            p.combos = TreinoCombos(f1)
            p.combos.i = getattr(self, "combo_i", 0) if getattr(self, "combo_de", None) == f1["nome"] else 0
            p.combos.arrumar(p)
            self.combo_de = f1["nome"]
            self.tela_atual = "luta"
            som.musica("luta")
            return
        if self.modo == SOBREV:  # uma luta só (1 round), com a vida que sobrou
            p = self.partida = Partida(f1, f2, Jogador(), Computador(self.sobrev_nivel()))
            p.rounds = 1
            p.sobrevivencia = self.sobrev["n"]
            if self.sobrev["vida"] is not None:
                p.vida_inicial = p.vida_comeco = self.sobrev["vida"]
                p.L[0].vida = p.L[0].vida_vista = self.sobrev["vida"]
            self.tela_atual = "luta"
            som.musica("luta")
            return
        if self.modo == TRIO:  # TRIO: 3 contra 3, troca no meio da luta
            meus = [roupas.vestir(f) for f in self.trio_meus]
            deles = [roupas.vestir(f, "padrao") for f in self.trio_cpu]
            self.partida = Partida(None, None, Jogador(), Computador(nivel), trio=(meus, deles))
            self.tela_atual = "luta"
            som.musica("luta")
            return
        if self.modo == TORNEIO:
            if getattr(self, "assistindo", False):  # assistindo dois computadores
                self.partida = Partida(f1, f2, Computador(self.torneio.nivel), Computador(self.torneio.nivel))
                self.partida.assistindo = True
            else:
                self.partida = Partida(f1, f2, Jogador(), Computador(self.torneio.nivel))
            self.partida.torneio = True
            self.tela_atual = "luta"
            som.musica("luta")
            return
        if self.modo == TREINO:  # MODO TREINO
            self.partida = Partida(f1, boneco(self.cor_boneco), Jogador(), BonecoTreino(), treino=True)
            self.tela_atual = "luta"
            som.musica("luta")
            return
        c1 = Computador(nivel) if self.modo == CPU else Jogador()
        c2 = Computador(nivel)
        if self.modo in (DOIS, REI):  # 2 JOGADORES: o 1 no teclado e mouse (e no 1º controle, se tiver dois), o 2 no controle
            cs = controle_video.CONTROLES
            c1 = Jogador(controle=cs[0] if len(cs) >= 2 else None)
            c2 = Jogador(controle=cs[-1] if cs else None, teclado=False)
        self.partida = Partida(f1, f2, c1, c2, cenario_nome=getattr(self, "cenario_nome", None))
        self.tela_atual = "luta"
        som.musica("luta")

    def depois_do_quadrinho(self):
        if self.depois_quadrinho == "arcade_luta":
            self.cenario_nome = None
            self.ir_pro_vs()
        else:
            self.creditos = Creditos()
            self.tela_atual = "creditos"

    # ------------------------------------------------------------ REI DA ARENA
    def evento_rei(self, ev):
        import reiarena
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
            return
        if self.tela_atual == "rei_nomes":
            t = self.tnomes
            if ev.type == pygame.KEYDOWN:
                t.tecla(ev)
            elif ev.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                t.mouse(ev.pos, ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1)
            if t.sair:
                self.tela_atual = "titulo"
            elif t.pronto:
                self.rei_nomes = list(t.nomes)
                self.arena = reiarena.ReiArena(t.nomes)
                self.tplacar = reiarena.TelaPlacar(self.arena)
                self.tela_atual = "rei_placar"
            return
        t = self.tplacar
        if ev.type == pygame.KEYDOWN:
            t.tecla(ev.key)
        elif ev.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            t.mouse(ev.pos, ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1)
        if t.sair:
            self.tela_atual = "titulo"
        elif t.continuar:  # próxima luta: escolhem os lutadores (já no último que cada um usou)
            rei, desafiante = self.arena.proxima_luta()
            self.lista = disponiveis()
            self.sel = TelaSelecao(self.lista, rotulo2="2P", titulo=f"REI: {rei}   x   DESAFIANTE: {desafiante}")
            for lado, nome in enumerate((rei, desafiante)):
                i = self.arena.lutador.get(nome)
                if i is not None and i < len(self.lista):
                    self.sel.cursor[lado] = i
            self.tela_atual = "escolha"

    # ------------------------------------------------------------ pausa
    def rect_pausa(self, i):
        return pygame.Rect(70, 190 + i * 56, 300, 44)

    def pausa(self, tecla):
        if tecla in (pygame.K_UP, pygame.K_w):
            self.opcao_pausa = (self.opcao_pausa - 1) % len(PAUSA)
            som.tocar("blip")
        elif tecla in (pygame.K_DOWN, pygame.K_s):
            self.opcao_pausa = (self.opcao_pausa + 1) % len(PAUSA)
            som.tocar("blip")
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE, "clique"):
            som.tocar("confirma")
            escolha = PAUSA[self.opcao_pausa]
            self.pausado = False
            if escolha == "CONTINUAR":
                if isinstance(self.partida.ctrl[0], Jogador):  # o clique do menu não vira soco
                    self.partida.ctrl[0].antes = {"soco": True, "chute": True}
            elif escolha == "MODO FOTO":  # a luta congelada: câmera, zoom, filtro e salva PNG
                import foto
                sem_hud = pygame.Surface((LARGURA, ALTURA))
                self.partida.desenhar_luta(sem_hud)
                com_hud = pygame.Surface((LARGURA, ALTURA))
                self.partida.desenhar(com_hud)
                self.tfoto = foto.TelaFoto(sem_hud, com_hud)
                self.pausado = True
                self.tela_atual = "foto"
            elif escolha == "RECOMEÇAR":
                self.comecar()
            else:
                self.tela_atual = "titulo"
                som.musica("menu")

    def desenhar_pausa(self):
        t = self.tela
        escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        escuro.fill((6, 4, 14, 190))
        t.blit(escuro, (0, 0))
        texto_grande(t, "PAUSA", 60, (255, 220, 70), (LARGURA // 2, 70))
        for i, op in enumerate(PAUSA):
            r = self.rect_pausa(i)
            sel = i == self.opcao_pausa
            pygame.draw.rect(t, (54, 46, 84) if sel else (26, 22, 42), r, border_radius=10)
            pygame.draw.rect(t, (255, 220, 70) if sel else (70, 62, 100), r, 3, border_radius=10)
            texto(t, op, 22 if sel else 19, AMARELO if sel else BRANCO, r.center)
        # lista de golpes do seu lutador
        f = self.partida.fichas[0]
        x0 = 420
        pygame.draw.rect(t, (20, 16, 34), (x0, 130, 500, 330), border_radius=12)
        pygame.draw.rect(t, (90, 80, 130), (x0, 130, 500, 330), 2, border_radius=12)
        texto(t, f"GOLPES DE {f['nome']}", 22, AMARELO, (x0 + 250, 156))
        n = f.get("nomes")
        y = 194
        no_controle = controle_video.no_controle()
        if n:
            texto(t, "no controle, cada especial tem o seu botão:" if no_controle else "segura M3 (rodinha) e aperta:",
                  14, (190, 190, 210), (x0 + 250, y))
            y += 28
            from efeitos import texto_botao
            for b in ("E", "Q", "R", "SHIFT", "Z"):
                texto_botao(t, b, n[b], 17, BRANCO, (x0 + 250, y))
                y += 26
        if f.get("habilidade"):
            import habilidades as hab
            h = hab.HABILIDADES[f["habilidade"]]
            y += 6
            texto(t, "PASSIVA: " + h["nome"], 16, (255, 220, 90), (x0 + 250, y))
            texto(t, h["desc"], 13, (220, 220, 235), (x0 + 250, y + 22))
            y += 50
        if no_controle:
            texto(t, "A soco   B chute   cima pula   baixo agacha   trás defende", 14, (190, 190, 210), (x0 + 250, y))
            texto(t, "toque pra frente na hora = PARRY     LT provoca", 14, (190, 190, 210), (x0 + 250, y + 22))
        else:
            texto(t, "M1 soco   M2 chute   W pula   S agacha   trás defende", 14, (190, 190, 210), (x0 + 250, y))
            texto(t, "M3 2x + especial = EX   apanhando: M3 2x = ESCAPE   T provoca", 13, (190, 190, 210),
                  (x0 + 250, y + 22))
        rodape = "direcional escolhe   A confirma   START continua" if no_controle else             "W/S escolhe   ENTER ou clique confirma   ESC continua"
        texto(t, rodape, 14, (200, 200, 220), (LARGURA // 2, ALTURA - 16))

    def torneio_enter(self, pular=False):
        t = self.torneio
        if t.campeao is not None:  # acabou: volta pro menu
            self.tela_atual = "titulo"
            return
        self.assistindo = False
        if t.tem_humano():  # a sua luta
            if pular:
                return
            som.tocar("confirma")
            self.cenario_nome = None
            self.ir_pro_vs()
        elif not pular:  # luta entre computadores: ASSISTE
            som.tocar("confirma")
            self.assistindo = True
            self.cenario_nome = None
            self.ir_pro_vs()
        else:  # S: pula (simula rapidinho)
            texto(self.tela, "simulando...", 22, AMARELO, (LARGURA // 2, ALTURA // 2))
            pygame.display.flip()
            t.simular_proxima()

    def pular_luta_assistida(self):
        """Assistindo os computadores: ENTER pula pro resultado (roda o resto da luta sem desenhar)."""
        self.partida.pular_pro_fim()

    def sair(self):
        pygame.quit()
        sys.exit()

    # ------------------------------------------------------------ laço
    def rodar(self):
        som.musica("menu")
        som.preparar_musicas()  # (as músicas do Gomes vão sendo fabricadas enquanto está no menu)
        while True:
            som.atualizar()  # (ficou pronta: troca na hora)
            for ev in pygame.event.get():
                if ev.type in (getattr(pygame, "CONTROLLERDEVICEADDED", -1), getattr(pygame, "CONTROLLERDEVICEREMOVED", -1)):
                    controle_video.atualizar()
                controle_video.perceber(ev)  # (teclado ou controle? a tela mostra os botões certos)
                tecla = controle_video.tecla_do_evento(ev, self.tela_atual == "luta" and not self.pausado)
                if tecla is not None:  # botão do controle nos menus = tecla
                    ev = pygame.event.Event(pygame.KEYDOWN, key=tecla, unicode="", mod=0, scancode=0)
                if ev.type == pygame.QUIT:
                    if self.tela_atual == "online":
                        self.online.voltar_menu()  # avisa o amigo que saiu
                    self.sair()
                if self.tela_atual in ("rei_nomes", "rei_placar"):  # REI DA ARENA (as telas cuidam das teclas)
                    self.evento_rei(ev)
                    continue
                if self.tela_atual == "foto":  # MODO FOTO: ele cuida de tudo (ESC volta pra pausa)
                    if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                    else:
                        self.tfoto.evento(ev)
                    if self.tfoto.sair:
                        self.tela_atual = "luta"
                        self.pausado = True
                    continue
                if self.tela_atual == "online":  # o modo online cuida das próprias teclas
                    if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                    else:
                        self.online.evento(ev)
                    continue
                if ev.type == pygame.MOUSEMOTION and self.tela_atual == "escolha":
                    self.sel.mouse(ev.pos, False)
                if ev.type == pygame.MOUSEMOTION and self.tela_atual == "cenario":
                    self.tcen.mouse(ev.pos, False)
                if ev.type == pygame.MOUSEMOTION and self.tela_atual == "loja":
                    self.loja.mouse(ev.pos, False)
                if ev.type == pygame.MOUSEMOTION and self.tela_atual == "config":
                    self.tconfig.mouse(ev.pos, False)
                if ev.type == pygame.MOUSEMOTION and self.tela_atual == "perfil":
                    self.tperfil.mouse(ev.pos, False)
                if ev.type == pygame.MOUSEMOTION and self.tela_atual == "passe":
                    self.tpasse.mouse(ev.pos, False)
                if ev.type == pygame.MOUSEMOTION and self.tela_atual == "titulo":
                    for i in range(len(MODOS)):
                        if self.rect_modo(i).collidepoint(ev.pos):
                            self.opcao = i
                if ev.type == pygame.MOUSEMOTION and self.tela_atual == "luta" and self.pausado:
                    for i in range(len(PAUSA)):
                        if self.rect_pausa(i).collidepoint(ev.pos):
                            self.opcao_pausa = i
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self.tela_atual == "luta" and self.pausado:
                        if any(self.rect_pausa(i).collidepoint(ev.pos) for i in range(len(PAUSA))):
                            self.pausa("clique")
                    elif self.tela_atual == "loja":
                        self.loja.mouse(ev.pos, True)
                    elif self.tela_atual == "config":
                        self.tconfig.mouse(ev.pos, True)
                    elif self.tela_atual == "perfil":
                        self.tperfil.mouse(ev.pos, True)
                    elif self.tela_atual == "passe":
                        self.tpasse.mouse(ev.pos, True)
                    elif self.tela_atual == "abertura":
                        self.tela_atual = "titulo"
                    elif self.tela_atual == "titulo":
                        if self.rect_modo(self.opcao).collidepoint(ev.pos):
                            self.titulo("clique")
                    elif self.tela_atual == "escolha":
                        self.sel.mouse(ev.pos, True)
                        if self.sel.pronto:
                            self.depois_da_selecao()
                    elif self.tela_atual == "cor":
                        self.escolher("clique")
                    elif self.tela_atual == "cenario":
                        self.tcen.mouse(ev.pos, True)
                        if self.tcen.pronto:
                            self.cenario_nome = self.tcen.escolhido
                            self.ir_pro_vs()
                    elif self.tela_atual == "vs":
                        self.comecar()
                if ev.type != pygame.KEYDOWN:
                    continue
                if ev.key == pygame.K_F11:  # tela cheia liga/desliga
                    pygame.display.toggle_fullscreen()
                    continue
                if self.tela_atual == "abertura":  # qualquer tecla passa da abertura
                    if self.abertura.t > 20:
                        self.tela_atual = "titulo"
                        som.tocar("confirma")
                    continue
                if ev.key == pygame.K_ESCAPE and self.tela_atual == "luta" and self.partida.fase != "fim":
                    self.pausado = not self.pausado  # ESC na luta = PAUSA (de novo = continua)
                    self.opcao_pausa = 0
                    som.tocar("blip")
                    if not self.pausado and isinstance(self.partida.ctrl[0], Jogador):
                        self.partida.ctrl[0].antes = {"soco": True, "chute": True}
                    continue
                if self.tela_atual == "luta" and self.pausado:
                    self.pausa(ev.key)
                    continue
                if ev.key == pygame.K_ESCAPE and self.tela_atual == "perfil" and getattr(self.tperfil, "album", None):
                    self.tperfil.album = None  # (no ÁLBUM, o ESC volta pro perfil)
                    continue
                if ev.key == pygame.K_ESCAPE:
                    if self.tela_atual == "titulo":
                        self.sair()
                    self.tela_atual = "titulo"
                    som.musica("menu")
                elif self.tela_atual in ("titulo", "escolha", "cor", "cenario"):
                    som.tocar("confirma" if ev.key in (pygame.K_RETURN, pygame.K_SPACE) else "blip")
                if ev.key == pygame.K_ESCAPE:
                    pass
                elif self.tela_atual == "titulo":
                    self.titulo(ev.key)
                elif self.tela_atual == "escolha":
                    self.sel.tecla(ev.key)
                    if self.sel.pronto:
                        self.depois_da_selecao()
                elif self.tela_atual == "cor":
                    self.escolher(ev.key)
                elif self.tela_atual == "loja":
                    self.loja.tecla(ev.key)
                elif self.tela_atual == "codigos":
                    self.tcodigos.tecla(ev)
                elif self.tela_atual == "config":
                    self.tconfig.tecla(ev.key)
                elif self.tela_atual == "perfil":
                    self.tperfil.tecla(ev.key)
                elif self.tela_atual == "passe":
                    self.tpasse.tecla(ev.key)
                elif self.tela_atual == "malucos":
                    self.tmalucos.tecla(ev.key)
                elif self.tela_atual == "torneio" and ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.torneio_enter()
                elif self.tela_atual == "torneio" and ev.key == pygame.K_s:
                    self.torneio_enter(pular=True)
                elif (self.tela_atual == "luta" and getattr(self.partida, "assistindo", False)
                      and self.partida.fase not in ("fim",) and ev.key == pygame.K_RETURN):
                    self.pular_luta_assistida()
                elif self.tela_atual == "cenario":
                    self.tcen.tecla(ev.key)
                    if self.tcen.pronto:
                        self.cenario_nome = self.tcen.escolhido
                        self.ir_pro_vs()
                elif self.tela_atual == "vs":
                    if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.comecar()
                elif self.tela_atual == "luta" and getattr(self.partida, "combos", None) and                         ev.key in (pygame.K_n, pygame.K_b, pygame.K_TAB):  # desafios de combo
                    c = self.partida.combos
                    if ev.key == pygame.K_TAB:
                        c.comecar_demo(self.partida)
                    else:
                        c.trocar(self.partida, 1 if ev.key == pygame.K_n else -1)
                        som.tocar("blip")
                    self.combo_i = c.i
                elif self.tela_atual == "luta" and self.partida.treino and ev.key == pygame.K_h:  # liga/desliga as caixas
                    self.partida.ver_caixas = not getattr(self.partida, "ver_caixas", False)
                    som.tocar("blip")
                elif self.tela_atual == "luta" and ev.key == pygame.K_m:  # o RADINHO: passa pra próxima música
                    som.proxima_musica()
                elif self.tela_atual == "luta" and ev.key == pygame.K_p:  # TESTE: enche a barra da ultimate
                    self.partida.L[0].barra = BARRA_TOTAL if self.partida.L[0].tem_ult2() else BARRA_MAX
                elif self.tela_atual == "luta" and self.partida.treino and pygame.K_1 <= ev.key <= pygame.K_5:
                    self.partida.ctrl[1].modo = BonecoTreino.MODOS[ev.key - pygame.K_1]
                elif (self.tela_atual == "luta" and self.partida.fase in ("entrada", "falas")
                      and ev.key == pygame.K_RETURN):
                    self.partida.pular_entrada()  # pula a entrada (e as falas)
                elif (self.tela_atual == "luta" and self.partida.fase == "fim" and ev.key == pygame.K_RETURN
                      and self.partida.replay_tocando()):
                    self.partida.pular_replay()  # (ENTER no replay só pula o replay)
                elif self.tela_atual == "luta" and self.partida.fase == "fim" and ev.key == pygame.K_RETURN:
                    if self.modo == REI:  # REI DA ARENA: quem ganha fica, quem perde vai pro fim da fila
                        import reiarena
                        self.arena.registrar(self.partida.vencedor)
                        self.tplacar = reiarena.TelaPlacar(self.arena)
                        self.tela_atual = "rei_placar"
                        som.musica("menu")
                    elif self.modo == TORNEIO:  # volta pra chave com o resultado
                        p = self.partida
                        venceu = p.vencedor == 0 or (p.vencedor == "empate" and p.L[0].vida >= p.L[1].vida)
                        if getattr(p, "assistindo", False):  # computadores: a esquerda é a "a" da chave
                            self.torneio.registrar(0 if venceu else 1)
                        else:
                            _, _, eu_esq = self.torneio.fichas_da_luta()
                            self.torneio.registrar((0 if venceu else 1) if eu_esq else (1 if venceu else 0))
                        self.tela_atual = "torneio"
                        som.musica("menu")
                    elif self.modo == SOBREV:
                        if self.partida.vencedor == 0:  # próxima luta, com um pouco de vida de volta
                            eu = self.partida.L[0]
                            self.sobrev["n"] += 1
                            self.sobrev["vida"] = min(eu.vida_max, eu.vida + SOBREV_VOLTA)
                        else:  # caiu: começa outra Sobrevivência do zero
                            self.sobrev = {"n": 0, "vida": None, "ultimo": None}
                        self.sobrev_proxima()
                    elif self.modo == ARCADE and self.partida.vencedor == 0:
                        self.arcade_proxima()
                    else:
                        self.comecar()  # revanche / tentar de novo
                elif self.tela_atual == "quadrinho" and ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.quadrinho.acabou:
                        self.depois_do_quadrinho()
                    else:
                        self.quadrinho.adiantar()
                elif self.tela_atual == "creditos" and ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.tela_atual = "titulo"

            if self.tela_atual == "abertura":
                self.abertura.desenhar(self.tela)
            elif self.tela_atual == "titulo":
                self.desenhar_titulo()
            elif self.tela_atual == "escolha":
                self.sel.desenhar(self.tela)
            elif self.tela_atual == "cor":
                self.desenhar_escolha()
            elif self.tela_atual == "cenario":
                self.tcen.desenhar(self.tela)
            elif self.tela_atual == "loja":
                self.loja.desenhar(self.tela)
            elif self.tela_atual == "codigos":
                self.tcodigos.desenhar(self.tela)
            elif self.tela_atual == "malucos":
                self.tmalucos.desenhar(self.tela)
            elif self.tela_atual == "como":
                self.tcomo.desenhar(self.tela)
            elif self.tela_atual == "passe":
                self.tpasse.desenhar(self.tela)
                if self.tpasse.sair:
                    self.tela_atual = "titulo"
            elif self.tela_atual == "perfil":
                self.tperfil.desenhar(self.tela)
                if self.tperfil.sair:
                    self.tela_atual = "titulo"
            elif self.tela_atual == "config":
                self.tconfig.desenhar(self.tela)
                if self.tconfig.sair:
                    self.tela_atual = "titulo"
            elif self.tela_atual == "torneio":
                self.torneio.desenhar(self.tela)
            elif self.tela_atual == "desafios":
                self.tdesafios.desenhar(self.tela)
            elif self.tela_atual == "quadrinho":
                self.quadrinho.desenhar(self.tela)
            elif self.tela_atual == "creditos":
                self.creditos.desenhar(self.tela)
                if self.creditos.acabou:
                    self.tela_atual = "titulo"
            elif self.tela_atual == "rei_nomes":
                self.tnomes.desenhar(self.tela)
            elif self.tela_atual == "rei_placar":
                self.tplacar.desenhar(self.tela)
            elif self.tela_atual == "foto":
                self.acumulado = 0
                self.tfoto.segurando(pygame.key.get_pressed())
                self.tfoto.desenhar(self.tela)
            elif self.tela_atual == "vs":
                self.vs.desenhar(self.tela)
                if self.vs.acabou:
                    self.comecar()
            elif self.tela_atual == "online":  # ONLINE: anda 60 vezes por segundo (os dois PCs no mesmo ritmo)
                bruto = (pygame.key.get_pressed(), pygame.mouse.get_pressed())
                passos = 0
                dt = 1 / FPS / self.online.velocidade()  # (MODO MALUCO TURBO)
                while self.acumulado >= dt and passos < 4:
                    self.online.tick(bruto)
                    self.acumulado -= dt
                    passos += 1
                if passos == 4:
                    self.acumulado = 0
                try:
                    self.online.desenhar(self.tela)
                except pygame.error:
                    gc.collect()
                if self.online.sair:
                    self.online.voltar_menu()
                    self.tela_atual = "titulo"
                    som.musica("menu")
            elif self.pausado:  # PAUSA: a luta fica congelada atrás do menu
                self.acumulado = 0
                self.partida.desenhar(self.tela)
                self.desenhar_pausa()
            else:
                # a luta anda sempre 60 quadros por segundo; se o desenho atrasar, pula desenho (não fica lento)
                bruto = (pygame.key.get_pressed(), pygame.mouse.get_pressed())
                passos = 0
                dt = 1 / FPS / (1.5 if "turbo" in self.partida.regras else 1)  # MODO MALUCO: TURBO
                while self.acumulado >= dt and passos < 6:
                    self.partida.passo(bruto)
                    self.acumulado -= dt
                    passos += 1
                if passos == 6:
                    self.acumulado = 0
                try:
                    self.partida.desenhar(self.tela)
                    if self.modo == REI and self.partida.fase not in ("fim",):  # a coroa em cima do REI
                        import reiarena
                        rei = self.partida.L[0]
                        reiarena.desenhar_coroa(self.tela, int(rei.x), int(rei.y - 150 * rei.s), self.partida.t_total, 0.8)
                except pygame.error:  # faltou memória num quadro: pula esse desenho e segue a luta
                    gc.collect()
            pygame.display.flip()
            self.acumulado += self.relogio.tick(FPS) / 1000


def pasta_do_jogo():
    """A pasta onde está o .exe (ou este arquivo, rodando pelo Python)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    try:
        jogo = Jogo()
        if "--robo-online" not in sys.argv:  # a abertura da FROGBIT STUDIO (qualquer tecla pula)
            import frogbit_abertura
            if not frogbit_abertura.tocar(jogo.tela):
                pygame.quit(); sys.exit()
        if "--robo-online" in sys.argv:  # o "robô da MARIA": cria uma sala e luta sozinho (pra testar o online)
            from online import Online
            pygame.display.set_caption("Battle Wish (robô da MARIA)")
            jogo.online = Online(robo=True, arquivo_codigo=os.path.join(save.pasta_do_jogo(), "sala_robo.txt"))
            jogo.tela_atual = "online"
        jogo.rodar()
    except SystemExit:
        raise
    except Exception:  # qualquer erro: salva o que aconteceu num erro.txt do lado do jogo
        import datetime
        import traceback
        with open(os.path.join(pasta_do_jogo(), "erro.txt"), "a", encoding="utf-8") as arq:
            arq.write(f"\n===== {datetime.datetime.now():%d/%m/%Y %H:%M:%S} =====\n")
            traceback.print_exc(file=arq)
        raise
