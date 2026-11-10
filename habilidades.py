"""Habilidades (passivas) de cada personagem — criadas pelo Gomes.

  MAX-10  MAQUINÁRIO PESADO  com 25% de vida ou menos: +25% de dano e leva 25% menos
  RIB     POSTURA NINJA      hitbox naturalmente menor
  TRAFO   (ele ainda está decidindo, dá pra trocar na seleção com H)
          CONEXÃO TERRESTRE  agachado fica bem menor, bate o dobro e leva menos dano
          MUTAÇÃO            levou um ultimate: vira o oponente (aparência, golpes e habilidade dele)
  KING    MAESTRIA DE COMBATE combos mais longos
  CANNAN  COLETE À PROVA DE BALAS  50% menos dano de média e longa distância
  FINN    PODER MÁGICO       fez o combo máximo: fica invisível por 3 segundos
  KUN     ÁS NA MANGA        a cada 15 segundos o ás acende: por 5 segundos, +5 de dano em todo ataque
  TROMOS  SANGUE ÁCIDO       quem bate nele de perto leva 1 de dano
  TAI     PESO PESADO        120 de vida, soco/chute normal não fazem ele recuar (mas é o mais lento)
  TAMER   ENTENDIMENTO MÚTUO X troca o lobo: BRANCO = +25% de dano, PRETO = ataques 50% mais rápidos
  SPHYRUS (escolhe com H) ELETRORRECEPÇÃO / NATAÇÃO / FRENESI
  MAGNUS  CORPO ÁGIL         70 de vida (30 a menos), mas a hitbox é metade da dos outros e é 20% mais rápido
"""
from config import CHAO, LARGURA, PAREDE_D, PAREDE_E

HABILIDADES = {
    "maquinario": dict(nome="MAQUINÁRIO PESADO", desc="25% de vida ou menos: +25% de dano, leva 25% menos"),
    "ninja": dict(nome="MAESTRIA NINJA", desc="pulo duplo e mais alto, leva 20% menos no ar; a cada 15 s: SUBSTITUIÇÃO"),
    "conexao": dict(nome="CONEXÃO TERRESTRE", desc="agachado: bem menor, bate o dobro e leva 20% menos"),
    "maestria": dict(nome="MAESTRIA DE COMBATE", desc="combos mais longos: 18 golpes em vez de 12"),
    "mutacao": dict(nome="MUTAÇÃO", desc="levou ultimate: vira o oponente e usa os golpes e a habilidade dele"),
    "alquimia": dict(nome="ALQUIMIA", desc="a cada 16 s bebe uma poção: FORÇA (+25% dano), VELOCIDADE ou CURA (+8)"),
    "cura": dict(nome="FEITIÇO DE CURA", desc="a cada 5 golpes no mesmo combo: recupera 5 de vida"),
    "emboscada": dict(nome="EMBOSCADA", desc="parado 1,5 s: fica CAMUFLADO; o 1º golpe saindo da camuflagem: +50%"),
    "regeneracao": dict(nome="REGENERAÇÃO", desc="toda vez que derruba o adversário: recupera 6 de vida"),
    "furia_sumo": dict(nome="FÚRIA DO SUMÔ", desc="levou 5 golpes no mesmo combo: +25% de dano por 5 s (recarga 15 s)"),
    "cartas": dict(nome="TRUQUE DE CARTAS", desc="cada golpe que acerta marca 1 carta no adversário; 3 cartas EXPLODEM (10)"),
    "coelho": dict(nome="COELHO AJUDANTE", desc="a cada 8 s o coelhinho morde quem chega perto (5) ou bloqueia um tiro"),
    "adaptacao": dict(nome="ADAPTAÇÃO", desc="cada golpe que acerta nele: leva 10% menos daquele golpe (até 40%)"),
    "colete": dict(nome="COLETE À PROVA DE BALAS", desc="leva 50% menos dano de ataques de média e longa distância"),
    "poder_magico": dict(nome="PODER MÁGICO", desc="fez o combo máximo: fica invisível por 3 segundos"),
    "as_na_manga": dict(nome="ÁS NA MANGA", desc="a cada 15 segundos: por 5 segundos, +5 de dano em todo ataque"),
    "sangue_acido": dict(nome="SANGUE ÁCIDO", desc="quem bate nele de perto leva 1 de dano de ácido"),
    "peso_pesado": dict(nome="PESO PESADO", desc="120 de vida e soco/chute normal não fazem ele recuar"),
    "entendimento": dict(nome="ENTENDIMENTO MÚTUO", desc="X troca o lobo: BRANCO = +50% de dano, PRETO = ataques mais rápidos"),
    "intangivel": dict(nome="INTANGÍVEL", desc="parado 2 segundos: o próximo golpe que levar ATRAVESSA (sem dano)"),
    "nevasca": dict(nome="NEVASCA", desc="cada golpe deixa o adversário mais lento; 3 seguidos = CONGELA 1 segundo"),
    "corpo_agil": dict(nome="CORPO ÁGIL", desc="70 de vida, mas a hitbox é 20% MENOR que a dos outros e é 10% mais rápido"),
    "eletro": dict(nome="PADRÃO DE CAÇA", desc="cada especial que acerta 2x fica +10% mais forte (até +50%); acerta invisível"),
    "natacao": dict(nome="NATAÇÃO", desc="X: nada só com a barbatana, intangível (8 s); passar por baixo dá 8 e derruba"),
    "frenesi": dict(nome="FRENESI", desc="adversário com 35% de vida ou menos: dano x2 e +30% de velocidade"),
    "abracadabra": dict(nome="ABRACADABRA", desc="depois de teleportar (Q e SHIFT), fica invisível por meio segundo"),
    "furia_samurai": dict(nome="FÚRIA SAMURAI", desc="levou PARRY: ultimate +8%; o CONTRA-ATAQUE (Q) acertou: +5%"),
    "eco": dict(nome="ECOLOCALIZAÇÃO", desc="o adversário se mexe MUITO: +50% velocidade e força; mexe POUCO: -25%"),
    "planar": dict(nome="PLANAR", desc="no ar cai devagar (plana com as asas) e leva 25% menos de dano lá em cima"),
    "senso": dict(nome="SENSO AUDITIVO", desc="X troca: AGUDO (leves/aéreos/multi) ou GRAVE (pesados/agachados/dash): "
                                              "leva 15% menos; a cada acerto: AGUDO +3% rapidez / GRAVE +5% dano (5x)"),
    "jardim": dict(nome="JARDIM VIVO", desc="cada armadilha no mapa: +7% de força (até 5 = +35%)"),
    "enganador": dict(nome="ENGANADOR SELVAGEM", desc="X + ataque: FINGE o golpe (0,5 s) e pode trocar por outro; 1x a cada 3 s"),
    "vantagem": dict(nome="VANTAGEM POR CIMA", desc="adversário AGACHADO: os ataques dele ficam 15% mais fortes"),
    "camuflagem": dict(nome="CAMUFLAGEM", desc="parado 2 s: some na flor (meio transparente); o próximo golpe bate +30%"),
    "foices_afiadas": dict(nome="FOICES AFIADAS", desc="golpe que acerta deixa um CORTE brilhando: tira mais 5 em 2 s"),
    "poder_samurai": dict(nome="PODER SAMURAI", desc="parado 3 s: por 3 s os golpes dão VENENO, FOGO, RAIO ou GELO (sorteado)"),
}

JARDIM_PASSO = 0.07   # JARDIM VIVO (Silvanus): +7% de força por armadilha no mapa (máximo 5)
VANTAGEM_DANO = 1.15  # VANTAGEM POR CIMA (Silvanus)
FINTA_TEMPO, FINTA_ESPERA = 30, 180  # ENGANADOR SELVAGEM: a finta dura 0,5 s; 1 vez a cada 3 s
MAQUINARIO_VIDA = 0.25
MAQUINARIO_DANO = 1.25
MAQUINARIO_DEFESA = 0.75
NINJA_LARGURA = 1.0         # (era 0,8: o Rib ganhava 100% do boneco — equilíbrio 19/10)
AGIL_LARGURA = 1.25         # CORPO ÁGIL: baixinho (altura 0,62 na ficha) e um pouco mais largo = ~80% da hitbox
                            # (era metade: o Gomes achou pequena demais; equilíbrio 19/10)
AGIL_VEL = 1.1              # CORPO ÁGIL: 10% mais rápido (era 20%: equilíbrio 19/10)
MAESTRIA_MALABAR = 18      # combo no ar: 18 golpes em vez de 12
MAESTRIA_CADEIA = 2        # emenda 2 golpes normais a mais
CONEXAO_AGACHADO = 0.5      # agachado fica com metade da altura
CONEXAO_DANO = 2.0          # soco e chute agachados batem o dobro
CONEXAO_DEFESA = 0.8        # agachado leva 20% menos dano (buff pedido pelo Gomes)
COLETE_DEFESA = 0.5         # ataque de média/longa distância tira metade
COLETE_DISTANCIA = 150      # mais longe que isso (em pixels) já conta como média distância


def ativas(l):
    """As habilidades que o lutador tem agora (a dele + a do oponente, se o Trafo mutou)."""
    hs = []
    for f in (l.f, getattr(l, "mutado", None)):
        if f and f.get("habilidade") and f["habilidade"] not in hs:
            hs.append(f["habilidade"])
    return hs


def ligada(l, h):
    """Se a habilidade está fazendo efeito neste momento (pra acender na tela)."""
    if h == "maquinario":
        return l.vida <= l.vida_max * MAQUINARIO_VIDA
    if h == "mutacao":
        return bool(getattr(l, "mutado", None))
    if h == "as_na_manga":
        return getattr(l, "as_ativo", 0) > 0
    if h == "poder_magico":
        return getattr(l, "invisivel", 0) > 0
    if h == "eletro":
        return l.extra.get("sente", 0) > 0
    if h == "natacao":
        return bool(l.extra.get("nadando"))
    if h == "frenesi":
        return bool(l.extra.get("frenesi"))
    if h == "cartas":
        return l.extra.get("cartas_n", 0) > 0
    if h == "coelho":
        return l.extra.get("coelho_espera", 0) <= 0
    if h == "furia_sumo":
        return getattr(l, "quadros", 0) < l.extra.get("furia_ate", -1)
    if h == "emboscada":
        return bool(l.extra.get("camuflado")) or l.extra.get("emboscada_id") is not None
    if h == "camuflagem":  # (KATCHADE)
        return bool(l.extra.get("camuflado")) or l.extra.get("camufla_id") is not None
    if h == "alquimia":  # (acende enquanto a poção de força/velocidade está fazendo efeito)
        return l.extra.get("pocao_forca", 0) > 0 or l.extra.get("pocao_veloz", 0) > 0
    if h == "ninja":  # (acende quando a SUBSTITUIÇÃO está pronta)
        return l.extra.get("subst_espera", 0) <= 0
    if h == "conexao":
        return l.estado == "agachado" or (l.estado == "ataque" and l.golpe and l.golpe.get("base") == "agachado")
    return True


def mult_causa(l, g):
    """Multiplica o dano que ESSE lutador causa."""
    m = 1.0
    hs = ativas(l)
    if "maquinario" in hs and ligada(l, "maquinario"):
        m *= MAQUINARIO_DANO
    if "conexao" in hs and g and g.get("base") == "agachado" and not g.get("especial"):
        m *= CONEXAO_DANO
    if "entendimento" in hs and l.extra.get("lobo_cor", "branco") == "branco":
        m *= LOBO_DANO  # ENTENDIMENTO MÚTUO: lobo branco = +dano
    if "frenesi" in hs and l.extra.get("frenesi"):
        m *= FRENESI_DANO  # FRENESI: dano x2
    if l.extra.get("pocao_forca", 0) > 0:  # ALQUIMIA (Finn): poção de força
        m *= POCAO_FORCA
    if "furia_sumo" in hs and getattr(l, "quadros", 0) < l.extra.get("furia_ate", -1):
        m *= FURIA_DANO  # FÚRIA DO SUMÔ (Tai)
    if l.extra.get("emboscada_id") is not None and l.extra.get("emboscada_id") == getattr(l, "golpe_id", -1):
        m *= EMBOSCADA_DANO  # EMBOSCADA (Tromos): o golpe que saiu da camuflagem
    if l.extra.get("camufla_id") is not None and l.extra.get("camufla_id") == getattr(l, "golpe_id", -1):
        import katchade
        m *= katchade.CAMUFLA_DANO  # CAMUFLAGEM (Katchade): o golpe que saiu da flor
    if "eletro" in hs:
        m *= padrao_caca(l, g)  # PADRÃO DE CAÇA (Sphyrus)
    if "eco" in hs:
        m *= ECO_MULT.get(l.extra.get("eco_nivel", "normal"), 1.0)  # ECOLOCALIZAÇÃO (Nocturnus)
    if "senso" in hs and l.extra.get("senso", "agudo") == "grave":
        m *= 1 + SENSO_PASSO * l.extra.get("senso_pilha", 0)  # SENSO GRAVE: +5% de dano por pilha
    if "jardim" in hs:  # JARDIM VIVO (Silvanus): +7% por armadilha no mapa
        m *= 1 + JARDIM_PASSO * len(l.extra.get("armadilhas") or ())
    return m


CACA_A_CADA = 2      # PADRÃO DE CAÇA (Sphyrus, ideia do Gomes): cada 2 vezes que um especial acerta...
CACA_PASSO = 0.10    # ...aquele especial fica 10% mais forte...
CACA_MAX = 0.50      # ...até +50%
_NOMES_GOLPES = {}


def _nome_golpe(g):
    """O nome do golpe (a chave dele no GOLPES), pra contar cada especial separado."""
    if id(g) not in _NOMES_GOLPES:
        from golpes import GOLPES
        _NOMES_GOLPES[id(g)] = next((n for n, v in GOLPES.items() if v is g), "?")
    return _NOMES_GOLPES[id(g)]


def padrao_caca(l, g):
    """PADRÃO DE CAÇA: devolve o multiplicador desse especial e conta mais um acerto dele.
    Conta por USO do golpe (um golpe de vários hits conta 1 vez); tiro conta pelo golpe do tiro (a onda de ar)."""
    if not g or not g.get("especial") or g.get("ultimate"):
        return 1.0
    nome = _nome_golpe(g)
    caca = l.extra.setdefault("caca", {})  # {nome do especial: [quantos acertos, id do último uso]}
    n, ultimo = caca.get(nome, [0, None])
    uso = getattr(l, "golpe_id", 0)
    ja = n - 1 if uso == ultimo else n  # (outro hit do MESMO uso vale igual o 1º hit dele)
    bonus = min(CACA_MAX, (ja // CACA_A_CADA) * CACA_PASSO)
    if uso != ultimo:  # um acerto NOVO desse especial
        caca[nome] = [n + 1, uso]
        if (n + 1) % CACA_A_CADA == 0 and (n + 1) // CACA_A_CADA * CACA_PASSO <= CACA_MAX + 1e-9:
            l.extra["sente"] = 20  # aprendeu o padrão: as linhas e os olhos acendem
    return 1 + bonus


FRENESI_DANO = 2.0
FRENESI_VEL = 1.3
AGUA_VEL = 1.1      # SPHYRUS: BÔNUS NA ÁGUA (cenário com água: um pouco mais rápido)


def mult_parry(l):
    """ELETRORRECEPÇÃO: sentiu o especial chegando = a janela do parry fica 2x."""
    return 2 if "eletro" in ativas(l) and l.extra.get("sente", 0) > 0 else 1


def sente_tudo(l):
    """ELETRORRECEPÇÃO: acerta (e vê) quem está invisível ou intangível."""
    return l is not None and "eletro" in ativas(l)


LOBO_DANO = 1.5  # (pedido do Gomes: lobo branco +50%)
LOBO_ATAQUE = 1.5   # lobo preto: os ataques andam 1,5x mais rápido (pedido do Gomes: ataque, não movimento)


def mult_vel(l):
    """Quanto mais rápido ele anda (CORPO ÁGIL: 20% mais; FRENESI: 30% mais; Sphyrus na água: 10% mais)."""
    hs = ativas(l)
    m = AGIL_VEL if "corpo_agil" in hs else 1.0
    if "frenesi" in hs and l.extra.get("frenesi"):
        m *= FRENESI_VEL
    if l.extra.get("agua"):
        m *= AGUA_VEL
    if l.extra.get("pocao_veloz", 0) > 0:  # ALQUIMIA (Finn): poção de velocidade
        m *= POCAO_VEL
    if "eco" in hs:
        m *= ECO_MULT.get(l.extra.get("eco_nivel", "normal"), 1.0)  # ECOLOCALIZAÇÃO (Nocturnus)
    if l.extra.get("neve_t", 0) > 0:  # NEVASCA (Frigantus): o gelo grudando deixa mais lento
        m *= 1 - NEVE_LENTO * l.extra.get("neve", 0)
    if l.extra.get("cicatriz"):  # CORTE VERTICAL (2ª ultimate do Katchade): mais lento até o fim da partida
        import katchade
        m *= katchade.CICATRIZ_VEL
    return m


NEVE_LENTO = 0.12   # cada golpe do Frigantus: 12% mais lento (até 3)
NEVE_TEMPO = 150    # quanto tempo o gelo fica grudado
NEVE_CONGELA = 60   # 3 golpes seguidos: congela 1 segundo


def nevasca(alvo):
    """Levou um golpe do Frigantus: o gelo gruda. 3 seguidos = CONGELA."""
    x = alvo.extra
    x["neve"] = (x.get("neve", 0) + 1) if x.get("neve_t", 0) > 0 else 1
    x["neve_t"] = NEVE_TEMPO
    if x["neve"] >= 3 and alvo.vida > 0 and alvo.estado == "golpeado":
        alvo.congelar(NEVE_CONGELA)
        x["neve"] = 0


def mult_ataque(l):
    """Quanto mais rápido os ataques dele rodam (ENTENDIMENTO MÚTUO: lobo preto)."""
    if "entendimento" in ativas(l) and l.extra.get("lobo_cor") == "preto":
        return LOBO_ATAQUE
    if "furia_sumo" in ativas(l):
        return TAI_ATAQUE  # (o Tai é LENTO nos ataques: pedido do Gomes)
    if "senso" in ativas(l) and l.extra.get("senso", "agudo") == "agudo" and l.extra.get("senso_pilha", 0) > 0:
        return 1 + SENSO_VEL_PASSO * l.extra["senso_pilha"]  # SENSO AGUDO: ataques mais rápidos
    return 1.0


TAI_ATAQUE = 0.8


def de_longe(l, atacante, g):
    """Golpe de média/longa distância: tiro, laser, bola, ou alguém batendo lá de longe."""
    if not g or g.get("transicao"):
        return False
    if g.get("proj") or g.get("ia") == "longe" or (atacante and atacante.feixe):
        return True
    return bool(atacante) and abs(atacante.x - l.x) > COLETE_DISTANCIA


def mult_recebe(l, atacante=None, g=None):
    """Multiplica o dano que ESSE lutador leva."""
    m = 1.0
    hs = ativas(l)
    if atacante is not None and atacante is not l and "vantagem" in ativas(atacante) and             (l.estado == "agachado" or (l.estado == "defendendo" and getattr(l, "agachado_def", False))):
        m *= VANTAGEM_DANO  # VANTAGEM POR CIMA (Silvanus): bateu em quem está AGACHADO
    if l.extra.get("cicatriz"):  # CORTE VERTICAL (Katchade): menos resistência até o fim da partida
        import katchade
        m *= katchade.CICATRIZ_DANO
    if "colete" in hs and atacante is not l and de_longe(l, atacante, g):
        m *= COLETE_DEFESA
    if "maquinario" in hs and ligada(l, "maquinario"):
        m *= MAQUINARIO_DEFESA
    if "conexao" in hs and (l.estado == "agachado" or (l.estado == "defendendo" and l.agachado_def)):
        m *= CONEXAO_DEFESA
    if "ninja" in hs and not l.no_chao():  # SAPO NINJA: no ar leva menos
        m *= SAPO_AR
    if "adaptacao" in hs and atacante is not None and atacante is not l and g is not None:
        m *= adaptar(l, atacante)
    if "planar" in hs and not l.no_chao():
        m *= PLANAR_DEFESA  # PLANAR (Nocturnus): lá em cima leva menos
    if "senso" in hs and atacante is not None and atacante is not l and g is not None and senso_pega(l, g):
        m *= SENSO_DEFESA  # SENSO AUDITIVO: o tipo de golpe que ele está "ouvindo" tira menos... e dá pilha
        x = l.extra
        x["senso_pilha"] = min(SENSO_MAX, x.get("senso_pilha", 0) + 1)
        x["senso_espera"] = SENSO_SOME
    if atacante is not None and atacante is not l and atacante.extra.get("poder_t", 0) > 0:
        aplicar_status(l, atacante.extra.get("poder_tipo", "veneno"))  # PODER SAMURAI de quem bateu
    if "furia_sumo" in hs and atacante is not None and atacante is not l and getattr(atacante, "combo", 0) >= FURIA_HITS:
        agora = getattr(l, "quadros", 0)
        if agora >= l.extra.get("furia_pronta", 0):  # levou o 5º golpe do combo: FÚRIA! (de vez em quando)
            l.extra["furia_ate"] = agora + FURIA_TEMPO
            l.extra["furia_pronta"] = agora + FURIA_RECARGA
    return m


ADAPTA_POR_GOLPE = 0.10   # ADAPTAÇÃO (Trafo): cada vez que um golpe acerta, 10% menos dele...
ADAPTA_MAX = 0.40         # ...até 40%


def adaptar(l, atacante):
    """ADAPTAÇÃO: devolve o multiplicador do dano DESSE golpe e conta mais uma vez que ele acertou.
    Conta por USO do golpe (um golpe de 10 hits conta 1 vez só, não 10)."""
    nome = atacante.nome_golpe or "?"
    vistos = l.extra.setdefault("adapta", {})  # {nome do golpe: [quantos usos, id do último uso]}
    n, ultimo = vistos.get(nome, [0, None])
    uso = getattr(atacante, "golpe_id", 0)
    if uso != ultimo:  # um USO novo desse golpe: conta mais um
        vistos[nome] = [n + 1, uso]
        if n < ADAPTA_MAX / ADAPTA_POR_GOLPE:  # se adaptou: o olho PISCA VERMELHO (mais forte quanto mais adaptado)
            l.extra["adapta_flash"] = 40
            l.extra["adapta_nivel"] = min(4, n + 1)
    else:              # (outro hit do mesmo uso: vale o mesmo que o 1º hit dele)
        n -= 1
    return 1 - min(ADAPTA_MAX, n * ADAPTA_POR_GOLPE)


AS_ESPERA = 15 * 60   # quadros até o ás acender
AS_DURA = 5 * 60      # quadros que ele fica aceso
AS_BONUS = 5          # dano a mais em cada ataque


def bonus_causa(l):
    """Dano A MAIS (somado) em cada ataque desse lutador."""
    b = AS_BONUS if "as_na_manga" in ativas(l) and ligada(l, "as_na_manga") else 0
    if l.extra.get("cacada", 0) > 0:  # CAÇADA NO ESCURO (2ª ultimate do Tromos): +5 por golpe
        b += CACADA_BONUS
    if l.extra.get("fornalha", 0) > 0:  # MODO FORNALHA (2ª ultimate do Magnus): cada golpe queima
        b += FORNALHA_BONUS
    return b


CACADA_BONUS = 5
FORNALHA_BONUS = 3
FORNALHA_PRENDE = 14


def relogio_as(l):
    """Ás na Manga: conta 15 s, acende por 5 s, apaga e conta de novo. Devolve True quando acende."""
    if "as_na_manga" not in ativas(l):
        return False
    if l.as_ativo > 0:
        l.as_ativo -= 1
        return False
    l.as_t += 1
    if l.as_t >= AS_ESPERA:
        l.as_t = 0
        l.as_ativo = AS_DURA
        return True
    return False


ACIDO_DANO = 1
ACIDO_PERTO = 140  # bateu mais perto que isso (golpe de perto, não tiro)


def queima_quem_bate(l, atacante, g):
    """SANGUE ÁCIDO: quem bate nele de perto (sem ser tiro) se queima."""
    if "sangue_acido" not in ativas(l) or not g or g.get("proj"):
        return False
    return abs(atacante.x - l.x) < ACIDO_PERTO


def limite_combo(l, padrao):
    return MAESTRIA_MALABAR if "maestria" in ativas(l) else padrao


def cadeia_extra(l):
    return MAESTRIA_CADEIA if "maestria" in ativas(l) else 0


PESO_LARGURA = 1.3  # o Tai é mais largo (mais fácil de acertar)


def largura(l):
    hs = ativas(l)
    if "corpo_agil" in hs:
        return AGIL_LARGURA
    return PESO_LARGURA if ("peso_pesado" in hs or "furia_sumo" in hs) else 1.0


def armadura(l, g):
    """PESO PESADO: soco e chute normais (não especiais) tiram vida, mas não fazem ele recuar."""
    return ("peso_pesado" in ativas(l) and g is not None and not g.get("especial") and l.no_chao()
            and l.estado not in ("caido", "voando", "agarrado", "tonto"))


def altura_agachado(l):
    return CONEXAO_AGACHADO if "conexao" in ativas(l) else 1.0


# =====================================================================
# SAPO NINJA (Rib, v2.x, pedido do Gomes: no lugar da POSTURA NINJA, que quase não fazia diferença)
#   PULO DE SAPO: pula 15% mais alto e tem PULO DUPLO (aperta pra cima de novo no ar)
#   no ar leva 20% menos dano
#   SUBSTITUIÇÃO: a cada 15 s, o próximo golpe que ia pegar nele acerta um TRONCO no lugar,
#                 e o Rib aparece ATRÁS de quem bateu (ultimate não dá pra substituir)
# =====================================================================
SAPO_PULO = 1.15
SAPO_PULO2 = 0.85      # o 2º pulo: 85% do pulo normal
SAPO_AR = 0.8
SUBST_RECARGA = 15 * 60    # (era 10 s: equilíbrio 19/10)
SUBST_INV = 20         # invencível um pouquinho depois de aparecer
TRONCO_TEMPO = 45


def sapo_quadro(l, jogo):
    """Todo quadro (o rib_todo_quadro chama): pulo alto, pulo duplo e os relógios da substituição."""
    if "ninja" not in ativas(l):
        return
    x = l.extra
    if x.get("subst_espera", 0) > 0:
        x["subst_espera"] -= 1
    if x.get("tronco"):
        tx, ty, tt, ts = x["tronco"]
        x["tronco"] = (tx, ty, tt - 1, ts) if tt > 1 else None
    if x.pop("puf", None):
        from max10 import fumaca
        fumaca(jogo, x["tronco"][0], x["tronco"][1] - 60 * l.s, 10, (220, 226, 236), 4, -1)
        fumaca(jogo, l.x, l.y - 60 * l.s, 8, (220, 226, 236), 4, -1)
    e = getattr(l, "entrada_atual", None)
    r = l.rel(e.dir) if e is not None else 5
    cima = r in (7, 8, 9)
    if l.no_chao():
        x["pulo2"] = x["subiu"] = False
    elif l.estado == "pulando":
        if not x.get("subiu") and l.vy < 0 and not l.perseguindo:  # o pulo de sapo: mais alto
            l.vy *= SAPO_PULO
            x["subiu"] = True
        if cima and not x.get("cima_antes") and not x.get("pulo2") and l.t >= 6 and not l.perseguindo:
            x["pulo2"] = True  # PULO DUPLO!
            l.vy = -l.f["pulo"] * SAPO_PULO2
            l.vx = {7: -1, 8: 0, 9: 1}[r] * 3.8 * l.dir
            l.ja_atacou = False
            from max10 import fumaca
            fumaca(jogo, l.x, l.y, 5, (200, 230, 200), 3, 0.5)
            import som
            som.tocar("pulo", 0.8)
    x["cima_antes"] = cima


def contra_samurai(l, g, atacante):
    """CONTRA-ATAQUE do INAZUMANEKO (Q): na janela da postura, o golpe (de perto: tiro não!) é desviado e ele revida.
    Devolve True se pegou (aí o golpe não acerta)."""
    if l.estado != "ataque" or l.nome_golpe != "inaz_contra" or "pegou" in l.memo:
        return False
    import inazumaneko
    if not (inazumaneko.C_INI <= l.t < inazumaneko.C_INI + inazumaneko.C_JANELA):
        return False
    if not g or g.get("proj") or g.get("ultimate") or g.get("ultimate2") or atacante is None or atacante is l:
        return False  # (não segura tiro nem ultimate: é o ponto fraco dele)
    l.memo["pegou"] = l.t
    l.inv = max(l.inv, 24)
    return True


def substituicao(l, g, atacante):
    """Chamado quando um golpe ia pegar nele: devolve True se ele SUBSTITUIU (o golpe pega no tronco)
    — ou se o INAZUMANEKO pegou no CONTRA-ATAQUE."""
    if contra_samurai(l, g, atacante):
        return True
    if l.estado == "ataque" and l.nome_golpe == "katch_reza":
        import katchade
        if katchade.reza_pega(l, g, atacante):  # POSTURA DE ORAÇÃO do KATCHADE
            return True
    if "ninja" not in ativas(l) or l.extra.get("subst_espera", 0) > 0 or l.vida <= 0:
        return False
    if not g or g.get("ultimate") or g.get("ultimate2") or atacante is None or atacante is l:
        return False
    if l.estado in ("caido", "voando", "agarrado") or getattr(l, "entrada_t", None) is not None:
        return False
    x = l.extra
    x["tronco"] = (l.x, l.y, TRONCO_TEMPO, l.s)  # (o l.s guarda a escala: o desenho é feito pequeno)
    x["puf"] = True
    x["subst_espera"] = SUBST_RECARGA
    atras = atacante.x - atacante.dir * 70 * atacante.s
    l.x = max(PAREDE_E, min(PAREDE_D, atras))
    l.dir = 1 if atacante.x > l.x else -1
    l.vx = 0
    l.inv = max(l.inv, SUBST_INV)
    if l.estado != "pulando":
        l.golpe = None
        l.mudar("parado")
    return True


# =====================================================================
# FINN (v2.x, pedido do Gomes: o PODER MÁGICO era fraco) — 2 passivas pra escolher com H na seleção:
#   ALQUIMIA        a cada 20 s bebe uma poção (sorteada): FORÇA +25% dano por 5 s, VELOCIDADE +25% por 5 s, CURA +8
#   FEITIÇO DE CURA a cada 5 golpes no mesmo combo (5º, 10º, 15º...): +5 de vida
# =====================================================================
POCAO_ESPERA = 16 * 60  # (era 20 s: buff do Gomes)
POCAO_TEMPO = 5 * 60
POCAO_FORCA = 1.25
POCAO_VEL = 1.25
POCAO_CURA = 8
POCOES = ("forca", "veloz", "cura")
COR_POCAO = {"forca": (230, 50, 40), "veloz": (60, 170, 255), "cura": (80, 220, 90)}
CURA_A_CADA = 5
CURA_VIDA = 5


def finn_quadro(l, jogo):
    """Todo quadro (o finn_todo_quadro chama): o relógio das poções e o feitiço de cura."""
    import random
    hs = ativas(l)
    x = l.extra
    for k in ("pocao_forca", "pocao_veloz", "bebendo"):
        if x.get(k, 0) > 0:
            x[k] -= 1
    if "alquimia" in hs and l.vida > 0:
        x["pocao_t"] = x.get("pocao_t", 0) + 1
        if x["pocao_t"] >= POCAO_ESPERA:
            x["pocao_t"] = 0
            tipo = random.choice(POCOES)  # (random da luta: igual nos dois PCs no online)
            x["pocao"], x["bebendo"] = tipo, 45
            if tipo == "forca":
                x["pocao_forca"] = POCAO_TEMPO
            elif tipo == "veloz":
                x["pocao_veloz"] = POCAO_TEMPO
            else:
                l.vida = min(l.vida_max, l.vida + POCAO_CURA)
            import som
            som.tocar("confirma", 0.5)
    if "cura" in hs and l.vida > 0:
        c = getattr(l, "combo", 0)
        ja = x.get("curou_ate", 0)
        if c <= 1:
            x["curou_ate"] = 0
        elif c // CURA_A_CADA > ja:  # chegou no 5º, 10º, 15º golpe do combo
            x["curou_ate"] = c // CURA_A_CADA
            l.vida = min(l.vida_max, l.vida + CURA_VIDA)
            x["curando"] = 30
            import som
            som.tocar("confirma", 0.4)
    if x.get("curando", 0) > 0:
        x["curando"] -= 1


# =====================================================================
# TROMOS (v2.x, pedido do Gomes: o SANGUE ÁCIDO era fraco) — 2 passivas pra escolher com H:
#   EMBOSCADA     parado 1,5 s fica CAMUFLADO (quase invisível, o CPU quase não vê);
#                 o 1º golpe que sai da camuflagem bate +50%
#   REGENERAÇÃO   toda vez que o adversário cai (derrubado): +5 de vida
# =====================================================================
EMBOSCADA_ESPERA = 90
EMBOSCADA_DANO = 1.5
CAMUFLA_ALFA = 20          # (usa o "invisível" do lutador: o vulto meio transparente)
REGENERA_VIDA = 6  # (era 5: buff do Gomes)


def tromos_quadro(l, jogo):
    hs = ativas(l)
    x = l.extra
    if "emboscada" in hs:
        parado = l.estado in ("parado", "agachado") and abs(l.vx) < 0.1 and l.no_chao()
        x["parado_t"] = x.get("parado_t", 0) + 1 if parado else 0
        if x["parado_t"] >= EMBOSCADA_ESPERA and l.vida > 0:
            if not x.get("camuflado"):
                import som
                som.tocar("vento", 0.3)
            x["camuflado"] = True
            l.invisivel = max(l.invisivel, CAMUFLA_ALFA)
        if x.get("camuflado") and l.estado == "ataque":  # saiu da camuflagem ATACANDO: esse golpe é a emboscada
            x["emboscada_id"] = l.golpe_id
            x["camuflado"] = False
        elif x.get("camuflado") and not parado:
            x["camuflado"] = False
        if x.get("emboscada_id") is not None and (l.estado != "ataque" or l.golpe_id != x["emboscada_id"]):
            x["emboscada_id"] = None  # (o golpe da emboscada acabou)
    if "regeneracao" in hs:
        outro = next((o for o in getattr(jogo, "L", ()) if o is not l), None)
        caiu = outro is not None and outro.estado == "caido"
        if caiu and not x.get("outro_caido") and l.vida > 0:
            l.vida = min(l.vida_max, l.vida + REGENERA_VIDA)
            x["regenerou"] = 30
        x["outro_caido"] = caiu
        if x.get("regenerou", 0) > 0:
            x["regenerou"] -= 1


# =====================================================================
# TAI (v2.x, pedido do Gomes): FÚRIA DO SUMÔ no lugar do PESO PESADO (ele era o mais forte do jogo)
#   levou o 5º golpe do mesmo combo: +25% de dano por 5 s; depois disso, 15 s até poder de novo
#   (continua largo: a hitbox de "peso pesado"; os 120 de vida são da ficha)
# =====================================================================
FURIA_HITS = 5
FURIA_DANO = 1.25
FURIA_TEMPO = 5 * 60
FURIA_RECARGA = 15 * 60



# =====================================================================
# JOHN (v2.x, pedido do Gomes: o ABRACADABRA era fraco) — 2 passivas pra escolher com H:
#   TRUQUE DE CARTAS  cada golpe dele que ACERTA marca 1 carta no adversário; com 3 cartas, elas EXPLODEM (10)
#   COELHO AJUDANTE   a cada 8 s o coelhinho do lado dele: MORDE quem chega perto (5) ou PULA NA FRENTE de um tiro
# =====================================================================
CARTAS_EXPLODE = 3
CARTAS_DANO = 10
COELHO_ESPERA = 8 * 60
COELHO_MORDE = 5
COELHO_PERTO = 120
COELHO_ANIM = 24
GOLPE_CARTAS = dict(dano=CARTAS_DANO, nivel="medio", especial=True, hit=0, defe=0, emp=0)
GOLPE_COELHO = dict(dano=COELHO_MORDE, nivel="medio", especial=True, hit=0, defe=0, emp=0)


def john_quadro(l, jogo):
    import som
    hs = ativas(l)
    x = l.extra
    outro = next((o for o in getattr(jogo, "L", ()) if o is not l), None)
    if outro is None:
        return
    if x.get("coelho_anim", 0) > 0:
        x["coelho_anim"] -= 1
    x["tela_toda"] = bool(x.get("cartas_n")) or x.get("coelho_anim", 0) > 0
    if "cartas" in hs:
        x["cartas_alvo"] = (outro.x, outro.y - 70 * outro.s)
        g = l.golpe if l.estado == "ataque" and l.golpe else None
        combo = getattr(l, "combo", 0)
        novos = combo - x.get("combo_antes", 0) if combo > x.get("combo_antes", 0) else 0
        x["combo_antes"] = combo  # (cada golpe que acerta sobe o combo, inclusive tiro e golpe de vários hits)
        ult = bool(g and (g.get("ultimate") or g.get("ultimate2")))
        for _ in range(novos if not ult else 0):
            x["cartas_n"] = x.get("cartas_n", 0) + 1
            if x["cartas_n"] >= CARTAS_EXPLODE:  # BUM!
                x["cartas_n"] = 0
                if outro.vida > 0:
                    outro.levar(CARTAS_DANO, l, GOLPE_CARTAS)
                    outro.tremor_hit = max(outro.tremor_hit, 8)
                    jogo.faisca(outro.x, outro.y - 70 * outro.s, False, True)
                    som.tocar("explosao", 0.6)
    if "coelho" in hs:
        if x.get("coelho_espera", 0) > 0:
            x["coelho_espera"] -= 1
            return
        if l.vida <= 0:
            return
        meu = l.x + l.dir * 30 * l.s
        for pr in getattr(jogo, "projeteis", ()):  # um TIRO chegando: o coelho pula na frente
            if pr.vivo and pr.dono is not l and abs(pr.x - meu) < 70 * l.s and (pr.x - l.x) * (getattr(pr, "vx", 0) or 0) < 0:
                pr.vivo = False
                x.update(coelho_espera=COELHO_ESPERA, coelho_anim=COELHO_ANIM, coelho_onde=(pr.x, CHAO),
                         coelho_dir=l.dir)
                jogo.faisca(pr.x, pr.y, True, False)
                som.tocar("puf", 0.6)
                return
        perto = abs(outro.x - l.x) < COELHO_PERTO * l.s / 1.36
        if perto and outro.vida > 0 and outro.estado not in ("defendendo", "caido", "agarrado") and outro.inv <= 0 \
                and not outro.extra.get("intangivel"):  # o coelho MORDE
            outro.levar(COELHO_MORDE, l, GOLPE_COELHO)
            outro.tremor_hit = max(outro.tremor_hit, 6)
            x.update(coelho_espera=COELHO_ESPERA, coelho_anim=COELHO_ANIM, coelho_onde=(outro.x - l.dir * 14 * l.s, CHAO),
                     coelho_dir=l.dir)
            jogo.faisca(outro.x, outro.y - 40 * outro.s, False, False)
            som.tocar("soco", 0.6)


# =====================================================================
# INAZUMANEKO (v3.0, ideia do Gomes) — 2 passivas pra escolher com H na seleção:
#   FÚRIA SAMURAI  o adversário deu PARRY nele: ultimate +8%; o CONTRA-ATAQUE dele (Q) acertou: +5%
#   PODER SAMURAI  ficou 3 s parado: por 3 s os golpes dão um STATUS sorteado (a katana brilha na cor):
#                  VENENO (1/s por 4 s), FOGO (2/s por 2 s), RAIO (trava 0,3 s) ou GELO (mais lento 2 s)
# =====================================================================
FURIA_PARRY = 0.08
FURIA_CONTRA = 0.05
PODER_PARADO = 3 * 60
PODER_TEMPO = 3 * 60
STATUS = ("veneno", "fogo", "raio", "gelo")
COR_STATUS = {"veneno": (110, 220, 80), "fogo": (255, 140, 40), "raio": (255, 230, 80), "gelo": (140, 210, 255)}
VENENO_TEMPO, VENENO_CADA = 4 * 60, 60     # 1 de dano por segundo, 4 s
FOGO_TEMPO, FOGO_CADA = 2 * 60, 30         # 2 por segundo, 2 s
RAIO_TRAVA = 18                            # 0,3 s travado
GELO_TEMPO, GELO_NIVEL = 2 * 60, 2         # 2 s mais lento (usa o "gelo grudado" da Nevasca)


def furia_samurai(l, quanto):
    """FÚRIA SAMURAI: enche a ultimate (quanto = fração da barra azul)."""
    if "furia_samurai" in ativas(l):
        from config import BARRA_MAX
        l.encher(BARRA_MAX * quanto)
        l.extra["furia_flash"] = 30


def aplicar_status(alvo, tipo):
    """PODER SAMURAI: o golpe deixou um status no alvo."""
    x = alvo.extra
    if tipo == "veneno":
        x["veneno_t"] = VENENO_TEMPO
    elif tipo == "fogo":
        x["fogo_t"] = FOGO_TEMPO
    elif tipo == "raio":
        x["raio_t"] = RAIO_TRAVA
    elif tipo == "gelo":
        x["neve"] = max(x.get("neve", 0), GELO_NIVEL) if x.get("neve_t", 0) > 0 else GELO_NIVEL
        x["neve_t"] = max(x.get("neve_t", 0), GELO_TEMPO)


def samurai_quadro(l, jogo):
    """Todo quadro (o inazumaneko.todo_quadro chama): a Fúria percebendo o parry, o Poder carregando
    e os status correndo em quem levou."""
    import random
    hs = ativas(l)
    x = l.extra
    outro = jogo.L[1] if jogo.L[0] is l else jogo.L[0]
    if x.get("furia_flash", 0) > 0:
        x["furia_flash"] -= 1
    # FÚRIA SAMURAI: o adversário acabou de dar parry (o brilho do parry acendeu)
    brilho = getattr(outro, "parry_brilho", 0)
    if brilho > x.get("parry_antes", 0):
        furia_samurai(l, FURIA_PARRY)
    x["parry_antes"] = brilho
    # PODER SAMURAI: parado 3 s -> acende por 3 s
    if x.get("poder_t", 0) > 0:
        x["poder_t"] -= 1
        x["parado_t"] = 0
    elif "poder_samurai" in hs and l.vida > 0:
        parado = l.estado in ("parado", "defendendo") and abs(l.vx) < 0.1 and l.no_chao()
        x["parado_t"] = x.get("parado_t", 0) + 1 if parado else 0
        if x["parado_t"] >= PODER_PARADO:
            x["parado_t"] = 0
            x["poder_t"] = PODER_TEMPO
            x["poder_tipo"] = random.choice(STATUS)  # (random da luta: igual nos dois PCs no online)
            import som
            som.tocar("confirma", 0.5)
    # os STATUS no adversário (quem bateu é quem cuida do relógio)
    o = outro.extra
    if o.get("veneno_t", 0) > 0:
        o["veneno_t"] -= 1
        if o["veneno_t"] % VENENO_CADA == 0 and outro.vida > 1:
            outro.vida = max(1, outro.vida - 1)  # (veneno não nocauteia sozinho)
    if o.get("fogo_t", 0) > 0:
        o["fogo_t"] -= 1
        if o["fogo_t"] % FOGO_CADA == 0 and outro.vida > 1:
            outro.vida = max(1, outro.vida - 1)
    if o.get("raio_t", 0) > 0:
        if outro.estado in ("parado", "andando", "agachado", "defendendo") and outro.vida > 0:
            outro.mudar("tonto")
            outro.golpe = None
            outro.tonto_tempo = o["raio_t"]
            outro.paralisado = True
        o["raio_t"] = 0


# =====================================================================
# NOCTURNUS (v3.0, ideias do Gomes) — 3 passivas pra escolher com H:
#   ECOLOCALIZAÇÃO  o adversário se mexe MUITO: +50% velocidade e força; normal: nada; mexe POUCO: -25%
#   PLANAR          no ar cai devagar (plana) e leva 25% menos lá em cima
#   SENSO AUDITIVO  X troca: AGUDO (golpes leves, aéreos ou de vários hits) / GRAVE (pesados, agachados ou dash):
#                   esse tipo tira 15% menos dele e cada um que acerta dá 1 pilha (até 5; some 5 s sem apanhar):
#                   AGUDO = +3% de RAPIDEZ por pilha, GRAVE = +5% de DANO por pilha (equilíbrio 21/10, escolha do Gomes)
#   + os efeitos que ele causa (controles trocados, cego, enjoo, sono) — o relógio deles roda aqui
# =====================================================================
ECO_MULT = {"muito": 1.5, "pouco": 0.75}
ECO_MUITO, ECO_POUCO = 2.5, 0.6    # (média de quanto o adversário anda por quadro)
PLANAR_QUEDA, PLANAR_DEFESA = 3.0, 0.75
SENSO_DEFESA, SENSO_PASSO, SENSO_MAX, SENSO_SOME = 0.85, 0.05, 5, 5 * 60  # (equilíbrio 21/10: o Gomes escolheu)
CEGO_CPU_BATE = 8  # (o computador cego: a cada 8 quadros os morcegos dele saem 1 leva; uns 2,5 s no total)
SENSO_VEL_PASSO = 0.03  # (AGUDO: velocidade de ataque por pilha; o GRAVE usa o SENSO_PASSO no dano)


def senso_pega(l, g):
    """O golpe é do tipo que o SENSO AUDITIVO está ouvindo agora?"""
    if l.extra.get("senso", "agudo") == "agudo":
        return (not g.get("especial") and g.get("dano", 0) <= 6) or bool(g.get("aereo"))             or len(g.get("janelas", ())) > 1 or bool(g.get("varios"))
    return (g.get("dano", 0) >= 10 and not g.get("proj")) or g.get("base") == "agachado" or g.get("ia") == "medio"


def finta(l, e):
    """ENGANADOR SELVAGEM (Silvanus, ideia do Gomes): depois do X, o próximo ataque é FALSO — só a animação começa
    (0,5 s, sem dano) — e apertar OUTRO ataque no meio troca pelo golpe de verdade."""
    x = l.extra
    botao = "soco" if e.soco else "chute" if e.chute else e.especial
    aperta = botao is not None and botao != x.get("finta_prev")
    x["finta_prev"] = botao
    if l.estado == "ataque" and l.nome_golpe == "silv_finta":
        if aperta and botao != x.get("finta_botao"):  # TROCOU: sai da finta e o golpe de verdade começa agora
            l.golpe = l.nome_golpe = None
            l.sobrepor = {}
            l.mudar("parado")
            return e
        return e
    if x.get("finta_armada", 0) > 0 and aperta and l.estado in ("parado", "andando", "agachado") and l.no_chao():
        from golpes import GOLPES
        nome = botao if botao in ("soco", "chute") else l.golpe_do_botao(botao)
        if nome and not GOLPES.get(nome, {}).get("ultimate"):
            x["finta_armada"] = 0
            x["finta_espera"] = FINTA_ESPERA
            x["finta_de"], x["finta_botao"] = nome, botao
            l.comecar("silv_finta")
            import copy
            e = copy.copy(e)
            e.soco = e.chute = False
            e.especial = None
    return e


def trocar_controles(l, e):
    """CONTROLES TROCADOS (a Bola de Eco do Nocturnus): soco<->chute, E->Q->R->E, SHIFT<->Z, cima<->baixo,
    frente<->trás. O lutador.update chama isso antes de usar a entrada."""
    if e is None:
        return e
    if "enganador" in ativas(l):
        e = finta(l, e)
    if l.extra.get("cego_cpu"):  # o COMPUTADOR CEGO (tela lotada de morcegos): fica PERDIDO — não anda, não defende,
        import copy                # não ataca (os morcegos vão saindo sozinhos: nocturnus.morcegos_tela_quadro)
        e = copy.copy(e)
        e.dir, e.especial, e.barra, e.soco, e.chute = 5, None, False, False, False
    if l.extra.get("trocado_t", 0) <= 0:
        return e
    import copy
    n = copy.copy(e)
    n.soco, n.chute = e.chute, e.soco
    n.especial = {"E": "Q", "Q": "R", "R": "E", "SHIFT": "Z", "Z": "SHIFT"}.get(e.especial, e.especial)
    troca_dir = {1: 9, 2: 8, 3: 7, 4: 6, 6: 4, 7: 3, 8: 2, 9: 1}
    n.dir = troca_dir.get(e.dir, e.dir)
    return n


def nocturnus_quadro(l, jogo):
    """Todo quadro (o nocturnus.todo_quadro chama): a Ecolocalização medindo o adversário, o Planar, o Senso
    perdendo as pilhas e o relógio dos efeitos no adversário."""
    hs = ativas(l)
    x = l.extra
    outro = jogo.L[1] if jogo.L[0] is l else jogo.L[0]
    if x.get("senso_flash", 0) > 0:
        x["senso_flash"] -= 1
    # ECOLOCALIZAÇÃO: quanto o adversário anda (média)
    x["eco_mexe"] = x.get("eco_mexe", 1.8) * 0.985 + (abs(outro.vx) + (2 if not outro.no_chao() else 0)) * 0.015
    if "eco" in hs:
        x["eco_nivel"] = "muito" if x["eco_mexe"] > ECO_MUITO else "pouco" if x["eco_mexe"] < ECO_POUCO else "normal"
    # PLANAR: caindo devagar
    if "planar" in hs and not l.no_chao() and l.estado == "pulando" and l.vy > PLANAR_QUEDA:
        l.vy = PLANAR_QUEDA
    # SENSO AUDITIVO: as pilhas somem se ficar 5 s sem apanhar
    if x.get("senso_espera", 0) > 0:
        x["senso_espera"] -= 1
        if x["senso_espera"] == 0:
            x["senso_pilha"] = 0
    # os efeitos no adversário
    o = outro.extra
    for k in ("trocado_t", "cego_t", "enjoo_t", "dormindo_t"):
        if o.get(k, 0) > 0:
            o[k] -= 1
    if o.get("tonto_extra", 0) > 0:  # (o efeito TONTO da ultimate: quando a paralisia acaba, ainda fica tonto)
        o["tonto_extra"] -= 1
        if outro.estado in ("parado", "andando") and outro.vida > 0 and o["tonto_extra"] > 30:
            outro.mudar("tonto")
            outro.tonto_tempo = 60
            o["tonto_extra"] = 0
    if o.get("dormindo_t", 0) > 0 and outro.estado != "tonto":
        o["dormindo_t"] = 0  # (acordou)

