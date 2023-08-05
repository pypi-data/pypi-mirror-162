from dynamod.core import *

class Segop:
    def __init__(self, model, seg=None, change=None, share=1, fractions=1):
        self.model = model
        self.n = len(model.attSystem.attributes)
        self.change = [None for att in model.attSystem.attributes] if change is None else change.copy()
        self.seg = tuple(self.change) if seg is None else seg
        self.share = share
        self.fractions = fractions

    def set_value (self, iaxis, ivalue):
        on = self.seg[iaxis]
        if on is None or (listlike(on) and ivalue in on):
            raise EvaluationError("illegal attribute assignament")
        if ivalue != on:
            self.change[iaxis] = ivalue

    def needs_split (self, iaxis, ivalue):
        on = self.seg[iaxis]
        return on is None or (listlike(on) and ivalue in on)

    def has_segment (self, iaxis, ivalue):
        on = self.seg[iaxis]
        if on == ivalue:
            return True
        if on is None or listlike(on):
            raise self.miss (iaxis)
        return False

    def get_value (self, iaxis):
        val = self.seg[iaxis]
        if val is None or listlike(val):
            raise self.miss (iaxis)
        return val

    def miss (self, iaxis):
        if self.model.missing_again:
            return MissingSplit(self.model.attSystem.attributes[iaxis].name)
        else:
            return MissingAxis(self.model.attSystem.attributes[iaxis].name)

    def has_segments (self, iaxis, ivalues):
        on = self.seg[iaxis]
        if on is None:
            raise self.miss(iaxis)
        if singlevar(on):
            return on in ivalues
        sect = set(ivalues) & set(on)
        if len(sect) == 0:
            return False
        if len(sect) == len(ivalues):
            return True
        raise self.miss(iaxis)

    def has_value (self, iaxis, ivalue):
        return self.seg[iaxis] == ivalue

    def modified_by_seg(self, seg):
        return Segop(self.model, seg, self.change, self.share, self.fractions)

    def copy(self):
        return Segop(self.model, self.seg, self.change, self.share, self.fractions)

    def restricted(self, iaxis, value):
        seg = modified_seg(self.seg, iaxis, value)
        return self.modified_by_seg(seg)

    def split_on_prob(self, prob):
        splits = []
        splits.append(Segop(self.model, self.seg, self.change, prob * self.share, self.fractions))
        splits.append(Segop(self.model, self.seg, self.change, (1-prob) * self.share, self.fractions))
        return splits

    def split_on_att(self, iaxis, ivalue):
        splits = []
        on = self.seg[iaxis]
        if on is None:
            splits.append(self.restricted (iaxis, ivalue))
            others = tuple_minus(range(len(self.model.attSystem.attributes[iaxis].values)), ivalue)
            splits.append(self.restricted (iaxis, others))
        elif listlike(on) and ivalue in on:
            splits.append(self.restricted(iaxis, ivalue))
            others = tuple_minus(on, ivalue)
            splits.append(self.restricted(iaxis, others))
        elif singlevar(on) and ivalue == on:
            splits.append(self)
        else:
            splits.append(self.restricted(iaxis, tuple()))
        return splits

    def split_on_attlist(self, iaxis, ivalues):
        splits = []
        on = self.seg[iaxis]
        if on is None:
            splits.append(self.restricted(iaxis, tuple(ivalues)))
            all = range(len(self.model.attSystem.attributes[iaxis].values))
            others = totuple([x for x in all if x not in ivalues])
            splits.append(self.restricted(iaxis, others))
        elif listlike(on):
            these = totuple([x for x in on if x in ivalues])
            others = totuple([x for x in on if x not in ivalues])
            splits.append(self.restricted(iaxis, these))
            if singlevar(others) or len(others) > 0:
                splits.append(self.restricted(iaxis, others))
        else:
            if on in ivalues:
                splits.append(self)
        return splits

    def split_on_axis(self, iaxis):
        splits = []
        on = self.seg[iaxis]
        if on is None:
            all = list(range(len(self.model.attSystem.attributes[iaxis].values)))
        elif listlike(on):
            all = on
        else:
            all = [on]
        for ivalue in all:
            splits.append(self.restricted(iaxis, ivalue))
        return splits

    def split_by_shares(self, iaxis, shares:dict):
        splits = []
        for ivalue, share in shares.items():
            seg = Segop(self.model, self.seg, self.change, share * self.share, self.fractions)
            if seg.needs_split(iaxis, ivalue):
                segs = seg.split_on_axis(iaxis)
                for sseg in segs:
                    sseg.set_value(iaxis, ivalue)
                splits.extend(segs)
            else:
                seg.set_value(iaxis, ivalue)
                splits.append(seg)
        return splits

    #return tuple sout, sin for non-list segments
    def one_apply(self):
        sout = []
        sin = []
        for on, to in zip(self.seg, self.change):
            if on is None:
                sout.append(NOSLICE)
                sin.append(NOSLICE)
            else:
                sout.append(on)
                if to is None:
                    sin.append(on)
                else:
                    sin.append(to)
        return tuple(sout), tuple(sin)

    #return list of tuples sout, sin, split by lists in seg
    def to_apply(self, list_at=None):
        if list_at == None:
            list_at = [i for i in range(self.n) if listlike(self.seg[i]) ]
        if len(list_at) == 0:
            return [self.one_apply()]
        reslist = []
        mylist = list_at.copy()
        iaxis = mylist.pop(0)
        for ivalue in self.seg[iaxis]:
            reslist.extend(self.restricted(iaxis, ivalue).to_apply(mylist))
        return reslist

    def as_key(self):
        return (self.seg, tuple(self.change))

    def __str__(self):
        text = ""
        if self.share != 1:
            text += "for " + str(self.share) + " "
        text += "on " + long_str(self.model, self.seg)
        text += " do " + long_str(self.model, self.change)
        return text

    def get_share(self):
        s = self.share
        if self.fractions > 1:
            s /= self.fractions
        return s

    def share_desc(self):
        from dynamod.partition import Partition
        return self.desc() + ": " + str(Partition(self.model, self).total())

    def desc(self):
        text = ""
        if self.fractions > 1:
            text += "1/" + str(self.fractions) + " fraction of "
        if self.share != 1:
            text += str(self.share) + " of "
        text += long_str(self.model, self.seg)
        return text

    def is_nop(self):
        return self.share == 0 or self.change == self.model.all_none