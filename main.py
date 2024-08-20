import pygame

largura = 1920
altura = 1080
loop = True
imagem_fundo = pygame.image.load('Wander-Warriors/src/cenario.png')
janela = pygame.display.set_mode((largura,altura))
pygame.display.set_caption('Wander Warriors')

while loop:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      loop = False
  pygame.display.update()
  janela.blit(imagem_fundo, (0,0))