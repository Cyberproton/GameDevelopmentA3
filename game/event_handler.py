import random

import pygame.mixer

from common.component import *
from common.event import *
from game.component import *
from game.entity import create_heart, create_missile
from game.particle.entity import create_bullet_explosion
from game.util import is_any_entities_has_components, get_entity_has_component, add_component_if_not_exists, \
    is_entity_has_any_component


def register_all_event_handlers():
    AreaEvent.register(on_player_and_heart_collide)
    AreaEvent.register(on_player_and_missile_collide)
    AreaEvent.register(on_bullet_collide)
    AreaEvent.register(on_critter_reach_player)
    AreaEvent.register(on_bat_reach_player)
    EntityDeathEvent.register(on_chest_death)


def on_critter_reach_player(event):
    world = event.world
    if is_any_entities_has_components(world, [event.first, event.second], [PlayerId, CritterId]):
        player = get_entity_has_component(world, [event.first, event.second], PlayerId)
        # add_component_if_not_exists(world, player, Blink(5))
        # for ent, _ in world.get_component(GunId):
        #     add_component_if_not_exists(world, ent, Blink(5))
        world.try_component(player, DamageStack).stack.append(Damage(100))


def on_bat_reach_player(event):
    world = event.world
    if is_any_entities_has_components(world, [event.first, event.second], [PlayerId, BatId]):
        player = get_entity_has_component(world, [event.first, event.second], PlayerId)
        world.try_component(player, DamageStack).stack.append(Damage(10))


def on_player_and_heart_collide(event):
    world = event.world
    data = event.data
    if is_any_entities_has_components(world, [event.first, event.second], [PlayerId, HeartId]):
        player = get_entity_has_component(world, [event.first, event.second], PlayerId)
        heart = get_entity_has_component(world, [event.first, event.second], HeartId)
        world.try_component(player, DamageStack).stack.append(Heal())
        pygame.mixer.Sound.play(data.resource.sound['health'])
        event.world.delete_entity(heart)


def on_player_and_missile_collide(event):
    world = event.world
    data = event.data
    if is_any_entities_has_components(world, [event.first, event.second], [PlayerId, MissileId]):
        player = get_entity_has_component(world, [event.first, event.second], PlayerId)
        missile = get_entity_has_component(world, [event.first, event.second], MissileId)

        bullet_powerup_effect = world.try_component(player, BulletPowerupEffect)
        if bullet_powerup_effect:
            bullet_powerup_effect.duration += EffectConstant.SHIELD_DURATION
        else:
            world.add_component(player, BulletPowerupEffect(player))

        shield_effect = world.try_component(player, ShieldEffect)
        if shield_effect:
            shield_effect.duration += EffectConstant.SHIELD_DURATION
        else:
            world.add_component(player, ShieldEffect(player))

        pygame.mixer.Sound.play(data.resource.sound['missile'])
        event.world.delete_entity(missile)


def on_chest_death(event):
    world = event.world
    data = event.data

    if world.try_component(event.entity, ChestId):
        pos = world.component_for_entity(event.entity, Position)

        heart_id = create_heart(world, (int(pos.x + 10), int(pos.y)))
        world.add_component(heart_id, Blink(3))

        missile = create_missile(world, (pos.x + random.uniform(-5, 5), pos.y))

        pygame.mixer.Sound.play(data.resource.sound['chest_break'])


def on_bullet_collide(event):
    world = event.world
    bullet = get_entity_has_component(world, [event.first, event.second], BulletId)
    other = event.first if bullet == event.second else event.second
    if bullet is None:
        return
    targets = world.component_for_entity(bullet, BulletTarget).targets
    if is_entity_has_any_component(world, other, targets):
        damage = world.component_for_entity(bullet, AttackDamage).value
        pos = world.component_for_entity(bullet, Position)
        damage_stack = world.try_component(other, DamageStack)
        if damage_stack:
            damage_stack.stack.append(Damage(damage))
        if world.has_component(other, PlayerId):
            add_component_if_not_exists(world, other, Blink(3))
        else:
            add_component_if_not_exists(world, other, Shake(1, 3))
        add_component_if_not_exists(world, other, Shake(1, 3))
        world.component_for_entity(bullet, IsAlive).value = False
        create_bullet_explosion(world, pos)
    if is_any_entities_has_components(world, [event.first, event.second], [BulletId, ObstacleId]):
        bullet = get_entity_has_component(world, [event.first, event.second], BulletId)
        world.component_for_entity(bullet, IsAlive).value = False
        pos = world.component_for_entity(bullet, Position)
        create_bullet_explosion(world, pos)
