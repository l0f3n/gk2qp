#!/usr/bin/python3

import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile


colors = {
    'GREEN':  'Green',
    'PINK':   'Pink',
    'BLUE':   'Blue',
    'RED':    'Red',
    'ORANGE': 'Orange',
    'YELLOW': 'Yellow',
}


extra_colors = {
    'CERULEAN': 'Blue',
    # 'GRAY':     'Default',
    'BROWN':    'Orange',
    'PURPLE':   'Pink',
    'TEAL':     'Blue',
}


dtre = re.compile(r'^\d\d\d\d-\d\d-\d\dT\d\d_\d\d_\d\d.\d\d\d\+\d\d_\d\d$')


def is_untitled(gk_name):
    return dtre.match(gk_name) is not None


def convert_note(id, filepath):
    with open(filepath) as f:
        gk = json.load(f)

    qp = {
        'id': id,
        'creationDate': gk['createdTimestampUsec'] // 1_000_000,
        'modifiedDate': gk['userEditedTimestampUsec'] // 1_000_000,
        'notebookId': 1,
    }

    if not is_untitled(filepath.stem):
        qp['title'] = filepath.stem

    if gk['isArchived']:
        qp['isArchived'] = True

    if gk['isPinned']:
        qp['isPinned'] = True

    if gk['isTrashed']:
        qp['isDeleted'] = True

    if gk['color'] in colors:
        qp['color'] = colors[gk['color']]

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

    attachments = []
    if 'attachments' in gk:
        qp['attachments'] = []
        for gka in gk['attachments']:
            qpa = {
                'description': gka['filePath'],
                'fileName': gka['filePath'],
            }
            qp['attachments'].append(qpa)

            attachments.append(gka['filePath'])

    return qp, tags, attachments


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

    attachments = []

    for i, filepath in enumerate(filepaths, start=1):
        qp_note, note_tags, note_attachments = convert_note(i, filepath)
        qp_notes['notes'].append(qp_note)

        join_entries = create_join_entries(i, note_tags, tags)
        qp_notes['joins'].extend(join_entries)

        attachments.extend(note_attachments)

    return qp_notes, attachments


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
    if not filepath.is_file():
        return []

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
    src = Path(args.takeout)
    dst = f'quillpad-{src.stem}'

    srcdir = Path(tempfile.mkdtemp())
    dstdir = Path(tempfile.mkdtemp())

    shutil.unpack_archive(src, srcdir)

    keepdir = srcdir / 'Takeout' / 'Keep'

    if args.use_extra_colors:
        colors.update(extra_colors)

    tags = extract_tags(keepdir / 'Labels.txt')

    qp_notes, attachments = convert_notes(keepdir.glob('*.json'), tags)

    noteLen = len(qp_notes['notes'])
    tagLen = len(tags)
    attachmentLen = len(attachments)

    print(f'Converted {noteLen} notes with {tagLen} tags and {attachmentLen} attachments')

    with open(dstdir / 'backup.json', 'w') as f:
        f.write(json.dumps(qp_notes))

    mediadir = dstdir / 'media'
    mediadir.mkdir()
    for attachment in attachments:
        shutil.copy(keepdir / attachment, mediadir)

    archive = shutil.make_archive(dst, 'zip', root_dir=dstdir)

    shutil.rmtree(srcdir)
    shutil.rmtree(dstdir)

    print(f'Created Quillpad backup: {archive}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='gk2gp',
        description='Converts Google Keep notes to Quillpad notes',
    )

    parser.add_argument('takeout',
                        help='Path to takeout archive containing Google Keep notes',
    )

    parser.add_argument('-c', '--disable-extra-colors',
                        dest='use_extra_colors',
                        action='store_false',
                        help='Map colors in Google Keep not supported in Quillpad to colorless, otherwise use the closest match',
    )

    args = parser.parse_args()

    main(args)

