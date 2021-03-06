from enum import IntEnum
from level import BlockCell, CellType, CheeseCell, EmptyCell, ExitCell, IceCell, StartPositionCell, TornadoCell, WineCell

class Action(IntEnum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3


# Maximum and minimum weight.
MIN_WEIGHT = 1
MAX_WEIGHT = 3

# Starting weight.
INIT_WEIGHT = 2

# Constraints.
MAX_WEIGHT_ON_ICE = 1
MIN_WEIGHT_ON_TORNADO = 3


class World(object):

    def __init__(self, level):
        self.level = level
        self.init_state = None
        self.player_position_idx = None
        self.weight_idx = None
        self.item_idx = {}
        self.tornado = set()
        self.ice = set()
        self.init()

    def get_player_position(self, state):
        return state[self.player_position_idx]

    def get_weight(self, state):
        return state[self.weight_idx]

    def init(self):
        # Initialization: analyze the level to build the initial state.
        # First get the state of stateful cells.
        self.init_state = []
        for pos, cell in self.level.enumerate_cells():
            if cell.has_state():
                self.init_state.append(cell.get_state())
            self.item_idx[pos] = len(self.init_state) - 1

        # Add player position.
        for pos, cell in self.level.enumerate_cells():
            if isinstance(cell, StartPositionCell):
                self.init_state.append(pos)
                self.player_position_idx = len(self.init_state) - 1
            elif isinstance(cell, (BlockCell, EmptyCell, ExitCell, TornadoCell, IceCell)):
                # Ignore.
                pass
            elif isinstance(cell, (WineCell, CheeseCell)):
                pass
            else:
                raise NotImplementedError(type(cell))
        assert self.player_position_idx is not None
        # Add weight.
        self.init_state.append(INIT_WEIGHT)
        self.weight_idx = len(self.init_state) - 1
        self.init_state = tuple(self.init_state)

    def perform(self, state, action):
        """
        Perform `action` in the given `state`.

        :return: The new state if the action was successful, or `None` otherwise.
        """
        x, y = self.get_player_position(state)
        if action == Action.DOWN:
            y += 1
        elif action == Action.UP:
            y -= 1
        elif action == Action.LEFT:
            x -= 1
        elif action == Action.RIGHT:
            x += 1
        else:
            raise NotImplementedError(action)
        target_cell_type = self.level.get((x, y))
        if x < 0 or x >= self.level.width or y < 0 or y >= self.level.height or target_cell_type == CellType.BLOCK:
            # Can't move!
            return None
        current_weight = state[self.weight_idx]
        if target_cell_type == CellType.TORNADO and current_weight < MIN_WEIGHT_ON_TORNADO:
            return None
        if target_cell_type == CellType.ICE and current_weight > MAX_WEIGHT_ON_ICE:
            return None
        new_state = list(state)
        pos = x, y
        new_state[self.player_position_idx] = pos
        if target_cell_type == CellType.WINE and state[self.item_idx[pos]]:
            new_state[self.weight_idx] = max(MIN_WEIGHT, current_weight - 1)
            new_state[self.item_idx[pos]] = False
        elif target_cell_type == CellType.CHEESE and state[self.item_idx[pos]]:
            new_state[self.weight_idx] = min(MAX_WEIGHT, current_weight + 1)
            new_state[self.item_idx[pos]] = False
        return tuple(new_state)

    def validate_trajectory(self, trajectory):
        state = self.init_state
        assert state is not None
        for action in trajectory.actions:
            new_state = self.perform(state, action)
            if new_state is None:
                return False
            else:
                state = new_state
        return True