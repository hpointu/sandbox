import random
import time


CELL_SIZE = 10  # simulate walking distance
SWITCH_THRESHOLD = 20
FOOD_PORTION = 1


def create_game(w, h):

    def food(seed):
        return seed * 10

    grid = [
        food(random.randint(1, 5))
        for i in range(w * h)
    ]

    return grid, w, h


def center(c):
    return c * CELL_SIZE + CELL_SIZE // 2


def cell_coords(game, i):
    _, w, _ = game
    return center(i % w), center(i // w)


def cell_index(game, x, y):
    _, w, _ = game
    col = x // CELL_SIZE
    row = y // CELL_SIZE
    return row * w + col


def create_agent(game, i):
    return cell_coords(game, i)


def cell_neighbours(game, i):
    grid, w, h = game
    c = i % w

    def neigh(p):
        return -2 < p % w - c < 2

    return [
        x for x in (i-w-1, i-w, i-w+1,
                    i-1,        i+1,
                    i+w-1, i+w, i+w+1)
        if 0 <= x < w*h and neigh(x)
    ]


def find_target(game, agent, switch_threshold=SWITCH_THRESHOLD):
    """ Scan agent surroundings for more food """
    grid, _, _ = game
    i = cell_index(game, *agent)
    neighs = cell_neighbours(game, i)
    food = grid[i]
    mod = switch_threshold if food else 0
    surrounding = [(k, grid[k] - mod) for k in neighs]
    return max([(i, food)] + surrounding,
               key=lambda s: s[1])


def move_agent(game, agent, target, speed=1):
    x, y = agent
    tx, ty = cell_coords(game, target)

    if (x, y) == (tx, ty):
        return agent, False

    dx = speed if tx > x else -speed
    dy = speed if ty > y else -speed

    return (x + dx, y + dy), True


def eat(game, agent, portion=FOOD_PORTION):
    grid, w, h = game
    i = cell_index(game, *agent)
    grid[i] -= portion
    return grid, w, h


def draw_agent(game, a):
    x, y = a
    cell = cell_index(game, x, y)
    print("Pos: {:0>2},{:0>2}".format(x, y))
    print("cell: {}".format(cell))


def draw_game(game):
    grid, w, h = game
    rows = (' '.join("{:0>2}".format(c)
                     for c in grid[i*w:i*w+w])
            for i in range(h))
    print('\n'.join(rows))


def render(game, agent, target):
    print("---")
    draw_agent(game, agent)
    print("Moving to: {}".format(cell_coords(game, target[0])))
    print()
    draw_game(game)
    print()


if __name__ == "__main__":
    g = create_game(10, 10)
    a = create_agent(g, random.randrange(0, 100))
    while True:
        target = find_target(g, a)
        a, moved = move_agent(g, a, target[0])
        if not moved:
            g = eat(g, a)  # only eat when not moving
        render(g, a, target)
        time.sleep(0.1)
