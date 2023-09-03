import gsd
import gsd.hoomd
import freud
import numpy as np
from numba import njit
from scipy.fft import rfftn
from analytic_tools import get_coord_frame


def fft(COORDS, N, buffer):
    '''INPUT: LIST -> np.shape = (MONOMER, DIMENSION)
       OUTPUT: Fourier transform. Same shape. Instead of MONOMER-> MODE
    '''

    fourier = rfftn(COORDS, axes=0) / N
    return fourier.real[:buffer]
    
@njit
def qcor(modes_a, modes_b):
    '''Returns the correlation factor of all modes.
    INPUT: 2 frames of modes. The format should be (MODE,DIMENSION)'''
    nominator = (modes_a * modes_b).sum(axis=1)
    denominator = np.sqrt((modes_a**2).sum(axis=1) * (modes_b**2).sum(axis=1))
    return nominator/denominator


def qcor_over_modes(MODES, dif): 
    '''Calculates the correlation factor of all modes that are apart (dif) frames.
    Then returns the avg'''
    COR = []
    for i in range(dif, len(MODES)):
        corr = qcor(MODES[i-dif], MODES[i])
        COR.append(corr)
    COR = np.array(COR)    
    return COR.mean(axis=0)

@njit
def maximum(bool_list):
    '''Returns the "gridy" index of the True value.
    Gridy: it will return the maximum of the indices.
    '''
    for i in range(-1,-len(bool_list),-1):
        if bool_list[i]==True:
            return i+len(bool_list)
    return 0.1

def find_maximum_correlated_mode(FFT, frame_dif, threashold):
    cor = qcor_over_modes(FFT, frame_dif)
    check = cor>threashold
    m = maximum(check)
    return m

class Rouse():
    def __init__(self, path):
        self.data = path
        self.gsd_file = gsd.hoomd.open(name=self.data, mode="rb")
        self.modes = None
        self.rouse_cor = None
        self.frames = len(self.gsd_file)
        self.N = self.gsd_file[-1].particles.N
        self.blocks = set(np.logspace(0,np.log10(1000), num = 20, dtype = int)[:-1])
        self.buffer=2000
        self.fourier_transforms = np.zeros((self.frames, self.buffer, 3))
        
    def calc_fourier(self):
        for frame in range(self.frames):
            self.fourier_transforms[frame]=fft(get_coord_frame(self.gsd_file, frame), self.N , self.buffer)
            
    def rouse(self):        
        self.calc_fourier()       
        MAXIMA_MODE = []
        FRAME_DIF =[]
        for frame_dif in self.blocks:             
            maxi = find_maximum_correlated_mode(self.fourier_transforms, frame_dif, 0.95)
            MAXIMA_MODE.append(maxi)
            FRAME_DIF.append(frame_dif)
        self.modes = np.array(MAXIMA_MODE)
        self.rouse_cor = np.array(FRAME_DIF)
        
        

if __name__=='__main__':
    print('I am a library not a main script!!!')