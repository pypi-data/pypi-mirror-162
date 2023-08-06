# -*- coding: utf-8 -*-
import os
import re

import chardet
from parse import parse, compile, search, findall

from docparser.core.document_parser_base import DocumentParserBase
from loguru import logger


class TextDocumentParser(DocumentParserBase):
    """
    文本文件解析器
    """

    def __init__(self, file, configs):
        """
        初始化
        :param file:文件路径
        :param configs: 配置
        """
        self._file = file
        self._configs = configs

        if not os.path.exists(file):
            raise FileNotFoundError

        fi_encoding = self.get_encoding(file)
        with open(file, 'r', encoding=fi_encoding, errors='ignore') as f:
            self._data = f.readlines()

    def get_encoding(slef, file):
        """
        推断文件编码
        : return： 编码名称
        """
        f3 = open(file=file, mode='rb')  # 以二进制模式读取文件
        file_data = f3.read()  # 获取文件内容
        # print(file_data)
        f3.close()  # 关闭文件
        result = chardet.detect(file_data)
        encode = result['encoding']
        # gb2312的编码需要转成gbk或者gb18030处理
        if str(encode).upper() == 'GB2312':
            return 'gbk'
        return encode

    def parse(self):
        """
        根据配置抽取数据
        :return: 返回抽取的数据
        """

        data_bucket = {}
        parse_log = []
        results = []
        errors = {}
        parse_bucket = {}
        search_bucket = {}
        match_bucket = {}
        find_bucket = {}

        for key in self._configs.keys():
            item_config = self._configs[key]
            self.fixed(item_config)
            if item_config.get('parse'):
                for m_parse in item_config['parse']:
                    m_parse = self.clear_str(m_parse)
                    q_paser = compile(m_parse)
                    for m_i in self._data:
                        try:
                            result = None
                            m = self.clear_str(m_i)
                            if m_parse[0:2] == m[0:2]:
                                result = q_paser.parse(m)
                            elif m_parse.startswith('{'):
                                result = q_paser.parse(m)
                            if result is not None:
                                results.append(result)
                                logger.debug(f'源字符串{m_parse} 目标字符串{m} 结果：{result.named.items()}')
                                for kv, val in result.named.items():
                                    parse_bucket[kv] = str(val).strip()
                                    data_bucket[kv] = str(val).strip()
                                    parse_log.append({'key': kv, 'value': val, '_source': m, '_match_from': 'parse'})

                        except Exception as ex:
                            logger.error(f'[解析异常]源字符串{m_parse} 目标字符串{m} ', ex)
                            errors['parse_error'].append(ex.args)

            full_text = ''.join(self._data)
            if item_config.get('search'):
                for search_str in item_config.get('search'):
                    result = search(search_str, full_text)
                    for kv, val in result.named.items():
                        search_bucket[kv] = str(val).strip()
                        parse_log.append({'key': kv, 'value': val, '_source': None, '_match_from': 'search'})

            if item_config.get('findall'):
                for search_key, search_str in item_config.get('findall').items():
                    result = findall(search_str, full_text)
                    key_result = []
                    for kc in result:
                        for kv, val in kc.named.items():
                            key_result.append(str(val).strip())
                            parse_log.append({'key': kv, 'value': val, '_source': None, '_match_from': 'findall'})
                    find_bucket[search_key] = key_result

            if item_config.get('match'):
                for match_key, match_str in item_config.get('match').items():
                    nos_re = re.compile(match_str)
                    nos = nos_re.findall(full_text)
                    match_bucket[match_key] = nos

        data_bucket['parse_bucket'] = parse_bucket
        data_bucket['search_bucket'] = search_bucket
        data_bucket['find_bucket'] = find_bucket
        data_bucket['match_bucket'] = match_bucket
        data_bucket['_parse_log'] = parse_log
        # data_bucket['_body'] = self._data
        return [data_bucket], [errors]

    def fixed(self, item_config):
        """
        修正字符串中异常的字符
        """
        if item_config is None:
            return None
        fixed_dic = item_config.get('fixed', None)
        if fixed_dic is None:
            return None
        fixed_data = []
        for m in self._data:
            m = self.clear_str(m)
            for k, v in fixed_dic.items():
                m = m.replace(k, v)
            fixed_data.append(m)
        self._data = fixed_data
        return self._data

    def clear_str(self, input_str):
        """
        去除掉字符串中的首尾空格，换行符
        """
        if not input_str:
            return input_str
        return input_str.strip().replace('\n', '').replace('\r', '')


if __name__ == '__main__':
    converter = TextDocumentParser(
        r"C:\Users\RobinJiang\Desktop\noa-cmacgm-noticeofarrival-cmacgmamerigovespucci-0tunkw1ma-at220805044334-555889-000089.txt",
        {
            'standard': {
                'parse':
                    [
                        r'CMDU {bill_no} Waybill'
                    ],
                'search': ["CMDU {bill_no} Waybill"],
                'findall': {r'bill_no': "CMDU {bill_no} Waybill",
                            r"container": "# DAYS AT PORT DAY AT RAMP {containers}PLEASE NOTE"},
                'match': {r'bill_no': r"\w{3}\d{7}",
                          r'conatiner_no': r"\w{4}\d{7}"
                          },
            }
        })
    data, err = converter.parse()
    print(data)
