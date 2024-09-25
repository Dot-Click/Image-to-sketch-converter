import cv2
import numpy as np
from matplotlib import pyplot as plt

# def model6(image, smoothness=5, denoise=False, enhance_before_sketching=True):
image = cv2.imread(r"D:\mustafa\avatar\MUSss.jpg") 
image = cv2.resize(image,(350,350))
b = cv2.bilateralFilter(image, 15, 100, 100) 
# gray = cv2.cvtColor(b, cv2.IMREAD_GRAYSCALE)
mergeImg = np.hstack((image, b))
cv2.imshow("filtered image",mergeImg)
cv2.waitKey(0)
cv2.destroyAllWindows()
# denoised_image = cv2.fastNlMeansDenoising(gray, h=10)
#  return b
