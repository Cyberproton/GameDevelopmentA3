import pygame.mixer


class GameData:
    def __init__(self, scene, screen, canvas, world, player_id, camera_pos=(0, 0)):
        self.screen = screen
        self.canvas = canvas
        self.world = world,
        self.player = player_id
        self.player_pos = None
        self.delta = None
        self.camera_pos = camera_pos
        self.debug = False
        self.resource = GameResource()
        self.pause = False
        self.scene = scene
        self.reset = True


class GameResource:
    def __init__(self):
        chest_break = pygame.mixer.Sound('./assets/sound/chest_break.ogg')
        chest_break.set_volume(0.2)
        player_run = pygame.mixer.Sound('./assets/sound/player_walk.ogg')
        player_run.set_volume(5.0)
        self.sound = {
            'attack': pygame.mixer.Sound('./assets/sound/ID17_snd_thud.wav'),
            'player_run': pygame.mixer.Sound('./assets/sound/ID18_snd_quote_walk.wav'),
            'player_step_1': pygame.mixer.Sound('./assets/sound/player_step_1.wav'),
            'player_step_2': pygame.mixer.Sound('./assets/sound/player_step_2.wav'),
            'player_pickup': pygame.mixer.Sound('./assets/sound/player_pickup.wav'),
            'chest_break': chest_break,
            'health': pygame.mixer.Sound('./assets/sound/ID14_snd_health_refill.wav'),
            'missile': pygame.mixer.Sound('./assets/sound/ID0e_snd_get_xp.wav'),
        }


def fill_keep_alpha(surface, color):
    """Fill all pixels of the surface with color, preserve transparency."""
    new_surface = surface.copy()
    w, h = new_surface.get_size()
    r, g, b = color
    for x in range(w):
        for y in range(h):
            a = new_surface.get_at((x, y))[3]
            new_surface.set_at((x, y), pygame.Color(r, g, b, a))
    return new_surface
