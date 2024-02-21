#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Convert complex Nifti to magnitude images
"""

import nibabel as nib
import numpy as np
from scipy.ndimage import binary_erosion
import argparse

def main(args):

    file = nib.load(args.in_file)
    data = file.get_fdata()

    kernel_2d = np.array([[0,1,0],
                          [1,1,1],
                          [0,1,0]])

    kernel_3d = np.array([[[0,0,0],
                           [0,1,0],
                           [0,0,0]],
                          [[0,1,0],
                           [1,1,1],
                           [0,1,0]],
                          [[0,0,0],
                           [0,1,0],
                           [0,0,0]]])

    if args.kernel == "2d":
        data_new = np.zeros_like(data)
        for i in range(data.shape[-1]):
            data_new[...,i] = binary_erosion(data[...,i], kernel_2d)
    elif args.kernel == "3d":
        data_new  = binary_erosion(data, kernel_3d)

    nifti_img = nib.Nifti1Image(data_new, affine=file.affine, header=file.header)
    nib.save(nifti_img, args.out_file)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Erode mask with 2D or 3D kernel that contains only directly neighbouring voxels.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('in_file', type=str, help='Input Nifti mask file.')
    parser.add_argument('out_file', type=str, help='Output Nifti mask file.')
    parser.add_argument('-k', '--kernel', default='2d', type=str, help='Erosion kernel, 2d (default) or 3d.')

    args = parser.parse_args()

    main(args)
