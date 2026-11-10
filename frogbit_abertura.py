"""Abertura da FROGBIT STUDIO: o sapinho espiando o bit, antes do menu.
Toca a tira frogbit_abertura_tira.png (quadros de 96x54, 12 por segundo) ampliada sem borrar.
Qualquer tecla, clique ou botão do controle pula. Devolve False se fecharam a janela."""
import os
import sys

import pygame

QUADRO_L, QUADRO_A, FPS_ABERTURA = 96, 54, 12
COR_FUNDO = (17, 19, 22)


def _tira():
    pasta = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return pygame.image.load(os.path.join(pasta, "frogbit_abertura_tira.png")).convert()


def _jingle():
    """O somzinho da abertura (se o som estiver ligado)."""
    try:
        if not pygame.mixer.get_init():
            return None
        pasta = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        som = pygame.mixer.Sound(os.path.join(pasta, "frogbit_jingle.wav"))
        som.set_volume(0.6)
        som.play()
        return som
    except (pygame.error, FileNotFoundError):
        return None


def tocar(tela):
    try:
        tira = _tira()
    except (pygame.error, FileNotFoundError):
        return True                                    # sem o arquivo: segue pro jogo sem abertura
    som = _jingle()
    total = tira.get_width() // QUADRO_L
    L, A = tela.get_size()
    esc = max(1, min(L // QUADRO_L, A // QUADRO_A))    # ampliação inteira (pixel nítido)
    dest = pygame.Rect(0, 0, QUADRO_L * esc, QUADRO_A * esc); dest.center = (L // 2, A // 2)
    relogio = pygame.time.Clock()
    for i in range(total):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                if som: som.stop()
                return False
            if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.JOYBUTTONDOWN):
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen(); continue
                if som: som.fadeout(250)
                return True
        quadro = tira.subsurface((i * QUADRO_L, 0, QUADRO_L, QUADRO_A))
        tela.fill(COR_FUNDO)
        tela.blit(pygame.transform.scale(quadro, dest.size), dest)
        pygame.display.flip()
        relogio.tick(FPS_ABERTURA)
    return True
