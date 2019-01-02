from Take import *

from time import time

start = time()


# the only required argument is the filename:
logfile = "Logfiles/test.csv"

# the following arguments can be given to control the labeling process, see the file Take.py for further description. 
# Here: examples how to specify 
marker_names = []
frame_marker_names = {100:{"Hands_L_L4":"Hands_L_R4", "Hands_L_L3": "Hands_L_L2"}} 
fallback_frames = [2,3] 
labeled_marker_names=["Hands_L_L1"]
check_hand_skeleton_heuristics = 0
use_skeleton = 1
debug = 1
ignore_marker_names = ["Hands_K_right_top", "Hands_K_right_bottom", "Hands_K_left_top"]
plot_every_X_frames = 100

# Create the Take object, which takes care of labeling, plotting and writing the new logfile. 
# Note that only the first argument is required and all others are optional. For the default values, simply write
# t = Take(logfile)


t = Take(logfile, 
         marker_names = marker_names,
         frame_marker_names = frame_marker_names,
         fallback_frames = fallback_frames,
         labeled_marker_names = labeled_marker_names, 
         check_hand_skeleton_heuristics = check_hand_skeleton_heuristics,
         use_skeleton = use_skeleton,
         debug =debug,
         ignore_marker_names = ignore_marker_names,
         plot_every_X_frames = plot_every_X_frames
        )
end = time()

def get_time_format(elapsed):
    hour = (elapsed) // (60*60)
    min = (elapsed - hour * 60*60) // (60)
    sec = elapsed % 60
    return '{:02.0f}:{:02.0f}:{:02.0f}'.format(hour, min, sec)

print("The script ran for ", get_time_format(end - start))