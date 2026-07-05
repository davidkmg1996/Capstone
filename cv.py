import cv2
import numpy as np
import kagglehub
import pandas


fpath =  kagglehub.dataset_download("kwentar/blur-dataset")

#Sharpening using kernel
def sharpenImageKernel(src):
    #src = cv2.imread('fpath')
    #Modify kernel as needed for image sharpening
    kernel = np.array([1, 1, 1,
                       1, 1, 1,
                       1, 1, 1])
    sharpen = cv2.filter2D(src, -1, kernel)
    return sharpen

#Sharpening using unmask
def sharpenImageGaussianBlur(src):
    #src = cv2.imread('fpath')
    blur = cv2.GaussianBlur(src(0,0), 10)
    sharpen = cv2.addWeighted(src, 1.5, blur, -.2, 0)
    return sharpen

#Noise Reduction COLOR (Nonlocal)
def reduceNoiseColorNonlocal(src):
    #src = cv2.imread('fpath')
    denoiseColor = cv2.fastNlMeansDenoisingColored(src, None, 0, 0, 0)
    return denoiseColor

#Noise reduction GRAY (Nonlocal)
def reduceNoiseGray(src):
        #src = cv2.imread('fpath', cv2.COLOR_BGR2GRAY)
        cv2.cvtColor(src, )
        denoiseGray = cv2.fastNlMeansDenoising(src, None, 0, 0, 0)
        return denoiseGray

#Upscaling
def resizeVision(src):
     #src = cv2.imread('fpath')
     #Update dimensions as needed
     width = 1
     height = 1

     imUpscale = cv2.resize(src(width, height), interpolation=cv2.INTER_CUBIC)

     return imUpscale

#Photo restoration
img = cv2.imread("inserFilePath")

#Super Resolution (With TensorFlow models)
def superRes(src):
    superRes = cv2.dnn_superres.DnnSuperResImpl.create()
    mPath = src
    superRes.readModel(mPath)
    superRes.setModel('modelName', 3)
    img = cv2.imread('imagePath')
    imgSuper = superRes.upsample(img)
    #cv2.imwrite("imageName", imgSuper)
    return imgSuper


sharpen