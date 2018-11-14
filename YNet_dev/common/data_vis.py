# @Yinan and @James, please transfer functions here and take care of necessary imports etc. 

#Imports 
import numpy as np 
import matplotlib.pyplot as plt 

def plot_bar_classes(data, preds): 
    """
    Plots a barchart for each class. Each barchart shows all prediction frequences. 

    Input: data object from get_data(PATH,SIZE,BATCH_SIZE)
    Output: barchart plot 
    """
    #list: get names of all classes in our dataset
    class_names = data.test_dl.dataset.fnames[0].split("\\")[1]

    #dictionary{key = class, value = list[predictions]}
    prediction_dict = {}
    temp_index2 = 0 
    for i, key in enumerate(class_names):
        temp_index1 = temp_index2 #set temp_index1 as the old temp_index2
        temp_index2 += list(data.test_dl.dataset.src_idx).count(i)
        preds_dict[key] = list(preds[temp_index1:temp_index2]) #create list of predictions per class 

    #dynamic scaling of GridSpec 
    temp_x = math.ceil((int(len(class_names))/2))
    temp_size = 4 * temp_x 

    #plotting
    plt.figure(figsize=(12, temp_size))
    gs1 = plt.GridSpec(temp_x, 2)
    gs1.update(wspace = 0.4)

    for i, class_name in enumerate(class_names):
        predictions = [preds_dict[class_name][key] for key in data.classes] 
        ax1 = plt.subplot(gs1[i])
        ax1.bar(data.classes, (np.bincount(predictions, minlength=len(class_names))/len(predictions)))
        ax1.set_title(class_name)
        ax1.set_xlim(0,1)

    plt.show()