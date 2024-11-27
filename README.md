# gk2qp - Import Google Keep notes into Quillpad

Google Keep 2 Quillpad is a simple Python script that converts Google Keep notes exported from Google Takeout into Quillpad notes.
Feel free to submit an issue or create a PR if you find any issues!

## Features

Supports:
 - Title
 - Text and list notes
 - Created and modified date
 - Pinned, archived and deleted
 - Colors
 - Labels (tags in Quillpad) 

Not supported:
 - Media

## Usage instructions

 1. Export your Google Keep data from [Google Takeout](https://takeout.google.com/).
 2. Unpack it.
 3. Run `./gk2qp.py <root>`, pointing to the folder you unpacked your data.
 4. Zip the resulting `backup.json` file.
 5. Go to Quillpad->Settings->Restore and choose to import the file you just created.

