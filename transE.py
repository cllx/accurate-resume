from random import uniform, sample
from numpy import *
from copy import deepcopy

class TransE:
    def __init__(self, entityList, relationList, tripleList, margin = 1, learingRate = 0.00001, dim = 10, L1 = True):
        self.margin = margin
        self.learingRate = learingRate #学习率
        self.dim = dim#向量维度
        self.entityList = entityList#一开始，entityList是entity的list；初始化后，变为字典，key是entity，values是其向量（使用narray）。
        self.relationList = relationList#理由同上
        self.tripleList = tripleList#理由同上
        self.loss = 0
        self.L1 = L1

    def initialize(self):
        '''
        初始化向量
        '''
        entityVectorList = {}
        relationVectorList = {}
        for entity in self.entityList:
            n = 0
            entityVector = []
            while n < self.dim:
                ram = init(self.dim)#初始化的范围，dim为10，调用init返回一个在一定范围内的随机初始化的值
                entityVector.append(ram) #用这个值先随机为entityVector进行初始化，每一个实体用以dim为维度的一定范围的随机数初始化
                n += 1
            entityVector = norm(entityVector)#归一化，将实体随机初始化后的值归一化
            entityVectorList[entity] = entityVector #将归一化后的初始化实体向量赋给实体向量列表
        print("entityVector初始化完成，数量是%d"%len(entityVectorList))
        for relation in self. relationList: #这下面是关系的初始化，与实体向量的随机初始化过程类似
            n = 0
            relationVector = []
            while n < self.dim:
                ram = init(self.dim)#初始化的范围
                relationVector.append(ram)
                n += 1
            relationVector = norm(relationVector)#归一化
            relationVectorList[relation] = relationVector
        print("relationVectorList初始化完成，数量是%d"%len(relationVectorList))
        self.entityList = entityVectorList #将随机初始化后的实体向量列表赋给self.entityList
        self.relationList = relationVectorList #将随机初始化后的关系向量列表赋给self.entityList

    def transE(self, cI = 20, filename = '方滨兴'):
        print("训练开始")
        for cycleIndex in range(cI): #循环cI轮
            Sbatch = self.getSample(25) #调用getSample从训练数据中抽取25个数据
            Tbatch = []#元组对（原三元组，打碎的三元组）的列表 ：{((h,r,t),(h',r,t'))}
            for sbatch in Sbatch:
                tripletWithCorruptedTriplet = (sbatch, self.getCorruptedTriplet(sbatch)) #tripletWithCorruptedTriplet保存打乱的结果
                if(tripletWithCorruptedTriplet not in Tbatch):
                    Tbatch.append(tripletWithCorruptedTriplet)
            self.update(Tbatch)
            if cycleIndex % 100 == 0:
                print("第%d次循环"%cycleIndex)
                print(self.loss)
                Relationpath = "static/TransE_shuju/"+filename+"_relationVector.txt"
                self.writeRelationVector(Relationpath) #调用writeRelationVector函数写入
                Entitypath = "static/TransE_shuju/"+filename+"_entityVector.txt"
                self.writeEntilyVector(Entitypath) #调用writeRelationVector函数写入
                self.loss = 0

    def getSample(self, size):
        return sample(self.tripleList, size) #从triplelist选择size大小个随机且独立的元素

    #对头或者尾实体进行随机打乱扰动
    def getCorruptedTriplet(self, triplet):
        '''
        training triplets with either the head or tail replaced by a random entity (but not both at the same time)
        :param triplet:
        :return corruptedTriplet:
        '''
        i = uniform(-1, 1)
        if i < 0:#小于0，打坏三元组的第一项
            while True:
                entityTemp = sample(self.entityList.keys(), 1)[0]
                if entityTemp != triplet[0]:
                    break
            corruptedTriplet = (entityTemp, triplet[1], triplet[2])
        else:#大于等于0，打坏三元组的第二项
            while True:
                entityTemp = sample(self.entityList.keys(), 1)[0]
                if entityTemp != triplet[1]:
                    break
            corruptedTriplet = (triplet[0], entityTemp, triplet[2])
        return corruptedTriplet

    #update主要负责更新修改实体或关系的向量，使其满足TransE的要求，存在关系的实体和关系向量满足一定的等式
    def update(self, Tbatch):
        copyEntityList = deepcopy(self.entityList)
        copyRelationList = deepcopy(self.relationList)
        #主要是打乱了的元组进行更新
        for tripletWithCorruptedTriplet in Tbatch:
            headEntityVector = copyEntityList[tripletWithCorruptedTriplet[0][0]]#tripletWithCorruptedTriplet是原三元组和打碎的三元组的元组tuple
            tailEntityVector = copyEntityList[tripletWithCorruptedTriplet[0][1]]
            relationVector = copyRelationList[tripletWithCorruptedTriplet[0][2]]
            headEntityVectorWithCorruptedTriplet = copyEntityList[tripletWithCorruptedTriplet[1][0]]
            tailEntityVectorWithCorruptedTriplet = copyEntityList[tripletWithCorruptedTriplet[1][1]]
            
            headEntityVectorBeforeBatch = self.entityList[tripletWithCorruptedTriplet[0][0]]#tripletWithCorruptedTriplet是原三元组和打碎的三元组的元组tuple
            tailEntityVectorBeforeBatch = self.entityList[tripletWithCorruptedTriplet[0][1]]
            relationVectorBeforeBatch = self.relationList[tripletWithCorruptedTriplet[0][2]]
            headEntityVectorWithCorruptedTripletBeforeBatch = self.entityList[tripletWithCorruptedTriplet[1][0]]
            tailEntityVectorWithCorruptedTripletBeforeBatch = self.entityList[tripletWithCorruptedTriplet[1][1]]
            
            if self.L1: #如果是L1，就用distanceL1的方式来衡量距离结果，否则用distanceL2来计算
                distTriplet = distanceL1(headEntityVectorBeforeBatch, tailEntityVectorBeforeBatch, relationVectorBeforeBatch) #调用distanceL1计算损失函数的值
                distCorruptedTriplet = distanceL1(headEntityVectorWithCorruptedTripletBeforeBatch, tailEntityVectorWithCorruptedTripletBeforeBatch ,  relationVectorBeforeBatch)
            else:
                distTriplet = distanceL2(headEntityVectorBeforeBatch, tailEntityVectorBeforeBatch, relationVectorBeforeBatch) #调用distanceL2计算损失函数的值
                distCorruptedTriplet = distanceL2(headEntityVectorWithCorruptedTripletBeforeBatch, tailEntityVectorWithCorruptedTripletBeforeBatch ,  relationVectorBeforeBatch)
            eg = self.margin + distTriplet - distCorruptedTriplet
            if eg > 0: #[function]+ 是一个取正值的函数
                self.loss += eg
                if self.L1:
                    tempPositive = 2 * self.learingRate * (tailEntityVectorBeforeBatch - headEntityVectorBeforeBatch - relationVectorBeforeBatch)
                    tempNegtative = 2 * self.learingRate * (tailEntityVectorWithCorruptedTripletBeforeBatch - headEntityVectorWithCorruptedTripletBeforeBatch - relationVectorBeforeBatch)
                    tempPositiveL1 = []
                    tempNegtativeL1 = []
                    for i in range(self.dim):#不知道有没有pythonic的写法（比如列表推倒或者numpy的函数）
                        if tempPositive[i] >= 0:
                            tempPositiveL1.append(1)
                        else:
                            tempPositiveL1.append(-1)
                        if tempNegtative[i] >= 0:
                            tempNegtativeL1.append(1)
                        else:
                            tempNegtativeL1.append(-1)
                    tempPositive = array(tempPositiveL1)  
                    tempNegtative = array(tempNegtativeL1)

                else:
                    tempPositive = 2 * self.learingRate * (tailEntityVectorBeforeBatch - headEntityVectorBeforeBatch - relationVectorBeforeBatch)
                    tempNegtative = 2 * self.learingRate * (tailEntityVectorWithCorruptedTripletBeforeBatch - headEntityVectorWithCorruptedTripletBeforeBatch - relationVectorBeforeBatch)
    
                headEntityVector = headEntityVector + tempPositive
                tailEntityVector = tailEntityVector - tempPositive
                relationVector = relationVector + tempPositive - tempNegtative
                headEntityVectorWithCorruptedTriplet = headEntityVectorWithCorruptedTriplet - tempNegtative
                tailEntityVectorWithCorruptedTriplet = tailEntityVectorWithCorruptedTriplet + tempNegtative

                #只归一化这几个刚更新的向量，而不是按原论文那些一口气全更新了
                copyEntityList[tripletWithCorruptedTriplet[0][0]] = norm(headEntityVector)
                copyEntityList[tripletWithCorruptedTriplet[0][1]] = norm(tailEntityVector)
                copyRelationList[tripletWithCorruptedTriplet[0][2]] = norm(relationVector)
                copyEntityList[tripletWithCorruptedTriplet[1][0]] = norm(headEntityVectorWithCorruptedTriplet)
                copyEntityList[tripletWithCorruptedTriplet[1][1]] = norm(tailEntityVectorWithCorruptedTriplet)
                
        self.entityList = copyEntityList
        self.relationList = copyRelationList
    
    #将结果写入到EntilyVector
    def writeEntilyVector(self, dir):
        print("写入实体")
        entityVectorFile = open(dir, 'w', encoding="gbk")
        for entity in self.entityList.keys():
            entityVectorFile.write(entity+"\t")
            entityVectorFile.write(str(self.entityList[entity].tolist()))
            entityVectorFile.write("\n")
        entityVectorFile.close()

    #将结果写入到RelationVector
    def writeRelationVector(self, dir):
        print("写入关系")
        relationVectorFile = open(dir, 'w', encoding="gbk")
        for relation in self.relationList.keys():
            relationVectorFile.write(relation + "\t")
            relationVectorFile.write(str(self.relationList[relation].tolist()))
            relationVectorFile.write("\n")
        relationVectorFile.close()

def init(dim):
    return uniform(-6/(dim**0.5), 6/(dim**0.5)) #以dim=10，来生成在这样一个范围的随机数

#这个即可看成TransE的损失函数，使存在关系的距离更小，不存在关系的距离更大,使用了fabs绝对值
def distanceL1(h, t ,r):
    s = h + r - t
    sum = fabs(s).sum()
    return sum

#这个即可看成TransE的损失函数，使存在关系的距离更小，不存在关系的距离更大，使用了平方值来衡量
def distanceL2(h, t, r):
    s = h + r - t
    sum = (s*s).sum()
    return sum
 
def norm(list):
    '''
    归一化
    :param 向量
    :return: 向量的平方和的开方后的向量
    '''
    var = linalg.norm(list)
    i = 0
    while i < len(list):
        list[i] = list[i]/var
        i += 1
    return array(list)

#从dir给的文件路径中获取其第一列信息
def openDetailsAndId(dir,sp="\t"):
    idNum = 0
    list = []
    with open(dir,"r",encoding="utf-8-sig") as file:
        lines = file.readlines()
        for line in lines:
            DetailsAndId = line.strip().split(sp)
            list.append(DetailsAndId[0]) #只取前面的非id表示的信息
            idNum += 1
    return idNum, list

#获取train文件中的信息并将结果保存为元组，存到列表
def openTrain(dir,sp="\t"):
    num = 0
    list = [] #list保存每一行的元组结果
    with open(dir,"r",encoding="utf-8-sig") as file:
        lines = file.readlines()
        for line in lines:
            triple = line.strip().split(sp)
            if(len(triple)<3):
                continue
            list.append(tuple(triple)) #将分割的关系列表转化为元组
            num += 1
    return num, list

def main(filename):
    dirEntity = "static/TransE_shuju/"+filename+"_entity2id.txt"
    entityIdNum, entityList = openDetailsAndId(dirEntity) #将读取的实体结果保存到entityList
    dirRelation = "static/TransE_shuju/"+filename+"_relation2id.txt"
    relationIdNum, relationList = openDetailsAndId(dirRelation) #将读取的关系结果保存到entityList
    dirTrain = "static/TransE_shuju/"+filename+"_train.txt"
    tripleNum, tripleList = openTrain(dirTrain) #tripleList就是train.txt每一行转化为元组并保存在list后的结果
    print("打开TransE")
    transE = TransE(entityList,relationList,tripleList, margin=1, dim = 100) #用参数对TransE进行初始化
    print("TranE初始化")
    transE.initialize() #对实体向量和关系向量进行初始化
    transE.transE(5000, filename) #迭代5000轮
    path1 = "static/TransE_shuju/"+filename+"_relationVector.txt"
    transE.writeRelationVector(path1) #将关系向量的训练向量结果保存到relationVector.txt
    path2 = "static/TransE_shuju/"+filename+"_entityVector.txt"
    transE.writeEntilyVector(path2) #将实体向量的训练向量结果保存到relationVector.txt