import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets import *
from IPython.display import display
from IPython.html import widgets
# plt.style.use('ggplot')


def on_button_clicked(pred):
    
    # converting to str and parsing to get description of the button clicked.
    _, cls, _ = str(pred).split("'")
    
    global idx
    global x
    global y
    global targs
    global preds
    global clss
    
    
    clear_output()
    
    for c in clss:
        buttons = widgets.Button(description=c)
        buttons.on_click(on_button_clicked)
        display(buttons)

    preds.append(lbl2index[cls])
    targs.append(y[idx])
    
#     print(preds, targs)
#     print(len(preds))
    
    if idx == (BATCH_SIZE - 1):
        print('new Batch!')
        idx = 0
        x, y = next(iter(data.trn_dl)) 
        xx = x[idx].cpu().numpy().copy()
        plt.imshow(np.sum(xx, axis=0))
        
    else:
        idx = idx + 1
        # loading it from GPU to CPU
        xx = x[idx].cpu().numpy().copy()
        yy = y[idx]
        plt.imshow(np.sum(xx, axis=0))
        
        
    evaluate(preds, targs)

def evaluate(a, b):
    print(f"human-level accuracy: [{sum((np.asarray(preds)) == (np.asarray(targs))) / len(preds):4.4}]")
    
def manual_preds(loaded_preds = None, loaded_targs = None):    
    
    from IPython.display import clear_output
    
    global idx
    global preds
    global targs
    global clss
    
    
    if loaded_preds is not None and loaded_targs is not None:
        preds = loaded_preds
        targs = loaded_targs
        print(evaluate(preds, targs))
        print("continuing with new batch")
    else:
        preds = []
        targs = []
        print("no previous results loaded - fresh start")
        
    idx = 0
    clss = list(lbl2index.keys())
    clss.append('Exit')

    # creating buttons
    for c in clss:
        buttons = widgets.Button(description=c)
        buttons.on_click(on_button_clicked)
        display(buttons)
    
    # load first image:
    xx = x[idx].cpu().numpy().copy()
    yy = y[idx]
    plt.imshow(np.sum(xx, axis=0))