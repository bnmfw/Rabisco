import pygame
import math
from entidades import *
from obstaculos import *
from inimigos import *
from time import sleep
from sprites import *
from random import randrange


##### PODERES NO JOGADOR #####
class PoderGenerico:
    "Classe base para todos os poderes do jogo"
    def __init__(self, nome: str, duracao: int, velmax: int, pulo: int, recarga: int, cor: tuple):
        self.__nome = nome
        self.__duracao = duracao
        self.__cor = cor
        self.limite_vel = velmax
        self.pulo = pulo
        self.recarga = recarga
        self.descanso = 0

    @property
    def tem_tempo(self):
        return self.__tem_tempo

    @tem_tempo.setter
    def tem_tempo(self, tem_tempo):
        self.__tem_tempo = tem_tempo

    @property
    def duracao(self):
        return self.__duracao

    @duracao.setter
    def duracao(self, duracao):
        self.__duracao = duracao

    @property
    def cor(self):
        return self.__cor

    @cor.setter
    def cor(self, cor):
        self.__cor = cor

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, nome):
        self.__nome = nome

    def acao(self, jogador, screen, mapa):  ### ERA PRA SER ABSTRATO MAS FDS
        pass


##### FORMA PADRAO DO JOGADOR #####
@poder_no_jogador
class Cinza(PoderGenerico):
    "Poder Padrao, nao faz nada quando ativado"
    def __init__(self):
        super().__init__("Cinza", 0, 5, 9, 1, (150,150,150))

    def acao(self, jogador, tela, mapa):
        pass

    def atualizar(self, tela, mapa):
        pass


##### PODER DO DASH #####
@poder_no_jogador
class Vermelho(PoderGenerico):
    "Poder de Dash, rapidamente faz o jogador se esquivar"
    def __init__(self):
        super().__init__("Vermelho", 0, 7, 10, 80, (50, 50, 50))

    def acao(self, jogador, screen, mapa):
        if not self.descanso:
            jogador.velx = jogador.face * 23
            self.descanso = self.recarga

    def atualizar(self, tela, mapa):
        if self.descanso > 0:
            self.descanso -= 1
        return False


##### PODER DA BOLA DE FOGO #####
@poder_no_jogador
class Laranja(PoderGenerico):
    "Poder de fogo, joga uma bola de fogo que quica"
    def __init__(self):
        super().__init__("Laranja", 0, 5, 9, 40, (255, 50, 50))

    def acao(self, jogador, screen, mapa):
        if not self.descanso:
            mapa.lista_de_entidades.append(BolaFogo([jogador.x, jogador.y], screen, mapa, jogador.face))
            self.descanso = self.recarga

    def atualizar(self, tela, mapa):
        if self.descanso > 0:
            self.descanso -= 1
        return 0


##### PODER DA INTANGIBILIDADE #####
@poder_no_jogador
class Azul(PoderGenerico):
    "Poder de intangibilidade, o jogador passa atraves dos inimigos"
    def __init__(self):
        super().__init__("Azul", 0, 5, 9, 600, (50, 50, 255))
        self.ativo = False

    def acao(self, jogador, screen, mapa):
        if not self.descanso:
            self.ativo = True
        elif self.ativo and self.descanso > 30:
            self.ativo = False

    def atualizar(self, tela, campo_visivel):
        if self.ativo:
            self.descanso += 2
            if self.descanso >= self.recarga:
                self.ativo = False
            return True
        elif self.descanso > 0:
            self.descanso -= 1
        return False


##### PODER DE PARAR O TEMPO #####
@poder_no_jogador
class Roxo(PoderGenerico):
    """てめえの付けは・・・金では払えねえぜ!
    
    Para o tempo,afetando a maioria dos inimigos
    """
    def __init__(self):
        super().__init__("Roxo", 300, 5, 9, 600, (80, 10, 120))
        self.ativo = False

    def acao(self, jogador, screen, mapa):
        if not self.descanso:
            mapa.escala_tempo = 0
            mapa.render_escala_tempo = -1
            self.ativo = True
        elif self.ativo and self.descanso > 30:
            mapa.escala_tempo = 1
            self.ativo = False

    def atualizar(self, tela, mapa):
        if self.ativo:
            self.descanso += 2
            if self.descanso >= self.recarga:
                self.ativo = False
                mapa.escala_tempo = 1.0
        elif self.descanso > 0:
            self.descanso -= 1
        return False


##### PODER DE ACELERAR O TEMPO #####
@poder_no_jogador
class Verde(PoderGenerico):
    "Segunda referencia- Acelera o tempo ate o fim de jogo"
    def __init__(self):
        super().__init__("Verde", 300, 5, 9, 600, (5, 200, 40))
        self.ativo = False

    def acao(self, jogador, screen, mapa):
        self.ativo = True

    def atualizar(self, tela, mapa):
        if self.ativo:
            mapa.escala_tempo += 0.05 * (math.log(mapa.escala_tempo, 2) + 1)
        return False


###### ataque ninja #####
@poder_no_jogador
class Marrom(PoderGenerico):
    "Cria clones que matam o inimigo"
    def __init__(self):
        super().__init__("Marrom", 0, 5, 9, 40, (255, 255, 0))

    def acao(self, jogador, screen, mapa):
        if not self.descanso:
            mapa.lista_de_entidades.append(
                Clones([jogador.x, jogador.y], screen, mapa, jogador.face, jogador.tamanho_jogador))
            self.descanso = self.recarga

    def atualizar(self, tela, mapa):
        if self.descanso > 0:
            self.descanso -= 1
        return 0


#### PODER DO INIMIGO ####
class Projetil(PoderGenerico):
    "Atira projeteis em linha reta"
    def __init__(self):
        super().__init__("Projetil", 0, 5, 9, 40, (0, 0, 0))
        self.__altura = 26

    def acao(self, jogador, screen, mapa, velx, vely, altura_random):
        if jogador.face == 1:
            mapa.lista_de_entidades.append(
                Bala([jogador.corpo.right, jogador.y + altura_random], screen, mapa, jogador.face, velx, vely))
        elif jogador.face == -1:
            mapa.lista_de_entidades.append(Bala([jogador.x, jogador.y + altura_random], screen, mapa, jogador.face, velx, vely))
        self.descanso = self.recarga

    def atualizar(self, tela, mapa):
        if self.descanso > 0:
            self.descanso -= 1

##### OBJETOS CRIADOS POR PODERES #####

class PoderManifestado(Entidade):
    "Base para entidades criadas por poderes"
    def __init__(self, nome, x, y, largura, altura, limite_vel, vida, dano_contato, duracao, imagem,
                 tipos_transparentes, frame = 0, cor=(0, 0, 0)):
        self.duracao = duracao
        super().__init__(nome, x, y, largura, altura, limite_vel, vida, dano_contato, imagem, cor, tipos_transparentes, frame)


class PoderManifestadoInimigo(Entidade):
    "Entidades criadas por poderes dos inimigos"
    def __init__(self, nome, x, y, largura, altura, limite_vel, vida, dano_contato, duracao, imagem, cor, frames):
        self.duracao = duracao
        tipos_transparentes = []
        super().__init__(nome, x, y, largura, altura, limite_vel, vida, dano_contato, imagem,
                         tipos_transparentes, cor, frames)

    def colisao_jogador(self, jogador, direcao, mapa):
        if not jogador.invisivel:
            self.auto_destruir(mapa)
            return self.dano_contato
        return 0

@instanciavel
class BolaFogo(PoderManifestado):
    "Bola de Fogo do jogador"
    def __init__(self, pos_inicial, screen, mapa, vel):
        x = pos_inicial[0] + 25 * vel
        y = pos_inicial[1]
        largura = 26
        altura = 26
        vida = 1
        limiteVel = 3 * vel
        dano_contato = 0
        duracao = 500
        super().__init__("fogo", x, y, largura, altura, limiteVel, vida, dano_contato, duracao, "fogo", (255,128,0), 4)
        self.escala_tempo = 1.0
        self.mapa = mapa
        self.vely = -1
        self.velx = 6 * vel

    def mover(self, dimensoes_tela, mapa):

        ##### COLISOES #####

        # 0-Cima, 1-Baixo, 2-Direita, 3-Esquerda
        obsCima, obsBaixo, obsDireita, obsEsquerda = self.checar_colisao(mapa.lista_de_entidades, [Entidade])

        if obsEsquerda: obsEsquerda.colisao_outros(self, "esquerda", mapa)
        if obsDireita: obsDireita.colisao_outros(self, "direita", mapa)

        if obsCima or obsBaixo:
            self.vely = -max(self.vely * 4 / 5, 8)
        if not obsBaixo: self.vely += gravidade * 7 * self.escala_tempo

        self.y += self.vely * self.escala_tempo
        self.x += self.velx * self.escala_tempo

    def atualizar(self, tela, mapa, dimensoes_tela):
        if self.escala_tempo != mapa.escala_tempo:
            self.escala_tempo += max(min(mapa.escala_tempo - self.escala_tempo, 0.05), -0.05)
        self.corpo = pygame.Rect(self.x, self.y, self.largura, self.altura)
        if self.duracao > 0 or not self.corpo.colliderect(mapa.campo_visivel):
            self.mover(dimensoes_tela, mapa)
            self.renderizar(tela, mapa)
            self.duracao -= 1 * self.escala_tempo
            return False
        return True

    def colisao_outros(self, entidade, direcao, mapa):
        if entidade.nome == "corpo_das_cores" and entidade.fase == 2:
            entidade.toma_dano_de_fogo()
        elif not entidade.a_prova_de_fogo:
            entidade.auto_destruir(mapa)
        self.auto_destruir(mapa)


@instanciavel
class Bala(PoderManifestadoInimigo):
    "Bola de Fogo do inimigo"
    def __init__(self, pos_inicial, screen, mapa, lado, velx, vely):
        x = pos_inicial[0] + 15 * lado
        largura = 26
        altura = 26
        y = pos_inicial[1]
        vida = 1
        limiteVel = 300
        dano_contato = 1
        duracao = 500
        # self.__corpo = pygame.Rect(self.x, self.y, self.largura, self.altura)
        super().__init__("fogo", x, y, largura, altura, limiteVel, vida, dano_contato, duracao, "fogo", (255,128,0), 4)
        self.escala_tempo = 1.0
        self.mapa = mapa
        self.vely = vely
        self.velx = velx

    def mover(self, dimensoesTela, mapa):
        #### SE MOVE ####
        self.y += self.vely * self.escala_tempo
        self.x += self.velx * self.escala_tempo

    def atualizar(self, tela, mapa, dimensoes_tela):
        if self.escala_tempo != mapa.escala_tempo:
            self.escala_tempo += max(min(mapa.escala_tempo - self.escala_tempo, 0.05), -0.05)
        self.corpo = pygame.Rect(self.x, self.y, self.largura, self.altura)
        if self.duracao > 0 or not self.corpo.colliderect(mapa.campo_visivel):
            self.mover(dimensoes_tela, mapa)
            self.renderizar(tela, mapa)
            self.duracao -= 1 * self.escala_tempo
            return False
        return True


@instanciavel
class Clones(PoderManifestado):
    "Clones do poder 'jutsu'"
    def __init__(self, pos_inicial, screen, mapa, vel, tamanho_jogador):
        x = pos_inicial[0] + vel + 50
        y = pos_inicial[1] 
        largura = tamanho_jogador[1]
        altura = tamanho_jogador[0]
        vida = 10
        limiteVel = 3 * vel
        dano_contato = 50
        duracao = 500
        # self.__corpo = pygame.Rect(self.x, self.y, self.largura, self.altura)
        super().__init__("JutsuDosClones", x, y, largura, altura, limiteVel, vida, dano_contato, duracao, "0")
        self.contato = False
        self.pos_inicial = pos_inicial
        self.escala_tempo = 1.0
        self.mapa = mapa
        self.vely = 0
        self.velx = 1 * vel
        self.obstaculo_destruido = 0

        ### IDEIA: SEGUNDO E TERCEIRO CLONE NAO SAO OBJETOS, APENAS DESENHOS
        ### QUANDO ELES CHEGAM NO INIMIO QUEM DE FATO MATA É O PRIMEIRO CLONE
        
        ### SEGUNDO CLONE #######
        self.x2 = pos_inicial[0] + vel
        self.y2 = pos_inicial[1] - 2*tamanho_jogador[0]
        self.vely2 = 0
        self.velx2 = 0* vel

        ### TERCEIRO CLONE #####
        self.x3 = (pos_inicial[0] + (8*tamanho_jogador[1]) * vel)  ##terceiro clone
        self.y3 = pos_inicial[1] - 2*tamanho_jogador[0]
        self.vely3 = 0
        self.velx3 = 0 * vel

    def mover(self, dimensoesTela, mapa):
        ##### COLISOES #####

        # 0-Cima, 1-Baixo, 2-Direita, 3-Esquerda
        obstaculos = self.checar_colisao(mapa.lista_de_entidades, [Clones, PoderNoMapa])

        for i in range(len(obstaculos)):
            if isinstance(obstaculos[i], Entidade):
                
                self.obstaculo_destruido = obstaculos[i]
                self.velx2 = (obstaculos[i].corpo.center[0] - self.corpo2.center[0])*0.04
                self.vely2 =  (obstaculos[i].corpo.center[1]- self.corpo2.center[1])*0.04
                self.velx3 = (obstaculos[i].corpo.center[0] - self.corpo3.center[0])*0.04
                self.vely3 =  (obstaculos[i].corpo.center[1]- self.corpo3.center[1])*0.04
                obstaculos[i].velx = 0
                self.velx = 0
                self.contato = True
                    

        ##### HORIZONTAIS #####
        if obstaculos[2] or obstaculos[3]:
            # self.duracao = 0
            self.velx = -self.velx
            #self.auto_destruir(mapa)

        ##### VERTICAIS #####
        if obstaculos[1] or obstaculos[0]:
            #self.auto_destruir(mapa)
            # self.vely = -max(self.vely*4/5,8)
            self.y = obstaculos[1].corpo.top - (self.altura)
        if not obstaculos[1]: self.vely += gravidade*self.escala_tempo

        
        if self.x < 2*self.pos_inicial[0]:
            self.y += self.vely * self.escala_tempo
            self.x += self.velx * self.escala_tempo
        

    def renderizar(self, tela, mapa):
        if renderizar_hitbox: self.renderizar(tela, mapa)
        
        if self.contato == True:
            pygame.draw.rect(tela, (50, 50, 0), [self.corpo2.x - mapa.campo_visivel.x,
                                                    self.corpo2.y - mapa.campo_visivel.y,
                                                    self.corpo2.w,
                                                    self.corpo2.h])

            pygame.draw.rect(tela, (50, 50, 0), [self.corpo3.x - mapa.campo_visivel.x,
                                                    self.corpo3.y - mapa.campo_visivel.y,
                                                    self.corpo3.w,
                                                    self.corpo3.h])

    def atualizar(self, tela, mapa, dimensoes_tela):
        if self.escala_tempo != mapa.escala_tempo:
            self.escala_tempo += max(min(mapa.escala_tempo - self.escala_tempo, 0.05), -0.05)

        self.corpo = pygame.Rect(self.x, self.y, self.largura, self.altura)
        #.corpo1 = pygame.Rect(self.x, self.y, self.largura, self.altura)
        self.corpo2 = pygame.Rect(self.x2, self.y2, self.largura, self.altura)
        self.corpo3 = pygame.Rect(self.x3, self.y3, self.largura, self.altura)

        
        ### SEGUNDO E TERCEIRO CLONE PRECISAM SE MECHER POR AQUI, 
        ### POIS DPS DE CAPTURAR O INIMIGO, O CLONE1 NAO SE MECHEE MAIS 
        if self.contato == True: 
                    
                self.y2 += self.vely2 * self.escala_tempo
                self.x2 += self.velx2 * self.escala_tempo
                
                self.y3 += self.vely3 * self.escala_tempo
                self.x3 += self.velx3 * self.escala_tempo

                if int(self.x2) == int(self.x3): 
                    self.obstaculo_destruido.auto_destruir(mapa)
                    self.auto_destruir(mapa)
        
        
        if (self.duracao > 0):
            self.mover(dimensoes_tela, mapa)
            self.renderizar(tela, mapa)
            self.duracao -= 1 * self.escala_tempo
            return False
        return True
