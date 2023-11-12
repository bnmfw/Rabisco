import pygame
from efeitosrender import *

class Janela:
    """Classe que segura a tela atual,
    pertence ao objeto jogo que a instanciar

    Atualiza a tela quando o jogo mandar
    """
    def __init__(self, tela):
        self.__tela = tela
    
    @property
    def tela(self):
        return self.__tela
    
    @tela.setter
    def tela(self, telanova):
        self.__tela = telanova

    def atualizar(self):
        self.tela.atualizar()


class Tela:
    """Classe base para qualquer tela que exista no jogo

    Divide-se em TelaMenu, a qual envolve gerenciar botoes
    e Tela_Jogo, que envolve logica de jogatina
    """
    def __init__(self,superficie):
        self.__superficie = superficie
    
    @property
    def superficie(self):
        return self.__superficie #superficie a se desenhar
    
    def atualizar(self, ciclo):
        pass


class TelaMenu(Tela):
    """Tela do jogo, utilizada para navegar entre os menus

    Este tipo de tela se caracteriza pelo uso de botoes.
    A cada atualizacao, checa se, e qual, botao foi apertado
    e reage apropriadamente

    A maioria dos fundos desses menus ciclam em cor, 
    representando o Guri em sua jornada artistica.

    @param listabotoes: lista de objetos botoes
    @param fundo: representacao r,g,b da cor do fundo
    @param superficie: superficie pygame da janela

    @param listatelas: lista que define a tela que 
    substitui esta quando o botao correspondente eh clicado
    Cada elemento desta fica tipicamente no formato a seguir:
    [Classe_Da_Tela,[*parametros_da_tela],index_do_botao]

    """
    def __init__(self,listabotoes:list,fundo:list,superficie,listatelas):
        super().__init__(superficie)
        self.__listatelas = listatelas
        self.__listabotoes = listabotoes        #lista de objetos Botao
        self.__fundo = fundo                    #[red,green,blue] do fundo 
        self.__contador_menu = 0
        self.musica = False
        

    
    @property
    def fundo(self):
        return self.__fundo
    
    @fundo.setter
    def fundo(self,fundo):
        self.__fundo = fundo
    
    def atualizar(self,ciclo):
        """Checa os botoes e retorna a tela correspondente ao clicado

        Primeiramente incrementa o contador:
        @param ciclo: ciclo atual de jogo em frames
        para criar o efeito de cores do menu

        Depois, checa se botoes foran clicados, e retorna
        o valor correspondente, apos renderiza-los

        return  [False,X,X] se o jogo for fechado,
        o que eh tratado pelo objeto jogo como sendo
        uma ordem de encerramento
                [True,X,X] se nao houve clique ou
                [0,X,X] se o clique nao foi em um botao,
        ambos interpretados como continue nesta tela
                [Tela,[*param],index(botao)+1]
        se algum botao for apertado
        """

        self.__contador_menu -= 0.3
        self.fundo = misturacor(psicodelico(self.__contador_menu), [200, 220, 230], 1, 5)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: return [False,"BORN TO DIE",0]
            if evento.type == pygame.MOUSEBUTTONDOWN:
                acao = self.clicar()
                if type(self.listatelas[acao]) == bool:
                    return [self.listatelas[acao],"WORLD IS A FUCK",acao]
                return self.listatelas[acao] + [acao]
        self.superficie.fill(self.__fundo)           #preenche o fundo
        for i in self.__listabotoes:            #renderiza cada botao
            i.renderizar(self.superficie)
        pygame.display.flip()
    


        return [True,"Kill Em All 1989",0]
    
    def clicar(self):
        """Caso o jogo detecte um clique, retornar o botao

        return o indice do primeiro botao
        acima do qual o mouse esta + 1

        O indice 0 eh reservado para a acao de nao fazer nada
        """
        for i in self.__listabotoes:
            if i.clicar():  return self.__listabotoes.index(i)+1
        else: return 0

    @property
    def listatelas(self):
        return self.__listatelas
    
    @property
    def listabotoes(self):
        return self.__listabotoes
    
class Botao:
    """Elemento da UI Grafica, principal metodo de entrada nos menus do jogo

    Tambem pode ser usado cmo saida de dados caso seja estatico e mutavel
    @param posicao, tamanho, cor
    """
    def __init__(self,x,y,w,h,cor,texto,borda,estatico=False,invisivel=False,tamanho_fonte=28):
        ### tamanho,posicao,cor e texto do botao
        self.__x = x-w/2
        self.__y = y-h/2
        self.__w = w
        self.__h = h
        self.__centro = [x,y,w,h]
        self.__cor = cor
        self.__corhover = [cor[0]*3/4,cor[1]*3/4,cor[2]*3/4] if not estatico else cor
        self.__textsf = pygame.font.SysFont('miriam',tamanho_fonte).render(texto,True,(0,0,0))
        self.__texttamanho = self.__textsf.get_size()
        self.__borda = borda
        self.__estatico = estatico
        self.__invisivel = invisivel

    @property
    def cor(self):
        return self.__cor
    
    @cor.setter
    def cor(self,cor):
        self.__cor = cor
        self.__corhover = [cor[0]*3/4,cor[1]*3/4,cor[2]*3/4] if not self.__estatico else cor
    
    @property
    def texto(self):
        return self.__textsf
    
    @texto.setter
    def texto(self,texto):
        self.__textsf = pygame.font.SysFont('miriam',28).render(texto,True,(0,0,0))
        self.__texttamanho = self.__textsf.get_size()

    def renderizar(self,superficie):
        """Renderizacao do botao na tela

        Passa um retangulo base, um retangulo colorido,
        e uma area de texto a fila de renderizacao

        A cor do retangulo depende de se o botao esta com
        o ponteiro do mouse em cima dele, indicando que clicar
        o ativara
        
        """
        if not self.__invisivel:
            pos = pygame.mouse.get_pos()
            pygame.draw.rect(superficie,(0,0,0),[self.__x,self.__y,self.__w,self.__h])

            cor = self.__corhover if self.__x <= pos[0] <= self.__x + self.__w and self.__y <= pos[1] <= self.__y + self.__h else self.cor
            pygame.draw.rect(superficie,cor,[self.__x+self.__borda,self.__y+self.__borda,self.__w-2*self.__borda,self.__h-2*self.__borda])

            superficie.blit(self.__textsf,[self.__centro[0]-self.__texttamanho[0]/2,self.__centro[1]-self.__texttamanho[1]/2])
        

    def clicar(self):
        """ Funcao de clicar neste botao em especifico
        Return True se foi apertado senao False
        """
        pos = pygame.mouse.get_pos()
        if self.__x <= pos[0] <= self.__x + self.__w and self.__y <= pos[1] <= self.__y + self.__h:
            return True
        else:
            return False


class Sobreposicao(TelaMenu):
    "Documentado em TelaPause"
    def __init__(self,listabotoes:list,fundo:list,tela,listatelas):
        super().__init__(listabotoes,fundo,tela.superficie,listatelas)
        self.__tela_superior = tela
    
    def atualizar(self,ciclo):
        """Gerencia o menu da sobreposicao

        return True se nada acontece,
            False se o jogo fechar,
            acao correspondente se algum botao for apertado
        """
        pygame.draw.rect(self.superficie,*self.fundo)
        for i in self.listabotoes:
            i.renderizar(self.superficie)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: return False
        if pygame.mouse.get_pressed()[0]:
            acao = self.clicar()
            return self.listatelas[acao]
        return True



