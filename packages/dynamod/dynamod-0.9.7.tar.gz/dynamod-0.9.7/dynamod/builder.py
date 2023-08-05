from dynamod.parser.DynamodVisitor import DynamodVisitor
from dynamod.parser.DynamodParser import DynamodParser
from antlr4 import ParserRuleContext
from dynamod.core import *

def check_statements (statements):
    had_for = False
    had_after = False
    first_split = None
    nr = 0
    for op in statements:
        if isinstance(op, DynamodElseList):
            if had_for:
                raise ConfigurationError("only one 'for..otherwise' section allowed per block", op.ctx)
            if had_after:
                raise ConfigurationError("can't combine 'after' and 'for..otherwise' in same block", op.ctx)
            had_for = True
            first_split = nr
        elif isinstance(op, DynamodAfter):
            if had_after:
                raise ConfigurationError("only one 'after' section allowed per block", op.ctx)
            if had_for:
                raise ConfigurationError("can't combine 'after' and 'for..otherwise' in same block", op.ctx)
            had_after = True
            first_split = nr
        elif False:
            if had_for or had_after:
                #move this item on top and repeat
                item = statements.pop(nr)
                statements.insert(first_split, item)
                check_statements(statements)
                return
        nr += 1

def unwrap (text):
    return text[1:-1]

def combine_list (first, second):
    reslist = []
    reslist.append(first)
    if second is None:
        return reslist
    if listlike(second):
        reslist.extend(second)
    elif second is not None:
        reslist.append(second)
    return reslist

def combine_map (first, second):
    resmap = {}
    resmap[first[0]] = first[1]
    if isinstance(second, dict):
        resmap.update(second)
    elif second is not None:
        resmap[second[0]] = second[1]
    return resmap

def to_dict (item):
    if item is None:
        return None
    if isinstance(item, tuple):
        return {item[0]: item[1]}
    if isinstance(item, list):
        map = {}
        for entry in item:
            map[entry[0]] = entry[1]
        return map
    if isinstance(item, dict):
        return item
    raise ValueError("to_dict() called on " + type(item))

def to_number (txt):
    try:
        return int(txt)
    except ValueError:
        return float(txt)

class DynamodBuilder(DynamodVisitor):
    def __init__(self, model):
        self.model = model

    def visit (self, ctx:ParserRuleContext):
        return ctx.accept(self) if ctx is not None else None

    # Visit a parse tree produced by DynamodParser#model.
    def visitModel(self, ctx:DynamodParser.ModelContext):
        self.visit(ctx.model_part())
        self.visit(ctx.model())

    # Visit a parse tree produced by DynamodParser#model_inc.
    def visitModel_inc(self, ctx:DynamodParser.Model_incContext):
        self.model.include (unwrap(ctx.STRING().getText()))

    # Visit a parse tree produced by DynamodParser#model_settings.
    def visitModel_settings(self, ctx:DynamodParser.Model_settingsContext):
        return self.visit(ctx.settings())

    # Visit a parse tree produced by DynamodParser#model_pars.
    def visitModel_pars(self, ctx:DynamodParser.Model_parsContext):
        return self.visit(ctx.parameters())

    # Visit a parse tree produced by DynamodParser#model_props.
    def visitModel_attribs(self, ctx:DynamodParser.Model_attribsContext):
        return self.visit(ctx.attributes())

    # Visit a parse tree produced by DynamodParser#model_formulas.
    def visitModel_formulas(self, ctx:DynamodParser.Model_formulasContext):
        return self.visit(ctx.formulas())

    # Visit a parse tree produced by DynamodParser#model_progressions.
    def visitModel_progressions(self, ctx:DynamodParser.Model_progressionsContext):
        return self.visit(ctx.progressions())

    # Visit a parse tree produced by DynamodParser#model_results.
    def visitModel_results(self, ctx:DynamodParser.Model_resultsContext):
        return self.visit(ctx.results())

    # Visit a parse tree produced by DynamodParser#settings.
    def visitSettings(self, ctx:DynamodParser.SettingsContext):
        self.visit(ctx.setting())
        self.visit(ctx.settings())

    # Visit a parse tree produced by DynamodParser#setting_expr.
    def visitSetting_expr(self, ctx:DynamodParser.Setting_exprContext):
        self.model.addSetting (ctx, ctx.NAME().getText(), self.visit(ctx.expression()))


    # Visit a parse tree produced by DynamodParser#setting_extends.
    def visitSetting_extends(self, ctx:DynamodParser.Setting_extendsContext):
        self.model.addSetting (ctx, 'extends', unwrap(ctx.STRING().getText()))

    # Visit a parse tree produced by DynamodParser#parameters.
    def visitParameters(self, ctx:DynamodParser.ParametersContext):
        self.visit(ctx.parameter())
        self.visit(ctx.parameters())

    # Visit a parse tree produced by DynamodParser#parameter.
    def visitParameter(self, ctx:DynamodParser.ParameterContext):
        self.model.addParameter (ctx, ctx.NAME().getText(), self.visit(ctx.expression()))

    # Visit a parse tree produced by DynamodParser#attributes.
    def visitAttributes(self, ctx:DynamodParser.AttributesContext):
        self.visit(ctx.attribute())
        self.visit(ctx.attributes())

    # Visit a parse tree produced by DynamodParser#attribute.
    def visitAttribute(self, ctx:DynamodParser.AttributeContext):
        self.model.addAttribute(ctx, ctx.NAME().getText(), self.visit(ctx.attribute_block()))

    # Visit a parse tree produced by DynamodParser#attribute_block.
    def visitAttribute_block(self, ctx:DynamodParser.Attribute_blockContext):
        return DynamodAttrib(self.visit(ctx.values()), self.visit(ctx.shares()))

    # Visit a parse tree produced by DynamodParser#shares_as_list.
    def visitShares_as_list(self, ctx:DynamodParser.Shares_as_listContext):
        return self.visit(ctx.expression_list())

    # Visit a parse tree produced by DynamodParser#shares_as_map.
    def visitShares_as_map(self, ctx:DynamodParser.Shares_as_mapContext):
        return self.visit(ctx.share_map_block())

    # Visit a parse tree produced by DynamodParser#shares_as_cond.
    def visitShares_as_cond(self, ctx:DynamodParser.Shares_as_condContext):
        return self.visit(ctx.cond_shares_block())

    # Visit a parse tree produced by DynamodParser#share_map_block.
    def visitShare_map_block(self, ctx:DynamodParser.Share_map_blockContext):
        return self.visit(ctx.share_map())

    # Visit a parse tree produced by DynamodParser#share_map.
    def visitShare_map(self, ctx:DynamodParser.Share_mapContext):
        return combine_map(self.visit(ctx.share_def()), self.visit(ctx.share_map()))

    # Visit a parse tree produced by DynamodParser#share_def.
    def visitShare_def(self, ctx:DynamodParser.Share_defContext):
        return (ctx.NAME().getText(), self.visit(ctx.pexpression()))

    # Visit a parse tree produced by DynamodParser#cond_shares_block.
    def visitCond_shares_block(self, ctx:DynamodParser.Cond_shares_blockContext):
        return DynamodElseList(ctx, self.visit(ctx.cond_shares()), self.visit(ctx.shares()))


    # Visit a parse tree produced by DynamodParser#cond_shares.
    def visitCond_shares(self, ctx:DynamodParser.Cond_sharesContext):
        return combine_list(self.visit(ctx.cond_share()), self.visit(ctx.cond_shares()))

    # Visit a parse tree produced by DynamodParser#cond_share.
    def visitCond_share(self, ctx:DynamodParser.Cond_shareContext):
        return (self.visit(ctx.segment()), self.visit(ctx.shares()))

    # Visit a parse tree produced by DynamodParser#pexpr_as_simple.
    def visitPexpr_as_simple(self, ctx:DynamodParser.Pexpr_as_simpleContext):
        return self.visit(ctx.expression())

    # Visit a parse tree produced by DynamodParser#pexpr_as_block.
    def visitPexpr_as_block(self, ctx:DynamodParser.Pexpr_as_blockContext):
        return self.visit(ctx.pexpression_block())

    # Visit a parse tree produced by DynamodParser#pexpression_block.
    def visitPexpression_block(self, ctx:DynamodParser.Pexpression_blockContext):
        return DynamodElseList(ctx, self.visit(ctx.pexp_list()), self.visit(ctx.pexpression()))

    # Visit a parse tree produced by DynamodParser#pexp_list.
    def visitPexp_list(self, ctx:DynamodParser.Pexp_listContext):
        return combine_list(self.visit(ctx.pexp_item()), self.visit(ctx.pexp_list()))

    # Visit a parse tree produced by DynamodParser#pexp_item.
    def visitPexp_for(self, ctx:DynamodParser.Pexp_forContext):
        return DynamodCondExp(ctx, 'for', self.visit(ctx.segment()), self.visit(ctx.pexpression()))

    # Visit a parse tree produced by DynamodParser#pexp_if.
    def visitPexp_if(self, ctx:DynamodParser.Pexp_ifContext):
        return DynamodCondExp(ctx, 'if', self.visit(ctx.condition()), self.visit(ctx.pexpression()))

    # Visit a parse tree produced by DynamodParser#seg_as_axval.
    def visitSeg_as_axval(self, ctx:DynamodParser.Seg_as_axvalContext):
        return DynamodAxisValue(ctx, ctx.axis.text, ctx.value.text)

    # Visit a parse tree produced by DynamodParser#seg_as_eq.
    def visitSeg_as_eq(self, ctx:DynamodParser.Seg_as_eqContext):
        return DynamodAxisValue(ctx, ctx.NAME().getText(), self.visit(ctx.expression()))

    # Visit a parse tree produced by DynamodParser#seg_as_in.
    def visitSeg_as_in(self, ctx:DynamodParser.Seg_as_inContext):
        return DynamodAxisValue(ctx, ctx.NAME().getText(), self.visit(ctx.values()))

    # Visit a parse tree produced by DynamodParser#values.
    def visitValues(self, ctx:DynamodParser.ValuesContext):
        list = []
        for entry in ctx.vals:
            list.append(entry.text)
        return list

    # Visit a parse tree produced by DynamodParser#expression_list.
    def visitExpression_list(self, ctx:DynamodParser.Expression_listContext):
        list = []
        for entry in ctx.exprs:
            list.append(self.visit(entry))
        return list

    # Visit a parse tree produced by DynamodParser#progressions.
    def visitProgressions(self, ctx:DynamodParser.ProgressionsContext):
        self.visit(ctx.progression())
        self.visit(ctx.progressions())

    # Visit a parse tree produced by DynamodParser#progression.
    def visitProgression(self, ctx:DynamodParser.ProgressionContext):
        self.model.addProgression(ctx, ctx.name.text, self.visit(ctx.progression_block()), ctx.before.text if ctx.before is not None else None)

    # Visit a parse tree produced by DynamodParser#progression_block.
    def visitProgression_block(self, ctx:DynamodParser.Progression_blockContext):
        statements = self.visit(ctx.progression_statements())
        check_statements(statements)
        return statements

    # Visit a parse tree produced by DynamodParser#progression_statements.
    def visitProgression_statements(self, ctx:DynamodParser.Progression_statementsContext):
        return combine_list (self.visit(ctx.progression_statement()), self.visit(ctx.progression_statements()))

    # Visit a parse tree produced by DynamodParser#prog_vardef.
    def visitProg_vardef(self, ctx:DynamodParser.Prog_vardefContext):
        return self.visit(ctx.variable_definition())

    # Visit a parse tree produced by DynamodParser#prog_restrictions.
    def visitProg_restrictions(self, ctx:DynamodParser.Prog_restrictionsContext):
        list = []
        for r in ctx.restr:
            list.append(self.visit(r))
        return DynamodElseList(ctx, list, self.visit(ctx.progression_block()))

    # Visit a parse tree produced by DynamodParser#prog_after.
    def visitProg_after(self, ctx:DynamodParser.Prog_afterContext):
        return self.visit(ctx.progression_after())

    # Visit a parse tree produced by DynamodParser#prog_iter.
    def visitProg_iter(self, ctx:DynamodParser.Prog_iterContext):
        return self.visit(ctx.progression_iteration())

    # Visit a parse tree produced by DynamodParser#prog_action.
    def visitProg_action(self, ctx:DynamodParser.Prog_actionContext):
        return self.visit(ctx.progression_action())

    # Visit a parse tree produced by DynamodParser#prog_expr.
    def visitProg_expr(self, ctx:DynamodParser.Prog_exprContext):
        return DynamodVarDef(ctx, None, None, None, self.visit(ctx.expression()))

    # Visit a parse tree produced by DynamodParser#restr_for.
    def visitRestr_for(self, ctx:DynamodParser.Restr_forContext):
        res = DynamodRestriction(ctx, 'for', self.visit(ctx.segment()), self.visit(ctx.progression_block()))
        if ctx.NAME() is not None:
            res.alias = ctx.NAME().getText()
        return res

    # Visit a parse tree produced by DynamodParser#restr_prob.
    def visitRestr_prob(self, ctx:DynamodParser.Restr_probContext):
        res = DynamodRestriction(ctx, 'for', self.visit(ctx.expression()), self.visit(ctx.progression_block()))
        if ctx.NAME() is not None:
            res.alias = ctx.NAME().getText()
        return res

    # Visit a parse tree produced by DynamodParser#restr_if.
    def visitRestr_if(self, ctx:DynamodParser.Restr_ifContext):
        return DynamodRestriction(ctx, 'if', self.visit(ctx.condition()), self.visit(ctx.progression_block()))


    # Visit a parse tree produced by DynamodParser#progression_after.
    def visitProgression_after(self, ctx:DynamodParser.Progression_afterContext):
        return DynamodAfter(ctx, ctx.NAME().getText(), self.visit(ctx.arguments()), self.visit(ctx.progression_block()), get_random_string(8))

    # Visit a parse tree produced by DynamodParser#progression_iteration.
    def visitProgression_iteration(self, ctx:DynamodParser.Progression_iterationContext):
        return DynamodIteration(ctx, ctx.NAME().getText(), self.visit(ctx.expression()), self.visit(ctx.progression_block()))

    # Visit a parse tree produced by DynamodParser#progression_action.
    def visitProgression_action(self, ctx:DynamodParser.Progression_actionContext):
        return DynamodAction(ctx, ctx.NAME().getText(), self.visit(ctx.pstate()))

    # Visit a parse tree produced by DynamodParser#pstate_name.
    def visitPstate_name(self, ctx:DynamodParser.Pstate_nameContext):
        return ctx.NAME().getText()

    # Visit a parse tree produced by DynamodParser#pstate_dot.
    def visitPstate_dot(self, ctx:DynamodParser.Pstate_dotContext):
        return BinaryOp(ctx, 'dot', self.visit(ctx.primary()), ctx.NAME().getText())

    # Visit a parse tree produced by DynamodParser#pstate_block.
    def visitPstate_block(self, ctx:DynamodParser.Pstate_blockContext):
        return self.visit(ctx.share_map_block())

    # Visit a parse tree produced by DynamodParser#results.
    def visitResults(self, ctx:DynamodParser.ResultsContext):
        self.visit(ctx.result())
        self.visit(ctx.results())

    # Visit a parse tree produced by DynamodParser#result.
    def visitResult(self, ctx:DynamodParser.ResultContext):
        self.model.addResult(ctx, ctx.NAME().getText(), self.visit(ctx.expression()))

    # Visit a parse tree produced by DynamodParser#formulas.
    def visitFormulas(self, ctx:DynamodParser.FormulasContext):
        self.visit(ctx.formula())
        self.visit(ctx.formulas())

    # Visit a parse tree produced by DynamodParser#formula_expr.
    def visitFormula_expr(self, ctx:DynamodParser.Formula_exprContext):
        self.model.addFormula(ctx, ctx.NAME().getText(), self.visit(ctx.pexpression()))

    # Visit a parse tree produced by DynamodParser#formula_func.
    def visitFormula_func(self, ctx:DynamodParser.Formula_funcContext):
        self.model.addFunc(ctx, ctx.NAME().getText(), self.visit(ctx.formal_args()), self.visit(ctx.pexpression()))

    # Visit a parse tree produced by DynamodParser#formal_args.
    def visitFormal_args(self, ctx:DynamodParser.Formal_argsContext):
        list = []
        for entry in ctx.args:
            list.append (entry.text)
        return list

    # Visit a parse tree produced by DynamodParser#vardef_simple.
    def visitVardef_simple(self, ctx:DynamodParser.Vardef_simpleContext):
        return DynamodVarDef(ctx, ctx.NAME().getText(), None, ctx.op.text, self.visit(ctx.pexpression()))

    # Visit a parse tree produced by DynamodParser#vardef_dot.
    def visitVardef_dot(self, ctx:DynamodParser.Vardef_dotContext):
        return DynamodVarDef(ctx, ctx.base.text, ctx.key.text, ctx.op.text, self.visit(ctx.pexpression()))


    # Visit a parse tree produced by DynamodParser#expr_ifelse.
    def visitExpr_ifelse(self, ctx:DynamodParser.Expr_ifelseContext):
        return TernaryOp(ctx, 'if', self.visit(ctx.condition()), self.visit(ctx.expval()), self.visit(ctx.expression()))

    # Visit a parse tree produced by DynamodParser#expr_value.
    def visitExpr_value(self, ctx:DynamodParser.Expr_valueContext):
        return self.visit(ctx.expval())

    # Visit a parse tree produced by DynamodParser#disj_ors.
    def visitDisj_ors(self, ctx:DynamodParser.Disj_orsContext):
        list = []
        for c in ctx.conds:
            list.append (self.visit(c))
        return UnaryOp(ctx, 'or', list)

    # Visit a parse tree produced by DynamodParser#disj_one.
    def visitDisj_one(self, ctx:DynamodParser.Disj_oneContext):
        return self.visit(ctx.conjunction())

    # Visit a parse tree produced by DynamodParser#conj_ands.
    def visitConj_ands(self, ctx:DynamodParser.Conj_andsContext):
        list = []
        for c in ctx.conds:
            list.append (self.visit(c))
        return UnaryOp(ctx, 'and', list)

    # Visit a parse tree produced by DynamodParser#conj_comp.
    def visitConj_comp(self, ctx:DynamodParser.Conj_compContext):
        return self.visit(ctx.comparison())

    # Visit a parse tree produced by DynamodParser#comp_two_ops.
    def visitComp_two_ops(self, ctx:DynamodParser.Comp_two_opsContext):
        return BinaryOp(ctx, ctx.op.text, self.visit(ctx.op1), self.visit(ctx.op2))

    # Visit a parse tree produced by DynamodParser#comp_not.
    def visitComp_not(self, ctx:DynamodParser.Comp_notContext):
        return UnaryOp(ctx, 'not', self.visit(ctx.comparison()))

    # Visit a parse tree produced by DynamodParser#comp_interval.
    def visitComp_interval(self, ctx:DynamodParser.Comp_intervalContext):
        return TernaryOp(ctx, 'between', self.visit(ctx.expval()), self.visit(ctx.op1), self.visit(ctx.op2))

    # Visit a parse tree produced by DynamodParser#exp_term.
    def visitExpval_term(self, ctx:DynamodParser.Expval_termContext):
        return self.visit(ctx.term())

    # Visit a parse tree produced by DynamodParser#exp_sub.
    def visitExpval_sub(self, ctx:DynamodParser.Expval_subContext):
        return BinaryOp(ctx, '-', self.visit(ctx.expval()), self.visit(ctx.term()))

    # Visit a parse tree produced by DynamodParser#exp_add.
    def visitExpval_add(self, ctx:DynamodParser.Expval_addContext):
        return BinaryOp(ctx, '+', self.visit(ctx.expval()), self.visit(ctx.term()))

    # Visit a parse tree produced by DynamodParser#term_mul.
    def visitTerm_mul(self, ctx:DynamodParser.Term_mulContext):
        return BinaryOp(ctx, '*', self.visit(ctx.term()), self.visit(ctx.factor()))

    # Visit a parse tree produced by DynamodParser#term_exp.
    def visitTerm_exp(self, ctx:DynamodParser.Term_expContext):
        return BinaryOp(ctx, '**', self.visit(ctx.term()), self.visit(ctx.factor()))

    # Visit a parse tree produced by DynamodParser#term_factor.
    def visitTerm_factor(self, ctx:DynamodParser.Term_factorContext):
        return self.visit(ctx.factor())

    # Visit a parse tree produced by DynamodParser#term_div.
    def visitTerm_div(self, ctx:DynamodParser.Term_divContext):
        return BinaryOp(ctx, '/', self.visit(ctx.term()), self.visit(ctx.factor()))

    # Visit a parse tree produced by DynamodParser#factor_pos.
    def visitFactor_pos(self, ctx:DynamodParser.Factor_posContext):
        return self.visit(ctx.factor())

    # Visit a parse tree produced by DynamodParser#factor_neg.
    def visitFactor_neg(self, ctx:DynamodParser.Factor_negContext):
        return BinaryOp(ctx, '-', 0, self.visit(ctx.factor()))

    # Visit a parse tree produced by DynamodParser#factor_primary.
    def visitFactor_primary(self, ctx:DynamodParser.Factor_primaryContext):
        return self.visit(ctx.primary())

    # Visit a parse tree produced by DynamodParser#factor_expr.
    def visitFactor_expr(self, ctx:DynamodParser.Factor_exprContext):
        return self.visit(ctx.expression())

    # Visit a parse tree produced by DynamodParser#factor_number.
    def visitFactor_number(self, ctx:DynamodParser.Factor_numberContext):
        try:
            return to_number(ctx.NUMBER().getText())
        except ValueError:
            raise ConfigurationError("illegal number format: " + ctx.NUMBER().getText(), ctx.NUMBER())

    # Visit a parse tree produced by DynamodParser#factor_date.
    def visitFactor_date(self, ctx:DynamodParser.Factor_dateContext):
        return UnaryOp(ctx, 'date', ctx.DATE().getText())

    # Visit a parse tree produced by DynamodParser#factor_percent.
    def visitFactor_percent(self, ctx:DynamodParser.Factor_percentContext):
        try:
            return to_number(ctx.NUMBER().getText()) / 100
        except ValueError:
            raise ConfigurationError("illegal number format: " + ctx.NUMBER().getText(), ctx.NUMBER())

    # Visit a parse tree produced by DynamodParser#factor_rest.
    def visitFactor_rest(self, ctx:DynamodParser.Factor_restContext):
        return -1

    # Visit a parse tree produced by DynamodParser#primary_func.
    def visitPrimary_func(self, ctx:DynamodParser.Primary_funcContext):
        return BinaryOp(ctx, 'func', ctx.NAME().getText(), self.visit(ctx.arguments()))

    # Visit a parse tree produced by DynamodParser#primary_method.
    def visitPrimary_method(self, ctx:DynamodParser.Primary_methodContext):
        return TernaryOp(ctx, 'method', self.visit(ctx.primary()), ctx.NAME().getText(), self.visit(ctx.arguments()))

    # Visit a parse tree produced by DynamodParser#primary_dot.
    def visitPrimary_dot(self, ctx:DynamodParser.Primary_dotContext):
        return BinaryOp(ctx, 'dot', self.visit(ctx.primary()), ctx.NAME().getText())

    # Visit a parse tree produced by DynamodParser#primary_list.
    def visitPrimary_list(self, ctx:DynamodParser.Primary_listContext):
        return UnaryOp(ctx, 'list', self.visit(ctx.arguments()))

    # Visit a parse tree produced by DynamodParser#primary_indexed.
    def visitPrimary_indexed(self, ctx:DynamodParser.Primary_indexedContext):
        return BinaryOp(ctx, 'index', self.visit(ctx.primary()), self.visit(ctx.expression()))

    # Visit a parse tree produced by DynamodParser#primary_name.
    def visitPrimary_name(self, ctx:DynamodParser.Primary_nameContext):
        return UnaryOp(ctx, 'var', ctx.NAME().getText())

    # Visit a parse tree produced by DynamodParser#primary_string.
    def visitPrimary_string(self, ctx:DynamodParser.Primary_stringContext):
        return unwrap(ctx.STRING().getText())

    # Visit a parse tree produced by DynamodParser#primary_partition.
    def visitPrimary_partition(self, ctx:DynamodParser.Primary_partitionContext):
        return self.visit(ctx.partition())

    # Visit a parse tree produced by DynamodParser#primary_partition_split.
    def visitPrimary_partition_split(self, ctx:DynamodParser.Primary_partition_splitContext):
        return BinaryOp(ctx, 'split', self.visit(ctx.partition()), [ctx.NAME().getText()])

    # Visit a parse tree produced by DynamodParser#primary_partition_splits.
    def visitPrimary_partition_splits(self, ctx:DynamodParser.Primary_partition_splitsContext):
        return BinaryOp(ctx, 'split', self.visit(ctx.partition()), self.visit(ctx.values()))

    # Visit a parse tree produced by DynamodParser#primary_share.
    def visitPrimary_share(self, ctx:DynamodParser.Primary_shareContext):
        return BinaryOp(ctx, 'share', self.visit(ctx.partition()), None)

    # Visit a parse tree produced by DynamodParser#primary_rel_share.
    def visitPrimary_rel_share(self, ctx:DynamodParser.Primary_rel_shareContext):
        return BinaryOp(ctx, 'share', self.visit(ctx.part), self.visit(ctx.base))

    # Visit a parse tree produced by DynamodParser#part_segment.
    def visitPart_segment(self, ctx:DynamodParser.Part_segmentContext):
        return BinaryOp(ctx, 'with', None, self.visit(ctx.segment()))

    # Visit a parse tree produced by DynamodParser#part_with.
    def visitPart_with(self, ctx:DynamodParser.Part_withContext):
        return BinaryOp(ctx, 'with', self.visit(ctx.partition()), self.visit(ctx.segment()))

    # Visit a parse tree produced by DynamodParser#part_name.
    def visitPart_name(self, ctx:DynamodParser.Part_nameContext):
        return UnaryOp(ctx, 'var', ctx.NAME().getText())

    # Visit a parse tree produced by DynamodParser#part_expr.
    def visitPart_expr(self, ctx:DynamodParser.Part_exprContext):
        return self.visit(ctx.partition())

    # Visit a parse tree produced by DynamodParser#part_method.
    def visitPart_method(self, ctx:DynamodParser.Part_methodContext):
        return TernaryOp(ctx, 'method', self.visit(ctx.partition()), ctx.NAME().getText(), self.visit(ctx.arguments()))

    # Visit a parse tree produced by DynamodParser#arguments.
    def visitArguments(self, ctx:DynamodParser.ArgumentsContext):
        list = []
        for a in ctx.args:
            list.append(self.visit(a))
        return list

