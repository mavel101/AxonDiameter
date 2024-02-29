
# input
if [ "$#" -lt 1 ]; then
    echo "Diffusion file missing"
    exit 1
elif [ "$#" -lt 2 ]; then
    echo "T1 file missing"
    exit 1
else
    IN_FILE="$1"
    T1_FILE="$2"
fi

IN_FILE_PREFIX=${IN_FILE%%.*}
IN_FILE_PATH=$(dirname $IN_FILE)
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Register axon diameter maps to midway space
flirt -in "${IN_FILE_PREFIX}_moco_unwarped_meanb0_bet.nii.gz" -ref "${IN_FILE_PATH}/../../dwi_midspace/dwi_midspace_meanb0_bet.nii.gz" -out "${IN_FILE_PREFIX}_moco_unwarped_meanb0_bet_midspace.nii.gz" -omat "${IN_FILE_PATH}/midspace_transform.mat"
flirt -in "${IN_FILE_PATH}/AxonRadiusMap.nii" -ref "${IN_FILE_PATH}/../../dwi_midspace/dwi_midspace_meanb0_bet.nii.gz" -out "${IN_FILE_PATH}/AxonRadiusMap_midspace.nii.gz" -applyxfm -init "${IN_FILE_PATH}/midspace_transform.mat" -interp spline
flirt -in "${IN_FILE_PREFIX}_sh_b6000_powderavg.nii.gz" -ref "${IN_FILE_PATH}/../../dwi_midspace/dwi_midspace_meanb0_bet.nii.gz" -out "${IN_FILE_PREFIX}_sh_b6000_powderavg_midspace.nii.gz" -applyxfm -init "${IN_FILE_PATH}/midspace_transform.mat" -interp spline
flirt -in "${IN_FILE_PREFIX}_sh_b30000_powderavg.nii.gz" -ref "${IN_FILE_PATH}/../../dwi_midspace/dwi_midspace_meanb0_bet.nii.gz" -out "${IN_FILE_PREFIX}_sh_b30000_powderavg_midspace.nii.gz" -applyxfm -init "${IN_FILE_PATH}/midspace_transform.mat" -interp spline
flirt -in "${IN_FILE_PATH}/grads_6000.nii" -ref "${IN_FILE_PATH}/../../dwi_midspace/dwi_midspace_meanb0_bet.nii.gz" -out "${IN_FILE_PATH}/grads_6000_midspace.nii.gz" -applyxfm -init "${IN_FILE_PATH}/midspace_transform.mat" -interp spline
flirt -in "${IN_FILE_PATH}/grads_30000.nii" -ref "${IN_FILE_PATH}/../../dwi_midspace/dwi_midspace_meanb0_bet.nii.gz" -out "${IN_FILE_PATH}/grads_30000_midspace.nii.gz" -applyxfm -init "${IN_FILE_PATH}/midspace_transform.mat" -interp spline

# improved tractography with MrTrix & along-fibre quantification (only CST left atm)
${SCRIPTPATH}/along_tract/along_tract_CST_midspace.sh "${IN_FILE_PATH}/../../dwi_midspace/dwi_midspace.nii.gz" "${T1_FILE%%.*}_bet.nii.gz" "${IN_FILE_PREFIX}_sh_b6000_powderavg.nii.gz" "${IN_FILE_PREFIX}_sh_b30000_powderavg.nii.gz" "${IN_FILE_PATH}/../../dwi_midspace/dwi_midspace_meanb0_bet_mask.nii.gz"

# recalculate axon diameters with along fibre quantified powder-averaged shells
PATH_TRACT=${IN_FILE_PATH}/along_tract_midspace/CST_L
matlab -nodisplay -r "addpath ${SCRIPTPATH}/../AxonRadiusMapping/;calcAxonAlongTracts('$PATH_TRACT/CST_stats_sh6000.txt', '$PATH_TRACT/CST_stats_sh30000.txt', '$PATH_TRACT/CST_grads_6000.txt', '$PATH_TRACT/CST_grads_30000.txt', 'CST_stats_Axon_afterAFQonShells.txt');exit"
matlab -nodisplay -r "addpath ${SCRIPTPATH}/../AxonRadiusMapping/;calcAxonAlongTracts('$PATH_TRACT/CST_stats_between_regions_sh6000.txt', '$PATH_TRACT/CST_stats_between_regions_sh30000.txt', '$PATH_TRACT/CST_grads_between_regions_6000.txt', '$PATH_TRACT/CST_grads_between_regions_30000.txt', 'CST_stats_between_regions_Axon_afterAFQonShells.txt');exit"
