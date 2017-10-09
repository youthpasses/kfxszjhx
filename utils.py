# coding: utf-8

import os

SPLIT_STR = '==*@#=='
SPLIT_STR2 = '==#@*=='

def getDirData():
    return './data'

def getDirTask(taskid=1):
    return os.path.join(getDirData(), 'task' + str(taskid))

def getPathTrainingData(taskid=1):
    if taskid == 3:
        return os.path.join(getDirTask(taskid), 'train.csv')
    else:
        return os.path.join(getDirTask(taskid), 'training.txt')

def getPathValidationData(taskid=1):
    if taskid == 3:
        return os.path.join(getDirTask(taskid), 'validation.csv')
    else:
        return os.path.join(getDirTask(taskid), 'validation.txt')

# 保存homepage的目录
def getDirHomepage():
    path = os.path.join(getDirTask(1), 'homepage')
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def getDirHomepage_true():
    path = os.path.join(getDirTask(1), 'homepage_1')
    if not os.path.exists(path):
        os.mkdir(path)
    return path

# 保存searchpage的目录
def getDirSearchpage():
    path = os.path.join(getDirTask(1), 'searchpage')
    if not os.path.exists(path):
        os.mkdir(path)
    return path

# 保存homepage index的文件路径
def getPathHomepageIndex():
    return os.path.join(getDirTask(1), 'homepage_idx.txt')

def getPathTask2labelsData():
    return os.path.join(getDirTask(2), 'labels.txt')

def getPathTask3papersData():
    return os.path.join(getDirTask(3), 'papers.txt')

# 训练数据特征
def getPathFeaTraining(taskid=1):
    return os.path.join(getDirTask(taskid), 'fea_training_%d.csv' % taskid)

# 测试数据特征
def getPathFeaVali(taskid=1):
    return os.path.join(getDirTask(taskid), 'fea_vali_%d.csv' % taskid)

# task1的homepage的每个url的的预测概率
def getPathValiHpIdxProba():
    return os.path.join(getDirTask(1), 'vali_hp_pred_proba.csv')

# task1的vali学者的homepage预测结果
def getPathValiHpPredIdx():
    return os.path.join(getDirTask(1), 'vali_hp_pred_idx.csv')

# 最终测试集
def getPathTestFinal(taskid=1):
    if taskid == 3:
        return os.path.join(getDirData(), 'test_final', 'task3_test_final.csv')
    elif taskid == 1 or taskid == 2:
        return os.path.join(getDirData(), 'test_final', 'task%d_test_final.txt' % taskid)
    return None

##################################################################################################
#   task2

def getPathDataLabel():
    return os.path.join(getDirTask(2), 'labels.txt')

# 作者姓名与id的映射
def getPathNameuid():
    return os.path.join(getDirTask(2), 'name_id.csv')

# 合作者计数
def getPathCoauthorCount():
    return os.path.join(getDirTask(2), 'coauthor_count.csv')
# 每个作者的合作者list
def getPathCoauthorlist():
    return os.path.join(getDirTask(2), 'coauthor_list.txt')


def getPathPapers():
    return os.path.join(getDirTask(3), 'papers.txt')

# 结果
def getPathValiTags():
    return os.path.join(getDirTask(2), 'vali_tag.txt')

def getPathRes(task=1, modelname=None):
    if modelname:
        return os.path.join(getDirData(), 'res_task%d_%s.txt' % (task, modelname))
    else:
        return os.path.join(getDirData(), 'res_task%d.txt' % task)


##################################################################################################
#   task3

# 会议期刊统计信息保存路径，文件的每一行是 会议名称,编号,论文次数统计
def getPathHuiyiStat():
    return os.path.join(getDirTask(3), 'huiyi_stat.csv')

def getPathUid_pids():
    return os.path.join(getDirTask(3), 'uid_pids.txt')

def getPathPid_info():
    return os.path.join(getDirTask(3), 'pid_info.txt')

# 模型保存模型
def getPath_model(taskid=1):
    return os.path.join(getDirTask(taskid), 'model_%d.mk' % taskid)

# xgboost的模型参数
def getPath_xgb_dump():
    return os.path.join(getDirTask(3), 'dump.raw.txt'), os.path.join(getDirTask(3), 'featmap.txt')

def getPathXtrain_p():
    return os.path.join(getDirTask(3), 'X_train.csv')

def getPathXtest_p():
    return os.path.join(getDirTask(3), 'X_test.csv')