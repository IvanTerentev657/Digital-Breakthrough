import json
import os
import re
from itertools import count

from pdfquery import PDFQuery

with open("pdfs.json") as _f:
    GLOBAL_PDFS_SETTINGS = json.load(_f)
del _f

def get_full_text(elem):
    answer = ""
    if elem.text:
        answer += elem.text
    for child in elem.getchildren():
        answer += get_full_text(child)
    return answer


def pdf_to_json(path):
    try:
        settings = GLOBAL_PDFS_SETTINGS[os.path.split(path)[-1]]
    except IndexError:
        raise NotImplementedError("Settings for this file dont set!")

    paragraph_re = re.compile(settings["paragraph-regex"])

    pdf = PDFQuery(path)
    pdf.load()

    # Get all child-free elements from any page.
    pages = []
    for page in count(settings["start-page"] - 1):
        try:
            pages.append(pdf.pq(f"LTPage[page_index=\"{page}\"]")[0].xpath(".//*[not(*)]"))
        except IndexError:
            break

    # Sort pages for lines and rows
    for page in pages:
        page.sort(
            key=lambda x:
            # Send annotations to end
            ((1, 1), (1, 1)) if x.tag == "Annot"
            else ((-x.layout.y0, -x.layout.y1), (x.layout.x0, x.layout.x1))
        )

    # List of lines blocks (paragraphs)
    all_blocks = [[[]]]
    for page_idx, page in enumerate(pages):
        # Make lines
        lines = []
        # Line is some text frames that's Y0 is same
        last_y0 = -1e8
        for elem in page:
            # Ignore annotations
            if elem.tag == "Annot":
                continue
            # Check Y0-s' similarity
            if abs(elem.layout.y0 - last_y0) < settings["epsilon"]:
                lines[-1].append(elem)
            else:
                lines.append([elem])
                last_y0 = elem.layout.y0
        # After this code line lines = [({line Y0}, {line text}) ...]
        lines = [(line[0].layout.x0, "".join([i.text for i in line if i.text])) for line in lines]
        # List of paragraphs
        blocks = []
        # This var need to detect first data block on page
        first_adding = True
        for line in lines:
            # If line has paragraph number (this line is start od block)
            if paragraph_re.match(line[1]) and any(
                    abs(line[0] - i) < settings["epsilon"] for i in settings["paragraph-lefts"]
            ):
                blocks.append([line[1]])
                first_adding = False
            # If this line is data line from previous block
            elif any(abs(line[0] - i) < settings["epsilon"] for i in settings["data-lefts"]):
                if blocks:
                    blocks[-1].append(line[1])
                else:
                    all_blocks[-1][-1].append(line[1])
                first_adding = False
            # If this is first data block in page
            elif first_adding and any(abs(line[0] - i) < settings["epsilon"] for i in settings["transfer-lefts"]):
                all_blocks[-1][-1].append(line[1])
                first_adding = False
        # We don't add empty blocks
        if blocks:
            all_blocks.append(blocks)
    # Delete service element
    all_blocks.pop(0)
    # And combine list of block from different pages
    all_blocks = sum(all_blocks, [])
    # Answer json object
    json_file = {}
    # Previous paragraph number
    prev = (-1,)
    for block in all_blocks:
        # Key is like "1.2.4" or "1." or any other paragraph number
        key, value = block[0].split()[0], "".join(block)
        # We transform key ti tuple, at example, "1.2.4." -> (1, 2, 4)
        key = tuple(map(int, key.strip(".").split(".")))
        # If we find extra value
        if key < prev:
            break
        # Creating path to this paragraph data
        current = json_file
        for prefix_idx in range(1, len(key) + 1):
            # 1 -> 1.2 -> 1.2.4
            part = ".".join(map(str, key[:prefix_idx]))
            # json_file -> json_file["1"] -> json_file["1.2"] -> json_file["1.2.4"]
            if part not in current:
                current[part] = {}
            current = current[part]
        # And write this data
        current["text"] = value.strip()

    return json_file


def pretty_save_json(json_object, json_file_name):
    with open(json_file_name, "w", encoding="UTF-8") as f:
        json.dump(json_object, f, ensure_ascii=False, indent=4)
