import random
import time


CELL_SIZE = 20  # simulate walking distance
SWITCH_THRESHOLD = 20
FOOD_PORTION = 1


def create_world(w, h):

    def food(seed):
        return seed * 10

    grid = [
        food(random.randint(0, 5))
        for i in range(w * h)
    ]

    return grid, w, h


def center(c):
    return c * CELL_SIZE + CELL_SIZE // 2


def cell_coords(world, i):
    _, w, _ = world
    return center(i % w), center(i // w)


def cell_index(world, x, y):
    _, w, _ = world
    col = x // CELL_SIZE
    row = y // CELL_SIZE
    return row * w + col


def create_agent(world, i):
    return cell_coords(world, i), None


def cell_neighbours(world, i):
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


def find_target(world, agent, switch_threshold=SWITCH_THRESHOLD):
    """ Scan agent surroundings for more food """
    grid, _, _ = world
    i = cell_index(world, *agent[0])
    neighs = cell_neighbours(world, i)
    food = grid[i]
    mod = switch_threshold if food > 0 else 0
    surrounding = [(k, grid[k] - mod) for k in neighs]
    target = max(
        [(i, food)] + surrounding,
        key=lambda s: s[1]
    )
    return agent[0], target[0]


def move_agent(world, agent, speed=1):
    (x, y), target = agent
    tx, ty = cell_coords(world, target)

    if (x, y) == (tx, ty):
        return (x, y), None

    dx = speed if tx > x else -speed
    dy = speed if ty > y else -speed

    return (x + dx, y + dy), target


def eat(world, agent, portion=FOOD_PORTION):
    grid, w, h = world
    i = cell_index(world, *agent[0])
    grid[i] -= portion
    return grid, w, h


def grow_food(world):
    grid, w, h = world

    def grow(c):
        g = 0 if random.random() > 0.01 else 1
        return c + g

    grid = [grow(c) for c in grid]
    return grid, w, h


def step_world(world):
    return grow_food(world)


def step_agent(world, a):
    a = find_target(world, a)
    a = move_agent(world, a)
    if not a[1]:
        world = eat(world, a)
    return world, a


# From here it's only to render the game in the terminal

def draw_agent(world, a):
    (x, y), target = a
    cell = cell_index(world, x, y)
    t = ""
    if target:
        t = "-> {}".format(cell_coords(world, target))
    print("Pos: {:0>2},{:0>2} {}".format(x, y, t))
    print("cell: {}".format(cell))


def draw_world(world):
    grid, w, h = world
    rows = (' '.join("{:0>2d}".format(c)
                     for c in grid[i*w:i*w+w])
            for i in range(h))
    print('\n'.join(rows))


def render(world, agents):
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
        time.sleep(0.1)
