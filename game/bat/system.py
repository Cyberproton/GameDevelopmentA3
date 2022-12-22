import random

from esper import Processor

from common.component import *
from game.component import *
from game.util import clamp, clamp_abs


class BatTargetProcessor(Processor):
    def process(self, *args, **kwargs):
        for ent, [target, _] in self.world.get_components(Target, BatId):
            for p_ent, [p_pos, _] in self.world.get_components(Position, PlayerId):
                target.target = p_pos.copy()
                target.entity = p_ent


class BatBehaviorProcessor(Processor):
    def process(self, *args, **kwargs):
        for ent, [pos, target, vel, is_on_floor, _] in self.world.get_components(Position,
                                                                                 Target,
                                                                                 Velocity,
                                                                                 IsOnFloor,
                                                                                 BatId):
            if target.target is None:
                continue
            if target.dest is None or pos.distance_to(target.dest) < 5:
                target.dest = target.target + (random.uniform(-10, 10), random.uniform(-10, 10))

            direction = target.dest - pos
            vel.x, vel.y = clamp_abs(direction.x, 0.2, 1), clamp_abs(direction.y, 0.2, 1)
