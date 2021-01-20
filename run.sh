#!/bin/bash

GPU="0"

# location of original data
# old_data_folder="/root/preprocess-3/root/Anshit/OLD_DATA/old_upper"
# # location of new data for retraining
# new_data_folder="/root/preprocess-3/root/Anshit/NEW_DATA_UPDATED"

# # location of output_checkpoints to be saved after retraining (also model checkpoint path)
# output_folder="/root/preprocess-3/root/Anshit/NEW_DATA_UPDATED/upper_retrain_ckpts"
# epochs=$2
# # location of old trained model
# old_model_path="/root/preprocess-3/root/Anshit/OLD_DATA/old_upper/old_trained_model/saved-model-augmented-gpu-100.h5"
# # location to save final best model
# final_model_path="/root/preprocess-3/root/Anshit/NEW_DATA_UPDATED/upper_model_final_wts"
language_1=$1
language_2=$2
language_3=$3
language_4=$4

# launch training script with required options
# echo "Launching Training Script"
# python3 Train_Upper.py  --old_data_path=${old_data_folder} --new_data_path=${new_data_folder} --output_dir=${output_folder} --old_model_path=${old_model_path} --final_model_path=${final_model_path} --name=${name} --epochs=${epochs}


python3 text_translation.py  --language_1=${language_1} --language_2=${language_2} --language_3=${language_3} --language_4=${language_4}
# echo "Job completed"
