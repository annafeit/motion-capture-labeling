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
    