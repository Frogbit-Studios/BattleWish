"""STAMINA e RECARGA (v4.0, ideia do Gomes contra o SPAM).

- Cada ataque gasta stamina (soco pouco, chute mais, especial bem mais; EX gasta 25% a mais).
- Pra usar um ataque precisa ter pelo menos o MÍNIMO dele (metade do custo): dá pra arriscar com pouca.
- Se a stamina ZERAR: fica CANSADO — não anda, não pula, não ataca e não rola até a barra encher.
  (Defender ainda dá: segurar pra trás/baixo parado.)
- Ela volta sozinha um pouquinho depois de parar de atacar.
- Cada especial (E, Q, R, SHIFT) tem RECARGA: depois de usar, espera um tempinho pra usar de novo.
"""
import pygame

STAMINA_MAX = 100
CUSTO = {"soco": 9, "ag_soco": 9, "ar_soco": 9, "chute": 13, "ag_chute": 13, "ar_chute": 13}
CUSTO_NORMAL = 10          # golpe normal de algum personagem que não está na lista
CUSTO_ESPECIAL = 22
EX_A_MAIS = 1.25           # EX gasta 25% a mais (pedido do Gomes)
MINIMO = 0.5               # precisa ter pelo menos metade do custo pra usar
ESPERA = 20                # quadros sem gastar pra começar a voltar
VOLTA = 0.5                # quanto volta por quadro (30 por segundo)
VOLTA_CANSADO = 1.1        # cansado: volta mais rápido, mas só sai quando encher (~1,5 s)
RECARGA = 36               # quadros de recarga do especial (contam depois que o golpe acaba)
RECARGA_RAJADA = 0         # especial de VÁRIOS tiros (shuriken do Rib, cartas do Kun...): já tem munição própria
CUSTO_RAJADA = 8
BOTOES = ("E", "Q", "R", "SHIFT")


def iniciar(l):
    l.stamina = float(STAMINA_MAX)
    l.stamina_espera = 0
    l.cansado = False
    l.recarga = {b: 0 for b in BOTOES}
    l.sem_folego = 0       # piscada da barra quando tentou e não tinha


def ligado(l):
    """Modos sem stamina: treino livre com o boneco e o MODO MALUCO 'sem cansaço'."""
    return "sem_cansaco" not in getattr(l, "regras", ())


def custo(nome, g, ex=False):
    if g.get("ultimate") or nome == "provocar" or g.get("gratis"):
        return 0
    c = g.get("stamina")
    if c is None:
        if g.get("especial"):
            c = CUSTO_RAJADA if g.get("varios") else CUSTO_ESPECIAL
        else:
            c = CUSTO.get(nome, CUSTO_NORMAL)
    return c * (EX_A_MAIS if ex else 1)


def pode_especial(l, botao):
    """O botão do especial já recarregou?"""
    if not ligado(l) or botao not in BOTOES:
        return True
    return l.recarga.get(botao, 0) <= 0


def pagar(l, nome, g, ex=False):
    """Tenta pagar o golpe. Devolve False se não tem o mínimo (o golpe não sai)."""
    if not ligado(l):
        return True
    c = custo(nome, g, ex)
    if c <= 0:
        return True
    if l.cansado or l.stamina < c * MINIMO:
        l.sem_folego = 20
        return False
    l.stamina = max(0.0, l.stamina - c)
    l.stamina_espera = 0
    if l.stamina <= 0:
        l.cansado = True
    return True


def usou_especial(l, botao, g=None):
    if botao in BOTOES:
        g = g or {}
        l.recarga[botao] = g.get("recarga", RECARGA_RAJADA if g.get("varios") else RECARGA)


def passo(l):
    """Todo quadro: a stamina volta e a recarga anda."""
    if l.sem_folego > 0:
        l.sem_folego -= 1
    atacando = l.estado == "ataque"
    if not atacando:
        for b in BOTOES:
            if l.recarga[b] > 0:
                l.recarga[b] -= 1
    if not ligado(l):
        l.stamina, l.cansado = float(STAMINA_MAX), False
        return
    if l.cansado:
        l.stamina = min(STAMINA_MAX, l.stamina + VOLTA_CANSADO)
        if l.stamina >= STAMINA_MAX:
            l.cansado = False
        return
    if atacando:
        l.stamina_espera = 0
        return
    l.stamina_espera += 1
    if l.stamina_espera >= ESPERA:
        l.stamina = min(STAMINA_MAX, l.stamina + VOLTA)


def preso(l):
    """Cansado e no chão: não anda, não pula, não ataca."""
    return l.cansado and ligado(l)


# ------------------------------------------------------------ desenho
def desenhar_barra(tela, l, x, y, larg, lado, t_total):
    """Barrinha verde da stamina (lado 0 = P1, cresce da direita pra esquerda como a vida)."""
    if not ligado(l):
        return
    pygame.draw.rect(tela, (20, 14, 24), (x - 2, y - 1, larg + 4, 6))
    w = int(larg * l.stamina / STAMINA_MAX)
    if l.cansado:
        cor = (255, 80, 60) if (t_total // 6) % 2 else (150, 40, 40)
    elif l.sem_folego and (t_total // 3) % 2:
        cor = (255, 255, 255)
    elif l.stamina < 30:
        cor = (240, 200, 60)
    else:
        cor = (110, 230, 120)
    if w > 0:
        pygame.draw.rect(tela, cor, (x + (larg - w if lado == 0 else 0), y, w, 4))
    if l.cansado:  # a moldura pisca vermelha
        pygame.draw.rect(tela, (255, 80, 60), (x - 2, y - 1, larg + 4, 6), 1)


def desenhar_recargas(tela, l, x, y, lado, fonte):
    """As letrinhas E Q R ⇧ do lado da barra da ultimate: apagadas enchendo enquanto recarregam."""
    if not ligado(l):
        return
    golpes = (getattr(l, "mutado", None) or l.f).get("golpes", None)
    tam = 18
    botoes = [b for b in BOTOES if golpes is None or golpes.get(b)]
    for k, b in enumerate(botoes):
        bx = x + k * (tam + 4) if lado == 0 else x - (k + 1) * (tam + 4) + 4
        r = pygame.Rect(bx, y, tam, tam)
        falta = l.recarga.get(b, 0) / RECARGA
        pygame.draw.rect(tela, (20, 14, 24), r.inflate(4, 4), border_radius=4)
        pygame.draw.rect(tela, (70, 60, 80) if falta > 0 else (60, 120, 200), r, border_radius=3)
        if falta > 0:  # enche de baixo pra cima
            h = int(tam * (1 - falta))
            if h > 0:
                pygame.draw.rect(tela, (60, 100, 160), (bx, y + tam - h, tam, h))
        letra = "SH" if b == "SHIFT" else b
        img = fonte(10 if b == "SHIFT" else 12).render(letra, True, (150, 150, 160) if falta > 0 else (255, 255, 255))
        tela.blit(img, img.get_rect(center=r.center))


def desenhar_cansado(tela, l, t, cx, cy):
    """Gotinhas de suor pingando da cabeça de quem cansou."""
    if not (l.cansado and ligado(l)):
        return
    for k in range(3):
        fase = (t + k * 9) % 27
        gx = cx + (-14, 2, 16)[k] * l.s
        gy = cy + fase * 1.1
        a = max(0, 255 - fase * 9)
        cor = (120, 200, 255) if a > 80 else (80, 140, 200)
        pygame.draw.polygon(tela, cor, [(gx, gy - 5), (gx - 3, gy + 1), (gx + 3, gy + 1)])
        pygame.draw.circle(tela, cor, (int(gx), int(gy + 1)), 3)
