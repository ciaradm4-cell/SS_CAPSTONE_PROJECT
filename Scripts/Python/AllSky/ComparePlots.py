# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 09:47:57 2021

@author: pmcculey
"""
import matplotlib.pyplot as plt
import numpy as np
import cv2
import os

import glob

on_folder='C:/Users/TCD/Documents/Tellus On-Off/On'
off_folder='C:/Users/TCD/Documents/Tellus On-Off/Off'

on_image_files = (glob.glob(on_folder +"/*.PNG"))
off_image_files = (glob.glob(off_folder +"/*.PNG"))

image=0
for image in range(len(on_image_files)):
    on_image = cv2.imread(on_image_files[image], cv2.IMREAD_COLOR)
    off_image = cv2.imread(off_image_files[image], cv2.IMREAD_COLOR)
    # cv2.imshow("On Image", on_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    subband=on_image_files[image][on_image_files[image].find('_sb')+3:on_image_files[image].find('_sb')+6]
    polarity=on_image_files[image][on_image_files[image].find('_sb')+6:on_image_files[image].find('_sb')+7]
    # initialize the figure
    fig = plt.figure("Comparison On/Off: subband - " + str(subband))
    plt.get_current_fig_manager().resize( 1500,1200 )
    images = ("On", on_image), ("Off", off_image)
    # loop over the images
    for (i, (name, image)) in enumerate(images):
    	# show the image
    	ax = fig.add_subplot(1, 2, i+1)
    	ax.set_title(name, color='k')
        # OpenCV represents RGB images as multi-dimensional NumPy arrays…but in reverse order!
        # This means that images are actually represented in BGR order rather than RGB!
        #https://www.pyimagesearch.com/2014/11/03/display-matplotlib-rgb-image/
    	plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    	plt.axis("off")
    # show the figure
    plt.tight_layout()
    plt.show()
    plt.savefig("C:/Users/TCD/Documents/Tellus On-Off/mode3_sb_" + subband + polarity + ".png",bbox_inches='tight', dpi=300)
    plt.close()