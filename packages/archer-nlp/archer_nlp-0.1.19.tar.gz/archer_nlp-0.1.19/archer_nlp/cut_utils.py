# coding: utf8
# 参考链接：https://github.com/z814081807/DeepNER
import re
from collections import defaultdict


def cut_sentences_v1(sent):
    """
    the first rank of sentence cut
    """
    sent = re.sub('([。！？\?])([^”’])', r"\1\n\2", sent)  # 单字符断句符
    sent = re.sub('(\.{6})([^”’])', r"\1\n\2", sent)  # 英文省略号
    sent = re.sub('(\…{2})([^”’])', r"\1\n\2", sent)  # 中文省略号
    sent = re.sub('([。！？\?][”’])([^，。！？\?])', r"\1\n\2", sent)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后
    return sent.split("\n")


def cut_sentences_v2(sent):
    """
    the second rank of spilt sentence, split '；' | ';'
    """
    sent = re.sub('([；;])([^”’])', r"\1\n\2", sent)
    return sent.split("\n")


def cut_sent(text, max_seq_len):
    # 将句子分句，细粒度分句后再重新合并
    sentences = []
    # 细粒度划分
    sentences_v1 = cut_sentences_v1(text)
    for sent_v1 in sentences_v1:
        if len(sent_v1) > max_seq_len - 2:
            sentences_v2 = cut_sentences_v2(sent_v1)
            sentences.extend(sentences_v2)
        else:
            sentences.append(sent_v1)
    assert ''.join(sentences) == text

    # 合并
    merged_sentences = []
    start_index_ = 0
    while start_index_ < len(sentences):
        tmp_text = sentences[start_index_]
        end_index_ = start_index_ + 1
        while end_index_ < len(sentences) and \
                len(tmp_text) + len(sentences[end_index_]) <= max_seq_len - 2:
            tmp_text += sentences[end_index_]
            end_index_ += 1
        start_index_ = end_index_
        merged_sentences.append(tmp_text)
    return merged_sentences


def get_sent_res(text):
    """
    根据标点和最大长度分成多个子句，多各子句的结果拼接成最终的句子结果
    :param text:
    :return:
    """
    # 每个程序不同，需单独写，下面示例仅供参考，主要看start_index的变化和tmp_start、tmp_end是否正确。
    text_list = [{'id': 1, 'text': text}]
    labels = defaultdict(list)
    for _ex in text_list:
        ex_idx = _ex['id']
        raw_text = _ex['text']
        sentences = cut_sent(text, max_seq_len=100)
        start_index = 0
        for sent in sentences:
            # get_sent_res：获取单个句子结果
            for _ent in get_sent_res(sent):
                tmp_start = _ent[1] + start_index
                tmp_end = tmp_start + len(_ent[0])
                assert raw_text[tmp_start: tmp_end] == _ent[0]
                # labels[ex_idx].append((_ent, tmp_start, tmp_end, _ent[0]))
                labels[ex_idx].append((tmp_start, tmp_end))
            start_index += len(sent)
            if not len(labels[ex_idx]):
                labels[ex_idx] = []
    return labels
