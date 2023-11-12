from .entidades import *
from .inimigos import *
from .poderes import *
from .obstaculos import *
from .coletaveis import *

@instanciavel
class Gota(Coletavel):
    """Coletavel da Batalha
    
    Ao coletar, jogador recupera vida
    e avisa ao rei que foi tomada
    """
    def __init__(self, nome, x, y, rei):
        largura = 20
        altura = 29
        self.__rei = rei
        super().__init__(nome, x, y, "sprites", (0, 0, 0), largura, altura)
    
    def coleta(self, jogador, mapa):
        jogador.ganha_vida()
        self.__rei.jogador_pega_gota()
        mapa.escala_tempo = 1
        self.auto_destruir(mapa)

class ParteDoRei(Entidade):
    "Partes do Rei das Cores"
    def __init__(self, nome: str, x: int, y: int, altura: int, largura: int, limiteVel: int, vida: int, dano_contato: int, imagem: str,
                 tipos_transparentes, cor, frames: int):
        super().__init__(nome, x, y, altura, largura, limiteVel, vida, dano_contato, imagem,
                         tipos_transparentes, cor, frames, True)
        self.__montado = False
        self.__fim_de_jogo = False
        self.__fase = 0
        self.__rei = 0

    @property
    def montado(self):
        return self.__montado

    @property
    def fase(self):
        return self.__fase

    @property
    def rei(self):
        return self.__rei

    @rei.setter
    def rei(self, rei):
        self.__rei = rei

    @property
    def fim_de_jogo(self):
        return self.__fim_de_jogo

    def finalizar_jogo(self):
        self.__fim_de_jogo = True

    @montado.setter
    def montado(self, montado):
        self.__montado = montado

    def passar_fase(self):
        self.__fase += 1

    def montar(self, mapa):
        for entidade in mapa.lista_de_entidades:
            if type(entidade) == ReiDasCores:
                self.__montado = True
                self.__rei = entidade
                if type(self) == CabecaLaranja:
                    entidade.cabeca = self
                elif type(self) == CoracaoRoxo:
                    entidade.coracao = self


@instanciavel
class PunhoVermelho(ParteDoRei):
    """Punhos do Rei das Cores

    Vao na direcao do jogador e voltam
    """
    def __init__(self, x, y, lado, primeiro_tiro):
        self.__centro_x = x
        self.__centro_y = y
        self.__lado = lado
        altura = 60
        largura = 60
        dano_contato = 1
        cor = (255,0,0)
        limiteVel = 10
        self.__espera = 0
        self.__recarga = 300
        self.__descanso_tiro = primeiro_tiro
        self.__atirando = False
        self.__atirou = False
        self.__vel_mao = 8
        self.__quebrado = False
        super().__init__("punho", x, y, altura, largura, limiteVel, 0, dano_contato, "punho",
                         [Bala, BolaFogo, Coletavel, ParteDoRei, ReiDasCores, PlataformaMovel], cor, 0)
    
    @property
    def recarga(self):
        return self.__recarga
    
    @recarga.setter
    def recarga(self, recarga):
        self.__recarga = recarga
    
    @property
    def vel_mao(self):
        return self.__vel_mao
    
    @vel_mao.setter
    def vel_mao(self, vel_mao):
        self.__vel_mao = vel_mao

    @property
    def quebrado(self):
        return self.__quebrado

    def renderizar_sprite(self, tela, mapa):
        "renderiza na tela na posicao correta"
        if self.velx > 0: face = 1
        elif self.velx < 0: face = -1
        else:
            if self.__lado == "esquerdo": face = -1
            else: face = 1
        self.sprite.imprimir(tela, "punho",
                             self.x - mapa.campo_visivel.x,
                             self.y - mapa.campo_visivel.y,
                             orientacao = face,
                             frame = 1 * (self.__quebrado))

    def montar(self, mapa):
        for entidade in mapa.lista_de_entidades:
            if type(entidade) == ReiDasCores:
                self.montado = True
                self.rei = entidade
                if self.__lado == "esquerdo":
                    entidade.punho_esquerdo = self
                else:
                    entidade.punho_direito = self


    def atualizar(self, tela, mapa, dimensoes_tela):
        atira = 0 #define se o boss vai laçar a mão
        if not self.__atirando: #se não esta lançando a posição é colada ao boss e conta para poder atirar
            if mapa.escala_tempo != 0:
                self.__descanso_tiro -= 1
            if self.__descanso_tiro == 0:
                self.__atirou = False
                self.__atirando = True
                atira = 1
                self.__descanso_tiro = self.__recarga
            self.x = self.__centro_x
            self.y = self.__centro_y
            self.vely = 0
            self.velx = 0
        
        self.mover(mapa.jogador, mapa, atira) # lançar é o mover da mão
        if not self.montado: self.montar(mapa)
        ##### ATUALIZACAO DO CORACAO #####
        if self.__lado == "direito":
            self.__centro_x = self.rei.x + 200
            self.__centro_y = self.rei.y + 100
        else:
            self.__centro_x = self.rei.x - 100
            self.__centro_y = self.rei.y + 100
        self.corpo = pygame.Rect(self.x, self.y, self.largura, self.altura)

        self.renderizar(tela, mapa)

    def mover(self, jogador, mapa, atira):
        velx_buff = self.velx
        obsBaixo = self.gerenciar_colisoes(mapa)
        if obsBaixo: self.velx = 0
        ##### VOLTANDO AO CORPO #####
        if velx_buff and not self.velx and self.__atirando: # se acabou de de tocar no chão começa o tempo de espera paravoltar ao corpo
            self.vely = 0
            self.__espera = 120
            self.__atirou = True # variavel para deixar a função de voltar ao corpo rodar só depois de ter atirado
        if self.__espera == 0 and self.__atirou:# função de voltar ao corpo
            distx = self.__centro_x - self.x
            disty = self.__centro_y - self.y
            dstancia = ((disty) ** 2 + (distx) ** 2) ** (1 / 2) # distancia entre a mão e sua posiçaõ no corpo
            divisor = max(dstancia / self.__vel_mao,0.001)

            self.velx = distx / divisor
            self.vely = disty / divisor
            if dstancia <= 8: #checagem para ver se chegou no corpo
                self.__atirando = False
        else:
            self.__espera -= 1 #contagem para a mão ficar um tempinho parada
        
        if abs(self.__centro_x - self.corpo.centerx) >= 700 or abs((self.__centro_y) - (self.y)) >= 700: #se a mão nunca chegar no chão começa a voltar
            self.__espera = 0
            self.__atirou = True # variavel para deixar a função de voltar ao corpo rodar só depois de ter atirado

        #### FUNÇÂO PARA ATIRAR ####
        if atira == 1:
            distx = jogador.corpo.centerx - self.corpo.centerx
            disty = jogador.corpo.centery - self.corpo.centery
            dstancia = ((disty) ** 2 + (
                    distx) ** 2) ** (1 / 2) #distancia entre a mão e o jogador
            divisor = max(dstancia / self.__vel_mao,0.001)

            self.velx = distx / divisor
            self.vely = disty / divisor
        
        #### Atualiza a posição da mão ####
        self.x += self.velx * mapa.escala_tempo
        self.y += self.vely * mapa.escala_tempo
        

    def colisao_jogador(self, jogador, direcao, mapa):
        "Detecta colisao com jogador, return dano caso valido"
        ##### COLISAO ESQUERDA #####
        if not jogador.invisivel:
            if direcao == "esquerda":
                if jogador.velx <= 0:
                    jogador.velx = 0
                    jogador.aceleracao = 0
                    jogador.x = self.corpo.right + 1
                return self.dano_contato
            ##### COLISAO DIREITA #####
            elif direcao == "direita":
                if jogador.velx >= 0:
                    jogador.velx = 0
                    jogador.aceleracao = 0
                    jogador.x = self.corpo.left - jogador.largura
                return self.dano_contato
            ##### COLISAO BAIXO #####
            elif direcao == "baixo":
                jogador.vely = 0
                jogador.y = self.corpo.top - jogador.altura
                self.__quebrado = True #Toma dano se o jogador pina nela
                return 0
            ##### COLISAO CIMA #####
            elif direcao == "cima":
                if jogador.vely < 0:
                    jogador.vely = 0
                    jogador.y = self.corpo.bottom
                return self.dano_contato
        else:
            return 0


@instanciavel
class CabecaLaranja(ParteDoRei):
    """Cabeca do Rei das Cores
    
    Pode atirar bolas de fogo
    Geralmente, fere quem a pisa
    """
    def __init__(self, x, y):
        #self.__rei = 0
        self.__vel_projetil = 3
        self.__descanso_poder_max = 125
        self.__descanso_poder = randrange(0, 25)
        self.__poder = Projetil()
        self.__quebrado = False
        altura = 59
        largura = 56
        dano_contato = 1
        cor = (255,128,0)
        limiteVel = 10
        super().__init__("cabeca", x, y, altura, largura, limiteVel, 0, dano_contato, "cabeca", [], cor, 0)


    @property
    def quebrado(self):
        return self.__quebrado

    @property
    def descanso_poder_max(self):
        return self.__descanso_poder_max

    @descanso_poder_max.setter
    def descanso_poder_max(self, descanso_poder_max):
        self.__descanso_poder_max = descanso_poder_max

    @property
    def numero_de_projeteis(self):
        return self.__numero_de_projeteis

    @numero_de_projeteis.setter
    def numero_de_projeteis(self, numero_de_projeteis):
        self.__numero_de_projeteis = numero_de_projeteis

    def renderizar_sprite(self, tela, mapa):
        "renderiza na tela na posicao correta"
        if self.fase < 4:
            self.sprite.imprimir(tela, "cabeca", self.x - mapa.campo_visivel.x, self.y - mapa.campo_visivel.y,
                                 orientacao = self.face, velx = 1 * (self.__quebrado), frame = int((mapa.escala_tempo != 0)*mapa.ciclo/6) % 8)
        else:
            self.sprite.imprimir(tela, "cabeca_final", self.x - mapa.campo_visivel.x, self.y - mapa.campo_visivel.y,
                                 orientacao = self.face, frame = int((mapa.escala_tempo != 0) * mapa.ciclo / 6) % 8)

    def atualizar(self, tela, mapa, dimensoes_tela):

        if not self.montado: self.montar(mapa)

        if mapa.jogador.x >= self.x:
            self.face = 1
        else:
            self.face = -1

        self.renderizar(tela, mapa)

        ##### ATUALIZACAO DA CABECA #####
        self.x = self.rei.x + 45
        self.y = self.rei.y - 59
        self.corpo = pygame.Rect(self.x, self.y, self.largura, self.altura)

        ##### FAZ ELE ATIRAR FOGO #####
        if mapa.jogador.x <= self.x:
            dstancia = (((mapa.jogador.y + mapa.jogador.altura) - (self.y + self.altura)) ** 2 + (
                    mapa.jogador.x - self.x - 15 * self.face) ** 2) ** (1 / 2)
            divisor = max(dstancia / self.__vel_projetil, 0.001)
            velx = (mapa.jogador.x - self.x - 15 * self.face) / divisor
        else:
            dstancia = (((mapa.jogador.y + mapa.jogador.altura) - (self.y + self.altura)) ** 2 + (
                    mapa.jogador.x - self.corpo.bottomright[0] - 15 * self.face) ** 2) ** (1 / 2)
            divisor = max(dstancia / self.__vel_projetil, 0.001)
            velx = (mapa.jogador.x - self.corpo.bottomright[0] - 15 * self.face) / divisor
        vely = ((mapa.jogador.y) - (self.y)) / divisor

        ##### FALA PRA ELE QUANDO ATIRAR FOGO #####
        if self.fase == 1:
            numero_de_projeteis = 0
            self.descanso_poder_max = 200
        elif self.fase == 2:
            numero_de_projeteis = 5
            self.descanso_poder_max = 150
        else:
            numero_de_projeteis = 1
            self.descanso_poder_max = 250
        if self.__descanso_poder <= 0:
            for i in range(numero_de_projeteis):
                self.__poder.acao(self, tela, mapa, velx, vely, 0+10*i)
            self.__descanso_poder = self.__descanso_poder_max# + randrange(0, 50)
        else:
            self.__descanso_poder -= 1 * mapa.escala_tempo

    def colisao_jogador(self, jogador, direcao, mapa):
        "Detecta colisao com jogador, return dano caso valido"
        ##### COLISAO ESQUERDA #####
        if not jogador.invisivel:
            if direcao == "esquerda":
                if jogador.velx <= 0:
                    if jogador.velx <= -8: #cabeça toma dano se for batida via dash
                        self.__quebrado = True
                    jogador.velx = 0
                    jogador.aceleracao = 0
                    jogador.x = self.corpo.right + 1
                return 0
            ##### COLISAO DIREITA #####
            elif direcao == "direita":
                if jogador.velx >= 0:
                    if jogador.velx >= 8: #cabeça toma dano se for batida via dash
                        self.__quebrado = True
                    jogador.velx = 0
                    jogador.aceleracao = 0
                    jogador.x = self.corpo.left - jogador.largura
                return 0
            ##### COLISAO BAIXO #####
            elif direcao == "baixo":
                jogador.vely = 0
                jogador.y = self.corpo.top - jogador.altura
                if self.fase != 4:
                    return 1
                else:
                    for ganhar in mapa.lista_de_entidades:
                        if isinstance(ganhar, Vitoria):
                            entidade_vitoria = ganhar
                    entidade_vitoria.x = 400
                    self.finalizar_jogo()
                    return 0
            ##### COLISAO CIMA #####
            elif direcao == "cima":
                if jogador.vely < 0:
                    jogador.vely = 0
                    jogador.y = self.corpo.bottom
                return 0
        else:
            return 0


@instanciavel
class CoracaoRoxo(ParteDoRei):
    """Coracao do Rei das Cores
    
    Pode parar o tempo
    """
    def __init__(self, x, y):
        #self.__rei = 0
        altura = 29
        largura = 29
        dano_contato = 0
        cor = (255,0,255)
        limiteVel = 4
        self.__tempo_parado = 100 #contador de tempo parado
        super().__init__("coracao", x, y, altura, largura, limiteVel, 0, dano_contato, "coracao", [], cor, 0)

    def parar_o_tempo(self, jogador):
        if self.__tempo_parado > 0:
            self.__tempo_parado -= 1
            jogador.congelar()
            return True
        else:
            self.__tempo_parado = 100
            jogador.descongelar()
            return False

    def renderizar_sprite(self, tela, mapa):
        "renderiza na tela na posicao correta"
        self.sprite.imprimir(tela, "coracao",
                             self.x - mapa.campo_visivel.x,
                             self.y - mapa.campo_visivel.y,
                             orientacao = self.face)

    def atualizar(self, tela, mapa, dimensoes_tela):
        if not self.montado: self.montar(mapa)

        self.renderizar(tela, mapa)

        ##### ATUALIZACAO DA POSICAO #####
        self.x = self.rei.x + 61
        self.y = self.rei.y + 100
        self.corpo = pygame.Rect(self.x, self.y, self.largura,self.altura)

    def colisao_jogador(self, jogador, direcao, mapa):
        "Determina que o jogador fique mais lento ao passar"
        if not jogador.invisivel:
            jogador.escala_tempo = 0.25
        return 0

    def colisao_outros(self, entidade, direcao, mapa):
        pass


@instanciavel
class ReiDasCores(Entidade):
    """O Monarca dos Pigmentos,
    O Imperador das frequencias eletromagneticas
    """
    def __init__(self, x, y, height):
        ##### PARTES DO CORPO #####
        self.__cabeca = 0
        self.__punho_esquerdo = 0
        self.__punho_direito = 0
        self.__coracao = 0
        super().__init__("corpo_das_cores", x, y, 300, 150, 0, 0, 0, "corpo_das_cores",
                         [Bala, Coletavel, ParteDoRei], (0, 0, 255), 9, True)
        self.velx = 1

        ##### ATRIBUTOS REFERENTES A FASE DA LUTA #####
        self.__fase = 0 #0, 1-Vermelho, 2-Laranja, 3-Azul, 4-Roxo
        self.__entidades_da_fase = [PlataformaMovel(height-150, x-300, 200, 0),
                                    PlataformaMovel(height-280, x-500, 200, 0),
                                    PlataformaMovel(height-400, x-300, 200, 0),
                                    PlataformaMovel(height-150, x+550, 200, 0),
                                    PlataformaMovel(height-280, x+750, 200, 0),
                                    PlataformaMovel(height-400, x+550, 200, 0),
                                    ]
        self.__vida_gelatinosa = 15
        self.__gota = 3
        self.__enjoo = 5
        self.__tempo_parado = False

        ##### ATRIBUTOS DE POSICIONAMENTO #####
        self.__posicao_inicial = x
        self.__posicao_final = x + 300

    @property
    def fase(self):
        return self.__fase

    @property
    def punho_esquerdo(self):
        return self.__punho_esquerdo

    @punho_esquerdo.setter
    def punho_esquerdo(self, punho_esquerdo):
        self.__punho_esquerdo = punho_esquerdo

    @property
    def punho_direito(self):
        return self.__punho_direito

    @punho_direito.setter
    def punho_direito(self, punho_direito):
        self.__punho_direito = punho_direito

    @property
    def cabeca(self):
        return self.__cabeca

    @cabeca.setter
    def cabeca(self, cabeca):
        self.__cabeca = cabeca

    @property
    def coracao(self):
        return self.__coracao

    @coracao.setter
    def coracao(self, coracao):
        self.__coracao = coracao

    def toma_dano_de_fogo(self):
        self.__vida_gelatinosa -= 1

    def spawn_poder(self,mapa,poder):
        if self.corpo.x > mapa.jogador.corpo.x:
            self.__entidades_da_fase.append(poder(self.__posicao_inicial-216,mapa.tamanho[1]-200))
        else:
            self.__entidades_da_fase.append(poder(self.__posicao_inicial+684,mapa.tamanho[1]-200))

    def fase_1(self, mapa):
        "Comeca fase 1 da batalha, com poder vermelho"
        self.__entidades_da_fase = [PlataformaMovel(mapa.tamanho[1]-150, self.__posicao_inicial-300, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-280, self.__posicao_inicial-500, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-400, self.__posicao_inicial-300, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-150, self.__posicao_inicial+550, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-280, self.__posicao_inicial+750, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-400, self.__posicao_inicial+550, 200, 0),
                                    Saltante(self.__posicao_inicial-300, mapa.tamanho[1] - 150),
                                    Saltante(self.__posicao_inicial+950, mapa.tamanho[1] - 150)
                                    ]
        self.spawn_poder(mapa, TintaVermelha)
    def fase_2(self, mapa):
        "Comeca fase 2 da batalha, com poder laranja"
        self.__entidades_da_fase = [PlataformaMovel(mapa.tamanho[1]-150, self.__posicao_inicial-300, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-280, self.__posicao_inicial-500, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-400, self.__posicao_inicial-300, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-150, self.__posicao_inicial+550, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-280, self.__posicao_inicial+750, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-400, self.__posicao_inicial+550, 200, 0),
                                    Atirador(self.__posicao_inicial-250, mapa.tamanho[1]-500),
                                    Atirador(self.__posicao_inicial+600, mapa.tamanho[1]-500),
                                    ]
        self.spawn_poder(mapa, TintaLaranja)
    def fase_3(self, mapa):
        "Comeca fase 3 da batalha, com poder azul"
        self.__entidades_da_fase = [PlataformaMovel(mapa.tamanho[1]-150, self.__posicao_inicial-300, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-280, self.__posicao_inicial-500, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-400, self.__posicao_inicial-300, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-150, self.__posicao_inicial+550, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-280, self.__posicao_inicial+750, 200, 0),
                                    PlataformaMovel(mapa.tamanho[1]-400, self.__posicao_inicial+550, 200, 0),
                                    Gota("R", self.__posicao_inicial-500, mapa.tamanho[1]-350, self),
                                    Gota("G", self.__posicao_inicial+850, mapa.tamanho[1]-350, self),
                                    Gota("B", self.__posicao_inicial+200, mapa.tamanho[1]-600, self)
                                    ]
        self.spawn_poder(mapa, TintaAzul)
    def fase_4(self, mapa):
        "Comeca fase 4 da batalha, com poder roxo"
        self.__entidades_da_fase = [PlataformaMovel(mapa.tamanho[1]-150, self.__posicao_inicial-250, 100, 4),
                                    PlataformaMovel(mapa.tamanho[1]-300, self.__posicao_inicial-150, 100, 4),
                                    PlataformaMovel(mapa.tamanho[1]-300, self.__posicao_inicial+500, 100, 4),
                                    PlataformaMovel(mapa.tamanho[1]-150, self.__posicao_inicial+600, 100, 4),]
        self.spawn_poder(mapa, TintaRoxa)
    def fase_5(self, mapa):
        "Termina Batalha"
        self.__entidades_da_fase = []
        for ganhar in mapa.lista_de_entidades:
            if isinstance(ganhar, Vitoria):
                ganhar.x = self.x+12
                ganhar.corpo.x = self.x+12
                break
        

    def jogador_pega_gota(self):
        "Remove uma das gotas do rei e cura o jogador"
        if self.__gota > 0:
            self.__gota -= 1
            self.__tempo_parado = True

    def passar_fase(self, mapa):
        "Inicia a proxima fase"
        ##### INCREMENTA A FASE #####
        self.__fase += 1
        self.__cabeca.passar_fase()
        self.__coracao.passar_fase()
        self.__punho_esquerdo.passar_fase()
        self.__punho_direito.passar_fase()

        ##### LIMPA ENTIDADES DA FASE ANTERIOR #####
        for entidade in self.__entidades_da_fase:
            if entidade in mapa.lista_de_entidades:
                mapa.lista_de_entidades.remove(entidade)

        if self.__fase == 1: self.fase_1(mapa)
        if self.__fase == 2: self.fase_2(mapa)
        if self.__fase == 3: self.fase_3(mapa)
        if self.__fase == 4: self.fase_4(mapa)
        if self.__fase == 5: self.fase_5(mapa)
        for entidade in self.__entidades_da_fase:

        ##### CRIA INIMIGOS DA NOVA FASE #####
            mapa.lista_de_entidades.append(entidade)

    def atualizar(self, tela, mapa, dimensoes_tela):
        ##### 25 FRAMES PRO JOGO CARREGAR TUDO #####
        if self.__enjoo == 1:
            for entidade in self.__entidades_da_fase: ##### CRIA INIMIGOS DA NOVA FASE #####
                mapa.lista_de_entidades.append(entidade)
        if self.__enjoo: self.__enjoo -= 1

        ##### PASSA AS FASES DA LUTA #####
        else:
            if self.__fase == 0:
                if self.punho_direito.quebrado and self.punho_esquerdo.quebrado:
                    self.passar_fase(mapa)
            if self.__fase == 1: #Jogador com dash
                if self.__cabeca.quebrado:
                    self.passar_fase(mapa)
            if self.__fase == 2: #Jogador com fogo
                if self.__vida_gelatinosa <= 0:
                    self.passar_fase(mapa)
            if self.__fase == 3: #Jogador invisivel
                if not self.__gota:
                    self.passar_fase(mapa)
            if self.__fase == 4:
                if self.__cabeca.fim_de_jogo:
                    self.passar_fase(mapa)
                    mapa.lista_de_entidades.remove(self.cabeca)
                    mapa.lista_de_entidades.remove(self.punho_esquerdo)
                    mapa.lista_de_entidades.remove(self.punho_direito)
                    mapa.lista_de_entidades.remove(self.coracao)
                    mapa.lista_de_entidades.remove(self)

        ##### ATUALIZACAO DO TEMPO PARADO #####
        if self.__tempo_parado:
            mapa.render_escala_tempo = 0
            self.__tempo_parado = self.__coracao.parar_o_tempo(mapa.jogador)

        ##### COISA BASICA #####
        self.mover(dimensoes_tela, mapa)
        self.renderizar(tela, mapa)

    def mover(self, dimensoesTela, mapa):
        ##### ATUALIZA A ESCALA TEMPO #####
        self.escala_tempo = mapa.escala_tempo

        ##### COLISOES #####
        obsBaixo = self.gerenciar_colisoes(mapa)

        ##### GRAVIDADE ######
        if not obsBaixo: self.vely += gravidade * self.escala_tempo

        ##### ATUALIZACAO DAS POSICOES #####
        self.y += self.vely * self.escala_tempo
        self.x += self.velx * self.escala_tempo

        if self.x > self.__posicao_final  or self.x < self.__posicao_inicial:
            self.velx = -self.velx

        self.corpo = pygame.Rect(self.x, self.y, self.largura, self.altura)

    def colisao_jogador(self, jogador, direcao, mapa):
        "Determina que o jogador fique mais lento ao passar"
        if not jogador.invisivel:
            jogador.escala_tempo = 0.25
        return 0

    def colisao_outros(self, entidade, direcao, mapa):
        pass