from io import StringIO
from antlr4.Utils import escapeWhitespace
from antlr4.tree.Tree import Tree
from antlr4.tree.Trees import Trees
from antlr4.error import ErrorListener

def treeDesc (t: Tree, p, indent=0):
    ruleNames = p.ruleNames
    s = escapeWhitespace(Trees.getNodeText(t, ruleNames), False)
    if t.getChildCount() == 0:
        return s
    with StringIO() as buf:
        buf.write(s + "\n")
        indent += 2
        for i in range(0, t.getChildCount()):
            buf.write(' ' * indent)
            buf.write(treeDesc(t.getChild(i), p, indent) + "\n")
        return buf.getvalue()

def print_tokens (srcfile):
    from antlr4 import FileStream, CommonTokenStream
    from dynamod.parser.DynamodLexer import DynamodLexer

    input = FileStream(srcfile)
    lexer = DynamodLexer(input)
    stream = CommonTokenStream(lexer)
    stream.fill()
    for token in stream.getTokens(0, 9999999):
        print (str(token))

class RegisterErrorListener(ErrorListener.ErrorListener):
    def __init__(self):
        self.had_error = False

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.had_error = True


