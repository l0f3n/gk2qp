#!/usr/bin/python3

import argparse
import json
from pathlib import Path
import sys


supported_colors = {
    'GREEN',
    'PINK',
    'BLUE',
    'RED',
    'ORANGE',
    'YELLOW',
}


def convert_note(id, filepath):
    with open(filepath) as f:
        gk = json.load(f)

    qp = {
        'title': filepath.stem,
        'id': id,
        'creationDate': gk['createdTimestampUsec'] // 1_000_000,
        'modifiedDate': gk['userEditedTimestampUsec'] // 1_000_000,
        'notebookId': 1,
    }

    if gk['isArchived']:
        qp['isArchived'] = True

    if gk['isPinned']:
        qp['isPinned'] = True

    if gk['isTrashed']:
        qp['isDeleted'] = True

    if gk['color'] in supported_colors:
        qp['color'] = gk['color'].capitalize()

    if 'textContent' in gk:
        qp['content'] = gk['textContent']

    if 'listContent' in gk:
        qp['isList'] = True
        qp['taskList'] = []
        for j, gkt in enumerate(gk['listContent']):
            qpt = {
                'id': j,
                'isDone': gkt['isChecked'],
                'content': gkt['text'],
            }
            qp['taskList'].append(qpt)

    tags = gk.get('labels', [])

    return qp, tags


def convert_notes(filepaths, tags):
    qp_notes = {
        'version': 26,
        'notes': [],
        'notebooks': [
            {
                'name': "Imported from Google Keep",
                'id': 1,
            }
        ],
        'tags': tags, 
        'joins': [],
    }

    for i, filepath in enumerate(filepaths, start=1):
        qp_note, note_tags = convert_note(i, filepath)
        qp_notes['notes'].append(qp_note)

        join_entries = create_join_entries(i, note_tags, tags)
        qp_notes['joins'].extend(join_entries)

    return qp_notes


def tag_id_from_name(tags, name):
    for tag in tags:
        if tag['name'] == name:
            return tag['id']

    print(f'Failed to find tag: {name}')
    sys.exit(-1)
    return 0


def create_join_entries(note_id, note_tags, tags):
    entries = []
    for note_tag in note_tags:
        entry = {
            'tagId': tag_id_from_name(tags, note_tag['name']),
            'noteId': note_id, 
        }
        entries.append(entry)

    return entries 


def extract_tags(filepath):
    tags = []
    with open(filepath) as f:
        for i, line in enumerate(f.readlines(), start=1):
            tag = {
                'id': i,
                'name': line.strip(),
            }
            tags.append(tag)

    return tags


def main(args):
    root = Path(args.root)

    labels_filepaths = list(root.glob('**/Labels.txt'))
    if len(labels_filepaths) == 1:
        tags = extract_tags(labels_filepaths[0])
    else:
        print(f'Found {len(labels_filepaths)} label files, skipping tags...')
        tags = []

    qp_notes = convert_notes(root.glob('**/*.json'), tags)

    with open(args.outfile, 'w') as f:
        f.write(json.dumps(qp_notes))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='gk2gp',
        description='Converts Google Keep notes to Quillpad notes',
    )

    parser.add_argument('root',
                        help='Path to folder containing Google Keep notes (e.g. Takeout/)',
                        )

    parser.add_argument('-o', '--outfile',
                        dest='outfile',
                        help='Name of the output file (default: %(default)s)',
                        default='backup.json')

    args = parser.parse_args()

    main(args)

