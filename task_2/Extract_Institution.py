import os
from bosonnlp import BosonNLP
from pyltp import SentenceSplitter
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
from pyltp import SementicRoleLabeller

LTP_DATA_DIR = r'I:\Coding_Practice\LTP\ltp_data_v3.4.0'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`ner.model`
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
srl_model_path = os.path.join(LTP_DATA_DIR, 'srl')  # 语义角色标注模型目录路径，模型目录为`srl`。注意该模型路径是一个目录，而不是一个文件。


def Extract_Institution_by_NER(line):
    # LTP分词
    def segmentor(sentence):
        segmentor = Segmentor()  # 初始化实例
        segmentor.load(cws_model_path)  # 加载模型
        # segmentor.load_with_lexicon('cws_model_path', 'D:\pyprojects\LTP\ltp_data\dict.txt') #加载模型   使用用户自定义字典的高级分词
        words = segmentor.segment(sentence)  # 分词
        # 默认可以这样输出
        # print('/'.join(words))
        # 可以转换成List 输出
        segmentor.release()  # 释放模型
        # seg_words = " ".join(words_list)
        return words

    # 波森分词
    def Text_Seg_By_BosonNLP(line):
        nlp = BosonNLP('QhCMB7FS.33943.0OYvhfw0JCx8')
        words = nlp.tag(line)[0]['word']
        # output_txt.write('{}\n'.format(result))             # 以列表字符串的形式写入
        # seg_words = ' '.join(result)   # 以纯文本的形式写入
        return words

    # 词性标注
    def posttagger(words):
        postagger = Postagger()  # 初始化实例
        postagger.load(pos_model_path)  # 加载模型
        postags = postagger.postag(words)  # 词性标注
        # for word, tag in zip(words, postags):
        #   print(word + '/' + tag)
        postagger.release()  # 释放模型
        return postags

    # 命名实体识别
    def ner(words, postags):
        recognizer = NamedEntityRecognizer()  # 初始化实例
        recognizer.load(ner_model_path)  # 加载模型
        netags = recognizer.recognize(words, postags)  # 命名实体识别
        # for word, ntag in zip(words, netags):
        #   print(word + '/' + ntag)
        recognizer.release()  # 释放模型
        return netags

    def process(UseLTP=True):
        global institutions_list
        if UseLTP == True:  # 使用LTP分词
            words = segmentor(line)
            words_list = list(words)
        else:  # 使用波森分词
            words = Text_Seg_By_BosonNLP(line)
            words_list = list(words)
        seg_words = " ".join(words_list)
        # print(seg_words)
        postags = posttagger(words_list)
        # print(postags)
        netags = ner(words, postags)
        sentence_pos = []
        for word, pt in zip(seg_words.split(" "), postags):
            # print(word + "/" + pt)
            sentence_pos.append(word + "/" + pt)
            pos_words_list = " ".join(sentence_pos)
        print(pos_words_list)

        # print(netags)
        institution_list = []
        institutions_list = []
        for word, netag in zip(words, netags):
            print(word + ':' + netag + '\n')
            # if netag == 'B-Ni' or 'I-Ni' or 'E-Ni' or 'S-Ni':  # 过滤非命名实体
            if netag in ['B-Ni', 'I-Ni']:  # 过滤非命名实体
                institution_list.append(word)
            elif netag == 'E-Ni':
                institution_list.append(word)
                institution = ''.join(institution_list)
                institution_list = []
                if institution not in institutions_list:
                    institutions_list.append(institution)
                # print(institutions_list)
                # f1.write(institution + '\n')
            elif netag == 'S-Ni':
                institution = word
                if institution not in institutions_list:
                    institutions_list.append(institution)
        print(institutions_list)
            # return ','.join(institutions_list)
                # print(institution)
                # f1.write(institution + '\n')
            # print(word + ':' + netag + ' ')
            # f1.write(word + ':' + netag + ' ')
        # f1.write('\n')
    global institutions_list
    process(UseLTP=False)
    return ','.join(institutions_list)

if __name__ == '__main__':
    # with open('./ner_data.txt', 'a', encoding='UTF-8') as f1:
    #     f1.seek(0)
    #     f1.truncate()
    global institutions_list
    with open('方滨兴_百度百科.txt', 'r', encoding='UTF-8') as f1:
        lines = f1.readlines()
        for line in lines:
            NER = Extract_Institution_by_NER(line)
            if NER:
                with open('NER_Institution.txt', 'a', encoding='UTF-8') as f2:
                    f2.write(NER)
                    f2.write('\n')


