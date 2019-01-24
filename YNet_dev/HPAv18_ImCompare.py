from PIL import Image, ImageSequence
import numpy as np 


def dhash_v1(image,hash_size = 16, **kwargs):
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


def dhash_v2(image, hash_size=8, axis='columns', **kwargs):
    """
    Difference Hash computation.
    Based on implementation at: https://github.com/JohannesBuchner/imagehash
    
    computes differences between pixel columns or rows
    @image must be a PIL instance.
    """
    # resize(w, h), but numpy.array((h, w))
    if hash_size < 2:
        raise ValueError("Hash size must be greater than or equal to 2")

    image = image.convert("L").resize((hash_size + 1, hash_size), Image.ANTIALIAS)
    pixels = np.asarray(image)
    
    if axis == 'columns':
        # compute differences between columns
        _diff = pixels[:, 1:] > pixels[:, :-1]
    elif axis == 'rows':
        # compute differences between rows
        _diff = pixels[1:, :] > pixels[:-1, :]
    else:
        raise ValueError(f"Invalid choice for axis-keyword in dhash_v2! Valid options: columns, rows") 

    diff = _binary_array_to_hex(_diff)
    return diff


def average_hash(image, hash_size=8, **kwargs):
    """
    Average Hash computation
    Based on implementation at: https://github.com/JohannesBuchner/imagehash
    
    Step by step explanation: https://www.safaribooksonline.com/blog/2013/11/26/image-hashing-with-python/
    @image must be a PIL instance.
    """
    if hash_size < 2:
        raise ValueError("Hash size must be greater than or equal to 2")

    # reduce size and complexity, then covert to grayscale
    image = image.convert("L").resize((hash_size, hash_size), Image.ANTIALIAS)

    # find average pixel value; 'pixels' is an array of the pixel values, ranging from 0 (black) to 255 (white)
    pixels = np.asarray(image)
    avg = pixels.mean()

    # create string of bits
    diff = pixels > avg
    # make a hash
    return _binary_array_to_hex(diff)


def phash(image, hash_size=8, highfreq_factor=4, **kwargs):
    """
    Perceptual Hash computation.
    Based on implementation at: https://github.com/JohannesBuchner/imagehash
    @image must be a PIL instance.
    """
    if hash_size < 2:
        raise ValueError("Hash size must be greater than or equal to 2")

    import scipy.fftpack
    img_size = hash_size * highfreq_factor
    image = image.convert("L").resize((img_size, img_size), Image.ANTIALIAS)
    pixels = np.asarray(image)
    dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
    dctlowfreq = dct[:hash_size, :hash_size]
    med = np.median(dctlowfreq)
    diff = dctlowfreq > med
    return _binary_array_to_hex(diff)

def _binary_array_to_hex(arr):
    """
    Function to make a hex string out of a binary array.
    """
    bit_string = ''.join(str(b) for b in 1 * arr.flatten())
    width = int(np.ceil(len(bit_string)/4))
    return '{:0>{width}x}'.format(int(bit_string, 2), width=width)