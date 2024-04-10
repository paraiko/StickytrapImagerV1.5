# -*- coding: utf-8 -*-
"""
Created on  Apr 9 2024
@author: Ate Boerema
@version: 1.0
"""

import cv2
import os
import pathlib

INPUT_DIR = "/home/luuk/InsectImager/data/0040_IWM24-mb/"
OUTPUT_DIR = "/home/luuk/InsectImager/data/0040_IWM24-mb_croptest/"


## well coordinates
width, height = 2100, 2100
x1, y1, = 1550, 520
x2, y2, = 3450, 520
x3, y3, = 1550, 2400
x4, y4, = 3450, 2400

# Iterate over the root directory and its subdirectories
for dirpath, dirnames, filenames in os.walk(INPUT_DIR):
    # Process files within each directory
    for filename in filenames:

        if filename.endswith(".jpg"):

            # Construct the full path to the file
            file_path = os.path.join(dirpath, filename)
            print("Processing file:", filename)


            fn = filename.split(".")[0]
            fnparts = fn.split("_")

            img = cv2.imread(file_path)

            # Crop the wells
            if fnparts[5] == "ab12":
                #print("ab12")
                well1 = img[y1:y1 + height, x1:x1 + width]
                well2 = img[y2:y2 + height, x2:x2 + width]
                well3 = img[y3:y3 + height, x3:x3 + width]
                well4 = img[y4:y4 + height, x4:x4 + width]
                w1n = f'{fnparts[0]}_{fnparts[1]}_{fnparts[2]}_{fnparts[3]}_{fnparts[4]}_A1.jpg'
                w2n = f'{fnparts[0]}_{fnparts[1]}_{fnparts[2]}_{fnparts[3]}_{fnparts[4]}_A2.jpg'
                w3n = f'{fnparts[0]}_{fnparts[1]}_{fnparts[2]}_{fnparts[3]}_{fnparts[4]}_B1.jpg'
                w4n = f'{fnparts[0]}_{fnparts[1]}_{fnparts[2]}_{fnparts[3]}_{fnparts[4]}_B2.jpg'

                #print (fnparts)
            elif fnparts[5] == "bc12":
                well3 = img[y3:y3 + height, x3:x3 + width]
                well4 = img[y4:y4 + height, x4:x4 + width]
                w3n = f'{fnparts[0]}_{fnparts[1]}_{fnparts[2]}_{fnparts[3]}_{fnparts[4]}_C1.jpg'
                w4n = f'{fnparts[0]}_{fnparts[1]}_{fnparts[2]}_{fnparts[3]}_{fnparts[4]}_C2.jpg'

            elif fnparts[5] == "ab34":
                well1 = img[y1:y1 + height, x1:x1 + width]
                well2 = img[y2:y2 + height, x2:x2 + width]
                well3 = img[y3:y3 + height, x3:x3 + width]
                well4 = img[y4:y4 + height, x4:x4 + width]
                w1n = f'{fnparts[0]}_{fnparts[1]}_{fnparts[2]}_{fnparts[3]}_{fnparts[4]}_A3.jpg'
                w2n = f'{fnparts[0]}_{fnparts[1]}_{fnparts[2]}_{fnparts[3]}_{fnparts[4]}_A4.jpg'
                w3n = f'{fnparts[0]}_{fnparts[1]}_{fnparts[2]}_{fnparts[3]}_{fnparts[4]}_B3.jpg'
                w4n = f'{fnparts[0]}_{fnparts[1]}_{fnparts[2]}_{fnparts[3]}_{fnparts[4]}_B4.jpg'

            elif fnparts[5] == "bc34":
                well3 = img[y3:y3 + height, x3:x3 + width]
                well4 = img[y4:y4 + height, x4:x4 + width]
                w3n = f'{fnparts[0]}_{fnparts[1]}_{fnparts[2]}_{fnparts[3]}_{fnparts[4]}_C3.jpg'
                w4n = f'{fnparts[0]}_{fnparts[1]}_{fnparts[2]}_{fnparts[3]}_{fnparts[4]}_C4.jpg'

            ## write the cropped images
            if fnparts[5] == "ab12" or fnparts[5] == "ab34":
                #print("ab12 write")
                cv2.imwrite(os.path.join(OUTPUT_DIR, w1n), well1)
                cv2.imwrite(os.path.join(OUTPUT_DIR, w2n), well2)
                cv2.imwrite(os.path.join(OUTPUT_DIR, w3n), well3)
                cv2.imwrite(os.path.join(OUTPUT_DIR, w4n), well4)
            else:
                cv2.imwrite(os.path.join(OUTPUT_DIR, w3n), well3)
                cv2.imwrite(os.path.join(OUTPUT_DIR, w4n), well4)


        # Crop the image


        # Display the cropped image
        # cv2.imshow('Cropped Image', well1)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
