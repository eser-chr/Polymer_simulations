#!/usr/bin/env python
#SBATCH --nodes=1
#SBATCH --partition=g
#SBATCH --gres=gpu:1
#SBATCH --job-name=TESTS
#SBATCH --mem=32000  
#SBATCH --output=./Logs/log-%A_%a.out
#SBATCH --error=./Logs/log-%A_%a.err
'''
A programm that sweeps over all the combinations that are passed via the setup file (see setup) as second argument.
The first argument is the id number that should be passed to the first simulation
'''
import subprocess
import os
import sys
import pickle

def get_ID():   # Do you really need this int(float(...)) 
    '''Calculates the ID that should be given to each simulation'''
    x=int(float(sys.argv[1]))
    task_id = int(os.environ.get("SLURM_ARRAY_TASK_ID", 0))
    return (int(float(x)) + task_id)


  
def get_combos():
    '''Open the setup file and get the combinations'''
    with open(f'./setups/{sys.argv[2]}', 'rb') as f:
        combos = pickle.load(f)   
        task_id = int(os.environ.get("SLURM_ARRAY_TASK_ID", 0))
    return dict(combos[task_id])




cmd = ["python", 'main.py']
sim_id = get_ID()
cli_params = {"--id":sim_id }
extra_params = get_combos()
cli_params.update(extra_params)
for k, v in cli_params.items():  # ----- Adding the parameters to the command so they can be parsed to the main.py file
    if v is not None:
        cmd.append(k)
        if bool(str(v)):  # Use guard and split this nested if statement
            cmd.append(str(v))
subprocess.call(cmd)
    

