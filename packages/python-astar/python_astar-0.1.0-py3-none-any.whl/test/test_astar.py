
import pytest

from astar.search import AStar

class TestAStar:

    # define a start and end goals (x, y) (vertical, horizontal)
    start = (0, 0)
    goal = (2, 0)

    def test_happy_path(self):
        """Draw a simple map and see if we can find the way out"""
        # Make a map
        grid = [
            [0,0,0],
            [1,1,0],
            [0,0,0],
            ]
        # search
        path = AStar(grid).search(self.start, self.goal)
        
        # should be:
        assert path == [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0)]

    def test_blocked_path(self):
        """Draw a blocked map and see if recognize we are lost"""
        # Given a blocked map
        grid = [
            [0,0,0],
            [1,1,0],
            [0,1,0],
            ]
        # search
        path = AStar(grid).search(self.start, self.goal)
        
        # should be:
        assert path is None

    def test_closest_path(self):
        """Check if we will seek the closest path"""
        # Make a map
        grid = [
            [0,0,0],
            [1,0,0],
            [0,0,0],
            ]
        # search
        path = AStar(grid).search(self.start, self.goal)
        
        # should be:
        assert path == [(0, 0), (0, 1), (1, 1), (2, 1), (2, 0)]
