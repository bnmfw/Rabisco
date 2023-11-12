import pygame
from .entidades import *
from .sprites import *


# FUNCOES DE ATUALIZAR NECESSITAM DA AREA VISIVEL PARA RENDERIZAR CORRETAMENTE
class Obstaculo(Estatico):
    "Base para objetos fisicos que nao sao inimigos"
    def __init__(self, nome: str, x: int, y: int, altura: int, largura: int, arquivo: str, cor: tuple):
        super().__init__(nome, x, y, altura, largura, arquivo, cor)

@instanciavel
class PlataformaMovel(Movel):
    def __init__(self, y: int , x: int, largura: int, vely):
        altura = 19
        super().__init__("chao", x, y, altura, largura, 5, "sprites",  [], (184, 20, 20))
        self.vely = vely

    def renderizar_sprite(self, tela, mapa):
        self.sprite.imprimir(tela, "chao",
                             self.x - mapa.campo_visivel.x,
                             self.y - mapa.campo_visivel.y,
                             largura=self.largura,
                             altura=self.altura)

    def mover(self, dimensoesTela, mapa):
        ##### REPOSICIONAMENTO DA PLATAFORMA #####
        self.y += self.vely * mapa.escala_tempo
        if self.y >= mapa.tamanho[1]:
            self.y = 2
        elif self.y <= 0:
            self.y = mapa.tamanho[1] - 2


@instanciavel
class Bloco(Obstaculo):
    def __init__(self, nome: str, x: int, y: int):
        largura = 30
        altura = 30
        super().__init__(nome, x, y, altura, largura, "0", (255, 102, 0))


@instanciavel
class Lapis(Obstaculo):
    def __init__(self, x: int, topo: int, base: int):
        largura = 44
        altura = base - topo
        super().__init__("lapis", x, topo, altura, largura, "sprites", (255, 255, 0))


@instanciavel
class Ponta(Obstaculo):
    def __init__(self, x: int, topo: int, base: int):
        largura = 44
        altura = base - topo
        super().__init__("ponta", x, topo, altura, largura, "sprites", (173, 68, 0))

    def colisao_jogador_baixo(self, jogador, mapa):
        jogador.vely = 0
        jogador.y = self.corpo.top - jogador.altura
        return 1 * (mapa.escala_tempo >= 1)


@instanciavel
class Cano(Obstaculo):
    def __init__(self, nome: str, y: int, esquerda: int, direita: int):
        altura = 50
        largura = direita - esquerda
        super().__init__(nome, esquerda, y, altura, largura, "0", (11, 137, 0))


@instanciavel
class Chao(Obstaculo):
    def __init__(self, nome: str, y: int, esquerda: int, direita: int):
        altura = 17
        super().__init__("chao", esquerda, y, altura, direita - esquerda, "sprites", (184, 20, 20))

    def renderizar_sprite(self, tela, mapa):
        self.sprite.imprimir(tela, "chao",
                             self.x - mapa.campo_visivel.x,
                             self.y - mapa.campo_visivel.y,
                             largura=self.largura,
                             altura=self.altura)


@instanciavel
class Vitoria(Obstaculo):
    def __init__(self, x: int, y: int):
        super().__init__("tela", x, y, 275,159, "sprites", (254, 254, 0))