import numpy as np
import pandas as pd
import gsd.hoomd

def points_sphere(N): 
    step_size=1.0
    theta = np.random.uniform(0.0, 2.0 * np.pi, N)    
    u = np.random.uniform(-1.0, 1.0, N)
    dx = step_size * np.sqrt(1.0 - u * u) * np.cos(theta)
    dy = step_size * np.sqrt(1.0 - u * u) * np.sin(theta)
    dz = step_size * u
    return np.vstack([dx,dy,dz]).T


def create_constrained_random_walk(N, constraint_f): 
    starting_point=(0, 0, 0)
    i,j = 1,N
    out = np.zeros((N, 3))
    while i < N:
        if j == N:           
            d = points_sphere(N)
            j = 0                       # I do not really like this code
        new_p = out[i - 1] + d[j]
        if constraint_f(new_p):
            out[i] = new_p
            i += 1
        j += 1
    return out    


def box_coord_check(point, xLen, yLen, zLen): # Better name : isConstrained & minimize parameters
    x,y,z = point
    tests = [-xLen/2+1 < x < xLen/2-1, 
                 -yLen/2+1 < y < yLen/2-1, 
                     -zLen/2+1 < z < zLen/2-1]
    return all(tests)


def create_box(N, side_length):
    box_conf = [side_length, side_length, side_length, 0, 0, 0]
    BoxCheck = lambda point: box_coord_check(point, side_length, side_length, side_length)
    initialConf = create_constrained_random_walk(N, BoxCheck)
    return box_conf, initialConf


def display_args(dic):
    print('              --------------              ')            
    for i, (key, val) in enumerate(dic.items()):
        if i%3==0:
            print()
            print()
        print(f'{key} = {val}', end = ',  ')
    print()
    print('              --------------              ')
    
    
def identity_writer(path, dic, run_time, density, kE): # Terrible -> add_sim_properties_to_catalog() && minimize parameters!!
    append = {'run_time':[run_time], 'rho':[density]
             ,'kT':[kE]}
    dic.update(append)
    data = pd.DataFrame(dic)
    data.to_csv(path, mode='a', index=False, header=False)
    
    
def calc_KE_of_last_frame(path): 
    gsd_file = gsd.hoomd.open(name = path, mode='rb')
    snap = gsd_file[-1]
    velocities = snap.particles.velocity
    return np.mean(0.5*np.linalg.norm(velocities, axis = 1)**2)


