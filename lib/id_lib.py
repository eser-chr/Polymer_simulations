import pickle
from my_package.paths import PATHS

def set_id(A:list):
    with open(PATHS.id_path,'wb') as f:
        pickle.dump(A,f)
        
def read_id():
    with open(PATHS.id_path, 'rb') as f:
        A = pickle.load(f)
    return(A)

