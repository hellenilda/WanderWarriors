import pygame

# Inicialização do pygame
pygame.init()

# Configurações da tela
largura = 1080
altura = 720
janela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Wander Warriors')

# Carregamento das imagens e redimensionamento dos personagens
player = pygame.image.load('assets/personagens/player.png')
enemy = pygame.image.load('assets/personagens/inimigos.png')

# Redimensionar os personagens (exemplo: metade do tamanho original)
largura_player, altura_player = player.get_size()
player = pygame.transform.scale(player, (largura_player // 2, altura_player // 2))

largura_enemy, altura_enemy = enemy.get_size()
enemy = pygame.transform.scale(enemy, (largura_enemy // 2, altura_enemy // 2))

# Configurações dos personagens
pos_x_player, pos_y_player = 10, 10
vel_player = 2

pos_x_enemy, pos_y_enemy = 500, 300

# Loop principal do jogo
loop = True
while loop:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = False

    teclas = pygame.key.get_pressed()
    # Movimento do personagem
    if teclas[pygame.K_UP]:
        pos_y_player -= vel_player
    if teclas[pygame.K_DOWN]:
        pos_y_player += vel_player
    if teclas[pygame.K_LEFT]:
        pos_x_player -= vel_player
    if teclas[pygame.K_RIGHT]:
        pos_x_player += vel_player

    # Criando os retângulos dos personagens
    player_rect = pygame.Rect(pos_x_player, pos_y_player, largura_player // 2, altura_player // 2)
    enemy_rect = pygame.Rect(pos_x_enemy, pos_y_enemy, largura_enemy // 2, altura_enemy // 2)

    # Verificação de colisão
    if player_rect.colliderect(enemy_rect):
        print("Colisão detectada!")
        # Exemplo de interação: parar o jogador ao colidir
        pos_x_player -= vel_player if teclas[pygame.K_RIGHT] else 0
        pos_x_player += vel_player if teclas[pygame.K_LEFT] else 0
        pos_y_player -= vel_player if teclas[pygame.K_DOWN] else 0
        pos_y_player += vel_player if teclas[pygame.K_UP] else 0

    # Atualização da tela
    janela.fill((0, 0, 0))  # Preenche a tela com uma cor preta antes de desenhar as imagens
    janela.blit(player, (pos_x_player, pos_y_player))
    janela.blit(enemy, (pos_x_enemy, pos_y_enemy))
    pygame.display.update()

# Encerrando o pygame
pygame.quit()
