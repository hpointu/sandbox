import game as ga


def test_neighbours():
    g = ga.create_game(5, 5)
    assert ga.cell_neighbours(g, 0) == [1, 5, 6]
    assert ga.cell_neighbours(g, 1) == [0, 2, 5, 6, 7]
    assert ga.cell_neighbours(g, 4) == [3, 8, 9]
    assert ga.cell_neighbours(g, 24) == [18, 19, 23]
    assert ga.cell_neighbours(g, 7) == [1, 2, 3, 6, 8, 11, 12, 13]


def test_cell_index():
    g = ga.create_game(5, 5)
    assert ga.cell_index(g, 0, 0) == 0
    assert ga.cell_index(g, 22, 16) == 7
