import random
import pyglet as pg
import game as ga


GREENS = [
    (204, 204, 194),
    (199, 204, 153),
    (191, 204, 71),
    (184, 204, 0),
    (82, 204, 0),
    (0, 204, 20),
]

RES = {
    'creature.png': 'image',
}


class Sprite(pg.sprite.Sprite):
    pass


def vertices(world):
    grid, w, h = world
    k = ga.CELL_SIZE

    return sum([
        (i*k, j*k,
         i*k + k - 1, j*k,
         i*k + k - 1, j*k + k - 1,
         i*k, j*k + k - 1)
        for j in range(h)
        for i in range(w)
    ], tuple())


def target_lines(world, agents):
    return sum(
        [tuple(map(int, [x, y, *target]))
         for (x, y), target, *_ in agents
         if target],
        tuple()
    )


def agent_boxes(agents):
    return sum(
        [tuple(map(
            int,
            (x - 16, y - 22, x + 15, y - 22,
             x + 15, y - 22, x + 15, y - 18,
             x + 15, y - 18, x - 15, y - 18,
             x - 15, y - 18, x - 16, y - 22)))
            for (x, y), *_ in agents],
        tuple()
    )


def agent_box_colors(agents):
    def color(pv):
        return (0, 0, 0) if pv > 0 else (255, 0, 0)

    return sum([color(a.pv)*8 for a in agents],
               tuple())


def agent_pvs(agents):
    def _pv(pv):
        return 30 * (pv/100)

    return sum(
        [tuple(map(
            int,
            (x - 15, y - 22,
             x - 15 + _pv(pv), y - 22,
             x - 15 + _pv(pv), y - 18,
             x - 15, y - 18)))
            for (x, y), _, _, pv in agents],
        tuple()
    )


def food_color(v):
    v //= 10
    v = min(v, len(GREENS)-1)
    return GREENS[v]


def map_colors(world):
    grid = world[0]
    return sum((food_color(f) * 4 for f in grid), tuple())


class WorldView(object):
    """ GL rendering of the world map """
    def __init__(self, window, world, agents,
                 x=0, y=0, scale=1):
        self._x = x
        self._y = y
        self.background = pg.graphics.OrderedGroup(0)
        self.foreground = pg.graphics.OrderedGroup(1)
        self.scale = scale
        self.window = window
        verts = vertices(world)
        self.world_batch = pg.graphics.Batch()
        colors = map_colors(world)
        self._build(verts, colors)
        self.update_agents(world, agents)

    def _build(self, verts, colors):
        n = len(verts) // 2
        self.verts = self.world_batch.add(
            n, pg.gl.GL_QUADS,
            self.background,
            ("v2i", verts),
            ("c3B", colors))

    def update_food(self, world):
        self.verts.colors = map_colors(world)

    def update_agents(self, world, agents):
        self.agents = [
            Sprite(
                RES['creature.png'],
                *pos,
                batch=self.world_batch,
                group=self.foreground,
            )
            for pos, *_ in agents
        ]

        lines = target_lines(world, agents)
        n = len(lines) // 2
        self.targets = pg.graphics.vertex_list(
            n, ("v2i", lines),
            ("c3B", (255, 0, 255) * n),
        )

        n = 4 * len(agents)
        self.agentpvs = pg.graphics.vertex_list(
            n, ("v2i", agent_pvs(agents)),
            ("c3B", (0, 255, 0) * n),
        )

        n = 8 * len(agents)
        self.agentboxes = pg.graphics.vertex_list(
            n, ("v2i", agent_boxes(agents)),
            ("c3B", agent_box_colors(agents)),
        )

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y - self.window.height

    def draw(self):
        pg.gl.glPushMatrix()
        pg.gl.glScalef(1, -1, 1)
        pg.gl.glTranslatef(self.x, self.y, 0)
        pg.gl.glScalef(self.scale, self.scale, 1)
        self.world_batch.draw()
        self.agentpvs.draw(pg.gl.GL_QUADS)
        self.agentboxes.draw(pg.gl.GL_LINES)
        self.targets.draw(pg.gl.GL_LINES)
        pg.gl.glPopMatrix()


def initialize_agents(world, number):
    grid, *_ = world
    size = len(grid)
    return [
        ga.create_agent(world, random.randrange(size))
        for _ in range(number)
    ]


def load_resources():
    for r, t in RES.items():
        if t != 'image':
            raise NotImplementedError
        res = pg.resource.image(r, flip_y=True)
        res.anchor_x = res.width / 2
        res.anchor_y = res.height / 2
        RES[r] = res


def step_game(view, world, agents):

    world = world
    agents = agents

    def _handler(dt):
        nonlocal world
        nonlocal agents

        world = ga.step_world(world)
        for i, a in enumerate(agents):
            world, agents[i] = ga.step_agent(world, agents[i])

        view.update_food(world)
        view.update_agents(world, agents)

    return _handler


def start_game():
    pg.gl.glEnable(pg.gl.GL_TEXTURE_2D)
    pg.gl.glTexParameteri(pg.gl.GL_TEXTURE_2D,
                          pg.gl.GL_TEXTURE_MAG_FILTER,
                          pg.gl.GL_NEAREST)
    WIDTH, HEIGHT = 10, 10

    window = pg.window.Window()

    load_resources()
    world = ga.create_world(WIDTH, HEIGHT)
    agents = initialize_agents(world, 8)

    world_view = WorldView(window, world, agents, x=10, y=10)

    pg.clock.schedule(step_game(world_view, world, agents))

    @window.event()
    def on_draw():
        window.clear()
        world_view.draw()


if __name__ == "__main__":
    start_game()
    pg.app.run()
