from model import model
import json
def is_paragraph(word):
    '''возращает является ли параграфом и является ли сложным параграфом'''
    is_dot = False
    is_num = False
    is_slash = False
    for x in word.rstrip(','):
        if x == '.':
            is_dot = True
        elif x.isdigit():
            is_num = True
        elif x == '—':
            if is_slash is True:
                is_slash = -1
            elif is_slash is False:
                is_slash = True
        else:
            return [False, False]

    return [is_dot * is_num, is_slash]


def json2text(json):
    text = ''
    if type(json) != dict:
        return ""
    if list(json.keys()) == ["text"]:
        json_text = json["text"].split()

        if is_paragraph(json_text[0])[0]:
            return " ".join(json_text[1:]) + " "
        else:
            return json["text"] + " "

    for key, value in json.items():
        #if key != 'text':
        text += json2text(value)
    return text


def json2list(json):
    """Get dict and return"""
    st = []
    if type(json) != dict:
        return []
    if list(json.keys()) == ["text"]:
        json_text = json["text"].split()

        if is_paragraph(json_text[0])[0]:
            return [" ".join(json_text[1:])]
        else:
            return [json["text"]]

    for key, value in json.items():
        #if key != 'text':
        st.extend(json2list(value))
    return st
# for i, x in enumerate(json2list(loaded_tech)):
#     print(i, x)


def parse_elementary_paragraph(json, paragraph):
    path = paragraph.rstrip(',').rstrip('.').split('.')

    el = json
    i = 1
    x = path[0]

    while True:
        if x in el:
            el = el[x]
        else:
            return False
        if i >= len(path):
            break
        x += '.' + path[i]
        i += 1

    return json2text(el)

#print(paragraph2text(loaded_json, '1.2'))

def parse_complementary_paragraph(json, paragraphs):
    '''Подаем четкий вид параграфов и те, что уже чекнули выдаем список текста и пунктов или False'''
    texts = ''
    paragraphs = paragraphs.split('—')
    paragraphs[0] = paragraphs[0].split('.')
    paragraphs[1] = paragraphs[1].split('.')
    prefics = paragraphs[0][:-1]

    if len(paragraphs[0]) != len(paragraphs[1]):
        return False
    start_point = int(paragraphs[0][-1])
    end_point = int(paragraphs[1][-1])

    result_paragraphs = []
    for point in range(start_point, end_point + 1):
        cur_paragraph = '.'.join(prefics) + '.' + str(point)
        result_paragraphs.append(cur_paragraph)

        par = parse_elementary_paragraph(json, cur_paragraph)
        if not par is False:
            texts += par
    return texts

#print(parse_complementary_paragraph(loaded_json, '1.2—1.3', ['1.2.1']))

# print(is_paragraph('1.2.3'))
# print(is_paragraph('1.2,'))
# print(is_paragraph('1.2—1.3'))

def summarization(text):
    text = model.summarize(text)
    return text

def unwrap_text(json, text, key_words=['paragraph', 'paragraphs'], depth=0):
    if text is False or text == "":
        return ""
    if depth >= 2:
        return text

    text_st = text.split()
    is_last_par_spoiler = False

    for i in range(len(text_st)):
        word = text_st[i]

        is_last_par_spoiler -= 1
        if word == '':
            continue

        res_is_par = is_paragraph(word)
        is_par, is_comp_par = res_is_par
        if is_par and (word[0] == '[' or is_last_par_spoiler > 0):
            if word.rstrip(',').rstrip('.').count('.') == 0:
                 linked_text = ''
            elif not (is_comp_par is True):
                linked_text = summarization(unwrap_text(json, parse_elementary_paragraph(json, word), depth=depth + 1))
            else:
                linked_text = summarization(unwrap_text(json, parse_complementary_paragraph(json, word), depth=depth + 1))

            text_st[i] = '(' + linked_text + ')'

        if word in key_words:
            is_last_par_spoiler = 7

    return text_st



def get_list_of_technical_requirements(json, list_of_technical_puncts_names = ['specifications', 'technical requirements']):
    for paragraph in json:
        if ' '.join(json[paragraph]['text'].lower().split()[1:]) in list_of_technical_puncts_names:
            return json2list(json[paragraph])
    return 'I didnt find Technical requirements'



# key_list = ['paragraph', 'paragraphs', 'mentioned', 'requirements', 'conforming', 'described', 'specified', 'conforms', 'defined', 'accordance', 'conditions', 'treated', 'regulation', 'satisfied']

# print(json2text(loaded_tech))
# print(unwrap_text(loaded_data, json2text(loaded_tech)))
# print(unwrap_text(loaded_data, 'paragraph pressure column 6.2.8. Column 5. If after '))

# print(get_list_of_technical_requirements(loaded_json)[:5])