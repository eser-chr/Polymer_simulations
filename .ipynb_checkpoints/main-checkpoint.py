import hoomd
import hoomd.md
import hoomd.md.integrate
import gsd
import gsd.hoomd
import argparse
import time
from utils import create_box
from utils import display_args  
from utils import identity_writer
from utils import calc_KE_of_last_frame
from lib.paths import PATHS
    
def write_snapshot(lattice_path, data):
    with gsd.hoomd.open(name = lattice_path, mode = 'wb') as f:
        f.append(data)
    
class Simulation:
    def __init__(self, N, L, steps, block_size, dt, gamma, integrator, ide, A): #split into dataclass
        self.id, self.catalog = ide, PATHS.catalog                    # Organisatory
        self.integrator, self.T = integrator, 1                         # Enviroment
        self.N, self.L, self.density = N, L, N/L**3                     # Configuration
        self.Steps, self.block_size, self.dt = steps, block_size, dt    # Discretization    
        self.A, self.gamma, self.k = A, gamma, 20                       # Force-related
        #-----------------------------------------                    REST_class_ global
        self.snapshot =  gsd.hoomd.Snapshot()
        self.sim = hoomd.Simulation(device = hoomd.device.GPU(), seed = int(1000*(time.time()%1)))               
        self.particle_filter = hoomd.filter.Type(['O'])
        self.thermo = hoomd.md.compute.ThermodynamicQuantities(
            filter = self.particle_filter)
        self.lattice_file = f'./lattice/{self.id}.gsd'
        self.trajectory_file = f'{PATHS.trajectory_folder}/{self.id}.gsd'        

#------------------------------------------------------------------------------------------    WRITER          
    def set_writer(self): 
        gsd_writer = hoomd.write.GSD(filename= self.trajectory_file, 
            trigger = hoomd.trigger.Periodic(self.block_size), dynamic=["momentum"])
        self.sim.operations.writers.append(gsd_writer) 
#------------------------------------------------------------------------------------------  SETUP    
    def create_bonds(self):
        polymerBonds = [(i,i+1) for i in range(self.N-1)]
        self.snapshot.bonds.N = len(polymerBonds)
        self.snapshot.bonds.group = polymerBonds
        self.snapshot.bonds.types = ['polymer']
        self.snapshot.bonds.typeid = [0] * self.snapshot.bonds.N
        self.snapshot.bonds.validate()           
        
    def create_particles(self):
        box_conf , prt_conf = create_box(self.N, self.L)
        self.snapshot.configuration.box = box_conf
        self.snapshot.particles.N = self.N
        self.snapshot.particles.typeid = [0] * self.N
        self.snapshot.particles.types = ['O']
        self.snapshot.particles.position = prt_conf 
#--------------------------------------------------------------------------------------    MAIN            
    def forces(self):
        harmonic = hoomd.md.bond.Harmonic()
        harmonic.params['polymer'] = dict(k = self.k, r0=1.0)
        forces=[harmonic]
        nl = hoomd.md.nlist.Tree(buffer = 0.4, exclusions = ('bond',))        
        if self.integrator == 'langevin':            
            dpdc = hoomd.md.pair.DPDConservative(nlist=nl, default_r_cut=1.0)
            dpdc.params[('O', 'O')] = dict(A = self.A)
            forces.append(dpdc)        
        elif self.integrator == 'dpd':            
            dpd = hoomd.md.pair.DPD(nlist=nl, kT=self.T, default_r_cut=1.0)
            dpd.params.default = dict(A = self.A, gamma = self.gamma)            
            forces.append(dpd)
        elif self.integrator == 'brownian':            
            dpdc = hoomd.md.pair.DPDConservative(nlist=nl, default_r_cut=1.0)
            dpdc.params[('O', 'O')] = dict(A = self.A)
            forces.append(dpdc)
        return forces    
    
            
    def method(self):  # Consider into splitting to three specific plus one abstract class
        if self.integrator == 'dpd':            
            return hoomd.md.methods.NVE(filter = self.particle_filter) 
        elif self.integrator == 'langevin':
            langevin = hoomd.md.methods.Langevin(
                filter = self.particle_filter, kT = self.T)
            langevin.gamma.default = self.gamma
            return langevin 
        elif self.integrator =='brownian':
            brownian = hoomd.md.methods.Brownian(
                filter = self.particle_filter, kT = self.T)
            brownian.gamma.default = self.gamma
            return brownian
    
    
    def set_integrator(self):         
        self.sim.operations.integrator = hoomd.md.Integrator(
            dt = self.dt, methods = [self.method()], forces = self.forces())    
    
    
    def create_sim(self):        # BAd name. Nice level of abstraction. Maybe rearrange it in the file.
        self.sim.create_state_from_gsd(filename = self.lattice_file)        
        self.sim.state.thermalize_particle_momenta(
            filter = self.particle_filter, kT = self.T)        
        self.sim.operations.computes.append(self.thermo)        
#------------------------------------------------------------------------------------------      FIRE - METHOD        
    def pira(self):
        NVE = hoomd.md.methods.NVE(filter = self.particle_filter)
        V = {'dt':self.dt, 'force_tol':5e-2, 'angmom_tol':5e-1, 'energy_tol':5e-1,
             'alpha_start':0.999, 'forces':self.forces(), 'methods':[NVE]}
        fire = hoomd.md.minimize.FIRE(**V)
        self.sim.operations.integrator = fire    
        display_args(vars(args))  # -------------diplays the passed param at terminal
        
        for _ in range(10):
            self.sim.run(100)
            print(f'kin temp = {self.thermo.kinetic_temperature}, E_P/N = {self.thermo.potential_energy / self.N}')
            
        for _ in range(len(fire.forces)):
            fire.forces.pop()

        for _ in range(len(fire.methods)):
            fire.methods.pop()
#------------------------------------------------------------------------------------------   PUT ALL TOGETHER
    def execute(self):  # NICE that you have splitted the levels of abstraction!!!
        start = time.time()
        self.create_bonds()
        self.create_particles()
        write_snapshot(self.lattice_file, self.snapshot)        
        self.create_sim()
        self.pira()
        self.set_writer()
        self.set_integrator()
        self.sim.run(self.Steps)
        print(run_time:=time.time()-start)  # Maybe that is off
        identity_writer(self.catalog ,vars(args), run_time, self.density, 2/3*calc_KE_of_last_frame(self.trajectory_file))     
        
        
#=================================================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ide', type=int, default = '0')
    parser.add_argument('--N', type=int, default = 100)
    parser.add_argument('--L', type=float, default = 10)
    parser.add_argument('--steps', type=int, default = int(1e2))
    parser.add_argument('--block_size', type=int, default = int(1e1))
    parser.add_argument('--dt', type=float, default = 0.01)
    parser.add_argument('--gamma', type=float, default = 1.0)
    parser.add_argument('--A', type=float, default = 3.0)
    parser.add_argument('--integrator', type=str, default = 'langevin')
    args = parser.parse_args()


    obj = Simulation(**vars(args))
    obj.execute()



