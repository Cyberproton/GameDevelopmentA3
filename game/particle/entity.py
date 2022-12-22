from common.component import *
from game.particle.component import *


def create_gun_particle(world, pos):
    particle = world.create_entity(
        ParticleId,
        Position(pos),
        AnimationList.load_single('./assets/entity/particle_gun'),
        Drawable(),
        LifeTime(0.2),
    )
    return particle


def create_bullet_explosion(world, pos):
    particle = world.create_entity(
        ParticleId,
        Position(pos),
        AnimationList.load_single('./assets/entity/particle_bullet_explosion'),
        Drawable(),
        LifeTime(0.2),
    )
    return particle
