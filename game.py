import math
import random
import time
from enum import Enum
from typing import NamedTuple, List, Tuple, Union, Optional


CELL_SIZE = 40  # simulate walking distance
FOOD_PORTION = 1


T = Union[int, float]
Coords = Tuple[T, T]
Food = int
Grid = List[Food]


class Action(Enum):
    SLEEPING = 0
    MOVING = 1
    EATING = 2


class ADN(NamedTuple):
    speed: float = 1.0
    laziness: float = 0.4
    sociability: float = 0.5
    hungriness: int = 80


class Agent(NamedTuple):
    pos: Coords
    target: Optional[Coords]
    adn: ADN
    action: Action = Action.SLEEPING
    pv: float = 100


class World(NamedTuple):
    grid: Grid
    width: int
    height: int
    agents: List[Agent]
    coords: List[Coords]


def create_world(w, h) -> World:

    def food(seed):
        return seed * 10

    grid = [
        food(random.randint(0, 5))
        for i in range(w * h)
    ]

    wo = World(grid, w, h, [], [])
    return wo._replace(coords=[cell_coords(wo, i)
                               for i in range(w * h)])


def center(c: int) -> int:
    return c * CELL_SIZE + CELL_SIZE // 2


def cell_coords(world: World, i: int) -> Coords:
    w = world.width
    return center(i % w), center(i // w)


def cell_index(world: World, c: Coords) -> int:
    x, y = c
    w = world.width
    col = int(x) // CELL_SIZE
    row = int(y) // CELL_SIZE
    return row * w + col


def create_agent(world: World, i: int) -> Agent:
    def mitigate(v, percent=20):
        r = 100 + random.randint(0, percent*2) - percent
        return v * r / 100

    adn = ADN()

    adn._replace(
        speed=mitigate(adn.speed),
        laziness=mitigate(adn.laziness),
        sociability=mitigate(adn.sociability),
        hungriness=mitigate(adn.hungriness),
    )
    return Agent(world.coords[i], None, adn)


def cell_neighbours(world: World, i: int) -> List[int]:
    grid, w, h, *_ = world
    c = i % w

    def neigh(p):
        return -2 < p % w - c < 2

    return [
        x for x in (i-w-1, i-w, i-w+1,
                    i-1,        i+1,
                    i+w-1, i+w, i+w+1)
        if 0 <= x < w*h and neigh(x)
    ]


def dist(p1: Coords, p2: Coords) -> float:
    (x1, y1), (x2, y2) = p1, p2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def dist_from_target(agent: Agent) -> float:
    pos, tgt, *_ = agent
    if not tgt:
        return 0
    return dist(pos, tgt)


def find_target(world: World, agent: Agent) -> Coords:
    """ Scan agent surroundings for more food """
    grid, *_ = world

    def _interest(i):
        occupied = bool([a for a in world.agents
                         if cell_index(world, a.pos) == i])
        social_factor = agent.adn.sociability if occupied else 1
        distance = dist(agent.pos, world.coords[i])
        return grid[i] * social_factor - distance * agent.adn.laziness

    i = cell_index(world, agent.pos)
    food = grid[i]

    neighs = cell_neighbours(world, i)
    random.shuffle(neighs)

    surroundings = [(world.coords[i], _interest(i))
                    for i in neighs]

    target = max([(world.coords[i], food), *surroundings],
                 key=lambda s: s[1])

    return target[0]


def move_agent(world: World, agent: Agent) -> Agent:
    if not agent.target:
        return agent

    if agent.pos == agent.target:
        return agent

    x, y = agent.pos
    tx, ty = agent.target
    s = agent.adn.speed

    dx = s if tx > x else -s
    dy = s if ty > y else -s

    return agent._replace(pos=(x+dx, y+dy))


def eat(world: World, agent: Agent,
        portion=FOOD_PORTION) -> Tuple[World, Agent]:

    grid, w, h, *_ = world
    i = cell_index(world, agent.pos)

    pv = agent.pv
    if grid[i]:
        grid[i] -= portion
        pv += portion * 4

    pv = min(100, pv)

    return world._replace(grid=grid), agent._replace(pv=pv)


def grow_food(world: World) -> World:

    def grow(c):
        if c >= 50:
            return c
        g = 0 if random.random() > 0.01 else 1
        return c + g

    grid = [grow(c) for c in world.grid]
    return world._replace(grid=grid)


def step_agent(world: World, agent: Agent) -> Tuple[World, Agent]:
    if agent.pv < 1:  # Deads don't eat or move
        return world, agent

    action = agent.action
    next_target = find_target(world, agent)

    if action == Action.MOVING:
        agent = move_agent(world, agent)
        if dist_from_target(agent) <= 2:
            agent = agent._replace(action=Action.EATING,
                                   target=next_target)
        else:
            agent = agent._replace(target=next_target)

    elif action == Action.EATING:
        if agent.pv >= 100 or next_target != agent.target:
            agent = agent._replace(action=Action.SLEEPING)
        else:
            world, agent = eat(world, agent)

    if action == Action.SLEEPING:
        if agent.pv < agent.adn.hungriness:
            agent = agent._replace(action=Action.MOVING,
                                   target=next_target)

    tireness = 0.3 if action == Action.SLEEPING else 1

    pv = max(agent.pv - tireness, 0)
    agent = agent._replace(pv=pv)
    return world, agent


def step_world(world) -> World:
    return grow_food(world)


# From here it's only to render the game in the terminal

def draw_agent(world: World, a: Agent) -> None:
    x, y = a.pos
    cell = cell_index(world, a.pos)
    t = ""
    if a.target:
        t = "-> {}".format(a.target)
    print("Pos: {:0>2},{:0>2} {}".format(int(x), int(y), t))
    print("cell: {}".format(cell))


def draw_world(world: World) -> None:
    grid, w, h, *_ = world
    rows = (' '.join("{:0>2d}".format(c)
                     for c in grid[i*w:i*w+w])
            for i in range(h))
    print('\n'.join(rows))


def render(world: World, agents: List[Agent]):
    print("---")
    for agent in agents:
        draw_agent(world, agent)
    print()
    draw_world(world)
    print()


if __name__ == "__main__":
    world = create_world(10, 10)

    agents = [create_agent(world, random.randrange(0, 100)),
              create_agent(world, random.randrange(0, 100))]

    world._replace(agents=agents)

    while True:
        world = step_world(world)
        for i, a in enumerate(agents):
            world, agents[i] = step_agent(world, agents[i])

        render(world, agents)
        time.sleep(0.05)
