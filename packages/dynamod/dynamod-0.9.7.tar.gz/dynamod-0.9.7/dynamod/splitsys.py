from dynamod.core import *
from dynamod.segop import Segop

class Splitsys:
    def __init__(self, model):
        self.model = model
        self.n = len(model.attSystem.attributes)
        self.share = 1
        self.changes = []
        self.childs = None
        self.childmap = None
        self.axis = None
        self.values = None

    def copy(self):
        cp = Splitsys(self.model)
        cp.share = self.share
        cp.changes = self.changes.copy() if self.changes is not None else None
        cp.childs = self.childs.copy() if self.childs is not None else None
        cp.childmap = self.childmap.copy() if self.childmap is not None else None
        cp.axis = self.axis
        cp.values = self.values.copy() if self.values is not None else None
        return cp

    def set_childs(self, childs):
        n = len(self.model.attSystem.attributes[self.axis].values)
        self.childmap = {}
        for c in childs:
            v = c.values
            if listlike(v):
                if len(v) == 1:
                    v = v[0]
                    n -= 1
                else:
                    v = tuple(v)
                    n -= len(v)
            self.childmap[v] = c
        if n != 0:
            raise ConfigurationError("corrupt split system")
        self.childs = childs

    def add_segop(self, segop):
        if segop.is_nop():
            return
        self.add_for(segop.seg, segop.share, segop.change)

    def add_for(self, seg, share, change):
        if self.childs is None:
            self.apply(seg, share, change)
            return
        on = seg[self.axis]
        rseg = [seg[i] if i != self.axis else None for i in range(self.n)]
        if on is None:
            for sub in self.childs:
                sub.add_for(rseg, share, change)
            return
        if listlike(on) and len(on) == 1:
            on = on[0]
        if on in self.childmap:
            self.childmap[on].add_for(rseg, share, change)
            return
        childs = []
        for sub in self.childs:
            both, rest = sub.split_maybe(on)
            if both is not None:
                childs.append(both)
                both.add_for(rseg, share, change)
            if rest is not None:
                childs.append(rest)
        self.set_childs(childs)

    def split_maybe(self, mask):
        if mask is None:
            return self, None
        if singlevar(mask):
            if mask not in self.values:
                return None, self
            mask = [mask]
        both = [i for i in self.values if i in mask]
        rest = [i for i in self.values if i not in mask]
        if len(rest) == 0:
            return self, None
        if len(both) == 0:
            return None, self
        other = self.copy()
        other.values = rest
        toapply = self.copy()
        toapply.values = both
        return toapply, other

    def apply(self, seg, share, change):
        base = self
        for axis in range(self.n):
            on = seg[axis]
            if on is not None:
                sub = base.copy()
                others = base.copy()
                if singlevar(on):
                    on = [on]
                sub.values = on.copy()
                att = self.model.attSystem.attributes[axis]
                others.values = [i for i in range(len(att.values)) if i not in on]
                base.share = 1
                base.changes = None
                base.axis = axis
                base.set_childs([sub, others])
                base = sub
        for i in range(len(base.changes)):
            (p, pchange) = base.changes[i]
            if change == pchange:
                base.changes[i] = (p+share, pchange)
                return
        base.changes.append((share, change))

    def build_segops(self, onseg=None):
        if onseg is None:
            onseg = Segop(self.model)
        segops = []
        if self.childs is None:
            total = 1
            for (p, pchange) in self.changes:
                total -= p
                myseg = onseg.copy()
                myseg.change = pchange
                myseg.share = p
                segops.append(myseg)
            if total > 0:
                myseg = onseg.copy()
                myseg.change = [None for i in range(self.n)]
                myseg.share = total
                segops.append(myseg)
        else:
            for sub in self.childs:
                on = sub.values
                if len(on) == 1:
                    on = on[0]
                myseg = onseg.restricted(self.axis, on)
                segops.extend(sub.build_segops(myseg))
        return segops



