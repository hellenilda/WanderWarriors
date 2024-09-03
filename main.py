import pygame
import sys

# Função para inicialização da tela
def iniciar_tela():
    largura, altura = 1280, 720
    screen = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption('Wander Warriors')
    clock = pygame.time.Clock()
    return screen, clock

# Função para carregar e redimensionar imagens
def dimensoes_imagem(caminho, dimensoes):
    return pygame.transform.scale(pygame.image.load(caminho).convert_alpha(), dimensoes)

# Função para carregar sprites de animação
def carregar_frames_animacao(caminho_base, quant_frames, dimensoes):
    return [dimensoes_imagem(f"{caminho_base}{i}.png", dimensoes) for i in range(1, quant_frames + 1)]

# Função para carregar balões de fala
def coletar_baloes_fala(quant, dimensoes, npc):
    return [dimensoes_imagem(f'Sprites/dialogos/{npc}/{i}.png', dimensoes) for i in range(1, quant + 1)]

# Função para desenhar a caixa de texto
def desenhar_balao_fala(supeficie, imagem_balao, largura_tela):
    bubble_rect = imagem_balao.get_rect(midbottom=(largura_tela // 2, supeficie.get_height() - 10))
    supeficie.blit(imagem_balao, bubble_rect)

# Função para criar um sprite
def criar_sprite(caminho_imagem, pos, grupo, dimensoes=None):
    sprite = pygame.sprite.Sprite(grupo)
    sprite.image = dimensoes_imagem(caminho_imagem, dimensoes) if dimensoes else pygame.image.load(caminho_imagem).convert_alpha()
    sprite.rect = sprite.image.get_rect(topleft=pos)
    return sprite

# Função para verificar colisões de limite
def verificar_limites_tela(rect, boundary_rect):
    rect.clamp_ip(boundary_rect)

# Função para criar o jogador
def criar_player(pos, grupo, sprites_obstaculos, frames):
    player = pygame.sprite.Sprite(grupo)
    player.frames = frames
    player.frame_index = 0
    player.image = player.frames[player.frame_index]
    player.rect = player.image.get_rect(center=pos)
    player.direction = pygame.math.Vector2()
    player.speed = 5
    player.animation_speed = 0.15
    player.sprites_obstaculos = sprites_obstaculos
    return player

# Função para atualizar a entrada do jogador
def movimentacao_player(player, wanderley_up, wanderley_down, wanderley_right):
    keys = pygame.key.get_pressed()
    player.direction.x, player.direction.y = 0, 0

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player.direction.y = -1
        player.frames = wanderley_up
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player.direction.y = 1
        player.frames = wanderley_down
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.direction.x = 1
        player.frames = wanderley_right
    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.direction.x = -1
        player.frames = [pygame.transform.flip(frame, True, False) for frame in wanderley_right]

# Função para animar o jogador
def animar_frames_jogador(player):
    if player.direction.length() > 0:
        player.frame_index += player.animation_speed
        if player.frame_index >= len(player.frames):
            player.frame_index = 0
    else:
        player.frame_index = 1  # Frame de idle
    player.image = player.frames[int(player.frame_index)]

# Função para mover o jogador e lidar com colisões
def eventos_colisoes_movimentos(player, velocidade, regiao_cenario):
    player.rect.x += player.direction.x * velocidade
    verificar_colisao(player, 'horizontal')
    player.rect.y += player.direction.y * velocidade
    verificar_colisao(player, 'vertical')
    verificar_limites_tela(player.rect, regiao_cenario)

# Função para verificar colisão com obstáculos
def verificar_colisao(player, direcao):
    for sprite in player.sprites_obstaculos:
        if sprite.rect.colliderect(player.rect):
            if direcao == 'horizontal':
                if player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                elif player.direction.x < 0:
                    player.rect.left = sprite.rect.right
            elif direcao == 'vertical':
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom

# Função para criar o grupo da câmera e configurar a superfície de exibição
def configuracoes_camera(regiao_cenario, cenario):
    group = pygame.sprite.Group()
    group.display_surface = pygame.display.get_surface()
    group.offset = pygame.math.Vector2()
    group.half_w, group.half_h = [dim // 2 for dim in group.display_surface.get_size()]
    group.camera_borders = {'left': 200, 'right': 200, 'top': 100, 'bottom': 100}

    l, t = group.camera_borders['left'], group.camera_borders['top']
    w, h = group.display_surface.get_size()
    w -= group.camera_borders['left'] + group.camera_borders['right']
    h -= group.camera_borders['top'] + group.camera_borders['bottom']
    group.camera_rect = pygame.Rect(l, t, w, h)

    group.ground_surf = cenario
    group.ground_rect = group.ground_surf.get_rect(topleft=(0, 0))

    group.internal_surf_size = (2500, 2500)
    group.internal_surf = pygame.Surface(group.internal_surf_size, pygame.SRCALPHA)
    group.internal_rect = group.internal_surf.get_rect(center=(group.half_w, group.half_h))
    group.internal_offset = pygame.math.Vector2(
        group.internal_surf_size[0] // 2 - group.half_w,
        group.internal_surf_size[1] // 2 - group.half_h
    )

    group.max_x = regiao_cenario.width - group.display_surface.get_width()
    group.max_y = regiao_cenario.height - group.display_surface.get_height()

    return group

# Função para centralizar a câmera no player (alvo)
def centralizar_camera(grupo_camera, alvo):
    grupo_camera.offset.x = min(max(alvo.rect.centerx - grupo_camera.half_w, 0), grupo_camera.max_x)
    grupo_camera.offset.y = min(max(alvo.rect.centery - grupo_camera.half_h, 0), grupo_camera.max_y)

# Função para desenhar elementos na tela usando a câmera
def desenhar_elementos(grupo_camera, player):
    centralizar_camera(grupo_camera, player)
    grupo_camera.internal_surf.fill('#71ddee')

    ground_offset = grupo_camera.ground_rect.topleft - grupo_camera.offset + grupo_camera.internal_offset
    grupo_camera.internal_surf.blit(grupo_camera.ground_surf, ground_offset)

    for sprite in sorted(grupo_camera.sprites(), key=lambda s: s.rect.centery):
        offset_pos = sprite.rect.topleft - grupo_camera.offset + grupo_camera.internal_offset
        grupo_camera.internal_surf.blit(sprite.image, offset_pos)

    grupo_camera.display_surface.blit(grupo_camera.internal_surf, grupo_camera.internal_rect)

# Função principal do jogo
def main():
    pygame.init()
    screen, clock = iniciar_tela()

    # Carrega e inicia a reprodução da música de fundo
    pygame.mixer.music.load('Músicas/22 - Dream.ogg')
    pygame.mixer.music.play(-1)

    # Carregar o cenário e as animações
    cenario = pygame.image.load('Sprites/ifpb.jpg').convert_alpha()
    wanderley_down = carregar_frames_animacao('Sprites/personagens/Vander/Baixo/Sprite-baixo-', 3, (64, 64))
    wanderley_up = carregar_frames_animacao('Sprites/personagens/Vander/Cima/Sprite-cima-', 3, (64, 64))
    wanderley_right = carregar_frames_animacao('Sprites/personagens/Vander/Lados/Sprite-lados-', 3, (64, 64))

    # Carregar balões de fala
    dimensoes_balao = (564, 350)
    baloes_fala = {
        'Hellen': coletar_baloes_fala(7, dimensoes_balao, 'Hellen'),  # 7 balões de fala para Hellen
        'Isac': coletar_baloes_fala(10, dimensoes_balao, 'Isac'),    # 2 balões de fala para Isac
        'Mateus': coletar_baloes_fala(10, dimensoes_balao, 'Mateus')   # 4 balões de fala para Mateus
    }

    regiao_cenario = cenario.get_rect()
    grupo_camera = configuracoes_camera(regiao_cenario, cenario)
    sprites_obstaculos = pygame.sprite.Group()

    # Criar o jogador
    player = criar_player((1350, 370), grupo_camera, sprites_obstaculos, wanderley_down)

    # Adicionar obstáculos
    sprites_colisores = [
        ('Sprites/colisores/bloco-adm.png', (0, 0), (1210, 500)),
        ('Sprites/colisores/estacionamento.png', (130, 785), (378, 257)),
        ('Sprites/colisores/frente-1.png', (50, 995), (1125, 180)),
        ('Sprites/colisores/frente-2.png', (1530, 940), (80, 200)),
        ('Sprites/colisores/lampada-1.png', (1536, 370), (45, 228)),
        ('Sprites/colisores/lampada-2.png', (1090, 790), (24, 95)),
        ('Sprites/colisores/lampada-2.png', (1330, 590), (24, 95))
    ]
    for caminho, pos, dimensoes in sprites_colisores:
        criar_sprite(caminho, pos, sprites_obstaculos, dimensoes)

    # Adicionar sprites de fundo
    fundo_info = [
        ('Sprites/colisores/arvore.png', (1292, 799), (97, 101)),
        ('Sprites/colisores/arco.png', (1165, 983), (355, 132)),
        ('Sprites/colisores/estacionamento-arbustos.png', (512, 768), (149, 91)),
        ('Sprites/colisores/rampa.png', (1210, 0), (390, 372))
    ]
    for caminho, pos, dimensoes in fundo_info:
        criar_sprite(caminho, pos, grupo_camera, dimensoes)

    # Instanciar NPCs com identificadores
    npcs = {
        'Hellen': criar_sprite('Sprites/personagens/NPCs/Hellen.png', (1420, 550), grupo_camera),
        'Isac': criar_sprite('Sprites/personagens/NPCs/Isac.png', (100, 550), grupo_camera),
        'Mateus': criar_sprite('Sprites/personagens/NPCs/Mateus.png', (1320, 1120), grupo_camera)
    }

    indice_atual_balao = 0
    ativar_balao = False
    interacao_npc = None  # Armazenar o nome do NPC interagido

    som_tocado = False 

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e and interacao_npc:
                    nome_npc = interacao_npc
                    kiki = pygame.mixer.Sound('Músicas/kiki.mp3')

                    # Dentro do loop principal
                    if ativar_balao:
                        # Avançar para o próximo balão
                        indice_atual_balao = (indice_atual_balao + 1) % len(baloes_fala[nome_npc])
                        if indice_atual_balao == 0:
                            ativar_balao = False  # Ocultar o balão após o último
                        if nome_npc == 'Isac' and indice_atual_balao == len(baloes_fala[nome_npc]) - 2 and not som_tocado:
                            kiki.play()
                            som_tocado = True  # Marcar que o som foi tocado

                    else:
                        ativar_balao = True  # Mostrar o balão


        # Atualizar entrada do jogador e movimento
        movimentacao_player(player, wanderley_up, wanderley_down, wanderley_right)
        eventos_colisoes_movimentos(player, player.speed, regiao_cenario)
        animar_frames_jogador(player)

        # Verificar interação com NPCs
        interacao_npc = None
        for nome_npc, npc_sprite in npcs.items():
            if player.rect.colliderect(npc_sprite.rect):
                interacao_npc = nome_npc
                break

        # Desenhar a tela de fundo
        screen.fill((0, 0, 0))

        # Desenhar elementos na tela
        desenhar_elementos(grupo_camera, player)

        # Desenhar o balão de fala se estiver ativo
        if ativar_balao and interacao_npc:
            bubble_set = baloes_fala.get(interacao_npc, [])
            if bubble_set:
                desenhar_balao_fala(screen, bubble_set[indice_atual_balao], screen.get_width())

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()