from enum import Enum

import pygame

import game
from common.component import *
from game.component import Metadata, PlayerId, Health, GunId, BulletStorage, MiseryId, BulletTarget, AttackDamage, \
    BulletId, CritterId, BatId, ChestId, MissileId, HeartId, Effect, ShieldEffect, ShieldId, DamageStack
from game.constant import *
from game.misery.component import Floating, BlackBallAbility, SpawnBatAbility


class EntityType(Enum):
    CRITTER = "CRITTER"
    PLAYER = "PLAYER"
    OBSTACLE = "OBSTACLE"
    BULLET = "BULLET"
    BAT = 'BAT'


def create_tilemap(world):
    tilemap = TileMap.load('./assets/map')
    _map = tilemap.tilemap
    tiles = tilemap.tiles
    map_height = len(_map)
    for i in range(0, map_height):
        row = _map[i]
        row_length = len(row)
        for j in range(0, row_length):
            tile_name = row[j]
            image = tiles[tile_name]
            if image is None:
                continue

            upper = _map[i - 1] if i > 0 else None
            top = '0'
            if upper is not None:
                top = upper[j] if -1 < j < len(upper) else '0'
            below = _map[i + 1] if i < map_height - 1 else None
            bottom = '0'
            if below is not None:
                bottom = below[j] if -1 < j < len(below) else '0'

            left = row[j - 1] if j > 0 else '0'
            right = row[j + 1] if j < row_length - 1 else '0'

            tile = world.create_entity(
                game.component.ObstacleId(),
                Metadata(EntityType.OBSTACLE),
                Position(j * TileMapConstant.TILE_SIZE, i * TileMapConstant.TILE_SIZE),
                Drawable(drawable=image),
            )
            if top == '0' or bottom == '0' or left == '0' or right == '0':
                world.add_component(tile, Collider((0, 0, TileMapConstant.TILE_SIZE, TileMapConstant.TILE_SIZE)))
                world.add_component(tile, CollisionMask.of(0, 1))


def create_player(world, pos):
    anim_list = AnimationList.load("./assets/entity/quote")
    anim_list.current_animation = "idle"
    collider = Collider((0, 0, 16, 16))
    collider.dynamic = True
    player = (
        PlayerId(),
        Position(pos),
        Velocity(),
        Acceleration(),
        Direction(),
        Gravity(),
        Drawable(),
        Controllable({
            Controllable.MOVE_UP: pygame.K_w,
            Controllable.MOVE_DOWN: pygame.K_s,
            Controllable.MOVE_LEFT: pygame.K_a,
            Controllable.MOVE_RIGHT: pygame.K_d,
            Controllable.ATTACK: pygame.K_f,
            Controllable.JUMP: pygame.K_SPACE,
            Controllable.PAUSE: pygame.K_p,
        }),
        Metadata(EntityType.PLAYER),
        collider,
        CollisionMask.of(0),
        anim_list,
        CooldownDict(),
        IsAlive(),
        Health(1000, 1000),
        BulletStorage(),
        DamageStack(),
        IsOnFloor(),
    )
    player = world.create_entity(*player)
    gun = world.create_entity(
        GunId(),
        Position(),
        Direction(),
        Drawable(pygame.image.load('./assets/entity/gun/left/0.png')),
        Owner(player),
    )
    world.create_entity(gun)
    return player


def create_misery(world, pos):
    misery = world.create_entity(
        MiseryId(),
        Position(pos),
        Velocity(),
        Drawable(),
        AnimationList.load('./assets/entity/misery', 'idle'),
        Target(),
        State(),
        IsOnFloor(),
        Floating(),
        CooldownDict(),
        BlackBallAbility(),
        SpawnBatAbility(),
        Health(1000),
        IsAlive(),
        Collider(0, 0, 16, 16),
        DamageStack(),
        ShakeLimit(1),
    )
    return misery


def create_misery_black_ball(world, position, velocity):
    col = Collider((0, 0, 16, 16))
    col.dynamic = True
    return world.create_entity(
        game.component.BulletId(),
        Metadata(EntityType.BULLET),
        Position(position[0], position[1]),
        Velocity(velocity[0], velocity[1]),
        Drawable(),
        AnimationList.load('./assets/entity/misery_black_ball', 'idle'),
        col,
        LifeTime(5),
        IsAlive(),
        BulletTarget([PlayerId]),
        AttackDamage(10),
    )


def create_red_bat(world, position):
    col = Collider((0, 0, 16, 16))
    bat = world.create_entity(
        BatId(),
        Metadata(EntityType.BAT),
        Position(position[0], position[1]),
        Velocity(),
        Drawable(),
        AnimationList.load('./assets/entity/red_bat', 'fly'),
        col,
        LifeTime(60),
        Health(10),
        IsAlive(),
        IsOnFloor(),
        AttackDamage(10),
        Target(),
        FlipByVelocity(),
        DamageStack(),
    )
    return bat


def create_bullet(world, position, velocity, collider=(0, 0, 15, 8), drawable=Drawable(pygame.image.load('./assets/entity/bullet/0.png')),
                  damage=100):
    col = Collider(collider)
    col.dynamic = True
    return world.create_entity(
        BulletId(),
        Metadata(EntityType.BULLET),
        Position(position[0], position[1]),
        Velocity(velocity[0], velocity[1]),
        drawable,
        FlipByVelocity(),
        col,
        LifeTime(2),
        IsAlive(),
        BulletTarget([CritterId, BatId, ChestId, MiseryId]),
        AttackDamage(damage) if type(damage) is int else damage,
    )


class BulletFactory:
    @staticmethod
    def create(world, bullet_type, position, velocity):
        if bullet_type == EntityConstant.Bullet.Type.BIG:
            create_bullet(
                world,
                position,
                velocity,
                (0, 0, 15, 8),
                Drawable(pygame.image.load('./assets/entity/bullet/1.png')),
                AttackDamage(100),
            )
        else:
            create_bullet(
                world,
                position,
                velocity,
                (0, 0, 15, 8),
                Drawable(pygame.image.load('./assets/entity/bullet/0.png')),
                AttackDamage(40),
            )


def create_critter(world, pos):
    col = Collider((0, 0, 25, 25))
    col.dynamic = True
    return world.create_entity(
        CritterId(),
        Metadata(EntityType.CRITTER),
        Position.create(pos),
        Velocity(),
        Health(1000),
        DamageStack(),
        IsAlive(),
        IsOnFloor(),
        Gravity(),
        Drawable(),
        col,
        CollisionMask([1]),
        AnimationList.load("./assets/entity/critter", 'idle'),
        Target(),
        State(),
    )


def create_heart(world, pos):
    return world.create_entity(
        HeartId(),
        Position(int(pos[0]), int(pos[1])),
        Drawable(),
        AnimationList.load_single('./assets/entity/heart'),
        Collider(-4, -4, 16, 16),
        IsAlive(),
    )


def create_missile(world, pos):
    return world.create_entity(
        MissileId(),
        Position(pos),
        Drawable(),
        AnimationList.load_single('./assets/entity/missile'),
        Collider(0, 0, 14, 12),
        IsAlive(),
    )


def create_shield(world, pos, owner):
    return world.create_entity(
        ShieldId(),
        Position(pos),
        Owner(owner),
        Drawable(pygame.image.load('./assets/entity/shield/0.png')),
        Collider(0, 0, 22, 22),
    )


def create_chest(world, pos):
    return world.create_entity(
        ChestId(),
        Position(pos),
        Drawable(drawable=pygame.image.load('./assets/entity/chest/0.png')),
        Collider(0, 0, 16, 16),
        CollisionMask([0, 1]),
        IsAlive(),
        Health(200),
        ShakeLimit(1),
        DamageStack(),
    )

