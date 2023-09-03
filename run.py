import pickle
import subprocess
import sys

def get_ID():
    with open('ID','rb') as f:
        A = pickle.load(f)
    return A[0], A[1]

def change_ID(a,b,num_of_new_sims):           
    a,b = a+b, num_of_new_sims
    with open('ID','wb') as f:
        pickle.dump([a,b],f)        
        
def import_setup_combos(setup_path): 
    with open(f'./setups/{setup_path}', 'rb') as f:  
        combos = pickle.load(f)   
    return combos 

def get_time(t): 
    hours,minutes = t.split(':')
    return hours, minutes

def get_time_flag(hours,minutes):
    return f'{hours}:{minutes}:00'

def get_qos_flag(hours):
    a = 'medium' if int(hours)>8 else 'short'     
    return a

        
setup_path = sys.argv[1]
t = sys.argv[2]
hours, minutes = get_time(t)
time_flag = get_time_flag(hours, minutes)
qos_flag = get_qos_flag(hours)


number_of_combos = len(import_setup_combos(setup_path))
ID, add = get_ID()
change_ID(ID, add, number_of_combos)

flag1 = f'--time={time_flag}'
flag2 = f'--qos=g_{qos_flag}'

cmd = ['sbatch', flag1, flag2, f'--array=0-{number_of_combos-1}', 'sweep.py', f'{ID+add}', f'{setup_path}']
subprocess.call(cmd)