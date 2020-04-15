import numpy as np
import cv2
from matplotlib import pyplot

class Fourier:
    def __init__(self, file_path):
        self.img = ~cv2.imread(file_path,0)
        self.img_color = cv2.cvtColor(cv2.imread(file_path,1), cv2.COLOR_BGR2RGB)

    def display(self):
        fourier_data = np.fft.fft2(self.img)                                    #IMG -> FT
        ftd_center = np.fft.fftshift(fourier_data)                               #Offset to center
        ftd_logscl = 20*np.log(np.abs(ftd_center))                                #Log scale
        ftd_logscl = np.asarray(ftd_logscl,dtype=np.uint8)                        #FT data -> uint8_t
        ftd_phase = np.angle(ftd_center)                                          #FT data -> phase of(FT_data)
        ftd_phase = np.asarray(ftd_phase,dtype=np.uint8)                          #phase of(FT_data) -> uint8_y

        #plotting
        pyplot.subplot(141),pyplot.imshow(self.img_color)
        pyplot.title('Image (color)'), pyplot.xticks([]), pyplot.yticks([])

        pyplot.subplot(142),pyplot.imshow(self.img, cmap = 'Greys')
        pyplot.title('Image (grayscale)'), pyplot.xticks([]), pyplot.yticks([])

        pyplot.subplot(143),pyplot.imshow(ftd_logscl, cmap = 'Greys')
        pyplot.title('Spectrum (FT log scale)'), pyplot.xticks([]), pyplot.yticks([])

        pyplot.subplot(144),pyplot.imshow(ftd_phase, cmap = 'Greys')
        pyplot.title('Phase plot'), pyplot.xticks([]), pyplot.yticks([])

        pyplot.show()
