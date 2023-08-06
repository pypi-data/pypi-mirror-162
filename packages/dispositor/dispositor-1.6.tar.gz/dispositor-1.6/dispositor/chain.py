from dispositor.space import Space
from dispositor.planet import Planet


class Chain:
    """
    Этот класс возвращает данные только для цепочки диспозиторов (части цепочки, содержимое части (планеты с орбитами))
    Предположительно изначально будет расчет вестись без учета орбит. Поэтому пока данный класс не реализуется.
    """
    def __init__(self, space):
        self.space = space
        self.temp_planets = []
        self.center_planets = set()

    def setSpace(self, space):
        self.space = space
        self.center_planets = set()

    def getCenterPlanets(self):
        for planet in self.space.planets:
            self.temp_planets = []
            self.detectCenterStep(planet)
        return self.center_planets

    def detectCenterStep(self, planet: Planet):
        if planet.name in self.temp_planets:
            if planet.name not in [planet_uniq.name for planet_uniq in self.center_planets]:
                self.center_planets.add(planet)
            return True
        else:
            self.temp_planets.append(planet.name)
            self.detectCenterStep(self.getParent(planet))

    def getParent(self, planet: Planet):
        return planet.getSegment().owner_planet(planet.space)
