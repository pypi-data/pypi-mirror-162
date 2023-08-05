"""python-astar demo

"""
from time import sleep
from random import uniform, randint, choice

from astar.search import AStar

def walk_through(world, path):
    """Plays the animation of the character walking through the maze"""
    if not path:
        return
    for x, y in path:
        world[x][y] = 2
        show_map(world)
        sleep(0.05)
        world[x][y] = 4
    
def show_map(grid):
    """Print the map"""
    sprints = {
        0: " ",
        1: "#",
        2: "*",
        4: ".",
        }
    print("------------------")
    for line in grid:
        row = ' '.join([sprints[x] for x in line])
        print(row)

def make_a_maze(size_x=32, size_y=32, density=0.3):
    """Build a random map. The ratio of walls is given by density."""
    def rand_tile():
        return (1 if uniform(0, 1) < density else 0)
    world = [[rand_tile() for y in range(size_y)] for x in range(size_x)]
    # make goal a safe place
    world[size_x-1][size_y-1] = 0
    return world

def make_a_contiguous_maze(size_x=32, size_y=32, lines=5):
    """Build a linear map. The ratio of walls is given by lines."""
    def draw_a_line(grid):
        size = randint(1, 10)
        direction = choice([True, False])
        if direction:
            # horizontal Y
            x = randint(0, len(grid) - 1)
            y = randint(0, len(grid[0]) - size - 1)
        
        else:
            # vertical X
            x = randint(0, len(grid) - size - 1)
            y = randint(0, len(grid[0]) - 1)

        for i in range(size):
            grid[x][y] = 1
            if direction:
                y += 1
            else:
                x += 1
            print(x, y)

    world = [[0 for y in range(size_y)] for x in range(size_x)]

    for i in range(lines):
        draw_a_line(world)
    # make goal a safe place
    world[size_x-1][size_y-1] = 0
    return world


def showcase(size_x=16, size_y=32):
    """loop random mazes and find the shortest path"""
    goal = (size_x-1, size_y-1)

    start = (0, 0)
    
    while True:
        if choice([True, False]):
            world = make_a_contiguous_maze(size_x, size_y, lines=20)
        else:
            world = make_a_maze(size_x, size_y, density=0.28)

        path = AStar(world).search(start, goal)

        # we try again if there is no path found
        if not path:
            continue

        walk_through(world, path)


