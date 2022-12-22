class TileMapConstant:
    TILE_SIZE = 16


class GameConstant:
    WIDTH = 1280
    HEIGHT = 720
    WIDTH_HEIGHT = (WIDTH, HEIGHT)
    SCALE = 4
    VIEW_WIDTH = WIDTH / SCALE
    VIEW_HEIGHT = HEIGHT / SCALE
    VIEW_WIDTH_HEIGHT = (VIEW_WIDTH, VIEW_HEIGHT)
    CAMERA_SPEED = 0.05


class PhysicsConstant:
    MAX_ACCELERATION = 3
    GRAVITY = 0.2


class EffectConstant:
    EFFECT_WEAR_OFF_BLINK = 3
    BLINK_INTERVAL = 0.2
    SHAKE_INTERVAL = 0.1
    SHAKE_OFFSET = 3
    SHIELD_DURATION = 10
    SHIELD_DAMAGE_REDUCTION = 0.8
    INVINCIBLE_DURATION = 3


class PlayerConstant:
    WEAPON_OFFSET_X = 11
    WEAPON_OFFSET_Y = 9


class EntityConstant:
    class Misery:
        MAX_FLOATING_OFFSET = 16
        FLOAT_VELOCITY = 0.6
        BLACK_BALL_ABILITY_TIMES = 5
        SPAWN_BAT_ABILITY_TIMES = 5

    class Bullet:
        class Type:
            NORMAL = 'normal'
            BIG = 'big'

    class Heart:
        HEAL = 100


class CooldownConstant:
    PLAYER_RUN = 'player_run'
    PLAYER_RUN_COOLDOWN = 0.3
    PLAYER_ATTACK = 'player_attack'
    PLAYER_ATTACK_COOLDOWN = 0.1

    MISERY_BLACK_BALL = 'misery_black_ball'
    MISERY_BLACK_BALL_COOLDOWN = 5
    MISERY_PER_BLACK_BALL = 'misery_per_black_ball'
    MISERY_PER_BLACK_BALL_COOLDOWN = 0.3

    MISERY_TELEPORT = 'misery_teleport'
    MISERY_TELEPORT_COOLDOWN = 7
    MISERY_PER_BAT = 'misery_per_bat'
    MISERY_PER_BAT_COOLDOWN = 0.3
