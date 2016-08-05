""" Automatic Labeling of Motion Capture Markers
 motion-capture-labeling
 Version: 1.0
 
 If you use this code for your research then please remember to cite our paper:
 
 Anna Maria Feit, Daryl Weir, and Antti Oulasvirta. 2016. 
 How We Type: Movement Strategies and Performance in Everyday Typing. 
 In Proceedings of the 2016 CHI Conference on Human Factors in Computing Systems (CHI '16). 
 ACM, New York, NY, USA, 4262-4273. 
 DOI: http://dx.doi.org/10.1145/2858036.2858233
 
 Copyright (C) 2016 by Anna Maria Feit, Aalto University, FI.
 
 Permission is hereby granted, free of charge, to any person obtaining a copy of this
 software and associated documentation files (the "Software"), to deal in the Software
 without restriction, including without limitation the rights to use, copy, modify,
 merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 permit persons to whom the Software is furnished to do so, subject to the following
 conditions: The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS",
 WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
 WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN 
 NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
 OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
 OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 """
from mocapMarker import *
from  helper import *
from skeleton import *
from Take import *

import re
import numpy as np


class MoCapLabeledDB:
    """
        Creates the labeled MoCapDB from the full MoCapDB
    """
    #automatically created marker names start with "Marker*". Our labeled names should not start like that
    UNLABELED_MARKER_NAME_REGEX = re.compile("Marker*") 
    
    #unit: meters
    BBOX_THRESH = 0.03 #unit: meters    
    MARKER_DIST_THRESH = 0.015 #threshold distance how far the marker is allowed to move from one frame to another
    MARKER_DIST_MISSING_THRESH = 0.03 #threshold distance how far the marker is allowed to move when it disappeared
    
    # For skeleton heuristics  
    CROSSOVER_THRESH = 0.005 #threshold distance for detecting if two bones are crossed (should be "close enough" because the lines never really cross in 3D space)
    BACKWARDS_TIP_THRESH = 2.0 #threshold for detecting backwards tip. min angle in rad 
    
                           

    def __init__(self, datafile,         
                 mirrorX=1,  
                 marker_names = [],
                 frame_marker_names={},
                 fallback_frames=[], 
                 labeled_marker_names=[],
                 check_hand_data = 1,
                 ignored_markers = [],
                 use_skeleton=1):
        
        self.datafile = datafile
        self.frame_marker_names = frame_marker_names                            #{int:{string:string}} for a certain frame fix to-be-labeled names on marker names
        self.fallback_frames = fallback_frames  
        self.ignoredMarkerNames = ignored_markers
        self.mirrorX = mirrorX        
        self.fixedLabeledMarkers = labeled_marker_names
        self.lastbbox = []                                                      # Akku variable to store last proper bounding box in case there is a frame without any data
        self.check_hand_data = check_hand_data   
      
        #get the mocap lines
        f = open(datafile, 'r')
        data_in = f.read().splitlines()        
        f.close()
        
        # Get the names of the markers from the fourth line of text.        
        text = data_in.pop(3)
        items = text.split(',')[2:]    #the first two columns are Frame and Time
        self.allOriginalNames = []
        for n in range(0, len(items), 3):
            self.allOriginalNames.append(items[n]) 
        
        self.markers = []           # Instances of mocapMarker
        self.bbox_width = 0         # x axis
        self.bbox_height = 0        # y axis
        self.bbox_length = 0        # z axis
                
        del data_in[0:6]
        self.frames = len(data_in) #TODO: check that deleting the first 6 lines is actually correct after popping 3 already
        self.firstFrame = int(data_in[0].split(',')[0])  
        self.lastFrame =  self.firstFrame + len(data_in)      
                
        # Get the labeled names and create marker objects
        names = self.allOriginalNames
        self.allNames= [l for l in names  if not l in self.ignoredMarkerNames]       # String[]: all valid marker names, labeled or automatically created
        if marker_names == []:
            labeledNames = [l for l in names for m in [self.UNLABELED_MARKER_NAME_REGEX.search(l)] if not m]           
            labeledNames = [l for l in labeledNames if not l in self.ignoredMarkerNames] #Filter out ignored marker names
            print "Inferred the following marker names:", labeledNames                                                 
        else:
            labeledNames = marker_names    
            
        # Initialize markers
        for name in labeledNames:
            self.markers.append(MoCapMarker(name, self.firstFrame, self.lastFrame, name))        
        self.names = [l.name for l in self.markers]                             # String[]: initially labeled names. Those we try to fill.    
        
        #Init with data from first frame.
        firstFrameData = self.get_rawdata(data_in, 0, mirrorX)
        for m in self.markers:
            m.append(firstFrameData[m.name])
                    
        # set parent-child relations for skeleton tree
        if use_skeleton:
            self.initSkeleton()        
        
        self.getdata(data_in)
                 

    def get_rawdata(self, data_in, frame, mirrorX):        
        """
            Input: 
            data_in: the original data line by line from the logfile
            frame: the line to be looked at
            
            Output: {String:[array]}
            Dictionary from marker name to position at given frame. Only those markers that have a position.
            Mirrors x component if requested.
        """
        rawdata = {}
               
        row = data_in[frame]
        all_rowdata = row.split(',')
        if len(all_rowdata)<len(self.names):
            all_rowdata = row.split('\t')
            
        data = all_rowdata[2:] # Ignore the values of Field & Time
        index = 0          
        for n in range(0, len(data), 3):                
            if not data[n] == "":                
                if self.mirrorX:
                    datapoint = [float(-1)*float(data[n]), float(data[n+1]), float(data[n+2])]                    
                else:
                    datapoint = [float(data[n]), float(data[n+1]), float(data[n+2])]
                    
            else: 
                datapoint = []
            n = self.allOriginalNames[index]
            if not n in self.ignoredMarkerNames:
                rawdata[n] = datapoint 
                           
            index += 1
            
        
        return rawdata
                
 

    def getdata(self, data_in):
        """
            Fills the markers with data. At every frame relabels ALL data points according to nearest neighbor
        """
        #in every frame get the original data and remap the whole point cloud.    
        for frame in range(1,self.frames):
            if ((frame%1000)==0):
                print "Frame", frame, "/", self.frames
            #get the data from that frame and relabel
            logdata = self.get_rawdata(data_in, frame, self.mirrorX)
            self.relabelAllMarkers(frame, logdata)
                        
            #some heuristics for better labeling if this is mocap data from hands and labeled correctly
            if self.check_hand_data and "Hands_R_T4" in self.names: #just checking one random name to see if it has the right naming convention 
                self.check_fingerCrossover(frame)
                self.check_backwardsTip(frame)
                            

    

    def relabelAllMarkers(self, frame, logdata,checkPosition=1, refFrame=-1, output=1):
        """
            Used to remap all markers to closest neighbor. Keeps marker.currentname updated
            If two markers are closest to the same marker, only the closest one is mapped.
            The other is marked as missing            
        """
        #-----> hardcoded fallback frames: 
        not_remappedMarkers = []
        if frame in self.fallback_frames:            
            for marker in self.markers:
                if logdata[marker.name] != []:
                    marker.append(logdata[marker.name])
                else:                    
                    not_remappedMarkers.append(marker)
            print "--> Hardcoded groundtruth at", str(frame)
            if not_remappedMarkers != []:
                self.markAsMissing(not_remappedMarkers, frame, refFrame)
            return 0
        
        #-----> case that marker known to be labeled correctly throughout log or for this specific frame
        alreadyLabeled = []
        for marker in self.markers:
            if marker.name in self.fixedLabeledMarkers and marker.name in logdata.keys():
                if logdata[marker.name] != []:
                    marker.append(logdata[marker.name])
                    logdata.pop(marker.name,0)
                    alreadyLabeled.append(marker.name)     
            elif frame in self.frame_marker_names:
                marker_map = self.frame_marker_names[frame]
                if marker.name in marker_map:
                    new_name = marker_map[marker.name]
                    if logdata[new_name] != []:
                        marker.append(logdata[new_name])
                        logdata.pop(new_name,0)
                        alreadyLabeled.append(marker.name)                          
                        print "--> Hardcoded groundtruth at", str(frame), "for", marker.name
            
        if refFrame==-1:
            refFrame = frame-1

        #the position in last frame
        lastMarkerData = {m.name:m.getdata(refFrame) for m in self.markers}

        #the unlabeled markers of this frame
        #consider only those markers that
        #(1) have data and that
        #(2) are inside the
        #bounding box of last frame + thresh
        db_unlabeledMarkers = {}

        bbox = self.getBbox(frame-1)
        if(bbox[0] > 100000):
            bbox = self.lastbbox

        bbox = [bbox[0]-self.BBOX_THRESH, \
                bbox[1]-self.BBOX_THRESH, \
                bbox[2]-self.BBOX_THRESH, \
                bbox[3]+self.BBOX_THRESH, \
                bbox[4]+self.BBOX_THRESH, \
                bbox[5]+self.BBOX_THRESH]
        self.lastbbox = bbox


        for n, db_data in logdata.iteritems():            
            #(1)
            if db_data != []:
                #(2)
                if helper.insideBoundingBox(db_data, bbox):
                    db_unlabeledMarkers[n] = db_data

        # Now try to label according to nearest neighbor 
        distance = 0
        missingData = 0
        
        not_remappedMarkers = []
        if db_unlabeledMarkers!= {}:
            nearestNeighborMapping = helper.nearestNeighbor(lastMarkerData, db_unlabeledMarkers, self, frame)

            for marker in self.markers:
                if marker.name in alreadyLabeled:
                    continue
                nearestNeighbor = nearestNeighborMapping[marker.name] #dictionary missingmarkername->[newmarkername,dist]
                if len(nearestNeighbor)>0:

                    newName = nearestNeighbor[0]
                    oldName = marker.currentName
                    newdata = db_unlabeledMarkers[newName]
                    olddata = lastMarkerData[marker.name]
                    if newdata == []:
                        print "data of nearest neighbor is empty, something's wrong"
                    
                    if checkPosition:
                        if self.checkNewPosition(marker, frame, olddata, newdata):
                            #take care of naming
                            marker.setCurrentName(newName, frame)
                            marker.append(newdata)          
                            
                            distance += nearestNeighbor[1]
                            
                            if marker.isMissingFrame(frame-1) and output:
                                print "Relabeled: ", oldName, "to", newName, "at frame", frame
                                print "Marker", marker.name, "was missing for", marker.getMissingTimeUntilFrame(frame), "frames"
                        else:                        
                            not_remappedMarkers.append(marker)     
                            missingData += 1
                    else:
                        #take care of naming
                        marker.setCurrentName(newName, frame)
                        marker.append(newdata)            
                        
                        distance += nearestNeighbor[1]
                        
                        if marker.isMissingFrame(frame-1) and output:
                            print "Relabeled: ", oldName, "to", newName, "at frame", frame
                            print "Marker", marker.name, "was missing for", marker.getMissingTimeUntilFrame(frame), "frames"         

                #if empty, label as before and mark as missing
                else:
                    not_remappedMarkers.append(marker)            
                            
            #mark all markers as missing that could not be labeled        
            distance += self.markAsMissing(not_remappedMarkers, frame, refFrame)


        else:
            print "There is no marker data in this frame."
            distance += self.markAsMissing(self.markers, frame, refFrame)
            
        
        return distance
        
    
    def checkNewPosition(self, marker, frame, old, new):
        """
            Checks the new position for the given marker at the given frame.
            Checks if:
            (1) new position is inside the allowed bounding box of the hand
            (2) new position is inside threshold of old position
        """
        validity = 1
        #(1)
        bbox = self.getBbox(frame-1)
        if(bbox[0] > 100000):
            bbox = self.lastbbox

        bbox = [bbox[0]-self.BBOX_THRESH, \
                bbox[1]-self.BBOX_THRESH, \
                bbox[2]-self.BBOX_THRESH, \
                bbox[3]+self.BBOX_THRESH, \
                bbox[4]+self.BBOX_THRESH, \
                bbox[5]+self.BBOX_THRESH]
        self.lastbbox = bbox

        if not helper.insideBoundingBox(new, bbox):
            validity = 0

        #(2)
        wasMissing = marker.isMissingFrame(frame-1)
        if not self.isWithinMarkerThresh(wasMissing, old, new):
            validity = 0

        return validity


    def isWithinMarkerThresh(self, wasMissing, point1, point2):
        """
            Checks if the distance between two marker points (e.g. old and new position)
            is below a threshold. Different threshold depending on if marker
            was missing last frame or not.
        """
        diffV = np.array(point1) - np.array(point2)
        dist = np.absolute(np.linalg.norm(diffV))
        if wasMissing:
            return dist < self.MARKER_DIST_MISSING_THRESH
        else:
            return dist < self.MARKER_DIST_THRESH


   

    
    def markAsMissing(self, markers, frame, refFrame=-1):
        
        if refFrame == -1:
            refFrame = frame-1
            
        distance = 0
        #sort markers to have parents before children.
        markers = sorted(markers, key=lambda x: x.name)
        for marker in markers:
            #marker.append(marker.getdata(frame-1))
            self.extrapolateMarker(marker, frame, refFrame)
            marker.addMissingFrame(frame)
            distance += np.linalg.norm(np.array(marker.getdata(frame))-np.array(marker.getdata(refFrame)))
        return distance

    def extrapolateMarker(self, marker, frame, refFrame=-1):
        """
            Extrapolates the marker based on the parent and child markers. 
            Takes the vector of the previous frame from parent and child marker to this marker
            and computes the new position based on the new position of parent and child marker
            + the vector from last frame. 
            If both, parent and child marker are missing as well, it appends the 
            position from last frame.  
        """
        if refFrame == -1:
            refFrame = frame-1
            
        parentMarker = marker.getParentMarker()
        childMarker = marker.getChildMarker()
        
        parentVector = marker.getParentVector(refFrame)
        childVector = marker.getChildVector(refFrame)
        
        extr_pos = []
        if parentVector != []: 
            parentPos = parentMarker.getdata(frame)
            if parentPos != []:
                extr_pos = np.array(parentPos) + parentVector
        
        if childVector != []:
            childPos = childMarker.getdata(frame)
            if childPos != []:
                extr_pos_child = np.array(childPos) + childVector
                if extr_pos != []:
                    extr_pos = np.mean([extr_pos_child, extr_pos], 0)
                else:
                    extr_pos = extr_pos_child
        
        
        if extr_pos == []:
            #has no child nor parent marker or both are missing.  
            extr_pos = marker.getdata(frame-1)
        #else:
            #print "Marker", marker.name , "extrapolated at frame", str(frame)
        extr_pos = [extr_pos[0], extr_pos[1], extr_pos[2]]     #fram np.array -> array
        marker.append(extr_pos)
        
    

    def getBboxPlusThresh(self, frame):
        bbox = self.getBbox()
        if(bbox[0] > 100000):
            bbox = self.lastbbox

            bbox = [bbox[0]-self.BBOX_THRESH, \
                    bbox[1]-self.BBOX_THRESH, \
                    bbox[2]-self.BBOX_THRESH, \
                    bbox[3]+self.BBOX_THRESH, \
                    bbox[4]+self.BBOX_THRESH, \
                    bbox[5]+self.BBOX_THRESH]
            self.lastbbox = bbox
        return bbox

    def getBbox(self, frame=-1):
        """
            Computes the bounding box around the whole marker space
        """
        if(frame==-1):
            minx = miny = minz = MoCapMarker.MIN
            maxx = maxy = maxz = MoCapMarker.MAX
            for m in self.markers:
                bbox = m.getBbox()
                if len(bbox) > 0:
                    minx = min(minx, bbox[0])
                    miny = min(miny, bbox[1])
                    minz = min(minz, bbox[2])
                    maxx = max(maxx, bbox[0])
                    maxy = max(maxy, bbox[1])
                    maxz = max(maxz, bbox[2])
            self.bbox_width =  abs(maxx - minx)
            self.bbox_height = abs(maxy - miny)
            self.bbox_length = abs(maxz - minz)
            return [minx,miny,minz,maxx,maxy,maxz]
        else:
            #return bounding box for given frame
            minx = miny = minz = MoCapMarker.MIN
            maxx = maxy = maxz = MoCapMarker.MAX
            for m in self.markers:
                data = m.getdata(frame)
                if len(data) > 0:
                    minx = min(minx, data[0])
                    miny = min(miny, data[1])
                    minz = min(minz, data[2])
                    maxx = max(maxx, data[0])
                    maxy = max(maxy, data[1])
                    maxz = max(maxz, data[2])
            self.bbox_width =  abs(maxx - minx)
            self.bbox_height = abs(maxy - miny)
            self.bbox_length = abs(maxz - minz)
            return [minx,miny,minz,maxx,maxy,maxz]

    def writeOutData(self, filename, orig=0):
        print "WRITING DATA"
        datafile = self.datafile
        newFilename = filename
        if orig:
            newFilename = filename+"_orig"
        f_new = open(newFilename, 'w')

        #get old data
        f_orig = open(datafile, 'r')
        original = f_orig.readlines()
        f_orig.close

        #Write data
        #Header from original file and marker names
        f_new.write(original[0] + "\n"+ "\n")
        markerline = ","
        columnline = "Frame, Time"
        for n in self.names:
            markerline = markerline + "," + n + "," + n + "," + n
            columnline = columnline + ",X,Y,Z"
        f_new.write(markerline + "\n")
        f_new.write("\n\n")
        f_new.write(columnline + "\n")

        #Entries
        for i in range(0,self.frames):
            line_i = i+7
            #Frame and time from original file
            orig_entry = original[line_i].split(",")
            new_entry = orig_entry[0] + "," + orig_entry[1] #frame and time
            for m in self.markers:
                new_entry = new_entry + m.getDataToString(i, sep=",")
            f_new.write(new_entry + "\n")

        f_new.close()
        print "DONE"

    def getMarkerData(self, index, begin, end, step):
        """
            Given the index of a marker, getMarkerData() returns a list of
            coordinates for the specified frame range (begin to end).
        """
        out = []
        marker = self.markers[index]
        if begin == end:
            end = begin + step
            step = 1
        for frame in range(begin, end, step):
            data = marker.getdata(frame)
            if len(data) > 0:
                out.extend(data)
        return out

    def getMarkerByName(self, marker_name, begin=0, end=0, step=0):
        """
            return the data of the corresponding marker.
            Return the whole marker if begin, end, step are 0
        """

        index = self.names.index(marker_name)

        if (self.markers[index].getname() != marker_name):
            print 'indexing of marker names wrong'
            return 0
        else:
            if(begin == end == step == 0):
                #return the whole marker
                return self.markers[index]
            else:
                #return requested frame
                return self.getMarkerData(index, begin, end, step)

    def initSkeleton(self):
        """
            sets the neighbor relations of the hand skeleton within the marker
        """
        for marker in self.markers:
            name = marker.getname()
            #child
            childname = childLookup(name)
            if childname != -1:
                try:
                    childmarker = self.getMarkerByName(childname)
                except ValueError:
                    #Marker not in the list, missing from log entirely.
                    print "Marker not in list", childname
                    childmarker = 0
                marker.setChildMarker(childmarker)

            #parent
            parentname = parentLookup(name)
            if parentname != -1:                
                try:
                    parentmarker = self.getMarkerByName(parentname)
                except ValueError:
                    #Marker not in the list, missing from log entirely.
                    print "Marker not in list", parentname
                    parentmarker = 0
                marker.setParentMarker(parentmarker)

    def getMarkers(self):
        return self.markers

    def numframes(self):
        """
            Returns the number of frames
        """
        return self.frames


    
   
#------------------------------------------------------------------------------
# Note, this is HARDCODED. 
# Works only if the markers are labeled as described in the intro.
# Otherwise gives a warning
#------------------------------------------------------------------------------

    def check_fingerCrossover(self, frame):
        """
            Checks if the markers of 2 neighboring fingers are switched:
            If t3-t4 bones are crossed, switch t4 marker data
            If t3-t4 AND t3-t2 are crossed, switch t3 data
        """
        #check if the names follow our naming convention: 
        try:
            fingerpairs = [('R_T','L_T'), ('R_L','R_R'), ('L_R','L_L') , ('R_R','R_M'), ('L_M','L_R'), ('R_M','R_I'), ('L_I','L_M')]
            for (i1,i2) in fingerpairs:
                if i1=='R_T':
                    if not 'Hands_R_T3' in [m.name for m in self.markers]:
                        return
                if "Hands_"+i1+"1" in self.names and "Hands_"+i2+"1" in self.names:  
                    L_1 = self.getMarkerByName("Hands_"+i2+"1")
                    R_1 = self.getMarkerByName("Hands_"+i1+"1")   
                R_2 = self.getMarkerByName("Hands_"+i1+"2")
                R_3 = self.getMarkerByName("Hands_"+i1+"3")
                R_4 = self.getMarkerByName("Hands_"+i1+"4")
                
                L_2 = self.getMarkerByName("Hands_"+i2+"2")
                L_3 = self.getMarkerByName("Hands_"+i2+"3")
                L_4 = self.getMarkerByName("Hands_"+i2+"4")
                
                #check if they are close enough
                if helper.closest3d(R_3.getdata(frame), R_4.getdata(frame),  L_3.getdata(frame), L_4.getdata(frame), infinite=0)<= self.CROSSOVER_THRESH:
                    if helper.closest3d(R_2.getdata(frame), R_3.getdata(frame),  L_2.getdata(frame), L_3.getdata(frame), infinite=0)<= self.CROSSOVER_THRESH:
                        #switch t3 data oNLY if it would help
                        if helper.closest3d(R_2.getdata(frame), L_3.getdata(frame),  L_2.getdata(frame), R_3.getdata(frame), infinite=0)> self.CROSSOVER_THRESH and\
                        helper.closest3d(L_3.getdata(frame), R_4.getdata(frame),  R_3.getdata(frame), L_4.getdata(frame), infinite=0)> self.CROSSOVER_THRESH:
                            self._swapMarkerData(frame, R_3, L_3)
                            print "Swapped",  R_3.name, "and", L_3.name, "at frame ", str(frame)
                    else:
                        #switch t4 data ONLY If it would help
                        if helper.closest3d(R_3.getdata(frame), L_4.getdata(frame),  L_3.getdata(frame), R_4.getdata(frame), infinite=0)> self.CROSSOVER_THRESH:
                            self._swapMarkerData(frame, R_4, L_4)
                            print "Swapped",  R_4.name, "and", L_4.name, "at frame ", str(frame)  
                elif helper.closest3d(R_2.getdata(frame), R_3.getdata(frame),  L_2.getdata(frame), L_3.getdata(frame), infinite=0)<= self.CROSSOVER_THRESH:
                    if helper.closest3d(R_2.getdata(frame), L_3.getdata(frame),  L_2.getdata(frame), R_3.getdata(frame), infinite=0)> self.CROSSOVER_THRESH:                
                        #switch both t4 and t3 data ONLY if it would help
                        self._swapMarkerData(frame, R_3, L_3)
                        self._swapMarkerData(frame, R_4, L_4)
                #only 1-2 bones are crossed. find out what to switch            
                elif "Hands_"+i1+"1" in self.names and "Hands_"+i2+"1" in self.names: 
                    if helper.closest3d(R_1.getdata(frame), R_2.getdata(frame),  L_1.getdata(frame), L_2.getdata(frame), infinite=0)<= self.CROSSOVER_THRESH:
                        #if the 2, 3, and 4 markers of the finger on the rigth (first one) are not on the right, switch all those. else do nothing, only the knuckle markers are somehow wrong            
                        if R_2.getdata(frame)[0] < L_2.getdata(frame)[0] and R_3.getdata(frame)[0] < L_3.getdata(frame)[0] and R_4.getdata(frame)[0] < L_4.getdata(frame)[0]:
                            #switch both t4 and t3 and t2 data ONLY if it would help
                            self._swapMarkerData(frame, R_2, L_2)
                            self._swapMarkerData(frame, R_3, L_3)
                        self._swapMarkerData(frame, R_4, L_4)
            
            for (i1,i2) in fingerpairs:
                R_2 = self.getMarkerByName("Hands_"+i1+"2")
                R_3 = self.getMarkerByName("Hands_"+i1+"3")
                R_4 = self.getMarkerByName("Hands_"+i1+"4")
                L_2 = self.getMarkerByName("Hands_"+i2+"2")
                L_3 = self.getMarkerByName("Hands_"+i2+"3")
                L_4 = self.getMarkerByName("Hands_"+i2+"4")
                
                #L4-3 and R2-3, check if they are close enough
                if helper.closest3d(L_3.getdata(frame), L_4.getdata(frame),  R_2.getdata(frame), R_3.getdata(frame))<= self.CROSSOVER_THRESH:
                    #switch L4, R3 data ONLY if it would help
                    if helper.closest3d(L_3.getdata(frame), R_3.getdata(frame),  R_2.getdata(frame), L_4.getdata(frame))> self.CROSSOVER_THRESH:
                        self._swapMarkerData(frame, R_3, L_4)
                        print "Swapped",  R_3.name, "and", L_4.name, "at frame ", str(frame)
                #L2-3 and R3-4, check if they are close enough
                elif helper.closest3d(L_2.getdata(frame), L_3.getdata(frame),  R_3.getdata(frame), R_4.getdata(frame))<= self.CROSSOVER_THRESH:                            
                    #switch R4, L3 data, ONLY if it would help!
                    if helper.closest3d(L_2.getdata(frame), R_4.getdata(frame),  R_3.getdata(frame), L_3.getdata(frame))> self.CROSSOVER_THRESH:
                        self._swapMarkerData(frame, L_3, R_4) 
                        print "Swapped",  L_3.name, "and", R_4.name, "at frame ", str(frame)
            
        except Exception:
            print ("WARNING: finger cross check not possible, marker names not recognized.")
                
    def check_backwardsTip(self, frame):
        """
            Check if there is this steep angle between at the fingertip where the fingertip points backwards.
            If so, switch 3 and 4 marker.
        """
        try:
            fingertips = ['R_T', 'R_I', 'R_M', 'R_R', 'R_L', 'L_T', 'L_I', 'L_M', 'L_R', 'L_I']
            for f in fingertips:
                if f=='R_T':
                    if not 'Hands_R_T3' in [m.name for m in self.markers]:
                        return
                    
                M2 = self.getMarkerByName('Hands_'+f+'2')
                M3 = self.getMarkerByName('Hands_'+f+'3')
                M4 = self.getMarkerByName('Hands_'+f+'4')
                
                b23 = np.array(M3.getdata(frame)) - np.array(M2.getdata(frame))
                b34 = np.array(M4.getdata(frame)) - np.array(M3.getdata(frame))
                
                #swapped
                b24 = np.array(M4.getdata(frame)) - np.array(M2.getdata(frame))
                b43 = np.array(M3.getdata(frame)) - np.array(M4.getdata(frame))
                
                if helper.angle_between(b23, b34) >= self.BACKWARDS_TIP_THRESH:
                    #switch 3 and 4 data, ONLUY if it would help
                    if helper.angle_between(b24, b43) < self.BACKWARDS_TIP_THRESH:
                        self._swapMarkerData(frame, M3, M4)
                    
        except Exception:
            print ("WARNING:backwards tip check not possible, marker names not recognized.")
                
    def _swapMarkerData(self, frame, M3, M4):        
        tmp = M3.data[frame]
        tmp_name = M3.currentName
        
        M3.data[frame] = M4.data[frame]                
        M3.currentName = M4.currentName
        M3.markerRelabeledTo[frame] = M3.currentName
        
        M4.data[frame]= tmp
        M4.currentName = tmp_name
        M4.markerRelabeledTo[frame] = M3.currentName
        
        if M3.isMissingFrame(frame):
            M4.missingFrames.append(frame)
        if M4.isMissingFrame(frame):
            M3.missingFrames.append(frame)
            

    