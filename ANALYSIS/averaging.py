import numpy as np

''' Utils to deal with specific structures:
str0: {key:[]}. A dic with single key and a list as a value
strA: [str0, str0, ...]: A list with elements of str0
'''


def extract_values(dic):
    '''Given str0. It returns the list [] (value)'''
    val = dic.values()
    return list(val)[0]


def create_matrix_with_vals(catalog):
    '''Given strA. It creates a matrix of the value_lists. 
    Each row represents a key. '''
    matrix = [extract_values(line) for line in catalog]
    return np.array(matrix)


def calc_mean(catalog):
    '''Calculates the mean of the list_values of a strA'''
    matrix = create_matrix_with_vals(catalog)
    return matrix.mean(axis=0)


def calc_std(catalog):
    '''Calculates the std of the list_values of a strA'''
    matrix = create_matrix_with_vals(catalog)
    return matrix.std(axis=0)

def permutation(lista, sigma):
    ''' Returns the permutation(sigma) of a list. sigma is in mathematical sense. For example sigma=(1,3,2) will flip position between the third and second item of a list. 0 index is already taken into account'''
    sigma = (i-1 for i in sigma)
    new = [lista[i] for i in sigma]
    return new

