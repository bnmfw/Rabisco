import pygame, random, json
from mapa import *
from menu import *
from efeitosrender import *
from telas import *


class Jogo:
    def __init__(self):
        ###### INFORMACOES TA TELA ######
        try:
            configs = json.load(open("configs.json","r"))
        except FileNotFoundError:
            configs = {"resolucao":[1000,600],
                "musica":1,
                "efeitos":1,
                "telacheia":False}
            json.dump(configs,open("configs.json","w"))
        
        (width, height) = configs["resolucao"]  # Tamanho da tela
        pygame.mixer.music.set_volume(configs["musica"])
        if configs["telacheia"]: self.__screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        else: self.__screen = pygame.display.set_mode((width, height)) 

        caption = ["O Risco do Rabisco: A Jornada das Cores"]
                   #  "As Aventuras do Guri",
                   # "A Aventura Bizarra de Guri",
                   # "Super Guri Bros",
                   # "Arte-lharida",
                   # "Uma Pincelada de Vigor",
                   # "Entre Riscos e Rabiscos"]
        pygame.display.set_caption(random.choices(caption,[1])[0])

        self.__ciclo = 0
        self.__janela = Janela(MenuPrincipal(self.__screen))
        self.__relogio = pygame.time.Clock()


    def menu_inicial(self):  # Menu inicial do jogo
        self.__janela.tela = InicioJogo(self.__screen)
        while True:
            self.__ciclo += 1
            acao = self.__janela.tela.atualizar(self.__ciclo)

            ### se acao == 0, nao fazer nada
            ### caso contrario, fazer a acao correspondente ao botao descrito

            if acao[0] == False:
                break
            elif isinstance(acao,list):
                try:
                    self.__janela.tela = acao[0](*acao[1])
                except IndexError:
                    "nada muda"
                except TypeError:
                    "onaji desu"
            self.__relogio.tick(60)

pygame.init()
pygame.mixer.music.load('musica_fundo.ogg')
jogo = Jogo()
jogo.menu_inicial()
