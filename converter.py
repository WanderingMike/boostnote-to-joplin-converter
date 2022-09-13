import sqlite3
import os
import re
import shutil
from uuid import uuid4

def clean_directory(pwd, config, connector):
    """Goes through entire tree of notes and converts them from Boostnote to Joplin markdown type"""

    resource_folder = os.path.join(config, "resources")

    for root, _, files in os.walk(pwd):
        for filename in files:
            print(filename)

            try:
                with open(os.path.join(root, filename), 'r', encoding="utf-8") as f:
                    filedata = f.read()

                    # Insert image hashes
                    newdata = insert_image_hashes(filedata, resource_folder, connector)

                    # Correct code cells
                    newdata = format_cells(newdata)

                with open(os.path.join(root, filename), 'w', encoding="utf-8") as file:
                    file.write(newdata)

            except Exception as e:
                print(e, filename)



def insert_image_hashes(text, resources, connector):
    """Adds image UUID to SQLite database in order to render them in Joplin"""
    
    #format ![](pic7-klarpl3n.png)
    pattern = r'!\[\]\((.*?)\)'
    matches = re.findall(pattern, text)

    for img_title in matches:
        new_uuid = uuid4().hex
        values = "('%s', '%s', 'image/png','', '1663022833188', '1663022833188', '1663022833188', '1663022833188','png','' ,0,0,121375,0,'' ,'' )" % (new_uuid, img_title)
        old_path = os.path.join(resources, img_title)
        new_path = os.path.join(resources, new_uuid + ".png")
        shutil.copy(old_path, new_path)
        connector.execute("INSERT INTO resources VALUES {}".format(values))
        con.commit()
        text = text.replace(img_title, ":/" + new_uuid)

    return text

def tab_begin(line):
    """Checks whether line of text begins with tab (i.e. four spaces)"""
    if line[:4] == " "*4:
        return True
    else: 
        return False

def format_cells(rawtext):
    """Creates code cells out of the tabbed lines"""

    text = rawtext.split("\n")
    incell = False

    i = 0
    while i < len(text):
        line = text[i]

        if tab_begin(line) and not incell:
            incell = True
            text.insert(i, "```")
            i += 1
        elif not tab_begin(line) and incell:
            incell = False
            text.insert(i, "```")
            i += 1
        i += 1

    return "\n".join(text)



if __name__ == "__main__":
    # all attachments should be placed under the joplin-desktop\resources folder.
    notes_location = r"C:\Users\mick9\Desktop\main\Notes\Notes"
    config_location = r"C:\Users\mick9\.config\joplin-desktop"
    con = sqlite3.connect(os.path.join(config_location, "database.sqlite"))
    con.cursor()
    clean_directory(notes_location, config_location, con)


