import types
import numpy as np
import helper
from array import array
from numpy.f2py.auxfuncs import throw_error

class MoCapMarker:
    """
        Stores the data of one marker.
    """
    MIN =  10000000.0
    MAX = -10000000.0
    ERROR = '-9999.99'
    def __init__(self, identifier, firstFrame, lastFrame, currentName=None):
        """
            Creates the marker. CurrentName is used when labeling the marker.
        """
        self.markerRelabeledTo = {}
        self.markerLabeledToAtFrame = [] #keeps track of current name for every frame
        #NOTE: assumes to have one parent and one child marker (not mroe)
        self.parentMarker = 0
        self.childMarker = 0
        self.childVectorAtFrame0 = []

        self.name = identifier
        self.data = [] # a list of lists of xyz values        
        self.missingFrames = []
        #self.disappearingFrame = -1 #tracks when is the first time that the marker is disappearing for rest of log
        if(currentName != None):
            self.currentName = currentName
        else:
            self.currentName = self.name
        self.markerRelabeledTo[0] = self.currentName #keeps track of when this marker was relabeled to a new one

        self.isFingerMarker = "1" in self.name or "2" in self.name or "3" in self.name or "4" in self.name                
        self.firstFrame = firstFrame
        self.lastFrame = lastFrame
        self.offset_keylog = 0
        self.offset_keylog_stdInFrames = 0

    def getname(self):
        return self.name

    def getNameAtFrame(self, frame):
        return self.markerLabeledToAtFrame[frame]

    def append(self, x,y=0,z=0):
        """
            Note: when calling this method, first rename (= call setCurrentName), then append!
        """
        self.markerLabeledToAtFrame.append(self.currentName)
        if type(x) == types.ListType:
            self.data.append(x)
        else:
            if (x == self.ERROR or
                y == self.ERROR or
                z == self.ERROR):
                self.data.append([])
                #if(self.disappearingFrame == -1):
                    #marker disappears for the first time.
                #    self.disappearingFrame = len(self.data)

            else:
                self.data.append( [float(x),
                                   float(y),
                                   float(z)] )
                #if(self.disappearingFrame >= 0):
                    #reset disappearing frame, as the marker reappears.
                #    self.disappearingFrame = -1

    def deleteLastDataFrame(self):
        if len(self.data) in self.markerRelabeledTo.keys():
            #Reset name
            self.markerRelabeledTo.pop(len(self.data))
            self.currentName = self.markerLabeledToAtFrame[len(self.data)-1]
        del self.data[-1]
        del self.markerLabeledToAtFrame[-1]


    def getdata(self, frame):
        if len(self.data) == 0:
            return []
        else:
            try:
                return self.data[frame]
            except IndexError:
                return []

    def getDataToString(self, frame, sep="\t"):
        """
            returns a string as needed for writing the data to file.
        """
        if len(self.data) == 0:
            return []
        else:
            framedata = self.data[frame]
            if framedata == []:
                return sep+sep+sep
            else:
                return sep + "{:f}".format(framedata[0])+ sep +"{:f}".format(framedata[1] )+ sep + "{:f}".format(framedata[2])


    def getBbox(self):
        minx = miny = minz = MoCapMarker.MIN
        maxx = maxy = maxz = MoCapMarker.MAX
        if len(self.data) == 0:
            return []
        for coords in self.data:
            if len(coords) == 0:
                return []
            minx = min(minx, coords[0])
            miny = min(miny, coords[1])
            minz = min(minz, coords[2])
            maxx = max(maxx, coords[0])
            maxy = max(maxy, coords[1])
            maxz = max(maxz, coords[2])
        return [minx,miny,minz,maxx,maxy,maxz]

    def addMissingFrame(self, frame):
        self.missingFrames.append(frame)

    def getMissingFrames(self):
        return self.missingFrames

    def isMissingFrame(self, frame):
        return frame in self.missingFrames
    
    def getMissingTimeUntilFrame(self,frame):
        """
            For a given frame returns for how many frames this marker was missing up to that frame            
        """
        f = frame-1
        #compute number of continuously missing frames
        while self.isMissingFrame(f):
            f-=1
        return frame-(f+1)

    def setCurrentName(self, name, frame):
        if self.currentName != name:
            self.currentName = name
            self.markerRelabeledTo[frame] = name


    def getAllLabels(self):
        return self.markerLabeledTo

    def setChildMarker(self, marker):
        self.childMarker = marker

    def setParentMarker(self, marker):
        self.parentMarker = marker

    def getChildMarker(self):
        return self.childMarker

    def getParentMarker(self):
        return self.parentMarker

    def getMarkerRelabeledTo(self):
        return self.markerRelabeledTo

    def isMarkerRelabledAt(self, frame):
        return self.markerLabeledToAtFrame[frame] != self.markerLabeledToAtFrame[frame-1]

    def getMeanPosition(self):
        """
            Computes the average position over all frames.
        """
        x_mean = np.mean(np.array([v[0] for v in self.data]))
        y_mean = np.mean(np.array([v[1] for v in self.data]))
        z_mean = np.mean(np.array([v[2] for v in self.data]))
        return [x_mean, y_mean, z_mean]
    
    def getChildVector(self, frame):
        """
            Returns a (np.array) vector from child marker to this marker 
            or [] if this marker has no child marker or the current position is missing
        """
        vector = []
        if self.childVectorAtFrame0 != []:
            return self.childVectorAtFrame0
        else:
            own_pos = np.array(self.getdata(frame))
            if own_pos != [] and self.childMarker != 0:
                vector = own_pos - np.array(self.childMarker.getdata(frame))
                self.childVectorAtFrame = vector     #save to speed up later use.
        return vector
    
    def getParentVector(self, frame):
        """
            Returns a (np.array) vector from parent marker to this marker
            or [] if this marker has no parent marker or the current position is missing
        """
        vector = []
        own_pos = self.getdata(frame)
        if own_pos != [] and self.parentMarker != 0:
            vector = own_pos - np.array(self.parentMarker.getdata(frame))            
        return vector
            
        self.childMarker.getdata(frame)
    
    def plotAtFrame(self, ax, frame, logtext, debug=0):
        #remapped?
        if debug: 
            if self.isMarkerRelabledAt(frame):
                logtext=logtext + self.getname() + " : " + self.getNameAtFrame(frame-1) + " -> " + self.getNameAtFrame(frame)+" \n"
    
        data = self.getdata(frame)
        if data!=[]:
            x_data = (data[0])
            y_data = (data[1])
            z_data = (data[2])
            
            #draw lines between this marker and its child
            childmarker = self.getChildMarker()
            if childmarker != 0:
                childData = childmarker.getdata(frame)
                if childData != []:
                    ax.plot([data[0], childData[0]],[data[1], childData[1]],[data[2], childData[2]],zdir='y',c = '#FA4200', linewidth=1.5)
                    
            #draw lines between this marker and its parent
            parentmarker = self.getParentMarker()
            if parentmarker != 0:
                parentData = parentmarker.getdata(frame)
                if parentData != []:
                    ax.plot([data[0], parentData[0]],[data[1], parentData[1]],[data[2], parentData[2]],zdir='y',c = '#FA4200', linewidth=1.5)
            
            #draw marker point
            ax.scatter(x_data, y_data, z_data, zdir='y',edgecolor='b',c='#04B2E5', marker='o')
                    
        return logtext
        

 
        