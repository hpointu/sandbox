import math
import random
import time


CELL_SIZE = 40  # simulate walking distance
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
    col = int(x) // CELL_SIZE
    row = int(y) // CELL_SIZE
    return row * w + col


def create_agent(world, i):
    amp = 40
    speed_mod = random.randint(0, amp) - amp//2
    return cell_coords(world, i), None, 1 + speed_mod/100


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


def dist(p1, p2):
    (x1, y1), (x2, y2) = p1, p2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def dist_from_target(agent):
    pos, tgt, *_ = agent
    if not tgt:
        return 0
    return dist(pos, tgt)


def find_target(world, agent, switch_threshold=SWITCH_THRESHOLD):
    """ Scan agent surroundings for more food """
    grid, _, _ = world
    i = cell_index(world, *agent[0])
    neighs = cell_neighbours(world, i)
    food = grid[i]
    mod = switch_threshold if food > 0 else 0
    surrounding = [(k, grid[k] - mod) for k in neighs]
    random.shuffle(surrounding)
    target = max(
        [(i, food)] + surrounding,
        key=lambda s: s[1]
    )
    return agent[0], cell_coords(world, target[0]), agent[2]


def move_agent(world, agent):
    (x, y), (tx, ty), speed = agent

    if (x, y) == (tx, ty):
        return agent

    dx = speed if tx > x else -speed
    dy = speed if ty > y else -speed

    return (x + dx, y + dy), (tx, ty), speed


def eat(world, agent, portion=FOOD_PORTION):
    grid, w, h = world
    i = cell_index(world, *agent[0])
    if grid[i]:
        grid[i] -= portion
    return (grid, w, h), agent


def grow_food(world):
    grid, w, h = world

    def grow(c):
        if c >= 50:
            return c
        g = 0 if random.random() > 0.01 else 1
        return c + g

    grid = [grow(c) for c in grid]
    return grid, w, h


def step_agent(world, agent):
    if dist_from_target(agent) > 1:
        agent = move_agent(world, agent)
    else:
        agent = find_target(world, agent)
    world, agent = eat(world, agent)
    return world, agent


def step_world(world):
    return grow_food(world)


# From here it's only to render the game in the terminal

def draw_agent(world, a):
    (x, y), target, _ = a
    cell = cell_index(world, x, y)
    t = ""
    if target:
        t = "-> {}".format(target)
    print("Pos: {:0>2},{:0>2} {}".format(int(x), int(y), t))
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
        time.sleep(0.05)
