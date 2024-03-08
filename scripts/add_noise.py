from skimage import util
import nibabel as nib
import numpy as np

# Load image
img = nib.load("/home/veldmannm/home/Projects/AxonDiameter/data/study/subject1/session1/spiral_mag_mle_extra_noise/MID30_AxonDiameter_reco_orig.nii.gz")
img_data = img.get_fdata(dtype=np.complex64)

# Add noise
rng = np.random.default_rng(None)
mean = 0
std_noise_map = 0.0027
fac = 0.5
noise = rng.normal(mean, fac*std_noise_map, img_data.shape[:-1]) \
      + 1j* rng.normal(mean, fac*std_noise_map, img_data.shape[:-1])

for k, img_k in enumerate(img_data.T):
    img_data[...,k] = img_k.T + noise

# Save image
img_new = nib.Nifti1Image(img_data, affine=img.affine, header=img.header)
nib.save(img_new, "/home/veldmannm/home/Projects/AxonDiameter/data/study/subject1/session1/spiral_mag_mle_extra_noise/MID30_AxonDiameter_reco.nii.gz")
