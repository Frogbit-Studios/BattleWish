"""Falas antes da luta (na tela de VS), estilo Injustice 2.
Cada dupla tem 2 ou 3 conversas ([(quem fala, o que fala), ...]) e sorteia uma a cada luta."""
import random

CONVERSAS = {
    ("MAX-10", "RIB"): [("MAX-10", "ANALISANDO... ALVO: SAPO. AMEAÇA: BAIXA."),
                        ("RIB", "Ameaça baixa? Seu sensor tá precisando de óleo, lata velha!")],
    ("MAX-10", "TRAFO"): [("TRAFO", "Grrr... você tem cheiro de ferro-velho!"),
                          ("MAX-10", "OBRIGADO. É O MEU PERFUME FAVORITO.")],
    ("KING RIP", "MAX-10"): [("KING RIP", "Na minha época, robô só servia pra lavar louça."),
                             ("MAX-10", "ATUALIZAÇÃO: AGORA EU TAMBÉM LIMPO O CHÃO. COM VOCÊ.")],
    ("CANNAN", "MAX-10"): [("CANNAN", "Já desmontei tanque maior que você, lataria."),
                           ("MAX-10", "MEUS CÁLCULOS DISCORDAM. INICIANDO COMBATE.")],
    ("RIB", "TRAFO"): [("RIB", "Um cachorro amarelo que rosna? Agora eu já vi de tudo."),
                       ("TRAFO", "Grrr... e eu nunca provei sapo... ainda.")],
    ("KING RIP", "RIB"): [("KING RIP", "Um ninja? Mostre o que o seu mestre te ensinou, garoto."),
                          ("RIB", "Meu vô me ensinou a respeitar os mais velhos... mas hoje vai ser difícil!")],
    ("CANNAN", "RIB"): [("CANNAN", "Fica parado, sapo. Assim fica mais fácil mirar."),
                        ("RIB", "Ninja não fica parado. Ninja SOME!")],
    ("KING RIP", "TRAFO"): [("KING RIP", "Senta! Fica! ...Ele não obedece."),
                            ("TRAFO", "AU! Eu só obedeço a minha matilha!")],
    ("CANNAN", "TRAFO"): [("CANNAN", "Na guerra eu tinha um cachorro. Ele tinha quatro patas."),
                          ("TRAFO", "Grrr... eu tenho seis. Faz as contas, soldado!")],
    ("FINN", "MAX-10"): [("FINN", "Uma armadura que anda sozinha? Que feitiço é esse?"),
                         ("MAX-10", "NÃO É FEITIÇO. É CIÊNCIA.")],
    ("FINN", "RIB"): [("RIB", "Um velho de chapéu pontudo? Meu vô tinha um igualzinho!"),
                      ("FINN", "Então o seu avô tinha bom gosto, pequeno sapo.")],
    ("FINN", "TRAFO"): [("FINN", "Uma fera mutante... daria um ótimo ingrediente de poção."),
                        ("TRAFO", "Grrr... chega perto que eu te mostro o ingrediente!")],
    ("FINN", "KING RIP"): [("KING RIP", "Barba branca, cajado... você também é dos antigos, hein?"),
                           ("FINN", "Antigo não. CLÁSSICO, meu caro.")],
    ("CANNAN", "FINN"): [("CANNAN", "Magia não segura bala, vovô."),
                         ("FINN", "Você nunca viu uma bala derreter, não é?")],
    ("KUN", "MAX-10"): [("KUN", "Aposto que você não sabe jogar truco, robô."),
                        ("MAX-10", "PROBABILIDADE DE VOCÊ VENCER: 2%.")],
    ("KUN", "RIB"): [("RIB", "Cartas? Eu jogo shuriken, que é a mesma coisa só que melhor!"),
                     ("KUN", "Shuriken não sai pela manga, sapinho.")],
    ("KUN", "TRAFO"): [("KUN", "Cachorro bonzinho... quer pegar a carta?"),
                       ("TRAFO", "GRRR! Não me trata que nem cachorro de estimação!")],
    ("KING RIP", "KUN"): [("KING RIP", "Na minha época, carta servia pra jogar com a família."),
                          ("KUN", "E hoje serve pra derrubar velhinho de nunchaku.")],
    ("CANNAN", "KUN"): [("CANNAN", "Carta de baralho contra um canhão? Desiste, garoto."),
                        ("KUN", "Ainda tenho um ás na manga. Literalmente.")],
    ("FINN", "KUN"): [("FINN", "Truques de cartas... isso é magia de criança."),
                      ("KUN", "Pelo menos a minha magia tira um sofá do nada, vovô.")],
    ("MAX-10", "TROMOS"): [("MAX-10", "FORMA DE VIDA DESCONHECIDA. NÍVEL DE AMEAÇA: MÁXIMO."),
                              ("TROMOS", "Hssssssss...")],
    ("RIB", "TROMOS"): [("RIB", "Que bicho é esse?! Por que ele tem DUAS bocas?!"),
                           ("TROMOS", "*GRRRK*")],
    ("TRAFO", "TROMOS"): [("TRAFO", "Grrr... sai daqui, coisa estranha!"),
                             ("TROMOS", "HSSSSSSSS!")],
    ("KING RIP", "TROMOS"): [("TROMOS", "Hssss..."),
                                ("KING RIP", "Na minha época os monstros ficavam só nos filmes.")],
    ("CANNAN", "TROMOS"): [("CANNAN", "Eu já enfrentei um de vocês. Dessa vez eu trouxe o canhão."),
                              ("TROMOS", "*KREEEEEE*")],
    ("FINN", "TROMOS"): [("FINN", "Criatura das trevas! Volte pro buraco de onde saiu!"),
                            ("TROMOS", "*KRRRAAAH!*")],
    ("KUN", "TROMOS"): [("KUN", "Ok... essa carta eu não tinha no baralho."),
                           ("TROMOS", "*clic-clic-clic*")],
    ("MAX-10", "TAI"): [("TAI", "Você é pesado, robô. Mas eu sou mais."),
                        ("MAX-10", "CALCULANDO SUA FORÇA... ERRO: NÚMERO GRANDE DEMAIS.")],
    ("RIB", "TAI"): [("RIB", "Nossa... você é GIGANTE!"),
                     ("TAI", "E você é pequeno o bastante pra caber na minha mão.")],
    ("TAI", "TRAFO"): [("TRAFO", "Grrr... sumô é só empurrar? Eu empurro com o focinho!"),
                       ("TAI", "Então vem. O meu círculo está te esperando.")],
    ("KING RIP", "TAI"): [("KING RIP", "Na minha época eu também era grandão assim."),
                          ("TAI", "Então hoje o senhor vai lembrar como é ser derrubado.")],
    ("CANNAN", "TAI"): [("CANNAN", "Esse colete aguenta muita coisa... será que aguenta você?"),
                        ("TAI", "Vamos descobrir. Segura firme, soldado.")],
    ("FINN", "TAI"): [("FINN", "Hm... acho que minha levitação não levanta tanto peso."),
                      ("TAI", "Ninguém levanta, velho mago.")],
    ("KUN", "TAI"): [("KUN", "Tenho um armário inteiro guardado nessa carta."),
                     ("TAI", "Pode jogar. Eu seguro.")],
    ("TAI", "TROMOS"): [("TROMOS", "Hssssss..."),
                           ("TAI", "Monstro estranho. Mas no meu ringue, quem empurra sou eu.")],
    ("MAX-10", "TAMER"): [("TAMER", "Já domei bicho mais bravo que um robô."),
                          ("MAX-10", "ANIMAL DETECTADO. ADESTRADOR TAMBÉM.")],
    ("RIB", "TAMER"): [("RIB", "Sai pra lá com esse cachorrão!"),
                       ("TAMER", "É um LOBO. E ele adora sapo.")],
    ("TAMER", "TRAFO"): [("TRAFO", "Grrr... um lobo branco? Esse aí é o meu rival!"),
                         ("TAMER", "Ele não briga com qualquer um. Primeiro passa por mim.")],
    ("KING RIP", "TAMER"): [("KING RIP", "Lutar com ajuda de bicho? Na minha época isso era trapaça."),
                            ("TAMER", "Na selva, isso se chama trabalho em equipe.")],
    ("CANNAN", "TAMER"): [("CANNAN", "Sobreviver na selva? Eu sobrevivi a uma guerra."),
                          ("TAMER", "Então vamos ver quem aguenta mais, soldado.")],
    ("FINN", "TAMER"): [("FINN", "Que lobo magnífico... será que ele aprende uma magia?"),
                        ("TAMER", "Ele já faz mágica: faz gente sumir da arena.")],
    ("KUN", "TAMER"): [("KUN", "Escolhe uma carta, lobinho."),
                       ("TAMER", "Ele só escolhe uma coisa: a sua perna.")],
    ("TAI", "TAMER"): [("TAMER", "Você é grande... mas eu já vi urso maior."),
                       ("TAI", "Urso nenhum sabe sumô.")],
    ("TAMER", "TROMOS"): [("TAMER", "Nunca vi esse bicho em nenhum documentário..."),
                             ("TROMOS", "*snif... snif...*")],
    ("CANNAN", "KING RIP"): [("KING RIP", "Arma de fogo? Isso é coisa de quem não sabe lutar."),
                             ("CANNAN", "E nunchaku é coisa de quem não sabe mirar, vovô.")],
    # ---- JOHN, o mágico (v2.x) ----
    ("CANNAN", "JOHN"): [("JOHN", "Respeitável público! O soldado vai sumir com um estalar de dedos!"),
                         ("CANNAN", "Some você. Eu só preciso de um tiro.")],
    ("FINN", "JOHN"): [("FINN", "Truques de palco... isso não é magia de verdade, rapaz."),
                       ("JOHN", "Magia de verdade não lota teatro, vovô!")],
    ("JOHN", "KING RIP"): [("KING RIP", "Na minha época, mágico só tirava moeda da orelha."),
                           ("JOHN", "Hoje eu tiro um crocodilo da cartola. Evoluímos!")],
    ("JOHN", "KUN"): [("KUN", "Cartas contra cartola? Vai ser truque contra truque."),
                      ("JOHN", "Então que vença o melhor show!")],
    ("JOHN", "MAX-10"): [("JOHN", "Um robô! Para o meu próximo truque, vou desligar você."),
                         ("MAX-10", "TRUQUE NÃO ENCONTRADO NO MEU SISTEMA.")],
    ("JOHN", "RIB"): [("RIB", "Ninja também some, sabia? Kawarimi!"),
                      ("JOHN", "Bonito! Mas a minha fumaça é roxa.")],
    ("JOHN", "TAI"): [("JOHN", "Respeitável público! Vou levantar o lutador mais forte da arena!"),
                      ("TAI", "Pode tentar. Ninguém conseguiu até hoje.")],
    ("JOHN", "TAMER"): [("TAMER", "Um coelho saindo da cartola... o garoto vai adorar."),
                        ("JOHN", "Ei! O coelho é artista, não é lanche!")],
    ("JOHN", "TRAFO"): [("TRAFO", "Grrr... cheiro de coelho! Cadê ele?"),
                        ("JOHN", "Na cartola. E ele é bem maior que você!")],
    ("JOHN", "TROMOS"): [("JOHN", "E agora, tirando da cartola... um... coelho?"),
                            ("TROMOS", "*KREEEEEE*")],
}

# mais conversas (v2.0, pedido do Gomes: cada dupla tem 2-3 e sorteia uma a cada luta)
MAIS = {
    ("MAX-10", "RIB"): [
        [("RIB", "Ei, robô! Sabia que sapo pula mais alto que lata?"),
         ("MAX-10", "TESTE DE SALTO AGENDADO. VOCÊ VAI VOAR.")],
        [("MAX-10", "UMIDADE DETECTADA. RISCO DE FERRUGEM."),
         ("RIB", "Relaxa, quem vai enferrujar hoje é o seu orgulho!")]],
    ("MAX-10", "TRAFO"): [
        [("TRAFO", "GRRR! Vou roer você igual um osso!"),
         ("MAX-10", "AVISO: ESTE OSSO É DE AÇO.")],
        [("MAX-10", "VOCÊ JÁ VIROU UM MAX-10 UMA VEZ. CÓPIA NÃO AUTORIZADA."),
         ("TRAFO", "E vou virar de novo! AUUUU!")]],
    ("KING RIP", "MAX-10"): [
        [("MAX-10", "IDADE DO OPONENTE: MUITO VELHO."),
         ("KING RIP", "Velho é o seu sistema operacional, rapaz.")],
        [("KING RIP", "Meu nunchaku já quebrou coisa mais dura que você."),
         ("MAX-10", "IMPOSSÍVEL. EU SOU A COISA MAIS DURA DA ARENA.")]],
    ("CANNAN", "MAX-10"): [
        [("MAX-10", "SOLDADO HUMANO. PEÇAS DE REPOSIÇÃO: NENHUMA."),
         ("CANNAN", "Não preciso de peça. Preciso de munição.")],
        [("CANNAN", "No quartel, robô a gente desligava na tomada."),
         ("MAX-10", "EU NÃO TENHO TOMADA. TENHO PUNHOS.")]],
    ("FINN", "MAX-10"): [
        [("FINN", "Será que um feitiço de ferrugem funciona em você?"),
         ("MAX-10", "ANTIVÍRUS ATUALIZADO. ANTIFEITIÇO TAMBÉM.")],
        [("MAX-10", "MAGIA NÃO CONSTA NO MEU BANCO DE DADOS."),
         ("FINN", "Então anote aí, latinha: MINI SOL.")]],
    ("KUN", "MAX-10"): [
        [("MAX-10", "CALCULANDO TODAS AS CARTAS DO BARALHO... PRONTO."),
         ("KUN", "Só faltou a que tá na minha manga.")],
        [("KUN", "Robô não sabe blefar, né? Que sem graça."),
         ("MAX-10", "EU NÃO BLEFO. EU ACERTO.")]],
    ("MAX-10", "TROMOS"): [
        [("TROMOS", "*KREEEEEE*"),
         ("MAX-10", "SOM IRRITANTE DETECTADO. DESLIGANDO OS OUVIDOS.")],
        [("MAX-10", "SANGUE ÁCIDO DETECTADO. VOU BATER DE LUVA."),
         ("TROMOS", "*baba ácida pingando*")]],
    ("MAX-10", "TAI"): [
        [("MAX-10", "MODO EMPURRÃO ATIVADO."),
         ("TAI", "Empurrar é a minha especialidade, lata.")],
        [("TAI", "No meu ringue, quem sai do círculo perde."),
         ("MAX-10", "ENTENDIDO. VOCÊ VAI SAIR VOANDO DO CÍRCULO.")]],
    ("MAX-10", "TAMER"): [
        [("MAX-10", "LOBO DETECTADO. ADICIONANDO À LISTA DE ALVOS."),
         ("TAMER", "Mexe com ele e você mexe comigo.")],
        [("TAMER", "Pega, garoto! Esse aí é de lata!"),
         ("MAX-10", "ALERTA: CACHORRO MORDENDO A MINHA PERNA.")]],
    ("RIB", "TRAFO"): [
        [("TRAFO", "Grrr... sapo é rápido, mas cachorro fareja!"),
         ("RIB", "Fareja isso aqui então: SHURIKEN!")],
        [("RIB", "Senta! Dá a pata! ...Qual das seis?"),
         ("TRAFO", "GRRR! TODAS! Na sua cara!")]],
    ("KING RIP", "RIB"): [
        [("RIB", "Vovô, o senhor não devia estar descansando?"),
         ("KING RIP", "Descansar é pra quem perde, sapinho.")],
        [("KING RIP", "Bonito esse cachecol. Pena que vai ficar sujo."),
         ("RIB", "Ninguém encosta no meu cachecol!")]],
    ("CANNAN", "RIB"): [
        [("RIB", "Sabia que eu desvio de bala?"),
         ("CANNAN", "Sabia que eu tenho MUITAS balas?")],
        [("CANNAN", "Missão no pântano de novo... odeio pântano."),
         ("RIB", "Então bem-vindo à MINHA casa!")]],
    ("FINN", "RIB"): [
        [("FINN", "Um sapo ninja! Que transformação curiosa..."),
         ("RIB", "Não sou príncipe encantado não, vovô!")],
        [("RIB", "Aposto que eu sou mais rápido que o seu feitiço!"),
         ("FINN", "Ninguém é mais rápido que uma bola de fogo, pequeno.")]],
    ("KUN", "RIB"): [
        [("KUN", "Duvido você pegar uma carta no ar."),
         ("RIB", "Duvido você pegar UM sapo no ar!")],
        [("RIB", "Eu tenho shuriken, você tem papel. Já era!"),
         ("KUN", "Papel corta, sabia?")]],
    ("RIB", "TROMOS"): [
        [("TROMOS", "Hssssss..."),
         ("RIB", "Eu também sei fazer barulho! RIBBIT!")],
        [("RIB", "Será que ele come sapo?"),
         ("TROMOS", "*SLURP*")]],
    ("RIB", "TAI"): [
        [("TAI", "Pequeno e rápido. Igual um mosquito."),
         ("RIB", "Mosquito não, mas eu pico igualzinho!")],
        [("RIB", "Dá pra empurrar quem você não consegue pegar?"),
         ("TAI", "Fica parado um segundo e você descobre.")]],
    ("RIB", "TAMER"): [
        [("TAMER", "Episódio de hoje: o sapo ninja."),
         ("RIB", "E o final é o sapo ganhando!")],
        [("RIB", "Seu lobo tá me olhando estranho..."),
         ("TAMER", "É que ele tá com fome.")]],
    ("KING RIP", "TRAFO"): [
        [("TRAFO", "Grrr... esse nunchaku parece um osso!"),
         ("KING RIP", "Então vem buscar, cachorrão.")],
        [("KING RIP", "Já treinei com tigre e urso. Cachorro é novidade."),
         ("TRAFO", "GRRR! Cachorro não. Cachorro MUTANTE!")]],
    ("CANNAN", "TRAFO"): [
        [("TRAFO", "Grrr... barulho de tiro me deixa BRAVO!"),
         ("CANNAN", "Então você vai ficar bravo o dia inteiro.")],
        [("CANNAN", "Eu trouxe biscoito. Quer desistir?"),
         ("TRAFO", "AU! Eu quero o biscoito E a vitória!")]],
    ("FINN", "TRAFO"): [
        [("TRAFO", "Grrr... seu chapéu parece um brinquedo, mago!"),
         ("FINN", "Esse brinquedo solta fogo, cachorrinho.")],
        [("FINN", "Seis patas... foi feitiço errado de alguém, certeza."),
         ("TRAFO", "Grrr! Eu nasci assim e sou PERFEITO!")]],
    ("KUN", "TRAFO"): [
        [("TRAFO", "AU! Me dá essa carta!"),
         ("KUN", "Vai buscar, então!")],
        [("KUN", "Aposto que você não sabe contar até seis."),
         ("TRAFO", "Conto nas patas! UM, DOIS... GRRR!")]],
    ("TRAFO", "TROMOS"): [
        [("TROMOS", "*KREEEEEE*"),
         ("TRAFO", "AUUUUUUU! Eu grito mais alto!")],
        [("TRAFO", "Grrr... uma boca dentro da boca? Que nojo!"),
         ("TROMOS", "*TSSSK!*")]],
    ("TAI", "TRAFO"): [
        [("TAI", "Já lutei com um touro. Cachorro mutante é a primeira vez."),
         ("TRAFO", "AUUU! Então prepara pra ver um campeão!")],
        [("TRAFO", "Grrr... você é grande demais pra morder!"),
         ("TAI", "Então tenta me empurrar, cachorro.")]],
    ("TAMER", "TRAFO"): [
        [("TAMER", "Senta, garoto. Isso. Bom garoto."),
         ("TRAFO", "EU NÃO SOU SEU GAROTO! GRRR!")],
        [("TRAFO", "Grrr... seu lobo é branquinho e limpinho. Eu sou BRAVO!"),
         ("TAMER", "Ele fica preto quando quer. E aí ninguém segura.")]],
    ("CANNAN", "FINN"): [
        [("FINN", "Um soldado... sempre achando que a força resolve tudo."),
         ("CANNAN", "E resolve. Quer ver?")],
        [("CANNAN", "Último aviso, vovô. Larga esse cajado."),
         ("FINN", "O cajado é que vai te largar no chão.")]],
    ("FINN", "KING RIP"): [
        [("FINN", "Vamos ver quem é o velho mais forte daqui."),
         ("KING RIP", "Mais forte e mais bonito, né?")],
        [("KING RIP", "Magia é atalho. Eu treinei quarenta anos."),
         ("FINN", "Eu estudei cem. E ainda acho pouco.")]],
    ("FINN", "KUN"): [
        [("KUN", "Pega uma carta, vovô. Qualquer uma."),
         ("FINN", "Peguei. Ela diz: você perdeu.")],
        [("FINN", "Seu baralho não tem magia de verdade."),
         ("KUN", "Mas tem uma mesa, uma cadeira e um abajur.")]],
    ("FINN", "TROMOS"): [
        [("TROMOS", "*KREEEEEE*"),
         ("FINN", "Que criatura mal-educada!")],
        [("FINN", "Será que fogo funciona em sangue ácido?"),
         ("TROMOS", "Hssssss...")]],
    ("FINN", "TAI"): [
        [("TAI", "Mago, a sua magia empurra?"),
         ("FINN", "Empurra, levanta e explode, meu caro.")],
        [("FINN", "Posso fazer você flutuar leve igual uma pena."),
         ("TAI", "Pena que eu volto pro chão. Em cima de você.")]],
    ("FINN", "TAMER"): [
        [("TAMER", "Na selva não tem magia. Tem instinto."),
         ("FINN", "Então o seu instinto vai pegar fogo.")],
        [("FINN", "Posso transformar seu lobo num cachorrinho de bolsa."),
         ("TAMER", "Tenta. Ele vai adorar morder esse cajado.")]],
    ("KING RIP", "KUN"): [
        [("KUN", "Nunchaku, vovô? Isso é tão antigo..."),
         ("KING RIP", "Antigo e invicto, moleque.")],
        [("KING RIP", "Truque de mão não ganha luta."),
         ("KUN", "Então por que o senhor tá olhando pras minhas mãos?")]],
    ("CANNAN", "KUN"): [
        [("KUN", "Soldado, quer apostar quem ganha?"),
         ("CANNAN", "Eu não aposto. Eu venço.")],
        [("CANNAN", "Mãos ao alto, garoto."),
         ("KUN", "Tá bom. Olha as cartas voando!")]],
    ("KUN", "TROMOS"): [
        [("TROMOS", "*GRRRK*"),
         ("KUN", "Eu blefaria, mas acho que você não ia entender.")],
        [("KUN", "Pega uma carta, monstrão."),
         ("TROMOS", "*CRUNCH*")]],
    ("KUN", "TAI"): [
        [("TAI", "Carta voadora não me derruba."),
         ("KUN", "E um sofá voador?")],
        [("KUN", "Tai? Parece nome de carta."),
         ("TAI", "E você vai sair voando igual uma.")]],
    ("KUN", "TAMER"): [
        [("TAMER", "Gente da cidade não aguenta um dia na selva."),
         ("KUN", "Eu aguento uma rodada inteira. Serve?")],
        [("KUN", "Lobo branco, lobo preto... parece naipe de baralho."),
         ("TAMER", "E os dois mordem.")]],
    ("KING RIP", "TROMOS"): [
        [("KING RIP", "Mostre o seu estilo de luta, criatura."),
         ("TROMOS", "*KREEEEEE*")],
        [("TROMOS", "*GRRRK*"),
         ("KING RIP", "Pelo menos você não fala demais.")]],
    ("CANNAN", "TROMOS"): [
        [("TROMOS", "Hssssss..."),
         ("CANNAN", "Dessa vez não tem nave pra você fugir.")],
        [("CANNAN", "Saiu de qual ovo, criatura? Volta pra ele."),
         ("TROMOS", "*CLAC-CLAC!*")]],
    ("TAI", "TROMOS"): [
        [("TAI", "Tem certeza que isso aí é um lutador?"),
         ("TROMOS", "*KRRRAAAH!*")],
        [("TROMOS", "*PTUI!*"),
         ("TAI", "Nem o seu ácido derrete a minha barriga.")]],
    ("TAMER", "TROMOS"): [
        [("TROMOS", "*KREEEEEE*"),
         ("TAMER", "Calma, garoto... fica atrás de mim.")],
        [("TAMER", "Isso vai dar uma ótima filmagem. Se eu sobreviver."),
         ("TROMOS", "Hssssss...")]],
    ("KING RIP", "TAI"): [
        [("TAI", "O senhor tem experiência. Eu tenho peso."),
         ("KING RIP", "E eu tenho um nunchaku.")],
        [("KING RIP", "Grande desse jeito, você cansa rápido."),
         ("TAI", "Por isso eu acabo a luta antes de cansar.")]],
    ("CANNAN", "TAI"): [
        [("TAI", "Seu canhão é muito barulhento."),
         ("CANNAN", "Espera só pra ver o tiro.")],
        [("CANNAN", "Você parece um tanque. Eu sei derrubar tanque."),
         ("TAI", "Tanque anda pra trás. Eu só ando pra frente.")]],
    ("TAI", "TAMER"): [
        [("TAMER", "Já vi elefante empurrar árvore. Você empurra igual."),
         ("TAI", "Obrigado. Eu treino pra isso.")],
        [("TAI", "Seu lobo também vai me empurrar?"),
         ("TAMER", "Não. Ele vai te morder.")]],
    ("KING RIP", "TAMER"): [
        [("TAMER", "O senhor já treinou com animais, não foi?"),
         ("KING RIP", "Treinei com um tigre. Ele que aprendeu comigo.")],
        [("KING RIP", "Bom lobo. Pena que o dono é fraco."),
         ("TAMER", "Cuidado, ele entende tudo que você fala.")]],
    ("CANNAN", "TAMER"): [
        [("CANNAN", "Sobrevivente, é? Já comeu ração de soldado?"),
         ("TAMER", "Já comi coisa bem pior. E gostei.")],
        [("TAMER", "Você faz barulho demais. Espanta os bichos."),
         ("CANNAN", "Ótimo. Espanta você também.")]],
    ("CANNAN", "KING RIP"): [
        [("CANNAN", "Velho e lento. Missão fácil."),
         ("KING RIP", "Lento? Pisca o olho e você perde.")],
        [("KING RIP", "Já vi muitos soldados. Todos caíram."),
         ("CANNAN", "Eu não sou muitos soldados.")]],
    # ---- JOHN, o mágico (v2.x) ----
    ("CANNAN", "JOHN"): [
        [("CANNAN", "Truque de cartola não segura bala, mágico."),
         ("JOHN", "E quem disse que eu vou estar aqui quando ela chegar?")],
        [("JOHN", "Para o meu próximo truque, preciso de um voluntário... você!"),
         ("CANNAN", "Voluntário não. Alvo.")]],
    ("FINN", "JOHN"): [
        [("JOHN", "Um mago de verdade! Posso pegar um autógrafo?"),
         ("FINN", "Pode. Depois que acordar da bola de fogo.")],
        [("FINN", "De onde você tira esse coelho, afinal?"),
         ("JOHN", "Um mágico nunca revela os seus segredos!")]],
    ("JOHN", "KING RIP"): [
        [("JOHN", "Senhoras e senhores, o mestre do nunchaku... vai desaparecer!"),
         ("KING RIP", "Já vi muito truque. Nenhum me derrubou.")],
        [("KING RIP", "Fica parado, mágico. Chega de sumir."),
         ("JOHN", "Abracadabra! ...Tarde demais, estou atrás de você.")]],
    ("JOHN", "KUN"): [
        [("JOHN", "Escolha uma carta, qualquer carta!"),
         ("KUN", "Ei! Essa fala é MINHA, mágico!")],
        [("KUN", "Eu tiro uma mesa e um sofá de uma carta."),
         ("JOHN", "E eu tiro um coelho gigante de um chapéu. Empate?")]],
    ("JOHN", "MAX-10"): [
        [("MAX-10", "COELHO SAINDO DE UM CHAPÉU. ISSO É IMPOSSÍVEL."),
         ("JOHN", "Impossível é a minha especialidade!")],
        [("MAX-10", "ESCANEANDO A CARTOLA... CONTEÚDO: DESCONHECIDO."),
         ("JOHN", "Nem eu sei tudo que tem aí dentro!")]],
    ("JOHN", "RIB"): [
        [("JOHN", "Um sapo! Achei que só saía coelho do meu chapéu."),
         ("RIB", "Eu não saio de chapéu nenhum!")],
        [("RIB", "Seu teleporte é igual o meu? Puf e sumiu?"),
         ("JOHN", "Igual, mas o meu termina com aplausos!")]],
    ("JOHN", "TAI"): [
        [("TAI", "No meu círculo não tem esconderijo, mágico."),
         ("JOHN", "Ainda bem que eu trouxe a minha cartola.")],
        [("JOHN", "Para o meu próximo truque: tirar um sumô do ringue!"),
         ("TAI", "Esse truque eu nunca vi dar certo.")]],
    ("JOHN", "TAMER"): [
        [("JOHN", "Que lobo lindo! Posso guardar ele na cartola?"),
         ("TAMER", "Ninguém guarda o garoto em lugar nenhum.")],
        [("TAMER", "Na selva, quem some assim é caçador... ou presa."),
         ("JOHN", "No palco, quem some assim é a ESTRELA!")]],
    ("JOHN", "TRAFO"): [
        [("JOHN", "Senta, cachorrinho, que o mágico te dá um biscoito!"),
         ("TRAFO", "GRRR! Eu não faço truque!")],
        [("TRAFO", "AU! Até o seu gato preto fugiu de você!"),
         ("JOHN", "Ele é tímido. Você vai fugir é de medo!")]],
    ("JOHN", "TROMOS"): [
        [("TROMOS", "Hssssss..."),
         ("JOHN", "Abracadabra! ...Por que ele não sumiu?!")],
        [("JOHN", "Respeitável público, calma! Ele faz parte do show!"),
         ("TROMOS", "*clic-clic-clic*")]],
}

# mesmo lutador dos dois lados
ESPELHO = [
    [(0, "Ei! Quem deixou você usar a minha cara?"), (1, "Eu ia te perguntar a mesma coisa!")],
    [(0, "Só pode existir um de nós."), (1, "Então pode ir saindo.")],
    [(0, "Até que eu sou bonito de longe..."), (1, "De perto é que você vai ver o estrago.")],
]

# espelho de quem tem jeito próprio de falar (MAX-10 em MAIÚSCULA, TROMOS só chia, TRAFO rosna)
ESPELHO_PROPRIO = {
    "MAX-10": [
        [(0, "ERRO: DOIS MAX-10 DETECTADOS."), (1, "CORREÇÃO: LOGO VAI SOBRAR SÓ UM.")],
        [(0, "VOCÊ É UMA CÓPIA PIRATA."), (1, "NEGATIVO. EU SOU A VERSÃO 2.0.")]],
    "TROMOS": [
        [(0, "Hssssss..."), (1, "*KREEEEEE*")],
        [(0, "*clic-clic*"), (1, "*CLAC-CLAC!*")]],
    "TRAFO": [
        [(0, "Grrr... quem é esse cachorro bonito?"), (1, "GRRR! Sou EU!")],
        [(0, "AUUU!"), (1, "AUUUUUUU! O meu é mais alto!")]],
    "JOHN": [
        [(0, "Dois mágicos? Isso sim é que é truque!"), (1, "Abracadabra! Agora some VOCÊ!")],
        [(0, "Qual de nós é o verdadeiro?"), (1, "O que ganhar os aplausos no final!")]],
    "RIBBAT": [
        [(0, "Ribbit?"), (1, "Ribbit!")],
        [(0, "RIBBIT!"), (1, "...RIBBIT!")]],
}

# o RIBBAT (secreto) contra qualquer um: o outro fala, e ele só responde de sapo
RIBBAT = [
    ("Um sapinho? Isso vai ser fácil.", "Ribbit."),
    ("Por que todo mundo tem medo desse sapo?", "RIBBIT!"),
    ("Que fofo... ele cabe na minha mão!", "...Ribbit."),
]
RIBBAT_PROPRIO = {  # (do mesmo jeito, pra quem tem voz própria)
    "MAX-10": [("ALVO: SAPO PEQUENO. AMEAÇA: ...CALCULANDO.", "Ribbit."),
               ("POR QUE TODOS TÊM MEDO DESTE SAPO?", "RIBBIT!")],
    "TROMOS": [("Hssssss...", "...Ribbit."), ("*SLURP*", "RIBBIT!")],
    "JOHN": [("Respeitável público, um sapinho! Vou fazer ele sumir!", "...Ribbit."),
             ("Abracadabra! ...Por que o sapo não sumiu?", "RIBBIT!")],
    "TRAFO": [("Grrr... um sapinho? Isso vai ser fácil.", "Ribbit."),
              ("AU! Que fofo... cabe na minha boca!", "...Ribbit.")],
}


def _voz(nome, txt):
    """Passa uma fala comum pro jeito do personagem (usada na fala da SOMBRA)."""
    if nome == "MAX-10":
        return txt.upper()
    if nome == "TROMOS":
        return "Hssssss..."
    if nome == "MAGNUS":
        return "*RRAAWR!*"
    if nome == "SPHYRUS":
        return "*GROOOAR!*"
    if nome == "FRIGANTUS":
        return "*GRUUUAAH!*"
    if nome == "NOCTURNUS":
        return "*IIIIII!*"
    if nome == "RIBBAT":
        return "Ribbit."
    if nome == "TRAFO":
        return "Grrr... " + txt[0].lower() + txt[1:]
    return txt

# quando não tem conversa pronta (ou é um personagem novo), cada um fala a sua frase
FRASES = {
    "MAX-10": "COMBATE INICIADO.",
    "RIB": "Pode vir! Eu sou mais rápido que a sua sombra!",
    "TRAFO": "AUUUUUU!",
    "KING RIP": "Vamos ver do que você é feito.",
    "CANNAN": "Missão: vencer. Começando agora.",
    "FINN": "Prepare-se para a minha magia!",
    "KUN": "A sorte já está lançada.",
    "TROMOS": "Hssssssss...",
    "TAI": "Hakkeyoi! Vamos lutar!",
    "TAMER": "Fica perto de mim, garoto. Vai ser divertido.",
    "RIBBAT": "Ribbit.",
    "JOHN": "Respeitável público! Abracadabra!",
}


# CRÁQUEN, o capitão pirata fantasma (2 conversas com cada um)
_CRAQUEN = {
    "MAX-10": [
        [("CRÁQUEN", "Arrr! Um homem de lata... vai enferrujar no fundo do mar!"),
         ("MAX-10", "SENSORES NÃO DETECTAM VOCÊ. VOCÊ ESTÁ AÍ?")],
        [("MAX-10", "FANTASMA: PROBABILIDADE DE EXISTIR = 0%."),
         ("CRÁQUEN", "Então vai apanhar de um zero, marujo! Har har!")]],
    "RIB": [
        [("RIB", "Um fantasma pirata?! Meu vô contava história de você!"),
         ("CRÁQUEN", "E todas terminavam com o sapo na prancha!")],
        [("CRÁQUEN", "Sapo ninja, hein? Ninja não atravessa parede."),
         ("RIB", "Mas desvia de fantasma rapidinho!")]],
    "TRAFO": [
        [("TRAFO", "Grrr... você não tem cheiro de nada!"),
         ("CRÁQUEN", "Fantasma não tem cheiro, cachorrinho. Só dá medo.")],
        [("CRÁQUEN", "Seis patas? Daria um ótimo cão de bordo!"),
         ("TRAFO", "GRRR! Eu não sou cachorro de navio!")]],
    "KING RIP": [
        [("KING RIP", "Na minha época, fantasma ficava quieto no castelo."),
         ("CRÁQUEN", "Na minha época, eu afundava castelos, vovô!")],
        [("CRÁQUEN", "Esse nunchaku não acerta quem não tem corpo!"),
         ("KING RIP", "Então vamos descobrir o que você tem.")]],
    "CANNAN": [
        [("CANNAN", "Um canhão contra um navio inteiro de canhões?"),
         ("CRÁQUEN", "Arrr! Agora sim é uma batalha de verdade!")],
        [("CRÁQUEN", "Soldado, você ia dar um ótimo marujo."),
         ("CANNAN", "Eu não sigo ordem de assombração.")]],
    "FINN": [
        [("FINN", "Uma alma perdida... posso te mandar pro descanso."),
         ("CRÁQUEN", "Descansar? Eu tenho sete mares pra assombrar!")],
        [("CRÁQUEN", "Mago, sabe um feitiço pra achar o meu tesouro?"),
         ("FINN", "Sei um pra te trazer de volta pro chão.")]],
    "KUN": [
        [("KUN", "Aposto meu baralho que você não me assusta."),
         ("CRÁQUEN", "Aposta aceita! BUUU!")],
        [("CRÁQUEN", "Cartas? Eu jogava pôquer com tubarões!"),
         ("KUN", "E perdeu o corpo na aposta?")]],
    "TROMOS": [
        [("TROMOS", "Hssssss..."),
         ("CRÁQUEN", "Até pra um fantasma você dá medo, criatura!")],
        [("CRÁQUEN", "Arrr... você estava escondido no porão do meu navio?"),
         ("TROMOS", "*clic-clic*")]],
    "TAI": [
        [("TAI", "Como é que eu empurro quem não tem pé?"),
         ("CRÁQUEN", "Não empurra, grandão! Har har!")],
        [("CRÁQUEN", "Seu ringue é pequeno. O meu é o oceano!"),
         ("TAI", "Então eu trago o oceano pro meu ringue.")]],
    "TAMER": [
        [("TAMER", "O garoto está rosnando... ele sente fantasmas."),
         ("CRÁQUEN", "Esperto o seu lobo, marujo!")],
        [("CRÁQUEN", "Esse lobo daria um ótimo cão do mar!"),
         ("TAMER", "Ele odeia água. E odeia você.")]],
    "JOHN": [
        [("JOHN", "Respeitável público! Vou fazer o fantasma desaparecer!"),
         ("CRÁQUEN", "Eu já sou meio sumido, mágico! Har har!")],
        [("CRÁQUEN", "Esse coelho da cartola... sobe a bordo como cozinheiro?"),
         ("JOHN", "Ele é artista, capitão! Não cozinha!")]],
}
for _outro, _convs in _CRAQUEN.items():
    _chave = tuple(sorted(("CRÁQUEN", _outro)))
    CONVERSAS[_chave] = _convs[0]
    MAIS[_chave] = _convs[1:]
ESPELHO_PROPRIO["CRÁQUEN"] = [
    [(0, "Arrr! Quem é esse impostor feito de névoa?"), (1, "Eu ia perguntar o mesmo, marujo!")],
    [(0, "Só um capitão comanda este navio!"), (1, "Então que o melhor fantasma vença!")]]
RIBBAT_PROPRIO["CRÁQUEN"] = [("Arrr! Um sapinho no meu convés!", "Ribbit."),
                             ("Vai pra prancha, sapinho!", "RIBBIT!")]
FRASES["CRÁQUEN"] = "Arrr! Pro fundo do mar com você!"


# RIVAIS (v2.x): quando os rivais se enfrentam, a conversa é sempre uma destas (rivais.py diz quem é rival de quem)
RIVAIS_CONVERSAS = {
    ("JOHN", "KUN"): [
        [("KUN", "De novo você, mágico? Esse palco é pequeno pra nós dois."),
         ("JOHN", "Então que vença o maior truque!")],
        [("JOHN", "Respeitável público! Hoje o rapaz das cartas some... de vez!"),
         ("KUN", "Aposto todas as minhas cartas que quem some é você.")],
        [("KUN", "Você roubou o meu \"escolha uma carta\"!"),
         ("JOHN", "Um mágico não rouba. Ele faz aparecer!")]],
    ("CRÁQUEN", "TAMER"): [
        [("TAMER", "Fica atrás de mim, garoto. É o fantasma de que te falei."),
         ("CRÁQUEN", "Arrr! O domador e o cãozinho... pra prancha, os dois!")],
        [("CRÁQUEN", "Na terra você manda, domador. No mar, manda o polvo!"),
         ("TAMER", "O garoto não tem medo de tentáculo.")],
        [("TAMER", "Já enfrentei tubarão, jacaré e cobra. Faltava um pirata."),
         ("CRÁQUEN", "Pirata FANTASMA, marujo! Har har!")]],
    ("TRAFO", "TROMOS"): [
        [("TRAFO", "GRRR! Você de novo, coisa babona!"),
         ("TROMOS", "*KREEEEEE*")],
        [("TROMOS", "Hssssss..."),
         ("TRAFO", "Grrr... só cabe UM mutante nesta arena!")],
        [("TRAFO", "AU! Da última vez o seu sangue queimou a minha língua!"),
         ("TROMOS", "*clic-clic-clic*")]],
    ("CANNAN", "KING RIP"): [
        [("KING RIP", "Na minha época, soldado respeitava os mestres."),
         ("CANNAN", "Na minha guerra, nunchaku não segurava canhão.")],
        [("CANNAN", "Velho, você não sabe a hora de se aposentar."),
         ("KING RIP", "E você não sabe a hora de abaixar esse canhão.")],
        [("KING RIP", "Ainda lembro da nossa última luta, soldado."),
         ("CANNAN", "Eu também. Hoje eu termino a missão.")]],
    ("RIB", "TAI"): [
        [("RIB", "Você de novo, grandão?! Hoje eu não caio do ringue!"),
         ("TAI", "Você disse isso da última vez, sapinho.")],
        [("TAI", "O menor da arena contra o maior. De novo."),
         ("RIB", "Tamanho não importa. Velocidade, sim!")],
        [("RIB", "Aposto que você não me pega nem se eu ficar parado!"),
         ("TAI", "Não preciso pegar. Só preciso empurrar.")]],
}


def _base(nome):
    return nome[len("SOMBRA DO "):] if nome.startswith("SOMBRA DO ") else nome


def conversas(n1, n2):
    """Todas as conversas que essa dupla tem (cada uma é [(quem fala, texto), ...])."""
    chave = tuple(sorted((n1, n2)))
    todas = [CONVERSAS[chave]] if chave in CONVERSAS else []
    return todas + MAIS.get(chave, [])


def dialogo(f1, f2, rng=random):
    """A conversa entre o lutador da esquerda (lado 0) e o da direita (lado 1): [(lado, texto), ...].
    Cada dupla tem 2 ou 3 conversas: sorteia uma."""
    n1, n2 = _base(f1["nome"]), _base(f2["nome"])
    if f2.get("sombra") or f1.get("sombra"):
        sombra = 1 if f2.get("sombra") else 0
        nomes = (n1, n2)
        return [(sombra, _voz(nomes[sombra], "Eu sou tudo aquilo que você tem medo de ser...")),
                (1 - sombra, _voz(nomes[1 - sombra], "Então hoje eu vou vencer o meu medo!"))]
    if n1 == n2:
        return list(rng.choice(ESPELHO_PROPRIO.get(n1, ESPELHO)))
    if "RIBBAT" in (n1, n2):
        sapo = 0 if n1 == "RIBBAT" else 1
        if n1 == "RIB" or n2 == "RIB":
            return [(1 - sapo, "Peraí... você é meu primo?!"), (sapo, "RIBBIT!")]
        fala, resposta = rng.choice(RIBBAT_PROPRIO.get((n1, n2)[1 - sapo], RIBBAT))
        return [(1 - sapo, fala), (sapo, resposta)]
    rivais = RIVAIS_CONVERSAS.get(tuple(sorted((n1, n2))))
    if rivais:  # RIVAIS: sempre uma conversa de rivalidade
        return [(0 if quem == n1 else 1, txt) for quem, txt in rng.choice(rivais)]
    todas = conversas(n1, n2)
    if todas:
        return [(0 if quem == n1 else 1, txt) for quem, txt in rng.choice(todas)]
    return [(lado, FRASES.get(n, "Prepare-se!")) for lado, n in ((0, n1), (1, n2))]


# MAGNUS, o dino-robô de fogo (personagem 13, do Gomes): ele não fala, só faz SOM (ruge, fareja, solta fumaça)
_M = "MAGNUS"
_MAGNUS = {
    "CANNAN": [
        [("CANNAN", "Experimento 13... o que fugiu da base. Missão: te levar de volta."), (_M, "*RRAAWR!*")],
        [(_M, "*snif... snif...*"), ("CANNAN", "É, sou eu. Cheiro de quartel você não esquece.")],
        [("CANNAN", "Dinossauro de fogo com peça de robô. O exército exagerou."), (_M, "*FSSSHH...*")]],
    "FINN": [
        [("FINN", "Um dragão?! Não... um lagarto de lata que cospe fogo."), (_M, "*GRRRAAAH!*")],
        [(_M, "*RRAAWR!*"), ("FINN", "Fogo eu também sei fazer, criatura. Olha o meu Mini Sol!")],
        [("FINN", "Que feitiço criaria uma coisa dessas?"), (_M, "*CLANK... CLANK...*")]],
    "JOHN": [
        [("JOHN", "Respeitável público! Um dinossauro! ...Isso não estava no show."), (_M, "*RRAAWR!*")],
        [(_M, "*snif... snif...*"), ("JOHN", "Ele está farejando o meu coelho! Fica na cartola, coelho!")],
        [("JOHN", "Para o meu próximo truque: fazer um dinossauro sumir!"), (_M, "*FSSSHH...*")]],
    "KING RIP": [
        [("KING RIP", "Na minha época, dinossauro só aparecia em museu."), (_M, "*GRRRAAAH!*")],
        [(_M, "*RRAAWR!*"), ("KING RIP", "Pode gritar. O meu nunchaku não tem medo.")],
        [("KING RIP", "Rápido e cheio de garras... bom adversário pra um velho."), (_M, "*snif... snif...*")]],
    "KUN": [
        [("KUN", "Aposto que esse fogo não queima uma carta."), (_M, "*FWOOSH!*")],
        [(_M, "*RRAAWR!*"), ("KUN", "Calma! Eu tiro um sofá da carta pra você sentar.")],
        [("KUN", "Um dino robô? Essa carta eu nunca tirei do baralho."), (_M, "*GRRRAAAH!*")]],
    "MAX-10": [
        [("MAX-10", "ANALISANDO... METADE DINOSSAURO, METADE MÁQUINA. ERRO."), (_M, "*GRRRAAAH!*")],
        [(_M, "*snif... snif...*"), ("MAX-10", "EU NÃO SOU COMIDA. SOU FEITO DE METAL.")],
        [("MAX-10", "PEÇAS DE ROBÔ NUM DINOSSAURO? QUEM MONTOU VOCÊ?"), (_M, "*FSSSHH...*")]],
    "RIB": [
        [("RIB", "Um dinossauro?! Que da hora! ...Ele não come sapo, né?"), (_M, "*RRAAWR!*")],
        [(_M, "*snif... snif...*"), ("RIB", "Ei! Não me cheira assim, eu não sou lanche!")],
        [("RIB", "Aposto que você não pega um ninja!"), (_M, "*GRRRAAAH!*")]],
    "TAI": [
        [("TAI", "No meu ringue, nem dinossauro me tira do círculo."), (_M, "*RRAAWR!*")],
        [(_M, "*GRRRAAAH!*"), ("TAI", "Pode rugir. Eu não saio do lugar.")],
        [("TAI", "Rabo de fogo? Vou precisar de mais sal."), (_M, "*FSSSHH...*")]],
    "TAMER": [
        [("TAMER", "Calma, garoto... esse bicho não está em nenhum documentário."), (_M, "*snif... snif...*")],
        [(_M, "*RRAAWR!*"), ("TAMER", "Já domei muito bicho. Dinossauro vai ser o primeiro.")],
        [("TAMER", "Ele fugiu de algum lugar. Dá pra ver nos olhos."), (_M, "*GRRRAAAH...*")]],
    "TRAFO": [
        [("TRAFO", "Grrr... mais um mutante? Esta arena tá lotada!"), (_M, "*RRAAWR!*")],
        [(_M, "*GRRRAAAH!*"), ("TRAFO", "AU! Pode rugir. Eu mordo mais forte!")],
        [("TRAFO", "Grrr... cheiro de fumaça e ferro queimado!"), (_M, "*FSSSHH...*")]],
    "TROMOS": [
        [("TROMOS", "Hssssss..."), (_M, "*RRAAWR!*")],
        [(_M, "*snif... snif...*"), ("TROMOS", "*KREEEEEE*")],
        [("TROMOS", "*clic-clic-clic*"), (_M, "*GRRRAAAH!*")]],
    "CRÁQUEN": [
        [("CRÁQUEN", "Arrr! Um lagarto de fogo no meu navio? Vai pro mar apagar!"), (_M, "*FSSSHH...*")],
        [(_M, "*RRAAWR!*"), ("CRÁQUEN", "Pode rugir, lagartixa! Fantasma não queima!")],
        [("CRÁQUEN", "Fogo e água não se misturam, marujo!"), (_M, "*GRRRAAAH!*")]],
}
for _outro, _convs in _MAGNUS.items():
    _chave = tuple(sorted((_M, _outro)))
    CONVERSAS[_chave] = _convs[0]
    MAIS[_chave] = _convs[1:]
# rival do MAX-10 (rivais.py): quando os dois se enfrentam, a conversa é sempre uma destas
RIVAIS_CONVERSAS[tuple(sorted((_M, "MAX-10")))] = [
    [("MAX-10", "EXPERIMENTO 13 DETECTADO. VOCÊ É UMA CÓPIA MAL FEITA."), (_M, "*RRAAWR!*")],
    [(_M, "*CLANK... CLANK...*"), ("MAX-10", "SÓ PODE HAVER UMA MÁQUINA NESTA ARENA.")],
    [("MAX-10", "ALERTA: FOGO PERTO DOS MEUS CIRCUITOS."), (_M, "*FWOOSH!*")]]
# FINN x CRÁQUEN também são rivais (o Cráquen tem 2 rivais)
RIVAIS_CONVERSAS[("CRÁQUEN", "FINN")] = [
    [("FINN", "Alma penada! Hoje eu mando você pro descanso de vez."),
     ("CRÁQUEN", "Arrr! Já ouvi isso de sete magos, vovô. Todos afundaram!")],
    [("CRÁQUEN", "Seu feitiço não pega em quem não tem corpo, mago!"),
     ("FINN", "Então vou usar um feitiço pra quem não tem juízo.")],
    [("FINN", "Essa maldição do seu navio... eu sei como quebrar."),
     ("CRÁQUEN", "Tenta, e vira enfeite do meu convés! Har har!")]]
ESPELHO_PROPRIO[_M] = [[(0, "*RRAAWR!*"), (1, "*GRRRAAAH!*")],
                       [(0, "*snif... snif...*"), (1, "*FSSSHH...*")]]
RIBBAT_PROPRIO[_M] = [("*snif... snif...*", "...Ribbit."), ("*RRAAWR!*", "RIBBIT!")]
FRASES[_M] = "*RRAAWR!*"


# SPHYRUS, o tubarão-martelo (personagem 14, do Gomes): ele não fala, só faz SOM (ruge, morde, a barbatana corta o chão)
_S = "SPHYRUS"
_SPHYRUS = {
    "MAX-10": [
        [("MAX-10", "ANALISANDO... TUBARÃO COM PERNAS. ERRO NO BANCO DE DADOS."), (_S, "*GROOOAR!*")],
        [(_S, "*clac-clac*"), ("MAX-10", "MEU METAL NÃO É COMESTÍVEL. RECALCULE O CARDÁPIO.")],
        [("MAX-10", "ÁGUA SALGADA DETECTADA. RISCO DE FERRUGEM: ALTO."), (_S, "*SPLASH!*")]],
    "RIB": [
        [("RIB", "Um tubarão andando?! Nem no pântano eu vi isso!"), (_S, "*CHOMP!*")],
        [(_S, "*shhhhk...*"), ("RIB", "Essa barbatana cortando o chão... tá vindo pra mim?!")],
        [("RIB", "Ninja também nada, sabia? Pode vir!"), (_S, "*GROOOAR!*")]],
    "TRAFO": [
        [("TRAFO", "Grrr... cheiro de peixe! Muito peixe!"), (_S, "*clac-clac*")],
        [(_S, "*GROOOAR!*"), ("TRAFO", "AU! Pode mostrar os dentes. Os meus também mordem!")],
        [("TRAFO", "Grrr... cachorro odeia banho. E odeia tubarão mais ainda!"), (_S, "*SPLASH!*")]],
    "KING RIP": [
        [("KING RIP", "Na minha época, tubarão ficava no mar."), (_S, "*shhhhk...*")],
        [(_S, "*GROOOAR!*"), ("KING RIP", "Pode rugir. Já pesquei peixe maior que você.")],
        [("KING RIP", "Duas fileiras de dentes e nenhum respeito pelos mais velhos."), (_S, "*CHOMP!*")]],
    "CANNAN": [
        [("CANNAN", "Mais um experimento fugido da ilha. Essa base não tranca nada?"), (_S, "*GROOOAR!*")],
        [(_S, "*clac-clac*"), ("CANNAN", "Código de barras na barbatana. Propriedade do laboratório.")],
        [("CANNAN", "Já desembarquei em praia sob fogo. Tubarão não me assusta."), (_S, "*SPLASH!*")]],
    "FINN": [
        [("FINN", "Uma fera dos mares em terra firme? Que feitiço é esse?"), (_S, "*GROOOAR!*")],
        [(_S, "*shhhhk...*"), ("FINN", "Feitiço de levitar: quero ver tubarão nadar no ar!")],
        [("FINN", "Até os meus livros de magia têm medo dessa boca."), (_S, "*CHOMP!*")]],
    "KUN": [
        [("KUN", "Aposto que tubarão não sabe jogar baralho."), (_S, "*CHOMP!*")],
        [(_S, "*clac-clac*"), ("KUN", "Calma! Pega um peixe da minha carta. ...Tá, eu não tenho peixe.")],
        [("KUN", "Um tubarão-martelo... essa carta é rara!"), (_S, "*GROOOAR!*")]],
    "TROMOS": [
        [("TROMOS", "Hssssss..."), (_S, "*GROOOAR!*")],
        [(_S, "*clac-clac*"), ("TROMOS", "*KREEEEEE*")],
        [("TROMOS", "*clic-clic-clic*"), (_S, "*SPLASH!*")]],
    "TAI": [
        [("TAI", "No meu ringue não tem água. Aqui você é só um peixe."), (_S, "*shhhhk...*")],
        [(_S, "*GROOOAR!*"), ("TAI", "Pode morder. A minha barriga é de aço.")],
        [("TAI", "Tubarão e sumô: os dois gostam de empurrar."), (_S, "*CHOMP!*")]],
    "TAMER": [
        [("TAMER", "Calma, garoto. Esse eu já filmei no mar... mas ele não andava."), (_S, "*GROOOAR!*")],
        [(_S, "*shhhhk...*"), ("TAMER", "Uma barbatana cortando o chão. Fica atrás de mim, garoto.")],
        [("TAMER", "Tubarão-martelo sente a eletricidade do corpo da gente."), (_S, "*clac-clac*")]],
    "JOHN": [
        [("JOHN", "Respeitável público! Um tubarão de verdade, sem truque!"), (_S, "*GROOOAR!*")],
        [(_S, "*CHOMP!*"), ("JOHN", "Ei! O coelho da cartola NÃO é petisco!")],
        [("JOHN", "Abracadabra! Sumi! ...Por que ele ainda está olhando pra mim?"), (_S, "*clac-clac*")]],
    "CRÁQUEN": [
        [("CRÁQUEN", "Arrr! Um tubarão no meu mar? Vai ser o cão de guarda do navio!"), (_S, "*GROOOAR!*")],
        [(_S, "*SPLASH!*"), ("CRÁQUEN", "Pode nadar, peixinho. Este oceano é meu há trezentos anos!")],
        [("CRÁQUEN", "Fantasma não tem carne pra morder, marujo! Har har!"), (_S, "*CHOMP!*")]],
    "MAGNUS": [
        [("MAGNUS", "*RRAAWR!*"), (_S, "*GROOOAR!*")],
        [(_S, "*clac-clac*"), ("MAGNUS", "*snif... snif...*")],
        [("MAGNUS", "*FSSSHH...*"), (_S, "*SPLASH!*")]],
}
for _outro, _convs in _SPHYRUS.items():
    _chave = tuple(sorted((_S, _outro)))
    CONVERSAS[_chave] = _convs[0]
    MAIS[_chave] = _convs[1:]
# rival do MAGNUS (rivais.py: PREDADOR CONTRA PREDADOR): dois experimentos fugidos, só rugido
RIVAIS_CONVERSAS[tuple(sorted((_S, "MAGNUS")))] = [
    [(_S, "*GROOOAR!*"), ("MAGNUS", "*RRAAWR!*")],
    [("MAGNUS", "*snif... snif...*"), (_S, "*shhhhk...*")],
    [(_S, "*CHOMP!*"), ("MAGNUS", "*FWOOSH!*")]]
ESPELHO_PROPRIO[_S] = [[(0, "*GROOOAR!*"), (1, "*GROOOAR!!*")],
                       [(0, "*clac-clac*"), (1, "*CHOMP!*")]]
RIBBAT_PROPRIO[_S] = [("*clac-clac*", "...Ribbit."), ("*GROOOAR!*", "RIBBIT!")]
FRASES[_S] = "*GROOOAR!*"


# FRIGANTUS, o yeti (personagem 15, do Gomes): não fala, só faz SOM (macaco gigante + gelo)
_F = "FRIGANTUS"
_FRIGANTUS = {
    "MAX-10": [
        [("MAX-10", "TEMPERATURA: -40 GRAUS. MEUS CIRCUITOS ESTÃO CONGELANDO."), (_F, "*fuuuuh...*")],
        [(_F, "*UH-UH-UH!*"), ("MAX-10", "MACACO GIGANTE DETECTADO. BANANA NÃO INCLUSA.")],
        [("MAX-10", "ANALISANDO PELO... RESULTADO: MUITO PELO."), (_F, "*GRUUUAAH!*")]],
    "RIB": [
        [("RIB", "Que frio! Sapo não foi feito pra neve!"), (_F, "*fuuuuh...*")],
        [(_F, "*GRUUUAAH!*"), ("RIB", "Grandão, peludo e gelado... ninja não tem medo!")],
        [("RIB", "Aposto que você não me pega no meio da neve!"), (_F, "*CRAC!*")]],
    "TRAFO": [
        [("TRAFO", "Grrr... um macaco de neve? Eu mordo até gelo!"), (_F, "*UH-UH-UH!*")],
        [(_F, "*GRUUUAAH!*"), ("TRAFO", "AU! Pode rugir. Eu rosno mais feio!")],
        [("TRAFO", "Grrr... minhas seis patas estão congelando!"), (_F, "*fuuuuh...*")]],
    "KING RIP": [
        [("KING RIP", "Na minha época, eu treinava descalço na neve."), (_F, "*UH-UH-UH!*")],
        [(_F, "*fuuuuh...*"), ("KING RIP", "Bafo gelado... nem o meu chá esquenta isso.")],
        [("KING RIP", "Forte como uma montanha. Mas montanha não desvia."), (_F, "*GRUUUAAH!*")]],
    "CANNAN": [
        [("CANNAN", "Missão no Ártico. Alvo: grande, peludo e bravo."), (_F, "*GRUUUAAH!*")],
        [(_F, "*CRAC!*"), ("CANNAN", "Meu canhão não congela. Vamos ver o seu soco.")],
        [("CANNAN", "Já lutei na neve. Você é o pior inverno que eu já vi."), (_F, "*UH-UH-UH!*")]],
    "FINN": [
        [("FINN", "Um gigante das montanhas! Meu fogo vai te derreter."), (_F, "*fuuuuh...*")],
        [(_F, "*GRUUUAAH!*"), ("FINN", "Calma, criatura! Eu só quero um pouco de neve pra poção.")],
        [("FINN", "Meu golem de pedra contra o seu gelo. Quero ver."), (_F, "*CRAC!*")]],
    "KUN": [
        [("KUN", "Aposto que você não sabe embaralhar com essas mãos."), (_F, "*UH-UH-UH!*")],
        [(_F, "*fuuuuh...*"), ("KUN", "Minhas cartas congelaram! Isso não vale!")],
        [("KUN", "Um yeti de verdade... essa carta é raríssima!"), (_F, "*GRUUUAAH!*")]],
    "TROMOS": [
        [("TROMOS", "Hssssss..."), (_F, "*GRUUUAAH!*")],
        [(_F, "*fuuuuh...*"), ("TROMOS", "*clic-clic-clic*")],
        [("TROMOS", "*KREEEEEE*"), (_F, "*UH-UH-UH!*")]],
    "TAI": [
        [("TAI", "Gigante contra gigante. Agora sim uma luta justa."), (_F, "*UH-UH-UH!*")],
        [(_F, "*GRUUUAAH!*"), ("TAI", "Pode ser grande. No meu círculo, quem empurra sou eu.")],
        [("TAI", "Na neve não dá pra fazer sumô... vou tentar mesmo assim."), (_F, "*CRAC!*")]],
    "TAMER": [
        [("TAMER", "Calma, garoto. O lendário das montanhas existe mesmo!"), (_F, "*fuuuuh...*")],
        [(_F, "*UH-UH-UH!*"), ("TAMER", "Essa filmagem vai ser a mais famosa do mundo.")],
        [("TAMER", "Pegadas gigantes na neve... ele está bem atrás de nós."), (_F, "*GRUUUAAH!*")]],
    "JOHN": [
        [("JOHN", "Respeitável público! O abominável homem das neves!"), (_F, "*GRUUUAAH!*")],
        [(_F, "*UH-UH-UH!*"), ("JOHN", "Para o meu próximo truque: fazer a neve sumir!")],
        [("JOHN", "Abracadabra! ...Ele virou picolé. Ah, não, ele já era assim."), (_F, "*CRAC!*")]],
    "CRÁQUEN": [
        [("CRÁQUEN", "Arrr! Um urso de gelo? Já afundei icebergs maiores!"), (_F, "*GRUUUAAH!*")],
        [(_F, "*fuuuuh...*"), ("CRÁQUEN", "Esse bafo congelou o meu navio inteiro, marujo!")],
        [("CRÁQUEN", "Fantasma não sente frio! Har har!"), (_F, "*UH-UH-UH!*")]],
    "MAGNUS": [
        [("MAGNUS", "*RRAAWR!*"), (_F, "*GRUUUAAH!*")],
        [(_F, "*fuuuuh...*"), ("MAGNUS", "*FSSSHH...*")],
        [("MAGNUS", "*FWOOSH!*"), (_F, "*CRAC!*")]],
    "SPHYRUS": [
        [("SPHYRUS", "*GROOOAR!*"), (_F, "*UH-UH-UH!*")],
        [(_F, "*fuuuuh...*"), ("SPHYRUS", "*clac-clac*")],
        [("SPHYRUS", "*SPLASH!*"), (_F, "*CRAC!*")]],
}
for _outro, _convs in _FRIGANTUS.items():
    _chave = tuple(sorted((_F, _outro)))
    CONVERSAS[_chave] = _convs[0]
    MAIS[_chave] = _convs[1:]
ESPELHO_PROPRIO[_F] = [[(0, "*UH-UH-UH!*"), (1, "*UH-UH-UH!!*")],
                       [(0, "*fuuuuh...*"), (1, "*GRUUUAAH!*")]]
RIBBAT_PROPRIO[_F] = [("*fuuuuh...*", "...Ribbit."), ("*GRUUUAAH!*", "RIBBIT!")]
FRASES[_F] = "*UH-UH-UH!*"


# INAZUMANEKO, o tigre samurai (personagem 16, v3.0, do Gomes): fala pouco, calmo e honrado, como mestre de espada
_I = "INAZUMANEKO"
_INAZUMANEKO = {
    "MAX-10": [
        [("MAX-10", "FELINO COM ARMADURA DETECTADO. AMEAÇA: ALTA."), (_I, "Sua armadura é de aço. A minha, de honra.")],
        [(_I, "Sua lâmina é um raio de luz. A minha é de verdade."), ("MAX-10", "COMPARANDO LÂMINAS... ERRO.")],
        [("MAX-10", "ANALISANDO ESPADA... AFIAÇÃO: PERIGOSA."), (_I, "Então não fique na frente dela.")]],
    "TRAFO": [
        [("TRAFO", "Grrr... um gato? Eu caço gatos!"), (_I, "Hoje, o gato é quem caça.")],
        [(_I, "Você muda de forma. Eu nunca mudo de caminho."), ("TRAFO", "AUUU! Vamos ver se o caminho aguenta!")],
        [("TRAFO", "Grrr... vou virar você e te cortar com a sua espada!"), (_I, "Uma espada sem treino não corta nada.")]],
    "KING RIP": [
        [("KING RIP", "Um samurai. Faz tempo que eu não vejo um de verdade."), (_I, "Mestre. É uma honra.")],
        [(_I, "Seu nunchaku é rápido. Mas o vento é mais."), ("KING RIP", "Na minha idade, eu sou o vento.")],
        [("KING RIP", "Depois da luta, um chá na montanha?"), (_I, "Só depois que um de nós cair.")]],
    "CANNAN": [
        [("CANNAN", "Eu trouxe um canhão pra uma luta de espada."), (_I, "Então eu corto as balas.")],
        [(_I, "Você luta de longe. Eu vou até você."), ("CANNAN", "Tenta chegar perto, soldado de pelo.")],
        [("CANNAN", "Missão: derrubar o gato. Câmbio."), (_I, "Câmbio... e desligo.")]],
    "FINN": [
        [("FINN", "Um tigre de armadura! Que criatura rara."), (_I, "E você, um velho com fogo na mão.")],
        [(_I, "Magia não se defende com espada... por isso eu ataco primeiro."), ("FINN", "Ho ho! Rápido e esperto!")],
        [("FINN", "Meu golem é feito de pedra, felino."), (_I, "Já cortei montanhas no meu treino.")]],
    "KUN": [
        [("KUN", "Aposto uma carta que você não corta ela no ar."), (_I, "Joga.")],
        [(_I, "Sorte não vence disciplina."), ("KUN", "Ainda bem que eu tenho as duas.")],
        [("KUN", "Ás de espadas. Combina com você."), (_I, "Então vou ganhar a mão.")]],
    "TROMOS": [
        [("TROMOS", "Hssssss..."), (_I, "Um caçador nas sombras. Eu luto na luz.")],
        [(_I, "Sua cauda é uma lâmina. A minha também."), ("TROMOS", "*KREEEEEE*")],
        [("TROMOS", "*clic-clic-clic*"), (_I, "Ácido não enferruja aço bom.")]],
    "TAI": [
        [("TAI", "Um samurai! No sumô a gente respeita a tradição."), (_I, "No duelo, também.")],
        [(_I, "Você é uma montanha. Eu sou o vento que passa por ela."), ("TAI", "Vento leve não empurra montanha!")],
        [("TAI", "Hakkeyoi! Vamos ver quem é mais firme."), (_I, "O mais firme é quem não cai.")]],
    "TAMER": [
        [("TAMER", "Um tigre branco! E fala! Nunca vi isso na selva."), (_I, "Eu não sou da selva. Sou da montanha.")],
        [(_I, "Seu lobo é leal. Isso é respeito."), ("TAMER", "E ele não gosta de gato. Fica esperto.")],
        [("TAMER", "Garoto, esse aí é perigoso. Fica atrás de mim."), (_I, "Os dois podem vir.")]],
    "JOHN": [
        [("JOHN", "Respeitável público: o tigre samurai!"), (_I, "Eu não sou atração de circo.")],
        [(_I, "Truques não enganam quem enxerga com calma."), ("JOHN", "Então feche os olhos... e PUF!")],
        [("JOHN", "Minha cartola tem lâminas também!"), (_I, "Lâmina sem mão firme é só enfeite.")]],
    "CRÁQUEN": [
        [("CRÁQUEN", "Arrr! Um gato na terra firme! Sobe no meu navio, se tem coragem!"), (_I, "Não preciso de navio. Corto a âncora.")],
        [(_I, "Fantasma ou não, quem empunha espada pode ser vencido."), ("CRÁQUEN", "Minha espada é de fantasma, gatinho!")],
        [("CRÁQUEN", "Tesouro, você tem? Har har!"), (_I, "O meu tesouro é a lâmina.")]],
    "MAGNUS": [
        [("MAGNUS", "*RRAAWR!*"), (_I, "Fogo e fúria. Sem controle, não vencem.")],
        [(_I, "Uma fera solta. Vou te ensinar o silêncio."), ("MAGNUS", "*FWOOSH!*")],
        [("MAGNUS", "*snif... snif...*"), (_I, "Sente o cheiro do aço?")]],
    "SPHYRUS": [
        [("SPHYRUS", "*GROOOAR!*"), (_I, "Um predador do mar. Aqui, você está longe de casa.")],
        [(_I, "Sua mordida é forte. Minha lâmina é mais rápida."), ("SPHYRUS", "*clac-clac*")],
        [("SPHYRUS", "*SPLASH!*"), (_I, "Nem a água foge do meu corte.")]],
    "FRIGANTUS": [
        [("FRIGANTUS", "*GRUUUAAH!*"), (_I, "Grande e forte. Mas lento.")],
        [(_I, "Na minha montanha não tem neve. Hoje vai ter."), ("FRIGANTUS", "*UH-UH-UH!*")],
        [("FRIGANTUS", "*fuuuuh...*"), (_I, "Um sopro gelado não para a minha espada.")]],
}
_INAZUMANEKO["RIB"] = [  # (fora da rivalidade: no treino, no torneio...)
    [("RIB", "Um samurai na minha frente? Ninja nunca perde pra samurai!"), (_I, "Ninja se esconde. Samurai encara.")],
    [(_I, "Você ataca pelas costas, sapo."), ("RIB", "Eu ataco por onde você não olha!")],
    [("RIB", "Shuriken contra katana. Hoje a gente resolve isso."), (_I, "Já está resolvido. Saca.")]]
for _outro, _convs in _INAZUMANEKO.items():
    _chave = tuple(sorted((_I, _outro)))
    CONVERSAS[_chave] = _convs[0]
    MAIS[_chave] = _convs[1:]
# o RIVAL (rivais.py: SAMURAI CONTRA NINJA): o RIB, o ninja sapo
RIVAIS_CONVERSAS[tuple(sorted((_I, "RIB")))] = [
    [("RIB", "Um samurai na minha frente? Ninja nunca perde pra samurai!"), (_I, "Ninja se esconde. Samurai encara.")],
    [(_I, "Você ataca pelas costas, sapo."), ("RIB", "Eu ataco por onde você não olha!")],
    [("RIB", "Shuriken contra katana. Hoje a gente resolve isso."), (_I, "Já está resolvido. Saca.")]]
ESPELHO_PROPRIO[_I] = [[(0, "Você copia a minha postura."), (1, "Ou você copia a minha?")],
                       [(0, "Só um de nós vai embainhar a espada."), (1, "Então saca primeiro.")]]
RIBBAT_PROPRIO[_I] = [("Um sapo com uma coroa?", "Ribbit."), ("Saca a sua espada, sapo.", "RIBBIT!")]
FRASES[_I] = "O vento corta."


# NOCTURNUS, o morcego-escorpião (personagem 17, v3.0, do Gomes): não fala, só faz SOM (guincho, eco, risadinha)
_N = "NOCTURNUS"
_NOCTURNUS = {
    "MAX-10": [
        [("MAX-10", "FREQUÊNCIA ULTRASSÔNICA DETECTADA. MEUS SENSORES ESTÃO... TONTOS."), (_N, "*IIIIII!*")],
        [(_N, "*hihihi...*"), ("MAX-10", "ALVO RINDO. MOTIVO: DESCONHECIDO.")],
        [("MAX-10", "MORCEGO MUTANTE. CÓDIGO DE BARRAS IGUAL AO DO MAGNUS."), (_N, "*SKREEE!*")]],
    "RIB": [
        [("RIB", "Um morcego? Sapo come inseto, não morcego!"), (_N, "*hihihi...*")],
        [(_N, "*IIIIII!*"), ("RIB", "Ai! Meus ouvidos! Para com isso!")],
        [("RIB", "Ninja trabalha no escuro também, sabia?"), (_N, "*SKREEE!*")]],
    "TRAFO": [
        [("TRAFO", "Grrr... um morcego? Eu pego no ar!"), (_N, "*hihihi...*")],
        [(_N, "*SKREEE!*"), ("TRAFO", "AUUU! Grito por grito, o meu é mais alto!")],
        [("TRAFO", "Grrr... para de voar em volta da minha cabeça!"), (_N, "*IIIIII!*")]],
    "KING RIP": [
        [("KING RIP", "Na minha época, morcego dormia de dia."), (_N, "*hihihi...*")],
        [(_N, "*IIIIII!*"), ("KING RIP", "Esse grito... até o meu chá ficou com eco.")],
        [("KING RIP", "Rápido e barulhento. Vamos ver se aguenta pancada."), (_N, "*SKREEE!*")]],
    "CANNAN": [
        [("CANNAN", "Alvo voador, sem visão noturna. Ótimo dia pra isso."), (_N, "*IIIIII!*")],
        [(_N, "*hihihi...*"), ("CANNAN", "Ele está rindo de mim? Câmbio?")],
        [("CANNAN", "Meu rádio só pega chiado perto de você."), (_N, "*SKREEE!*")]],
    "FINN": [
        [("FINN", "Um morcego mutante! Que ingrediente raro pra uma poção!"), (_N, "*SKREEE!*")],
        [(_N, "*IIIIII!*"), ("FINN", "Ai, ai! Até o meu chapéu tremeu!")],
        [("FINN", "Uma canção de ninar? Não vai me fazer dormir, criatura!"), (_N, "*hihihi...*")]],
    "KUN": [
        [("KUN", "Aposto que você não sabe jogar cartas de cabeça pra baixo."), (_N, "*hihihi...*")],
        [(_N, "*IIIIII!*"), ("KUN", "Minhas cartas embaralharam sozinhas com esse grito!")],
        [("KUN", "Um morcego... essa é a carta coringa."), (_N, "*SKREEE!*")]],
    "TROMOS": [
        [("TROMOS", "Hssssss..."), (_N, "*IIIIII!*")],
        [(_N, "*hihihi...*"), ("TROMOS", "*clic-clic-clic*")],
        [("TROMOS", "*KREEEEEE*"), (_N, "*SKREEE!*")]],
    "TAI": [
        [("TAI", "Fica parado no chão que nem gente!"), (_N, "*hihihi...*")],
        [(_N, "*SKREEE!*"), ("TAI", "Esse grito não me tira do meu círculo.")],
        [("TAI", "Hakkeyoi! Desce daí do teto!"), (_N, "*IIIIII!*")]],
    "TAMER": [
        [("TAMER", "Morcego-escorpião! Garoto, isso não existe na natureza."), (_N, "*hihihi...*")],
        [(_N, "*IIIIII!*"), ("TAMER", "Calma, garoto! O grito dele assusta, mas não morde... ainda.")],
        [("TAMER", "Pegadas não tem. Ele só voa. Fica esperto."), (_N, "*SKREEE!*")]],
    "JOHN": [
        [("JOHN", "Respeitável público: o morcego que canta!"), (_N, "*IIIIII!*")],
        [(_N, "*hihihi...*"), ("JOHN", "Para o meu próximo truque: protetor de ouvido!")],
        [("JOHN", "Na minha cartola só tem coelho, não morcego!"), (_N, "*SKREEE!*")]],
    "CRÁQUEN": [
        [("CRÁQUEN", "Arrr! Morcego na minha caverna de tesouro? Fora!"), (_N, "*SKREEE!*")],
        [(_N, "*hihihi...*"), ("CRÁQUEN", "Fantasma não dorme, bicho! Sua canção não pega em mim!")],
        [("CRÁQUEN", "Esse grito acordou até a tripulação inteira!"), (_N, "*IIIIII!*")]],
    "MAGNUS": [
        [("MAGNUS", "*RRAAWR!*"), (_N, "*IIIIII!*")],
        [(_N, "*hihihi...*"), ("MAGNUS", "*snif... snif...*")],
        [("MAGNUS", "*FWOOSH!*"), (_N, "*SKREEE!*")]],
    "FRIGANTUS": [
        [("FRIGANTUS", "*GRUUUAAH!*"), (_N, "*IIIIII!*")],
        [(_N, "*hihihi...*"), ("FRIGANTUS", "*UH-UH-UH!*")],
        [("FRIGANTUS", "*fuuuuh...*"), (_N, "*SKREEE!*")]],
    "INAZUMANEKO": [
        [(_N, "*IIIIII!*"), ("INAZUMANEKO", "Um grito não me tira o foco.")],
        [("INAZUMANEKO", "Você luta escondido no escuro. Eu luto de frente."), (_N, "*hihihi...*")],
        [(_N, "*SKREEE!*"), ("INAZUMANEKO", "Asas e ferrão. Os dois vão ser cortados.")]],
}
_NOCTURNUS["SPHYRUS"] = [  # (fora da rivalidade)
    [("SPHYRUS", "*GROOOAR!*"), (_N, "*SKREEE!*")],
    [(_N, "*hihihi...*"), ("SPHYRUS", "*clac-clac*")],
    [("SPHYRUS", "*SPLASH!*"), (_N, "*IIIIII!*")]]
for _outro, _convs in _NOCTURNUS.items():
    _chave = tuple(sorted((_N, _outro)))
    CONVERSAS[_chave] = _convs[0]
    MAIS[_chave] = _convs[1:]
# o RIVAL (rivais.py: IRMÃOS DE LABORATÓRIO): o SPHYRUS (os dois fugiram do mesmo laboratório)
RIVAIS_CONVERSAS[tuple(sorted((_N, "SPHYRUS")))] = [
    [(_N, "*IIIIII!*"), ("SPHYRUS", "*GROOOAR!*")],
    [("SPHYRUS", "*shhhhk...*"), (_N, "*hihihi...*")],
    [(_N, "*SKREEE!*"), ("SPHYRUS", "*CHOMP!*")]]
ESPELHO_PROPRIO[_N] = [[(0, "*IIIIII!*"), (1, "*IIIIIIII!!*")],
                       [(0, "*hihihi...*"), (1, "*hihihi...*")]]
RIBBAT_PROPRIO[_N] = [("*SKREEE!*", "...Ribbit."), ("*hihihi...*", "RIBBIT!")]
FRASES[_N] = "*IIIIII!*"


# SILVANUS, a planta carnívora guardiã da Floresta Antiga (personagem 18, v3.0, do Gomes): ELA fala POUQUÍSSIMO —
# frases curtas e calmas de guardiã antiga ("Este não é seu lugar.")
_S = "SILVANUS"
_SILVANUS = {
    "MAX-10": [
        [("MAX-10", "FORMA DE VIDA VEGETAL. NÍVEL DE AMEAÇA: BAIXO."), (_S, "...Raízes não aparecem no seu radar.")],
        [(_S, "Metal não cresce."), ("MAX-10", "CORRETO. METAL É ATUALIZADO.")],
        [("MAX-10", "ANALISANDO... ESSA PLANTA TEM DENTES."), (_S, "Tem.")]],
    "RIB": [
        [("RIB", "Uma planta que morde? Na minha lagoa não tem disso!"), (_S, "Este não é seu lugar.")],
        [(_S, "Pequeno sapo. Pule com cuidado."), ("RIB", "Por quê?! ...Ai! Tinha uma armadilha ali!")],
        [("RIB", "Ninja se esconde no mato. Você É o mato!"), (_S, "Então eu sempre te vejo.")]],
    "TRAFO": [
        [("TRAFO", "Grrr... vira uma planta também? Eu viro!"), (_S, "Você copia a forma. Não a raiz.")],
        [(_S, "Animal inquieto."), ("TRAFO", "AUUU! Planta parada!")],
        [("TRAFO", "Grrr... cheira a terra molhada."), (_S, "Cheira a casa.")]],
    "KING RIP": [
        [("KING RIP", "Na minha época, as plantas ficavam no vaso."), (_S, "Na minha época, não existia vaso.")],
        [(_S, "Velho mestre."), ("KING RIP", "Velha planta. Vamos ver quem tem mais paciência.")],
        [("KING RIP", "Seu chá deve ser amargo."), (_S, "Não vire o meu chá.")]],
    "CANNAN": [
        [("CANNAN", "Terreno hostil, vegetação armada. Câmbio."), (_S, "Abaixe a arma. Aqui, quem caça sou eu.")],
        [(_S, "Botas pesadas pisam nas minhas mudas."), ("CANNAN", "Desculpa, mas a missão é a missão.")],
        [("CANNAN", "Nenhum mapa mostra essa floresta."), (_S, "Ela não quer ser achada.")]],
    "FINN": [
        [("FINN", "Uma guardiã da floresta! Posso pegar uma folhinha pra poção?"), (_S, "...Uma.")],
        [(_S, "Seu fogo assusta as árvores."), ("FINN", "Prometo que é fogo do bem! ...Quase sempre.")],
        [("FINN", "Essas runas são mais velhas que o meu livro!"), (_S, "Mais velhas que o seu mestre.")]],
    "KUN": [
        [("KUN", "Aposto que você nunca perdeu um jogo de paciência."), (_S, "Nunca joguei. Só esperei.")],
        [(_S, "Cartas são feitas de árvore."), ("KUN", "...Ok, isso ficou estranho.")],
        [("KUN", "Qual é a sua carta na manga?"), (_S, "Raiz.")]],
    "TROMOS": [
        [("TROMOS", "Hssssss..."), (_S, "Volte para a sombra.")],
        [(_S, "Caçador do escuro."), ("TROMOS", "*clic-clic-clic*")],
        [("TROMOS", "*KREEEEEE*"), (_S, "Aqui, o escuro é meu.")]],
    "TAI": [
        [("TAI", "Pé no chão, que nem eu! Gostei."), (_S, "Raiz no chão. É diferente.")],
        [(_S, "Você é pesado."), ("TAI", "Hakkeyoi! É o que eu mais escuto!")],
        [("TAI", "Sai do meu círculo, plantinha!"), (_S, "O círculo é da floresta.")]],
    "TAMER": [
        [("TAMER", "Planta carnívora do tamanho de um homem. Fica perto de mim, garoto."), (_S, "Este não é seu lugar.")],
        [(_S, "Você caça na minha floresta."), ("TAMER", "Eu protejo ela. Do meu jeito.")],
        [("TAMER", "Lobo nenhum chega perto disso aí."), (_S, "Lobos são sábios.")]],
    "JOHN": [
        [("JOHN", "Para o meu próximo truque: fazer uma flor aparecer!"), (_S, "Eu faço florestas aparecerem.")],
        [(_S, "Seu coelho tem cheiro de comida."), ("JOHN", "NÃO. Nem pensar. Ele é da família!")],
        [("JOHN", "Respeitável público: a planta que morde!"), (_S, "Não sou um show.")]],
    "CRÁQUEN": [
        [("CRÁQUEN", "Arrr! Madeira boa pra consertar meu navio!"), (_S, "Toque numa árvore. Uma só.")],
        [(_S, "Você cheira a mar e a morte."), ("CRÁQUEN", "Hahaha! É o meu perfume, marujo!")],
        [("CRÁQUEN", "Tem tesouro enterrado nessas raízes?"), (_S, "Tem. E vai continuar enterrado.")]],
    "MAGNUS": [
        [("MAGNUS", "*RRAAWR!*"), (_S, "Fogo, não. Aqui, não.")],
        [(_S, "Pequeno dragão."), ("MAGNUS", "*snif... snif...*")],
        [("MAGNUS", "*FWOOSH!*"), (_S, "...Minhas folhas.")]],
    "FRIGANTUS": [
        [("FRIGANTUS", "*GRUUUAAH!*"), (_S, "O inverno passa. A floresta fica.")],
        [(_S, "Grande e peludo."), ("FRIGANTUS", "*UH-UH-UH!*")],
        [("FRIGANTUS", "*fuuuuh...*"), (_S, "Frio. Eu durmo no frio.")]],
    "SPHYRUS": [
        [("SPHYRUS", "*GROOOAR!*"), (_S, "Águas paradas. Dentes demais.")],
        [(_S, "Você também morde."), ("SPHYRUS", "*CHOMP!*")],
        [("SPHYRUS", "*SPLASH!*"), (_S, "Obrigada pela água.")]],
    "INAZUMANEKO": [
        [("INAZUMANEKO", "Uma lâmina corta qualquer planta."), (_S, "E a planta cresce de novo.")],
        [(_S, "Guerreiro paciente."), ("INAZUMANEKO", "Guardiã paciente. Lutamos com honra.")],
        [("INAZUMANEKO", "Sua floresta é silenciosa como o meu monte."), (_S, "Silêncio é força.")]],
    "NOCTURNUS": [
        [("NOCTURNUS", "*IIIIII!*"), (_S, "Shhh. A floresta dorme.")],
        [(_S, "Asas de couro, cheiro de caverna."), ("NOCTURNUS", "*hihihi...*")],
        [("NOCTURNUS", "*SKREEE!*"), (_S, "Gritar não faz a raiz soltar.")]],
}
for _outro, _convs in _SILVANUS.items():
    _chave = tuple(sorted((_S, _outro)))
    CONVERSAS[_chave] = _convs[0]
    MAIS[_chave] = _convs[1:]
# o RIVAL (rivais.py): o TAMER (o caçador que entra na floresta dela)
RIVAIS_CONVERSAS[tuple(sorted((_S, "TAMER")))] = [
    [(_S, "Caçador. De novo."), ("TAMER", "Eu só sigo as pegadas. Elas sempre me trazem aqui.")],
    [("TAMER", "Calma, garoto... essa aí já pegou um lobo meu uma vez."), (_S, "Ele pisou onde não devia.")],
    [(_S, "Saia da minha floresta."), ("TAMER", "A floresta não é sua. É de todo mundo que cuida dela.")]]
ESPELHO_PROPRIO[_S] = [[(0, "Duas raízes. Uma terra."), (1, "Só uma fica.")],
                       [(0, "...Este não é seu lugar."), (1, "...Nem o seu.")]]
RIBBAT_PROPRIO[_S] = [("...O que é você?", "...Ribbit."), ("Este não é seu lugar.", "RIBBIT!")]
FRASES[_S] = "Este não é seu lugar."


# KATCHADE, o louva-a-deus-orquídea (personagem 19, v4.0, do Gomes): calmo, fala POUCO, frases de PACIÊNCIA
# (um monge caçador que espera a hora certa: "Quem tem pressa erra o golpe.")
_K = "KATCHADE"
_KATCHADE = {
    "MAX-10": [
        [("MAX-10", "INSETO DETECTADO. TAMANHO: ANORMAL."), (_K, "...Seus olhos medem. Os meus esperam.")],
        [(_K, "Você faz barulho até parado."), ("MAX-10", "MOTORES NÃO SABEM FICAR EM SILÊNCIO.")],
        [("MAX-10", "CALCULANDO PRÓXIMO MOVIMENTO DO ALVO..."), (_K, "Eu ainda nem decidi.")]],
    "RIB": [
        [("RIB", "Um louva-a-deus?! Sapo come inseto, sabia?"), (_K, "...E louva-a-deus come sapo.")],
        [(_K, "Você pula demais, pequeno."), ("RIB", "E você fica parado demais! Tá dormindo?")],
        [("RIB", "Ninja contra... sei lá o que você é!"), (_K, "Uma flor com lâminas.")]],
    "TRAFO": [
        [("TRAFO", "Grrr... vira inseto? Eu viro inseto!"), (_K, "Pode copiar as foices. A paciência, não.")],
        [(_K, "Tanta forma... e nenhuma calma."), ("TRAFO", "AUUU! Calma é chato!")],
        [("TRAFO", "Grrr... cheiro de flor."), (_K, "É o cheiro da armadilha.")]],
    "KING RIP": [
        [("KING RIP", "Você reza antes de lutar, inseto?"), (_K, "Eu rezo DURANTE.")],
        [(_K, "Velho mestre. Você também sabe esperar."), ("KING RIP", "Esperei setenta anos. Posso esperar mais um round.")],
        [("KING RIP", "Na minha época, os insetos ficavam no jardim."), (_K, "Eu sou o jardim.")]],
    "CANNAN": [
        [("CANNAN", "Alvo camuflado na vegetação. Câmbio."), (_K, "...Você me achou. Ou eu deixei?")],
        [(_K, "Suas botas assustam a grama."), ("CANNAN", "Soldado não anda na ponta do pé.")],
        [("CANNAN", "Nunca vi um inimigo tão parado."), (_K, "Parado não é desarmado.")]],
    "FINN": [
        [("FINN", "Uau! Um louva-a-deus gigante! Posso estudar você?"), (_K, "...Depois da luta. Se você ainda quiser.")],
        [(_K, "Sua magia brilha. Brilho chama caçador."), ("FINN", "Opa. Vou brilhar mais baixinho.")],
        [("FINN", "Tem feitiço pra ficar paciente assim?"), (_K, "Tem. Chama esperar.")]],
    "KUN": [
        [("KUN", "Aposto tudo que você ataca primeiro."), (_K, "Perdeu a aposta.")],
        [(_K, "Você embaralha rápido. Eu corto mais rápido."), ("KUN", "Quer apostar?")],
        [("KUN", "Qual é a sua carta na manga?"), (_K, "Não tenho manga.")]],
    "TROMOS": [
        [("TROMOS", "Hssssss..."), (_K, "Dois caçadores. Só um come.")],
        [(_K, "Você também espera no escuro."), ("TROMOS", "*clic-clic-clic*")],
        [("TROMOS", "*KREEEEEE*"), (_K, "Gritar espanta a presa.")]],
    "TAI": [
        [("TAI", "Você é tão magrinho! Uma empurrada e cai!"), (_K, "Empurre. Se me achar.")],
        [(_K, "Pé firme no chão. Bom."), ("TAI", "Hakkeyoi! Pelo menos alguém respeita o sumô!")],
        [("TAI", "Sai do meu círculo, bichinho!"), (_K, "Eu já estava aqui antes do círculo.")]],
    "TAMER": [
        [("TAMER", "Fica atrás de mim, garoto. Esse inseto caça igual a gente."), (_K, "Igual, não. Melhor.")],
        [(_K, "Seu lobo sente meu cheiro."), ("TAMER", "E ele não gostou.")],
        [("TAMER", "Já cacei de tudo. Nunca uma flor com foice."), (_K, "Hoje é a flor que caça.")]],
    "JOHN": [
        [("JOHN", "Para o meu próximo truque: fazer um inseto sumir!"), (_K, "Eu sumo sozinho.")],
        [(_K, "Seu coelho treme."), ("JOHN", "Ele é tímido! Não olha assim pra ele!")],
        [("JOHN", "Respeitável público: o louva-a-deus!"), (_K, "...Não aplaudam. Assusta.")]],
    "CRÁQUEN": [
        [("CRÁQUEN", "Arrr! Um bicho de jardim no meu caminho!"), (_K, "O caminho também é jardim.")],
        [(_K, "Oito braços. Muita pressa."), ("CRÁQUEN", "Hahaha! Oito é melhor que duas foices, marujo!")],
        [("CRÁQUEN", "Vai virar isca de peixe!"), (_K, "Peixe nenhum chega no campo.")]],
    "MAGNUS": [
        [("MAGNUS", "*RRAAWR!*"), (_K, "Fogo no meu campo, não.")],
        [(_K, "Pequeno dragão. Grande barulho."), ("MAGNUS", "*snif... snif...*")],
        [("MAGNUS", "*FWOOSH!*"), (_K, "...Errou. Agora é minha vez.")]],
    "FRIGANTUS": [
        [("FRIGANTUS", "*GRUUUAAH!*"), (_K, "Inverno é bom. A presa fica lenta.")],
        [(_K, "Tão grande... e tão aberto."), ("FRIGANTUS", "*UH-UH-UH!*")],
        [("FRIGANTUS", "*fuuuuh...*"), (_K, "Frio. As pétalas fecham. As foices, não.")]],
    "SPHYRUS": [
        [("SPHYRUS", "*GROOOAR!*"), (_K, "Dentes demais. Paciência de menos.")],
        [(_K, "Você também caça."), ("SPHYRUS", "*CHOMP!*")],
        [("SPHYRUS", "*SPLASH!*"), (_K, "...Molhou minhas pétalas.")]],
    "INAZUMANEKO": [
        [("INAZUMANEKO", "Duas foices contra uma katana."), (_K, "Duas foices contra duas katanas. Eu contei.")],
        [(_K, "Você espera também, samurai."), ("INAZUMANEKO", "Esperar é metade do corte.")],
        [("INAZUMANEKO", "Sua postura é perfeita."), (_K, "A sua tem um furo. Eu vi.")]],
    "NOCTURNUS": [
        [("NOCTURNUS", "*IIIIII!*"), (_K, "Shhh. Grito assusta a presa.")],
        [(_K, "Asas no escuro. Eu também tenho asas."), ("NOCTURNUS", "*hihihi...*")],
        [("NOCTURNUS", "*SKREEE!*"), (_K, "Morcego come inseto. Hoje, não.")]],
    "SILVANUS": [
        [("SILVANUS", "Este não é seu lugar."), (_K, "O campo é meu lugar. A floresta é o seu.")],
        [(_K, "Flor contra flor."), ("SILVANUS", "Só uma tem raiz.")],
        [("SILVANUS", "Você caça na grama."), (_K, "E você na terra. Somos vizinhos.")]],
}
for _outro, _convs in _KATCHADE.items():
    _chave = tuple(sorted((_K, _outro)))
    CONVERSAS[_chave] = _convs[0]
    MAIS[_chave] = _convs[1:]
# o RIVAL (rivais.py): o INAZUMANEKO (lâmina contra lâmina, paciência contra paciência)
RIVAIS_CONVERSAS[tuple(sorted((_K, "INAZUMANEKO")))] = [
    [("INAZUMANEKO", "Louva-a-deus. Disseram que você corta mais rápido que eu."), (_K, "Disseram errado. Eu corto antes.")],
    [(_K, "Desembainhe, samurai."), ("INAZUMANEKO", "Quando a minha lâmina sair, a luta já acabou.")],
    [("INAZUMANEKO", "Contra-ataque contra contra-ataque... quem ataca primeiro?"), (_K, "...Ninguém. Por isso é bonito.")]]
ESPELHO_PROPRIO[_K] = [[(0, "Duas foices. Duas preces."), (1, "Uma resposta.")],
                       [(0, "...Você também está esperando."), (1, "...Sempre.")]]
RIBBAT_PROPRIO[_K] = [("...Um sapo de coroa?", "...Ribbit."), ("Quem tem pressa erra o golpe.", "RIBBIT!")]
FRASES[_K] = "Quem tem pressa erra o golpe."
