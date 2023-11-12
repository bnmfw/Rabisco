import json, pygame, os
from .mapa import montar_mapas
from .entidades import *

class DAO:
    """Classe responsavel por dados de mapa, jogos salvos, e configs
    
    Configuracoes incluem tamanho de tela, tela cheia,
    volume de musica e efeitos

    Jogos salvos incluem nome da fase, a fase em si, poderes guardados

    Dados de mapa incluem inimigos, obstaculos e coletaveis,
    definidos pela funcao montar_mapas
    """
    def __init__(self):
        self.carregar_configs()
        self.carregar_saves()
        self.carregar_mapas()
    
    def carregar_configs(self):
        try:
            self.__configs = json.load(open("data/configs.json","r"))
        except FileNotFoundError:
            configs = {"resolucao":[1000,600],
                "musica":1,
                "efeitos":1,
                "telacheia":False}
            json.dump(configs,open("data/configs.json","w"))
            self.__configs = configs
    
    def carregar_saves(self):
        try:
            self.__saves = json.load(open("data/saves.json","r"))
        except FileNotFoundError:
            slots = {'0':["Novo Jogo","fase1","Cinza","Cinza",0],'1':["Novo Jogo","fase1","Cinza","Cinza",0],
                        '2':["Novo Jogo","fase1","Cinza","Cinza",0],'3':["Novo Jogo","fase1","Cinza","Cinza",0],
                        '4':["Novo Jogo","fase1","Cinza","Cinza",0],'6':["Novo Jogo","fase1","Cinza","Cinza",0]}
            json.dump(slots,open("data/saves.json","w"))
            self.__saves = slots
    
    def carregar_mapas(self):
        try:
            if modo_dev:
                raise FileNotFoundError
            self.__mapas = json.load(open("data/mapas.json","r"))
        except FileNotFoundError:
            with open("data/mapas.json","w") as mapa_arquivo:
                mapas = montar_mapas()
                json.dump(mapas, mapa_arquivo)
                self.__mapas = mapas
    
    def carregar_sprites(self):
        pass

    @property
    def configs(self):
        return self.__configs
    
    @configs.setter
    def configs(self,configs):
        self.__configs = configs
        json.dump(configs,open("data/configs.json","w"))

    @property
    def mapas(self):
        return self.__mapas
    
    @mapas.setter
    def mapas(self,mapas):
        self.__mapas = mapas
        json.dump(mapas,open("data/mapas.json","w"))
    
    @property
    def saves(self):
        return self.__saves
    
    @saves.setter
    def saves(self,saves):
        self.__saves = saves
        json.dump(saves,open("data/saves.json","w"))

DAOJogo = DAO()