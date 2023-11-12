import pygame
from obstaculos import *
from entidades import gravidade, colisao_analisada, renderizar_hitbox, renderizar_sprite
from inimigos import Bolota,Gelatina,Temporal
from coletaveis import *
from poderes import *
from sprites import Sprite


class Jogador(Movel):
    """ Entidade controlada pela pessoa que joga, o jogador
    """
    def __init__(self, nome: str, x: int, y: int, poder_atual: PoderGenerico, poder_armazenado: PoderGenerico, paletas_coletadas: int):
        ##### ATRIBUTOS GERAIS #####
        self.__vida = 5
        self.__sprite = {"cinza": Sprite("rabisco_cinza"),
                         "laranja": Sprite("rabisco_laranja"),
                         "vermelho": Sprite("rabisco_vermelho"),
                         "roxo": Sprite("rabisco_roxo"),
                         "azul": Sprite("rabisco_azul"),
                         "verde": Sprite("rabisco_verde"),
                         "marrom": Sprite("rabisco_marrom")}
        self.__posicao_comeco = (x, y)
        self.__descanso_troca_poder = 0
        ##### ATRIBUTOS POSICIONAIS #####
        altura = 45
        largura = 45
        limite_vel = 5
        self.__aceleracao = 0

        ##### ATRIBUTOS COMPORTAMENTAIS #####
        self.__tipos_transparentes = [BolaFogo, Vitoria]
        self.__poder = poder_atual
        self.__poder_armazenado = poder_armazenado
        self.__recuperacao = 0
        self.__recarga = 0
        self.__invisivel = 0
        self.__moedas = 0
        self.escala_tempo = 1
        self.__paleta = paletas_coletadas
        self.__auxiliar = 0 #usado para fazer o jogador pular no instane que toca no castelo
        self.__congelado = False

        super().__init__(nome, x, y, altura, largura, limite_vel, "0", [], (128,128,128))

    @property
    def invisivel(self):
        return self.__invisivel
    
    @property
    def paleta(self):
        return self.__paleta

    @property
    def poder(self):
        return self.__poder
    
    @property
    def poder_armazenado(self):
        return self.__poder_armazenado

    @poder.setter
    def poder(self, poder):
       self.__poder = poder

    @property
    def moedas(self):
        return self.__moedas

    @moedas.setter
    def moedas(self, moedas):
       self.__moedas = moedas

    @property
    def aceleracao(self):
        return self.__aceleracao

    @aceleracao.setter
    def aceleracao(self, aceleracao):
       self.__aceleracao = aceleracao

    @property
    def posicao_comeco(self):
       return self.__posicao_comeco

    @posicao_comeco.setter
    def posicao_comeco(self, posicao_comeco):
       self.__posicao_comeco = posicao_comeco

    @property
    def vida(self):
        return self.__vida

    @property
    def tipos_transparentes(self):
        return self.__tipos_transparentes
    
    @tipos_transparentes.setter
    def tipos_transparentes(self,tipos):
        self.__tipos_transparentes = tipos
    
    #@property
    #def recuperacao(self):
    #    return self.__recuperacao

    def vida_pra_zero(self):
        self.__vida = 0
    
    def ganha_vida(self):
        "Recupera 1 vida"
        if self.__vida < 5:
            self.__vida += 1

    def coletar_poder(self, item):
        if (not isinstance(self.__poder, Cinza)) and (self.__paleta == 3):
            self.__poder_armazenado = self.__poder
        self.__poder = item.poder_atribuido
        self.ganha_vida()

    def coletar_moeda(self):
        self.__moedas += 1
    
    def coletar_paleta(self):
        if self.__paleta < 3:
            self.__paleta += 1
        else:
            self.coletar_moeda()
        if self.__vida < 5:
            self.__vida += 1

    def congelar(self):
        self.__congelado = True
        self.escala_tempo = 0

    def descongelar(self):
        self.__congelado = False
        self.escala_tempo = 1

    def renderizar_sprite(self, tela, mapa):
        "renderiza na tela na posicao correta, relativo ao local no mapa"
        if self.__recuperacao % 15 < 10:
                self.__sprite[type(self.poder).__name__.lower()].imprimir(tela, "rabisco", self.x - mapa.campo_visivel.x, self.y - mapa.campo_visivel.y,
                                self.face*(self.escala_tempo!=0)+1*(self.escala_tempo==0), self.velx*(self.escala_tempo>0), self.vely, int(mapa.ciclo/6) % 12*(self.escala_tempo>0))

    def atualizar(self, screen, mapa, entradas):
        """define logica de interacao com objetos especificos
        
        return o campo que determina a renderizacao do mapa
        para permitir sidescrolling
        """
        pega_poder_armazenado = entradas[3]
        tamanho_tela = screen.get_size()
        if self.__descanso_troca_poder == 0:
            if self.__paleta == 3 and pega_poder_armazenado and not isinstance(self.__poder_armazenado, Cinza):
                poder_a_ser_armazenado = self.__poder
                self.__poder = self.__poder_armazenado
                self.__poder_armazenado = poder_a_ser_armazenado
                self.__descanso_troca_poder = 30
        else:
            self.__descanso_troca_poder -= 1
        self.mover(entradas[0], entradas[1], entradas[2], tamanho_tela, mapa, 0.5)
        self.corpo = pygame.Rect(self.x, self.y, self.largura, self.altura)

        self.renderizar(screen, mapa)

        ##### ATUALIZACAO DOS PODERES #####
        self.__invisivel = self.__poder.atualizar(screen, mapa)

        ##### SIDESCROLL #####
        if self.x > mapa.campo_visivel.x + tamanho_tela[0]*3/5:
            campo_x = max(0, min((mapa.tamanho[0] - mapa.campo_visivel.w, self.x - tamanho_tela[0]*3/5)))
        elif self.x < mapa.campo_visivel.x + tamanho_tela[0]*2/5:
            campo_x = max(0, min((mapa.tamanho[0] - mapa.campo_visivel.w, self.x - tamanho_tela[0]*2/5)))
        else:
            campo_x = mapa.campo_visivel.x
        if self.y < mapa.campo_visivel.y + tamanho_tela[1]/3:
            campo_y = min((mapa.tamanho[1] - mapa.campo_visivel.h, self.y - tamanho_tela[1]/3))
        elif self.y > mapa.campo_visivel.y + tamanho_tela[1]/2:
            campo_y = min((mapa.tamanho[1] - mapa.campo_visivel.h, self.y - tamanho_tela[1]/2))
        else:
            campo_y = mapa.campo_visivel.y
        return pygame.Rect(campo_x, campo_y, mapa.campo_visivel.w, mapa.campo_visivel.h)

    def respawn(self):
        ##### EMPURRA O JOGADOR #####
        self.x = self.posicao_comeco[0]
        self.y = self.posicao_comeco[1]

    def mover(self, direita, esquerda, espaco, screen, mapa, atrito):
        "Atualiza posicao e velocidade"
        if not self.__congelado: self.escala_tempo = 1

        ##### MOVIMENTO HORIZONTAL #####
        self.__aceleracao = (direita - esquerda)
        self.velx += self.__aceleracao

        ##### COLISOES #####
        # 0-Cima, 1-Baixo, 2-Direita, 3-Esquerda
        obsCima, obsBaixo, obsDireita, obsEsquerda = self.checar_colisao(mapa.lista_de_entidades, self.__tipos_transparentes)
        obstaculos = [obsCima, obsBaixo, obsDireita, obsEsquerda]
        dano_total = 0

        if obsCima:
            dano_sofrido = obsCima.colisao_jogador(self, "cima", mapa)
            dano_total += dano_sofrido
        if obsBaixo:
            dano_sofrido = obsBaixo.colisao_jogador(self, "baixo", mapa)
            dano_total += dano_sofrido
        if obsDireita:
            dano_sofrido = obsDireita.colisao_jogador(self, "direita", mapa)
            dano_total += dano_sofrido
        if obsEsquerda:
            dano_sofrido = obsEsquerda.colisao_jogador(self, "esquerda", mapa)
            dano_total += dano_sofrido

        if not self.__invisivel:
            if dano_total and not self.__recuperacao > 0 and not mapa.ganhou:
                self.__vida -= dano_total
                self.__recuperacao = 90
            elif self.__recuperacao > 0:
                self.__recuperacao -= 1


        ##### PERMITE
        if self.__invisivel:
            for i in range(len(obstaculos)):
                if isinstance(obstaculos[i], Entidade):
                    obstaculos[i] = 0

        ##### REPOSICIONAMENTO POS COLISAO #####
        if isinstance(obsDireita, Obstaculo) and isinstance(obsEsquerda, Obstaculo):  # ESMAGAMENTO
            self.__vida = 0

        ##### IMPEDE QUE O JOGADOR PASSE DA BORDA ESQUERDA #####
        if self.x <= 0:
            if self.velx <= 0:
                self.velx = 0
                self.x = 0

        ##### IMPEDE QUE O JOGADOR PASSE DA BORDA DIREITA #####
        if self.x >= mapa.tamanho[0] - self.largura:
            if self.velx >= 0:
                self.velx = 0
                self.x = mapa.tamanho[0] - self.largura

        ### CHECANDO VITÓRIA ###
        entidade_vitoria = 0
        for ganhar in mapa.lista_de_entidades:
            if isinstance(ganhar, Vitoria):
                entidade_vitoria = ganhar

        if self.corpo.colliderect(entidade_vitoria.corpo):
            mapa.ganhou = True

        ##### GRAVIDADE ######
        if not obsBaixo: self.vely += gravidade * self.escala_tempo

        ##### ATRITO ######
        if self.__aceleracao == 0:
            if self.velx < 0:
                self.velx += atrito
            elif self.velx > 0:
                self.velx -= atrito

        #### PULO ####
        flag = False
        for tipo in [PoderManifestado, Coletavel]:
            if isinstance(obsBaixo, tipo):
                flag = True
        if obsBaixo and not flag and espaco:
            self.vely = -self.poder.pulo

        ##### ANIMACAO DE ENTRAR NA TELA #####
        if mapa.ganhou:
            if self.__auxiliar == 0:
                self.vely = -10
                self.__auxiliar += 1
            dist_meio_vitoria = entidade_vitoria.corpo.centerx - self.corpo.centerx
            if dist_meio_vitoria < 0:
                self.velx = -1
            elif dist_meio_vitoria > 0:
                self.velx = 1
            else:
                self.velx = 0
            dist_metade_vitoria = (entidade_vitoria.corpo.centery - self.corpo.y) - 30
            if dist_metade_vitoria <= 0 and self.vely > 0:
                self.vely = 0

        ##### AJUSTE DE VELOCIDADE MAXIMA #####
        if self.velx > self.poder.limite_vel:
            if self.velx > self.poder.limite_vel + 1:
                self.velx -= 1
            else:
                self.velx = self.poder.limite_vel

        elif self.velx < -self.poder.limite_vel:
            if self.velx < -self.poder.limite_vel - 1:
                self.velx += 1
            else:
                self.velx = -self.poder.limite_vel

        ##### ATUALIZACAO DE POSICOES #####
        self.y += self.vely * self.escala_tempo
        self.x += self.velx * self.escala_tempo

        ##### MATA O JOGADOR SE CAIR NO BURACO #####
        if self.y > mapa.tamanho[1]: self.__vida = 0

        ##### INDICA A DIRECAO DO JOGADOR PARA DIRECIONAR PODERES #####
        if self.velx > 0:
            self.face = 1
        elif self.velx < 0:
            self.face = -1

        ##### ATUALIZACAO DO CORPO DO JOGADOR #####
        #self.corpo = pygame.Rect(self.x, self.y, self.largura, self.altura)

    def poderes(self, screen, mapa, acao=False):
        "Faz com que o jogador ative seu poder quando disponivel"
        ##### ATIRA BOLA DE FOGO SE ESTIVER DISPONIVEL
        if acao:
            self.__poder.acao(self, screen, mapa)
