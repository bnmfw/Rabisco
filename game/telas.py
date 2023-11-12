#from prototipo.menu import Musica
import pygame
from .jogador import Jogador
from .mapa import Mapa
from .menu import *
from .poderes import *
from .entidades import classes_instanciaveis, renderizar_hitbox
from .DAOjogo import DAOJogo
from .efeitosrender import *

dicionaro_mapa = DAOJogo.mapas

class TelaPause(Sobreposicao):
    """Menu utilizado ao pausar jogo

    Funciona igual a uma tela, mas nao substitui a tela do jogo,
    apenas eh renderizada apos ela, com logica de botoes

    Possui botoes para continuar o jogo,
    ou desistir e perder automaticamente
    """
    def __init__(self,tela):
        continuar = Botao(tela.superficie.get_size()[0]/2, tela.superficie.get_size()[1]/2, 200, 50, (220, 0, 0), "Continuar", 5)
        sair = Botao(tela.superficie.get_size()[0]/2, tela.superficie.get_size()[1]/2+60, 200, 50, (220, 0, 0), "Desistir", 5)
        listabotoes = [continuar,sair]
        listatelas = [True,False,"Fechar"]
        super().__init__(listabotoes,[(50,50,50),(tela.superficie.get_size()[0]/2-120,tela.superficie.get_size()[1]/2-35,240,130)],tela,listatelas)


class InicioJogo(TelaMenu):
    """Tela apresentada ao jogador apos perder

    Caso o jogador perca toda a vida ou acabe o tempo, 
    lhe eh dada a opcao de reiniciar a fase do comeco,
    ou voltar ao menu principal
    """
    def __init__(self,superficie):
        t = superficie.get_size()
        self.__imagem = pygame.image.load("sprites/inicidojogo.png")
        self.__imagem = pygame.transform.scale(self.__imagem,t)
        iniciar = Botao(t[0]*7/8,t[1]*3/5, t[0]/5, t[0]/8, (220, 220, 60), "Menu Principal", 5,False,True)
        listabotoes = [iniciar]
        listatelas = [True, [MenuPrincipal, [superficie]]]
        cormenu = misturacor(psicodelico(0), [255, 255, 255], 1, 5)
        super().__init__(listabotoes,cormenu,superficie,listatelas)

    def atualizar(self,ciclo):
        "Atualizar especifico a tela de inicio, por conter sprite"

        self._TelaMenu__contador_menu -= 0.3
        self.fundo = misturacor(psicodelico(self._TelaMenu__contador_menu), [200, 220, 230], 1, 5)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: return [False,"BORN TO DIE",0]
            if evento.type == pygame.MOUSEBUTTONDOWN:
                acao = self.clicar()
                if type(self.listatelas[acao]) == bool:
                    return [self.listatelas[acao],"WORLD IS A FUCK",acao]
                return self.listatelas[acao] + [acao]
        self.superficie.fill(self.fundo)           #preenche o fundo
        self.superficie.blit(self.__imagem,[0,0]) 
        for i in self._TelaMenu__listabotoes:            #renderiza cada botao
            i.renderizar(self.superficie)
        pygame.display.flip()
        return [True,"Kill Em All 1989",0]


class MenuPrincipal(TelaMenu):
    """Menu principal do jogo
    
    Temporariamente possui botoes para testar cada fase

    Tambem possui botoes para ir a tela de selecao de arquivo de save,
    para a tela de configuracoes,
    e para sair do jogo.
    """
    def __init__(self, superficie):
        t = superficie.get_size()
        botaojogar = Botao(t[0]/2, t[1]/4, t[0]/3, t[1]/6, (30, 220, 30),  "Jogar", 10,tamanho_fonte=48)
        botaoconfig = Botao(t[0]/2, t[1]/2, t[0]/3, t[1]/6, (0, 220, 180), "Configurações", 10,tamanho_fonte=48)
        botaosair = Botao(t[0]/2, t[1]*3/4, t[0]/3, t[1]/6, (220, 30, 30), "Sair", 10,tamanho_fonte=48)
        cormenu = misturacor(psicodelico(0), [255, 255, 255], 1, 5)
        listabotoes = [botaosair, botaojogar, botaoconfig]
        listatelas = [True, False, [CarregarJogo, [superficie]],[Configuracoes,[superficie]]]
        super().__init__(listabotoes, cormenu, superficie,listatelas)
        pygame.mixer.music.stop()


class CarregarJogo(TelaMenu):
    """ Menu de selecionar save game

    O jogador pode selecionar um espaco vazio para iniciar um novo jogo,
    selecionar um ja ocupado para iniciar o jogo gravado nele,
    ou deletar um dos jogos ativos.
    """
    def __init__(self,superficie):
        slots = DAOJogo.saves
        
        encaixe = [slots[str(i)] for i in range(5)]
        deletar_encaixe = ["Deletar" if slots[str(i)][0] != "Novo Jogo" else False for i in range(5)]

        t = superficie.get_size()
        botoes_encaixe = [Botao(t[0]/3, max(75,t[1]/10)+i*max(60,t[1]/8), max(t[0]*2/3,400), 50, (60, 220, 20), encaixe[i][0], 5) if deletar_encaixe[i] == "Deletar"
                        else Botao(t[0]/3,  max(75,t[1]/10)+i*max(60,t[1]/8), max(t[0]*2/3,400), 50, (160, 160, 160), encaixe[i][0], 5) for i in range(5)]
        sair = Botao(90,t[1]-35, 160, 50, (220, 20, 60), "Sair", 5)
        botoes_deletar = [Botao(t[0]*3/4,  max(75,t[1]/10)+i*max(60,t[1]/8), 100, 40, (220, 20, 60), "Deletar", 5) if deletar_encaixe[i] == "Deletar" 
                        else Botao(-1000, -1000, 50, 50, (0,0,0), "", 5) for i in range(5)]
        texto = Botao(200, 20, 400, 40, (200, 200, 200), "Escolha de Jogo Salvo", 5,True)
        
        listabotoes = botoes_encaixe + botoes_deletar + [sair] + [texto]

        listatelas = [True]
        listatelas += [[TelaDeJogo, [superficie, encaixe[i][1], str(i)]] for i in range(5)]
        listatelas += [[DeletarSave, [superficie, str(i)]] for i in range(5)]
        listatelas += [[MenuPrincipal, [superficie]]] + [True]

        cormenu = misturacor(psicodelico(0), [255, 255, 255], 1, 5)
        super().__init__(listabotoes,cormenu,superficie,listatelas)


class DeletarSave(TelaMenu):
    """Tela que apaga um jogo salvo

    Apos apertar um dos botoes de deletar na tela de escolha,
    o jogador devera confirmar se quer mesmo deletar seu jogo salvo

    Ambos botoes levam o jogador de volta para a tela de selecao,
    mas confirmar tambem apaga o slot selecionado
    """
    def __init__(self,superficie,save):
        t = superficie.get_size()
        self.__save = save
        texto = Botao(t[0]/2, t[1]/3, 550, 150, (200, 200, 200), "Quer mesmo deletar esse jogo salvo?", 5,True)
        deletar = Botao(t[0]/2+150, t[1]/3+150, 260, 50, (220, 20, 60), "Deletar", 5)
        cancelar = Botao(t[0]/2-150, t[1]/3+150, 260, 50, (60, 220, 20), "Cancelar", 5)
        listabotoes = [deletar,cancelar,texto]
        listatelas = [True, [CarregarJogo, [superficie]], [CarregarJogo, [superficie]], True]
        cormenu = misturacor(psicodelico(0), [255, 255, 255], 1, 5)
        super().__init__(listabotoes,cormenu,superficie,listatelas)

    def atualizar(self,ciclo):
        """Como outras telas, checa cada botao e responde de acordo

        Se o botao apertado for o de deletar,
        ele salva no arquivo de saves que o slot esta vazio
        """
        resultado = super().atualizar(ciclo)
        if resultado[2] == 1: # CONFIRMAR DELECAO
            slots = DAOJogo.saves
            slots[self.__save] = ["Novo Jogo","fase1","Cinza","Cinza",0]
            DAOJogo.saves = slots
        return resultado


class FimDeJogo(TelaMenu):
    """Tela apresentada ao jogador apos perder

    Caso o jogador perca toda a vida ou acabe o tempo, 
    lhe eh dada a opcao de reiniciar a fase do comeco,
    ou voltar ao menu principal
    """
    def __init__(self,superficie,nivel,save):
        t = superficie.get_size()
        texto = Botao(t[0]/2, t[1]/3, 550, 150, (200, 200, 200), "Você perdeu...", 5,True)
        continuar = Botao(t[0]/2+150, t[1]/3+150, 260, 50, (160, 220, 60), "Tentar Novamente", 5)
        voltar = Botao(t[0]/2-150, t[1]/3+150, 260, 50, (220, 220, 60), "Menu Principal", 5)
        listabotoes = [voltar,continuar,texto]
        listatelas = [True, [MenuPrincipal, [superficie]], [TelaDeJogo, [superficie, nivel, save]], True]
        cormenu = misturacor(psicodelico(0), [255, 255, 255], 1, 5)
        super().__init__(listabotoes,cormenu,superficie,listatelas)


class Configuracoes(TelaMenu):
    """ Tela de configuracoes de jogo

    Altera configuracoes referentes ao jogo,
    salvando-as em um arquivo json para serem iniciadas
    quando o jogo for iniciado pela proxima vez.

    Configuracoes padroes, quando se joga pela primeira vez
    acaba sendo lidada pelo Jogo.
    """
    def __init__(self,superficie):
        configs = DAOJogo.configs
        self.__tamanho = configs["resolucao"]
        self.__volume_musica = configs["musica"]
        self.__volume_efeitos = configs["efeitos"] ### IMPLEMENTAR VOLUME DE EFEITOS SONOROS!!! ###
        self.__tela_cheia = configs["telacheia"]
        t = self.__tamanho
    
        sair = Botao(120, superficie.get_size()[1]-45, 200, 50, (220, 60, 60), "Salvar e Sair", 5)

        musica = Botao(360, 120, 140, 50, (200, 200, 200), "Musica: "+ str(int(round(self.__volume_musica,1)*100)), 5,True)
        musica_mais = Botao(360, 70, 40, 40, (160, 220, 60), "+", 5)
        musica_menos = Botao(360, 170, 40, 40, (220, 160, 60), "-", 5)

        efeitos = Botao(520, 120, 140, 50, (200, 200, 200), "Efeitos:100", 5,True)
        efeitos_mais = Botao(520, 70, 40, 40, (160, 220, 60), "+", 5)
        efeitos_menos = Botao(520, 170, 40, 40, (220, 160, 60), "-", 5)

        tela = Botao(140, 120, 120, 80, (200, 200, 200), "({}x{})".format(*self.__tamanho), 5,True)
        tela_largura_menos = Botao(40, 120, 60, 40, (220, 160, 60), "-100", 5)
        tela_largura_mais = Botao(240, 120, 60, 40, (160, 220, 60), "+100", 5)
        tela_altura_menos = Botao(140, 190, 60, 40, (220, 160, 60), "-100", 5)
        tela_altura_mais = Botao(140, 50, 60, 40, (160, 220, 60), "+100", 5)

        tela_cheia = Botao(295, 240, 150, 40, (160, 220, 60) if self.__tela_cheia else (220,160,60), "Tela Cheia", 5)

        creditos = Botao(295, 300, 150, 40, (160, 220, 60), "Créditos", 5)

        listabotoes = [sair,musica,musica_mais,musica_menos,efeitos,efeitos_mais,efeitos_menos,
                        tela,tela_largura_menos,tela_largura_mais,tela_altura_menos,tela_altura_mais,tela_cheia,creditos]
        listatelas = [True, [MenuPrincipal, [superficie]]] + [True for i in range(12)] + [[Creditos, [superficie]]]
        cormenu = misturacor(psicodelico(0), [255, 255, 255], 1, 5)
        super().__init__(listabotoes,cormenu,superficie,listatelas)

    def atualizar(self,ciclo):
        """Como outras telas, checa cada botao e responde de acordo

        Possui botoes para alterar a altura e largura da tela,
        alterar entre tela cheia e janela,
        o volume da musica e dos efeitos,
        acessar a tela de creditos do jogo,
        e voltar ao menu principal

        return proxima tela como definido no atualizar da superclasse
        """
        resultado = super().atualizar(ciclo)
        acao = resultado[2]
        if acao == 1: # SAIR, SALVAR E APLICAR CONFIGS
            if self.__tela_cheia: pygame.display.set_mode((0,0), pygame.FULLSCREEN)
            else: pygame.display.set_mode(self.__tamanho,0)
            self.salvar_config()
        elif acao == 3: # AUMENTAR VOLUME - MAX: 100
            pygame.mixer.music.set_volume(min(round(pygame.mixer.music.get_volume(),1)+0.1,1))
            self.__volume_musica = round(pygame.mixer.music.get_volume(),1)
            self.listabotoes[1].texto = "Musica: "+ str(int(round(pygame.mixer.music.get_volume(),1)*100))
        elif acao == 4: # DIMINUIR VOLUME - MIN: 0
            pygame.mixer.music.set_volume(max(round(pygame.mixer.music.get_volume(),1)-0.1,0))
            self.__volume_musica = round(pygame.mixer.music.get_volume(),1)
            self.listabotoes[1].texto = "Musica: "+ str(int(round(pygame.mixer.music.get_volume(),1)*100))
        elif acao == 9: # DIMINUIR LARGURA DA TELA - MIN: 600
            self.__tamanho[0] = max(600,self.__tamanho[0]-100)
        elif acao == 10: # AUMENTAR LARGURA - MAX: 1400
            self.__tamanho[0] = min(1400,self.__tamanho[0]+100)
        elif acao == 11: # DIMINUIR ALTURA - MIN: 400
            self.__tamanho[1] = max(400,self.__tamanho[1]-100)
        elif acao == 12: # AUMENTAR ALTURA - MAX: 800
            self.__tamanho[1] = min(800,self.__tamanho[1]+100)
        elif acao == 13: # ALTERNAR TELA CHEIA
            self.__tela_cheia = not self.__tela_cheia
            self.listabotoes[12].cor = (160, 220, 60) if self.__tela_cheia else (220,160,60)
        elif acao == 14: # SALVAR CONFIGS PARA ENTRAR NOS CREDITOS
            self.salvar_config()
        self.listabotoes[7].texto = "({}x{})".format(*self.__tamanho)
        return resultado

    def salvar_config(self):
        "Salva as configuracoes definidas para o arquivo json"
        DAOJogo.configs = {"resolucao":self.__tamanho,
                "musica":self.__volume_musica,
                "efeitos":self.__volume_efeitos,
                "telacheia":self.__tela_cheia}


class Creditos(TelaMenu):
    """ Tela de Creditos, todos que criaram algo neste jogo

    Botoes simplesmente mostram a funcao e nome de cada um,
    seja artista ou programador, exceto o que retorna as configuracoes
    """
    def __init__(self,superficie):
        w,h = superficie.get_size()

        listabotoes = [Botao(120, h-45, 200, 50, (220, 60, 60), "Voltar", 5)]
        listabotoes.append(Botao(w/2, 90, 100, 50, (220, 220, 220), "Créditos", 5,True))
        listapessoas = [   ### COLOCAR AQUI NOMES E CREDITOS
            ["Música","André Hanazaki Peroni",(220,0,0)],
            ["Entidades e Movimento","Arthur João Lourenço",(220,110,0)],
            ["Inimigos e Colisão","Bernardo Borges Sandoval",(220,220,0)],
            ["Menus e Persistência","Otávio Wada",(0,220,0)],
            ["Sprites","Vicente Tavares Alves Ferreira",(0,220,220)],
            ["Classes Abstratas, Impl. Música","Victor Cunha",(160,0,220)]]
        for pessoa in listapessoas:
            listabotoes.append(Botao(w/2+200, 150 + listapessoas.index(pessoa)*60, 375, 50, pessoa[2], pessoa[0], 5,True))
            listabotoes.append(Botao(w/2-200, 150 + listapessoas.index(pessoa)*60, 375, 50, pessoa[2], pessoa[1], 5,True))
        listatelas = [True,[Configuracoes,[superficie]]] + [True for i in range(2*len(listapessoas)+1)]
        cormenu = misturacor(psicodelico(0), [255, 255, 255], 1, 5)
        super().__init__(listabotoes,cormenu,superficie,listatelas)
    

class TelaDeJogo(Tela):
    """ Tela responsavel pelo nivel em si

    Guarda algumas das variaveis utilizadas no jogo,
    enquanto outras pertencem ao mapa sendo utilizado

    @param superficie: superficie pygame
    @param nivel: nome do nivel a ser carregado
    @param slot: slot de jogo salvo selecionado
    """
    def __init__(self, superficie, nivel, slot):
        global dicionaro_mapa
        super().__init__(superficie)
        (width, height) = superficie.get_size()
        self.__campo_visivel = pygame.Rect(0, 0, width, height)
        self.__comeco = 0
        self.__tempo_maximo = 350
        self.__fonte = pygame.font.SysFont('miriam', 48)
        self.__atrasofim = 0
        self.__nivel = nivel
        self.__slot = slot
        self.__sobreposicao = None

        ##### ENTRADAS DO JOGADOR #####
        self.__cima, self.__baixo, self.__direita, self.__esquerda = 0, 0, 0, 0
        self.__espaco = False
        self.__bola_fogo = False
        self.__troca_poder = False

        ##### MAPA #####
        self.__mapa = Mapa(superficie)
        poder_atual = Cinza()
        poder_armazenado = Cinza()
        slots = DAOJogo.saves
        slot_atual = slots[self.__slot]
        for item in poderes_no_jogador:
            if item.__name__ == slot_atual[2]:
                poder_atual = item()
            if item.__name__ == slot_atual[3]:
                poder_armazenado = item()
        self.__jogador = self.__mapa.iniciar(nivel,dicionaro_mapa, poder_atual, poder_armazenado, slot_atual[4])
        self.__comeco = pygame.time.get_ticks() / 1000
        if not pygame.mixer.music.get_busy(): pygame.mixer.music.play(-1)



    def salvar_jogo(self):
        "Salva o jogo ao ganhar ou perder"
        slots = DAOJogo.saves
        slots[self.__slot] = [self.__nivel,self.__nivel, type(self.__jogador.poder).__name__,
                                type(self.__jogador.poder_armazenado).__name__, self.__jogador.paleta]
        DAOJogo.saves = slots

    def atualizar(self, ciclo):
        '''Logica de jogo, envolvendo controles, colisao e renderizacao

        Deve ser chamada pela funcdao gerente 60 vezes por segundo

        @param ciclo: responsavel pelas frames de animacao do Rabisco
        
        @returns: Instancia da proxima tela a ser executada apos o nivel
                  [False] se o jogo for fechado,
                  [True] se o jogo continuar na frame seguinte
        '''
        if isinstance(self.__sobreposicao,Sobreposicao): pausado = True
        else: pausado = False
        if not pausado:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.salvar_jogo()
                    return [False]
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_w: self.__cima = 5
                    if evento.key == pygame.K_s: self.__baixo = 5
                    if evento.key == pygame.K_d:
                        self.__direita = 0.5
                    if evento.key == pygame.K_a:
                        self.__esquerda = 0.5
                    if evento.key == pygame.K_SPACE or evento.key == pygame.K_w: self.__espaco = True
                    if evento.key == pygame.K_ESCAPE:
                        self.__sobreposicao = TelaPause(self)
                    if evento.key == pygame.K_TAB:
                        self.__troca_poder = True
                if evento.type == pygame.KEYUP:
                    if evento.key == pygame.K_w: self.__cima = 0
                    if evento.key == pygame.K_s: self.__baixo = 0
                    if evento.key == pygame.K_d:
                        self.__direita = 0
                    if evento.key == pygame.K_a:
                        self.__esquerda = 0
                    if evento.key == pygame.K_SPACE or evento.key == pygame.K_w: self.__espaco = False
                    if evento.key == pygame.K_TAB:
                        self.__troca_poder = False
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    self.__bola_fogo = True
                elif evento.type == pygame.MOUSEBUTTONUP:
                    self.__bola_fogo = False
        else:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.salvar_jogo()
                    return False
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.__sobreposicao = None
            self.__direita = 0
            self.__esquerda = 0
            self.__cima = 0
            self.__baixo = 0
            self.__espaco = False
            self.__bola_fogo = False
            self.__troca_poder = False

        ##### FILA DE RENDERIZACAO E ATUALIZACAO #####

        self.__mapa.atualizar(self.superficie, self.__campo_visivel, self.superficie.get_size(),ciclo)

        # FAZER O JOGADOR RECEBER UM MAPA E SALVAR ONDE ELE TA
        if self.__atrasofim > 0:
            self.__direita = 0
            self.__esquerda = 0
            self.__espaco = not self.__mapa.ganhou
        else:
            self.__jogador.poderes(self.superficie, self.__mapa, self.__bola_fogo)
        self.__campo_visivel = self.__jogador.atualizar(self.superficie,self.__mapa,
                                                        [self.__direita, self.__esquerda, self.__espaco, self.__troca_poder])

        # PERDENDO POR MORRER
        if self.__jogador.vida <= 0 and not self.__mapa.ganhou:
            self.__jogador.vida_pra_zero()
            self.__atrasofim += 1
            if self.__atrasofim <= 1:
                self.__textin = self.__fonte.render("FIM DE JOGO", False, (0, 0, 0))
                pygame.mixer.music.fadeout(2400)
                if self.__mapa.escala_tempo > 1:
                    self.__textin = pygame.font.SysFont('msminchomspmincho', 48).render("神の御名（みめい）においてしりそける", False, (0, 0, 0))
            else:
                self.__jogador.tipos_transparentes = classes_instanciaveis
            self.superficie.blit(self.__textin, (self.__campo_visivel.w/2 - self.__textin.get_size()[0] / 2, self.__campo_visivel.h/2 - self.__textin.get_size()[1] / 2))
            if self.__atrasofim >= 150:
                self.salvar_jogo()
                return [FimDeJogo, [self.superficie, self.__nivel, self.__slot]]

        ### VENCENDO ###
        if self.__mapa.ganhou:
            self.__atrasofim += 1
            #if self.__atrasofim <= 1:
                #pygame.mixer.music.fadeout(2400)
            self.__textin = self.__fonte.render("VITÓRIA", False, (0, 0, 0))
            self.superficie.blit(self.__textin, (self.__campo_visivel.w/2 - self.__textin.get_size()[0] / 2, self.__campo_visivel.h/2 - self.__textin.get_size()[1] / 2))
            if self.__atrasofim >= 150:
                self.salvar_jogo()
                return [TelaDeJogo, [self.superficie, self.__mapa.proxima_fase, self.__slot]] if self.__mapa.proxima_fase else [MenuPrincipal, [self.superficie]]

        ##### TELA DE PAUSE NO JOGO #####
        try:
            resultado = self.__sobreposicao.atualizar(ciclo)
            if not resultado:
                self.__sobreposicao = None
            elif resultado == "Fechar":
                self.salvar_jogo()
                pygame.mixer.music.fadeout(500)
                return [FimDeJogo, [self.superficie, self.__nivel, self.__slot]]
        except AttributeError:
            pass

        ### FLIP PARA PASSAR PARA A TELA, LOGICA DE TEMPO
        pygame.display.flip()
        self.__tempo_maximo += (1 - self.__mapa.escala_tempo) / 60
        tempo_decorrido = pygame.time.get_ticks() / 1000 - self.__comeco
        if not self.__mapa.ganhou:
            self.__mapa.tempo_restante = int(max(self.__tempo_maximo - tempo_decorrido, 0))

        ### PERDENDO POR TEMPO
        if self.__mapa.tempo_restante == 0:
            self.__jogador.vida_pra_zero()
        return [True]