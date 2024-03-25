import json
import os
import collections
import argparse

def parse_goalstep_json(json_fl, out_fl):

    annotations = json.load(open(json_fl))['videos']

    stats = collections.Counter()
    video_annots = []
    for annot in annotations:

        video_uid = annot['video_uid']
        stats['videos'] += 1

        # Unannotated
        if 'start_time' not in annot:
            video_annots.append({
                'video_uid': video_uid,
                'clips': []
            })
            continue

        start_time, end_time = annot['start_time'], annot['end_time']
        goal_clip_uid = f'{video_uid}_{start_time}_{end_time}'
        
        clip_annots = [{
            'clip_uid': video_uid, # full video = 1 clip
            'video_start_sec': start_time,
            'video_end_sec': end_time,
            'annotations':[{'language_queries': None, 'annotation_uid': goal_clip_uid}] # fill in language queries
        }]
        
        if isinstance(annot['goal_description'], list):
            assert len(annot['goal_description']) == 1, 'multiple goals'
            annot['goal_description'] = annot['goal_description'][0]

        language_queries = []
        for segment in annot['segments']:

            assert isinstance(annot['goal_description'], str), 'goal is not string'

            step_description = segment['step_description'].strip()
            assert len(step_description) > 0, 'len(step_description) == 0'

            query = {
                'clip_start_sec': segment['start_time'], # video == clip
                'clip_end_sec': segment['end_time'], # video == clip
                'query': step_description,
                'step_label': segment['step_category'],
                'parent_goal': annot['goal_description'].strip(),
                'is_relevant': segment.get('is_relevant', 'unsure'),
                'num_train_samples': segment.get('num_train_samples', None),
                'type': 'step',
            }

            assert segment['end_time'] - segment['start_time'] > 0, 'end_time - start_time <= 0'
            language_queries.append(query)
            stats['query'] += 1
            stats['step'] += 1
          
            for sub_segment in segment['segments']:

                assert isinstance(segment['step_description'], str), 'goal is not string'
                step_description = sub_segment['step_description'].strip()
                assert len(step_description) > 0, 'len(step_description) == 0'

                query = {
                    'clip_start_sec': sub_segment['start_time'], # video == clip
                    'clip_end_sec': sub_segment['end_time'], # video == clip
                    'query': step_description,
                    'step_label': sub_segment['step_category'],
                    'parent_goal': segment['step_description'].strip(),
                    'is_relevant': sub_segment['is_relevant'],
                    'num_train_samples': sub_segment.get('num_train_samples', None),
                    'type': 'substep',
                }
                assert sub_segment['end_time'] - sub_segment['start_time'] > 0, 'end_time - start_time <= 0'
                language_queries.append(query)
                stats['query'] += 1
                stats['substep'] += 1

        clip_annots[0]['annotations'][0]['language_queries'] = language_queries
        video_annots.append({'video_uid': video_uid, 'clips': clip_annots})

    output = {
        'version': 'v1',
        'date': '231006',
        'description': 'Goal step annotations',
        'metadata': 's3://ego4d-consortium-sharing/public/v2/ego4d.json',
        'videos': video_annots,
    }

    json.dump(output, open(out_fl, 'w'))
    print (stats)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse JSONs')
    parser.add_argument('--annot_dir', help='path that contains goalstep_[train/val/test].json')
    parser.add_argument('--out_dir', default='data/annotations/')
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)

    for split in ['train', 'val', 'test_unannotated']:
        json_fl = f'{args.annot_dir}/goalstep_{split}.json'

        split = 'test' if split == 'test_unannotated' else split
        out_fl = f'{args.out_dir}/{split}.json'
        parse_goalstep_json(json_fl, out_fl)
