""" Compute separations on a DAG"""
import numpy as np

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
    LP = np.zeros((N, N))
    i = 1
    B = A.copy()
    while np.sum(B) > 0.:
        path_exist = np.sign(B)
        path_length = i * path_exist
        LP = np.maximum.reduce((LP, path_length))
        B = np.dot(B, A)
        i += 1
        if dmax and (i == dmax):
            return LP
    return LP
    
def naive_spacelike_matrix(LP, dmax=None):  
    """ Calculate all naive spacelike distances and return them in a matrix
    
    Arguments:
    LP -- longest path matrix
    dmax -- maximum spacelike distance to be returned
    
    Result should be an NxN symmetric matrix of negative longest paths
    and positive naive spacelike separations
    
    JC - this seems quite slow
    """
    if dmax == None:
        dmax = np.max(LP)
    ds = LP + LP.transpose()
    ds2 = ds * ds * -1
    N = LP.shape[0]
    for i in range(N):
        for j in range(N):
            if i > j:
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
    
def twolink_spacelike_matrix(LP, dmax=None):
    """ 2-link spatial distance as described in Rideout2009a 
    Arguments:
    LP -- longest path matrix
    dmax -- maximum spacelike distance to be returned
    
    Result should be an NxN symmetric matrix of negative longest paths
    and positive 2-link spacelike separations
    """
    if dmax == None:
        dmax = np.max(LP)
    ds = LP + LP.transpose()
    ds2 = ds * ds * -1
    N = LP.shape[0]
    for i in range(N):
        for j in range(N):
            if i > j: # spacelike distance is symmetric so ds[i,j]==ds[j,i], and ds[i,i]==0
                if ds2[i,j] == 0: # then they are spacelike separated and need a new value here
                    # find all 2-links in the future
                    i2_future = np.where(LP[:,i]==1)[0]
                    j2_future = np.where(LP[:,j]==1)[0]
                    two_link_future = np.intersect1d(i2_future, j2_future)
                    i_past = np.flatnonzero(LP[:,i])
                    j_past = np.flatnonzero(LP[:,j])
                    link_past = np.intersect1d(i_past, j_past)
                    
                    if len(two_link_future) > 0:
                        # find all minimal LP to a point in their mutual past
                        c = 0
                        for w in two_link_future:
                            sp_dist = dmax
                            for z in link_past:
                                w_z = LP[w,z]
                                if w_z > 0:
                                    sp_dist = min(sp_dist, w_z)
                            c += sp_dist
                        av_sp_dist = float(c) / len(two_link_future)  
                    else:
                        av_sp_dist = dmax   
                    ds2[i,j] = av_sp_dist**2
                    ds2[j,i] = av_sp_dist**2
    return ds2 
    
if __name__ == "__main__":
    print __doc__
    