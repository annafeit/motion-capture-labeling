import numpy as np
import scipy.spatial
import datetime

def closest3d(p0, p1, q0, q1, infinite=0):
    """
        computes the closest distance between two line segments, if it exists
    """
    p0 = np.array(p0)
    q1 = np.array(q1)
    p1 = np.array(p1)
    q0 = np.array(q0)
    u = p1-p0
    v = q1-q0
    w0 = p0-q0
    a = np.dot(u,u)
    b = np.dot(u,v)
    c = np.dot(v,v)
    d = np.dot(u, w0)
    e = np.dot(v,w0)
    
    denom = a*c - (b*b)
    if denom != 0: #otherwise parallel
        s = (b*e-c*d)/denom
        t = (a*e-b*d)/denom
        dist = np.linalg.norm(w0 + s*u - t*v)
        if not infinite and s>=0 and s<=1 and t>=0 and t<=1:
            return dist
        elif infinite:
            return dist
        
    return 1000000

def lineIntersectOnce(a1,a2,b1,b2):    
    """
        Check is two line segments intersect at one (!) point. 
        Returns 0 if they are parallel or lye on top each other
    """
    if not type(a1) == np.ndarray:
        a1 = np.array(a1)
        a2 = np.array(a2)
        b1 = np.array(b1)
        b2 = np.array(b2)
    v1 = a2- a1
    v2 = b2 -b1
    c = b1-a1    
    
    if np.linalg.norm(np.cross(v1, v2)) == 0:
        return 0
    
    if np.dot(c, np.cross(v1, v2)) != 0: #not in the same plane        
        return 0
    
    s = np.dot(np.cross(c, v2), np.cross(v1, v2))/np.linalg.norm(np.cross(v1, v2))
    if s>= 0.0 and s<= 1.0:
        return 1
    else:        
        return 0

def lineIntersect2D(a1_3d,a2_3d,b1_3d,b2_3d, thresh, dim):
    """
        Tests of two 3D line segments intersect in 2d. If thresh=0 it's tested if they also intersect in 3D. 
        if thresh > 0 they can be apart in 3D by that much. 
    """
    a1_3d = np.array(a1_3d)
    a2_3d = np.array(a2_3d)
    b1_3d = np.array(b1_3d)
    b2_3d = np.array(b2_3d)
    
    if dim=="xz":
        a1 = np.array([a1_3d[0], a1_3d[2]])
        a2 = np.array([a2_3d[0], a2_3d[2]])
        b1 = np.array([b1_3d[0], b1_3d[2]])
        b2 = np.array([b2_3d[0], b2_3d[2]])
    elif dim=="xy":
        a1 = np.array([a1_3d[0], a1_3d[1]])
        a2 = np.array([a2_3d[0], a2_3d[1]])
        b1 = np.array([b1_3d[0], b1_3d[1]])
        b2 = np.array([b2_3d[0], b2_3d[1]])
    
    da = a2-a1
    db = b2-b1
    dp = a1-b1
    dap = _perp(da)
    denom = np.dot( dap, db)
    num = np.dot( dap, dp )
    p= (num / denom.astype(float))*db + b1
    distFromA = np.linalg.norm(p-a1)
    distFromB = np.linalg.norm(p-b1)
    inside =  p[0]>=min(b1[0], b2[0]) and p[1]>=min(b1[1], b2[1]) and p[0] <=max(b2[0], b1[0]) and p[1] <=max(b2[1], b1[1]) and\
    p[0]>=min(a1[0], a2[0]) and p[1]>=min(a1[1], a2[1]) and p[0] <=max(a2[0], a1[0]) and p[1] <=max(a2[1], a1[1])
    
    if not inside:
        return 0
    else:
        point_3d_onA = a1_3d + distFromA*(a2_3d - a1_3d)
        point_3d_onB = b1_3d + distFromB*(b2_3d - b1_3d)

        dist = np.linalg.norm(point_3d_onA-point_3d_onB)
        print "dist: ", str(dist)
        if dist < thresh:
            return 1
        
        else: 
            return 0
        
def _perp(a):
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b
    
def _unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    if np.linalg.norm(vector) == 0:
        # 0 vector
        return vector
    else:  
        return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = _unit_vector(v1)
    v2_u = _unit_vector(v2)
    angle = np.arccos(np.dot(v1_u, v2_u))
    if np.isnan(angle):
        if (v1_u == v2_u).all():
            return 0.0
        else:
            return np.pi
    return angle

def projectToPlane(v1,v2, M):
    """
        Given vectors v1 and v2 defining a plane and project the given points onto that plane.
        Return the projection.
        Input:
            v1, v2: np.array
                the vectors defining the plane
            M: Nx3 np.matrix
                the matrix of points that should be projected onto the plane
                
        Output:
            projections: array of arrays of points projected onto the plane
            distances: np.matrix of distances of each point from the plane
    """
    nhat = np.cross( v1, v2 )
    nhat = nhat/np.sqrt( np.dot( nhat,nhat) )
        
    distances = np.abs(M.dot(nhat))
    projections = []
    for i in xrange( M.shape[0] ):
        p = M[i,:] + nhat*distances[0,i] 
        projections.append(p)
        
    return projections, distances

def projectToLine(p1,p2,points):
    """
        Given points p1 and p2 defining a line, project the given points onto that line.
        Return the projection and distances.
        Input:
            v1, v2: np.array
                the vectors defining the line
            points: [np.array]
                the array of points that should be projected onto the plane
                
        Output:
            projections: array of arrays of points projected onto the plane
            distances: array of distances of each point from the plane
    """
    
    distances = []
    projections = []
    for x in points:        
        a = p2-p1
        b = x-p1
        t = (b.dot(a) / (a[0]*a[0]+a[1]*a[1]+a[2]*a[2]))
        projectionPoint = p1+ (t*a)
        if t>1.0:
            distance = np.linalg.norm(p2-x)
        elif t<0.0:
            distance = np.linalg.norm(p1-x)
        else:
            distance = np.linalg.norm(x-projectionPoint)
        distances.append(distance)
        projections.append(projectionPoint)    
    
    return projections, distances

def smooth(data, window_len=5):
    """
        smooth data with moving average of window_leng
    """    
    s=np.r_[data[window_len-1:0:-1],data,data[-1:-window_len:-1]]
    w=np.ones(window_len,'d')
    data=np.convolve(w/w.sum(),s,mode='valid')
    return data


def _do_kdtree(neighbors,points, k_neighbors):
    mytree = scipy.spatial.cKDTree(neighbors)    
    dist = []
    indexes = []
    try:
        dist, indexes = mytree.query(points, k=k_neighbors)
    except Exception:
        for i in range(0,len(points)):
            print i
            p = points[i]
            d, ix = mytree.query(p, k=k_neighbors)
            dist.append(d)
            indexes.append(ix)
        
     
    return dist, indexes

def _computeNearestNeighbor(neighbors, points, k_neighbors):
    """
        returns the distances and indices of nearest neighbors of given points 
        to given neighbors.
        Format must be according to following example:
            points_y = numpy.array([1,2,5])
            points_x = numpy.array([0.5,0,2])
            points = numpy.array([points_y, points_x])
            >> array([[ 1 ,  2 ,  5 ],
                      [ 0.5,  0 ,  2 ]])
                      
            y_array = numpy.array([0,1,2,3,4,5])
            x_array = numpy.array([0,0,0,0,0,0])
            neighbors = numpy.dstack([y_array.ravel(),x_array.ravel()])[0]
            >> array([[0, 0],
                      [1, 0],
                      [2, 0],
                      [3, 0],
                      [4, 0],
                      [5, 0]])
    """
    dist, indexes = _do_kdtree(neighbors, points, k_neighbors)
    return dist,indexes
    
    
def nearestNeighbor(lastLabeledData, db_unlabeledData, db, frame):
    """ returns a dictionary. Each marker in lastLabeledData is mapped to an array:
        [name of the new Marker, distance to new marker]
        Filters out markers that are mapped to the same marker and maps only the
        one with the smallest distance. 
    """
    #Number of neighbors to compute for each marker
    k_neighbors = 1 #k = 2 does not work (yet!?)
    
    neighbors = np.array(db_unlabeledData.values())
    points = np.array(lastLabeledData.values())    
    dist, indexes = _computeNearestNeighbor(neighbors, points, k_neighbors)    
    takenindexes = [] #keep track of taken elements in case several markers have the same distance
    mapDict = {}
    for i in range(0,len(lastLabeledData.keys())):
        name =  lastLabeledData.keys()[i]   
        index = indexes[i]
        if index not in takenindexes:
            double = np.where(indexes==index)[0]
            if(len(double)>1):
                #there are more markers that should be mapped to that index
                 
                #map only if this one has the smallest distance
                if _hasSmallestDistance(dist, i, double):
                
                #map only if this one has the smallest change in angle
                #if _hasSmallestAngleChange(double, i, db, name, db_unlabeledData, lastLabeledData, index, dist, frame):
                    mapDict[name] = [db_unlabeledData.keys()[index], dist[i]]  
                    takenindexes.append(index)  
                
                else:
                    #no marker available for this
                    mapDict[name] = []
            else:     
                mapDict[name] = [db_unlabeledData.keys()[index], dist[i]]
        else:
            #no marker available for this
            mapDict[name] = []     
    return mapDict

def _hasSmallestAngleChange(double, i, db, marker_name, db_unlabeledData, lastLabeledData, index, dist, frame):    
    
    marker = db.getMarkerByName(marker_name)
    if marker.getChildMarker() != 0 and marker.getParentMarker() != 0:
        newPos = db_unlabeledData[db_unlabeledData.keys()[index]]
        
        angleChange = _computeChangeInAngle(marker, frame, newPos)
        minAngleChange = min([_computeChangeInAngle(db.getMarkerByName(lastLabeledData.keys()[d])  , frame, newPos) for d in double])
        
        if(minAngleChange == angleChange):
            #this is the smallest change in angle
            return 1
        else:
            return 0 
       
    else: 
        return _hasSmallestDistance(dist, i, double)
    
def _computeChangeInAngle(marker, frame, newPos):    
    middle = marker
    child = marker.getChildMarker()
    parent = marker.getParentMarker()
    #has child and parent
    #previous angle
    bone1_prev = np.array(middle.getdata(frame-1)) - np.array(parent.getdata(frame-1))
    bone2_prev =  np.array(child.getdata(frame-1)) - np.array(middle.getdata(frame-1))
    previous_angle = angle_between(bone1_prev, bone2_prev)

    #potential new angle
    bone1 = np.array(newPos) - np.array(parent.getdata(frame-1))
    bone2 =  np.array(child.getdata(frame-1)) - np.array(newPos)
    angle = angle_between(bone1, bone2)

    return np.absolute(angle - previous_angle)

def _hasSmallestDistance(dist, i, double):
    minDist = min([dist[d] for d in double])
    if(minDist == dist[i]):
        #this is the smallest distance
        return 1
    else:
        return 0        

                    
def insideBoundingBox(point, bbox):
    return point[0]>=bbox[0] and \
            point[1]>=bbox[1] and \
            point[2]>=bbox[2] and \
            point[0]<=bbox[3] and \
            point[1]<=bbox[4] and \
            point[2]<=bbox[5]
            
            

      