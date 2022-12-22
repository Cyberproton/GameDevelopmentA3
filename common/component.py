import json
import time
from dataclasses import dataclass
from typing import Optional

import pygame.image
from pygame import Vector2, Surface

from game.constant import EffectConstant


class Position(Vector2):
    @staticmethod
    def create(pos):
        if type(pos) is Position:
            return pos.copy()
        return Position(pos[0], pos[1])


class Velocity(Vector2):
    def reset(self):
        self.x = 0
        self.y = 0


@dataclass
class Acceleration(Vector2):
    def reset(self):
        self.x = 0
        self.y = 0


@dataclass
class Direction(Vector2):
    def __init__(self):
        super().__init__()
        self.x = 1


class Collider(pygame.Rect):
    pass


class Collision:
    def __init__(self):
        self.to = []


class CollisionMask:
    def __init__(self, mask=None):
        if mask is None:
            mask = set()
        self.mask = set(mask)

    @staticmethod
    def of(*args):
        return CollisionMask(mask=args)

    def intersection(self, other):
        return self.mask.intersection(other.mask)


class Gravity:
    pass


class AirTimer:
    def __init__(self):
        self.frames = 0


class State:
    def __init__(self, on_state_change_handler=None):
        self.current = 'idle'
        self.prev = None
        self.on_state_change_handler = on_state_change_handler
        self.check = True

    def set_current_state(self, name):
        if self.current == name:
            return
        self.prev = self.current
        self.current = name
        self.check = False



@dataclass
class Drawable:
    def __init__(self, drawable=None, offset: tuple[float, float] = (0, 0), flip=False):
        self.drawable = drawable
        self.flip = flip
        self.hide = False
        self.offset_x = offset[0]
        self.offset_y = offset[1]
        self.custom_offset_x = 0
        self.custom_offset_y = 0


class FlipByVelocity:
    pass


class Sprite:
    def __init__(self, surface: Surface, rect: (float, float, float, float) = (0, 0, 0, 0),
                 offset: (float, float) = (0, 0), step=-1):
        self.surface = surface
        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2]
        self.h = rect[3]
        self.offset_x = offset[0]
        self.offset_y = offset[1]
        self.step = step


class Animation:
    def __init__(self, name: str, sprites: list[Sprite], step: float = 0.15, offset: Vector2 = Vector2(), loop=True,
                 flip=False,
                 scale=1):
        self.name = name
        self.sprites = sprites
        self.index = 0
        self.max_index = len(sprites) - 1
        self.total_frames = len(sprites)
        self.step = step
        self.offset = offset
        self.loop = loop
        self.flip = flip
        self.scale = scale

    def get_current_sprite(self) -> Optional[Sprite]:
        return self.sprites[int(self.index)]

    def is_last_sprite(self):
        return int(self.index) >= self.max_index

    def is_last_step(self):
        return self.index + self.step >= self.max_index

    def reset(self):
        self.index = 0

    @staticmethod
    def load(animation_path):
        with open(f'{animation_path}/animation.json') as metadata_file:
            metadata = json.load(metadata_file)
        metadata_file.close()
        animation_name = animation_path.split("/")[-1]
        count = metadata["count"]
        loop = metadata.get('loop', True)
        sprites = []
        flip = metadata.get("flip", False)
        step = metadata.get('step', 0.15)
        for i in range(0, count):
            path = f'{animation_path}/{i}.png'
            image = pygame.image.load(path).convert()
            image.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
            sprites.append(Sprite(image))
        return Animation(animation_name, sprites, loop=loop, flip=flip, step=step)


class AnimationList:
    def __init__(self, animations):
        self.animations = animations
        self.current_animation = None

    def get_current_animation(self) -> Optional[Animation]:
        if not self.current_animation or self.current_animation not in self.animations.keys():
            return None
        return self.animations[self.current_animation]

    def set_current_animation_from_list(self, names):
        for name in names:
            if name == self.current_animation:
                return
            if name not in self.animations.key():
                continue
            if self.current_animation is not None:
                current = self.get_current_animation()
                current.reset()
            self.current_animation = name
            return

    def set_current_animation(self, name):
        if name == self.current_animation:
            return
        if name not in self.animations.keys():
            return
        if self.current_animation is not None:
            current = self.get_current_animation()
            current.reset()
        self.current_animation = name

    def get_animation(self, name) -> Optional[Animation]:
        return self.animations[name]

    @staticmethod
    def load(path, initial_state=None):
        with open(f'{path}/animation_list.json') as metadata_file:
            metadata = json.load(metadata_file)
        metadata_file.close()
        animations = {}
        for (animation_name, _) in metadata.items():
            animation = Animation.load(f'{path}/{animation_name}')
            animations[animation_name] = animation
        anim_list = AnimationList(animations)
        if initial_state:
            anim_list.set_current_animation(initial_state)
        return anim_list

    @staticmethod
    def load_single(path, initial_state='default', default_animation_name='default'):
        animation = Animation.load(path)
        animations = {default_animation_name: animation}
        anim_list = AnimationList(animations)
        if initial_state:
            anim_list.set_current_animation(initial_state)
        return anim_list

    def __str__(self):
        return '{animations=' + str(self.animations) + ',current_animation=' + str(self.current_animation) + '}'


@dataclass
class Controllable:
    MOVE_LEFT = 'MOVE_LEFT'
    MOVE_RIGHT = 'MOVE_RIGHT'
    MOVE_UP = 'MOVE_UP'
    MOVE_DOWN = 'MOVE_DOWN'
    ATTACK = "ATTACK"
    JUMP = "JUMP"
    PAUSE = "PAUSE"

    def __init__(self, key_bindings=None):
        self.key_bindings = key_bindings


class TileMap:
    def __init__(self, tilemap, tiles):
        self.tilemap = tilemap
        self.tiles = tiles

    @staticmethod
    def load(map_path):
        with open(f'{map_path}/map.json') as metadata_file:
            metadata = json.load(metadata_file)
        metadata_file.close()
        tilemap = metadata.get('map')
        tiles = {}

        for row in tilemap:
            for col in row:
                tiles[col] = None

        for key in tiles.keys():
            if key == '0':
                continue
            path = f'{map_path}/tile/{key}.png'
            image = pygame.image.load(path).convert()
            image.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
            tiles[key] = image

        return TileMap(tilemap, tiles)


class LifeTime:
    def __init__(self, duration, start=None):
        self.duration = duration
        if start is None:
            self.start = time.time()
        else:
            self.start = start
        self.end = self.start + duration


class IsAlive:
    def __init__(self, value=True):
        self.value = value


class Blink:
    def __init__(self, duration, interval=EffectConstant.BLINK_INTERVAL):
        self.start = time.time()
        self.duration = duration
        self.end = self.start + self.duration
        self.latest_blink = None
        self.interval = interval


class Shake:
    STATE_LEFT = 'left'
    STATE_NORMAL = 'normal'
    STATE_RIGHT = 'right'

    def __init__(self, duration, times=None, interval=EffectConstant.SHAKE_INTERVAL):
        self.start = time.time()
        self.duration = duration
        self.times = times
        self.run = 0
        self.state = None
        self.latest_blink = None
        self.interval = interval

    def get_end(self):
        return self.start + self.duration

    end = property(fget=get_end)


class ShakeLimit:
    def __init__(self, offset_x):
        self.offset_x = offset_x


class Cooldown:
    def __init__(self, cooldown_type: str, duration: float, start: float = None):
        self.cooldown_type = cooldown_type
        if start is None:
            start = time.time()
        self.start = start
        self.end = start + duration
        self.duration = duration

    def has_expired(self) -> bool:
        return time.time() > self.end

    def add_duration(self, duration: float):
        return Cooldown(self.cooldown_type, self.duration + duration, self.start)


class CooldownDict:
    def __init__(self):
        self.cooldown = {}

    def get_cooldown(self, cooldown_type: str) -> Optional[Cooldown]:
        if cooldown_type not in self.cooldown:
            return None
        return self.cooldown[cooldown_type]

    def has_cooldown_expired(self, cooldown_type: str) -> bool:
        if cooldown_type not in self.cooldown:
            return True
        return self.cooldown[cooldown_type].has_expired()

    def add_cooldown_duration(self, cooldown_type: str, duration: float):
        if cooldown_type in self.cooldown and not self.cooldown[cooldown_type].has_expired():
            cooldown = self.cooldown[cooldown_type].add_duration(duration)
        else:
            cooldown = Cooldown(cooldown_type, duration, time.time())
        self.cooldown[cooldown_type] = cooldown

    def add_cooldown(self, cooldown: Cooldown):
        cooldown_type = cooldown.cooldown_type
        duration = cooldown.duration
        if cooldown_type in self.cooldown and not self.cooldown[cooldown_type].has_expired():
            cooldown = self.cooldown[cooldown_type].add_duration(duration)
        else:
            cooldown = Cooldown(cooldown_type, duration, time.time())
        self.cooldown[cooldown_type] = cooldown

    def remove_cooldown(self, cooldown: Cooldown):
        if cooldown.cooldown_type not in self.cooldown:
            return
        self.cooldown.pop(cooldown.cooldown_type)

    def remove_expired_cooldowns(self):
        for value in list(self.cooldown.values()):
            if value.has_expired():
                self.cooldown.pop(value.cooldown_type)


class Owner:
    def __init__(self, owner_id):
        self.owner = owner_id


class Target:
    def __init__(self, target=None):
        self.entity = None
        self.target = target
        self.dest = None


class IsOnFloor:
    def __init__(self):
        self.ground = True
        self.ceiling = True
