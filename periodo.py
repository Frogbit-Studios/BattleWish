"""DIA E NOITE (v2.x, pedido do Gomes): os cenários ABERTOS ganham outras horas do dia, sorteadas em cada luta.
Os fechados (Toca, Dojo, Torre do Mago, Cassino, Laboratório, Arena de Sumô, Teatro) ficam sempre iguais.

  cenário de DIA (Selva, Vila dos Sapos, Cercado, Praia)  -> DIA, PÔR DO SOL ou NOITE
  cenário de PÔR DO SOL (Templo, Ferro-velho, Campo)      -> PÔR DO SOL ou NOITE (o céu deles não vira dia direito)
  cenário de NOITE (Pântano)                              -> NOITE, AMANHECER ou DIA NUBLADO
  NAVIO FANTASMA                                          -> NOITE ou AMANHECER (navio fantasma de dia não assusta)

É SÓ DESENHO: pinta a imagem pequena (pixel art) por cima, não muda nada da luta (dá igual no online).
Como usar (a partida):
  self.periodo = periodo.criar(nome_do_cenario, rng)         # rng = random.Random(semente) se tiver
  ... baixo = cena.desenhar_pequeno(...); self.periodo.pintar_fundo(baixo)      # logo depois do fundo
  ... (objetos, clima, lutadores, efeitos desenhados no baixo) ...
  self.periodo.pintar_tudo(baixo)                                                # antes de ampliar a tela
"""
import random

import pygame

DIA, POR, NOITE, AMANHECER, NUBLADO = "DIA", "PÔR DO SOL", "NOITE", "AMANHECER", "DIA NUBLADO"

# os possíveis de cada cenário (o primeiro é o original, o que já está desenhado)
PERIODOS = {
    "SELVA": (DIA, POR, NOITE),
    "VILA DOS SAPOS": (DIA, POR, NOITE),
    "CERCADO DO DESERTO": (DIA, POR, NOITE),
    "PRAIA DA ILHA": (DIA, POR, NOITE),
    "TEMPLO": (POR, NOITE),
    "FERRO-VELHO": (POR, NOITE),
    "CAMPO DE BATALHA": (POR, NOITE),
    "PÂNTANO": (NOITE, AMANHECER, NUBLADO),
    "NAVIO FANTASMA": (NOITE, AMANHECER),
    "MONTE KARASUMA": (POR, NOITE, AMANHECER),
    "CAMPO GIGANTE": (DIA, POR, NOITE),
}
HORIZONTE = 0.6  # até onde (fração da altura) vai o "céu", pra o degradê e as estrelas


def criar(nome_do_cenario, rng=random, periodo=None):
    """Sorteia a hora do dia do cenário (ou usa a pedida). Cenário fechado: Nada (não pinta nada)."""
    opcoes = PERIODOS.get(nome_do_cenario)
    if not opcoes:
        return Nada()
    if periodo not in opcoes:
        periodo = rng.choice(opcoes)
    return Periodo(nome_do_cenario, opcoes[0], periodo)


class Nada:
    nome = ""
    original = True

    def pintar_fundo(self, peq, t=0):
        pass

    def pintar_tudo(self, peq):
        pass


class Periodo:
    def __init__(self, cenario, original, periodo):
        self.cenario = cenario
        self.de = original
        self.nome = periodo
        self.original = original == periodo
        self._grad = {}       # degradês prontos (por tamanho)
        self._estrelas = {}   # posições das estrelas (por tamanho)

    # ---- peças guardadas (feitas uma vez só) ----
    def degrade(self, tam, cor, forte=1.0):
        chave = (tam, cor, forte)
        if chave not in self._grad:
            w, h = tam
            camada = pygame.Surface((w, h))
            camada.fill((0, 0, 0))
            lim = max(1, int(h * HORIZONTE))
            for y in range(lim):
                k = (1 - y / lim) * forte
                camada.fill(tuple(int(c * k) for c in cor), (0, y, w, 1))
            self._grad[chave] = camada
        return self._grad[chave]

    def estrelas(self, tam):
        if tam not in self._estrelas:
            w, h = tam
            rng = random.Random(sum(map(ord, self.cenario)))  # (sempre as mesmas estrelas nesse cenário)
            self._estrelas[tam] = [(rng.randrange(w), rng.randrange(int(h * 0.5)), rng.randint(170, 255))
                                   for _ in range(60)]
        return self._estrelas[tam]

    # ---- pintura ----
    def pintar_fundo(self, peq, t=0):
        """Logo depois do fundo: a pintura forte (céu, cor do lugar, estrelas)."""
        if self.original:
            return
        tam = peq.get_size()
        de, para = self.de, self.nome
        if para == NOITE:
            peq.fill((70, 85, 150), special_flags=pygame.BLEND_RGB_MULT)
            peq.blit(self.degrade(tam, (0, 4, 20)), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            for i, (x, y, v) in enumerate(self.estrelas(tam)):
                c = peq.get_at((x, y))
                if c.r + c.g + c.b < 200:  # só no céu escuro (não em cima de árvore ou nuvem)
                    pisca = v if (t // 20 + i) % 9 else v // 2
                    peq.set_at((x, y), (pisca, pisca, min(255, pisca + 20)))
        elif para == POR:  # (de DIA)
            peq.fill((255, 190, 160), special_flags=pygame.BLEND_RGB_MULT)
            peq.blit(self.degrade(tam, (90, 30, 0)), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        elif para == AMANHECER:  # (de NOITE)
            peq.fill((22, 16, 12), special_flags=pygame.BLEND_RGB_ADD)
            peq.blit(self.degrade(tam, (120, 55, 30)), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            peq.fill((255, 225, 210), special_flags=pygame.BLEND_RGB_MULT)
        elif para == NUBLADO:  # (de NOITE)
            peq.fill((45, 50, 45), special_flags=pygame.BLEND_RGB_ADD)
            peq.blit(self.degrade(tam, (40, 80, 120)), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            peq.fill((235, 245, 255), special_flags=pygame.BLEND_RGB_MULT)

    def pintar_tudo(self, peq):
        """Depois de desenhar tudo (lutadores, objetos, efeitos): uma pintura leve, pra ninguém ficar
        'brilhando' no escuro nem branco demais no pôr do sol."""
        if self.original:
            return  # (a hora original do cenário fica exatamente como sempre foi)
        if self.nome == NOITE:
            peq.fill((185, 195, 235), special_flags=pygame.BLEND_RGB_MULT)
        elif self.nome == POR:
            peq.fill((255, 225, 205), special_flags=pygame.BLEND_RGB_MULT)
        elif self.nome == AMANHECER:
            peq.fill((255, 235, 225), special_flags=pygame.BLEND_RGB_MULT)
