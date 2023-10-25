#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Convert complex Nifti to magnitude images
"""

import numpy as np
import nibabel as nib
import argparse
import mpcomplex as mp
from dipy.io.image import load_nifti, save_nifti

def main(args):

    # load data
    data, affine = load_nifti(args.in_file)
    mag = abs(data)
    if np.iscomplexobj(data):
        print("Complex denoising.")
        phase = np.angle(data)
    else:
        print("Magnitude denoising.")
        phase = None

    # calculate extent/patch size
    ext = int(np.ceil(np.cbrt(data.shape[-1])))
    if not ext%2:
        ext += 1

    # do denoising
    denoised, sigma, npars = mp.denoise(mag, extent=[ext,ext,ext], shrinkage='frob', algorithm='cordero-grande', phase=phase)

    # remove nans and overflows
    denoised = np.nan_to_num(denoised)
    thresh = 1e38
    denoised[denoised > thresh] = 0
    denoised[denoised < -thresh] = 0

    hdr =  nib.load(args.in_file).header
    hdr.set_data_dtype(denoised.dtype)
    save_nifti(args.out_file+'.nii.gz', data=denoised, affine=affine, hdr=hdr)
    hdr.set_data_dtype(sigma.dtype)
    save_nifti(args.out_file+'_noise_map.nii.gz', data=sigma, affine=affine, hdr=hdr)
    hdr.set_data_dtype(npars.dtype)
    save_nifti(args.out_file+'_npars.nii.gz', data=npars, affine=affine, hdr=hdr)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Do complex PCA denoising with code from Benjamin Ades-Aron (NYU).',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('in_file', type=str, help='Input noisy data.')
    parser.add_argument('out_file', type=str, help='Output denoised data.')

    args = parser.parse_args()

    main(args)
