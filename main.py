#coding: utf-8

import pygame
from pygame.locals import *
from pygame.rect import Rect
from random import shuffle
import time
import math
from datetime import datetime
import pickle
import copy

pygame.init()

NAME_SIZE_LIMIT = 8
RANK_LIMIT = 10
RECORDS_FILE = 'data/records.db'
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

    def __init__(self, minutes, seconds=0):
        self.minutes = minutes
        self.seconds = seconds
        
    def decrement(self):
        if self.seconds > 0:
            self.seconds -= 1
        else:
            self.minutes -= 1
            self.seconds = 59
        
    def zero(self):
        if self.minutes < 0:
            return True
        return False

    def get_minutes(self):
        return self.minutes

    def get_seconds(self):
        return self.seconds

    def render(self, x, y):
        text = "Tempo: %2d : %2d" % (self.minutes, self.seconds)
        font_surface = FONTE.render(text, False, Color(255,255,255))
        SceneManager.screen.blit(font_surface, (x, y))

        
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


class Record(object):
    def __init__(self, score, time, date=datetime.now()):
        self.score = score
        self.time = time
        self.date = date 


class Rank(object):
    __records = None

    @classmethod
    def load(cls):
        if cls.__records is not None:
            return
        records_file = None
        try:
            records_file = open(RECORDS_FILE)
        except IOError:
            records_file = file(RECORDS_FILE, 'w')
            pickle.dump([], records_file, 2)
            records_file.close()
            records_file = open(RECORDS_FILE)
        cls.__records = pickle.load(records_file)
        cls.__records = sorted(cls.__records, key=lambda x: x.time)
        cls.__records = sorted(cls.__records, key=lambda x: x.score, reverse=True)

    @classmethod
    def __save(cls):
        records_file = file(RECORDS_FILE, 'w')
        pickle.dump(cls.__records, records_file, 2)

    @classmethod
    def is_record(cls, record):
        rank_length = len(cls.__records) 
        if rank_length < RANK_LIMIT:
            return True
        i = 0
        draw = False
        for i, r in enumerate(cls.__records[:RANK_LIMIT]):
            if record.score > r.score:
                return True
            if record.score == r.score:
                draw = True
                break
        if draw:
            for i, r in enumerate(cls.__records[i:RANK_LIMIT], i):
                if record.time < r.time:
                    return True
        return False

    @classmethod
    def get_records(cls):
        return copy.deepcopy(cls.__records)

    @classmethod
    def pop(cls):
        cls.__records.pop()
        cls.__save()

    @classmethod
    def add(cls, record):
        rank_length = len(cls.__records) 
        if rank_length == RANK_LIMIT:
            cls.__records.pop()
            rank_length = RANK_LIMIT - 1 
        i = 0
        draw = False
        for i, r in enumerate(cls.__records[:rank_length]):
            if record.score > r.score:
                cls.__records.insert(i, record)
                cls.__save()
                return
            if record.score == r.score:
                draw = True
                break
        if draw:
            for i, r in enumerate(cls.__records[i:rank_length], i):
                if record.time < r.time:
                    cls.__records.insert(i, record)
                    cls.__save()
                    return
        if rank_length < RANK_LIMIT:
            cls.__records.append(record)
            cls.__save()
        

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
            SceneManager.scene = CenaFimPartida("venceu", self.pontuacao, self.relogio)
        if self.relogio.zero():
            self.relogio = Relogio(0, 0)
            SceneManager.scene = CenaFimPartida("perdeu", self.pontuacao, self.relogio)
        if self.turno != 0 and (time.time() - self.tempo) >= 1:
            self.relogio.decrement()
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
        elif self.turno == 1:
            if c:
                c.selecionada = True
                self.par.append(c)
                self.turno = 2
        elif self.turno == 2:
            if c:
                if c != self.par[0]: #Se clicar em carta diferente
                    c.selecionada = True
                    self.par.append(c)
                    if self.par[0].par_id == self.par[1].par_id: #se o par corresponde
                        #Acerto
                        self.acertou = True
                        self.pontuacao += 1
                        self.espera = 1
                        self.tempo2 = time.time()
                    else:
                        #Erro
                        self.espera = 1
                        self.tempo2 = time.time()
                        for _ in xrange(DESCONTO):
                            self.relogio.decrement()
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

    def __init__(self, resultado, score, clock):
        seconds = TEMPO[0] * 60 + TEMPO[1] - (clock.get_minutes() * 60 + clock.get_seconds())
        self.name = ''
        self.record = Record(score, seconds)
        self.new_record = Rank.is_record(self.record)
        self.confirmed = True
        if self.new_record:
            self.input_name_imagem = pygame.image.load("imagens/fundo.jpg")
            self.confirmed = False
        if resultado == "venceu":
            self.imagem = pygame.image.load("imagens/venceu.png")
        elif resultado == "perdeu":
            self.imagem = pygame.image.load("imagens/perdeu.png")
        self.tempo = time.time()
        self.espera = 2
        self.mouse_button = False
        self.k_enter = False
        
    def render(self):
        SceneManager.screen.blit(self.imagem, (0, 0))
        if not self.confirmed and self.new_record:
            SceneManager.screen.blit(self.input_name_imagem, (0, 0))
            text = "Nome: %s" % self.name
            font_surface = FONTE.render(text, False, Color(255,255,255))
            SceneManager.screen.blit(font_surface, (0, 0))
        
    def pygame_events(self, e):
        super(CenaFimPartida, self).pygame_events(e)
        if e.type == KEYDOWN:
            if e.key == K_BACKSPACE:
                name_length = len(self.name)
                if name_length > 0:
                    self.name = self.name[0:name_length-1]
            elif e.key == K_RETURN:
                self.confirmed = True
                self.k_enter = True
            else:
                if len(self.name) < NAME_SIZE_LIMIT:
                        self.name += e.unicode
        if e.type == MOUSEBUTTONDOWN:
            self.mouse_button = True

    def process(self):
        if not self.new_record and (time.time() - self.tempo) >= self.espera and (self.mouse_button or self.k_enter):
            SceneManager.scene = CenaInicial()
        if self.new_record and self.confirmed:
            SceneManager.scene = CenaPontuacoes()
        self.mouse_button = False
        self.k_enter = False
    
    def finish(self):
        if self.new_record:
            self.record.name = self.name
            Rank.add(self.record)
            del self.input_name_imagem
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
        self.mouse_pos = (-1, -1)
        self.exit_button = Botao("sair", "sair.png", x=1168/2, y=220)
        
    def render(self):
        SceneManager.screen.blit(self.imagem, (0, 0))
        self.exit_button.render()
        text = 'Nome\tPontuação\tTempo'
        text = text.decode('utf-8')
        x = 0
        for i in text.split('\t'):
            font_surface = FONTE.render(i, False, Color(0, 0, 0))
            SceneManager.screen.blit(font_surface, (x, 0))
            x += 100
        y = font_surface.get_height() + 2
        for record in Rank.get_records():
            text = '%s\t%s\t%ss' % (record.name, record.score, record.time)
            text = text.decode('utf-8')
            x = 0
            for i in text.split('\t'):
                font_surface = FONTE.render(i, False, Color(0, 0, 0))
                SceneManager.screen.blit(font_surface, (x, y))
                x += 100
            y += font_surface.get_height() + 2
        
    def pygame_events(self, e):
        super(CenaPontuacoes, self).pygame_events(e)
        if e.type == MOUSEBUTTONDOWN:
            self.mouse_button = True
            self.mouse_pos = e.pos

    def process(self):
        opcao = self.opcaoClicada()
        if opcao is not None:
            if opcao.nome == "sair":
                SceneManager.scene = CenaInicial()
        self.mouse_button = False # resetar clique
            
    def finish(self):
        del self.imagem
        del self.tempo
        del self.espera
        del self.mouse_button
        del self.mouse_pos
        del self.exit_button
        
    def opcaoClicada(self):
        x = self.mouse_pos[0]
        y = self.mouse_pos[1]
        if self.mouse_button:
            if self.exit_button.verificarClique(x, y):
                return self.exit_button
        return None
#class CenaCreditos(SceneBase):
#    pass #
    
if __name__ == "__main__":
    Rank.load()
    SceneManager.createWindow(1120 + 48, 480)
    SceneManager.scene = CenaInicial()
    SceneManager.run()
