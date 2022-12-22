import pygame.font
import pygame_gui
from esper import World

import common.event_handler
import game.event_handler
from common.util import *
from common.system import *
from game.bat.system import BatBehaviorProcessor, BatTargetProcessor
from game.critter.system import *
from game.entity import *
from game.misery.system import MiseryBehaviorProcessor, MiseryTargetProcessor
from game.player.system import PlayerAnimationProcessor, PlayerPositionSaverProcessor
from game.system import *

pygame.init()
clock = pygame.time.Clock()
pygame.display.set_icon(pygame.image.load('./assets/game/icon.png'))
pygame.display.set_caption("Assignment 3")
SCREEN_WIDTH = GameConstant.WIDTH
SCREEN_HEIGHT = GameConstant.HEIGHT
GAME_SCALE = GameConstant.SCALE
VIEW_WIDTH = GameConstant.VIEW_WIDTH
VIEW_HEIGHT = GameConstant.VIEW_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
canvas = pygame.Surface((SCREEN_WIDTH / GAME_SCALE, SCREEN_HEIGHT / GAME_SCALE))
framerate = 60
last_time = time.time()

common.event_handler.register_all_event_handlers()
game.event_handler.register_all_event_handlers()

mm_font = pygame.font.Font('./assets/gui/font/upheavtt.ttf', 72)
mm_font_small = pygame.font.Font('./assets/gui/font/upheavtt.ttf', 48)

gui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), './assets/gui/theme/theme.json')

start_rect = pygame.Rect(30, 20, 300, 100)
start_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 70)

credit_rect = pygame.Rect(30, 100, 300, 100)
credit_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30)

start_button = pygame_gui.elements.UIButton(relative_rect=start_rect,
                             text='Start', manager=gui_manager)

credit_button = pygame_gui.elements.UIButton(relative_rect=credit_rect,
                             text='Credit', manager=gui_manager)


ingame_gui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), './assets/gui/theme/theme.json')
health_bar = pygame_gui.elements.UIProgressBar(pygame.Rect(10, 10, 100, 10), manager=ingame_gui_manager)

credit_gui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_WIDTH), './assets/gui/theme/credit_theme.json')
credit_back_to_main = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(150, 500, 1000, 100), text='Back to Menu', manager=credit_gui_manager)
credit = pygame_gui.elements.UILabel(pygame.Rect(150, 100, 1000, 100), manager=credit_gui_manager, text='Base on Cave Story')
credit_me = pygame_gui.elements.UILabel(pygame.Rect(30, 300, 1280, 100), manager=credit_gui_manager, text='@Cyberproton - Assignment 3')

gameover_gui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_WIDTH), './assets/gui/theme/credit_theme.json')
gameover_back_to_main = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(150, 500, 1000, 100), text='Back to Menu', manager=gameover_gui_manager)
gameover = pygame_gui.elements.UILabel(pygame.Rect(150, 300, 1000, 100), manager=gameover_gui_manager, text='Game Over')

pygame.mixer.music.load('assets/music/background.ogg')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)

game_data = GameData('main_menu', screen, canvas, None, None, (380, 140))


def setup_world():
    global game_data

    world = World()
    game_data.world = world

    create_tilemap(world)

    player = create_player(world, (380, 140))
    #player = create_player(world, (1300, 140))
    game_data.player = player

    create_critter(world, (420, 140))
    create_misery(world, (1280, 200))
    create_critter(world, (1200, 200))
    create_chest(world, (720, 213))
    create_chest(world, (1060, 213))

    world.add_processor(PlayerPositionSaverProcessor())
    world.add_processor(CameraProcessor())

    world.add_processor(PlayerInputProcessor())
    world.add_processor(PlayerAnimationProcessor())
    world.add_processor(GravitySystem())
    world.add_processor(AreaProcessor())
    world.add_processor(MovementProcessor())
    world.add_processor(GunPositionProcessor())
    world.add_processor(ShieldPositionProcessor())
    world.add_processor(CollisionProcessor())
    world.add_processor(AnimationStateProcessor())
    world.add_processor(AnimationProcessor())
    world.add_processor(BlinkProcessor())
    world.add_processor(ShakeProcessor())
    world.add_processor(RendererProcessor())
    world.add_processor(CooldownDictProcessor())
    world.add_processor(FlipByVelocityProcessor())
    world.add_processor(StateProcessor())
    world.add_processor(ShieldEffectProcessor())
    world.add_processor(BulletPowerupEffectProcessor())
    world.add_processor(InvincibleEffectProcessor())
    world.add_processor(DamageStackProcessor())
    world.add_processor(HealthProcessor())
    world.add_processor(LifeProcessor())

    world.add_processor(CritterTargetProcessor())
    world.add_processor(CritterNavigationSystem())

    world.add_processor(MiseryTargetProcessor())
    world.add_processor(MiseryBehaviorProcessor())

    world.add_processor(BatTargetProcessor())
    world.add_processor(BatBehaviorProcessor())


def main_menu(game_data, events):
    start_button.show()
    credit_button.show()

    canvas.fill((0, 0, 0))

    icon = pygame.image.load('./assets/game/icon.png')
    icon_rect = icon.get_rect(center=(VIEW_WIDTH / 2, VIEW_HEIGHT / 5))
    canvas.blit(icon, icon_rect)

    scaled_canvas = pygame.transform.scale(canvas, screen.get_size())
    screen.blit(scaled_canvas, (0, 0))

    text = mm_font_small.render("@Cyberproton - Assignment 3", False, (255, 255, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 160))
    screen.blit(text, text_rect)

    for event in events:
        gui_manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == start_button:
                game_data.scene = 'game'
                start_button.hide()
                credit_button.hide()
            if event.ui_element == credit_button:
                game_data.scene = 'credit'
                start_button.hide()
                credit_button.hide()

    gui_manager.update(game_data.delta)
    gui_manager.draw_ui(screen)


def credit_menu(game_data, events):
    screen.fill((0, 0, 0))

    for event in events:
        credit_gui_manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == credit_back_to_main:
                game_data.scene = 'main_menu'

    credit_gui_manager.update(game_data.delta)
    credit_gui_manager.draw_ui(screen)


def gameover_menu(game_data, events):
    screen.fill((0, 0, 0))

    for event in events:
        gameover_gui_manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == gameover_back_to_main:
                game_data.scene = 'main_menu'

    gameover_gui_manager.update(game_data.delta)
    gameover_gui_manager.draw_ui(screen)


def game(game_data):
    world = game_data.world
    player = game_data.player
    game_data.delta = delta

    key_pressed = pygame.key.get_pressed()
    if key_pressed[pygame.K_p]:
        game_data.pause = not game_data.pause

    if game_data.pause:
        return

    canvas.fill((6, 10, 33))

    world.process(game_data)

    health = world.try_component(player, Health)
    health_percentage = max(health.value, 0) / health.max_value
    health_bar.set_current_progress(health_percentage)
    ingame_gui_manager.update(delta)
    ingame_gui_manager.draw_ui(canvas)

    scaled_canvas = pygame.transform.scale(canvas, screen.get_size())

    screen.blit(scaled_canvas, (0, 0))


while True:
    if game_data.reset:
        setup_world()
        game_data.reset = False

    delta = clock.tick(framerate) / 1000.0
    game_data.delta = delta

    events = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        events.append(event)

    if game_data.scene == 'main_menu':
        main_menu(game_data, events)
    elif game_data.scene == 'credit':
        credit_menu(game_data, events)
    elif game_data.scene == 'gameover':
        gameover_menu(game_data, events)
    else:
        game(game_data)

    gui_manager.update(delta)
    gui_manager.draw_ui(screen)
    pygame.display.update()
