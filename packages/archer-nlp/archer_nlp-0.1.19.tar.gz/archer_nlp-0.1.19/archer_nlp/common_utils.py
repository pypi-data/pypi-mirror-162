# coding:utf8
import hashlib
import json
import os.path
import pickle
import sys
import uuid
from datetime import datetime

import Levenshtein
import numpy as np
import pandas as pd


def generate_uuid():
    try:
        uuid4 = uuid.uuid4()
        return str(uuid4).upper().replace('-', '')
    except Exception as e:
        print('generate_uuid error:', e)
        return None


def generate_uuid_md5(data, start='C1'):
    try:
        md5 = hashlib.md5(data.encode(encoding='utf8')).hexdigest().upper()[2:]
        return start + md5[0:6] + '-' + md5[6:10] + '-' + md5[10:14] + '-' + md5[14:18] + '-' + md5[18:]
    except Exception as e:
        print('get_md5 error:', e)
        return None


def get_time():
    # 2022-03-03 16:12:30
    return datetime.now().strftime("%Y-%m-%d %X")


def read_excel(path, sheet_index=0, is_value=True, is_replace=True, is_ffill=False):
    """
    读取Excel
    :param path:
    :param sheet_index:
    :param is_value:
    :param is_replace:
    :param is_ffill: 单元格为空值（NaN，非空字符串）时，填充上一行的值，适用于合并单元格的情况。
    :return:
    """
    df = pd.read_excel(path, sheet_name=sheet_index)
    if is_ffill:
        df = df.ffill()

    # nan替换为空字符串
    if is_replace:
        df = df.replace(np.nan, '', regex=True)

    if is_value:
        return df.values
    else:
        return df


def write_excel(path, res_list=[], columns=[], df=None):
    if df is None:
        df = pd.DataFrame(res_list, columns=columns)
    # 加engine、encoding参数是防止“openpyxl.utils.exceptions.IllegalCharacterError”
    df.to_excel(path, engine='xlsxwriter', index=False, encoding='utf-8')


def df_to_sql(path_df, table, engine, is_df=False):
    """
    df import to sql
    :param path_df:
    :param table: sql table
    :param engine: sqlalchemy engine
    :param is_df: True为DataFrame，False为Excel路径
    :return:
    """
    # pandas批量导入mysql
    if is_df:
        df = path_df
    else:
        df = read_excel(path_df, is_value=False)
    df.to_sql(table, engine, if_exists='append', index=False)


def get_extension(path):
    """
    获取扩展名（小写）
    :param path:
    :return:
    """
    if not os.path.exists(path):
        raise ValueError('file not exists!')
    return os.path.splitext(path)[-1].lower()


def read_txt(path):
    data_list = []
    with open(path, encoding='utf8') as f:
        for line in f:
            data_list.append(line.strip())
    return data_list


def dump_json(obj, path):
    json.dump(obj, open(path, 'w', encoding='utf8'), ensure_ascii=False)


def load_json(path):
    return json.load(open(path, encoding='utf8'))


def save_pkl(data, path):
    with open(path, "wb") as f:
        pickle.dump(data, f)


def load_pkl(path):
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data


def generate_dict(list1, list2=[]):
    try:
        if not isinstance(list1, list):
            list1 = list(list1)
        if list2 is not None:
            if not isinstance(list2, list):
                list2 = list(list2)
            return dict(zip(list1, list2))
        else:
            return dict(zip(list1, range(len(list1))))
    except Exception as e:
        print(f"generate_dict error:{e}")
        return {}


def get_max_check(check_base_list, check_refer_list, max_ratio=0.5, is_ret_lr=False):
    result_list = []
    for check_base in check_base_list:
        max_lr = -1
        max_check = ''
        for check_refer in check_refer_list:
            rcc_lr = Levenshtein.ratio(check_base, check_refer)
            if rcc_lr < max_ratio:
                continue
            if rcc_lr > max_lr:
                max_lr = rcc_lr
                max_check = check_refer
        if max_lr >= max_ratio:
            if is_ret_lr:
                result_list.append([check_base, max_check, max_lr])
            else:
                result_list.append([check_base, max_check])
        else:
            if is_ret_lr:
                result_list.append([check_base, '', max_lr])
            else:
                result_list.append([check_base, ''])
    return result_list


def except_info(e=None):
    t, v, tb = sys.exc_info()
    # f'当前类名称：{self.__class__.__name__}'
    # f"当前方法名：{sys._getframe().f_code.co_name}"
    if e is None:
        return {'lineno': tb.tb_lineno, 'error': '%s(\'%s\')' % (v.__class__.__name__, str(v))}
    else:
        return {'file': e.__traceback__.tb_frame.f_globals["__file__"], 'line': tb.tb_lineno,
                'error': '%s(\'%s\')' % (v.__class__.__name__, str(v))}
