import re
import os
import pyltp
from bosonnlp import BosonNLP
from pyltp import SentenceSplitter
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
from pyltp import SementicRoleLabeller

LTP_DATA_DIR = r'./task_2/Extract_job_infos/ltp_data'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`ner.model`
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
srl_model_path = os.path.join(LTP_DATA_DIR, 'pisrl.model')  # 语义角色标注模型目录路径，模型目录为`srl`。注意该模型路径是一个目录，而不是一个文件。

job_list = []
personal_experience = []
# work_experience = []  改成放到函数中不会出现检查警告


def Extract_Institution_by_NER(line):
    # print("Extract_Institution_by_NER function.....")
    global institutions_list
    # LTP分词
    def segmentor(sentence):
        # print("segmentor function....")
        segmentor = Segmentor()  # 初始化实例
        # print(cws_model_path)
        segmentor.load(cws_model_path)  # 加载模型
        # print("test")
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
        # print("posttagger function.....")
        postagger = Postagger()  # 初始化实例
        # print(pos_model_path)
        postagger.load(pos_model_path)  # 加载模型
        # print("load done...")
        postags = postagger.postag(words)  # 词性标注
        # print("标注完成。。。")
        # for word, tag in zip(words, postags):
        #   print(word + '/' + tag)
        postagger.release()  # 释放模型
        # print("释放模型。。。")
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
        # print(pos_words_list)

        # print(netags)
        institution_list = []
        institutions_list = []
        for word, netag in zip(words, netags):
            #print(word + ':' + netag + '\n')
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
        # print(institutions_list)
            # return ','.join(institutions_list)
                # print(institution)
                # f1.write(institution + '\n')
            # print(word + ':' + netag + ' ')
            # f1.write(word + ':' + netag + ' ')
        # f1.write('\n')

    process(UseLTP=False)
    return ','.join(institutions_list)


def process_personal_experience(personal_experience_list):
    work_experience = []
    edu_element = ['人物 经历', '社会 任职', '学位', '出生', '学习', '就读', '博士', '硕士', '本科']
    for exp in personal_experience_list:
        count = 0
        for element in edu_element:
            if element not in exp:
                count += 1
                # print('yes')
        if count == 9:
            work_experience.append(exp)
            # print(work_experience)
    return work_experience


def read_file(filename1):
    with open(filename1, 'r', encoding='utf-8') as jobs:
        job_list = eval(jobs.read())
    # with open(filename2, 'r', encoding='utf-8') as f:
    #     resume_txt = f.readlines()
    return job_list


def process_work_experience(work_experience_list):
    global job_list
    global institutions_list
    global time_unit_job_list
    # with open('title_list.py', 'r', encoding='utf-8') as jobs:
    #     job_list = eval(jobs.read())
    time_unit_job_list = []
    for exp in work_experience_list:

        # 获取任职起始时间点
        # print(exp)
        begin_time_pre = re.findall(
            r'(\d*年|\d*年 \d*月|\d*年\d*月|\d*.\d*|\d*|\d*年 起|\d* 起|\d*年 \d*月 \d*日) (—|－|-|——|至|，).*?', exp)
        if begin_time_pre:
            begin_time = begin_time_pre[0][0]
        else:
            begin_time = []
        # print(begin_time)
        # 获取任职终止时间点
        end_time_pre = re.findall(r'.*(—|－|-|——|至) (\d*年 \d*月|\d*年|\d*.\d*|\d*)', exp)
        if end_time_pre:
            end_time = end_time_pre[0][1]
        else:
            end_time = ''
        job_out_list = []  # 该列表必须在循环里面，对每条工作经历文本单独处理
        job_txt1 = re.findall(r'.* (当选|担任|入选|任|任命 为|任命|成立|加入) (.*?) (,|、|，) (.*).*? (。|;|；)', exp)
        job_new_txt1 = []
        if job_txt1:
            for info in job_txt1[0]:
                if info not in ['成立', '加入', '担任', '当选', '入选', '任', '任命', '任命 为', ',', '、', '，', '。', ';', '；']:
                    # print(info)
                    job_new_txt1.append(info)
        # print(job_new_txt1)
        if job_new_txt1:
            for each in job_new_txt1:
                if each not in job_out_list:
                    # print(each)
                    job_out_list.append(each)
        # print(job_txt1)
        job_txt2 = re.findall(r'.* (当选|担任|入选|任|任命 为|任命|成立|加入) (.*?) (,|，|。|;|；)', exp)
        # print(job_txt2)
        job_new_txt2 = []
        if job_txt2:
            for info in job_txt2[0]:
                if info not in ['成立', '加入', '担任', '当选', '入选', '任', '任命', '任命 为', ',', '、', '，', '。', ';', '；']:
                    # print(info)
                    job_new_txt2.append(info)
        if job_new_txt2:
            for each in job_new_txt2:
                if each not in job_out_list:
                    # print(each)
                    job_out_list.append(each)
        job_txt3 = re.findall(r'.* 在 (.*?) 工作 (，|。|;|；) .* 担任(.*?) 。', exp)
        job_new_txt3 = []
        if job_txt3:
            for info in job_txt3[0]:
                if info not in ['成立', '加入', '担任', '当选', '入选', '任', '任命', '任命 为', ',', '、', '，', '。', ';', '；']:
                    # print(info)
                    job_new_txt3.append(info)
        if job_new_txt3:
            for each in job_new_txt3:
                if each not in job_out_list:
                    # print(each)
                    job_out_list.append(each)
        job_txt4 = re.findall(r'.* 加入 (.*?) (，|。|;|；) .* 担任 (.*?) 。', exp)
        job_new_txt4 = []
        if job_txt4:
            for info in job_txt4[0]:
                if info not in ['成立', '加入', '担任', '当选', '入选', '任', '任命', '任命 为', ',', '、', '，', '。', ';', '；']:
                    # print(info)
                    job_new_txt4.append(info)
        if job_new_txt4:
            for each in job_new_txt4:
                if each not in job_out_list:
                    # print(each)
                    job_out_list.append(each)
        # print(job_out_list)

        job_filter2_symbol_list = []
        for one in job_out_list:  # 对每一条任职信息都预处理一遍，过滤检查
            if '、' in one:  # 去除任职文本里的顿号
                job_filter2 = one.split('、')
                # print(job_filter2)
                for one_job in job_filter2:
                    one_job_ = one_job.strip()
                    if one_job_ not in job_filter2_symbol_list:
                        job_filter2_symbol_list.append(one_job_)
            else:
                if one.strip() not in job_filter2_symbol_list:
                    job_filter2_symbol_list.append(one.strip())
            # print(job_filter2_symbol_list)

        job_filter3_number_list = []
        for one_job in job_filter2_symbol_list:
            # 去除任职信息末尾的标注信息如:[7]
            # print(one_job)
            remove_number = re.findall(r'.* (\[ \d* \]).*', one_job)
            # print(remove_number)
            if remove_number:
                job_filter3_num = one_job.replace(remove_number[0], '')
                if job_filter3_num.strip() not in job_filter3_number_list:
                    job_filter3_number_list.append(job_filter3_num.strip())
            else:
                if one_job.strip() not in job_filter3_number_list:
                    job_filter3_number_list.append(one_job.strip())
        # print(job_filter3_number_list)

        job_filter4_years_list = []
        for one_ in job_filter3_number_list:
            # 去除任职信息末尾的任职年份区间，并更新任职时间如（ 2000年 — 2002年 ）
            # print(one_)
            # 更新准确的任职区间
            begin_time_pre = re.findall(
                r'(\d*年|\d*年 \d*月|\d*年\d*月|\d+.\d*|\d*|\d*年 起|\d* 起|\d*年 \d*月 \d*日) (—|－|-|——|至|，).*?', one_)
            if begin_time_pre:
                begin_time_pre_ = begin_time_pre[0][0]
                if begin_time_pre_ == '':
                    begin_time = re.findall(
                        r'(\d*年|\d*年 \d*月|\d*年\d*月|\d*.\d*|\d*|\d*年 起|\d* 起|\d*年 \d*月 \d*日) (—|－|-|——|至|，).*?', exp)[0][0]
                # print(begin_time)
            else:
                begin_time_pre = re.findall(
                    r'(\d*年|\d*年 \d*月|\d*年\d*月|\d*.\d*|\d*|\d*年 起|\d* 起|\d*年 \d*月 \d*日) (—|－|-|——|至|，).*?', exp)
                if begin_time_pre:
                    begin_time = begin_time_pre[0][0]
                else:
                    begin_time = ''
            end_time_pre = re.findall(r'.*(—|－|-|——|至) (\d*年 \d*月|\d*年|\d*.\d*|\d*)', one_)
            if end_time_pre:
                end_time = end_time_pre[0][1]
                # print(end_time)
            else:
                end_time_pre = re.findall(r'.*(—|－|-|——|至) (\d*年 \d*月|\d*年|\d*.\d*|\d*)', exp)
                if end_time_pre:
                    end_time = end_time_pre[0][1]
                else:
                    end_time = ''
            remove1 = re.findall(r'.*(\（.*\d*年.* \）).*', one_)
            # print(remove1)
            if remove1:
                job_filter4_years = one_.replace(remove1[0], '')
                if job_filter4_years.strip() not in job_filter4_years_list:
                    # job_filter4_years_list.append(job_filter4_years.strip())
                    info = job_filter4_years.strip()
                else:
                    info = ''

            else:
                if one_ not in job_filter4_years_list:
                    job_filter4_years_list.append(one_.strip())
                    info = one_
                else:
                    info = ''
        # print(job_filter4_years_list)
# 弃用下面的循环，为了将类似‘教授级 高级 工程师（2000年—2002年）、主任（2002年—2006年）’
# 的信息上的任职年份起止时间点和特定的职称逐一对应上
        # for info in job_filter4_years_list:
            # job = []
            # institution = []
            if info:
                units = info.split(' ')
                # print(units)
                if len(units) >= 4:
                    unit_1 = units[-1]
                    unit_2 = units[-2]
                    unit_3 = units[-3]
                    unit_4 = units[-4]
                    unit_21 = unit_2 + ' ' + unit_1
                    unit_321 = unit_3 + ' ' + unit_2 + ' ' + unit_1
                    unit_4321 = unit_4 + ' ' + unit_3 + ' ' + unit_2 + ' ' + unit_1
                    if unit_4321 in job_list:
                        # print('职称_职位：{}'.format(unit_4321))
                        job = unit_4321
                        unit_institution = units[: -4]
                        institution = ' '.join(unit_institution)
                        # print('所在单位_机构：{}'.format(institution))
                    elif unit_321 in job_list:
                        # print('职称_职位：{}'.format(unit_1))
                        job = unit_321
                        unit_institution = units[: -3]
                        institution = ' '.join(unit_institution)
                        # print('所在单位_机构：{}'.format(institution))
                    elif unit_21 in job_list:
                        # print('职称_职位：{}'.format(unit_1))
                        job = unit_21
                        unit_institution = units[: -2]
                        institution = ' '.join(unit_institution)
                        # print('所在单位_机构：{}'.format(institution))
                    else:
                        if unit_1 in job_list:
                            job = unit_1
                            unit_institution = units[: -1]
                            institution = ' '.join(unit_institution)
                        else:
                            job = ''
                            unit_institution = units
                            institution = ' '.join(unit_institution)
                        # print('所在单位_机构：{}'.format(institution))
                elif len(units) == 3:
                    unit_1 = units[-1]
                    unit_2 = units[-2]
                    unit_3 = units[-3]
                    # print(unit_1, unit_2, unit_3)
                    unit_21 = unit_2 + ' ' + unit_1
                    unit_321 = unit_3 + ' ' + unit_2 + ' ' + unit_1
                    if unit_321 in job_list:
                        # print('职称_职位：{}'.format(unit_1))
                        job = unit_321
                        institution = ''
                        # print('所在单位_机构：{}'.format(institution))
                    elif unit_21 in job_list:
                        # print('职称_职位：{}'.format(unit_1))
                        job = unit_21
                        unit_institution = units[: -2]
                        institution = ' '.join(unit_institution)
                        # print('所在单位_机构：{}'.format(institution))
                    else:
                        if unit_1 in job_list:
                            job = unit_1
                            institution = ''
                        else:
                            job = ''
                            unit_institution = units
                            institution = ' '.join(unit_institution)
                        # print('所在单位_机构：{}'.format(institution))
                elif len(units) == 2:
                    unit_1 = units[-1]
                    unit_2 = units[-2]
                    # print(unit_1, unit_2)
                    unit_21 = unit_2 + ' ' + unit_1
                    if unit_21 in job_list:
                        # print('职称_职位：{}'.format(unit_1))
                        job = unit_21
                        institution = ''
                        # print('所在单位_机构：{}'.format(institution))
                    else:
                        if unit_1 in job_list:
                            job = unit_1
                            unit_institution = units[: -1]
                            institution = ' '.join(unit_institution)
                        else:
                            job = ''
                            unit_institution = units
                            institution = ' '.join(unit_institution)
                        # print('所在单位_机构：{}'.format(institution))
                else:
                    unit_1 = units[-1]
                    if unit_1 in job_list:
                        job = unit_1
                        institution = ''
                    else:
                        job = ''
                        unit_institution = units
                        institution = ' '.join(unit_institution)
                Institution_by_NER = Extract_Institution_by_NER(exp)
                # print("{"+"\'起始时间\':\'{}\',\'终止时间\':\'{}\',\'所在单位\':\'{}\',\'职称\':\'{}\'".format(begin_time, end_time, institution, job)+"}")
                time_unit_job = "{"+"\"起始时间\":\"{}\",\"终止时间\":\"{}\",\"所在单位\":\"{}\",\"职称\":\"{}\"".format(begin_time.replace(" ",""), end_time.replace(" ",""), Institution_by_NER.replace(" ",""), job.replace(" ",""))+"}"
                time_unit_job_list.append(eval(time_unit_job))
    return time_unit_job_list


def main_han(resume_txt):

    time_unit_job_list = []
    global job_list
    global institutions_list
    # 读入简历文件和任职列表
    job_list = read_file('/home/chenxl/data_mining_resume/task_2/title_list.py')
    # print(job_list, resume_txt)
    flag_store = False
    for line in resume_txt:
        if line == '人物 经历\n':
            # (开始使用字典遍历的标志，将职称内容读到job_list中）
            flag_store = True     # (开始使用字典遍历的标志，将职称内容读到job_list中）

        if flag_store:
            personal_experience.append(line)

        if line == '社会 任职\n':
            # (结束字典遍历的标志，表示职称内容已经全部读完到job_list中)
            flag_store = False
    # print(personal_experience)
    # 处理人物经历，获取工作经历
    work_experience = process_personal_experience(personal_experience)

    # 处理工作经历，获取任职多信息列表
    time_unit_job_list = process_work_experience(work_experience)
    # print(time_unit_job_list)
    return time_unit_job_list


if __name__ == '__main__':
    txt = ['基本 信息\n', 
    '中文名 : 方滨兴\n', 

    '外文 名 : BinxingFang\n', '国籍 : 中国\n', '性别 : 男\n', '毕业 院校 : 哈尔滨 工业 大学\n', '主要 成就 : 2005年 当选 为 中国 工程院 院士\n', '曾 任职 : 北京 邮电 大学 校长\n', '原籍 : 江西省 上饶市 万年 县\n', '出生地 : 黑龙江 哈尔滨市\n', '出生 日期 : 1960年 07月 17日\n', '职业 : 科研 工作者\n', '民族 : 汉族\n', '代表 作品 : 《 论 网络 空间 主权 》 、 《 在线 社交 网络 分析 》\n', '信仰 : 共产主义\n', '政治 面貌 : 中国 共产党 党员\n', '人物 经历\n', '1960年 7月 17日 ， 方滨兴 出生 于 黑龙江省 哈尔滨市 ， 原籍 江西省 上饶市 万年 县 。\n', '1978年 3月 ， 方滨兴 进入 哈尔滨 工业 大学 计算机 与 应用 专业 学习 。\n', '1982年 1月 ， 方滨兴 从 哈尔滨 工业 大学 毕业 ， 获得 学士 学位 ， 并 考上 清华大学 计算机 组织 与 系统 结构 专业 研究生 。\n', '1984年 10月 ， 方滨兴 获得 硕士 学位 后 回到 哈尔滨 工业 大学 计算机 系 工作 ， 先后 担任 助教 、 讲师 、 副教授 、 教授 （ 1992年 晋升 ） 、 博士生 导师 （ 1995年 晋升 ） 。\n', '1986年 2月 ， 方滨兴 在 哈尔滨 工业 大学 就读 在职 博士 研究生 （ 1989年 9月 毕业 ） 。\n', '1990年 4月 ， 方滨兴 进入 国防 科学技术 大学 计算机 科学 与 技术 博士后 流动站 在职 研究 学习 （ 至 1993年 10月 ） ， 师从 计算机 专家 胡守仁 教授 。\n', '1993年 7月 ， 方滨兴 担任 哈尔滨 工业 大学 计算机 系 计算机 系统 结构 教研室 副 主任 、 主任 （ 至 1997年 5月 ） 。\n', '1997年 6月 ， 方滨兴 担任 哈尔滨 工业 大学 计算机 与 电气 工程学院 副 院长 （ 至 1999年 6月 ） 。\n', '1998年 8月 ， 方滨兴 担任 哈尔滨 工业 大学 网络 中心 主任 （ 至 1999年 6月 ） 。\n', '1999年 6月 ， 方滨兴 加入 中国 共产党 。 7月 在 国家 计算机 网络 应急 技术 处理 协调 中心 工作 ， 先后 担任 副 总工 （ 1999年 - 2000年 ） 、 总工程师 、 副 主任 、 教授级 高级 工程师 （ 2000年 - 2002年 ） 、 主任 （ 2002年 - 2006年 ） 。\n', '2003年 4月 ， 方滨兴 担任 信息 产业部 互联网 应急 处理 协调 办公室 主任 （ 至 2008年 1月 ） ， 同年 在 中央 党校 地厅级 干部 进修班 第41 期 脱产 学习 半 年 。\n', '2004年 ， 方滨兴 入选 新 世纪 百千万 人才 工程 国家级 人选 。\n', '2005年 ， 方滨兴 当选 中国 工程院 院士 。\n', '2006年 ， 方滨兴 被 任命 为 国家 计算机 网络 与 信息 安全 管理 中心 名誉 主任 。\n', '2007年 12月 ， 方滨兴 担任 北京 邮电 大学 校长 （ 至 2013年 6月 ） 。\n', '2013年 6月 ， 方滨兴 称 因 身体 原因 ， 不再 连任 北邮 校长 职务 。\n', '2014年 11月 19日 ， 方滨兴 在 世界 互联网 大会 做 题 为 《 物联网 搜索 技术 》 的 演讲 。\n', '2016年 3月 25日 ， 中国 网络 空间 安全 协会 在 北京 举行 成立 大会 ， 方滨兴 当选 为 中国 网络 空间 安全 协会 理事长 。 8月 ， 担任 哈尔滨 工业 大学 （ 深圳 ） 计算机 科学 与 技术 学院 教授 、 首席 学术 顾问 。\n', '2017年 7月 ， 方滨兴 团队 30 多 人 整体 加入 广州 大学 ， 成立 广州 大学 网络 空间 先进 技术 研究院 ， 担任 名誉 院长 。\n', '社会 任职\n', '2002年 起 信息 产业部 通信 科学技术 委员会 常务委员\n', '2003年 起 中国 通信 标准化 协会 理事 、 网络 与 信息 安全 技术 委员会 （ TC8 ） 主席 ， 专家 咨询 委员会 委员 、 技术 管理 委员会 委员\n', '2003年 起 财政部 金财 工程 专家 咨询 委员会 委员\n', '2004年 起 中国 下一代 互联网 示范 工程 （ CNGI ） 项目 专家 委员会 委员\n', '2004年 起 中国 互联网 协会 副 理事长 、 网络 与 信息 安全 工作 委员会 主任\n', '2004年 起 国家 计算机 网络 与 信息 安全 管理 中心 科学技术 委员会 主任\n', '2004年 起 解放军 总后勤部 信息化 专家 咨询 委员会 委员\n', '2005年 起 国家 信息 安全 产品 认证 管理 委员会 委员\n', '2005年 起 中国 通信 学会 会士 、 常务 理事 、 通信 安全 技术 委员会 主任 ， 学术 工作 委员会 委员\n', '2005年 起 中国 网络 通信 集团公司 技术 委员会 委员\n', '2005年 起 清华大学 计算机 系 兼职 教授\n', '2005年 起 全国 人大 信息化 系统 改造 和 建设 工程 专家 咨询 顾问组 成员\n', '2005年 起 国家 863 计划 十一 五 信息 技术 领域 专家 委员会 委员\n', '2006年 起 哈尔滨 工业 大学 教授 、 博士生 导师 、 哈尔滨 工业 大学 国家 计算机 内容 安全 重点 实验室 主任\n', '2006年 起 国家 信息化 专家 咨询 委员会 委员 ， 网络 与 信息 安全 专业 委员会 副 主任\n', '2006年 起 上海市 互联网 宣传 管理 技术 咨询 专家\n', '2006年 起 北京市 信息化 专家 咨询 委员会 委员\n', '2006年 起 国家 应急 管理 专家组 成员\n', '2007年 起 公安部 信息 安全 特聘 专家\n', '2007年 起 新 世纪 百千万 人才 工程 国家级 人选 评审 委员会 委员\n', '2007年 起 北京市 公安 交通 管理局 专家 顾问团 成员\n', '2007年 起 中国 科学院 计算所 客座 研究员 、 博士生 导师 、 信息 安全 首席 科学家\n', '2007年 起 国防 科学技术 大学 特聘 教授 、 博士生 导师\n', '2007年 起 《 通信 学报 》 编辑 委员会 主任\n', '2007年 起 国家 自然科学 基金 可信 软件 重大 专项 专家组 副 组长\n', '2008年 起 中国 计算机 学会 副 理事长 、 计算机 安全 专业 委员会 主任\n', '2008年 至 2013年 中华人民共和国 第十一 届 全国 人民 代表大会 代表\n', '2016年 8月 哈尔滨 工业 大学 （ 深圳 ） 计算机 学院 首席 学术 顾问\n', '2016年 12月 中国 中文 信息 学会 第八 届 理事会 理事长\n', '中国 电子 信息 产业 集团 首席 科学家\n', '信息 内容 安全 技术 国家 工程 实验室 主任\n', '可信 分布式 计算 与 服务 教育部 重点 实验室 （ 北京 邮电 大学 ） 主任\n', '中国 云 安全 与 新兴 技术 安全 创新 联盟 理事长\n', '教育部 网络 空间 安全 学科 评议组 召集人\n', '国家 八六三 计划 信息 安全 主题 组 专家\n', '国家 发展 改革委 信息 安全 专家 咨询组 成员\n', '主要 成就\n', '科研 综述\n', '方滨兴 的 研究 领域 主要 是 网络 与 信息 安全 的 理论 与 技术 ， 侧重点 在于 信息 安全 体系 框架 的 研究 、 网络 协议 分析 技术 、 IPv6 技术 、 网络 应急 处理 技术 、 系统 灾备 技术 、 入侵 检测 技术 、 honey-net 技术 、 计算机 病毒 技术 、 信息 捕获 与 分析 技术 、 高效 文字 匹配 算法 研究 、 网络 健壮性 研究 、 网格 计算 及其 安全 技术 。\n', '1989年 方滨兴 开始 研究 计算机 病毒 防御 技术 ， 并 于 1992年 出版 《 计算机 病毒 及其 防范 》 专著 ， 20 世纪 90 年代 末 从事 计算机 安全 事件 入侵 检测 方面 的 研究 工作 。 1999年 提出 建设 国家 信息 安全 基础 设施 的 理念 ， 并 组织 建设 了 相关 系统 ， 为 保障 国家 信息 安全 工作 奠定 了 坚实 的 技术 基础 。\n', '学术 论著\n', '截至 2017年 3月 ， 方滨兴 在 中国 国内外 核心 学术 期刊 、 会议 上 发表 论文 400 余 篇 ， 出版 著作 3 部 。\n', '承担 项目\n', '截至 2017年 12月 ， 方滨兴 先后 担任 信息 安全 关键 技术 973 项目 （ 2007年 ） 、 社交 网络 分析 973 项目 首席 科学家 。\n', '科研 成果 奖励\n', '截至 2017年 3月 ， 方滨兴 作为 第一 完成 人 ， 先后 获得 国家 科技 进步 一 、 二等奖 4 项 ， 部级 科技 进步奖 10 余 项 ， 省 、 市 青年 科技 奖 3 次 。\n', '2017.09 《 论 网络 空间 主权 》 方滨兴 著 北京 ： 科学 出版社\n', '2014.11 《 在线 社交 网络 分析 》 方滨兴 著 北京 ： 电子 工业 出版社\n', '2010.12 《 网 和 天下 三 网 融合 理论 、 实验 与 信息 安全 》 曾剑秋 ， 方滨兴 编著 北京 ： 北京 邮电 大学 出版社\n', '1992.09 《 计算机 病毒 及其 对策 》 方滨兴 等 编著 哈尔滨 ： 黑龙江 科学技术 出版社\n', '1980 《 ECLIPSE MV / 8000 超级 小型 机产品 介绍 》 方滨兴 译 苏州 电子 计算机 厂 情报 厂\n', '2007年 至 2011年 信息 安全 理论 及 若干 关键 技术 国家 973 项目 （ 2007 CB311100 ）\n', '2010年 至 2012年 非常规 突发 事件 中 网络 舆情 作用 机制 与 相关 技术 研究 国家 自然科学 基金 重大 研究 计划 培育 项目 （ 90924029 ）\n', '2010年 至 2013年 Web 搜索 与 挖掘 的 新 理论 和 新 方法 - 支持 舆情 监控 的 Web 搜索 与 挖掘 的 理论 与 方法 研究 国家 自然科学 基金 重点 研究 计划 项目 （ 60933005 ）\n', '2008年 至 2010年 网络 环境 下 特定 信息 获取 与 处理 技术 国防 科技 创新 团队 项目\n', '2009年 至 2011年 下一代 互联网 舆情 管理 系统 应用 示范 国家 发改委 CNGI 下一代 互联网 应用 示范 项目\n', '2006年 至 2010年 大规模 网络 入侵 定位 与 容忍 总装 预研 项目\n', '1995年 支持 存储器 无 冲突 访问 的 互联网络 开关 门阵 列 芯片 的 研制 部级 科学 进步 二等奖 ， 第二\n', '1995年 多 机 系统 的 性能 评价 的 研究 部级 科学 进步 二等奖 ， 第二\n', '1996年 支持 存储器 无 冲突 访问 的 互连 开关 设计 理论 及 方法 部级 科学 进步 三等奖 ， 第一\n', '1996年 ABC-90 阵列 计算机 综合 模拟 器 部级 科学 进步 三等奖 ， 第一\n', '2001年 计算机 病毒 及其 预防 技术 国防 科学技术 三等奖 ， 排名 第一\n', '2002年 国家 信息 安全 管理 系统 国家 科学技术 进步 一等奖 ， 排名 第一\n', '2002年 大 范围 宽带 网络 动态 处置 系统 国防 科学技术 二等奖 ， 排名 第二\n', '2004年 大规模 网络 信息 获取 系统 国家 科学技术 进步 二等奖 ， 排名 第一\n', '2004年 国家 信息 安全 展 略 研究 国家 发展 改革委 机关 优秀 成果 三等奖\n', '2005年 搜索引擎 安全 管理 系统 中国 通信 学会 科学技术 二等奖 ， 排名 第二\n', '2007年 国家 通信 数据 安全 管理 系统 国家 科学技术 进步 二等奖 ， 排名 第一\n', '2015年 在线 社交 网络 分析 关键 技术 及 系统 国家级 二等奖\n', '2018年 大规模 网络 安全 态势 分析 关键 技术 及 系统 YHSAS 国家 科学技术 进步奖 二等奖\n', '教育 理念\n', '方滨兴 认为 ： 网络 空间 安全 人才 培养 存在 三 个 特殊性 ： 一 是 自身 网络 安全 的 特殊性 ； 二 是 人才 特殊性 ； 三 是 网络 空间 安全 人才 培养 的 特殊性 。\n', '指导 学生\n', '截至 2017年 3月 ， 方滨兴 先后 培养 硕士 与 博士生 百 余 名 。\n', '2001年 在 信息 产业部 重点 工程 中 做出 突出 贡献 特等奖 先进 个人 称号 信息 产业部\n', '2001年 先进 个人 称号 中组部 、 中宣部 、 中央 政法委 、 公安部 、 民政部 、 人事部 等 联合\n', '2001年 国务院 政府 特殊 津贴 专家 中华人民共和国 国务院\n', '2002年 全国 杰出 专业 技术 人才 荣誉 称号 中组部 、 中宣部 、 人事部 、 科技部 联合\n', '2005年 中国 工程院 院士 中国 工程院\n', '2006年 8月 信息 产业 科技 创新 先进 工作者 信息 产业部\n', '2006 年度 中国 信息 安全 保障 突出 贡献奖 《 计算机 世界 》\n', '2007年 何 梁何利 基金 科学 与 技术 进步奖 何梁 何利 基金会\n', '2014年 中国 互联网 年度 人物 特别 贡献奖 人民网 、 新华网 、 中国 网络 电视台 等\n', '方滨兴 在 信息 安全 理论 及 若干 关键 技术 领域 获得 了 卓越 学术 成就 ， 做出 了 重要 贡献 。 （ 人民网 评 ）\n', '方滨兴 先后 提出 了 国家 信息 安全 基础 设施 建设 思想 、 信息 安全 属性 可 计算 理论 ， 在 网络 与 信息 安全 领域 做出 了 突出 贡献 。 （ 广州 大学 评 ）\n', '2018年 9月 3日 ， 为 培养 更 多 优秀 的 网络 安全 人才 ， 广州 大学 网络 空间 先进 技术 研究院 专门 成立 了 以 方滨兴 名字 命名 的 方滨兴 班 （ 简称 方班 ） ， 主要 围绕 几 个 方向 开展 人才 培养 ， 分别 是 网络 安全 研究 、 物联网 及 安全 研究 、 大数据 及 安全 研究 、 先进 计算 技术 研究 。\n']
    main_han(txt)



