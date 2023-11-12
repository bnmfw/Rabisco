import pygame
import json

class Sprite():
    def __init__(self, arquivo):
        arquivo = "sprites/"+arquivo
        self.__imagem = arquivo+".png"
        self.__sprite_sheet = pygame.image.load(self.__imagem).convert_alpha()
        self.__arquivo_dados = arquivo+".json"
        self.__dados = {}
        with open(self.__arquivo_dados) as f:
            self.__dados = json.load(f)

    @property
    def imagem(self):
        return self.__imagem

    def imprimir(self, tela, nome, posx, posy, orientacao = None, velx = None, vely = None, frame = 0, largura = None, altura = None):
        if orientacao == 1: nome = nome + "_right"
        elif orientacao == -1: nome = nome + "_left"
        if velx: nome = nome + "_walk"
        if self.__imagem != "sprites/sprites.png": nome = nome + "_" + str(frame)
        self.carregar_sprite(nome, posx, posy, largura, altura, tela)

    def carregar_sprite(self, nome, posx, posy, width, height, tela):
        sprite = self.__dados[nome]
        x, y, w, h = sprite["x"], sprite["y"], sprite["w"], sprite["h"]
        if nome == "chao":
            ciclos_completos = int(width/w)
            extra = width - ciclos_completos * w
            for i in range(ciclos_completos):
                tela.blit(self.__sprite_sheet, (posx+i*w, posy), (x, y, w, h))
            tela.blit(self.__sprite_sheet, (posx+ciclos_completos*w, posy), (x, y, extra, h))
        else:
            if width: w = width
            if height: h = height
            tela.blit(self.__sprite_sheet, (posx, posy), (x, y, w, h))