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
# Marker names must end with "_X" where X is the name given here, e.g. Hands_L_R1
          
def parentLookup(x):
    return {
        'L2':'L1',
        'L3':'L2',
        'L4':'L3',
        'R2':'R1',
        'R3':'R2',
        'R4':'R3',
        'M2':'M1',
        'M3':'M2',
        'M4':'M3',
        'I2':'I1',
        'I3':'I2',
        'I4':'I3',
        'T2':'T1',
        'T3':'T2',
        'T4':'T3',
        'Cin':'Cout',
        'Ain':'Aout',
        'Win':'Wout',
    }.get(x,-1)
    
def childLookup(x):
    return {
        'L1': 'L2',
        'L2': 'L3',
        'L3': 'L4',
        'R1': 'R2',
        'R2': 'R3',
        'R3': 'R4',
        'M1': 'M2',
        'M2': 'M3',
        'M3': 'M4',
        'I1': 'I2',
        'I2': 'I3',
        'I3': 'I4',
        'T1': 'T2',
        'T2': 'T3',
        'T3': 'T4',
        'Cout': 'Cin',
        'Aout': 'Ain',
        'Wout': 'Win',
    }.get(x,-1)
    