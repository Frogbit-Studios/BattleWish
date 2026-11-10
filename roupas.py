"""Roupas alternativas (compradas com as moedas do jogo).
Cada roupa troca cores da paleta do personagem: {letra da paleta: cor nova}.
Roupa com codigo="..." não se compra: só aparece com o código certo na tela de CÓDIGOS."""
import chapeus_ribbat
import save

ROUPAS = {
    "MAX-10": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="prata", nome="PRATA", preco=100, cor=(170, 174, 184), troca={
            "G": (236, 238, 244), "g": (184, 188, 198), "d": (126, 130, 142), "D": (78, 82, 94), "r": (60, 200, 255),
            "R": (200, 240, 255)}),
        dict(id="carmesim", nome="CARMESIM", preco=200, cor=(170, 40, 40), troca={
            "G": (236, 110, 100), "g": (190, 54, 50), "d": (130, 30, 32), "D": (80, 16, 20), "S": (60, 60, 66),
            "s": (40, 40, 46), "m": (24, 24, 28), "r": (255, 220, 60), "R": (255, 250, 200)}),
        dict(id="wartank", nome="WARTANK", preco=0, codigo="IRONMAN", cor=(200, 40, 36), troca={
            "G": (232, 64, 52), "g": (186, 34, 32), "d": (134, 20, 22), "D": (86, 10, 14),
            "S": (252, 216, 96), "s": (214, 168, 52), "m": (150, 108, 30),
            "r": (190, 246, 255), "R": (255, 255, 255), "w": (150, 236, 255), "b": (110, 220, 255),
            "y": (220, 250, 255)}),
    ],
    "RIB": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="venenoso", nome="SAPO VENENOSO", preco=100, cor=(40, 120, 220), troca={
            "G": (120, 200, 255), "g": (40, 130, 230), "d": (24, 80, 170), "D": (14, 44, 110), "c": (40, 40, 50),
            "C": (24, 24, 32), "y": (255, 120, 40), "Y": (255, 220, 170)}),
        dict(id="deserto", nome="SAPO DO DESERTO", preco=200, cor=(210, 140, 60), troca={
            "G": (250, 206, 130), "g": (214, 150, 70), "d": (160, 100, 44), "D": (104, 62, 26), "n": (110, 60, 40),
            "N": (150, 92, 60), "x": (210, 190, 150), "X": (240, 226, 190)}),
        dict(id="greninja", nome="NINJA DAS ÁGUAS", preco=0, codigo="FIGHTMON", cor=(40, 70, 170), troca={
            "G": (96, 150, 232), "g": (52, 100, 196), "d": (30, 64, 146), "D": (18, 38, 96),
            "c": (196, 232, 250), "C": (140, 190, 226), "n": (28, 36, 86), "N": (48, 62, 128),
            "x": (236, 96, 160), "X": (255, 170, 210), "s": (52, 76, 150), "m": (26, 40, 92),
            "b": (52, 76, 150), "B": (30, 46, 104), "t": (24, 30, 70)}),
    ],
    "TRAFO": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="lobo", nome="LOBO CINZA", preco=100, cor=(140, 140, 150), troca={
            "G": (210, 212, 220), "g": (150, 152, 162), "d": (104, 106, 116), "D": (66, 68, 78), "h": (80, 82, 92),
            "r": (60, 170, 255), "L": (150, 152, 162)}),
        dict(id="chocolate", nome="CHOCOLATE", preco=200, cor=(110, 70, 40), troca={
            "G": (170, 116, 70), "g": (120, 78, 42), "d": (84, 52, 26), "D": (54, 32, 14), "h": (40, 24, 10),
            "c": (230, 200, 160), "C": (190, 156, 116), "L": (120, 78, 42)}),
        dict(id="indoraptor", nome="HÍBRIDO SOMBRIO", preco=0, codigo="DINOWOLF", cor=(40, 40, 46), troca={
            "G": (78, 78, 88), "g": (50, 50, 58), "d": (34, 34, 40), "D": (20, 20, 24),
            "h": (50, 50, 58), "L": (240, 176, 40), "c": (104, 104, 114), "C": (78, 78, 88), "r": (255, 200, 30)}),
    ],
    "KING RIP": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="vermelho", nome="MESTRE VERMELHO", preco=100, cor=(180, 50, 50), troca={
            "B": (236, 110, 100), "b": (180, 46, 44), "v": (110, 22, 26)}),
        dict(id="negro", nome="MESTRE DA NOITE", preco=200, cor=(40, 40, 50), troca={
            "B": (90, 90, 104), "b": (46, 46, 56), "v": (26, 26, 32), "x": (230, 230, 236), "X": (255, 255, 255)}),
        dict(id="aragorn", nome="GUARDIÃO ERRANTE", preco=0, codigo="DESTEMIBLEWARRIOR", cor=(80, 70, 50), troca={
            "B": (104, 92, 66), "b": (72, 64, 44), "v": (44, 38, 26), "h": (70, 48, 32), "H": (100, 70, 46),
            "j": (52, 36, 24), "x": (52, 40, 30), "X": (84, 66, 48)}, estilo="aragorn"),  # (espada no lugar do nunchaku)
    ],
    "CANNAN": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="deserto", nome="FARDA DO DESERTO", preco=100, cor=(190, 160, 110), troca={
            "o": (176, 146, 100), "O": (210, 182, 136), "x": (110, 88, 60), "X": (150, 124, 90)}),
        dict(id="artico", nome="FARDA DO ÁRTICO", preco=200, cor=(220, 224, 230), troca={
            "o": (214, 218, 226), "O": (244, 246, 250), "x": (70, 76, 90), "X": (110, 118, 134), "g": (255, 120, 60)}),
        dict(id="megacannon", nome="MEGA-CANNON", preco=0, codigo="MEGACANNON", cor=(40, 140, 240), troca={
            "o": (60, 170, 250), "O": (120, 210, 255), "x": (10, 80, 200), "X": (30, 120, 236),
            "h": (10, 80, 200), "H": (30, 120, 236), "b": (10, 60, 160),
            "c": (60, 170, 250), "C": (150, 224, 255), "m": (10, 80, 200), "g": (255, 236, 110)}),
    ],
    "FINN": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="branco", nome="MAGO BRANCO", preco=100, cor=(220, 220, 228), troca={
            "R": (250, 250, 255), "r": (214, 216, 226), "v": (150, 154, 170), "x": (120, 124, 140),
            "X": (170, 174, 190), "a": (200, 170, 70), "A": (240, 214, 120), "b": (200, 200, 210), "B": (150, 150, 164)}),
        dict(id="fogo", nome="MAGO DO FOGO", preco=200, cor=(180, 50, 30), troca={
            "R": (236, 110, 60), "r": (180, 50, 30), "v": (110, 24, 16), "a": (40, 34, 40), "A": (80, 70, 80),
            "b": (150, 40, 24), "B": (100, 24, 14), "o": (255, 200, 60)}),
        dict(id="gandalf", nome="MAGO PEREGRINO", preco=0, codigo="THEBESTMAGICIAN", cor=(140, 140, 148), troca={
            "R": (160, 160, 168), "r": (128, 128, 136), "v": (90, 90, 98), "o": (110, 110, 118),
            "x": (90, 70, 50), "X": (120, 96, 70), "a": (150, 150, 156), "A": (190, 190, 196),
            "b": (120, 120, 128), "B": (90, 90, 98), "h": (206, 206, 212), "H": (236, 236, 240)}, estilo="gandalf"),
    ],
    "KUN": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="ouros", nome="ÁS DE OUROS", preco=100, cor=(220, 180, 60), troca={
            "R": (250, 220, 110), "r": (214, 170, 50), "v": (150, 110, 24), "e": (210, 40, 40)}),
        dict(id="coringa", nome="CORINGA", preco=200, cor=(110, 50, 150), troca={  # (o Gomes pediu: mais Coringa)
            "R": (160, 90, 210), "r": (116, 52, 160), "v": (70, 28, 104),         # terno roxo
            "c": (104, 46, 146), "C": (140, 80, 186),                             # calça roxa
            "w": (240, 140, 40), "e": (60, 150, 70),                              # camisa laranja e colete verde
            "h": (60, 160, 70), "H": (120, 210, 110),                             # cabelo verde
            "p": (242, 242, 236), "P": (214, 214, 210), "q": (176, 176, 172),     # cara branca
            "b": (210, 20, 40), "B": (210, 20, 40),                               # o sorrisão vermelho
            "s": (120, 72, 40), "S": (84, 48, 24)}),                              # sapatos marrons
        dict(id="ash", nome="TREINADOR", preco=0, codigo="CARDFIGHT", cor=(220, 30, 40), troca={
            "R": (70, 120, 220), "r": (40, 84, 190), "v": (24, 52, 130), "w": (34, 34, 40), "e": (34, 34, 40),
            "c": (54, 76, 140), "C": (84, 108, 172), "s": (220, 36, 40), "S": (240, 240, 244)}, estilo="ash"),
    ],
    "TROMOS": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="albino", nome="TROMOS ALBINO", preco=100, cor=(200, 200, 206), troca={
            "b": (150, 150, 158), "x": (196, 196, 204), "X": (230, 230, 236), "s": (255, 255, 255),
            "y": (230, 40, 40), "Y": (255, 160, 160)}),
        dict(id="fogo", nome="TROMOS DE FOGO", preco=200, cor=(140, 30, 20), troca={
            "b": (60, 10, 8), "x": (120, 24, 18), "X": (200, 60, 30), "s": (255, 150, 60),
            "y": (255, 255, 255), "Y": (255, 255, 255)}),
        dict(id="indominus", nome="REX FUGITIVO", preco=0, codigo="UNTAMABLE", cor=(214, 212, 204), troca={
            "b": (150, 150, 152), "x": (204, 202, 194), "X": (232, 230, 222), "s": (180, 180, 176),
            "y": (230, 30, 30), "Y": (255, 150, 130), "d": (250, 250, 240)}, estilo="indominus"),
    ],
    "TAMER": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="noturno", nome="EXPLORADOR NOTURNO", preco=100, cor=(60, 80, 60), troca={
            "c": (70, 90, 66), "C": (100, 124, 92), "v": (44, 58, 42), "o": (40, 44, 40), "O": (66, 70, 64),
            "h": (50, 62, 46), "H": (80, 96, 72)}),
        dict(id="safari", nome="SAFÁRI", preco=200, cor=(230, 220, 190), troca={
            "c": (232, 222, 192), "C": (250, 244, 224), "v": (196, 180, 140), "o": (176, 150, 100),
            "O": (206, 182, 130), "h": (232, 222, 192), "H": (250, 244, 224)}),
        dict(id="zeus", nome="ZEUS (e o FENRIR)", preco=0, codigo="FENRIR", cor=(240, 240, 250), troca={
            "c": (238, 238, 246), "C": (255, 255, 255), "v": (200, 202, 218), "u": (238, 238, 246),
            "o": (226, 228, 238), "O": (250, 250, 255), "h": (246, 246, 250), "H": (255, 255, 255),
            "b": (190, 146, 44), "B": (240, 200, 90), "s": (226, 186, 60), "x": (246, 246, 250)},
             estilo="zeus",
             lobo=dict(olho=(255, 40, 30), tam=1.2, corrente=True,  # FENRIR: maior, olho vermelho, corrente quebrada
                       cores={"branco": ((150, 160, 182), (112, 120, 142), (70, 76, 96), (255, 40, 30)),
                              "preto": ((40, 42, 56), (26, 28, 38), (14, 14, 20), (255, 40, 30))})),
    ],
    "JOHN": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="branco", nome="ILUSIONISTA BRANCO", preco=100, cor=(230, 230, 236), troca={
            "f": (226, 226, 234), "F": (250, 250, 255), "c": (214, 214, 224), "C": (240, 240, 248),
            "v": (60, 160, 230), "g": (60, 160, 230), "s": (230, 230, 236), "S": (255, 255, 255)}),
        dict(id="carmesim", nome="MÁGICO CARMESIM", preco=200, cor=(160, 30, 40), troca={
            "f": (140, 24, 34), "F": (190, 50, 60), "v": (240, 200, 70), "g": (240, 200, 70),
            "h": (24, 20, 26), "H": (60, 56, 70), "m": (24, 20, 26)}),
        dict(id="gatola", nome="GATOLA DA CARTOLA", preco=0, codigo="TIGERHAT", cor=(220, 30, 40), troca={
            "f": (26, 24, 30), "F": (52, 50, 60), "v": (26, 24, 30), "w": (26, 24, 30), "g": (220, 30, 40),
            "h": (26, 24, 30), "H": (52, 50, 60), "p": (46, 44, 52), "P": (70, 68, 80), "q": (246, 246, 246),
            "m": (246, 246, 246), "e": (240, 220, 80)}, estilo="gatola"),  # cara preta, focinho branco, olho de gato  # (código da v2.0: cartola listrada, gravata vermelha, bigodes)
    ],
    "CRÁQUEN": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="roxo", nome="ASSOMBRAÇÃO ROXA", preco=100, cor=(120, 70, 160), troca={
            "c": (90, 50, 130), "C": (130, 90, 180), "v": (54, 26, 84), "p": (220, 190, 245), "P": (240, 220, 255),
            "q": (170, 130, 200), "e": (255, 120, 200)}),
        dict(id="fogo", nome="FANTASMA DE FOGO", preco=200, cor=(200, 80, 30), troca={
            "c": (150, 40, 20), "C": (210, 90, 40), "v": (90, 20, 10), "p": (255, 200, 140), "P": (255, 230, 190),
            "q": (230, 140, 80), "e": (255, 250, 150), "a": (60, 60, 60), "A": (100, 100, 100)}),
        dict(id="mumia", nome="MÚMIA DO DESERTO", preco=0, codigo="MAGICCREATURES", cor=(206, 186, 136), troca={
            "c": (196, 176, 126), "C": (226, 210, 166), "v": (150, 130, 90), "g": (120, 96, 60),
            "w": (214, 198, 150), "b": (120, 98, 64), "p": (184, 152, 100), "P": (210, 182, 132),
            "q": (146, 116, 76), "e": (40, 28, 18), "a": (226, 212, 172), "A": (244, 234, 200), "k": (54, 40, 22)},
             estilo="mumia"),  # (parecida com o Husk do Minecraft, só que arredondada)
    ],
    "MAGNUS": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="gelo", nome="MAGNUS DE GELO", preco=100, cor=(150, 200, 240), troca={
            "m": (196, 214, 230), "M": (130, 156, 186), "c": (236, 244, 252), "b": (80, 190, 255),
            "B": (200, 240, 255)}),
        dict(id="dourado", nome="PROTÓTIPO DOURADO", preco=200, cor=(220, 180, 60), troca={
            "m": (200, 160, 50), "M": (140, 104, 24), "c": (250, 222, 120), "b": (255, 60, 40),
            "B": (255, 170, 140)}),
        dict(id="blue", nome="RAPTOR AZUL", preco=0, codigo="MASTEROFTACTICS", cor=(60, 110, 200), troca={
            "m": (150, 142, 120), "M": (110, 102, 84), "c": (206, 196, 168), "b": (52, 104, 196),
            "B": (236, 196, 70)}, estilo="blue"),  # a raptor do Jurassic World: sem metal, sem fogo, listra azul
    ],
    "SPHYRUS": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="tigre", nome="TUBARÃO-TIGRE", preco=100, cor=(170, 140, 90), troca={
            "m": (150, 128, 92), "M": (104, 86, 58), "a": (232, 222, 190), "l": (255, 170, 60), "o": (255, 240, 120)}),
        dict(id="abissal", nome="ABISSAL", preco=200, cor=(40, 30, 70), troca={
            "m": (40, 38, 60), "M": (24, 22, 38), "a": (90, 70, 120), "l": (200, 90, 255), "o": (120, 255, 200)}),
        dict(id="megalodonte", nome="MEGALODONTE", preco=0, codigo="ANCIENTJAW", cor=(60, 64, 72), troca={
            "m": (58, 62, 70), "M": (38, 40, 46), "a": (214, 212, 204), "l": (40, 70, 120), "o": (10, 10, 12)},
             estilo="megalodonte"),  # o tubarão pré-histórico: sem martelo, cabeçona, dentões, cicatrizes
    ],
    "FRIGANTUS": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="tundra", nome="TUNDRA", preco=100, cor=(190, 190, 186), troca={
            "m": (196, 194, 188), "M": (150, 148, 142), "p": (70, 66, 64), "c": (200, 220, 230)}),
        dict(id="aurora", nome="AURORA", preco=200, cor=(170, 210, 255), troca={
            "m": (214, 232, 255), "M": (150, 120, 230), "p": (60, 70, 100), "c": (120, 255, 200)}),
        dict(id="pegrande", nome="PÉ-GRANDE", preco=0, codigo="BIGFOOTPRINT", cor=(110, 80, 50), troca={
            "m": (118, 84, 52), "M": (84, 58, 34), "p": (62, 50, 42), "c": (80, 130, 50)}, estilo="pegrande"),
    ],
    "INAZUMANEKO": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="tigrenegro", nome="TIGRE NEGRO", preco=100, cor=(40, 38, 44), troca={  # o pelo preto, listras brancas
            "w": (46, 44, 52), "W": (28, 26, 34), "l": (90, 88, 96), "s": (236, 236, 230), "o": (255, 80, 60),
            "r": (60, 60, 70), "R": (96, 96, 110), "d": (180, 180, 196), "g": (110, 20, 30), "G": (150, 40, 50)}),
        dict(id="ronindejade", nome="RONIN DE JADE", preco=200, cor=(60, 160, 120), troca={  # o tigre dourado de armadura verde
            "w": (236, 180, 90), "W": (196, 140, 60), "l": (250, 236, 210), "s": (70, 40, 20), "o": (90, 230, 160),
            "r": (40, 120, 90), "R": (70, 170, 130), "d": (236, 220, 150), "g": (30, 60, 50), "G": (50, 90, 74),
            "h": (30, 40, 34), "H": (50, 64, 56)}),
        dict(id="oni", nome="ONI", preco=0, codigo="PARADISEHELL", cor=(190, 30, 34), troca={  # a máscara de demônio
            "r": (30, 28, 34), "R": (60, 56, 64), "d": (190, 30, 34), "g": (24, 22, 28), "G": (50, 46, 56),
            "h": (20, 18, 24), "H": (44, 40, 50), "o": (255, 40, 40), "w": (120, 120, 128), "W": (90, 90, 98),
            "l": (160, 160, 166), "b": (190, 30, 34)}, estilo="oni"),
    ],
    "KATCHADE": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="inverno", nome="INVERNO", preco=100, cor=(236, 244, 255), troca={  # quase todo branquinho, olho de gelo
            "w": (255, 255, 255), "W": (214, 224, 242), "p": (232, 238, 252), "P": (186, 200, 236),
            "m": (140, 166, 220), "e": (226, 244, 255), "E": (140, 196, 240), "a": (250, 252, 255),
            "A": (206, 222, 246), "l": (240, 250, 255), "L": (176, 208, 240)}),
        dict(id="samurai", nome="ESPADACHIM ERRANTE", preco=200, cor=(58, 62, 112), troca={  # inspirado no Musashi
            "w": (236, 226, 212), "W": (198, 184, 166), "p": (150, 118, 140), "P": (108, 82, 104),
            "m": (70, 58, 92), "e": (240, 220, 200), "E": (176, 140, 120), "a": (222, 212, 200),
            "A": (178, 164, 148), "l": (214, 222, 232), "L": (146, 156, 174), "s": (56, 56, 66)}, estilo="samurai"),
    ],
    "SILVANUS": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="outono", nome="OUTONO", preco=100, cor=(210, 110, 40), troca={  # as folhas de outono, a boca vermelha
            "g": (200, 110, 40), "G": (240, 170, 70), "d": (140, 64, 26), "p": (170, 36, 30), "P": (220, 80, 56),
            "m": (160, 90, 34), "f": (255, 210, 80), "F": (255, 246, 200), "y": (255, 200, 90), "Y": (150, 96, 50)}),
        dict(id="luar", nome="LUAR DA FLORESTA", preco=200, cor=(150, 200, 230), troca={  # a planta que brilha de noite
            "g": (70, 110, 140), "G": (130, 190, 220), "d": (40, 60, 90), "p": (40, 70, 130), "P": (90, 150, 220),
            "q": (14, 24, 50), "m": (60, 100, 120), "f": (200, 240, 255), "F": (255, 255, 255),
            "y": (140, 255, 250), "Y": (60, 110, 130), "t": (70, 70, 90), "T": (110, 110, 140)}),
    ],
    "NOCTURNUS": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="albino", nome="ALBINO", preco=100, cor=(236, 226, 230), troca={  # o morcego branco de olho vermelho
            "p": (226, 218, 222), "P": (250, 244, 246), "m": (240, 190, 200), "M": (210, 150, 166), "f": (250, 236, 240),
            "F": (255, 250, 252), "e": (255, 60, 70), "r": (255, 120, 140), "b": (200, 120, 140), "B": (240, 190, 200)}),
        dict(id="cristal", nome="ECO DE CRISTAL", preco=200, cor=(140, 90, 220), troca={  # o morcego dos cristais da caverna
            "p": (60, 30, 100), "P": (110, 60, 170), "m": (170, 110, 255), "M": (120, 70, 200), "f": (150, 110, 220),
            "F": (200, 170, 255), "e": (255, 220, 120), "b": (255, 200, 90), "B": (255, 240, 180), "v": (220, 130, 255)}),
    ],
    "TAI": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="dourado", nome="MAWASHI DOURADO", preco=100, cor=(236, 190, 150), troca={
            "m": (210, 170, 50), "M": (250, 220, 110), "n": (150, 110, 24)}),
        dict(id="luchador", nome="OGRO DO PÂNTANO", preco=200, cor=(140, 186, 70), troca={  # (era o Hawlucha; o Gomes pediu o Shrek)
            "p": (150, 190, 70), "P": (182, 214, 100), "q": (108, 146, 48), "h": (150, 190, 70), "e": (40, 30, 20),
            "z": None, "y": None,
            "a": (226, 214, 176), "A": (244, 236, 208), "Q": (186, 172, 132),
            "v": (112, 76, 42), "V": (142, 102, 58), "w": (80, 52, 26), "x": (150, 120, 80),
            "i": (160, 128, 84), "I": (186, 154, 106), "j": (118, 92, 58),
            "f": (74, 48, 28), "F": (100, 70, 42), "g": (50, 32, 18),
            "m": (96, 64, 34), "M": (128, 90, 50), "n": (60, 40, 20)}, orelhas=True),
        dict(id="gru", nome="GÊNIO DO MAL", preco=0, codigo="THEMOONISMINE", cor=(40, 40, 46), troca={
            "p": (236, 214, 190), "P": (250, 232, 212), "q": (200, 170, 150), "h": (236, 214, 190), "e": (24, 20, 24),
            "z": None, "y": None,
            "a": (58, 58, 66), "A": (80, 80, 90), "Q": (40, 40, 46), "v": (30, 30, 36), "V": (50, 50, 58),
            "w": (20, 20, 24), "x": (90, 90, 98), "i": (50, 50, 58), "I": (70, 70, 80), "j": (34, 34, 40),
            "f": (22, 20, 24), "F": (44, 42, 48), "g": (12, 10, 14),
            "m": (30, 30, 36), "M": (50, 50, 58), "n": (20, 20, 24)}, estilo="gru"),
    ],
}


# RIBBAT: os chapéus do jogo dele (todos com o código ULTRA-MEGA-SKINS)
ROUPAS["RIBBAT"] = [dict(id="padrao", nome="ORIGINAL", preco=0)] + [
    dict(id=c, nome=chapeus_ribbat.NOMES[c], preco=0, codigo="ULTRAMEGASKINS", cor=chapeus_ribbat.CORES[c], troca={},
         chapeu=c) for c in chapeus_ribbat.CHAPEUS]


# SOMBRA (código THEDARKESTDUMMY) e OURO (código BRUTEFORTUNE): pra TODO MUNDO.
# Não trocam cor por cor: pintam o desenho inteiro (a "tinta"), então funcionam em qualquer personagem.
for _lista in ROUPAS.values():
    _lista.append(dict(id="sombra", nome="SOMBRA", preco=0, codigo="THEDARKESTDUMMY", cor=(70, 50, 110), troca={},
                       tinta="sombra"))
    _lista.append(dict(id="ouro", nome="LENDÁRIA (OURO)", preco=0, codigo="BRUTEFORTUNE", cor=(240, 190, 60),
                       troca={}, tinta="ouro"))
    # HOLOGRÁFICA: prêmio do ÁLBUM (completou a página de figurinhas do lutador). Tinta arco-íris que muda.
    _lista.append(dict(id="holografica", nome="HOLOGRÁFICA", preco=0, cor=(170, 120, 255), troca={}, tinta="holo",
                       album=True))


# HALLOWEEN (evento automático pela data): 5 skins que só se ganham no PASSE DO EVENTO (com DOCES).
# Quem pegou fica com ela pra sempre (a loja mostra a skin só pra quem tem).
HALLOWEEN = {
    "SPHYRUS": dict(id="esqueleto", nome="SPHYRUS ESQUELETO", cor=(226, 222, 206), troca={
        "m": (226, 222, 206), "M": (170, 166, 150), "a": (54, 52, 62), "l": (110, 255, 160), "o": (150, 255, 190)}),
    "FINN": dict(id="bruxo", nome="FINN BRUXO", cor=(80, 40, 110), troca={
        "R": (90, 52, 120), "r": (62, 34, 88), "v": (36, 18, 54), "a": (240, 130, 30), "A": (255, 186, 80),
        "b": (62, 34, 88), "B": (40, 20, 58), "o": (120, 220, 80)}),
    "CRÁQUEN": dict(id="vampiro", nome="CRÁQUEN VAMPIRO", cor=(150, 20, 30), troca={
        "c": (40, 12, 22), "C": (90, 22, 36), "v": (22, 6, 12), "p": (224, 224, 234), "P": (248, 248, 252),
        "q": (172, 172, 190), "e": (255, 40, 40), "a": (60, 56, 70), "A": (96, 92, 106)}),
    "MAX-10": dict(id="frankenrobo", nome="MAX-10 FRANKENROBÔ", cor=(126, 160, 110), troca={
        "G": (170, 200, 150), "g": (126, 160, 110), "d": (90, 120, 80), "D": (60, 82, 54), "r": (170, 255, 110),
        "R": (230, 255, 200)}),
    "RIB": dict(id="zumbi", nome="RIB ZUMBI", cor=(110, 130, 70), troca={
        "G": (150, 172, 104), "g": (112, 132, 72), "d": (78, 96, 50), "D": (48, 62, 32), "c": (196, 184, 140),
        "C": (154, 144, 102), "y": (230, 226, 160), "Y": (250, 248, 210)}),
}
for _nome, _r in HALLOWEEN.items():
    ROUPAS[_nome].append(dict(_r, preco=0, evento="halloween", estilo=_r["id"]))


def de_evento(ficha, evento="halloween"):
    """As skins do evento desse lutador (prêmio do passe do evento)."""
    return [r for r in da(ficha) if r.get("evento") == evento]


def da(ficha):
    """As roupas desse personagem (só a original se ele não tiver nenhuma)."""
    nome = ficha.get("nome_base", ficha["nome"])
    return ROUPAS.get(nome, [dict(id="padrao", nome="ORIGINAL", preco=0)])


def vestir(ficha, roupa=None):
    """A ficha do personagem com a roupa (a que ele está usando no save, se não disser qual).
    Sem dizer a roupa = é o SEU lutador: também vai com a entrada, a vitória e a provocação que você equipou."""
    nome = ficha.get("nome_base", ficha["nome"])
    if roupa is None:
        import extras
        return extras.aplicar(_vestir(ficha, save.usando(nome)), nome)
    return _vestir(ficha, roupa)


def _vestir(ficha, roupa):
    nome = ficha.get("nome_base", ficha["nome"])
    r = next((r for r in da(ficha) if r["id"] == roupa), None)
    if not r or r["id"] == "padrao":
        return dict(ficha, nome_base=nome, roupa="padrao", troca=ficha.get("troca_base"), lobo=None, chapeu=None,
                    tinta=None, orelhas=None, estilo=None)
    return dict(ficha, nome_base=nome, roupa=r["id"], troca=r["troca"] or None, cor=r.get("cor", ficha["cor"]),
                lobo=r.get("lobo"), chapeu=r.get("chapeu"), tinta=r.get("tinta"), orelhas=r.get("orelhas"),
                estilo=r.get("estilo"))


def de_codigo():
    """{código: [(personagem, roupa), ...]} de todas as roupas secretas (um código pode dar várias)."""
    cods = {}
    for nome, lista in ROUPAS.items():
        for r in lista:
            if r.get("codigo"):
                cods.setdefault(r["codigo"], []).append((nome, r))
    return cods


def outra(ficha, menos):
    """Espelho (mesmo personagem dos dois lados): o adversário veste uma roupa diferente."""
    ids = [r["id"] for r in da(ficha)]
    i = ids.index(menos) if menos in ids else 0
    return vestir(ficha, ids[(i + 1) % len(ids)])
