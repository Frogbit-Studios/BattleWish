"""Números do jogo de luta. Mexer aqui muda o jogo inteiro."""
import pygame

LARGURA, ALTURA = 960, 540
FPS = 60

CHAO = 482                  # altura do chão (onde ficam os pés)
PAREDE_E, PAREDE_D = 50, 910
GRAVIDADE = 0.85            # tudo aqui é "por quadro" (60 quadros = 1 segundo)
CORPO = 26                  # meia-largura do corpo (os dois não se atravessam)

TEMPO_ROUND = 99            # segundos
ROUNDS_PRA_VENCER = 2
# PIXEL ART: tamanho de cada "pixel" do desenho, em pixels da tela.
# 1 = sem pixel art, 2 = pixel art com bastante detalhe (tipo SF2), 4, 6, 10 = cada vez mais quadradão
PIXEL = 3
EFEITOS_DUROS = True  # (v3.0, pedido do Gomes: os EFEITOS também em pixel art de verdade, com borda dura)

PARADA_GOLPE = 7
DURACAO_ENTRADA = 110       # quadros da entrada dos personagens (começo da luta)            # quadros que a tela "congela" quando um golpe acerta (dá peso)

# ---- controles ----
# Andar: W pula, S agacha, A/D anda.
# Mouse: botão 1 = esquerdo, 2 = rodinha, 3 = direito.
MOUSE_SOCO, MOUSE_ARMAR, MOUSE_CHUTE = 1, 2, 3
# Segurando a rodinha (M3), ou até JANELA_M3 quadros depois de soltar, essas teclas soltam o especial:
# (o golpe de cada botão depende do personagem, veja personagens.py)
ESPECIAIS = {pygame.K_e: "E", pygame.K_q: "Q", pygame.K_r: "R", pygame.K_LSHIFT: "SHIFT", pygame.K_RSHIFT: "SHIFT"}
ULTIMATE = pygame.K_z
ULTIMATE2 = pygame.K_c     # M3 + C = 2ª ULTIMATE (com a barra AMARELA cheia)
JANELA_M3 = 12              # 0,2 segundo depois de soltar a rodinha (pedido do Gomes)
DUPLO_M3 = 15               # TOQUE E SEGURA a rodinha (clique duplo) em até 0,25 s = EX (e, apanhando, ESCAPE)

# ---- guarda (defesa) ----
GUARDA_MAX = 100
GUARDA_POR_GOLPE = 12       # cada golpe defendido gasta isso...
GUARDA_POR_DANO = 2         # ...mais 2 por ponto de dano do golpe (soco = 22, uns 5 socos quebram)
GUARDA_VOLTA_DEPOIS = 50    # quadros sem defender pra guarda começar a voltar
GUARDA_VOLTA = 0.6          # quanto volta por quadro
TONTO_TEMPO = 60            # guarda quebrada: 1 segundo tonto

DEFESA_DANO = 0.2           # defender um golpe normal ainda tira 20% do dano
DEFESA_DANO_ESPECIAL = 0.25 # ...e um especial, 25%

# ---- parry: tocar pra FRENTE (ou pra BAIXO, contra golpe baixo) bem na hora ----
ROLA_JANELA = 3             # ROLAMENTO: M1 e M2 com até 3 quadros de diferença = rola
ROLA_TEMPO = 24             # quadros rolando
ROLA_INV = 14               # quadros invencível no começo do rolamento
ROLA_VEL = 8.5
ROLA_ESPERA = 30            # depois de rolar, espera isso pra rolar de novo
ESQ_JANELA = 8              # ESQUIVA PERFEITA (v3.0): rolou e o golpe ia pegar nesses primeiros quadros do rolamento...
ESQ_LENTO = 60              # ...o OPONENTE fica em câmera lenta (metade da velocidade) por 1 s; quem esquivou não
PARRY_JANELA = 8            # quadros que o parry fica ligado depois do toque
PARRY_TRAVA = 22            # errou o tempo: espera isso pra poder tentar de novo
PARRY_PARADA = 16           # quadros que tudo congela quando dá parry

# ---- combos ----
PULO_PERSEGUE = 20          # pulo atrás de quem foi jogado pra cima (aperta CIMA depois do Q acertar)
BUFFER_BOTAO = 8            # soco/chute apertado até 8 quadros antes ainda vale

# ---- barra do ultimate ----
BARRA_MAX = 1000           # a parte AZUL (1ª ultimate)
BARRA_AMARELA = 500        # a parte AMARELA (metade do tamanho): cheia = 2ª ULTIMATE
BARRA_TOTAL = BARRA_MAX + BARRA_AMARELA
BONUS_COMBO = 100          # (só com a azul cheia) combo de 5+ golpes enche a amarela
BONUS_CHOQUE = 120         # ...vencer um choque
BONUS_OBJETO = 80          # ...usar o objeto do cenário
BARRA_BATER = 16            # quanto enche por ponto de dano que você dá
BARRA_APANHAR = 10          # quanto enche por ponto de dano que você leva
ULT2_PAUSA = 84             # 2ª ULTIMATE: a apresentação (faixa dourada com o nome) fica mais tempo
ULTIMATE_PAUSA = 36         # quadros com a tela escura antes do ultimate sair

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AMARELO = (255, 214, 60)

# ---- moedas (pra comprar roupas na LOJA) ----
MOEDAS_VITORIA = 10
MOEDAS_PERFECT = 15        # por round vencido sem perder vida
MOEDAS_QUASE = 8           # QUASE PERFECT: venceu o round com 75% de vida ou mais
QUASE_VIDA = 0.75
MOEDAS_VIDA = 10           # +1 moeda pra cada 10 de vida que sobrou no fim da luta
MOEDAS_COMBO = 20          # fez o combo máximo
COMBO_MAXIMO = 12          # golpes (a Maestria do King Rip aumenta pra 18)
INVISIVEL_TEMPO = 180      # PODER MÁGICO do Finn: 3 segundos invisível depois do combo máximo
MOEDAS_ARCADE = 100        # terminou o Arcade
MOEDAS_RECORDE = 30        # recorde novo na Sobrevivência
MOEDAS_MULT = {"FÁCIL": 0.5, "MÉDIO": 1, "DIFÍCIL": 2}

# ---- provocação (tecla T) ----
PROVOCA = pygame.K_t
PROVOCA_TEMPO = 70         # quadros parado provocando
PROVOCA_BARRA = 120        # quanto enche da barra da ultimate (de 1000) se não apanhar

# ---- online ----
VERSAO = "4.0"      # os dois PCs precisam da mesma versão (o online confere)

# ---- botão de BARRA (F no teclado, LT no controle) ----
BARRA_TECLA = pygame.K_f
EX_CUSTO = 250             # segurar F + especial = especial EX (mais forte), gasta 1/4 da barra
EX_DANO = 1.5
ESCAPE_CUSTO = 500         # tocar F apanhando = ESCAPE de combo, gasta 1/2 da barra
ESCAPE_INV = 24            # quadros invulnerável depois do escape
TROCA_TECLA = pygame.K_g   # TRIO: troca de lutador (R3 no controle)
