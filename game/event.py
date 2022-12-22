from common.event import Event


class PlayerCollisionEvent(Event):
    name = 'player_collision'

    def __init__(self, world, data, player, other):
        super().__init__(world, data)
        self.player = player
        self.other = other
