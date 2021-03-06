""" Utility functions for DAG analysis using adjacency matrices"""

#    Copyright (C) 2016 by
#    James Clough <james.clough91@gmail.com>
#    All rights reserved.
#    BSD license.

__author__ = "\n".join(["James Clough (james.clough91@gmail.com)"])

import numpy as np

def causet_adj_matrix(S, R):
    """ Return causal set adjacency matrix A
    
        S: separations
        R: original coordinates"""
    N = S.shape[0]
    A = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            # check time ordering - A[i,j] is 1 if i is in the future of j
            if R[i,0] > R[j,0]:
                if S[i,j] < 0:
                    A[i,j] = 1.
    return A  
    
def transitive_completion(A_):
    """ Transitively complete adjacency matrix A"""
    A = A_[:,:]
    A_0 = A[:,:]
    N, _ = A.shape
    A_diff = True
    i = 0
    while A_diff:
        A_old = A[:,:]
        A = np.dot(A, A_0)
        A += A_0
        A[A>1.] = 1.
        if np.array_equal(A_old, A):
            A_diff = False
        assert i < N, 'ERROR - Transitive Completion required more than N steps'
        i += 1
    return A
    
def transitive_reduction(A_, LP=None):
    """ Transitively reduce adjacency matrix A
   
    plan is to look at successive powers of A and if an element is 1 in both
    then it represents an edge which is transitively implied
    we need to do this |LP| times - 
       - could do it N times to be sure (start here)
       - could compute |LP| but that might be slower
       - could allow |LP| as optional input incase it is already calculated
   """
    A = A_[:,:]
    A_0 = A[:,:]
    N, _ = A.shape
    if LP:
        max_path = LP
    else:
        max_path = N
    i = 0
    while i < max_path:
        A = np.dot(A, A_0)
        A = A_0 - A
        A[A<1] = 0
        A[A>1] = 1
        i += 1
    return A

def longest_path_matrix(A, dmax=None):
    """ Calculate all longest paths and return them in a matrix
    
    Arguments:
    A -- adjacency matrix
    dmax -- maximum path length to be returned
    
    Result should be an NxN assymetric matrix of longest paths
    
    Notes:
    JC - I believe this scales like N**3
         Finding one longest path can be done in linear time
         And we need to find N**2 of them so this is reasonable
        
    JC - The longest path is conjectured to approximate the geodesic in 
         Lorentzian spacetimes but this is not proven to my knowledge 
    """
    N = A.shape[0]
    if dmax is None:
        dmax = N
    LP = np.zeros((N, N))
    i = 1
    B = A[:,:]
    while np.sum(B) > 0.:
        path_exist = np.sign(B)
        path_length = i * path_exist
        LP = np.maximum.reduce((LP, path_length))
        B = np.dot(B, A)
        i += 1
        if i == dmax:
            return LP
    return LP
    
def naive_spacelike_matrix(LP, dmax=None, k=None):  
    """ Calculate all naive spacelike distances and return them in a matrix
    
    Arguments:
    LP -- longest path matrix
    dmax -- maximum spacelike distance to be returned
    k -- only determine distances to k 'landmark' points, and leave the rest
        # this feature needs testing
    
    Result should be an NxN symmetric matrix of negative longest paths
    and positive naive spacelike separations
    
    JC - this seems quite slow when calculated for all N - I think it is the 
         limiting factor on embedding large networks in spacetimes
    """
    if dmax == None:
        dmax = np.max(LP)
    ds = LP + LP.transpose()
    ds2 = ds * ds * -1
    N = LP.shape[0]
    for i in range(N):
        max_j = i
        if k:
            max_j = np.min([i, k])
        for j in range(max_j):
            # spacelike distance is symmetric so ds[i,j]==ds[j,i], and ds[i,i]==0
            if ds2[i,j] == 0:
                # then they are spacelike separated and need a new value here
                i_past = np.flatnonzero(LP[:,i])
                j_past = np.flatnonzero(LP[:,j])
                w_list = np.intersect1d(i_past, j_past)

                i_future = np.flatnonzero(LP[i,:])
                j_future = np.flatnonzero(LP[j,:])
                z_list = np.intersect1d(i_future, j_future)
                if (len(z_list)>0) and (len(w_list)>0):
                    # find min non-zero LP from w to z
                    sp_dist = dmax
                    for w in w_list:
                        for z in z_list:
                            w_z = LP[w, z]
                            if w_z > 0:
                                sp_dist = min(sp_dist, w_z)
                else:
                    sp_dist = dmax
                    
                ds2[i,j] = sp_dist * sp_dist
                ds2[j,i] = sp_dist * sp_dist
    return ds2 
