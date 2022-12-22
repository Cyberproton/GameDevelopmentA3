import time

from esper import Processor

from common.component import *
from game.component import *
from game.constant import CooldownConstant
from game.entity import create_misery_black_ball, create_red_bat
from game.misery.component import *

class MiseryTargetProcessor(Processor):
    def process(self, data):
        for ent, [pos, target, _] in self.world.get_components(Position, Target, MiseryId):
            target.target = None
            target.entity = None
            for p_ent, [p_pos, _] in self.world.get_components(Position, PlayerId):
                if p_pos.distance_squared_to(pos) > 65536:
                    continue
                target.target = p_pos.copy()
                target.entity = p_ent


class MiseryBehaviorProcessor(Processor):
    def process(self, data):
        current = time.time()
        for ent, [pos, target, vel, state, collider, drawable, anim_list, is_on_floor, floating, cooldown_dict, _, black_ball_ability, spawn_bat_ability] \
                in self.world.get_components(Position,
                                             Target,
                                             Velocity,
                                             State,
                                             Collider,
                                             Drawable,
                                             AnimationList,
                                             IsOnFloor,
                                             Floating,
                                             CooldownDict,
                                             MiseryId,
                                             BlackBallAbility,
                                             SpawnBatAbility):

            if target.target is None:
                state.set_current_state('idle')
            elif state.current == 'idle':
                if floating.position is None:
                    floating.position = pos.copy()
                origin = floating.position
                if floating.direction == Floating.DIRECTION_UP:
                    expected = origin.y - floating.max_offset
                    if abs(expected - pos.y) < 5:
                        floating.direction = Floating.DIRECTION_DOWN
                        vel.y = EntityConstant.Misery.FLOAT_VELOCITY
                    else:
                        vel.y = -EntityConstant.Misery.FLOAT_VELOCITY
                else:
                    expected = origin.y + floating.max_offset
                    if abs(expected - pos.y) < 5:
                        floating.direction = Floating.DIRECTION_UP
                        vel.y = -EntityConstant.Misery.FLOAT_VELOCITY
                    else:
                        vel.y = EntityConstant.Misery.FLOAT_VELOCITY
                if abs(expected - pos.y) < 5:
                    if cooldown_dict.has_cooldown_expired(CooldownConstant.MISERY_TELEPORT):
                        state.set_current_state('teleport')
                        floating.reset()
                    elif cooldown_dict.has_cooldown_expired(CooldownConstant.MISERY_BLACK_BALL):
                        state.set_current_state('attack')
                        floating.reset()
            elif state.current == 'teleport':
                teleport = self.world.try_component(ent, Teleport)
                vel.x, vel.y = 0, 0
                if teleport is None:
                    anim_list.set_current_animation('teleport')
                    self.world.add_component(ent, Teleport(ent, 2))
                    collider.enable = False
                elif current > teleport.end:
                    pos.x, pos.y = target.target.x, target.target.y - 32
                    anim_list.set_current_animation('attack')
                    state.set_current_state('summon_bat')
                    self.world.remove_component(ent, Teleport)
                    collider.enable = True
                    drawable.hide = False
                elif current > teleport.end - 1:
                    drawable.hide = True
            elif state.current == 'summon_bat':
                if cooldown_dict.has_cooldown_expired(CooldownConstant.MISERY_PER_BAT):
                    create_red_bat(self.world, pos)
                    cooldown_dict.add_cooldown_duration(CooldownConstant.MISERY_PER_BAT,
                                                        CooldownConstant.MISERY_PER_BAT_COOLDOWN)
                    spawn_bat_ability.time += 1
                if spawn_bat_ability.time >= spawn_bat_ability.times:
                    state.set_current_state('idle')
                    anim_list.set_current_animation('idle')
                    cooldown_dict.add_cooldown_duration(CooldownConstant.MISERY_TELEPORT,
                                                        CooldownConstant.MISERY_TELEPORT_COOLDOWN)
                    spawn_bat_ability.reset()
            elif state.current == 'attack':
                vel.x, vel.y = (0, 0)
                anim_list.set_current_animation('attack')
                if cooldown_dict.has_cooldown_expired(CooldownConstant.MISERY_PER_BLACK_BALL):
                    ball_vel = (target.target - pos).normalize()
                    create_misery_black_ball(self.world, pos, ball_vel)
                    cooldown_dict.add_cooldown_duration(CooldownConstant.MISERY_PER_BLACK_BALL, CooldownConstant.MISERY_PER_BLACK_BALL_COOLDOWN)
                    black_ball_ability.time += 1
                if black_ball_ability.time >= black_ball_ability.times:
                    state.set_current_state('idle')
                    anim_list.set_current_animation('idle')
                    cooldown_dict.add_cooldown_duration(CooldownConstant.MISERY_BLACK_BALL, CooldownConstant.MISERY_BLACK_BALL_COOLDOWN)
                    black_ball_ability.reset()
