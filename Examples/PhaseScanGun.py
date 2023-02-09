"""Runs a phase scan of the ASU CXLS gun

This script uses the IMPACT_IN module to perform a phase scan for the CXLS 
gun. It is expected to be run from a slurm scheduler, hence the 
call to the IMPACT-T executable using srun. The input file used is named 
ImpactT_original.in and it is expected that the particle distribution used 
is a single on-axis particle. For this reason, a single core is used.

The user will need to edit the system calls to srun depending on how they 
call the script and the name of the IMPACT-T executable. The same applies 
to the name of the ImpactT.in file that has the variables in it.

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

# --------User specified Values--------
num_data_points = 106
min_phase = -80
max_phase = 135
# --------------------------------------

gun_phase_vals = np.linspace(min_phase,max_phase,num_data_points)
replace_var = ["gunPhaseF1","gunPhaseF2"]

KE_ouput = []

# save phase values to file
with open("gun_Phase.npy", 'wb') as f:
    np.save(f, gun_phase_vals)

# read in original ImpactT.in file
impact_file = ImpactIn(filename="ImpactT_original.in")

for ind,val in enumerate(gun_phase_vals):
    # replace phase values
    impact_edit = impact_file.replace(varnames=replace_var,varvals=[val,val+90])
  
    # write edited ImpactZ.in file to case directory
    impact_edit.write(filename='ImpactT.in')
    
    # write output to screen and run simulation
    print(f"run {ind} of {num_data_points}")
    os.system(f"srun --mpi=pmi2 -n 1 ./ImpactTexe-mpi-short-quad")
    
    # get energy at output
    ref_df = rpn.read_fort('fort.18')
    KE_ouput.append(ref_df.KE.values[-1])
    
# save average kinetic energy to file
with open("gun_Energy.npy", 'wb') as f:
    np.save(f, KE_ouput)
