import subprocess
import os
import itertools
import pickle
import numpy as np
from lib.paths import PATHS

def indexed_pairs(grid:dict)->list[list]:
    '''Create all indexed pairs based on a dictionary and return a list of list. 
    Each sublist is the set of all indexed pairs that correspond 
    to a specific key of the dicionary.'''
    
    catalog = []
    for key, vals in grid.items():
        item = [(key,val) for val in vals]
        catalog.append(item)
    return catalog          


def create_combos (grid:dict, copies:int)->list[tuple]:
    ''' Create all the unique combinations from a dict, based on the grid and returnes a list!
    Unique in the sense that each combination contains exactly one value of each key   '''
    
    catalog = indexed_pairs(grid)
    x = itertools.product(*catalog)
    x = list(x)
    r = x.copy()
    if copies != 1:
        for i in range(copies - 1):
            r = [*r,*x]
            
    return(r)


def save_setup(parameters:list, name:str):    
    path = f'{PATHS.setup_folder}/{name}'        
    with open(path, 'wb') as f:
        pickle.dump(parameters, f)
    f.close()


def density_to_L(N, density):
    L = (N/density)**0.33333
    return L

def memory_estimator(N, steps, block):
    frames = steps/block
    byte_size = 35*frames*N
    if byte_size > int(1e7):
        print(f'{byte_size/int(1e9)} GB')
    else:
        print(f'{byte_size/ int(1e6)} MB')