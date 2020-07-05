from numpy import *
import matplotlib.pyplot as plt
import pylab
import matplotlib
from matplotlib.font_manager import FontProperties
#%matplotlib inline
myfont = matplotlib.font_manager.FontProperties(fname='static/font/simsun.ttc')
plt.switch_backend('agg')

def loadData(str):
    fr = open(str,"r",encoding="gbk")
    sArr = [line.strip().split("\t") for line in fr.readlines()]
    datArr = [[float(s) for s in line[1][1:-1].split(", ")] for line in sArr]
    matA = mat(datArr)
    #print(matA.shape)
    nameArr = [line[0] for line in sArr]
    return matA, nameArr

def pca(inputM, k):
    covM = cov(inputM, rowvar=0)
    s, V = linalg.eig(covM)
    s = s.real
    V = V.real
    paixu = argsort(s)
    paixuk = paixu[:-(k+1):-1]
    kwei = V[:,paixuk]
    outputM = inputM * kwei
    chonggou = (outputM * kwei.T)
    return outputM,chonggou

def plotV(a, labels, filename):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    font = { 'fontname':'Tahoma', 'fontsize':8, 'verticalalignment': 'top', 'horizontalalignment':'center' }
    ax.scatter(a[:,0].tolist(), a[:,1].tolist(), marker = ' ')
    ax.set_xlim(-0.8,0.8)
    ax.set_ylim(-0.8,0.8)
    i = 0
    for label, x, y in zip(labels, a[:, 0], a[:, 1]):
        i += 1
        s = random.uniform(0,100)
        if i<80:
            if s > 3.1:
                continue
        else:
            if s > 6.7:
                continue
        ax.annotate(label, xy = (x, y), xytext = None, ha = 'right', va = 'bottom', **font, fontproperties=myfont)
        #ax.annotate(label, xy = (x, y), xytext = None, ha = 'right', va = 'bottom')
    plt.title('TransE pca2dim',fontproperties='SimHei')
    plt.xlabel('X')
    plt.ylabel('Y')
    transE_img = 'static/TransE_img/'+filename
    plt.savefig(transE_img, dpi = 2000, bbox_inches = 'tight' ,orientation = 'landscape', papertype = 'a0')
def main(filename):
    dirRelation = "static/TransE_shuju/"+filename+"_relationVector.txt"
    dirEntity = "static/TransE_shuju/"+filename+"_entityVector.txt"
    matEntity, nameEntity = loadData(dirEntity)
    matRelation, nameRelation = loadData(dirRelation)
    mat = row_stack((matEntity, matRelation))
    nameEntity.extend(nameRelation)
    k = 2
    a, b = pca(mat, k)
    plotV(a, nameEntity, filename)