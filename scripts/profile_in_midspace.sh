
# input
if [ "$#" -lt 1 ]; then
    echo "Diffusion file missing"
    exit 1
elif [ "$#" -lt 2 ]; then
    echo "Midspace file missing"
    exit 1
elif [ "$#" -lt 3 ]; then
    echo "T1 file missing"
    exit 1
else
    IN_FILE="$1"
    DWI_MIDSPACE="$2"
    T1_FILE="$3"
fi

IN_FILE_PREFIX=${IN_FILE%%.*}
IN_FILE_PATH=$(dirname $IN_FILE)
DWI_MIDSPACE_PATH=$(dirname $DWI_MIDSPACE)
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Create new directory
WORKDIR="${IN_FILE_PATH}/along_tract_midspace"
mkdir $WORKDIR

# Register diffusion images to midspace
flirt -in "${IN_FILE_PREFIX}_moco_unwarped_meanb0_bet.nii.gz" -ref $DWI_MIDSPACE -out "${WORKDIR}/dwi_reg_midspace_meanb0.nii.gz" -omat "${WORKDIR}/diffusion_to_midspace.mat"

# # Apply registration on SH and grads
flirt -in "${IN_FILE_PREFIX}_sh_b6000_powderavg.nii.gz" -ref $DWI_MIDSPACE -out "${WORKDIR}/sh_b6000_powderavg_reg_midspace.nii.gz" -applyxfm -init "${WORKDIR}/diffusion_to_midspace.mat"
flirt -in "${IN_FILE_PREFIX}_sh_b30000_powderavg.nii.gz" -ref $DWI_MIDSPACE -out "${WORKDIR}/sh_b30000_powderavg_reg_midspace.nii.gz" -applyxfm -init "${WORKDIR}/diffusion_to_midspace.mat"
flirt -in $IN_FILE_PATH/grads_6000.nii -ref $DWI_MIDSPACE -out $WORKDIR/grads_6000.nii.gz -applyxfm -init "${WORKDIR}/diffusion_to_midspace.mat"
flirt -in $IN_FILE_PATH/grads_30000.nii -ref $DWI_MIDSPACE -out $WORKDIR/grads_30000.nii.gz -applyxfm -init "${WORKDIR}/diffusion_to_midspace.mat"
gunzip -f $WORKDIR/grads_6000.nii.gz
gunzip -f $WORKDIR/grads_30000.nii.gz

# Apply on diffusion data
# flirt -in "${IN_FILE_PREFIX}_moco_unwarped_bet.nii.gz" -ref $DWI_MIDSPACE -out "${WORKDIR}/dwi_reg_midspace.nii.gz" -applyxfm -init "${WORKDIR}/diffusion_to_midspace.mat"
# mrconvert -force "${WORKDIR}/dwi_reg_midspace.nii.gz" -fslgrad "${IN_FILE_PREFIX}_moco_unwarped_bet.bvec" "${IN_FILE_PREFIX}_moco_unwarped_bet.bval" "${WORKDIR}/dwi_reg_midspace.mif"

# Mask from midspace image (which is already brain extracted)
fslmaths $DWI_MIDSPACE -bin "${DWI_MIDSPACE_PATH}/midspace_mask.nii.gz"

cp -r ${IN_FILE_PATH}/../../session1/spiral_mag_mle/along_tract_midspace/along_tract $WORKDIR/along_tract
rm $WORKDIR/along_tract/CST_L/CST*.txt

# improved tractography with MrTrix & along-fibre quantification (only CST left atm)
${SCRIPTPATH}/along_tract/along_tract_CST.sh "${WORKDIR}/dwi_reg_midspace.nii.gz" "${T1_FILE%%.*}_bet.nii.gz" "${WORKDIR}/sh_b6000_powderavg_reg_midspace.nii.gz" "${WORKDIR}/sh_b30000_powderavg_reg_midspace.nii.gz" "${DWI_MIDSPACE_PATH}/midspace_mask.nii.gz"

# recalculate axon diameters with along fibre quantified powder-averaged shells
PATH_TRACT=${WORKDIR}/along_tract/CST_L
matlab -nodisplay -r "addpath ${SCRIPTPATH}/../AxonRadiusMapping/;calcAxonAlongTracts('$PATH_TRACT/CST_stats_sh6000.txt', '$PATH_TRACT/CST_stats_sh30000.txt', '$PATH_TRACT/CST_grads_6000.txt', '$PATH_TRACT/CST_grads_30000.txt', 'CST_stats_Axon_afterAFQonShells.txt');exit"
matlab -nodisplay -r "addpath ${SCRIPTPATH}/../AxonRadiusMapping/;calcAxonAlongTracts('$PATH_TRACT/CST_stats_between_regions_sh6000.txt', '$PATH_TRACT/CST_stats_between_regions_sh30000.txt', '$PATH_TRACT/CST_grads_between_regions_6000.txt', '$PATH_TRACT/CST_grads_between_regions_30000.txt', 'CST_stats_between_regions_Axon_afterAFQonShells.txt');exit"
