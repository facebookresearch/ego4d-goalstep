import json
import os
import collections
import argparse
import pandas as pd
import ast

def parse_goalstep_json(json_fl, out_fl):

    annotations = json.load(open(json_fl))['videos']

    stats = collections.Counter()
    video_annots = []
    for annot in annotations:

        video_uid = annot['video_uid']
        stats['videos'] += 1

        start_time, end_time = annot['start_time'], annot['end_time']
        goal_clip_uid = f'{video_uid}_{start_time}_{end_time}'
        
        clip_annots = [{
            'clip_uid': video_uid, # full video = 1 clip
            'video_start_sec': start_time,
            'video_end_sec': end_time,
            'annotations':[{'language_queries': None, 'annotation_uid': goal_clip_uid}] # fill in language queries
        }]
    

        language_queries = []
        for segment in annot['segments']:

            step_description = segment['step_description'].strip()
            assert len(step_description) > 0, 'len(step_description) == 0'

            query = {
                'clip_start_sec': segment['start_time'], # video == clip
                'clip_end_sec': segment['end_time'], # video == clip
                'query': step_description,
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


def load_test_metadata(annot_dir):
    metadata = json.load(open(f'{annot_dir}/ego4d.json'))
    video_durations = {entry['video_uid']: entry['duration_sec'] for entry in metadata['videos']}
    video_groups = pd.read_csv(f'{annot_dir}/goalstep_video_groups.tsv', delimiter='\t')
    for entry in video_groups.to_dict('records'):
        video_group = ast.literal_eval(entry['video_group'])
        gvideo_uid = f'grp-{video_group[0]}'
        duration = 0
        for video_uid in video_group:
            duration += video_durations[video_uid]
        video_durations[gvideo_uid] = duration
    return video_durations

def parse_goalstep_test_json(json_fl, out_fl, video_durations):

    annotations = json.load(open(json_fl))['videos']

    stats = collections.Counter()
    video_annots = []
    for annot in annotations:

        video_uid = annot['video_uid']
        stats['videos'] += 1
        
        # full video = 1 clip
        clip_annots = [{
            'clip_uid': video_uid, 
            'video_start_sec': 0,
            'video_end_sec': video_durations[video_uid],
            'annotations':[{'language_queries': None, 'annotation_uid': video_uid}] # fill in language queries
        }]
        
        language_queries = []
        for segment in annot['step_segments']:

            step_description = segment['step_description'].strip()
            assert len(step_description) > 0, 'len(step_description) == 0'

            query = {
                'query': step_description,
            }
            language_queries.append(query)
            stats['query'] += 1
          
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
    parser.add_argument('--annot_dir', help='path that contains goalstep_[train/valid/test].json and ego4d.json metadata')
    parser.add_argument('--out_dir', default='data/annotations/')
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)


    parse_goalstep_json(
        f'{args.annot_dir}/goalstep_train.json',
        f'{args.out_dir}/train.json'
    )

    parse_goalstep_json(
        f'{args.annot_dir}/goalstep_valid.json',
        f'{args.out_dir}/val.json'
    )

    metadata = load_test_metadata(args.annot_dir)
    parse_goalstep_test_json(
        f'{args.annot_dir}/goalstep_test.json',
        f'{args.out_dir}/test.json',
        metadata
    )