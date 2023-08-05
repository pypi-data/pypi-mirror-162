from dynamod.core import *
from dynamod.context import *
from dynamod.actionstack import Action
from dynamod.partition import Partition
from dynamod.flexdot import FlexDot

class DynamodExpression:
    def __init__(self, model, ctx, name, expr):
        self.model = model
        self.srcfile = model.srcfile
        self.line = get_line(ctx)
        self.name = name
        self.expr = expr

    def evaluate(self, context:DynaContext):
        with Action(self.model, "evaluate expression " + self.name, line=self.line):
            return Evaluator(context).evalExpr(self.expr)

class DynamodFunction:
    def __init__(self, model, ctx, name, args, expr):
        self.model = model
        self.srcfile = model.srcfile
        self.line = get_line(ctx)
        self.name = name
        self.args = args
        self.expr = expr

    def evaluate(self, params, context:DynaContext):
        with Action(self.model, "evaluate function " + self.name, line=self.line):
            if singlevar(params) or len(params) != len(self.args):
                raise EvaluationError("failed to invoke '" + self.name + "', wrong number of arguments", self.srcfile, self.line)
            localCtx = MapStore()
            for n,v in zip(self.args, params):
                localCtx.put(n, v)
            return Evaluator(context.chained_by(localCtx)).evalExpr(self.expr)

class Evaluator:
    def __init__(self, context:DynaContext):
        self.context = context
        self.model = context.model

    def evalComparison (self, opcode, op1, op2):
        if opcode == '<':
            return op1 < op2
        if opcode == '<=':
            return op1 <= op2;
        if opcode == '>':
            return op1 > op2
        if opcode == '>=':
            return op1 >= op2;
        if opcode == '==':
            return op1 == op2
        if opcode == '!=':
            return op1 != op2;
        raise ConfigurationError("unknown comparison operator: " + opcode)

    def evalCond (self, expr):
        with Action(self.model, "evaluate condition", op=expr):
            if isinstance(expr, UnaryOp):
                if expr.opcode == 'or':
                    for sub in expr.op:
                        if self.evalCond (sub):
                            return True
                    return False
                if expr.opcode == 'and':
                    for sub in expr.op:
                        if not self.evalCond (sub):
                            return False
                    return True
                if expr.opcode == 'not':
                    return not self.evalCond (expr.op)
                raise ConfigurationError("unknown condition operation(1): " + expr.opcode, expr.ctx)

            if isinstance(expr, BinaryOp):
                op1 = self.evalExpr(expr.op1)
                op2 = self.evalExpr(expr.op2)
                if is_num(op1) and is_num(op2):
                    return self.evalComparison (expr.opcode, op1, op2)
                raise ConfigurationError("illegal comparision", expr.ctx)

            if isinstance(expr, TernaryOp):
                if expr.opcode == 'between':
                    val = self.evalExpr(expr.op1)
                    limFrom = self.evalExpr(expr.op2)
                    limTo = self.evalExpr(expr.op3)
                    if is_num(val) and is_num(limFrom) and is_num(limTo):
                        return self.evalComparison('>=', val, limFrom) and self.evalComparison('<=', val, limTo)
                    raise ConfigurationError("illegal comparision", expr.ctx)
                raise ConfigurationError("unknown condition operation(3): " + expr.opcode, expr.ctx)

            raise ConfigurationError("unknown condition rule:" + str(expr))

    def evalExpr (self, expr):
        if isinstance(expr, int) or isinstance(expr, float) or isinstance(expr, str):
            return expr

        with Action(self.model, "evaluate expression", op=expr):
            if isinstance(expr, UnaryOp):
                if expr.opcode == 'var':
                    if self.context.values.knows (expr.op):
                        return self.context.values.get (expr.op)
                    raise ConfigurationError("unknown variable: " + expr.op, expr.ctx)
                if expr.opcode == 'list':
                    return [self.evalExpr(x) for x in expr.op]
                if expr.opcode == 'date':
                    return get_date_day(expr.op, self.model.startDate, expr.ctx)
                raise ConfigurationError("unknown expression type(1): " + expr.opcode, expr.ctx)

            if isinstance(expr, BinaryOp):
                if expr.opcode in ['+', '-', '*', '/', '**']:
                    if self.model.tracer is not None:
                        self.model.tracer.begin({'+':'add', '-':'subtract', '*':'multiply', '/':'divide', '**':'exp'}[expr.opcode])
                    op1 = self.evalExpr(expr.op1)
                    op2 = self.evalExpr(expr.op2)
                    if is_num(op1) and is_num(op2):
                        res = evalCalculation (expr.opcode, op1, op2)
                        if self.model.tracer is not None:
                            self.model.tracer.end(str(op1) + " " + expr.opcode + " " + str(op2) + " = " + str(res))
                        return res
                    if isinstance(op1, str) or isinstance(op2, str):
                        if self.model.tracer is not None:
                            self.model.tracer.end(str(op1) + " " + expr.opcode + " " + str(op2) + " = " + str(res))
                        return str(op1) + str(op2)
                    raise ConfigurationError("illegal calculation operands: " + str(op1) + expr.opcode + str(op2), expr.ctx)
                if expr.opcode == 'func':
                    args = []
                    if expr.op2 is not None:
                        for op in expr.op2:
                            args.append(self.evalExpr(op))
                    return self.model.invokeFunc (expr.op1, args)
                if expr.opcode == 'dot':
                    op1 = self.evalExpr(expr.op1)
                    if isinstance(op1, Partition):
                        att = self.model.attribute(expr.op2)
                        return op1.onseg.get_value(att.index)
                    if isinstance(op1, FlexDot):
                        return op1.get(expr.op2)
                    if hasattr(op1, expr.op2):
                        return getattr(op1, expr.op2)
                    raise ConfigurationError("unknown field " + expr.op2, expr.ctx)
                if expr.opcode == 'index':
                    op1 = self.evalExpr(expr.op1)
                    op2 = self.evalExpr(expr.op2)
                    return op1[op2]
                if expr.opcode == 'with':
                    if expr.op1 is None:
                        if self.context.values.knows('_SHARE_BASE'):
                            part = self.context.values.get('_SHARE_BASE')
                        else:
                            part = self.model.full_partition()
                    else:
                        part = self.evalExpr(expr.op1)
                        if not isinstance(part, Partition):
                            raise ConfigurationError("base of with-operator must be a partition", expr.ctx)
                    axval = expr.op2
                    if listlike(axval.value):
                        value = [self.evalExpr(v) for v in axval.value]
                    else:
                        value = self.evalExpr(axval.value)
                    return part.restricted(axval.axis, value)
                if expr.opcode == 'share':
                    if expr.op2 is not None:
                        base = self.evalExpr(expr.op2)
                        if not isinstance(base, Partition):
                            raise ConfigurationError("base of $(...|...) must be a partition", expr.ctx)
                        self.context.values.put('_SHARE_BASE', base)
                    part = self.evalExpr(expr.op1)
                    if not isinstance(part, Partition):
                        raise ConfigurationError("expression in $(...) must be a partition", expr.ctx)
                    if expr.op2 is not None:
                        self.context.values.delete('_SHARE_BASE')
                    share = part.total()
                    if share > 0 and expr.op2 is not None:
                        share /= base.total()
                    return share
                if expr.opcode == 'split':
                    part = self.evalExpr(expr.op1)
                    if not isinstance(part, Partition):
                        raise ConfigurationError("'by' operator can only be applied to partisions", expr.ctx)
                    return part.splitter(expr.op2)

                raise ConfigurationError("unknown expression operation(2): " + expr.opcode, expr.ctx)

            if isinstance(expr, TernaryOp):
                if expr.opcode == 'method':
                    args = []
                    if expr.op3 is not None:
                        for op in expr.op3:
                            args.append(self.evalExpr(op))
                    obj = self.evalExpr(expr.op1)
                    methodname = expr.op2
                    if hasattr(obj, methodname):
                        method = getattr(obj, methodname)
                        if callable(method):
                            return method(*args)
                    raise ConfigurationError("unknown method '" + methodname + "' on " + str(obj), expr.ctx)
                if expr.opcode == 'if':
                    if self.evalCond(expr.op1):
                        return self.evalExpr(expr.op2)
                    elif expr.op3 is not None:
                        return self.evalExpr(expr.op3)
                    else:
                        return None

                raise ConfigurationError("unknown expression operation(3): " + expr.opcode, expr.ctx)

            if isinstance(expr, DynamodElseList):
                return self.eval_restrictions(expr)

            if isinstance(expr, DynamodExpression):
                return self.evalExpr(expr.expr)

            raise ConfigurationError("unknown expression rule: " + str(expr))

    def eval_restrictions (self, op:DynamodElseList):
        with Action(self.model, "evaluate conditional expression", op=op):
            for cond_expr in op.list:
                if cond_expr.type == 'if':
                    if self.evalCond(cond_expr.cond):
                        return self.evalExpr (cond_expr.expr)
                elif isinstance(cond_expr, DynamodCondExp):
                    axis = cond_expr.cond.axis
                    att = self.model.attribute(axis)
                    value = cond_expr.cond.value
                    if listlike(value):
                        values = [att.indexof(self.evalExpr(v)) for v in value]
                        if self.context.onseg.has_segments(att.index, values):
                            return self.evalExpr (cond_expr.expr)
                    else:
                        value = self.evalExpr(value)
                        if self.context.onseg.has_segment(att.index, att.indexof(value)):
                            return self.evalExpr(cond_expr.expr)
                else:
                    raise EvaluationError("illegal conditional expression" + str(cond_expr.cond))

            if op.otherwise is None:
                raise EvaluationError("missing 'otherwise' clause")
            return self.evalExpr(op.otherwise)

def evalExpression (expr, context):
    return Evaluator(context).evalExpr(expr)

def evalCondition (expr, context):
    return Evaluator(context).evalCond(expr)

