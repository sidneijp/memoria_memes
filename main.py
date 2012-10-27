#coding: utf-8

import pygame
from pygame.locals import *
from pygame.rect import Rect
from random import shuffle
#from random import random # Em construcao
import time
import math

pygame.init()

VAZIO = pygame.Color(0, 0, 0, 0)
FUNDO_CARTA = pygame.image.load("imagens/fundo.jpg")
TEMPO = (2,0)
DESCONTO = 5
ESPERA = 2
FONTE = pygame.font.SysFont('arial', 15)
MEMES = [("challenge.png", 0),
        ("foreveralone.png", 1),
        ("fuckyea.png", 2),
        ("fuuu.png", 3),
        ("lolguy.png", 4),
        ("okguy.png", 5),
        ("poker.png", 6),
        ("troll.png", 7)]
MEMES.extend(list(MEMES))

class SceneManager(object):
    """ Classe que gerencia as Cenas"""
    
    scene = None #cena atual
    screen = None #surface da tela
    
    @staticmethod
    def createWindow(width, height, depth=32):
        """ cria a janela do pygame """
        # SRCALPHA para permitir trasnparencia
        SceneManager.screen = pygame.display.set_mode((width, height), SRCALPHA, depth)
    
    @staticmethod
    def run():
        while SceneManager.scene != None:
            SceneManager.scene.main()
    
    @staticmethod
    def isScene(scene):
        return SceneManager.scene == scene
    
    @staticmethod
    def exit():
        SceneManager.scene = None

class SceneBase(object):

    def main(self):
        self.start()
        while SceneManager.isScene(self):
            self.update()
        self.finish()
    
    def start(self):
        pass
    
    def update(self):
        self.draw()
        self.render()
        for e in pygame.event.get():
            self.pygame_events(e)
        self.process()
    
    def draw(self):
        pygame.display.update()
        
    def render(self):
        SceneManager.screen.fill(VAZIO)
    
    def pygame_events(self, e):
        if e.type == QUIT:
            SceneManager.exit()
    
    def process(self):
        pass
        
    def finish(self):
        pass

class Botao(object):

    def __init__(self, nome, imagem, x=0, y=0):
        self.nome = nome
        self.imagem = pygame.image.load("imagens/" + imagem)
        self.x = x - self.imagem.get_width()/2
        self.y = y
        self.selecionada = False #ignorar

    def render(self):
        if self.selecionada: #ignorar
            return #ignorar
        SceneManager.screen.blit(self.imagem, (self.x, self.y))
    
    def verificarClique(self, x, y):
        if x >= self.x and x <= self.x + self.imagem.get_width():
            if y >= self.y and y <= self.y + self.imagem.get_height():
                return True
        return False
        
class Relogio(object):

    def __init__(self, minutos, segundos=0):
        self.minutos = minutos
        self.segundos = segundos
        
    def decremento(self):
        if self.segundos > 0:
            self.segundos -= 1
        else:
            self.minutos -= 1
            self.segundos = 59
        
    def zero(self):
        if self.minutos < 0:
            return True
        return False
        
    def render(self, x, y):
        texto = "Tempo: %2d : %2d" % (self.minutos, self.segundos)
        fonte_superficie = FONTE.render(texto, False, Color(255,255,255))
        SceneManager.screen.blit(fonte_superficie, (x, y))
        
class Carta(object):
    """ Classe que define as cartas do jogo """
    
    def __init__(self, image, par_id, x=0, y=0, selecionada=False):
        self.imagem = pygame.image.load("imagens/" + image)
        self.x = x
        self.y = y
        self.par_id = par_id
        self.selecionada = selecionada
        self.retirada = False
        
    def render(self):
        if self.retirada:
            return
        if self.selecionada:
            SceneManager.screen.blit(self.imagem, (self.x, self.y))
        else:
            SceneManager.screen.blit(FUNDO_CARTA, (self.x, self.y))
    
    def verificarClique(self, x, y):
        if self.retirada:
            return False
        if x >= self.x and x <= self.x + self.imagem.get_width():
            if y >= self.y and y <= self.y + self.imagem.get_height():
                return True
        return False
        
    def retirarCarta(self):
        superficie = pygame.Surface((self.imagem.get_width(), self.imagem.get_height()))
        SceneManager.screen.blit(superficie, (self.x, self.y))
        self.retirada = True

class CenaInicial(SceneBase):
    """ Tela inicial do Jogo """
    
    def start(self):
        self.mouse_button = False
        self.mouse_pos = (-1, -1)
        self.opcoes = [ Botao("iniciar", "iniciar.png", x=1168/2, y=100),
                        Botao("ranking", "ranking.png", x=1168/2, y=160),
                        #Botao("creditos", "creditos.png", x=1168/2, y=300),
                        Botao("sair", "sair.png", x=1168/2, y=220) ]
        
    def render(self):
        FUNDO = pygame.image.load("imagens/plano_de_fundo.jpg")
        SceneManager.screen.blit(FUNDO, (0, 0))
        for opcao in self.opcoes:
            opcao.render()
        
    def pygame_events(self, e):
        super(CenaInicial, self).pygame_events(e)
        if e.type == MOUSEBUTTONDOWN:
            self.mouse_button = True
            self.mouse_pos = e.pos
            
    def process(self):
        opcao = self.opcaoClicada()
        if opcao is not None:
            if opcao.nome == "iniciar":
                SceneManager.scene = CenaJogo()
            elif opcao.nome == "ranking":
                SceneManager.scene = CenaPontuacoes()
            elif opcao.nome == "creditos":
                SceneManager.scene = CenaCreditos()
            elif opcao.nome == "sair":
                SceneManager.exit()
        self.mouse_button = False # resetar clique
        
    def opcaoClicada(self):
        x = self.mouse_pos[0]
        y = self.mouse_pos[1]
        if self.mouse_button:
            for opcao in self.opcoes:
                if opcao.verificarClique(x, y):
                    return opcao
        return None
    
    def finish(self):
        del self.opcoes
        del self.mouse_pos
        del self.mouse_button
        
#Cena do Jogo
class CenaJogo(SceneBase):
    """ Tela principal do Jogo """
    
    def start(self, nivel=0):
        self.cartas = []
        self.mouse_button = False
        self.mouse_pos = (-1, -1)
        self.turno = 0
        self.par = []
        self.tempo = time.time()
        self.relogio = Relogio(*TEMPO)
        self.pontuacao = 0
        self.tempo2 = time.time()
        self.espera = ESPERA
        self.acertou = False

        nomes_imagens = list(MEMES)
        shuffle(nomes_imagens)
        shuffle(nomes_imagens)
        for i in range(8):
            for j in range(2):
                par = nomes_imagens.pop()
                self.cartas.append(Carta(par[0], par[1], 32 + i*(124+16), 32 + j*(164+16), True))
    
    def render(self):
        super(CenaJogo, self).render()
        pygame.draw.rect(SceneManager.screen, (255,255,255), Rect((16, 16), (1120 + 16, 380)), 1)
        for c in self.cartas:
            c.render()
        self.relogio.render(100, 400)
        texto = "Pontuacao: %d" % (self.pontuacao,)
        fonte_superficie = FONTE.render(texto, False, Color(255,255,255))
        SceneManager.screen.blit(fonte_superficie, (500, 400))
    
    def pygame_events(self, e):
        super(CenaJogo, self).pygame_events(e)
        if e.type == MOUSEBUTTONDOWN:
            self.mouse_button = True
            self.mouse_pos = e.pos
    
    def process(self):
        if len(self.cartas) == 0:
            SceneManager.scene = CenaFimPartida("venceu")
        if self.relogio.zero():
            SceneManager.scene = CenaFimPartida("perdeu")
        if self.turno != 0 and (time.time() - self.tempo) >= 1:
            self.relogio.decremento()
            self.tempo = time.time()
        if (time.time() - self.tempo2) <= self.espera:
            self.mouse_button = False
            return
        else:
            self.espera = 0
            
        c = self.cartaClicada()
        if self.turno == 0:
            self.turno = 1
            for c in self.cartas:
                c.selecionada = False
            #self.cartas = [] #TESTE - VENCER
        elif self.turno == 1:
            if c:
                c.selecionada = True
                self.par.append(c)
                self.turno = 2
        elif self.turno == 2:
            if c:
                #if c == self.par[0]: #Se clicar na mesma carta
                #    c.selecionada = False
                #    self.par = []
                #    self.turno = 1
                if c != self.par[0]: #Se clicar em carta diferente
                    c.selecionada = True
                    self.par.append(c)
                    if self.par[0].par_id == self.par[1].par_id: #se o par corresponde
                        #Acerto
                        self.acertou = True
                        self.pontuacao += 1
                        #self.par[0].retirarCarta()
                        #self.par[1].retirarCarta()
                        self.espera = 1
                        self.tempo2 = time.time()
                    else:
                        #Erro
                        self.espera = 1
                        self.tempo2 = time.time()
                        for _ in xrange(DESCONTO):
                            self.relogio.decremento()
                    self.turno = 3
        elif self.turno == 3:
            if self.acertou:
                self.cartas.remove(self.par[0])
                self.cartas.remove(self.par[1])
                self.acertou = False
            else:
                self.par[0].selecionada = False
                self.par[1].selecionada = False
            self.par = []
            self.turno = 1
        self.mouse_button = False # reseta o clique
    
    def cartaClicada(self):
        x = self.mouse_pos[0]
        y = self.mouse_pos[1]
        if self.mouse_button:
            for c in self.cartas:
                if c.verificarClique(x, y):
                    return c
        return None
    
    def finish(self):
        del self.cartas
        del self.mouse_button
        del self.mouse_pos
        del self.turno
        del self.par
        del self.tempo
        del self.relogio
        del self.pontuacao
        del self.tempo2
        del self.espera
        del self.acertou

class CenaFimPartida(SceneBase):

    def __init__(self, resultado):
        if resultado == "venceu":
            self.imagem = pygame.image.load("imagens/venceu.png")
        elif resultado == "perdeu":
            self.imagem = pygame.image.load("imagens/perdeu.png")
        self.tempo = time.time()
        self.espera = 2
        self.mouse_button = False
        
    def render(self):
        SceneManager.screen.blit(self.imagem, (0, 0))
        
    def pygame_events(self, e):
        super(CenaFimPartida, self).pygame_events(e)
        if e.type == MOUSEBUTTONDOWN:
            self.mouse_button = True

    def process(self):
        if (time.time() - self.tempo) >= self.espera and self.mouse_button:
            SceneManager.scene = CenaInicial()
    
    def finish(self):
        del self.imagem
        del self.tempo
        del self.espera
        del self.mouse_button
        
class CenaPontuacoes(SceneBase):

    def __init__(self):
        self.imagem = pygame.image.load("imagens/emcontrucao.png")
        self.tempo = time.time()
        self.espera = 2
        self.mouse_button = False
        
    def render(self):
        SceneManager.screen.blit(self.imagem, (0, 0))
        
    def pygame_events(self, e):
        super(CenaPontuacoes, self).pygame_events(e)
        if e.type == MOUSEBUTTONDOWN:
            self.mouse_button = True

    def process(self):
        if (time.time() - self.tempo) >= self.espera and self.mouse_button:
            SceneManager.scene = CenaInicial()
            
    def finish(self):
        del self.imagem
        del self.tempo
        del self.espera
        del self.mouse_button

#class CenaCreditos(SceneBase):
#    pass #
    
if __name__ == "__main__":
    SceneManager.createWindow(1120 + 48, 480)
    SceneManager.scene = CenaInicial()
    SceneManager.run()
