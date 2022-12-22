import esper


class Event:
    name = 'event'

    def __init__(self, world, game_data):
        self.world = world
        self.data = game_data

    def dispatch(self):
        esper.dispatch_event(self.name, self)

    @classmethod
    def register(cls, func):
        esper.set_handler(cls.name, func)

    @classmethod
    def unregister(cls, func):
        esper.remove_handler(cls.name, func)


class EntityEvent(Event):
    name = 'entity'

    def __init__(self, world, game_data, entities=None):
        super().__init__(world, game_data)
        if entities is None:
            entities = []
        self.entities = entities

    def get_entities(self, component_type):
        res = []
        for entity in self.entities:
            if not entity.try_component(entity, component_type):
                continue
            res.append(entity)
        return res

    def has_entity(self, component_type):
        for entity in self.entities:
            if not entity.try_component(entity, component_type):
                continue
            return True
        return False


class CollisionEvent(Event):
    name = 'collision'

    def __init__(self, world, game_data, first, second):
        super().__init__(world, game_data)
        self.first = first
        self.second = second


class EntityDeathEvent(Event):
    name = 'entity-death'

    def __init__(self, world, game_data, ent):
        super().__init__(world, game_data)
        self.entity = ent


class AreaEvent(Event):
    name = 'area'

    def __init__(self, world, game_data, first, second):
        super().__init__(world, game_data)
        self.first = first
        self.second = second


class StateChangeEvent(Event):
    name = 'state'

    def __init__(self, world, game_data, old, new):
        super().__init__(world, game_data)
        self.old = old
        self.new = new




