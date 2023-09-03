import gsd
import gsd.hoomd
import freud
import numpy as np
from numba import njit
from analytic_tools import get_coord_frame

@njit
def MSD_between_two_frames_B(frame_a : np.array, frame_b : np.array):
    '''INPUT: Coords of two single frames. FORMAT is (Monomers, Coords).
    OUTPUT: single number 
    It calculates the avg square displacement of monomers.    '''
    
    diff = frame_a - frame_b
    amp = np.zeros(len(diff))
    for i in range(len(diff)):
        for j in range(3):
            amp[i] += diff[i,j]**2
    msd = np.mean(amp)
    return msd

@njit
def create_matrix(initial_frames:np.array, end_frame:int)->np.matrix:
    '''INPUT: A np.array with all the initial frames for our analysis, the last frame
    OUTPUT: A matrix
    It provides the initial matrix for calculating msd.'''
    
    return np.zeros((len(initial_frames), end_frame-min(initial_frames)))

@njit
def fill_row(initial_frames,REAL_FRAME, j_th_coord,initial_coords, matrix): ## minimize numbers of parameters
    
    for i in range(len(initial_coords)):
        if REAL_FRAME>=initial_frames[i]:
            frame_difference = REAL_FRAME-initial_frames[i]
            matrix[i,frame_difference] = MSD_between_two_frames_B(initial_coords[i], j_th_coord)   
            
def fill_matrix(initial_frames, initial_coords, matrix, msd_gsd_frame): # minimize number of parameters
    INITIAL = min(initial_frames)    
    for j in range(len(matrix[0])): 
        REAL_FRAME = int(j+INITIAL)
        j_th_coord = get_coord_frame(msd_gsd_frame, REAL_FRAME)        
        fill_row(initial_frames, REAL_FRAME, j_th_coord, initial_coords, matrix)   
        
@njit
def get_average_values(matrix, max_difference):
    length = len(matrix[0]) - max_difference
    msd = np.zeros(length, dtype='float64')
    matrix = matrix.T
    for i in range(length):        
        msd[i]=np.mean(matrix[i])
    return msd[1:]


class MSD(): 
    def __init__(self, path_to_file):
        self.data = path_to_file
        self.gsd_file = gsd.hoomd.open(name=self.data, mode="rb")
        self.frames = len(self.gsd_file)
        self.msd = None
        self.initial_frames = np.array([int(self.frames/2 +10*i) for i in range(0,10)])
        self.end_frame = self.frames  
        
        
    def calc_msd(self):
        A = create_matrix(self.initial_frames, self.end_frame)
        initial_coords = [get_coord_frame(self.gsd_file, int(frame))for frame in self.initial_frames]
        fill_matrix(self.initial_frames, initial_coords, A, self.gsd_file)
        max_difference = max(self.initial_frames)-min(self.initial_frames)
        self.msd = get_average_values(A, max_difference)



if __name__=='__main__':
    print('I am a library not a main script!!!')