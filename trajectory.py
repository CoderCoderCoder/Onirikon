import random
import numpy

from level import Level
from world import Action

def pos_add(a, b):
    return (a[0]+b[0], a[1]+b[1])

class Trajectory():
    # an array of directions, validate for maximum extend, and for non-crossing
    # direction: 0,1,2,3
    
    offsets = { Action.LEFT : (-1,0), Action.RIGHT: (1,0), Action.UP : (0,-1), Action.DOWN: (0,1)}
    opposites = { Action.LEFT : Action.RIGHT, Action.RIGHT : Action.LEFT, Action.UP : Action.DOWN, Action.DOWN : Action.UP }
    
    def __init__(self, level_width, level_height):
        self.level_width = level_width
        self.level_height = level_height
        self.actions = []
        self.start = (1,1)
        
    def get_traversed_cells(self):
        cells = { self.start }
        pos = self.start
        for action in self.actions:
            offset = self.offsets[action]
            pos = (pos[0] + offset[0], pos[1] + offset[1])
            cells.add(pos)
        return cells

    def get_start(self):
        return self.start
    
    def get_end(self):
        pos = self.start
        for action in self.actions:
            offset = self.offsets[action]
            pos = (pos[0] + offset[0], pos[1] + offset[1])
        return pos

    def get_path(self):
        pos = self.start
        points = [pos]
        for action in self.actions[:-1]:
            offset = self.offsets[action]
            pos = pos_add(pos, offset)
            points.append(pos)
        return points
    
    # visualize trajectory in (empty) level  
    def draw(self):
        level = Level(self.level_width, self.level_height)
        path = self.get_path()
        for point in path:
            level.set(point, 2)
        level.print()
        return

class TrivialTrajectory(Trajectory):
    def __init__(self, level_width, level_height, min_length = None, max_length = None):
        super().__init__(level_width, level_height)

        length_limit = self.level_width-3
        if min_length is None:
            min_length = 1
        if max_length is None:
            max_length = length_limit
            
        max_length = min(max_length, length_limit)

        if min_length > max_length:
            raise ValueError("Max length < min length")
            return

        length = random.randint(min_length, max_length)
        y = random.randint(1, self.level_height-2)
        self.start = (1,y)
        for i in range(length):
            self.actions.append(Action.RIGHT);

class SimpleTrajectory(Trajectory):
    def __init__(self, level_width, level_height):
        super().__init__(level_width, level_height)

        start = (random.randint(1,self.level_width-2), random.randint(1,self.level_height-2))
        end = start
        while start == end:
            end = (random.randint(1,self.level_width-2), random.randint(1,self.level_height-2))

        self.start = start
        x_dir = Action.RIGHT if start[0] < end[0] else Action.LEFT
        for i in range(abs(start[0]-end[0])):
            self.actions.append(x_dir)

        y_dir = Action.DOWN if start[1] < end[1] else Action.UP
        for i in range(abs(start[1]-end[1])):
            self.actions.append(y_dir)
    
class RandomWalkTrajectory(Trajectory):
    def __init__(self, level_width, level_height, max_length = None):
        super().__init__(level_width, level_height)

        if max_length is None:
            max_length = self.level_width + self.level_height

        level = Level(level_width, level_height)
        self.start = (random.randint(1,self.level_width-2), random.randint(1,self.level_height-2))
        self.actions = self.generate_path(level, self.start, max_length)

    def generate_path(self, level, pos, max_length):
        level.set(pos, 4)

        if max_length == 1:
            return []
        else:
            actions = [Action.LEFT, Action.RIGHT, Action.UP, Action.DOWN]
            random.shuffle(actions)
            # try a random move
            for action in actions:
                offset = self.offsets[action]
                next_pos = pos_add(pos, offset)
                # skip if it leads into a wall
                if level.get(next_pos) == 1:
                    continue
                
                # get a list of all neighbors
                neighbors = set(actions) - { self.opposites[action] }
                
                # check all neighbors
                all_clear = True
                for neighbor_action in neighbors:
                    neighbor = pos_add(next_pos, self.offsets[neighbor_action])
                    all_clear &= level.get(neighbor) != 4
                # if all neighbors are good, keep going
                if all_clear:
                    path = self.generate_path(level, next_pos, max_length-1)
                    if path is not None:
                        return [action] + path
            # none of the moves was successful
            level.set(pos, 0)
            return None

#'''
#l = Level(60, 30)
t = RandomWalkTrajectory(60, 30)
#l.generate_from_trajectory(t, 0.1)
t.draw()
#l.print()
#'''