"""
demo.py - Optimized style transfer pipeline for interactive demo.
"""

# system imports
import argparse
import logging
from threading import Lock
import time
import os
from datetime import datetime 

# library imports
import caffe
import cv2
import numpy as np
from skimage.transform import rescale

# local imports
from style import StyleTransfer


# argparse
parser = argparse.ArgumentParser(description="Run the optimized style transfer pipeline.",
                                 usage="demo.py -s <style_image> -c <content_image>")
parser.add_argument("-s", "--style-img", type=str, required=True, help="input style (art) image")
parser.add_argument("-c", "--content-img", type=str, required=True, help="input content image")

# style transfer
# style workers, each should be backed by a lock
workers = {}





def gpu_count():
    """
        Counts the number of CUDA-capable GPUs (Linux only).
    """

    # use nvidia-smi to count number of GPUs
    try:
        output = subprocess.check_output("nvidia-smi -L")
        return len(output.strip().split("\n"))
    except:
        return 0

def init(n_workers=1):
    """
        Initialize the style transfer backend.
    """

    global workers

    if n_workers == 0:
        n_workers = 1

    # assign a lock to each worker
    for i in range(n_workers):
        worker = StyleTransfer("vgg16", use_pbar=False)
        workers.update({Lock(): worker})

def st_api(img_style, img_content, callback=None):
    """
        Style transfer API.
    """

    global workers

    # style transfer arguments
    all_args = [{"length": 360, "ratio": 5e3, "n_iter": 32, "callback": callback},
                {"length": 512, "ratio": 5e4, "n_iter": 16, "callback": callback}]

    # acquire a worker (non-blocking)
    st_lock = None
    st_worker = None
    while st_lock is None:
        for lock, worker in workers.items():

            # unblocking acquire
            if lock.acquire(False):
                st_lock = lock
                st_worker = worker
                break
            else:
                time.sleep(0.1)

    # start style transfer
    img_out = "content"
    for args in all_args:
        args["init"] = img_out
        st_worker.transfer_style(img_style, img_content, **args)
        img_out = st_worker.get_generated()
    st_lock.release()

    return img_out

def main(args):
    """
        Entry point.
    """

    # spin up a worker
    init()

    # perform style transfer
    img_style = caffe.io.load_image(args.style_img)
    img_content = caffe.io.load_image(args.content_img)
    result = st_api(img_style, img_content)
    
    result_trans = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
    
    #save the image
    filename = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    filename += 'pic'
    cv2.imwrite(filename + '.jpg', result_trans*255)

    # show the image
    cv2.imshow("Art", result_trans)
    cv2.waitKey()
    cv2.destroyWindow("Art")

def transfer(image_style, image_content , choice):
    """
        Entry point.
    """

    # spin up a worker
    init()
    caffe.set_mode_gpu()

    # perform style transfer
    img_style = caffe.io.load_image(image_style)
    img_content = caffe.io.load_image(image_content)
    result = st_api(img_style, img_content)
    
    result_trans = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

    result_com = result_trans*255

   # if(choice=='camera'):
      # result_com = np.rot90(result_com)
      #result_com = np.rot90(result_com)
    
    #save the image
    filename = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    filename += 'pic.jpg'
    img_path = os.path.join('C:/Users/ml2020/Desktop/Demo/static', filename)
    cv2.imwrite(img_path, result_com)
    
    return img_path
    


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
