"""Finds the phase that maximizes the Kinetic Energy for the ASU CXLS gun

This script uses the IMPACT_IN module and minimize_scalar from scipy.optimize
to find the phase that maximizes the energy gain in the ASU CXLS gun.
It is expected to be run from a slurm scheduler, hence the 
call to the IMPACT-T executable using srun. The input file used is named 
ImpactT_original.in and it is expected that the particle distribution used 
is a single on-axis particle. For this reason, a single core is used.

The user will need to edit the system calls to srun depending on how they 
call the script and the name of the IMPACT-T executable. The same applies 
to the name of the ImpactT.in file that has the variables in it as well as 
the bounds used in the optimization. The values of (-50,25) specified are 
taken from the phase scan of the gun.

The two variables in ImpactT_original.in varied for the phase scan are called
gunPhaseF1 and gunPhaseF2 and they appear as such in the input file. The gun 
used in the CXLS beamline is a semi-travelling wave cavity, hence the 
treatment of the fields using complex fields (where complex part is shifted
 by 90 degrees from the real part).

"""

import os
from impact_input import ImpactIn
import numpy as np
import pyPartAnalysis.read_partial_norm as rpn
from scipy.optimize import minimize_scalar

def getEnergy(phase,impact_file):
# Gets the negative of the kinetic energy for the input phase
    replace_var = ["gunPhaseF1","gunPhaseF2"]
    impact_edit = impact_file.replace(varnames=replace_var,varvals=[phase,phase+90])
  
    # write edited ImpactT.in file to case directory
    impact_edit.write(filename='ImpactT.in')
    
    os.system(f"srun --mpi=pmi2 -n 1 ./ImpactTexe-mpi-short-quad")
    
    ref_df = rpn.read_fort('fort.18')
    return -ref_df.KE.values[-1]

impact_file = ImpactIn(filename="ImpactT_original.in")
f = lambda phase: getEnergy(phase,impact_file)

res = minimize_scalar(f, bounds=(-50,25), method='bounded')

# save the phase that gives the max kinetic energy
with open("maxPhase.npy", 'wb') as f:
    np.save(f, res)
    
