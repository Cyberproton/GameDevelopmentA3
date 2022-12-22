import random
from math import ceil

import pygame.draw
from esper import Processor
from pygame import Rect

from common.event import *
from game.entity import *
from game.particle.entity import create_gun_particle
from game.util import *


class LifeProcessor(Processor):
    def process(self, data):
        current = time.time()
        for ent, [life_time] in self.world.get_components(LifeTime):
            if life_time.end < current:
                self.world.delete_entity(ent)
                if self.world.has_component(ent, PlayerId):
                    data.reset = True
                    data.scene = 'gameover'
                if self.world.has_component(ent, MiseryId):
                    data.reset = True
                    data.scene = 'gameover'
                EntityDeathEvent(self.world, data, ent).dispatch()
        for ent, [alive] in self.world.get_components(IsAlive):
            if alive.value:
                continue
            self.world.delete_entity(ent)
            if self.world.has_component(ent, PlayerId):
                data.reset = True
                data.scene = 'gameover'
            if self.world.has_component(ent, MiseryId):
                data.reset = True
                data.scene = 'gameover'
            for child, [owner] in self.world.get_components(Owner):
                if owner.owner == ent:
                    self.world.delete_entity(child)
            EntityDeathEvent(self.world, data, ent).dispatch()


class MovementProcessor(Processor):
    def process(self, data):
        for ent, (pos, vel) in self.world.get_components(Position, Velocity):
            collider = self.world.try_component(ent, Collider)
            f_mask = self.world.try_component(ent, CollisionMask)
            pos.x += vel.x

            area_events = {}
            collision_events = {}

            if collider:
                for ent2, (pos2, collider2) in self.world.get_components(Position, Collider):
                    if ent == ent2:
                        continue
                    if hasattr(collider2, 'enable') and not collider2.enable:
                        continue
                    s_mask = self.world.try_component(ent2, CollisionMask)
                    col1 = pygame.Rect((pos.x + collider.x, pos.y + collider.y, collider.w, collider.h))
                    col2 = pygame.Rect((pos2.x + collider2.x, pos2.y + collider2.y, collider2.w, collider2.h))
                    if col1.colliderect(col2):
                        event = AreaEvent(self.world, data, ent, ent2)
                        area_events[ent2] = event
                    if f_mask is None or s_mask is None or len(f_mask.intersection(s_mask)) < 1:
                        continue
                    if col1.colliderect(col2):
                        if vel.x > 0:
                            pos.x = col2.left - collider.w
                            vel.x = 0
                        if vel.x < 0:
                            pos.x = col2.right
                            vel.x = 0
                        event = CollisionEvent(self.world, data, ent, ent2)
                        collision_events[ent2] = event

            if self.world.has_component(ent, Gravity):
                vel.y += 0.1
            pos.y += vel.y

            air_timer = self.world.try_component(ent, AirTimer)
            if air_timer is not None:
                air_timer.frames += 1

            is_on_floor = self.world.try_component(ent, IsOnFloor)
            if is_on_floor is not None:
                is_on_floor.ground = False
                is_on_floor.ceiling = False

            if collider:
                for ent2, (pos2, collider2) in self.world.get_components(Position, Collider):
                    if ent == ent2:
                        continue
                    if hasattr(collider2, 'enable') and not collider2.enable:
                        continue
                    col1 = pygame.Rect((pos.x + collider.x, ceil(pos.y + collider.y), collider.w, collider.h))
                    col2 = pygame.Rect((pos2.x + collider2.x, ceil(pos2.y + collider2.y), collider2.w, collider2.h))
                    if col1.colliderect(col2):
                        event = AreaEvent(self.world, data, ent, ent2)
                        area_events[ent2] = event
                    s_mask = self.world.try_component(ent2, CollisionMask)
                    if f_mask is None or s_mask is None or len(f_mask.intersection(s_mask)) < 1:
                        continue
                    if col1.colliderect(col2):
                        if vel.y >= 0:
                            pos.y = col2.top - collider.h
                            vel.y = 0
                            if air_timer is not None:
                                air_timer.frames = 0
                            if is_on_floor is not None:
                                is_on_floor.ground = True
                        if vel.y < 0:
                            pos.y = col2.bottom
                            vel.y = 0
                            if is_on_floor is not None:
                                is_on_floor.ceiling = True
                        event = CollisionEvent(self.world, data, ent, ent2)
                        collision_events[ent2] = event

            for event in area_events.values():
                event.dispatch()

            for event in collision_events.values():
                event.dispatch()


class CollisionProcessor(Processor):
    def process(self, data):
        entities = self.world.get_components(Position, Collider)
        entities = list(filter(lambda e: not hasattr(e[1][1], 'enable') or e[1][1].enable, entities))
        dyn_entities = list(filter(lambda e: hasattr(e[1][1], 'dynamic') and e[1][1].dynamic, entities))
        for i in range(0, len(dyn_entities)):
            f_ent, [f_pos, f_collider] = dyn_entities[i]
            f_mask = self.world.try_component(f_ent, CollisionMask)
            for j in range(0, len(entities)):
                s_ent, [s_pos, s_collider] = entities[j]
                if f_ent == s_ent:
                    continue
                s_mask = self.world.try_component(s_ent, CollisionMask)
                if f_mask is None or s_mask is None or len(f_mask.intersection(s_mask)) < 1:
                    continue
                col1 = pygame.Rect((f_pos.x + f_collider.x, f_pos.y + f_collider.y, f_collider.w, f_collider.h))
                col2 = pygame.Rect((s_pos.x + s_collider.x, s_pos.y + s_collider.y, s_collider.w, s_collider.h))
                if not col1.colliderect(col2):
                    continue
                CollisionEvent(self.world, data, f_ent, s_ent).dispatch()


class AreaProcessor(Processor):
    def process(self, data):
        entities = self.world.get_components(Position, Collider)
        entities = list(filter(lambda e: not hasattr(e[1][1], 'enable') or e[1][1].enable, entities))
        dyn_entities = list(filter(lambda e: hasattr(e[1][1], 'dynamic') and e[1][1].dynamic, entities))
        for i in range(0, len(dyn_entities)):
            f_ent, [f_pos, f_collider] = dyn_entities[i]
            for j in range(0, len(entities)):
                s_ent, [s_pos, s_collider] = entities[j]
                if f_ent == s_ent:
                    continue
                col1 = pygame.Rect((f_pos.x + f_collider.x, f_pos.y + f_collider.y, f_collider.w, f_collider.h))
                col2 = pygame.Rect((s_pos.x + s_collider.x, s_pos.y + s_collider.y, s_collider.w, s_collider.h))
                if not col1.colliderect(col2):
                    continue
                AreaEvent(self.world, data, f_ent, s_ent).dispatch()


class GravitySystem(Processor):
    def process(self, *args, **kwargs):
        for ent, [accel, vel] in self.world.get_components(Acceleration, Velocity):
            vel.y += accel.y


class CameraProcessor(Processor):
    def process(self, data):
        old_x, old_y = data.camera_pos
        for ent, (pos, _) in self.world.get_components(Position, PlayerId):
            data.camera_pos = (
                old_x + (pos.x - old_x - GameConstant.VIEW_WIDTH / 2) * GameConstant.CAMERA_SPEED,
                old_y + (pos.y - old_y - GameConstant.VIEW_HEIGHT / 2) * GameConstant.CAMERA_SPEED
            )


class BlinkProcessor(Processor):
    def process(self, data):
        current = time.time()
        for ent, (drawable, blink) in self.world.get_components(Drawable, Blink):
            if blink.duration >= 0 and blink.end < current:
                drawable.hide = False
                self.world.remove_component(ent, Blink)
                continue
            if blink.latest_blink and current < blink.latest_blink + blink.interval:
                continue
            drawable.hide = not drawable.hide
            blink.latest_blink = current


class ShakeProcessor(Processor):
    def process(self, *args, **kwargs):
        current = time.time()
        for ent, (drawable, shake) in self.world.get_components(Drawable, Shake):
            shake_limit = self.world.try_component(ent, ShakeLimit)
            offset = shake_limit.offset_x if shake_limit else EffectConstant.SHAKE_OFFSET
            if shake.end < current or shake.times and shake.run >= shake.times:
                x = 0
                if shake.state == Shake.STATE_LEFT:
                    x = offset
                elif shake.state == Shake.STATE_RIGHT:
                    x = -offset
                drawable.custom_offset_x += x
                self.world.remove_component(ent, Shake)
                continue
            if shake.latest_blink and current < shake.latest_blink + shake.interval:
                continue
            x = 0
            if shake.state == Shake.STATE_NORMAL or shake.state is None:
                x = -offset
                shake.state = Shake.STATE_LEFT
            elif shake.state == Shake.STATE_LEFT:
                x = offset * 2
                shake.state = Shake.STATE_RIGHT
            elif shake.state == Shake.STATE_RIGHT:
                x = -offset
                shake.state = Shake.STATE_NORMAL
            drawable.custom_offset_x += x
            shake.latest_blink = current
            shake.run += 1


class RendererProcessor(Processor):
    def process(self, data):
        (cam_x, cam_y) = data.camera_pos
        p_pos = data.player_pos
        for ent, (pos, drawable) in self.world.get_components(Position, Drawable):
            if pos.distance_squared_to(p_pos) > 60000:
                continue
            if drawable.drawable is not None and not drawable.hide:
                if type(drawable.drawable) is Surface:
                    # if self.world.has_component(ent, Shake):
                    #     print(drawable.custom_offset_x)
                    pos_x = int(pos.x + drawable.offset_x + drawable.custom_offset_x)
                    pos_y = int(pos.y + drawable.offset_y + drawable.custom_offset_y)
                    surface = drawable.drawable
                    if drawable.flip:
                        surface = pygame.transform.flip(surface, True, False)
                    data.canvas.blit(surface, (pos_x - int(cam_x), pos_y - int(cam_y)))
                elif type(drawable.drawable) is Rect:
                    rect = drawable.drawable
                    rect.x = pos.x
                    rect.y = pos.y
                    pygame.draw.rect(data.canvas, (255, 255, 255), drawable.drawable)
            if data.debug:
                collider = self.world.try_component(ent, Collider)
                if collider:
                    tl = [collider.x + pos.x, collider.y + pos.y]
                    tr = [collider.x + pos.x + collider.w, collider.y + pos.y]
                    bl = [collider.x + pos.x, collider.y + pos.y + collider.h]
                    br = [collider.x + pos.x + collider.w, collider.y + pos.y + collider.h]
                    points = (tl, tr, br, bl)
                    for point in points:
                        point[0] -= cam_x
                        point[1] -= cam_y
                    pygame.draw.lines(data.canvas, (255, 0, 0), True, points, 1)


class AnimationProcessor(Processor):
    def process(self, data):
        entities = self.world.get_components(Position, Drawable, AnimationList)
        entities = sorted(entities, key=lambda entity: entity[1][0].y)
        for ent, (pos, drawable, animation_list) in entities:
            next_animation = animation_list.get_current_animation()
            current_sprite = None
            if next_animation:
                current_sprite = next_animation.get_current_sprite()
                step = current_sprite.step
                if step <= 0:
                    step = next_animation.step
                if not next_animation.is_last_sprite() or next_animation.loop:
                    next_animation.index = (next_animation.index + step) % next_animation.total_frames

            direction = self.world.try_component(ent, Direction)
            offset = Vector2()
            scale = 1
            if next_animation:
                offset = next_animation.offset
                scale = next_animation.scale

            if current_sprite is not None:
                surface = next_animation.get_current_sprite().surface
                pos_x = pos.x + offset.x + next_animation.get_current_sprite().offset_x
                pos_y = pos.y + offset.y + next_animation.get_current_sprite().offset_y

                if next_animation.flip:
                    surface = pygame.transform.flip(surface, True, False)
                if scale != 1:
                    surface = pygame.transform.scale(surface,
                                                     (surface.get_size()[0] * scale, surface.get_size()[1] * scale))

                if direction and direction.x == 1:
                    surface = pygame.transform.flip(surface, True, False)
                drawable.drawable = surface
                drawable.offset_x = offset.x + next_animation.get_current_sprite().offset_x
                drawable.offset_y = offset.y + next_animation.get_current_sprite().offset_y

            if next_animation and next_animation.is_last_sprite() and next_animation.is_last_step() and next_animation.loop:
                next_animation.reset()


class AnimationStateProcessor(Processor):
    def process(self, *args, **kwargs):
        for ent, (pos, vel, anim_list) in self.world.get_components(Position, Velocity, AnimationList):
            pass


class StateSystem(Processor):
    def process(self, *args, **kwargs):
        for ent, [vel] in self.world.get_components(Velocity):
            y = min(vel.y + 1, 5)
            vel.y = y


class PlayerInputProcessor(Processor):
    def process(self, data):
        key_pressed = pygame.key.get_pressed()

        for ent, (controllable, velocity, direction, anim_list, pos, cooldown_dict, bullet_storage) in self.world.get_components(
                Controllable,
                Velocity,
                Direction,
                AnimationList,
                Position,
                CooldownDict,
                BulletStorage,
        ):
            velocity.x = 0
            if key_pressed[controllable.key_bindings[Controllable.JUMP]] and anim_list.current_animation != 'jump':
                velocity.y = -4
                direction.y = -1
            if key_pressed[controllable.key_bindings[Controllable.MOVE_LEFT]]:
                velocity.x = -1
                direction.x = -1
                if cooldown_dict.has_cooldown_expired(CooldownConstant.PLAYER_RUN):
                    pygame.mixer.Sound.play(data.resource.sound['player_run'])
                    cooldown_dict.add_cooldown(RunCooldown())
            if key_pressed[controllable.key_bindings[Controllable.MOVE_RIGHT]]:
                velocity.x = 1
                direction.x = 1
                if cooldown_dict.has_cooldown_expired(CooldownConstant.PLAYER_RUN):
                    pygame.mixer.Sound.play(data.resource.sound['player_run'])
                    cooldown_dict.add_cooldown(RunCooldown())
            if key_pressed[controllable.key_bindings[Controllable.ATTACK]]:
                if cooldown_dict.has_cooldown_expired(CooldownConstant.PLAYER_ATTACK):
                    pos_x = pos.x
                    pos_y = pos.y
                    if direction.x > 0:
                        pos_x += 11
                        pos_y += 5
                    else:
                        pos_x -= 13
                        pos_y += 5
                    bullet_vel = (direction.x * 10, 0)
                    bullet_pos = (pos_x, pos_y)
                    BulletFactory.create(self.world, bullet_storage.current, bullet_pos, bullet_vel)
                    create_gun_particle(self.world, (pos_x + (-1 if direction.x < 0 else 1), pos_y - 5 + random.uniform(-2, 2)))
                    cooldown_dict.add_cooldown(AttackCooldown())
                    pygame.mixer.Sound.play(data.resource.sound['attack'])


class TileMapProcessor(Processor):
    def process(self, data):
        for ent, [tileMap] in self.world.get_components(TileMap):
            _map = tileMap.tilemap
            tiles = tileMap.tiles
            for i in range(0, len(_map)):
                row = _map[i]
                for j in range(0, len(row)):
                    tile_name = row[j]
                    image = tiles[tile_name]
                    if image is None:
                        continue
                    data.canvas.blit(image, (j * 16, i * 16))


class CooldownDictProcessor(Processor):
    def process(self, data):
        for ent, [cooldown_dict] in self.world.get_components(CooldownDict):
            cooldown_dict.remove_expired_cooldowns()


class FlipByVelocityProcessor(Processor):
    def process(self, *args, **kwargs):
        for ent, [_, drawable, vel] in self.world.get_components(FlipByVelocity, Drawable, Velocity):
            drawable.flip = vel.x > 0


class StateProcessor(Processor):
    def process(self, *args, **kwargs):
        for ent, [state] in self.world.get_components(State):
            if state.check:
                return
            if state.on_state_change_handler:
                state.on_state_change_handler(self.world, state.prev, state.current)
            state.check = True
