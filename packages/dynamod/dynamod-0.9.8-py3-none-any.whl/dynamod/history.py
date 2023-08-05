from dynamod.segop import *
import pandas as pd
import datetime

class History:
    def __init__(self, model, flexCycle, flexGlobal):
        self.model = model
        self.matrix = []    #matrix[0]= start of calculation, matrix[1]= result after tick 0
        self.cycles = []    #cycles[0] = cycle vars after tick 0
        flexCycle.historic = self.cycles
        self.globals = []    #global[0] = global vars after tick 0
        flexGlobal.historic = self.globals
        self.results = {}
        for name in self.model.results:
            self.results[name] = []

    def store(self):
        self.matrix.append(self.model.matrix.copy())
        for name, expr in self.model.results.items():
            self.results[name].append (self.model.evalExpr(expr, Segop(self.model)))
        if len(self.matrix) > 0:
            self.cycles.append(self.model.flexCycle.copy())
            self.globals.append(self.model.flexGlobal.copy())

    def get_attribute(self, axis, value, start=None, stop=None):
        segment = axval_segment(self.model, axis, value)
        return [m[segment].sum() for m in self.matrix[slice(start,stop,None)]]

    def get_attributes(self, axis, start=None, stop=None):
        att = self.model.attSystem.attr_map[axis]
        axl = axis_exclude(self.model, axis)
        data = [m.sum(axis=axl) for m in self.matrix[slice(start,stop,None)]]
        return self.datify(pd.DataFrame(data, columns=att.values), start)

    def get_result(self, name, start=None, stop=None):
        pair = name.split('=')
        if len(pair) == 2:
            return self.get_attribute(pair[0], pair[1], start, stop)
        return self.results[name][slice(start,stop,None)]

    def get_results(self, names, start=None, stop=None):
        data = {name:(self.get_result(name, start, stop)) for name in names}
        return self.datify(pd.DataFrame(data), start)

    def get_all_results(self, start=None, stop=None):
        data = {name:(hist[slice(start,stop,None)]) for (name,hist) in self.results.items()}
        return self.datify(pd.DataFrame(data), start)

    def datify(self, df, start=None):
        if self.model.startDate is None:
            return df
        t0 = self.model.startDate
        if start != None:
            t0 += datetime.timedelta(days=start)
        df.index = pd.date_range(t0, periods=len(df), freq='D')
        return df
