# Arquivo destinado a fazer todos os inimigos
import pygame
from entidades import *
from poderes import *
from coletaveis import *
from random import randrange


class Inimigo(Entidade):
    def __init__(self, nome, x, y, altura, largura, limiteVel, vida, danoContato, imagem,
                 tipos_transparentes, cor, frames, fogo = False, tempo_inverso = False):
        super().__init__(nome, x, y, altura, largura, limiteVel, vida, danoContato, imagem,
                         tipos_transparentes, cor, frames, fogo, tempo_inverso)

    def mover(self, dimensoesTela, mapa):
        "Atualiza posicao e velocidade"
        ##### COLISOES #####
        obsBaixo = self.gerenciar_colisoes(mapa)

        ##### GRAVIDADE ######
        if not obsBaixo:
            self.vely += gravidade * self.escala_tempo

        ##### ATUALIZACAO DAS POSICOES #####
        self.y += self.vely * self.escala_tempo
        self.x += self.velx * self.escala_tempo


@instanciavel
class Bolota(Inimigo):
    "Inimigo comum, anda em uma direcao e muda quando bate"
    def __init__(self, x: int, y: int):
        vida = 1
        danoContato = 1
        largura = 46
        altura = 46
        limiteVel = 1
        super().__init__("bolota", x, y, altura, largura, limiteVel, vida, danoContato, "bolota",
                         [Bala, PoderNoMapa], (88, 51, 0), 25)
        self.vely = 0
        self.velx = 1
        self.xinicial = x
        self.escala_tempo = 1


@instanciavel
class Espinhento(Inimigo):
    "Inimigo que da dano quando esmagado"
    def __init__(self, x: int, y: int):
        vida = 1
        danoContato = 1
        largura = 48
        altura = 45
        limiteVel = 1
        super().__init__("espinhento", x, y, altura, largura, limiteVel, vida, danoContato, "espinhento",
                         [Bala, PoderNoMapa], (50, 50, 50), 8)
        self.vely = 0
        self.velx = 0.5
        self.xinicial = x
        self.escala_tempo = 1

    def colisao_jogador_baixo(self, jogador, mapa):
        if not jogador.invisivel:
            jogador.vely = 0
            jogador.y = self.corpo.top - jogador.altura
            return self.dano_contato+1
        return 0


@instanciavel
class Voador(Inimigo):
    "Inimigo que voa, ignora o jogador por maior parte"
    def __init__(self, nome: str, x: int, y: int, altitude: int):
        vida = 1
        danoContato = 1
        largura = 26
        altura = 26
        limiteVel = 4
        super().__init__(nome, x, y, altura, largura, limiteVel, vida, danoContato, "0",
                         [Bala, PoderNoMapa, Estatico], (88, 51, 0), 0)
        self.altitude = pygame.Rect(x, y + largura + 2, largura,
                                    altura + altitude)  # CAMPO UTILIZADO PARA CHECAR ALTURA DE VOO
        self.vely = 0
        self.velx = 1
        self.xinicial = x
        self.escala_tempo = 1

    def mover(self, dimensoesTela, mapa):
        "Atualiza posicao e velocidade"
        ##### COLISOES #####
        obsCima, obsBaixo, obsDireita, obsEsquerda = self.checar_colisao(mapa.lista_de_entidades,
                                                                         [Bala, PoderNoMapa, Estatico])

        ##### HORIZONTAIS #####
        if obsEsquerda or obsDireita:
            self.velx = self.velx * -1

        ##### VERTICAIS #####
        if obsBaixo or obsCima:
            self.vely = -self.vely

        ##### GRAVIDADE ######
        if (self.altitude.collidelist([x.corpo for x in mapa.lista_de_entidades if x != self]) != -1
                or self.altitude.y + self.altitude.h > dimensoesTela[1]):
            self.vely -= gravidade * self.escala_tempo * 0.2
        else:
            self.vely += gravidade * self.escala_tempo * 0.2

        if self.vely < -1:
            self.vely = -1
        self.y += self.vely * self.escala_tempo
        self.x += self.velx * self.escala_tempo
        self.altitude.x = self.x
        self.altitude.y = self.y + self.largura + 2


@instanciavel
class Atirador(Inimigo):
    "Inimigo que atira bolas de fogo periodicamente"
    def __init__(self, x: int, y: int):#, anda = True):
        vida = 1
        danoContato = 1
        largura = 90
        altura = 44
        limiteVel = 0
        super().__init__("atirador", x, y, altura, largura, limiteVel, vida, danoContato, "atirador",
                         [Bala, PoderNoMapa], (255, 25, 25), 8, True)
        self.vely = 0
        self.velx = 0
        self.__vel_projetil = 3
        #self.__anda = anda
        self.xinicial = x
        self.escala_tempo = 1
        self.__poder = Projetil()
        self.__descanso_poder_max = 125
        self.__descanso_poder = randrange(0,25)
        self.__gravidade = 1


    def atualizar(self, tela, mapa, dimensoes_tela):
        "Determina se atira ou nao"
        if self.escala_tempo != mapa.escala_tempo:
            self.escala_tempo += max(min(mapa.escala_tempo - self.escala_tempo, 0.05), -0.05)
        self.mover(dimensoes_tela, mapa)
        self.corpo = pygame.Rect(self.x, self.y, self.largura, self.altura)
        if mapa.campo_visivel.colliderect(self.corpo):
            self.renderizar(tela, mapa)

        #### DETERMINA A VELOCIDADE DO PROJETIL PRA SEGUIR O JOGADOR ####
        if self.corpo.colliderect(mapa.campo_visivel):
            altura_random = 0 #randrange(0, self.altura - 26)
            disty = (mapa.jogador.y + mapa.jogador.altura) - (self.y + self.altura)
            if mapa.jogador.x <= self.x:
                distx = mapa.jogador.x - self.x -15*self.face
                dstancia = ((disty) ** 2 + (
                        distx) ** 2) ** (1 / 2)
                divisor = max(dstancia / self.__vel_projetil,0.001)
                velx = distx / divisor
            else:
                distx = mapa.jogador.x - self.corpo.bottomright[0] -15*self.face
                dstancia = ((disty) ** 2 + (
                        distx) ** 2) ** (1 / 2)
                divisor = max(dstancia / self.__vel_projetil,0.001)
                velx = distx / divisor
            vely = disty / divisor

            if self.__descanso_poder <= 0:
                self.__poder.acao(self, tela, mapa, velx, vely, altura_random)
                self.__descanso_poder = self.__descanso_poder_max + randrange(0, 50)
            else:
                self.__descanso_poder -= 1 * self.escala_tempo
        return False

    def mover(self, dimensoesTela, mapa):
        "Atualiza posicao e velocidade"
        ##### COLISOES #####
        obsBaixo = self.gerenciar_colisoes(mapa)

        ##### GRAVIDADE ######
        if not obsBaixo:
            self.vely += self.__gravidade * self.escala_tempo

        #### SE NÃO TA NO CAMPO VISIVEL FICA PARADO ####
        dist_x_jogador = self.x - mapa.jogador.x
        if dist_x_jogador > 0:
            self.face = -1
        elif dist_x_jogador < 0:
            self.face = 1

        self.x += self.velx * self.escala_tempo * self.face
        self.y += self.vely * self.escala_tempo


@instanciavel
class Saltante(Inimigo):
    "Inimigo que pula de um lado pro outro"
    def __init__(self, x: int, y: int):
        vida = 1
        danoContato = 1
        largura = 54
        altura = 99
        limiteVel = 1
        super().__init__("saltante", x, y, altura, largura, limiteVel, vida, danoContato, "saltante",
                         [Bala, PoderNoMapa], (128, 0, 0), 6)
        #self.vely = 0
        #self.velx = 0
        self.xinicial = x
        self.escala_tempo = 1
        self.__descanso_pulo_max = 145
        self.__descanso_pulo = self.__descanso_pulo_max
        self.__pulo_lado = True
        self.face = -1

    def mover(self, dimensoesTela, mapa):
        "Atualiza posicao e velocidade"
        ##### COISA PRO PULO MAIS PRA FRENTE #####
        vely_buff = self.vely

        ##### COLISOES #####
        obsBaixo = self.gerenciar_colisoes(mapa)

        ##### GRAVIDADE ######
        if not obsBaixo: self.vely += gravidade * self.escala_tempo

        ##### GERENCIADOR DO PULO #####
        self.__descanso_pulo = (self.__descanso_pulo-1) % self.__descanso_pulo_max

        if not self.__descanso_pulo and obsBaixo: self.vely -= 9 #PULA

        if self.vely : self.velx = self.face * 3 * self.__pulo_lado #MOVIMENTO HORIZONTAL
        else: self.velx = 0

        if not self.vely and vely_buff: #INVERTE A FACE
            if self.__pulo_lado: self.face = -self.face
            self.__pulo_lado = not(self.__pulo_lado)

        ##### REPOSICIONAMENTO #####
        self.y += self.vely * self.escala_tempo
        self.x += self.velx * self.escala_tempo


@instanciavel
class Gelatina(Inimigo):
    "Inimigo que nem eh solido, mas deixa lento ao atravessar"
    def __init__(self, x: int, y: int):
        vida = 1
        danoContato = 1
        largura = 150
        altura = 150
        limiteVel = 1
        super().__init__("gelatina", x, y, altura, largura, limiteVel, vida, danoContato, "gelatina",
                         [Bala, PoderNoMapa, Inimigo], (50, 50, 255), 9, True)
        self.vely = 0
        self.velx = 1
        self.xinicial = x
        self.escala_tempo = 1

    def colisao_jogador(self, jogador, direcao, mapa):
        "Determina que o jogador fique mais lento ao passar"
        if not jogador.invisivel:
            jogador.escala_tempo = 0.25
        return 0

    def colisao_outros(self, entidade, direcao, mapa):
        pass


@instanciavel
class Temporal(Inimigo):
    """Inimigo com o mesmo tipo de stand

    Permanece estatico maior parte do tempo, mas eh muito agressivo
    e rapido quando o tempo esta parado, para fazer com que o
    jogador use o poder apenas quando necessario
    """
    def __init__(self, x: int, y: int):
        vida = 1
        danoContato = 1
        largura = 59
        altura = 59
        limiteVel = 4
        super().__init__("temporal", x, y, altura, largura, limiteVel, vida, danoContato, "temporal",
                         [Bala, PoderNoMapa], (80, 10, 120), 15, tempo_inverso=True)
        self.vely = 0
        self.xinicial = x
        self.escala_tempo = 0
        self.aceleracao = 1

    def colisao_jogador(self, jogador, direcao, mapa):
        ##### COLISAO ESQUERDA #####
        if direcao == "esquerda":
            if jogador.velx <= 0:
                jogador.velx = 4
                jogador.aceleracao = 0
            return self.dano_contato * (mapa.escala_tempo < 1)
        ##### COLISAO DIREITA #####
        elif direcao == "direita":
            if jogador.velx >= 0:
                jogador.velx = -4
                jogador.aceleracao = 0
            return self.dano_contato * (mapa.escala_tempo < 1)
        ##### COLISAO BAIXO #####
        elif direcao == "baixo":
            jogador.vely = 0
            jogador.y = self.corpo.top - jogador.altura
            return self.dano_contato * (mapa.escala_tempo < 1)
        ##### COLISAO CIMA #####
        elif direcao == "cima":
            if jogador.vely < 0:
                jogador.vely = 0
                jogador.y = self.corpo.bottom
            return self.dano_contato * (mapa.escala_tempo < 1)

    def mover(self, dimensoesTela, mapa):
        "Atualiza posicao e velocidade,mas no tempo parado"
        ##### COLISOES #####
        obsBaixo = self.gerenciar_colisoes(mapa)
        if obsBaixo:
            if mapa.jogador.vely < 0:
                self.vely = -10

        ##### GRAVIDADE ######
        else: self.vely += gravidade * max(0,(-self.escala_tempo+1))

        if not self.escala_tempo:
            if mapa.jogador.x > self.x:
                self.face = 1
            else:
                self.face = -1

        ##### ACELERACAO #####
        self.velx += self.aceleracao * self.face
        if self.escala_tempo: self.velx = 0
        if self.velx > self.limite_vel:
            self.velx = self.limite_vel
        elif self.velx < - self.limite_vel:
            self.velx = - self.limite_vel

        ##### REPOSICIONALMENTO #####
        self.y += self.vely * max(0,(-self.escala_tempo+1))
        self.x += self.velx * max(0,(-self.escala_tempo+1))

    def colisao_outros(self, entidade, direcao, mapa):
        if direcao == "esquerda":
            if entidade.velx <= 0:
                if self.escala_tempo > 0:
                    entidade.velx = - entidade.velx
                    entidade.face = -(entidade.face)
                    entidade.x = self.corpo.right + 1
                self.velx = - self.velx
                self.face = - self.face
        ##### COLISAO DIREITA #####
        elif direcao == "direita":
            if entidade.velx >= 0:
                if self.escala_tempo > 0:
                    entidade.x = self.corpo.left - entidade.largura
                    entidade.velx = - entidade.velx
                    entidade.face = -(entidade.face)
                self.velx = - self.velx
                self.face = - self.face
        elif direcao in ["baixo"]:
            entidade.vely = 0
            entidade.y = self.corpo.top - entidade.altura