#!/usr/bin/env python3
import json


def generate_diff(file_path1, file_path2):
    file_data1 = json.load(open(file_path1))
    file_data2 = json.load(open(file_path2))
    result = ['{']
    common_keys_list = sorted(list(file_data1.keys() | file_data2.keys()))
    deleted_fil1_keys = file_data1.keys() - file_data2.keys()
    added_file2_keys = file_data2.keys() - file_data1.keys()
    for key in common_keys_list:
        if key in file_data1.keys() and key in file_data2.keys():
            if file_data1[key] == file_data2[key]:
                result.append('   {}: {}'.format(key, file_data1[key]))
            else:
                result.append(' - {}: {}'.format(key, file_data1[key]))
                result.append(' + {}: {}'.format(key, file_data2[key]))
        elif key in deleted_fil1_keys:
            result.append(' - {}: {}'.format(key, file_data1[key]))
        elif key in added_file2_keys:
            result.append(' + {}: {}'.format(key, file_data2[key]))
    result.append('}')
    return '\n'.join(result)
