
def join(*args):
  return ' '.join(map(str, args))

from unicodedata import east_asian_width
import numpy as np
def align(array):
  (m, n) = array.shape
  length = np.array(tuple( tuple( get_length(array[i, j])
    for j in range(n) ) for i in range(m) ))
  length_max = np.max(length, axis=0).astype(int)
  array = [ [ (str(array[i, j])+(' '*(int(length_max[j]-length[i, j]))))[:length_max[j]] 
    for j in range(array.shape[1]) ] for i in range(array.shape[0]) ]
  array = [ ' '.join(array_i)  for array_i in array]
  array = '\n'.join(array)
  return array
IS_FULL = set(('F', 'W', 'A'))
def get_length(element):
  return sum( 2 if (east_asian_width(s) in IS_FULL) else 1 for s in str(element) )
