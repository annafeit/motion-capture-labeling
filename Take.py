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
 
import os
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    # The following is necessary if you are running on a headless
    import matplotlib
    matplotlib.use('Agg')

import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from labelMoCapDB import MoCapLabeledDB
import os

# -------- GLOBAL PARAMETERS ----------#


#------ CHANGE HERE -----------
 
class Take:
    
    # For skeleton heuristics to work marker labeling must correspond to the 
    # following naming convention example:  Hands_R_L4
    # - start with "Hands"
    # - the first single letter is R (right) or L (left), corresponding to the hand
    # - the second letter is one of 
    #    - T (thumb)
    #    - I (index)
    #    - M (middle)
    #    - R (ring)
    #    - L (little)
    # - the number is between 1-4 and increases from the MCP joint (1) to the fingertip (4)
    CHECK_HAND_SKELETON_HEURISTICS = 0
    
    # if set to true, the child and parent markers must be defined in the skeleton module.
    # Then sets the child and parent markers for each marker and uses them for interpolating the 
    # position when marker is missing. Also plots lines from child to parent. 
    USE_SKELETON = 1
    
    # Prints the names of the relabeled markers when plotting data of a frame
    DEBUG = 1
    
    # the final marker names as labeled in the first frame. If this is set to [] the script will try to figure them out automatically. Setting them is more reliable
    MARKER_NAMES = []
    
    # the names of the markers that should be ignored while relabeling, e.g. already labeled reference markers
    IGNORED_MARKER_NAMES = []
    
    # if > 0, plots the *labeled* marker data every X frames
    PLOT_EVERY_X_FRAMES = 10000
    
    # hardcoded mapping of to-be-mapped markers on actual marker names in the logfile for certainf frames. Dict from frame to dict of mapping: {int:{string:string}}
    FRAME_MARKER_NAMES = {}
    
    # hardcoded fallback frames which are labeled correctly (1st frame already implicitly included)
    FALLBACK_FRAMES = []
    
    #marker names that we are sure are correctly labeled throughout the whole take. Those will be assumed to be always correct.   
    LABELED_MARKER_NAMES = []  
    
    # Limits of x, y, z axis for plotting the marker data
    PLOT_X_LIM = (-0.5,0.5)
    PLOT_Y_LIM = (-0.5,0.5)
    PLOT_Z_LIM = (-0.5,0.5)      
    
    def __init__(self, filename, 
                 marker_names = [],
                 frame_marker_names=[],
                 fallback_frames = [], 
                 labeled_marker_names=[], 
                 check_hand_skeleton_heuristics=0,
                 use_skeleton=1,
                 debug =1,
                 ignore_marker_names=[],
                 plot_every_X_frames = 10000, 
                 plot_xlim = (-0.5,0.5), 
                 plot_ylim = (-0.5,0.5), 
                 plot_zlim = (-0.5,0.5)):
        """
            filename: the path to the log file                     
        """  
        plt.ioff() #Turns interactive plots off and only shows if wanted.      
        self.markers = []
        self.MARKER_NAMES = marker_names          
        self.file = filename 
        self.FRAME_MARKER_NAMES = frame_marker_names
        self.FALLBACK_FRAMES = fallback_frames
        self.LABELED_MARKER_NAMES = labeled_marker_names
        self.CHECK_HAND_SKELETON_HEURISTICS = check_hand_skeleton_heuristics
        self.USE_SKELETON = use_skeleton
        self.DEBUG = debug
        self.IGNORED_MARKER_NAMES = ignore_marker_names
        self.PLOT_EVERY_X_FRAMES = plot_every_X_frames
        self.PLOT_X_LIM = plot_xlim
        self.PLOT_Y_LIM = plot_ylim
        self.PLOT_Z_LIM = plot_zlim
        
        if not os.path.exists("IMG"):
            os.makedirs("IMG")
    
        self.readIn()
        
        #Write out the relabeled data
        labeledName = self.file.split(".")[0] + "_labeled." + self.file.split('.')[1]
        directory = "/".join(labeledName.split("/")[0:len(labeledName.split("/"))-1]) + "/"
        labeledName = directory + labeledName.split("/")[-1]        
        self.labeledDB.writeOutData(labeledName)
        
        
        
    def readIn(self):
        """
            Reads in the given mocap file, by creating the corresponding MoCapLabeledDB 
            and produces plots of the labeled markers every X frames
        """
        print "START LABELING"
        start_time = time.time()
        mocapfile = self.file
        
            
        #takes care of actually reading it in and labeling it
        labeledDB = MoCapLabeledDB(mocapfile,  
                                   mirrorX=1, #set this to 0 if data seems mirrored
                                   marker_names = self.MARKER_NAMES,
                                   frame_marker_names = self.FRAME_MARKER_NAMES,
                                   fallback_frames = self.FALLBACK_FRAMES,
                                   labeled_marker_names=self.LABELED_MARKER_NAMES,
                                   check_hand_data = self.CHECK_HAND_SKELETON_HEURISTICS,
                                   ignored_markers = self.IGNORED_MARKER_NAMES,
                                   use_skeleton = self.USE_SKELETON
                                   )
        
        
      
        
        self.labeledDB = labeledDB
        self.markers = labeledDB.markers   
        if self.PLOT_EVERY_X_FRAMES > 0:     
            self.save_plots_everyXFrames(x_frames=self.PLOT_EVERY_X_FRAMES)
        
        print "DONE LABELING"
        print "--- %s seconds ---" % (time.time() - start_time)
        
        
    
    def save_plots_everyXFrames(self, x_frames=10000):
        #Save images every 10000 frames, start with first and end with last
        frame=0 
        while frame < int(self.labeledDB.frames-1):
            plotName = "IMG/"+self.file.split("/")[-1].split(".")[0] + "_" + str(frame) + ".png"
            self.plotAt(frame, filename=plotName)
            frame+=x_frames
                    
        #also print last        
        frame = int(self.labeledDB.frames-1)
        plotName = "IMG/"+self.file.split("/")[-1].split(".")[0] + "_" + str(frame) + ".png"
        self.plotAt(frame, filename=plotName)
        
    
    def plotAt(self, frame,
               filename=""):
        """
        plots the data of this study take at the  given frame
        """
                  
        fig = plt.figure(figsize=(18,12))            
        ax = fig.add_subplot(111, projection='3d')
        
    
        debugtext="Remaps: \n" 
        for marker in self.markers:
            debugtext = marker.plotAtFrame(ax, frame, debugtext, self.DEBUG) #actual plotting is done in marker object
            
        if self.DEBUG: 
            mapping_text = ax.text2D(-0.1, 0.8, debugtext , transform=ax.transAxes, va = 'top')
            
                     
        frame_text = ax.text2D(-0.1, 0.95, "Frame: " + str(frame), transform=ax.transAxes)
        
        #adjust limits of X, Y, and Z axis as you like 
        ax.set_xlim3d(self.PLOT_X_LIM)
        ax.set_ylim3d(self.PLOT_Y_LIM)
        ax.set_zlim3d(self.PLOT_Z_LIM)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Z')
        ax.set_zlabel('Y')
        
        ax.view_init(azim=90, elev=70) #takes car of the viewing angle
        if filename == "":
            plt.show()
        else:
            #Store it as an image
            plt.savefig(filename, bbox_inches='tight')
            
            
           