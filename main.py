import pygame
from game.jogo import Jogo


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.music.load('game/musica_fundo.ogg')
    jogo = Jogo()
    jogo.menu_inicial()