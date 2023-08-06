class NumerousEvent:

    def __init__(self, key, condition, action, compiled, terminal, direction, compiled_functions=None):
        self.key = key
        self.condition = condition
        self.action = action
        self.compiled = compiled
        self.compiled_functions = compiled_functions
        self.direction = direction
        self.terminal = terminal


class TimestampEvent:
    def __init__(self, key, action, timestamps, compiled_functions=None):
        self.key = key
        self.action = action
        self.compiled_functions = compiled_functions
        self.timestamps = timestamps
