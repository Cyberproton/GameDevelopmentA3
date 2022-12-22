from esper import Processor

from common.component import *
from game.component import *


class CritterTargetProcessor(Processor):
    def process(self, *args, **kwargs):
        for ent, [target, _, pos] in self.world.get_components(Target, CritterId, Position):
            for p_ent, [p_pos, _] in self.world.get_components(Position, PlayerId):
                if p_pos.distance_squared_to(pos) > 147456:
                    continue
                target.target = p_pos.copy()
                target.entity = p_ent


class CritterNavigationSystem(Processor):
    def process(self, *args, **kwargs):
        for ent, [pos, target, vel, state, anim_list, is_on_floor, _] in self.world.get_components(Position, Target,
                                                                                                Velocity, State,
                                                                                                AnimationList,
                                                                                                IsOnFloor,
                                                                                                CritterId):
            if target.target is None:
                continue
            if state.current == 'idle':
                state.set_current_state('jump')
                anim_list.set_current_animation('jump')
                target.dest = pos.copy() + (0, -32)
            elif state.current == 'jump':
                if pos.distance_to(target.dest) < 2 or is_on_floor.ceiling:
                    state.set_current_state('fly')
                    anim_list.set_current_animation('fly')
                    self.world.remove_component(ent, Gravity)
                    y = -50
                    target.dest = target.target.copy() + (0, y)
                else:
                    direction = target.dest - pos
                    vel.x, vel.y = direction.x * 0.1, direction.y * 0.1
            elif state.current == 'fly':
                if pos.distance_to(target.dest) < 2 or (
                        is_on_floor.ground or is_on_floor.ceiling):
                    state.set_current_state('fall')
                    anim_list.set_current_animation('fall')
                    self.world.add_component(ent, Gravity())
                    vel.x, vel.y = 0, 0
                else:
                    direction = (target.dest - pos).normalize()
                    vel.x, vel.y = direction.x * 1, direction.y * 1
            elif state.current == 'fall':
                if is_on_floor.ground:
                    state.set_current_state('idle')
                    anim_list.set_current_animation('idle')
