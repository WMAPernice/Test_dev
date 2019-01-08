from .imports import *
from .torch_imports import *

def accuracy_np(preds, targs):
    preds = np.argmax(preds, 1)
    return (preds==targs).mean()

def accuracy(preds, targs):
    preds = torch.max(preds, dim=1)[1]
    return (preds==targs).float().mean()

def accuracy_thresh(thresh):
    return lambda preds,targs: accuracy_multi(preds, targs, thresh)

def accuracy_multi(preds, targs, thresh):
    return ((preds>thresh).float()==targs).float().mean()

def accuracy_multi_np(preds, targs, thresh):
    return ((preds>thresh)==targs).mean()

def recall(preds, targs, thresh=0.5, kind='micro', eps=1e-9): #(!) modified to support macro averages
    pred_pos = preds > thresh
    tpos = torch.mul((targs.byte() == pred_pos), targs.byte()).float()
    if kind == 'macro':
        _rec = torch.mean(tpos.sum(dim=0) / (targs.float().sum(dim=0) + eps))
    else:
        _rec = tpos.sum()/targs.sum()
    return _rec

def precision(preds, targs, thresh=0.5, kind='micro', eps=1e-9): #(!) modified to support macro averages
    pred_pos = preds > thresh
    tpos = torch.mul((targs.byte() == pred_pos), targs.byte()).float()
    if kind == 'macro':
        _prec = torch.mean(tpos.sum(dim=0) / (pred_pos.float().sum(dim=0) + eps))
    else: 
        _prec = tpos.sum()/(pred_pos.sum() + eps) # eps to avoid div-zero if nothing > threshold
    return _prec

def fbeta(preds, targs, beta=1, thresh=0.5, kind='micro'): #(!) modified to support macro averages
    """Calculates the F-beta score (the weighted harmonic mean of precision and recall).
    This is the micro averaged version where the true positives, false negatives and
    false positives are calculated globally (as opposed to on a per label basis).

    beta == 1 places equal weight on precision and recall, b < 1 emphasizes precision and
    beta > 1 favors recall.
    """
    assert beta > 0, 'beta needs to be greater than 0'
    beta2 = beta ** 2
    rec = recall(preds, targs, thresh, kind)
    prec = precision(preds, targs, thresh, kind)
    return (1 + beta2) * prec * rec / (beta2 * prec + rec)

def f1_micro(preds, targs, thresh=0.5, kind='micro'): #(!) replaces original f1() function ... modified to support macro averages
    return fbeta(preds, targs, 1, thresh, kind)

def f1_macro(preds, targs, thresh=0.5, kind='macro'): # (!) support for macro F1 score
    return fbeta(preds, targs, 1, thresh, kind)
