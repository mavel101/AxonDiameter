Created by Sjoerd B. Vos (s.vos@ucl.ac.uk, http://cmictig.cs.ucl.ac.uk/people/research-staff/50-sjoerd-vos)
Translational Imaging Group - Centre for Medical Image Computing
University College London, London, United Kingdom
This code is released under the BSD license (see the license.txt).
Version 1.0 - 16 Jan 2015

The main function (correct_signal_drift.m) was designed to correct for signal drift in diffusion-weighted MRI data as described in Vos et al., MRM 2016, in press (doi:).
This requires multiple b=0-images to be acquired throughout the DWI acquisition.

WARNING - Function is currently only tested for DWI data of the brain using global signal intensities from b=0-images.


DEPENDENCIES:
Please make sure you have the niftimatlib in your Matlab path. It can be downloaded here: http://sourceforge.net/projects/niftilib/files/niftimatlib/niftimatlib-1.2/



Inputs:
As inputs (detailed below) it requires:
1) a nifti (*.nii/*.nii.gz) file with all DWI data; 
2) some information about the diffusion-weighting for each of those images. This can be provided as either a b-value per image, the full gradient table for the acquisition (not compatible with FSL format bvec-file), or the full b-matrix.
3) An additional input can be given to specify the filename of the drift-corrected output nifti. If this is not given the user will be prompted for this filename.
Example usage:
correct_signal_drift('DWI_data.nii.gz', 'DWI_data_bmatrix.txt', 'DWI_data_drift_corr.nii.gz')


Short description:
Signal drift correction is based on the assumption that the global signal intensity (intensity averaged over all voxels within a brain mask ) of b=0-images remains constant throughout the DWI acquisition.
Signal drift is then defined as any structured deviation from a constant signal level. A quadratic (default - with linear also possible) model is fitted to these global b=0-image intensities to estimate signal drift.
From this fit a correction factor is estimated to scale the intensities back to a stable level. The corrected images will then be saved to nifti.
A figure will pop up to show the uncorrected and corrected intensities as well as the fit, specifying the estimated percentage of signal drift (optional - can be turned off).


For experienced diffusion MRI users there are additional parameters to set in the code to allow drift correction in a more flexible way:
- bval_to_use: set the b-value to use for drift correction (default 0) - requires b-value or b-matrix input 
- b_thr:       threshold on how much b-values may deviate from the set bval_to_use value to be included in drift estimation (default 10)


Install/Build
The function has several dependencies that need to be present in the Matlab path in order to run properly. All are included.
1) the niftimatlib library
This is one of many publicly available matlab nifti readers (http://sourceforge.net/projects/niftilib/files/niftimatlib/). The function is tested with version 1.2 (as included)
2) "drift_brainmask.m"
A function to calculate a brain mask within which the signal intensities are averaged. This function is strongly based on the brain mask methods from dr. Alexander Leemans' ExploreDTI (http://www.exploredti.com/).
3) "SaveAsNifTI.m"
A nifti writing function to save the drift-corrected images to *.nii/*.nii.gz. Original function from dr. Gary Zhang's NODDI toolbox (http://www.nitrc.org/projects/noddi_toolbox/) has been adapted to allow gzipped nifti files to be written.