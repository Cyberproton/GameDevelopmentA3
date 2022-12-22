from esper import Processor

from common.component import *
from game.component import *
from game.entity import create_shield
from game.util import clamp, add_component_if_not_exists


class HealthProcessor(Processor):
    def process(self, *args, **kwargs):
        for ent, [health, is_alive] in self.world.get_components(Health, IsAlive):
            if health.value <= 0:
                is_alive.value = False


class DamageStackProcessor(Processor):
    def process(self, *args, **kwargs):
        for ent, [damage_stack, health] in self.world.get_components(DamageStack, Health):
            stack = damage_stack.stack
            damage_stack.stack = []

            if self.world.try_component(ent, InvincibleEffect):
                continue

            damage = 0
            damage_reduction = 0
            heal = 0
            for item in stack:
                if type(item) == int or type(item) == float:
                    damage += item
                elif type(item) == Damage:
                    damage += item.value
                elif type(item) == Heal:
                    heal += item.value
                elif type(item) == DamageReduction:
                    damage_reduction += item.value

            damage_reduction = clamp(damage_reduction, 0, 1)
            v = heal - damage * (1 - damage_reduction)
            if health.max_value > 0:
                health.value = min(health.value + v, health.max_value)
            else:
                health.value += v

            if self.world.has_component(ent, PlayerId) and v < 0:
                add_component_if_not_exists(self.world, ent, Blink(5))
                add_component_if_not_exists(self.world, ent, InvincibleEffect(5))
                for gun, _ in self.world.get_component(GunId):
                    add_component_if_not_exists(self.world, gun, Blink(5))


class GunPositionProcessor(Processor):
    def process(self, *args, **kwargs):
        for ent, (pos, drawable, owner, _) in self.world.get_components(Position, Drawable, Owner, GunId):
            owner_dir = self.world.component_for_entity(owner.owner, Direction)
            drawable.flip = owner_dir.x > 0
            if owner_dir.x > 0:
                drawable.offset_x = 11
                drawable.offset_y = 9
            else:
                drawable.offset_x = -4
                drawable.offset_y = 9
            owner_pos = self.world.component_for_entity(owner.owner, Position)
            pos.x = owner_pos.x
            pos.y = owner_pos.y


class ShieldPositionProcessor(Processor):
    def process(self, *args, **kwargs):
        for ent, (pos, drawable, owner, _) in self.world.get_components(Position, Drawable, Owner, ShieldId):
            owner_pos = self.world.component_for_entity(owner.owner, Position)
            pos.x = owner_pos.x - 3
            pos.y = owner_pos.y - 3


class ShieldEffectProcessor(Processor):
    def process(self, *args, **kwargs):
        current = time.time()
        for ent, [effect] in self.world.get_components(ShieldEffect):
            if effect.just_added:
                pos = self.world.try_component(ent, Position)
                shield = create_shield(self.world, pos, effect.owner)
                effect.shield = shield
                effect.just_added = False

            if effect.end < current:
                self.world.delete_entity(effect.shield)
                self.world.remove_component(effect.owner, ShieldEffect)
                continue

            if current > effect.end - EffectConstant.EFFECT_WEAR_OFF_BLINK:
                if not effect.just_blink:
                    self.world.add_component(effect.shield, Blink(-1))
                    effect.just_blink = True
            elif self.world.has_component(effect.shield, Blink):
                self.world.remove_component(effect.shield, Blink)

            damage_stack = self.world.try_component(ent, DamageStack)
            if damage_stack:
                damage_stack.stack.append(DamageReduction(effect.value))


class BulletPowerupEffectProcessor(Processor):
    def process(self, *args, **kwargs):
        current = time.time()
        for ent, [effect] in self.world.get_components(BulletPowerupEffect):
            if effect.just_added:
                bullet_storage = self.world.try_component(effect.owner, BulletStorage)
                bullet_storage.current = EntityConstant.Bullet.Type.BIG
                effect.just_added = False

            if effect.end < current:
                bullet_storage = self.world.try_component(effect.owner, BulletStorage)
                bullet_storage.current = EntityConstant.Bullet.Type.NORMAL
                self.world.remove_component(effect.owner, BulletPowerupEffect)
                continue


class InvincibleEffectProcessor(Processor):
    def process(self, *args, **kwargs):
        current = time.time()
        for ent, [effect] in self.world.get_components(InvincibleEffect):
            if current > effect.end:
                self.world.remove_component(ent, InvincibleEffect)


