

class Tracer:
    def __init__(self):
        self.current = TraceItem(None, None)

    def begin (self, text):
        self.current = self.current.begin (text)

    def line (self, text):
        self.current.begin (text)

    def end (self, res=None):
        self.current = self.current.end (res)

    def finish(self):
        for c in self.current.childs:
            c.print (0)

class TraceItem:
    def __init__(self, father, text):
        self.father = father
        self.text = text
        self.childs = []
        self.res = None

    def begin(self, text):
        sub = TraceItem(self, text)
        self.childs.append(sub)
        return sub

    def end(self, res):
        if res is not None:
            self.res = str(res)
        return self.father

    def print(self, indent):
        if len(self.childs) > 0:
            print ("    " * indent + str(self.text) + ":")
            for c in self.childs:
                c.print(indent + 1)
            if self.res is not None:
                print("    " * indent + self.text + " = " + self.res)
        elif self.res is not None:
            print("    " * indent + self.text + " = " + self.res)
        else:
            print("    " * indent + str(self.text))
