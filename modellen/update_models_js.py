import re
import glob
import shutil


FOLDER_PREFIX = 'modellen/'
MODELS_JS = 'models.js'

def parse_line(line):
    """ parse model.js line-by-line using voodoo-regexp:

    '{title: "Bungeejumper", url: "modellen/Bungeejumper.xml"},\n'
        =>  ["Bungeejumper", "modellen/Bungeejumper.xml"]

    [\"|']       --> match " or '
    (.[^'|\"]*)  --> group: match anything except " or '
    [\"|']       --> match " or '

    """
    return re.findall("[\"|'](.[^'|\"]*)[\"|']", line)
assert parse_line('{title: "Bungeejumper", url: "modellen/Bungeejumper.xml"},\n') == \
                  ["Bungeejumper", "modellen/Bungeejumper.xml"]
#assert parse_line("{title: 'Bungeejumper', url: 'modellen/Bungeejumper.xml'},\n") == \
#                  ["Bungeejumper", "modellen/Bungeejumper.xml"]


def maak_eerste_letter_hoofdletter(s):
    """maak van de eerste letter een hoofdletter"""
    return s[0].upper()+s[1:]


def fn_to_path(fn):
    """maak van een filename een path

    modelnaam.xml ->> modellen/modelnaam.xml

    """
    return FOLDER_PREFIX + fn


def write_models_js(modellen, outfile_fn=MODELS_JS):
    """schrijf models_js"""

    print(f'writing to: {outfile_fn}')
    with open(outfile_fn, 'w') as outfile:
        outfile.write('// models.js generated by update_model_js.py. EDIT WITH CAUTION!\n')
        outfile.write('var model_index = [\n')
        for path, titel in sorted(modellen.items(), key =
                 lambda kv:(kv[1], kv[0])):
            outfile.write('\t\t{' + f'title: "{titel}",' + f' url: "{path}"' + '},\n')
            pass
        outfile.write('];')


def read_models_js(models_js=MODELS_JS):
    modellen = {}
    bestanden_in_models_js = []

    with open(models_js) as f:
        for line in f.readlines():
            match = parse_line(line)
            if match:
                titel, path = match
                if titel.startswith(FOLDER_PREFIX) and titel.endswith('.xml'):
                    # draai path/titel om
                    titel, path = path, titel
                prefix, fn = path.split('/')
                assert prefix + '/' == FOLDER_PREFIX, f"Error prefix: != FOLDER_PREFIX"
                modellen[path] = titel
                bestanden_in_models_js.append(fn)

    return modellen, bestanden_in_models_js


def add_new_files_to_index(bestanden_in_folder, bestanden_in_models_js, modellen):
    """add new files to models.js, rename files with spaces"""

    for fn in bestanden_in_folder:
        if fn not in bestanden_in_models_js:
            print(f'new file: {fn}')
            assert fn.endswith('.xml'), 'ABORT: filename != *.xml'

            if " " in fn:
                fn_new = fn.replace(' ', '_')
                fn_new = maak_eerste_letter_hoofdletter(fn_new)
                print(f'rename: {fn} -> {fn_new}')
                shutil.move(fn, fn_new)
                fn = fn_new

            path = fn_to_path(fn)
            # default titel = bestandsnaam zonder .xml
            titel = maak_eerste_letter_hoofdletter(fn.replace('_', ' '))
            titel = titel[:-4]  # remove '.xml'
            modellen[path] = titel


def remove_missing_files_from_index(bestanden_in_models_js, bestanden_in_folder, modellen):
    """skip missing/removed xml files (remove (don't add) to models.js)"""

    for fn in bestanden_in_models_js:
        if fn not in bestanden_in_folder:
            print(f'file not found: {fn}: skipping.')
            del modellen[fn_to_path(fn)]


def main():

    modellen, bestanden_in_models_js = read_models_js()
    bestanden_in_folder = glob.glob('*.xml')

    remove_missing_files_from_index(bestanden_in_models_js, bestanden_in_folder, modellen)
    add_new_files_to_index(bestanden_in_folder, bestanden_in_models_js, modellen)
    write_models_js(modellen)


if __name__ == '__main__':
    main()