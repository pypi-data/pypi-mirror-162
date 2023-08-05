# Generated from Dynamod.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .DynamodParser import DynamodParser
else:
    from DynamodParser import DynamodParser

# This class defines a complete generic visitor for a parse tree produced by DynamodParser.

class DynamodVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by DynamodParser#model.
    def visitModel(self, ctx:DynamodParser.ModelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#model_inc.
    def visitModel_inc(self, ctx:DynamodParser.Model_incContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#model_settings.
    def visitModel_settings(self, ctx:DynamodParser.Model_settingsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#model_pars.
    def visitModel_pars(self, ctx:DynamodParser.Model_parsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#model_attribs.
    def visitModel_attribs(self, ctx:DynamodParser.Model_attribsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#model_formulas.
    def visitModel_formulas(self, ctx:DynamodParser.Model_formulasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#model_progressions.
    def visitModel_progressions(self, ctx:DynamodParser.Model_progressionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#model_results.
    def visitModel_results(self, ctx:DynamodParser.Model_resultsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#model_ignore.
    def visitModel_ignore(self, ctx:DynamodParser.Model_ignoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#parameters.
    def visitParameters(self, ctx:DynamodParser.ParametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#settings.
    def visitSettings(self, ctx:DynamodParser.SettingsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#setting_expr.
    def visitSetting_expr(self, ctx:DynamodParser.Setting_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#setting_extends.
    def visitSetting_extends(self, ctx:DynamodParser.Setting_extendsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#parameter.
    def visitParameter(self, ctx:DynamodParser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#attributes.
    def visitAttributes(self, ctx:DynamodParser.AttributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#attribute.
    def visitAttribute(self, ctx:DynamodParser.AttributeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#attribute_block.
    def visitAttribute_block(self, ctx:DynamodParser.Attribute_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#shares_as_list.
    def visitShares_as_list(self, ctx:DynamodParser.Shares_as_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#shares_as_map.
    def visitShares_as_map(self, ctx:DynamodParser.Shares_as_mapContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#shares_as_cond.
    def visitShares_as_cond(self, ctx:DynamodParser.Shares_as_condContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#share_map_block.
    def visitShare_map_block(self, ctx:DynamodParser.Share_map_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#share_map.
    def visitShare_map(self, ctx:DynamodParser.Share_mapContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#share_def.
    def visitShare_def(self, ctx:DynamodParser.Share_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#cond_shares_block.
    def visitCond_shares_block(self, ctx:DynamodParser.Cond_shares_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#cond_shares.
    def visitCond_shares(self, ctx:DynamodParser.Cond_sharesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#cond_share.
    def visitCond_share(self, ctx:DynamodParser.Cond_shareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#pexpr_as_simple.
    def visitPexpr_as_simple(self, ctx:DynamodParser.Pexpr_as_simpleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#pexpr_as_block.
    def visitPexpr_as_block(self, ctx:DynamodParser.Pexpr_as_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#pexpression_block.
    def visitPexpression_block(self, ctx:DynamodParser.Pexpression_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#pexp_list.
    def visitPexp_list(self, ctx:DynamodParser.Pexp_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#pexp_for.
    def visitPexp_for(self, ctx:DynamodParser.Pexp_forContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#pexp_if.
    def visitPexp_if(self, ctx:DynamodParser.Pexp_ifContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#seg_as_axval.
    def visitSeg_as_axval(self, ctx:DynamodParser.Seg_as_axvalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#seg_as_eq.
    def visitSeg_as_eq(self, ctx:DynamodParser.Seg_as_eqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#seg_as_in.
    def visitSeg_as_in(self, ctx:DynamodParser.Seg_as_inContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#values.
    def visitValues(self, ctx:DynamodParser.ValuesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#expression_list.
    def visitExpression_list(self, ctx:DynamodParser.Expression_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#progressions.
    def visitProgressions(self, ctx:DynamodParser.ProgressionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#progression.
    def visitProgression(self, ctx:DynamodParser.ProgressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#progression_block.
    def visitProgression_block(self, ctx:DynamodParser.Progression_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#progression_statements.
    def visitProgression_statements(self, ctx:DynamodParser.Progression_statementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#prog_vardef.
    def visitProg_vardef(self, ctx:DynamodParser.Prog_vardefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#prog_restrictions.
    def visitProg_restrictions(self, ctx:DynamodParser.Prog_restrictionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#prog_after.
    def visitProg_after(self, ctx:DynamodParser.Prog_afterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#prog_iter.
    def visitProg_iter(self, ctx:DynamodParser.Prog_iterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#prog_action.
    def visitProg_action(self, ctx:DynamodParser.Prog_actionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#prog_expr.
    def visitProg_expr(self, ctx:DynamodParser.Prog_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#restr_for.
    def visitRestr_for(self, ctx:DynamodParser.Restr_forContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#restr_prob.
    def visitRestr_prob(self, ctx:DynamodParser.Restr_probContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#restr_if.
    def visitRestr_if(self, ctx:DynamodParser.Restr_ifContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#progression_after.
    def visitProgression_after(self, ctx:DynamodParser.Progression_afterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#progression_iteration.
    def visitProgression_iteration(self, ctx:DynamodParser.Progression_iterationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#progression_action.
    def visitProgression_action(self, ctx:DynamodParser.Progression_actionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#pstate_name.
    def visitPstate_name(self, ctx:DynamodParser.Pstate_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#pstate_dot.
    def visitPstate_dot(self, ctx:DynamodParser.Pstate_dotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#pstate_block.
    def visitPstate_block(self, ctx:DynamodParser.Pstate_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#results.
    def visitResults(self, ctx:DynamodParser.ResultsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#result.
    def visitResult(self, ctx:DynamodParser.ResultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#formulas.
    def visitFormulas(self, ctx:DynamodParser.FormulasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#formula_expr.
    def visitFormula_expr(self, ctx:DynamodParser.Formula_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#formula_func.
    def visitFormula_func(self, ctx:DynamodParser.Formula_funcContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#formal_args.
    def visitFormal_args(self, ctx:DynamodParser.Formal_argsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#vardef_simple.
    def visitVardef_simple(self, ctx:DynamodParser.Vardef_simpleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#vardef_dot.
    def visitVardef_dot(self, ctx:DynamodParser.Vardef_dotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#expr_ifelse.
    def visitExpr_ifelse(self, ctx:DynamodParser.Expr_ifelseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#expr_value.
    def visitExpr_value(self, ctx:DynamodParser.Expr_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#disj_ors.
    def visitDisj_ors(self, ctx:DynamodParser.Disj_orsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#disj_one.
    def visitDisj_one(self, ctx:DynamodParser.Disj_oneContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#conj_ands.
    def visitConj_ands(self, ctx:DynamodParser.Conj_andsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#conj_comp.
    def visitConj_comp(self, ctx:DynamodParser.Conj_compContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#comp_two_ops.
    def visitComp_two_ops(self, ctx:DynamodParser.Comp_two_opsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#comp_not.
    def visitComp_not(self, ctx:DynamodParser.Comp_notContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#comp_interval.
    def visitComp_interval(self, ctx:DynamodParser.Comp_intervalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#expval_sub.
    def visitExpval_sub(self, ctx:DynamodParser.Expval_subContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#expval_add.
    def visitExpval_add(self, ctx:DynamodParser.Expval_addContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#expval_term.
    def visitExpval_term(self, ctx:DynamodParser.Expval_termContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#term_mul.
    def visitTerm_mul(self, ctx:DynamodParser.Term_mulContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#term_exp.
    def visitTerm_exp(self, ctx:DynamodParser.Term_expContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#term_factor.
    def visitTerm_factor(self, ctx:DynamodParser.Term_factorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#term_div.
    def visitTerm_div(self, ctx:DynamodParser.Term_divContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#factor_pos.
    def visitFactor_pos(self, ctx:DynamodParser.Factor_posContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#factor_neg.
    def visitFactor_neg(self, ctx:DynamodParser.Factor_negContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#factor_primary.
    def visitFactor_primary(self, ctx:DynamodParser.Factor_primaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#factor_expr.
    def visitFactor_expr(self, ctx:DynamodParser.Factor_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#factor_date.
    def visitFactor_date(self, ctx:DynamodParser.Factor_dateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#factor_number.
    def visitFactor_number(self, ctx:DynamodParser.Factor_numberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#factor_percent.
    def visitFactor_percent(self, ctx:DynamodParser.Factor_percentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#factor_rest.
    def visitFactor_rest(self, ctx:DynamodParser.Factor_restContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#primary_string.
    def visitPrimary_string(self, ctx:DynamodParser.Primary_stringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#primary_func.
    def visitPrimary_func(self, ctx:DynamodParser.Primary_funcContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#primary_method.
    def visitPrimary_method(self, ctx:DynamodParser.Primary_methodContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#primary_partition_splits.
    def visitPrimary_partition_splits(self, ctx:DynamodParser.Primary_partition_splitsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#primary_dot.
    def visitPrimary_dot(self, ctx:DynamodParser.Primary_dotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#primary_list.
    def visitPrimary_list(self, ctx:DynamodParser.Primary_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#primary_partition_split.
    def visitPrimary_partition_split(self, ctx:DynamodParser.Primary_partition_splitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#primary_partition.
    def visitPrimary_partition(self, ctx:DynamodParser.Primary_partitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#primary_share.
    def visitPrimary_share(self, ctx:DynamodParser.Primary_shareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#primary_name.
    def visitPrimary_name(self, ctx:DynamodParser.Primary_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#primary_rel_share.
    def visitPrimary_rel_share(self, ctx:DynamodParser.Primary_rel_shareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#primary_indexed.
    def visitPrimary_indexed(self, ctx:DynamodParser.Primary_indexedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#part_expr.
    def visitPart_expr(self, ctx:DynamodParser.Part_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#part_method.
    def visitPart_method(self, ctx:DynamodParser.Part_methodContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#part_segment.
    def visitPart_segment(self, ctx:DynamodParser.Part_segmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#part_name.
    def visitPart_name(self, ctx:DynamodParser.Part_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#part_with.
    def visitPart_with(self, ctx:DynamodParser.Part_withContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DynamodParser#arguments.
    def visitArguments(self, ctx:DynamodParser.ArgumentsContext):
        return self.visitChildren(ctx)



del DynamodParser