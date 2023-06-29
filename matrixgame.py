# import numpy as np
# import pulp
# def matrixgame(A):
#   (m, n) = A.shape
#   lp = pulp.LpProblem(sense=pulp.LpMaximize)
#   v = pulp.LpVariable("v") 
#   x = [ pulp.LpVariable("x_"+str(i)) for i in range(m) ]
#   for j in range(n):
#     lp += v <= pulp.lpDot(A[:,j], x)
#   for i in range(m):
#     lp += x[i] >= 0
#   lp += pulp.lpSum(x) == 1
#   lp += v
#   lp.solve(pulp.PULP_CBC_CMD(msg=False))
#   x = np.array([ x[i].value() for i in range(m) ])
#   return (x, v.value())

from itertools import combinations
import numpy as np
def matrixgame(A):

  x_list = list()
  v_max = -float('inf')

  (m, n) = A.shape
  for l in range(1, m+1):
    for basis_i in map(list, combinations(range(m), l)):
      for basis_j in map(list, combinations(range(n), l)):

        M = np.ones((1+l, l+1))
        for i in range(l):
          M[0, i] = 1
        M[0, l] = 0
        for i in range(l):
          for j in range(l):
            M[1+j, i] = A[basis_i[i], basis_j[j]]
        for i in range(l):
          M[1+i, l] = -1

        q = np.zeros(1+l)
        q[0] = 1

        x_v = np.zeros(m+1)
        try:
          x_v[basis_i+[m]] = np.linalg.solve(M, q)
        except:
          continue
        x = x_v[:-1]
        v = x_v[-1]

        w = (A.T).dot(x) - v

        if not all(x.round(5) >= 0):
          continue
        if not all(w.round(5) >= 0):
          continue

        if (round(v, 5) < round(v_max, 5)):
          continue
        elif (round(v, 5) == round(v_max, 5)):
          for x_ in x_list:
            if all(x.round(5)==x_.round(5)):
              break
          else:
            x_list.append(x)
        else:
          x_list = [x]
          v_max = v

  x_list = np.array(x_list)
  x = x_list.mean(axis=0)

  return (x, v_max)
