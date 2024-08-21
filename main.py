import pygame

largura = 1920
altura = 1080
loop = True
imagem_fundo = pygame.image.load('Wander-Warriors/src/cenario.png')
player = pygame.image.load()
givo = pygame.image.load()
raf = pygame.image.load()
hel = pygame.image.load()
mat = pygame.image.load()
pos_y_player = 400
pos_x_player = 420
vel_player = 10
janela = pygame.display.set_mode((largura,altura))
pygame.display.set_caption('Wander Warriors')

while loop:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      loop = False
  teclas = pygame.key.get_pressed()
  #Se pressionar a tecla para cima, o perssonagem se move para cima
  if teclas[pygame.K_UP]:
    pos_y_player -= vel_player
  #Se pressionar a tecla para baixo, o perssonagem se move para baixo
  if teclas[pygame.K_DOWN]:
    pos_y_player += vel_player
  #Se pressionar a tecla para esquerda, o perssonagem se move para esquerda
  if teclas[pygame.K_LEFT]:
    pos_x_player -= vel_player
  #Se pressionar a tecla para direita, o perssonagem se move para direita
  if teclas[pygame.K_RIGHT]:
    pos_x_player += vel_player
  pygame.display.update()
  janela.blit(imagem_fundo, (0,0))
  janela.blit(player, (400,300))