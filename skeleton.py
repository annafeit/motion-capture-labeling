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
 
# A lookup table with the parent-child relation for the markers. 
# Each marker can have only 1 child and 1 parent. 
          
def parentLookup(x):
    return {
        'Hands_R_L2':'Hands_R_L1',
        'Hands_L_L2':'Hands_L_L1',
        'Hands_L_L3':'Hands_L_L2',
        'Hands_L_L4':'Hands_L_L3',
        'Hands_L_R2':'Hands_L_R1',
        'Hands_L_R3':'Hands_L_R2',
        'Hands_L_R4':'Hands_L_R3',
        'Hands_L_M2':'Hands_L_M1',
        'Hands_L_M3':'Hands_L_M2',
        'Hands_L_M4':'Hands_L_M3',
        'Hands_L_I2':'Hands_L_I1',
        'Hands_L_I3':'Hands_L_I2',
        'Hands_L_I4':'Hands_L_I3',
        'Hands_L_T2':'Hands_L_T1',
        'Hands_L_T3':'Hands_L_T2',
        'Hands_L_T4':'Hands_L_T3',
        'Hands_L_Cin':'Hands_L_Cout',
        'Hands_L_Ain':'Hands_L_Aout',
        'Hands_L_Win':'Hands_L_Wout',
        'Hands_R_L3':'Hands_R_L2',
        'Hands_R_L4':'Hands_R_L3',
        'Hands_R_R2':'Hands_R_R1',
        'Hands_R_R3':'Hands_R_R2',
        'Hands_R_R4':'Hands_R_R3',
        'Hands_R_M2':'Hands_R_M1',
        'Hands_R_M3':'Hands_R_M2',
        'Hands_R_M4':'Hands_R_M3',
        'Hands_R_I2':'Hands_R_I1',
        'Hands_R_I3':'Hands_R_I2',
        'Hands_R_I4':'Hands_R_I3',
        'Hands_R_T2':'Hands_R_T1',
        'Hands_R_T3':'Hands_R_T2',
        'Hands_R_T4':'Hands_R_T3',
        'Hands_R_Cin':'Hands_R_Cout',
        'Hands_R_Ain':'Hands_R_Aout',
        'Hands_R_Win':'Hands_R_Wout',
    }.get(x,-1)
    
def childLookup(x):
    return {
        'Hands_L_L1': 'Hands_L_L2',
        'Hands_L_L2': 'Hands_L_L3',
        'Hands_L_L3': 'Hands_L_L4',
        'Hands_L_R1': 'Hands_L_R2',
        'Hands_L_R2': 'Hands_L_R3',
        'Hands_L_R3': 'Hands_L_R4',
        'Hands_L_M1': 'Hands_L_M2',
        'Hands_L_M2': 'Hands_L_M3',
        'Hands_L_M3': 'Hands_L_M4',
        'Hands_L_I1': 'Hands_L_I2',
        'Hands_L_I2': 'Hands_L_I3',
        'Hands_L_I3': 'Hands_L_I4',
        'Hands_L_T1': 'Hands_L_T2',
        'Hands_L_T2': 'Hands_L_T3',
        'Hands_L_T3': 'Hands_L_T4',
        'Hands_L_Cout': 'Hands_L_Cin',
        'Hands_L_Aout': 'Hands_L_Ain',
        'Hands_L_Wout': 'Hands_L_Win',
        'Hands_R_L1': 'Hands_R_L2',
        'Hands_R_L2': 'Hands_R_L3',
        'Hands_R_L3': 'Hands_R_L4',
        'Hands_R_R1': 'Hands_R_R2',
        'Hands_R_R2': 'Hands_R_R3',
        'Hands_R_R3': 'Hands_R_R4',
        'Hands_R_M1': 'Hands_R_M2',
        'Hands_R_M2': 'Hands_R_M3',
        'Hands_R_M3': 'Hands_R_M4',
        'Hands_R_I1': 'Hands_R_I2',
        'Hands_R_I2': 'Hands_R_I3',
        'Hands_R_I3': 'Hands_R_I4',
        'Hands_R_T1': 'Hands_R_T2',
        'Hands_R_T2': 'Hands_R_T3',
        'Hands_R_T3': 'Hands_R_T4',
        'Hands_R_Cout': 'Hands_R_Cin',
        'Hands_R_Aout': 'Hands_R_Ain',
        'Hands_R_Wout': 'Hands_R_Win',
    }.get(x,-1)
    