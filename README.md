# gk2qp - Import Google Keep notes into Quillpad

Google Keep to Quillpad is a simple Python script that converts Google Keep notes exported from Google Takeout into [Quillpad](https://github.com/quillpad/quillpad) notes.
Feel free to submit an issue or create a PR if you find any issues!

## Features

Supports:
 - Title
 - Text and list notes
 - Created and modified date
 - Pinned, archived and deleted
 - Colors
 - Labels (tags in Quillpad) 
 - Images (media in Quillpad) 

## Usage

 1. Export your Google Keep data from [Google Takeout](https://takeout.google.com/).
 2. Run `./gk2qp.py <takeout>`, pointing to the exported Google Keep archive.
 3. In Quillpad, go to Settings->Restore and choose to import the newly created backup.
