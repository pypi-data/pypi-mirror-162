import numpy as np

from dynamod.segop import *
from scipy.stats import norm, erlang
import math

class AfterDistribution:

    def get_distribution (model, op:DynamodAfter, segment):
        argvals = [model.evalExpr(arg) for arg in op.args]
        key = (segment, get_line(op.ctx), tuple(argvals))
        if key in model.distributions:
            return model.distributions[key]
        dist = AfterDistribution (model, op, segment)
        model.distributions[key] = dist
        return dist

    def __init__(self, model, op:DynamodAfter, segment):
        self.model = model
        self.dist = op.distrib
        self.segment = reslice(segment)
        self.distmethod = "after_" + op.distrib
        if not hasattr(AfterDistribution, self.distmethod):
            raise ConfigurationError("unknown after-distrbution " + op.distrib, op.ctx)
        self.argvals = [model.evalExpr(arg) for arg in op.args]
        self.timeshares = self.get_timeshares()
        self.total = self.model.matrix[self.segment].sum()
        self.init_sections()
        self.incoming = 0
        self.cache = {}

    def calc_rfactor (self, timeshares):
        r = 0
        for i in range(len(timeshares)):
            r += (i+1) * timeshares[i]
        return 1 / r

    def init_sections(self):
        r = self.calc_rfactor(self.timeshares)
        #build [xn, xn-1+xn, ... x1+x2+...+xn]
        factors = np.cumsum(self.timeshares[::-1])[::-1].tolist()
        self.sections = [r * x for x in factors]
        self.normalize()

    def get_timeshares(self):
        try:
            return getattr(AfterDistribution, self.distmethod)(self.model.fractions, *self.argvals)
        except Exception as e:
            raise ConfigurationError("error invoking distribution " + self.distmethod + ": " + str(e.args))

    def get_share(self):
        return self.sections[0]

    def normalize(self):
        total = sum(self.sections)
        if total != 0:
            self.sections = [s / total for s in self.sections]

    def describe(self):
        return "after." + self.dist

    def distribute (self, sin, sout, transfer, key):
        res = self.get_cached (key)
        if res is None:
            res = leads_into (self.segment, sout, sin)
            self.put_cached (key, res)
        if res:
            self.add_in(transfer)

    def add_in(self, transfer):
        self.incoming += transfer.sum()

    def get_cached(self, key):
        if key in self.cache:
            return self.cache[key]
        return None

    def put_cached(self, key, res):
        self.cache[key] = res

    def tickover (self):    #called after changes are applied to matrix. total is segment size before changes
        y = 0
        if self.incoming > 0:
            y = self.incoming / (self.total * (1 - self.sections[0]) + self.incoming)
        self.sections.pop(0)
        self.sections.append (0)
        for i in range(len(self.timeshares)):
            self.sections[i] += y * self.timeshares[i]
        self.normalize()
        self.total = self.model.matrix[self.segment].sum()
        self.incoming = 0

    @staticmethod
    def after_fix(fractions, delay):
        if delay <= 0:
            raise ValueError("after.fix delay must be positive")
        if delay < 1:
            delay = 1
        delay *= fractions
        len = math.ceil(delay)
        if len > delay:
            timeshares = [0 for i in range(len + 1)]
            timeshares[-2] = len - delay
            rest = 1 + delay - len
            timeshares[-1] = rest
        else:
            timeshares = [0 for i in range(len)]
            timeshares[-1] = 1
        #print ("after fix ", delay, " = ", timeshares)
        return timeshares

    @staticmethod
    def after_explicit(fractions, *args):
        from dynamod.model import normalize_list
        timeshares = normalize_list(args, name="after.explicit attributes")
        if fractions > 1:
            extended = []
            for s in timeshares:
                for _ in range(fractions):
                    extended.append(s/fractions)
            return extended
        return timeshares

    @staticmethod
    def shares_from_cdf (fractions, cdf):
        shares = []
        total = 0
        upper = 1.5/fractions
        lower = None
        while total < 0.999:
            share = cdf(upper)
            if lower is not None:
                share -= cdf(lower)
            total += share
            shares.append (share)
            lower = upper
            upper += 1/fractions
        shares[-1] += 1 - total
        return shares

    @staticmethod
    def after_std (fractions, loc=0, scale=1):
        cdf = norm(loc, scale).cdf
        return AfterDistribution.shares_from_cdf (fractions, cdf)

    @staticmethod
    def after_erlang (fractions, k, lmbda):
        cdf = lambda x: erlang.cdf(x, a=k, scale=1/lmbda)
        return AfterDistribution.shares_from_cdf (fractions, cdf)

