import time
from dataclasses import dataclass

from game.constant import EntityConstant, EffectConstant


@dataclass
class Metadata:
    def __init__(self, entity_type):
        self.type = entity_type


class PlayerId:
    pass


class GunId:
    pass


class SwordId:
    pass


class ObstacleId:
    pass


class VillagerId:
    pass


class HeartId:
    pass


class MissileId:
    pass


class ChestId:
    pass


class EnemyId:
    pass


class CritterId:
    pass


class BatId:
    pass


class BulletId:
    pass


class ShieldId:
    pass


class MiseryId:
    pass


class Health:
    def __init__(self, value=0, max_value=-1):
        self.value = value
        self.max_value = max_value


class AttackDamage:
    def __init__(self, value=0):
        self.value = value


class BulletTarget:
    def __init__(self, targets):
        self.targets = targets


class BulletStorage:
    def __init__(self):
        self.current = EntityConstant.Bullet.Type.NORMAL


class DamageStack:
    def __init__(self):
        self.stack = []


class DamageReduction:
    def __init__(self, value):
        self.value = value


class Heal:
    def __init__(self, value=EntityConstant.Heart.HEAL):
        self.value = value


class Damage:
    def __init__(self, value):
        self.value = value


class Effect:
    def __init__(self, owner, duration):
        self.start = time.time()
        self.owner = owner
        self.duration = duration
        self.just_added = True

    def get_end(self):
        return self.start + self.duration

    end = property(fget=get_end)


class InvincibleEffect(Effect):
    def __init__(self, owner, duration=EffectConstant.INVINCIBLE_DURATION):
        super().__init__(owner, duration)


class ShieldEffect(Effect):
    def __init__(self, owner, duration=EffectConstant.SHIELD_DURATION, value=EffectConstant.SHIELD_DAMAGE_REDUCTION):
        super().__init__(owner, duration)
        self.value = value
        self.shield = None
        self.just_blink = False


class BulletPowerupEffect(Effect):
    def __init__(self, owner, duration=EffectConstant.SHIELD_DURATION):
        super().__init__(owner, duration)


