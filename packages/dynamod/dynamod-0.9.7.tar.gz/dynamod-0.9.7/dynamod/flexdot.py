from dynamod.core import ConfigurationError

class FlexDot:
    def __init__(self, model):
        self.model = model
        self.data = {}
        self.historic = None

    def clear(self):
        self.data = {}

    def get(self, key):
        if key in self.data:
            return self.data[key]
        return 0

    def put(self, key, value):
        self.data[key] = value

    def copy(self):
        cp = FlexDot(self.model)
        cp.data = self.data.copy()
        return cp

    def before(self, t):
        if not isinstance(t, int):
            raise ConfigurationError("argument of .before() must be int")
        return self.of(self.model.tick - t)

    def of(self, t):
        if not isinstance(t, int):
            raise ConfigurationError("argument of .of() must be int")
        if self.historic is None:
            raise ConfigurationError(".before()/.of() not supported for this object")
        if t < 0:
            return FlexDot(self.model)    #empty values
        if t > self.model.tick:
            raise ConfigurationError(".before()/.of() accesses future values")
        if t == self.model.tick:
            return self
        return self.historic[t]
