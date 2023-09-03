#!/usr/bin/env python
#SBATCH --nodes=1
#SBATCH --time=0:05:00 
#SBATCH --partition=g
#SBATCH --gres=gpu:1
#SBATCH --qos=g_short
#SBATCH --job-name=MSD
#SBATCH --output=./Logs/log-%A_%a.out
#SBATCH --error=./Logs/log-%A_%a.err 

import os
import sys
import pandas as pd
import numpy as np
from tqdm import tqdm
import pickle
sys.path.append(os.getcwd()) 
from analyser import get_coords
from analyser import get_frame_num


def create_traj(file, monomer):
    ''' Returns a list of coords for all frames of a single particle'''
    N = get_frame_num(file)
    coord_list = []
    for i in range(N):
        coords = get_coords(file, i)
        coord_list.append(coords[monomer])
    return coord_list

def SD_p(trajectory):  
    ''' Square root of difference vs frames for a specific particle'''
    initial = trajectory[0]    
    diff = trajectory - initial
    amp = np.linalg.norm(diff, axis = 1)
    return amp**2

def MSD(file):
    ''' Returns the mean Square difference vs frames. 
    Mean over particles for a single file'''
    general = []
    for monomer in tqdm(range(10)):
        mono = np.random.randint(0,1000)
        traj = create_traj(file, mono)
        catalog = SD_p(traj)
        general.append(catalog)
    return np.mean(general, axis = 0)


if __name__=='__main__':
    
    FOLDER = f'../{sys.argv[1]}'    
    with open(f'{FOLDER}/paths', 'rb') as f:
        paths = pickle.load(f)

    task_id = int(os.environ.get("SLURM_ARRAY_TASK_ID", 0))
    file = paths[task_id] 
    col = os.path.basename(file)
    try:
        data = pd.read_csv(f'{FOLDER}/MSD.csv')
    except:
        data = pd.DataFrame()

    data[col] = MSD(file)
    data.to_csv(f'{FOLDER}/MSD.csv', index = False)
    
