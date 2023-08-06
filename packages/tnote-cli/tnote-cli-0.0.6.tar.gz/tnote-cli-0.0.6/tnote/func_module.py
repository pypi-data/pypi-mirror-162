
import os
import json
CONFIGPATH = os.path.expanduser('~/.tnote.json')


def intialize_config():
    if not os.path.exists(CONFIGPATH):
        with open(CONFIGPATH, "w") as config:
            config.write('\
{\n\
"DATAPATH": "",\n\
"NOTESPATH": "",\n\
"INDEXPATH": "",\n\
"EDITOR": "",\n\
"GLOW": false\n\
}')


def get_file(path, name=None):
    if path == CONFIGPATH:
        intialize_config()
    else:
        intialize_files()
    dicti = {}
    with open(path, 'r') as file:
        dicti = json.load(file)
        try:
            return dicti[name]
        except KeyError:
            return dict(dicti)


config = get_file(CONFIGPATH)
DATAPATH = config['DATAPATH'] or os.path.expanduser('~/.tnote/')
NOTESPATH = config['NOTESPATH'] or os.path.join(DATAPATH, "notes")
INDEXPATH = config['INDEXPATH'] or os.path.join(DATAPATH, "index.json")
EDITOR = config['EDITOR'] or os.getenv("$EDITOR")
RECENT = '.recent'
GLOW = config['GLOW'] or False


def intialize_files():
    intialize_config()
    if not os.path.exists(DATAPATH):
        os.mkdir(DATAPATH)
    if not os.path.exists(NOTESPATH):
        os.mkdir(NOTESPATH)
    if not os.path.exists(INDEXPATH):
        with open(INDEXPATH, 'w') as index:
            index.write('{\n\n}')


def print_index():
    intialize_files()
    index_dict = get_file(INDEXPATH)
    print("\
|-------------------------INDEX-------------------------|\n\
\n")
    if RECENT in index_dict.keys():
        print("\
|-------------------------RECENT------------------------|\n\
 Note ID: {}\n\
 Name: {}\n\
 Path: {}\n\
|-------------------------------------------------------|\n\
    \n\
            _________________________________\n\
            \n".format(index_dict[RECENT]['id'], index_dict[RECENT]['name'], index_dict[RECENT]['path']))
    keys = index_dict.keys()
    for key in keys:
        if key == RECENT:
            continue
        print("\
|-------------------------------------------------------|\n\
 Note ID: {}\n\
 Name: {}\n\
 Path: {}\n\
|-------------------------------------------------------|\n".format(key, index_dict[key]['name'], index_dict[key]['path']))


def write_index(dict: dict):
    with open(INDEXPATH, 'w') as index:
        json.dump(dict, index)


def recent_check(index):
    try:
        note_id = index[RECENT]['id']
        return note_id
    except KeyError:
        print("Error: Cannot find recent note you are looking for")
        quit()


def index_check(index, note_id, move):
    try:
        return index[note_id]['path']
    except KeyError:
        if move:
            print("Error: Cannot move a note that doesn't exist")
            quit()
        return
