import re
import pandas as pd
from functools import reduce
import operator
import json

cm_csv = pd.read_csv('CM_scheme.csv', encoding='windows-1251', delimiter=';', keep_default_na=None)
sep_pattern = r'\s+\W{1}\s+'
scheme = list(set(x for x in cm_csv['Раздел']))
parameters = [x for x in cm_csv['Имя ключевого параметра']]
descriptions = [x for x in cm_csv['Описание на русском языке']]
units = [x for x in cm_csv['Единицы измерения']]
paths = [x for x in cm_csv['Раздел']]
head_scheme = {}
# print(paths)

model1_params = {'x': {'value': 3, 'type': 'I', 'path': "test - numbers - first-degree"},
                 'y': {'value': 4, 'type': 'I', 'path': "test - numbers - first-degree"},
                 'z': {'value': None, 'type': 'O', 'path': "test - numbers - first-degree"}}
model2_params = {'x': {'value': None, 'type': 'I', 'path': "test - numbers - first-degree"},
                 'y': {'value': None, 'type': 'I', 'path': "test - numbers - first-degree"},
                 'z': {'value': None, 'type': 'I', 'path': "test - numbers - first-degree"},
                 'x3': {'value': None, 'type': 'O', 'path': "test - numbers - third-degree"},
                 'y3': {'value': None, 'type': 'O', 'path': "test - numbers - third-degree"},
                 'z3': {'value': None, 'type': 'O', 'path': "test - numbers - third-degree"}}

model1_data = {'input': {x: model1_params[x]['value'] for x in model1_params if model1_params[x]['type'] == 'I'},
               'output': {x: model1_params[x]['value'] for x in model1_params if model1_params[x]['type'] == 'O'}}
model2_data = {'input': {x: model2_params[x]['value'] for x in model2_params if model2_params[x]['type'] == 'I'},
               'output': {x: model2_params[x]['value'] for x in model2_params if model2_params[x]['type'] == 'O'}}
models = dict(model_one=model1_params, model_two=model2_params)
models_data = dict(model_one=model1_data, model_two=model2_data)


def getFromDict(dataDict: dict, mapList: list):
    return reduce(operator.getitem, mapList, dataDict)


def setInDict(dataDict: dict, mapList: list, value: any):
    getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value


def add_el_to_dict(base_dict: dict, path: list):
    count = 1
    tmp_dict = {x: base_dict[x] for x in base_dict}
    while count < len(path):
        try:
            elm = dict(getFromDict(tmp_dict, path[:count]))
            if list(elm.keys()) != [] and not path[count] in list(elm.keys()):
                setInDict(elm, [path[count]], {})
                setInDict(tmp_dict, path[:count], elm)
            elif elm == {}:
                setInDict(tmp_dict, path[:count], {path[count]: {}})
            count += 1
        except (KeyError, TypeError):
            setInDict(tmp_dict, path[:count], {path[count]: {}})
    return tmp_dict


for el in scheme:
    tmp_str = re.sub(sep_pattern, ':', el)
    # tmp_list = re.sub(r'\s', '_', tmp_str).split(sep=':')
    tmp_list = tmp_str.split(sep=':')
    head_scheme = add_el_to_dict(head_scheme, tmp_list)

del scheme

'''for x in head_scheme:

    print(x, '::')
    for y in head_scheme[x]:
        print(3 * '\t', y, '::')
        for z in head_scheme[x][y]:
            print(6 * '\t', z, '::', head_scheme[x][y][z])'''

for i in range(len(parameters)):
    tmp_dict = dict(description=descriptions[i], units=units[i], value=None)
    tmp_path = re.sub(sep_pattern, ':', paths[i]).split(sep=':')
    tmp_element = dict(getFromDict(head_scheme, tmp_path))
    setInDict(tmp_element, [parameters[i]], tmp_dict)
    setInDict(head_scheme, tmp_path, tmp_element)

'''for x in head_scheme:
    print(x, '::')
    for y in head_scheme[x]:
        print(3 * '\t', y, '::')
        for z in head_scheme[x][y]:
            print(6 * '\t', z, '::', head_scheme[x][y][z])'''

with open('cm_file.json', 'w') as jsf:
    json.dump(head_scheme, jsf, indent=3, ensure_ascii=False)


# Необходимо будет изменить под файлы
def set_in_CM(CM_filename: str, model_info: dict, data_filename: dict, read_output: bool = True):
    with open(CM_filename, 'r') as CM_jsf:
        CM_scheme = json.load(CM_jsf)
        CM_jsf.close()
    # with open(data_filename) as D_jsf:
    # data = json.load(D_jsf)
    data = data_filename  # tmp
    if read_output:
        for d in data['output']:
            path = re.sub(sep_pattern, ':', model_info[d]['path']).split(sep=':')
            path.extend((d, 'value'))
            print(path)
            setInDict(CM_scheme, path, data['output'][d])
    else:
        for d in data['input']:
            path = re.sub(sep_pattern, ':', model_info[d]['path']).split(sep=':')
            path.extend((d, 'value'))
            print(CM_scheme)
            setInDict(CM_scheme, path, data['input'][d])
    with open(CM_filename, 'w') as CM_jsf:
        json.dump(CM_scheme, CM_jsf, indent=3, ensure_ascii=False)


def get_from_CM(CM_filename: str, model_info: dict, data_filename: dict):
    with open(CM_filename, 'r') as CM_jsf:
        CM_scheme = json.load(CM_jsf)
        CM_jsf.close()
    data = data_filename
    for d in data['input']:
        path = re.sub(sep_pattern, ':', model_info[d]['path']).split(sep=':')
        path.extend((d, 'value'))
        data['input'][d] = getFromDict(CM_scheme, path)
    return data


'''set_in_CM('cm_file.json', model1_params, model1_data, read_output=False)
dict1 = get_from_CM('cm_file.json', model1_params, model1_data)
print(dict1)
with open('tst_json.json') as tjsf:
    json.dump(dict1, tjsf, indent=3, ensure_ascii=False)'''
