# python-astar
Yet another A* path search algorithm.


This is one more A star implementation done for fun and I hope someone might find this useful.

You can import this module and use it to find the shortest path in a map given by a matrix.

There also a procedural implementation in the _examples/basic.py_ file that will probably be more easy to read and didactic in case you are learning how A* works.


## install:

```shell
    pip install python-astar
```


## usage:

```python
    from astar.search import AStar

    # Make a map (any size!)
    world = [
        [0,0,0],
        [1,1,0],
        [0,0,0],
        ]

    # define a start and end goals (x, y) (vertical, horizontal)
    start = (0, 0)
    goal = (2, 0)
    
    # search
    path = AStar(world).search(start, goal)
    
    print(path)
    # should be:
    
    # [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0)]

```

_path_ returns a list with (x, y) tuples with each step to reach that goal!


## random map with animation!


```python
    from astar.demo import make_a_maze, walk_through


    if __name__ == "__main__":
        # Given a map size
        size_x, size_y = 16, 32
        
        # Build a map
        world = make_a_maze(size_x, size_y, density=0.1)
        
        # Set start and end goal
        start = (0, 0)
        goal = (size_x-1, size_y-1)
        
        # Search for path
        path = AStar(world).search(start, goal)

        # Show the path
        walk_through(world, path)

```

## more examples:

Please take a look in the _examples/_ dir for some cool examples how to use it.


## testing:

```shell
    pytest
```

If you find it useful give it a star :D

