import matplotlib.pyplot as plt
import numpy as np
import os 
import cv2
import imutils


#FILE_PATH = '/opt/ml/input/final_project/test_pics/person_05'

def detect_blur_fft(image, size=60):
	# grab the dimensions of the image and use the dimensions to
	# derive the center (x, y)-coordinates
	(h, w) = image.shape
	(cX, cY) = (int(w / 2.0), int(h / 2.0))
	fft = np.fft.fft2(image)
	fftShift = np.fft.fftshift(fft)
	fftShift[cY - size:cY + size, cX - size:cX + size] = 0
	fftShift = np.fft.ifftshift(fftShift)
	recon = np.fft.ifft2(fftShift)
    # compute the magnitude spectrum of the reconstructed image,
	# then compute the mean of the magnitude values
    
	magnitude = 20 * np.log(np.abs(recon))
	mean = np.mean(magnitude)
	# the image will be considered "blurry" if the mean value of the
	# magnitudes is less than the threshold value
	return (mean)

def pick_one(FILE_PATH):
	mean = []
	for i, imagePath in enumerate(os.listdir(FILE_PATH)):
		orig = cv2.imread(os.path.join(FILE_PATH,imagePath))
		orig = imutils.resize(orig, width=500)
		gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
		# apply our blur detector using the FFT
		mean.append( [imagePath, round(detect_blur_fft(gray, size=60),3 )])
	#sort in descending order by sharpness 
	mean = sorted(mean, key = lambda x: x[1], reverse = True)
	#return FILE_PATH + FILE_NAME
	return os.path.join(FILE_PATH,mean[0][0])

