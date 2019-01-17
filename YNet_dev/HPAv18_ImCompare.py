from PIL import Image, ImageSequence
import numpy as np 



def dhash(image,hash_size = 16):
    image = image.convert('LA').resize((hash_size+1, hash_size), Image.ANTIALIAS)
    mat = np.array(
        list(map(lambda x: x[0], image.getdata()))
    ).reshape(hash_size, hash_size+1)
    
    return ''.join(
        map(
            lambda x: hex(x)[2:].rjust(2,'0'),
            np.packbits(np.fliplr(np.diff(mat) < 0))
        )
    )