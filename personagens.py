"""Os lutadores.

Os bonecos de treino são provisórios. "golpes" diz qual golpe sai em cada botão (M3 + E/Q/R/SHIFT/Z).
Quem não tem "golpes" usa os golpes dos bonecos de treino.
"""
from corpo import desenhar_manequim
from max10 import GOLPES_MAX10, desenhar_robo
from max10 import entrada as entrada_max
from max10 import entrada_efeito as entrada_efeito_max
from max10 import figura_extra as figura_max
from max10 import vitoria as vitoria_max
from max10 import vitoria_efeito as vitoria_efeito_max
from rib import GOLPES_RIB, POSES_RIB, desenhar_rib, rib_todo_quadro
from rib import entrada as entrada_rib
from rib import entrada_efeito as entrada_efeito_rib
from rib import figura_extra as figura_rib
from rib import vitoria as vitoria_rib
from rib import vitoria_efeito as vitoria_efeito_rib
from trafo import GOLPES_TRAFO, POSES_TRAFO, desenhar_trafo, trafo_todo_quadro
from king import GOLPES_KING, POSES_KING, desenhar_king
from king import entrada as entrada_king
from king import entrada_efeito as entrada_efeito_king
from king import figura_extra as figura_king
from king import vitoria as vitoria_king
from cannan import GOLPES_CANNAN, POSES_CANNAN, desenhar_cannan, cansado_efeito
from cannan import entrada as entrada_cannan
from finn import GOLPES_FINN, POSES_FINN, desenhar_finn, finn_todo_quadro
from kun import GOLPES_KUN, POSES_KUN, desenhar_kun
import xeno
import tai
import tamer
import john
import craquen
import magnus
import sphyrus
import frigantus
import inazumaneko
import nocturnus
import silvanus
import katchade
from kun import entrada as entrada_kun
from kun import entrada_efeito as entrada_efeito_kun
from kun import figura_extra as figura_kun
from kun import vitoria as vitoria_kun
from kun import vitoria_efeito as vitoria_efeito_kun
from finn import entrada as entrada_finn
from finn import entrada_efeito as entrada_efeito_finn
from finn import figura_extra as figura_finn
from finn import vitoria as vitoria_finn
from cannan import entrada_efeito as entrada_efeito_cannan
from cannan import figura_extra as figura_cannan
from cannan import vitoria as vitoria_cannan
from trafo import entrada as entrada_trafo
from trafo import entrada_efeito as entrada_efeito_trafo
from trafo import figura_extra as figura_trafo
from trafo import vitoria as vitoria_trafo
from trafo import vitoria_efeito as vitoria_efeito_trafo

NOMES_PALITO = {"E": "bola", "Q": "subida", "R": "giro", "SHIFT": "avanço", "Z": "BOLA GIGANTE"}

# O BONECO DE TREINO: não é lutador da lista; é o parceiro do MODO TREINO (dá pra escolher a cor).
CORES_BONECO = [("AZUL", (70, 130, 220), (120, 200, 255)), ("VERMELHO", (210, 70, 60), (255, 150, 90)),
                ("VERDE", (70, 170, 90), (150, 240, 160)), ("AMARELO", (220, 190, 60), (255, 230, 120)),
                ("ROXO", (140, 90, 200), (210, 160, 255)), ("BRANCO", (225, 225, 230), (255, 255, 255))]
BONECO = dict(nome="BONECO DE TREINO", cor=CORES_BONECO[0][1], vida=100, vel=3.8, pulo=16.5, forca=1.0, tam=1.35,
              desenho=desenhar_manequim, cor_poder=CORES_BONECO[0][2], nomes=NOMES_PALITO, cenario="TEMPLO")


def sombra(ficha):
    """O chefão do Arcade: a SOMBRA do lutador (mesmos golpes, escura, um pouco mais forte)."""
    return dict(ficha, nome="SOMBRA DO " + ficha["nome"], sombra=True, vida=120, forca=1.15, cenario="TEMPLO",
                cor_poder=(170, 120, 255))


def boneco(i):
    """O boneco de treino na cor i."""
    _, cor, poder = CORES_BONECO[i % len(CORES_BONECO)]
    return dict(BONECO, cor=cor, cor_poder=poder)


PERSONAGENS = [
    dict(nome="MAX-10", cor=(200, 164, 86), vida=100, vel=3.4, pulo=16, forca=0.92, tam=1.42,
         cor_poder=(255, 50, 40), desenho=desenhar_robo, golpes=GOLPES_MAX10, figura_extra=figura_max, provocacao="ERRO 404: DESAFIO NÃO ENCONTRADO.", cenario="FERRO-VELHO", habilidade="maquinario",
         entrada=entrada_max, entrada_efeito=entrada_efeito_max, vitoria=vitoria_max,
         vitoria_efeito=vitoria_efeito_max,
         nomes={"E": "laser dos olhos", "Q": "agarrão (joga pra cima)", "R": "metralhadora de socos", "SHIFT": "voozinho",
                "Z": "RASANTE"}),
    dict(nome="RIB", cor=(100, 174, 66), vida=100, vel=4.3, pulo=18, forca=0.6, tam=1.34, altura=0.84,
         cor_poder=(150, 220, 255), desenho=desenhar_rib, golpes=GOLPES_RIB, poses=POSES_RIB,
         todo_quadro=rib_todo_quadro, provocacao="Tá lento, hein?",
         provocacao_quadros=[(0, "parado"), (8, "r_cruzado"), (58, "r_cruzado"), (70, "parado")], figura_extra=figura_rib, cenario="PÂNTANO", habilidade="ninja", entrada=entrada_rib, entrada_efeito=entrada_efeito_rib,
         vitoria=vitoria_rib, vitoria_efeito=vitoria_efeito_rib,
         nomes={"E": "shuriken", "Q": "rasteira + chute pra cima", "R": "corrida ninja", "SHIFT": "LINGUADA",
                "Z": "KAGE BUNSHIN"}),
    dict(nome="TRAFO", cor=(190, 152, 52), vida=100, vel=3.6, pulo=15.5, forca=0.75, tam=1.32, altura=0.9,
         cor_poder=(196, 36, 28), desenho=desenhar_trafo, golpes=GOLPES_TRAFO, poses=POSES_TRAFO,
         figura_extra=figura_trafo, provocacao="AUUUUUU!",
         provocacao_quadros=[(0, "parado"), (8, "t_agacha"), (16, "t_uivo"), (58, "t_uivo"), (70, "parado")], cenario="TOCA", habilidade="conexao",
         habilidades_opcoes=("conexao", "adaptacao"), todo_quadro=trafo_todo_quadro,  # (H troca na seleção)
         entrada=entrada_trafo, entrada_efeito=entrada_efeito_trafo,
         vitoria=vitoria_trafo, vitoria_efeito=vitoria_efeito_trafo,
         nomes={"E": "linguão (paralisa)", "Q": "braços da terra", "R": "metralhadora de olhos", "SHIFT": "pulão",
                "Z": "TRANSFORMAÇÃO"}),
    dict(nome="KING RIP", cor=(62, 98, 182), vida=100, vel=3.7, pulo=16.5, forca=0.9, tam=1.36,
         cor_poder=(200, 220, 255), desenho=desenhar_king, golpes=GOLPES_KING, poses=POSES_KING,
         figura_extra=figura_king, provocacao="Na minha época, eu já tinha vencido.",
         provocacao_quadros=[(0, "parado"), (10, "k_gira"), (30, "k_bastao"), (58, "k_bastao"), (70, "parado")], cenario="DOJO", habilidade="maestria", entrada=entrada_king,
         entrada_efeito=entrada_efeito_king, vitoria=vitoria_king,
         nomes={"E": "nunchaku bumerangue", "Q": "chute acrobático", "R": "nunchaku giratório",
                "SHIFT": "salto com nunchaku", "Z": "MESTRE DO NUNCHAKU"}),
    dict(nome="CANNAN", cor=(96, 104, 60), vida=100, vel=3.6, pulo=15.5, forca=0.67, tam=1.38,
         cor_poder=(130, 220, 255), desenho=desenhar_cannan, golpes=GOLPES_CANNAN, poses=POSES_CANNAN,
         figura_extra=figura_cannan, provocacao="Isso é tudo, recruta?",
         provocacao_quadros=[(0, "parado"), (8, "c_continencia"), (58, "c_continencia"), (70, "parado")], cenario="CAMPO DE BATALHA", habilidade="colete", entrada=entrada_cannan,
         entrada_efeito=entrada_efeito_cannan, vitoria=vitoria_cannan, cansado_efeito=cansado_efeito,
         nomes={"E": "pistola (3 tiros)", "Q": "coronhada + soco pra cima", "R": "canhão de perto",
                "SHIFT": "corrida maluca", "Z": "FOGO TOTAL (segura o Z pra carregar)"}),
    dict(nome="FINN", cor=(104, 58, 150), vida=100, vel=3.5, pulo=15.5, forca=1.3, tam=1.36,
         cor_poder=(190, 120, 255), desenho=desenhar_finn, golpes=GOLPES_FINN, poses=POSES_FINN,
         figura_extra=figura_finn, provocacao="Magia de verdade, aprendiz!",
         provocacao_quadros=[(0, "parado"), (8, "f_vitoria"), (58, "f_vitoria"), (70, "parado")],
         cenario="TORRE DO MAGO", habilidade="alquimia", habilidades_opcoes=("alquimia", "cura"),
         todo_quadro=finn_todo_quadro, entrada=entrada_finn, entrada_efeito=entrada_efeito_finn, vitoria=vitoria_finn,
         nomes={"E": "bola de fogo", "Q": "levitação (joga pra cima)", "R": "cajado amarelo (barrage)",
                "SHIFT": "empurrão mágico", "Z": "MINI SOL"}),
    dict(nome="KUN", cor=(176, 44, 42), vida=100, vel=3.9, pulo=16.5, forca=1.18, tam=1.34,
         cor_poder=(255, 220, 140), desenho=desenhar_kun, golpes=GOLPES_KUN, poses=POSES_KUN,
         figura_extra=figura_kun, provocacao="Escolha uma carta... qualquer carta.",
         provocacao_quadros=[(0, "parado"), (8, "k_vitoria"), (58, "k_vitoria"), (70, "parado")],
         cenario="CASSINO", habilidade="as_na_manga", entrada=entrada_kun, entrada_efeito=entrada_efeito_kun, vitoria=vitoria_kun,
         vitoria_efeito=vitoria_efeito_kun,
         nomes={"E": "carta", "Q": "shoryuken de carta (joga pra cima)", "R": "carta-espada",
                "SHIFT": "teleporte da carta", "Z": "CARTA DOS MÓVEIS"}),
    dict(nome="TROMOS", nome_completo="TROMOSTOU ERGATITIRIOU", cor=(40, 42, 52), vida=100, vel=4.2, pulo=17, forca=1.03, tam=1.4, altura=0.85,
         cor_poder=(255, 210, 40), desenho=xeno.desenhar_xeno, golpes=xeno.GOLPES_XENO, poses=xeno.POSES_XENO,
         figura_extra=xeno.figura_extra, todo_quadro=xeno.todo_quadro, desenhar_sempre=xeno.desenhar_pocas,
         provocacao="Hssssssss...",
         provocacao_quadros=[(0, "parado"), (8, "x_vitoria"), (58, "x_vitoria"), (70, "parado")],
         cenario="LABORATÓRIO", habilidade="emboscada", habilidades_opcoes=("emboscada", "regeneracao"),
         entrada=xeno.entrada, entrada_efeito=xeno.entrada_efeito,
         vitoria=xeno.vitoria,
         nomes={"E": "cuspe de ácido", "Q": "rabada (joga pra cima)", "R": "garras", "SHIFT": "rasteja",
                "Z": "SEGUNDA BOCA (morde e se cura)"}),
    dict(nome="TAI", cor=(236, 190, 150), vida=120, vel=2.9, pulo=14.5, forca=1.33, tam=1.5,
         cor_poder=(255, 230, 160), desenho=tai.desenhar_tai, golpes=tai.GOLPES_TAI, poses=tai.POSES_TAI,
         figura_extra=tai.figura_extra, provocacao="HAKKEYOI!",
         provocacao_quadros=[(0, "parado"), (10, "t_shiko"), (50, "t_shiko"), (56, "t_pisao"), (70, "parado")],
         cenario="ARENA DE SUMÔ", habilidade="furia_sumo", entrada=tai.entrada, vitoria=tai.vitoria,
         nomes={"E": "pisão (onda no chão)", "Q": "agarra e arremessa", "R": "tapas de sumô",
                "SHIFT": "investida", "Z": "YOKOZUNA"}),
    dict(nome="TAMER", cor=(176, 152, 100), vida=100, vel=3.8, pulo=16.5, forca=0.82, tam=1.36,
         cor_poder=(200, 220, 255), desenho=tamer.desenhar_tamer, golpes=tamer.GOLPES_TAMER, poses=tamer.POSES_TAMER,
         figura_extra=tamer.figura_extra, todo_quadro=tamer.todo_quadro, desenhar_sempre=tamer.lobo_flash,
         tecla_x=tamer.trocar_lobo, tela_toda=True, provocacao="Bom garoto!",
         provocacao_quadros=[(0, "parado"), (8, "t_carinho"), (58, "t_carinho"), (70, "parado")],
         cenario="SELVA", habilidade="entendimento", entrada=tamer.entrada, vitoria=tamer.vitoria,
         nomes={"E": "o lobo avança", "Q": "chute na parede (sobe)", "R": "combo com o lobo",
                "SHIFT": "galope no lobo", "Z": "A ALCATEIA"}),
    dict(nome="JOHN", cor=(70, 50, 110), vida=100, vel=4.0, pulo=17, forca=0.8, tam=1.36,
         cor_poder=(170, 90, 230), desenho=john.desenhar_john, golpes=john.GOLPES_JOHN, poses=john.POSES_JOHN,
         figura_extra=john.figura_extra, todo_quadro=john.todo_quadro,
         provocacao="Para o meu próximo truque... você vai sumir!",
         provocacao_quadros=[(0, "parado"), (8, "j_tira"), (58, "j_tira"), (70, "parado")],
         cenario="TEATRO DE MÁGICA", habilidade="cartas", habilidades_opcoes=("cartas", "coelho"),
         entrada=john.entrada, entrada_efeito=john.entrada_efeito,
         vitoria=john.vitoria, vitoria_efeito=john.vitoria_efeito,
         nomes={"E": "cartola de lâminas", "Q": "agradece + teleporta + bicuda", "R": "boca de crocodilo",
                "SHIFT": "coelho gigante", "Z": "OS DANÇARINOS"}),
    dict(nome="CRÁQUEN", cor=(60, 130, 140), vida=100, vel=3.9, pulo=16.5, forca=0.8, tam=1.38,
         cor_poder=(170, 230, 220), desenho=craquen.desenhar_craquen, golpes=craquen.GOLPES_CRAQUEN,
         poses=craquen.POSES_CRAQUEN, figura_extra=craquen.figura_extra, todo_quadro=craquen.todo_quadro,
         desenhar_sempre=craquen.desenhar_sempre, fantasma=True,
         provocacao="Arrr! Vai pra prancha, marujo!",
         provocacao_quadros=[(0, "parado"), (8, "q_ri"), (58, "q_ri"), (70, "parado")],
         cenario="NAVIO FANTASMA", habilidade="intangivel", entrada=craquen.entrada,
         entrada_efeito=craquen.entrada_efeito, vitoria=craquen.vitoria, vitoria_efeito=craquen.vitoria_efeito,
         nomes={"E": "âncora (puxa pra perto)", "Q": "tentáculo (joga pra cima)", "R": "espada fantasma",
                "SHIFT": "atravessa + susto", "Z": "O NAVIO FANTASMA"}),
    dict(nome="MAGNUS", cor=(78, 82, 92), vida=70, vel=4.3, pulo=17, forca=1.05, tam=1.4, altura=0.62,
         cor_poder=(255, 130, 40), desenho=magnus.desenhar_magnus, golpes=magnus.GOLPES_MAGNUS,
         poses=magnus.POSES_MAGNUS, figura_extra=magnus.figura_extra, todo_quadro=magnus.todo_quadro,
         provocacao="*RRAAWR!*",
         provocacao_quadros=[(0, "parado"), (8, "m_ruge"), (58, "m_ruge"), (70, "parado")],
         cenario="CERCADO DO DESERTO", habilidade="corpo_agil", entrada=magnus.entrada, entrada_efeito=magnus.entrada_efeito,
         vitoria=magnus.vitoria, vitoria_efeito=magnus.vitoria_efeito,
         nomes={"E": "espinhos da nuca (prende)", "Q": "duas rabadas", "R": "o bote (garradas)",
                "SHIFT": "corrida + rabada de fogo (paralisa)", "Z": "BOLAS DE FOGO + RABADA DE FOGO"}),
    dict(nome="SPHYRUS", cor=(96, 106, 122), vida=80, vel=4.1, pulo=17, forca=1.18, tam=1.38,
         cor_poder=(80, 200, 255), desenho=sphyrus.desenhar_sphyrus, golpes=sphyrus.GOLPES_SPHYRUS,
         poses=sphyrus.POSES_SPHYRUS, figura_extra=sphyrus.figura_extra, todo_quadro=sphyrus.todo_quadro,
         tecla_x=sphyrus.tecla_x, provocacao="*GROOOAR!*",
         provocacao_quadros=[(0, "parado"), (8, "s_ruge"), (58, "s_ruge"), (70, "parado")],
         cenario="PRAIA DA ILHA", habilidade="natacao", habilidades_opcoes=("natacao", "eletro", "frenesi"),
         entrada=sphyrus.entrada, vitoria=sphyrus.vitoria, vitoria_efeito=sphyrus.vitoria_efeito,
         nomes={"E": "onda de ar (cauda)", "Q": "martelada (joga pra cima)", "R": "corte de barbatana em X",
                "SHIFT": "mergulho (sai mordendo embaixo)", "Z": "O MAR (salto gigante)"}),
    dict(nome="FRIGANTUS", cor=(236, 240, 248), vida=120, vel=3.0, pulo=14.5, forca=0.8, tam=1.5,
         cor_poder=(180, 230, 255), desenho=frigantus.desenhar_frigantus, golpes=frigantus.GOLPES_FRIGANTUS,
         poses=frigantus.POSES_FRIGANTUS, figura_extra=frigantus.figura_extra, todo_quadro=frigantus.todo_quadro,
         provocacao="*UH-UH-UH!*", provocacao_quadros=frigantus.PROVOCA_QUADROS,
         cenario="MONTANHA NEVADA", habilidade="nevasca", entrada=frigantus.entrada,
         entrada_efeito=frigantus.entrada_efeito, vitoria=frigantus.vitoria, vitoria_efeito=frigantus.vitoria_efeito,
         nomes={"E": "bola de neve (congela)", "Q": "pisão + estacas de gelo (joga pra cima)",
                "R": "bloco de gelo: 8 estacas na cabeça", "SHIFT": "escorregão de barriga",
                "Z": "AVALANCHE", "Z2": "ERA DO GELO"}),
    dict(nome="INAZUMANEKO", cor=(242, 242, 238), vida=100, vel=3.9, pulo=16.5, forca=0.84, tam=1.38,
         cor_poder=(170, 220, 255), desenho=inazumaneko.desenhar_inazumaneko, golpes=inazumaneko.GOLPES_INAZUMANEKO,
         poses=inazumaneko.POSES_INAZUMANEKO, figura_extra=inazumaneko.figura_extra, todo_quadro=inazumaneko.todo_quadro,
         provocacao="O VENTO CORTA.",
         provocacao_quadros=[(0, "parado"), (8, "i_equilibra"), (58, "i_equilibra"), (68, "parado")],
         cenario="MONTE KARASUMA", habilidade="furia_samurai", habilidades_opcoes=("furia_samurai", "poder_samurai"),
         retrato_zoom=0.62, retrato_dy=14,
         entrada=inazumaneko.entrada, entrada_efeito=inazumaneko.entrada_efeito, vitoria=inazumaneko.vitoria,
         vitoria_efeito=inazumaneko.vitoria_efeito, nomes=dict(inazumaneko.NOMES)),
    dict(nome="NOCTURNUS", cor=(38, 28, 50), vida=100, vel=3.8, pulo=16.5, forca=0.75, barra_mult=0.5, tam=1.38,
         cor_poder=(150, 210, 255), desenho=nocturnus.desenhar_nocturnus, golpes=nocturnus.GOLPES_NOCTURNUS,
         poses=nocturnus.POSES_NOCTURNUS, todo_quadro=nocturnus.todo_quadro, tecla_x=nocturnus.tecla_x,
         desenhar_sempre=nocturnus.desenhar_sempre, efeito_tela=nocturnus.efeito_tela,
         entrada=nocturnus.entrada, entrada_efeito=nocturnus.entrada_efeito,
         vitoria=nocturnus.vitoria, vitoria_efeito=nocturnus.vitoria_efeito, nomes=dict(nocturnus.NOMES),
         habilidade="eco", habilidades_opcoes=("eco", "planar", "senso"), provocacao="*IIIIII!*",
         provocacao_quadros=[(0, "parado"), (8, "n_grito"), (30, "n_grito"), (36, "n_ri"), (60, "n_ri"), (68, "parado")],
         cenario="CAVERNA DOS MORCEGOS"),
    dict(nome="SILVANUS", cor=(72, 150, 60), vida=100, vel=3.6, pulo=16.0, forca=0.8, barra_mult=0.7, tam=1.36,
         cor_poder=(214, 255, 120),
         desenho=silvanus.desenhar_silvanus, golpes=silvanus.GOLPES_SILVANUS, poses=silvanus.POSES_SILVANUS,
         todo_quadro=silvanus.todo_quadro, tecla_x=silvanus.tecla_x, desenhar_sempre=silvanus.desenhar_sempre,
         entrada=silvanus.entrada, entrada_efeito=silvanus.entrada_efeito,
         vitoria=silvanus.vitoria, vitoria_efeito=silvanus.vitoria_efeito, vitoria_atras=silvanus.vitoria_atras,
         provocacao_quadros=silvanus.PROVOCACAO_QUADROS, nomes=dict(silvanus.NOMES),
         habilidade="jardim", habilidades_opcoes=("jardim", "enganador", "vantagem"), cenario="FLORESTA ANTIGA"),
    # (v4.0) o 19º: KATCHADE, o louva-a-deus-orquídea (paciência e contra-ataque)
    dict(nome="KATCHADE", cor=(246, 166, 202), vida=95, vel=4.0, pulo=16.5, forca=0.85, tam=1.3,
         cor_poder=(255, 190, 230), desenho=katchade.desenhar_katchade, golpes=katchade.GOLPES_KATCHADE,
         poses=katchade.POSES_KATCHADE, todo_quadro=katchade.todo_quadro, desenhar_sempre=katchade.desenhar_sempre,
         provocacao="...", provocacao_quadros=katchade.PROVOCACAO_QUADROS, nomes=dict(katchade.NOMES),
         habilidade="camuflagem", habilidades_opcoes=("camuflagem", "foices_afiadas"), cenario="CAMPO GIGANTE",
         retrato_zoom=0.62, retrato_dy=14, entrada=katchade.entrada, entrada_efeito=katchade.entrada_efeito,
         vitoria=katchade.vitoria),
]


import ult2  # noqa: E402
ult2._registra("inaz_ult2", inazumaneko.mil_cortes, inazumaneko.mil_cortes_efeito, [(0, "parado")])  # (MIL CORTES)
ult2._registra("noct_ult2", nocturnus.cancao, nocturnus.cancao_efeito, [(0, "parado")])  # (CANÇÃO DE NINAR)
ult2._registra("silv_ult2", silvanus.chuva, silvanus.chuva_efeito, [(0, "parado")])  # (CHUVA DE SEMENTES)
ult2._registra("katch_ult2", katchade.corte_vertical, katchade.corte_vertical_efeito, [(0, "parado")])  # (CORTE VERTICAL)
ult2.ligar(PERSONAGENS)  # as 2ª ULTIMATES (botão "Z2")
import provocacoes_loja  # noqa: E402,F401  (as provocações da LOJA)
import vitorias_loja  # noqa: E402,F401  (as poses de vitória da LOJA)
import entradas_loja  # noqa: E402,F401  (as entradas da LOJA)
import provocacoes_halloween  # noqa: E402,F401  (as provocações de HALLOWEEN, do passe)

# ---- personagens SECRETOS (aparecem na seleção depois do código; nunca no online) ----
from ribbat_lutador import RIBBAT  # noqa: E402

SECRETOS = [RIBBAT]


# ENTRADA (v2.0): a pose em que cada um espera pra falar (o Rib faz o selo de mão, o Tai joga o sal...)
ESPERA = {'MAX-10': 'vitoria', 'RIB': 'r_selo', 'TRAFO': 't_agacha', 'KING RIP': 'k_bastao', 'CANNAN': 'c_continencia', 'FINN': 'f_carrega', 'KUN': 'k_brinca', 'TROMOS': 'x_vitoria', 'TAI': 't_sal', 'TAMER': 't_carinho', 'JOHN': 'j_agradece', 'CRÁQUEN': 'q_espera', 'MAGNUS': 'm_fareja', 'SPHYRUS': 's_ruge', 'FRIGANTUS': 'fr_peito_a', 'INAZUMANEKO': 'i_curva', 'NOCTURNUS': 'n_ri', 'SILVANUS': 's_ergue', 'KATCHADE': 'k_reza'}
for _f in PERSONAGENS:
    _f.setdefault("espera", ESPERA.get(_f["nome"], "vitoria"))
for _f in SECRETOS:
    _f.setdefault("espera", "r_cruzado")


def disponiveis():
    """Os lutadores que dá pra escolher agora (os normais + os secretos já desbloqueados)."""
    import codigos
    return PERSONAGENS + [f for f in SECRETOS if codigos.ativo(f["codigo"])]


# (MODO MALUCO "CABEÇÕES": marca as peças de cabeça de cada um)
import cannan as _cannan, finn as _finn, kun as _kun, king as _king, max10 as _max10  # noqa: E401,E402
import rib as _rib, trafo as _trafo  # noqa: E401,E402
for _m in (_max10, _rib, _trafo, _king, _cannan, _finn, _kun, xeno, tai, tamer, john, craquen, magnus, sphyrus, frigantus):
    for _nome in ("CABECA", "CABECA_COSTAS"):
        if hasattr(_m, _nome):
            getattr(_m, _nome).cabeca = True
