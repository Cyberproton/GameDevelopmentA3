from common.component import Cooldown
from game.constant import CooldownConstant


class AttackCooldown(Cooldown):
    def __init__(self, start: float = None):
        super().__init__(CooldownConstant.PLAYER_ATTACK, CooldownConstant.PLAYER_ATTACK_COOLDOWN, start)


class RunCooldown(Cooldown):
    def __init__(self, start: float = None):
        super().__init__(CooldownConstant.PLAYER_RUN, CooldownConstant.PLAYER_RUN_COOLDOWN, start)


def add_component_if_not_exists(world, entity, component) -> bool:
    if world.has_component(entity, type(component)):
        return False
    world.add_component(entity, component)
    return True


def is_entity_has_any_component(world, entity, component_types):
    for component_type in component_types:
        if world.has_component(entity, component_type):
            return True
    return False


def is_any_entities_has_components(world, entities, components):
    res = [False] * len(components)
    for entity in entities:
        for i in range(len(components)):
            component = components[i]
            if world.has_component(entity, component):
                res[i] = True
    return all(res)


def get_entity_has_component(world, entities, component):
    for entity in entities:
        if not world.has_component(entity, component):
            continue
        return entity
    return None


def clamp(n, min_value, max_value):
    return max(min(max_value, n), min_value)


def clamp_abs(n, min_value, max_value):
    a = abs(n)
    c = n
    if a > max_value:
        c = max_value if c > 0 else -max_value
    if a < min_value:
        c = min_value if c > 0 else -min_value
    return c
