#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Direct estimation of axon radii using the power law ratio from
Pizzolato: "Axial and radial axonal diffusivities and radii from single encoding strongly diffusion-weighted MRI"
(https://www.sciencedirect.com/science/article/pii/0730725X84901218?via%3Dihub)
"""

import numpy as np
import nibabel as nib
from nipype.interfaces import fsl

path_data = ["../data/study/subject7/session1/spiral_mag_mle/", 
             "../data/study/subject7/session2/spiral_mag_mle/"]
mid = ["159","189"]

# multiplicative/additive factors for gradient or b-values [session1, session2]
g_fac = [1, 1]
g_add = [0, 0]
b_fac = [1, 1]
b_add = [0, 0]

apply_both = False # apply on both gradients/b-values, if False only apply on higher gradient/b-value

t1 = "../data/study/subject7/session1/t1/S3_t1w_mprage_anat_t1w_mprage_anat_20230417120015_3_bet.nii.gz"
wm_mask = "../data/study/subject7/session1/t1/S3_t1w_mprage_anat_t1w_mprage_anat_20230417120015_3_bet_seg.nii.gz"

for k,path in enumerate(path_data):

    sh1 = nib.load(path+f"MID{mid[k]}_AxonDiameter_reco_sh_b6000_powderavg.nii.gz")
    sh2 = nib.load(path+f"MID{mid[k]}_AxonDiameter_reco_sh_b30000_powderavg.nii.gz")
    sh = np.stack([sh1.get_fdata(),sh2.get_fdata()])

    g1 = nib.load(path+"grads_6000.nii").get_fdata()
    g2 = nib.load(path+"grads_30000.nii").get_fdata()
    g = np.stack([g1,g2])

    # Apply factors on g
    if apply_both:
        g[0] += g_add[k]
        g[0] *= g_fac[k]
    g[1] += g_add[k]
    g[1] *= g_fac[k]
    
    # mT/m to T/m
    g *= 1e-3

    # Calculate diffusion parameters
    delta = 15e-3 # s
    Delta = 29.25e-3 # s
    gamma = 42.57e6*2*np.pi # rad*/(T*s)
    b = 1e-6*(gamma*g*delta)**2*(Delta - delta/3) # s/mm²

    if apply_both:
        b[0] += b_add[k]
        b[0] *= b_fac[k]
    b[1] += b_add[k]
    b[1] *= b_fac[k]

    # radial diffusivity from equation 11 of Pizzolato paper
    log = np.divide(sh[0],sh[1],out=np.zeros_like(sh[0]),where=sh[1]>0) * np.sqrt(b[0]/b[1])
    da = np.log(log,out=np.zeros_like(sh[0]),where=log>0) / (b[1]-b[0]) # mm²/s

    # D_0 from "getAxonRadius.m"
    d0 = 2.5e-3 # mm²/s

    # axon radius
    base = 48/7*delta*(Delta-delta/3)*d0*da
    exp = 1/4
    radius = 1e3*np.power(base, exp, out=np.zeros_like(base),where=base>0) # um
    nifti = nib.Nifti1Image(radius, sh1.affine, sh1.header)
    axon_file = path+"AxonRadiusMap_plr.nii.gz"
    nib.save(nifti, axon_file)

    # Register to T1
    mat = path+f"MID{mid[k]}_AxonDiameter_reco_moco_unwarped_bet_meanb0_reg.mat"
    out_file = path+"AxonRadiusMap_plr_reg.nii.gz"
    flt = fsl.FLIRT()
    flt.inputs.in_file = axon_file
    flt.inputs.reference = t1
    flt.inputs.output_type = "NIFTI_GZ"
    flt.inputs.apply_xfm = True
    flt.inputs.in_matrix_file = mat
    flt.inputs.out_file = out_file
    res = flt.run() 

# Load registered images
ax_reg = [nib.load(path+"AxonRadiusMap_plr_reg.nii.gz").get_fdata() for path in path_data]

# Calculate differences only in white matter
mask = nib.load(wm_mask).get_fdata()
ax_diff = ax_reg[1] - ax_reg[0]
ax_diff = ax_diff[mask!=0]

# Print mean difference
print(ax_diff.mean())
