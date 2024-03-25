EXPT_ROOT=$1

FEAT_DIM=1536
FV="omnivore_video_swinl"  

CUDA_VISIBLE_DEVICES="0 1" python NaQ/VSLNet/main.py \
 --task ego4d_goalstep \
 --predictor bert \
 --mode val \
 --video_feature_dim $FEAT_DIM \
 --max_pos_len 128 \
 --fv $FV \
 --model_dir $EXPT_ROOT/checkpoints \
 --eval_gt_json data/annotations/val.json \
