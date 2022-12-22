from esper import Processor

from common.component import Position, Velocity, AnimationList, IsOnFloor
from game.component import PlayerId


class PlayerPositionSaverProcessor(Processor):
    def process(self, data):
        for ent, (_, pos) in self.world.get_components(PlayerId, Position):
            data.player_pos = pos


class PlayerAnimationProcessor(Processor):
    def process(self, data):
        for ent, (_, pos, vel, anim_list, is_on_floor) in self.world.get_components(PlayerId, Position, Velocity, AnimationList, IsOnFloor):
            if is_on_floor.ground:
                if vel.x == 0:
                    anim_list.set_current_animation('idle')
                else:
                    anim_list.set_current_animation('run')
            else:
                anim_list.set_current_animation('jump')
