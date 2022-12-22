import time

from game.component import Effect
from game.constant import EntityConstant


class Floating:
    DIRECTION_UP = 'up'
    DIRECTION_DOWN = 'down'

    def __init__(self, position=None, max_offset=EntityConstant.Misery.MAX_FLOATING_OFFSET):
        self.position = position
        self.current = position
        self.max_offset = max_offset
        self.direction = Floating.DIRECTION_UP

    def reset(self):
        self.position = None
        self.current = None
        self.direction = Floating.DIRECTION_UP


class BlackBallAbility:
    def __init__(self, times=EntityConstant.Misery.BLACK_BALL_ABILITY_TIMES):
        self.times = times
        self.time = 0

    def reset(self):
        self.time = 0


class SpawnBatAbility:
    def __init__(self, times=EntityConstant.Misery.BLACK_BALL_ABILITY_TIMES):
        self.times = times
        self.time = 0

    def reset(self):
        self.time = 0


class Teleport(Effect):
    pass
