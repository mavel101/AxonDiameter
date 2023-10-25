#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Convert complex Nifti to magnitude images
"""

import numpy as np
import nibabel as nib
import argparse
from dipy.denoise.localpca import genpca, mppca
from dipy.io.image import load_nifti, save_nifti

def main(args):

    # load data
    data, affine = load_nifti(args.in_file)
    noise_map,_ = load_nifti(args.noise_map)

    if np.iscomplexobj(data):
        print("Convert to magnitude. Complex input not possible.")
        data = abs(data)

    # calculate the patch radius - cubic root of the number of directions (data.shape[-1]) is the minimum patch size
    patch_radius = int(np.ceil((np.cbrt(data.shape[-1]) - 1) / 2))

    # do denoising
    denoised = genpca(data, sigma=noise_map, mask=None, patch_radius=patch_radius,
                  pca_method='eig', tau_factor=None,
                  return_sigma=False, out_dtype=None)
    # denoised, sigma = mppca(data, patch_radius=patch_radius, return_sigma=True)

    hdr =  nib.load(args.in_file).header
    hdr.set_data_dtype(denoised.dtype)
    save_nifti(args.out_file+'.nii.gz', data=denoised, affine=affine, hdr=hdr)
    # hdr.set_data_dtype(sigma.dtype)
    # save_nifti(args.out_file+'_noise_map.nii.gz', data=sigma, affine=affine, hdr=hdr)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Do PCA denoising with dipy providing a noise map (e.g. from dwidenoise).',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('in_file', type=str, help='Input noisy data.')
    parser.add_argument('noise_map', type=str, help='Input noise map.')
    parser.add_argument('out_file', type=str, help='Output denpoised data.')

    args = parser.parse_args()

    main(args)
