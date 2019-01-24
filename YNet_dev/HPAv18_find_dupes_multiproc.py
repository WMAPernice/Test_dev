import numpy as np
import pandas as pd
import os
import errno
from multiprocessing.pool import Pool
from tqdm import tqdm


def hamming_distance(s1, s2):
    """Return the Hamming distance between equal-length sequences"""
    if len(s1) != len(s2):
        raise ValueError("Undefined for sequences of unequal length")
    return sum(el1 != el2 for el1, el2 in zip(s1, s2))

def find_dupes_multiproc(needles, haystack, th=10):
    dupes = []
    n_chans = len(needles[0,1:])

    for n_im, *n_hashes in tqdm(needles, total=len(needles), unit='files'):
        _dist = np.array([list(map(lambda x,y: hamming_distance(x,y), n_hashes, h_hashes)) for h_im, *h_hashes in haystack])
        _idx = np.flatnonzero(_dist.sum(axis=1) < th * n_chans)
        _dupes = haystack[:,0][_idx]
        
        if len(_dupes) > 0: # duplicate found!
            dupes.extend([[n_im, j, *_dist[_idx][i]] for i, j in enumerate(_dupes)])

if __name__ == '__main__':
    # Parameters
    process_num = 24
    path = 'datasets/HPA_challenge_2018/'

    print('Parent process %s.' % os.getpid())
    needles = pd.read_csv(path + 'needles.csv').values[1:,1:]
    haystack = pd.read_csv(path + 'haystack_no_si.csv').values[1:,1:]
    list_len = len(needles)
    p = Pool(process_num)
    
    for i in range(process_num):
        start = int(i * list_len / process_num)
        end = int((i + 1) * list_len / process_num)
        process_needles = needles[start:end]
        p.apply_async(find_dupes_multiproc, args=(str(i), process_needles, haystack))
        
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
    
if __name__ == '__main__':
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=worker, args=(i,return_dict))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()
    print return_dict.values()   

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    print(f'Duplicates found: {len(dupes)}')
    cols = ['Id', 'dupe'] + [f"Hdist_{c}" for c in range(n_chans)]

return pd.DataFrame(dupes, columns= cols)