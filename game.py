import math
import random
import time
from typing import NamedTuple, List, Tuple, Union, Optional


CELL_SIZE = 40  # simulate walking distance
SWITCH_THRESHOLD = 20
FOOD_PORTION = 1


T = Union[int, float]
Coords = Tuple[T, T]
Food = int
Grid = List[Food]


class World(NamedTuple):
    grid: Grid
    width: int
    height: int


class Agent(NamedTuple):
    pos: Coords
    target: Optional[Coords]
    speed: float


def create_world(w, h) -> World:

    def food(seed):
        return seed * 10

    grid = [
        food(random.randint(0, 5))
        for i in range(w * h)
    ]

    return World(grid, w, h)


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
    amp = 40
    speed_mod = random.randint(0, amp) - amp//2
    return Agent(cell_coords(world, i), None, 1 + speed_mod/100)


def cell_neighbours(world: World, i: int) -> List[int]:
    grid, w, h = world
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


def find_target(world: World, agent: Agent,
                switch_threshold=SWITCH_THRESHOLD) -> Agent:
    """ Scan agent surroundings for more food """
    grid, _, _ = world
    i = cell_index(world, agent.pos)
    neighs = cell_neighbours(world, i)
    food = grid[i]
    mod = switch_threshold if food > 0 else 0
    surrounding = [(k, grid[k] - mod) for k in neighs]
    random.shuffle(surrounding)
    target = max(
        [(i, food)] + surrounding,
        key=lambda s: s[1]
    )
    return agent._replace(target=cell_coords(world, target[0]))


def move_agent(world: World, agent: Agent) -> Agent:
    if not agent.target:
        return agent

    if agent.pos == agent.target:
        return agent

    x, y = agent.pos
    tx, ty = agent.target
    s = agent.speed

    dx = s if tx > x else -s
    dy = s if ty > y else -s

    return agent._replace(pos=(x+dx, y+dy))


def eat(world: World, agent: Agent,
        portion=FOOD_PORTION) -> Tuple[World, Agent]:

    grid, w, h = world
    i = cell_index(world, agent.pos)

    if grid[i]:
        grid[i] -= portion

    return World(grid, w, h), agent


def grow_food(world: World) -> World:

    def grow(c):
        if c >= 50:
            return c
        g = 0 if random.random() > 0.01 else 1
        return c + g

    grid = [grow(c) for c in world.grid]
    return world._replace(grid=grid)


def step_agent(world: World, agent: Agent) -> Tuple[World, Agent]:
    if dist_from_target(agent) > 1:
        agent = move_agent(world, agent)
    else:
        agent = find_target(world, agent)
    world, agent = eat(world, agent)
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
    grid, w, h = world
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
    while True:
        world = step_world(world)
        for i, a in enumerate(agents):
            world, agents[i] = step_agent(world, agents[i])

        render(world, agents)
        time.sleep(0.05)
