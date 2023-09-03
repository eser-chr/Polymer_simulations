from dataclasses import dataclass

@dataclass
class PATHS:
    setup_folder:str = './setups'    
    lattice_folder:str = './lattice'
    logs_folder:str ='./Logs'
    trajectory_folder:str = './'
    id_path:str = './ID'
    catalog:str = './catalog.csv'