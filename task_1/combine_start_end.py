#-*- coding:utf-8 -*-
def combine_start_end(similar_word,end = '',start = ''):
    a = similar_word
    similar_word = list(set(similar_word)) #去重
    similar_word.sort(key=a.index) #保持顺序不变
    start_end = []
    for i in range(len(similar_word)):
        start_end.append(start + similar_word[i] + end)
    return (start_end)
