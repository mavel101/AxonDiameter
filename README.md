# AxonDiameter

Processing for spiral data can be started running scripts/process_spiral.sh #IN_FILE.
Processing for EPI data can be started running scripts/process_epi.sh #IN_FILE #IN_FILE_PA.

Before processing EPI data, the b-vectors should be corrected with the submodule "correctBmatrixOverflow", which corrects for an integer overflow leading to partly wrong b-vectors. Resulting b-vectors have to be transformed to Nifti space with the function "transformForNifti".

## Preprocessing & Axon diameter calculation

Steps 1 & 2 can be interchanged, if only magnitude data is available.

1. Denoising (MRtrix3: "dwidenoise") [1]. If the maximum-likelihood estimator is used for spherical harmonic decomposition (step 8), the denoising is only done to get the noise map.

2. Convert to magnitude data ("nifti2mag.py")
     
3. Gibbs Ringing removal (MRtrix3: "mrdegibbs") [2]

4. EPI:
   - TOPUP (FSL) [3]
   - Eddy (FSL) [4,5,6]

5. Spiral
   - Motion correction (FSL Eddy)

6. Gradient nonlinearity correction (is essential due to high b-values/strong gradients) [7,8]
   - GradientDistortionUnwarp.sh (needs https://github.com/Washington-University/gradunwarp)
   - includes b-vector correction (gradient nonlinearity correction leads to different b-values/b-vectors in different voxels)

7. Brain masking (FSL BET) [9]

8. Spherical harmonic decomposition to get spherical average per shell & per voxel (MRtrix3: amp2sh [11] for complex-denoised data, maximum-likelihood estimator [18] for magnitude data) 
	
9. Take the 0th order spherical harmonic and divide by $\sqrt{4\pi}$ to get the powder average [10]

10. Calculate axon radius maps [12,13]
    
11. Calculate relative SNR maps
       
12. White matter masking of axon radius maps (FSL FAST [14] & FSL FLIRT [15, 16]) 

13. Along-fibre quantification currently only along the left CST (using Dipy for along-fibre quantification [17] and MrTrix for tractography [11])

## Requirements

- MRtrix3 (needs up to commit 3853c58 from https://github.com/lukeje/mrtrix3, that fixes a bug in the Rician bias correction)
- FSL
- gradunwarp (included submodule)
- AxonRadiusMapping (included submodule)
- Python (incl. Numpy, Nibabel 3.2.2 (< version 4))
- Matlab
For along-fibre quantification:
- Dipy
- PyAFQ
- Antspy

## References

1. Cordero-Grande, L. et. al. Complex diffusion-weighted image estimation via matrix recovery under general noise models. NeuroImage, 2019, 200, 391-404, doi: 10.1016/j.neuroimage.2019.06.039

2. Kellner, E; Dhital, B; Kiselev, V.G & Reisert, M. Gibbs-ringing artifact removal based on local subvoxel-shifts. Magnetic Resonance in Medicine, 2016, 76, 1574–1581

3. Jesper L. R. Andersson and Stamatios N. Sotiropoulos. An integrated approach to correction for off-resonance effects and subject movement in diffusion MR imaging. NeuroImage, 125:1063-1078, 2016. 

4. Jesper L. R. Andersson and Stamatios N. Sotiropoulos. An integrated approach to correction for off-resonance effects and subject movement in diffusion MR imaging. NeuroImage, 125:1063-1078, 2016.
   
5. Jesper L. R. Andersson, Mark S. Graham, Eniko Zsoldos and Stamatios N. Sotiropoulos. Incorporating outlier detection and replacement into a non-parametric framework for movement and distortion correction of diffusion MR images. NeuroImage, 141:556-572, 2016.
   
6. Jesper L. R. Andersson, Mark S. Graham, Ivana Drobnjak, Hui Zhang, Nicola Filippini and Matteo Bastiani. Towards a comprehensive framework for movement and distortion correction of diffusion MR images: Within volume movement. NeuroImage, 152:450-466, 2017. 

7. Janke, A., et al. Use of spherical harmonic deconvolution methods to compensate for nonlinear gradient effects on MRI images, MRM, 2004;52(1):115-122
   
8. Glasser, M. et. al. The minimal preprocessing pipelines for the Human Connectome Project. Neuroimage, 2013;80:105-24

9.  S.M. Smith. Fast robust automated brain extraction. Human Brain Mapping, 17(3):143-155, 2002.

10. Afzali, et al. Computing the orientational-average of diffusion-weighted MRI signals: a comparison of different techniques. Scientific Reports, 11:14345, 2021

11. Tournier, J.-D. et. al.. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137

12. Veraart, J. et. al. Noninvasive quantification of axon radii using diffusion MRI, eLife, 9:e49855, 2020

13. Veraart, J. et. al. The variability of MR axon radii estimates in the human white matter, Human Brain Mapping, 42:2201–2213, 2021
          
14. Zhang, Y. and Brady, M. and Smith, S. Segmentation of brain MR images through a hidden Markov random field model and the expectation-maximization algorithm. IEEE Trans Med Imag, 20(1):45-57, 2001.
    
15. M. Jenkinson and S.M. Smith. A global optimisation method for robust affine registration of brain images. Medical Image Analysis, 5(2):143-156, 2001. 

16. M. Jenkinson, P.R. Bannister, J.M. Brady, and S.M. Smith. Improved optimisation for the robust and accurate linear registration and motion correction of brain images. NeuroImage, 17(2):825-841, 2002. 

17. Yeatman, Jason D., Robert F. Dougherty, Nathaniel J. Myall, Brian A. Wandell, and Heidi M. Feldman. 2012. “Tract Profiles of White Matter Properties: Automating Fiber-Tract Quantification” PloS One 7 (11): e49790.

18. Sijbers, J., den Dekker, A. J., Scheunders, P., & Van Dyck, D. (1998). Maximum-likelihood estimation of Rician distribution parameters. IEEE Transactions on Medical Imaging, 17(3), 357–361.
