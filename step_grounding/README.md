# Step grounding starter code

The VSLNet baseline is trained using the Narrations-as-Queries (NaQ) [codebase](https://github.com/srama2512/NaQ). Steps are below.

### (1) Set up NaQ repository following official instructions
Installation instructions can be found [here](https://github.com/srama2512/NaQ?tab=readme-ov-file#installation).


### (2) Convert Ego4D GoalStep annotation jsons into the required format for NaQ

```
# Put the ego4d metadata file to the data directory
ln -s ${EGO4D_ROOT}/ego4d.json ../data/

# Parse annotations to NLQ format
python -m tools.parse_goalstep_jsons \
    --annot_dir ../data/ \
    --out_dir data/annotations/
```
Output: `data/annotations/[train|val|test].json`


### (3) Group omnivore video features for GoalStep videos
Ensure you first download video features using the [Ego4D CLI](https://ego4d-data.org/docs/data/features/) to `{EGO4D_ROOT}`.
```
python -m tools.aggregate_features \
    --annot_dir data/annotations/ \
    --feature_dir ${EGO4D_ROOT}/omnivore_video_swinl/ \
    --out_dir data/features/omnivore_video_swinl/
```
Output: `data/features/omnivore_video_swinl/*.pth` features for each video_uid

### (4) Prepare dataset for consumption by NaQ codebase
```
python NaQ/utils/prepare_ego4d_dataset.py \
    --input_train_split data/annotations/train.json \
    --input_val_split data/annotations/val.json \
    --input_test_split data/annotations/test.json \
    --output_save_path data/dataset/ego4d_goalstep/
```
Output: `data/dataset/ego4d_goalstep/[train/val/test].json` in NaQ format.


### (5) Train and evalaute the model
```
# Train VSLNet on GoalStep
bash train.sh experiments/vslnet/goalstep/

# Perform inference on test set
bash infer.sh experiments/vslnet/goalstep/
```


# References

We encourage you to cite both research works if you use this codebase.
```
@article{song2024ego4d,
  title={Ego4d goal-step: Toward hierarchical understanding of procedural activities},
  author={Song, Yale and Byrne, Eugene and Nagarajan, Tushar and Wang, Huiyu and Martin, Miguel and Torresani, Lorenzo},
  journal={Advances in Neural Information Processing Systems},
  year={2024}
}

@inproceedings{ramakrishnan2023naq,
  title={Naq: Leveraging narrations as queries to supervise episodic memory},
  author={Ramakrishnan, Santhosh Kumar and Al-Halah, Ziad and Grauman, Kristen},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  year={2023}
}
```
