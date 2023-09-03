import numpy as np
import matplotlib.pyplot as plt
import gsd.hoomd
import freud
from polychrom import polymer_analyses
from tqdm import tqdm
import pickle
import os
from lib.paths import PATHS
    
def path_to_ide(path):
    A = os.path.basename(path).split('.')
    ide = A[0]
    return int(ide)

def get_label(data, ide, char):
    return list(data[data['id']==ide][char])[0]

def exp(ide):  
    return f'{PATHS.trajectory_folder}/{ide}.gsd'


def calc_block_size(gsd_file): 
        a = gsd_file[-2].configuration.step
        b = gsd_file[-1].configuration.step
        return b-a
    
def get_coord_frame(gsd_file, frame_num):
    ''' INPUT: A gsd_file and the frame number from which we want to get our coordinates
    OUTPUT: A np.matrix of shape (MONOMERS, DIMENSIONS)
    ''' 
    snap = gsd_file[frame_num]
    config = freud.box.Box.from_box(snap.configuration.box)
    coords = config.unwrap( snap.particles.position, snap.particles.image)        
    return coords  

def get_coord_frame_excluding_com(self, frame_num):
    ''' Same as get_coords_frame, but the origin of axis is the center of mass.'''
    snap = self.gsd_file[frame_num]
    config = freud.box.Box.from_box(snap.configuration.box)
    coords = config.unwrap( snap.particles.position, snap.particles.image)            
    com = np.mean(coords, axis = 0)
    return coords - com 


def get_coords_sim(gsd_file):
    coords = [get_coord_frame(gsd_file, frame) 
            for frame in range(len(gsd_file))]    
    return coords

def get_bonds_frame(gsd_file, frame = -1):
    coords = get_coord_frame(gsd_file, frame)
    return np.diff(coords[frame], axis = 0)

def get_vel_frame(gsd_file, frame_num): 
    return gsd_file[frame_num].particles.velocity     

def get_KE_frame(gsd_file, frame = -1):  
    vels = get_vel_frame(gsd_file, frame)
    return np.mean(0.5*np.linalg.norm(vels, axis = 1)**2)









