import pygame
import sys

# Inicialização do pygame
pygame.init()

# Configurações da tela
largura = 1600
altura = 1402
screen = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Wander Warriors')
clock = pygame.time.Clock()

# Carregamento das imagens e redimensionamento dos personagens
cenario = pygame.image.load('C:/Wander-Warriors/Cenário/ifpb.jpg').convert_alpha()

wanderley_down = [
    pygame.image.load('C:/Wander-Warriors/Sprites/Wander/Baixo/Sprite-baixo-1.png').convert_alpha(),
    pygame.image.load('C:/Wander-Warriors/Sprites/Wander/Baixo/Sprite-baixo-2.png').convert_alpha(),  # Idle
    pygame.image.load('C:/Wander-Warriors/Sprites/Wander/Baixo/Sprite-baixo-3.png').convert_alpha(),
]

wanderley_up = [
    pygame.image.load('C:/Wander-Warriors/Sprites/Wander/Cima/Sprite-cima-1.png').convert_alpha(),
    pygame.image.load('C:/Wander-Warriors/Sprites/Wander/Cima/Sprite-cima-2.png').convert_alpha(),
    pygame.image.load('C:/Wander-Warriors/Sprites/Wander/Cima/Sprite-cima-3.png').convert_alpha(),
]

wanderley_right = [
    pygame.image.load('C:/Wander-Warriors/Sprites/Wander/Lados/Sprite-lados-1.png').convert_alpha(),
    pygame.image.load('C:/Wander-Warriors/Sprites/Wander/Lados/Sprite-lados-2.png').convert_alpha(),
    pygame.image.load('C:/Wander-Warriors/Sprites/Wander/Lados/Sprite-lados-3.png').convert_alpha(),
]

# Carregar as imagens dos NPCs
npc1_image = pygame.image.load('C:/Wander-Warriors/Sprites/NPCs/Hell/Hellen.png').convert_alpha()
npc2_image = pygame.image.load('C:/Wander-Warriors/Sprites/NPCs/Isac/Isac.png').convert_alpha()
npc3_image = pygame.image.load('C:/Wander-Warriors/Sprites/NPCs/Mat/Mateus.png').convert_alpha()


# Classe NPC
class NPC(pygame.sprite.Sprite):
    def __init__(self, image, pos, group):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect(center=pos)


# Classe Player
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.frames = wanderley_down
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.animation_speed = 0.15

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.frames = wanderley_up  # Altera para a animação para cima
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.frames = wanderley_down  # Altera para a animação para baixo
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.frames = wanderley_right  # Altera para a animação para a direita
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.frames = [pygame.transform.flip(frame, True, False) for frame in wanderley_right]
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def animate(self):
        if self.direction.magnitude() != 0:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[int(self.frame_index)]
        else:
            self.frame_index = 1  # Frame de idle
            self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.input()
        self.animate()
        self.rect.center += self.direction * self.speed


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

        # box setup
        self.camera_borders = {'left': 200, 'right': 200, 'top': 100, 'bottom': 100}
        l = self.camera_borders['left']
        t = self.camera_borders['top']
        w = self.display_surface.get_size()[0] - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size()[1] - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(l, t, w, h)

        # ground
        self.ground_surf = cenario
        self.ground_rect = self.ground_surf.get_rect(topleft=(0, 0))

        # camera speed
        self.keyboard_speed = 12

        self.internal_surf_size = (2500, 2500)
        self.internal_surf = pygame.Surface(self.internal_surf_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center=(self.half_w, self.half_h))
        self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surf_size)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surf_size[0] // 2 - self.half_w
        self.internal_offset.y = self.internal_surf_size[1] // 2 - self.half_h

    def center_target_camera(self, target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def custom_draw(self, player):
        self.center_target_camera(player)
        self.internal_surf.fill('#71ddee')

        # ground
        ground_offset = self.ground_rect.topleft - self.offset + self.internal_offset
        self.internal_surf.blit(self.ground_surf, ground_offset)

        # active elements
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset + self.internal_offset
            self.internal_surf.blit(sprite.image, offset_pos)

        self.display_surface.blit(self.internal_surf, self.internal_rect)


# Função para desenhar a caixa de texto
def draw_text_box(surface, text, position, width, height):
    font = pygame.font.Font(None, 36)  # Escolha a fonte e o tamanho
    text_surf = font.render(text, True, pygame.Color('white'))
    text_rect = text_surf.get_rect(center=position)

    # Desenho da caixa de texto
    box_rect = pygame.Rect(0, 0, width, height)
    box_rect.center = position

    pygame.draw.rect(surface, pygame.Color('black'), box_rect)
    pygame.draw.rect(surface, pygame.Color('white'), box_rect, 2)  # Bordas brancas

    # Desenho do texto na caixa
    surface.blit(text_surf, text_rect)


# Setup
camera_group = CameraGroup()
player = Player((1400, 200), camera_group)

# Instanciar os NPCs
npc1 = NPC(npc1_image, (1420, 550), camera_group)
npc2 = NPC(npc2_image, (100, 550), camera_group)
npc3 = NPC(npc3_image, (1320, 1120), camera_group)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    screen.fill('#71ddee')

    # Atualiza o grupo de sprites
    camera_group.update()

    # Desenho do grupo de câmera
    camera_group.custom_draw(player)

    # Verificar proximidade com NPC1
    if player.rect.colliderect(npc1.rect):
        # Mostrar mensagem se a tecla 'E' for pressionada
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            draw_text_box(screen, "Olá, eu sou o Hellen!", (640, 650), 400, 60)

    # Verificar proximidade com NPC2
    if player.rect.colliderect(npc2.rect):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            draw_text_box(screen, "Oi, eu sou o Isac!", (640, 650), 400, 60)

    # Verificar proximidade com NPC3
    if player.rect.colliderect(npc3.rect):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            draw_text_box(screen, "Olá, eu sou o Mateus!", (640, 650), 400, 60)

    pygame.display.update()
    clock.tick(60)

