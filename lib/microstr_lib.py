import gsd
import gsd.hoomd
import freud
import numpy as np
from numba import njit
from analytic_tools import get_coord_frame
from scipy.optimize import curve_fit
from scipy.stats import gaussian_kde

def gaussian(x, sigma, mu):
    return 1/(sigma*(2*np.pi)**0.5) * np.exp(-(x-mu)**2/(2*sigma**2))

def boltzmann(x, alpha):
    return (2/np.pi)**0.5 * x**2 * np.exp(-x**2/(2*alpha**2)) / (alpha**3)


def get_distribution(vals:list[float]):
    '''Get distribution out of a list'''
    
    density = gaussian_kde(vals)
    x = np.linspace(min(vals), max(vals), 100)
    y = density(x)
    return x, y


class Bonds():
    def __init__(self, path):
        self.data = path
        self.gsd_file = gsd.hoomd.open(name=self.data, mode="rb")
        self.mu = None
        self.sigma = None  
        self.frames = len(self.gsd_file)
        self.frame_list = [i*100 for i in range(int(self.frames/100))]
    
            
    def get_opts(self, frame): 
        ''' Fits the bonds of a frame into a gaussian distribution and returns the values
        of that gaussian fitting.'''
        coords = get_coord_frame(self.gsd_file, frame)               
        bonds = coords[1:,:]-coords[:-1,:]
        amp = np.linalg.norm(bonds, axis =1)
        x,y = get_distribution(amp)
        popt, pcov = curve_fit(gaussian, x,y)
        return popt
    
    def calc_opts(self):
        A = [self.get_opts(i) for i in self.frame_list]
        self.sigma = [a[0] for a in A] 
        self.mu = [a[1] for a in A] 
        

        
class Velocities():
    def __init__(self, path):
        self.data = path
        self.gsd_file = gsd.hoomd.open(name=self.data, mode="rb")
        self.alphas = None
        self.frames = len(self.gsd_file)       
        self.frame_list = [i*100 for i in range(int(self.frames/100))]    
            
    def get_alpha(self, frame):     # SPlit it
        vels = self.gsd_file[frame].particles.velocity
        amp = np.linalg.norm(vels, axis =1)
        x,y = get_distribution(amp)
        popt, pcov = curve_fit(boltzmann, x,y)
        return [popt[0], pcov[0][0]]
    
    def calc_alphas(self):
        A = [self.get_alpha(i) for i in self.frame_list]
        self.alphas = [a[0] for a in A] 
        self.err = [a[1] for a in A] 
    
  