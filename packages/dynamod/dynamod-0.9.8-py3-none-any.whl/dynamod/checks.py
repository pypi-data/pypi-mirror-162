from dynamod.afterdist import *

def check_nonnegatives(model):
    matrix = model.matrix + model.incoming - model.outgoing
    if np.amin(matrix) < -0.00000001:
        at = np.unravel_index(np.argmin(matrix), matrix.shape)
        print ("!!! negative share for ", end='')
        for att, index in zip(model.attSystem.attributes, at):
            print (att.name + ":" + att.values[index], end=', ')
        print(" entrycode", at)
        raise EvaluationError("negative matrix entries")

def check_total(model):
    total = (model.matrix + model.incoming - model.outgoing).sum()
    if total < 0.99999999 or total > 1.00000001:
        print ("!!! total is ", total)
        raise EvaluationError("inconsistent matrix total")

def check_changes(model, sin, sout, transfer):
    mysin, tr_subin, my_subin = intersect(sin, model.trace_for)
    mysout, tr_subout, my_subout = intersect(sout, model.trace_for)
    if mysin is not None and mysout is None:
        print ("increase by:", transfer[tr_subin].sum())
    if mysout is not None and mysin is None:
        print ("decrease by:", transfer[tr_subout].sum())

def check_tickchange(model, tick):
    matrix = model.matrix
    value = model.get_traceval(matrix)
    if value != model.trace_val:
        print("[" + str(tick) + "] value changed from", model.trace_val, "to", value)
        model.trace_val = value

def check_correctness(model):
    #matrix = model.matrix + model.incoming + model.outgoing
    if abs(model.matrix.sum() - 1) > 0.00000001:
        raise EvaluationError("matrix total is " + str(model.matrix.sum()))
