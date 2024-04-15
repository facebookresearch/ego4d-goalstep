import pandas as pd
import json
import ast
import tqdm
import torch
import os
import argparse


def run(src_dir, dst_dir, annot_dir):

    video_uids = set()
    for split in ['train', 'valid', 'test']:
        json_fl = f'{annot_dir}/goalstep_{split}.json'
        annotations = json.load(open(json_fl))['videos']
        video_uids |= set([annot['video_uid'] for annot in annotations])

    gvideo_uids = set([video_uid for video_uid in video_uids if video_uid.startswith('grp-')])
    video_uids = video_uids - gvideo_uids

    feature_shapes = {}

    # symlink features for videos if they already exist
    for video_uid in tqdm.tqdm(video_uids):

        src = f'{src_dir}/{video_uid}.pt'
        dst = f'{dst_dir}/{video_uid}.pt'

        if not os.path.exists(src):
            raise Exception(f'{video_uid} video feature missing. Check if all features are downloaded?')

        if os.path.exists(dst):
            os.remove(dst)
        os.symlink(src, dst)

        feature_shapes[video_uid] = torch.load(dst).shape[0]


    # Merge features for grouped videos
    video_groups = pd.read_csv(f'{annot_dir}/goalstep_video_groups.tsv', delimiter='\t')
    for entry in tqdm.tqdm(video_groups.to_dict('records')):
        video_group = ast.literal_eval(entry['video_group'])
        gvideo_uid = f'grp-{video_group[0]}'

        if gvideo_uid not in gvideo_uids:
            continue

        gfeats = []
        for video_uid in video_group:
            feats = torch.load(f'{src_dir}/{video_uid}.pt')
            gfeats.append(feats)
        gfeats = torch.cat(gfeats, 0)

        feature_shapes[gvideo_uid] = gfeats.shape[0]
        torch.save(gfeats, f'{dst_dir}/{gvideo_uid}.pt')

    json.dump(feature_shapes, open(f'{dst_dir}/feature_shapes.json', 'w'))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Aggregate GoalStep video features')
    parser.add_argument('--annot_dir', help='path that contains goalstep_video_groups.tsv and split jsons')
    parser.add_argument('--feature_dir', help='path that contains Ego4D videos')
    parser.add_argument('--out_dir', default='data/features/omnivore_video_swinl/')
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)
    run(args.feature_dir, args.out_dir, args.annot_dir)
