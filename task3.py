# coding: utf-8

import os
import utils
from tqdm import tqdm
import numpy as np
import task2
import os
import pandas as pd
# import xgboost as xgb
from sklearn import linear_model
import pickle

# 所有paper的name id
# pname_pid = {}
# 获取会议信息，{'会议名': {'hid': 会议id, 'pcount': 论文数量}...}
hname_hid_pcount = {}

# 学者的所有paper的pid，{0:[3,5,8], 1:[1,9,10]...}
uid_pids = {}

# 作者name与id映射
name_uid = {}

# 作者的合作者, {0:[1,4,6], 1:[0,2,3,9,10], 2:[1,5,9,10,]...}
uid_couids = {}

# pid_info, {pid: {'pname': '', 'uids':{0,1,2..}, 'hid': 1, 'year': 2008, 'cia':90, 'pids_cia': [10,78,63...]}}
# pname: 论文题目
# uids: 论文作者
# hid: 会议、期刊id
# year: 论文发表时间
# cia: 论文被引用量
# pids_cia: 引用的其他论文id
pid_info = {}

# 期刊id与期刊name
hid_hname = {}

# 训练数据
uid_cit_train = {}

# 测试数据
uid_vali = []


# 获取会议信息，{'会议名': {'hid': 会议id, 'pcount': 论文数量}...}
def get_hname_hid_pcount():
    # print 'task3 ==> get_hname_hid_pcount()'
    global hname_hid_pcount
    if hname_hid_pcount == {}:
        path = utils.getPathHuiyiStat()
        if not os.path.exists(path):
            k = 0
            for line in open(utils.getPathPapers(), 'r'):
                line = line.strip()
                if line[:2] == '#c':
                    hname = line[2:]
                    try:
                        hid_pcount = hname_hid_pcount[hname]
                        hid_pcount['pcount'] += 1
                        hname_hid_pcount[hname] = hid_pcount
                    except:
                        hid_pcount = {}
                        hid_pcount['hid'] = k
                        hid_pcount['pcount'] = 1
                        k += 1
                        hname_hid_pcount[hname] = hid_pcount
            f = open(path, 'w')
            for hname in hname_hid_pcount.keys():
                hid_pcount = hname_hid_pcount[hname]
                s = '%s%s%d%s%d\n' % (hname, utils.SPLIT_STR, hid_pcount['hid'], utils.SPLIT_STR, hid_pcount['pcount'])
                f.write(s)
            f.close()
            print 'file %s saved success.' % path
        else:
            print '\tread data from %s' % path
            for line in open(path, 'r'):
                line = line.strip().split(utils.SPLIT_STR)  #第一个是会议名称，第二个是会议id，第三个是投稿数量
                hid_pcount = {}
                hid_pcount['hid'] = int(line[1])
                hid_pcount['pcount'] = int(line[2])
                hname_hid_pcount[line[0]] = hid_pcount
    return hname_hid_pcount


# name_uid 必须从papers中获取
def get_name_uid():
    print 'task3 ==> get_name_uid():'
    global name_uid
    if name_uid == {}:
        if not os.path.exists(utils.getPathNameuid()):
            f_name_uid = open(utils.getPathNameuid(), 'w')
            k = 0
            for line in open(utils.getPathPapers(), 'r'):
                if line[:2] == '#@':
                    line = line.strip()
                    names = line[2:].split(',')
                    names = [name.strip() for name in names]
                    for name in names:
                        uid = name_uid.get(name, -1)
                        if uid == -1:
                            uid = k
                            k += 1
                        name_uid[name] = uid
            # name_uid = sorted(name_uid.items(), lambda x, y: cmp(x[1], y[1]))
            for name in name_uid.keys():
                f_name_uid.write('%s,%d\n' % (name, name_uid[name]))
            f_name_uid.close()
        else:
            print '\tread data from %s' % utils.getPathNameuid()
            for line in open(utils.getPathNameuid(), 'r'):
                line = line.strip().split(',')
                name_uid[line[0]] = int(line[1])
    return name_uid


# 作者的合作者, {0:[1,4,6], 1:[0,2,3,9,10], 2:[1,5,9,10,]...}
# uid_couids = {}
def get_uid_couids():
    # print 'task3 ==> get_uid_couids()'
    global uid_couids
    if uid_couids == {}:
        path_coauthor_list = utils.getPathCoauthorlist()
        if not os.path.exists(path_coauthor_list):
            uid_couids = task2.get_coauthor_list()
            return uid_couids
        else:
            print '\tread data from %s' % path_coauthor_list
            for line in open(path_coauthor_list, 'r'):
                line = line.strip().split(':')
                uid_couids[int(line[0])] = np.array(line[1].split(','), dtype=int)
            return uid_couids
    return uid_couids



# 学者的所有paper的pid，{0:[3,5,8], 1:[1,9,10]...}
# uid_pids = {}
# 作者name与id映射
# name_uid = {}

# pid_info, {pid: {'pname': '', 'uids':{0,1,2..}, 'hid': 1, 'year': 2008, 'cia':90, 'pids_cia': [10,78,63...]}}
# pid_info = {}


def getYearValid(one=[]):
    for line in one:
        if line[:2] == '#t':
            year = int(line[2:])
            if (year <= 2013):
                return True
    # print one
    return False

def init():
    print 'task3 ==> init()'
    global hname_hid_pcount
    global name_uid
    global uid_pids
    global pid_info
    hname_hid_pcount = get_hname_hid_pcount()
    name_uid = get_name_uid()
    one = []
    print 'handle with %s...' % utils.getPathPapers()
    # k = 0
    for ll in open(utils.getPathPapers(), 'r'):
        # if k > 999:
        #     break
        # k += 1
        ll = ll.strip()
        if ll == '':
            if getYearValid(one=one):
                pid = int(one[0][6:])
                info = pid_info.get(pid, {})
                for x in xrange(1, len(one)):
                    line = one[x]
                    if line[:2] == '#*':
                        info['pname'] = line[2:]
                    elif line[:2] == '#@':
                        # 学者，多名学者以逗号分开
                        uids = []
                        for uname in line[2:].split(','):
                            uid = name_uid[uname]
                            uids.append(uid)
                            pids = uid_pids.get(uid, set([]))
                            pids.add(pid)
                            uid_pids[uid] = pids
                        info['uids'] = uids
                    elif line[:2] == '#t':
                        # 发表年份
                        year = int(line[2:])
                        info['year'] = year
                    elif line[:2] == '#c':
                        # 发表的会议、期刊
                        hname = line[2:]
                        info['hid'] = hname_hid_pcount[hname]['hid']
                    elif line[:2] == '#%':
                        # 包含多行，每一行代表一篇所引用论文的id
                        pids = info.get('pids_cia', [])
                        pid_cia = int(line[2:])
                        pids.append(pid_cia)
                        info['pids_cia'] = pids
                        info_cia = pid_info.get(pid_cia, {})
                        info_cia_cia = info_cia.get('cia', 0)
                        info_cia_cia += 1
                        info_cia['cia'] = info_cia_cia
                        pid_info[pid_cia] = info_cia
                pid_info[pid] = info
            one = []
        else:
            one.append(ll)
    f_uid_pids = open(utils.getPathUid_pids(), 'w')
    for uid in uid_pids.keys():
        pids = [str(pid) for pid in uid_pids[uid]]
        s = '%d:%s\n' % (uid, ','.join(pids))
        f_uid_pids.write(s)
    f_uid_pids.close()
    print 'file %s saved successed.' % utils.getPathUid_pids()
    f_pid_info = open(utils.getPathPid_info(), 'w')
    for pid in pid_info.keys():
        info = pid_info[pid]
        s = str(pid) + utils.SPLIT_STR
        for info_key in info.keys():
            if info_key == 'pname':
                s += 'pname:' + info[info_key] + utils.SPLIT_STR2
            elif info_key == 'hid':
                s += 'hid:' + str(info[info_key]) + utils.SPLIT_STR2
            elif info_key == 'year':
                s += 'year:' + str(info[info_key]) + utils.SPLIT_STR2
            elif info_key == 'cia':
                s += 'cia:' + str(info[info_key]) + utils.SPLIT_STR2
            elif info_key == 'uids':
                # print 'uids:', info[info_key]
                s += 'uids:' + ','.join([str(uid) for uid in info[info_key]]) + utils.SPLIT_STR2
            elif info_key == 'pids_cia':
                # print 'pids_cia:', inf
                s += 'pids_cia:' + ','.join([str(pid_cia) for pid_cia in info[info_key]]) + utils.SPLIT_STR2
        s = s[:len(s)-len(utils.SPLIT_STR2)]
        s += '\n'
        f_pid_info.write(s)
    f_pid_info.close()
    print 'file %s saved successed.' % utils.getPathPid_info()


# {pid: {'pname': '', 'uids':{0,1,2..}, 'hid': 1, 'year': 2008, 'cia':90, 'pids_cia': [10,78,63...]}}
def get_pid_info():
    # print 'task3 ==> get_pid_info()'
    global pid_info
    if pid_info == {}:
        if not os.path.exists(utils.getPathPid_info()):
            init()
        else:
            print '\tread data from %s' % utils.getPathPid_info()
            for line in open(utils.getPathPid_info(), 'r'):
                line = line.strip().split(utils.SPLIT_STR)
                pid = int(line[0])
                items = line[1].split(utils.SPLIT_STR2)
                info = {}
                for item in items:
                    item = item.split(':')
                    key = item[0]
                    values = item[1]
                    if key == 'pname':
                        info[key] = values
                    elif key == 'hid' or key == 'year' or key == 'cia':
                        info[key] = int(values)
                    elif key == 'uids' or key == 'pids_cia':
                        info[key] = [int(v) for v in values.split(',')]
                pid_info[pid] = info
    return pid_info


def get_uid_pids():
    # print 'task3 ==> get_uid_pids()'
    global uid_pids
    if uid_pids == {}:
        if not os.path.exists(utils.getPathUid_pids()):
            init()
        print '\tread data from %s' % utils.getPathUid_pids()
        for line in open(utils.getPathUid_pids(), 'r'):
            line = line.strip().split(':')
            pids = [int(pid) for pid in line[1].split(',')]
            uid_pids[int(line[0])] = pids
    return uid_pids

def get_hid_hname():
    # print 'task3 ==> get_hid_hname()'
    global hid_hname
    if hid_hname == {}:
        hname_hid_pcount = get_hname_hid_pcount()
        for hname in hname_hid_pcount.keys():
            values = hname_hid_pcount[hname]
            hid_hname[values['hid']] = hname
    return hid_hname

# 训练数据
# uid_cit_train = {}
def get_uid_cit_train():
    print 'task3 ==> get_uid_cit_train()'
    global name_uid
    global uid_cit_train
    name_uid = get_name_uid()
    lines = open(utils.getPathTrainingData(3), 'r').readlines()
    del lines[0]
    for line in tqdm(lines):
        line = line.strip().split(',')
        uid_cit_train[name_uid[line[0]]] = int(line[1])
    return uid_cit_train

# 预测数据
def get_uid_vali():
    global name_uid
    global uid_vali
    name_uid = get_name_uid()
    lines = open(utils.getPathValidationData(3), 'r').readlines()
    del lines[0]
    uid_vali = [int(name_uid[name.strip()]) for name in lines]
    return uid_vali


# 特征 2：获取某个学者的所有论文总引用数
def getFea2(uid):
    # print 'task3 ==> getFea2(uid)'
    global uid_pids
    global pid_info
    uid_pids = get_uid_pids()
    pid_info = get_pid_info()
    res = 0
    for pid in uid_pids.get(uid, []):
        res += pid_info[pid].get('cia', 0)
    return res

# 特征 3-10 学者从2013年往前每10年发表论文的总数；
# 特征 11-18 学者从2013年往前每10年发表论文的引用总数；
# 特征 19 学者发表论文的会议期刊数；
def getFea3_10_11_18_19(uid):
    # print 'task3 ==> getFea3_10_11_18_19(uid)'
    global uid_pids
    global pid_info
    uid_pids = get_uid_pids()
    pid_info = get_pid_info()
    # fea3_10_11_18_19 = np.zeros((17,), dtype=np.int8)
    fea = {}
    hids = set([])
    for pid in uid_pids.get(uid, []):
        info = pid_info.get(pid, {})
        hid = info.get('hid', '')
        if hid != '':
            hids.add(hid)
        if 'year' in info.keys():
            year = int(info['year'])
            cia = int(info.get('cia', 0))
            if year > 2003 and year <= 2013:
                fea[0] = fea.get(0, 0) + 1
                fea[8] = fea.get(8, 0) + cia
            elif year > 1993 and year <= 2003:
                fea[1] = fea.get(1, 0) + 1
                fea[9] = fea.get(9, 0) + cia
            elif year > 1983 and year <= 1993:
                fea[2] = fea.get(2, 0) + 1
                fea[10] = fea.get(10, 0) + cia
            elif year > 1973 and year <= 1983:
                fea[3] = fea.get(3, 0) + 1
                fea[11] = fea.get(11, 0) + cia
            elif year > 1963 and year <= 1973:
                fea[4] = fea.get(4, 0) + 1
                fea[12] = fea.get(12, 0) + cia
            elif year > 1953 and year <= 1963:
                fea[5] = fea.get(5, 0) + 1
                fea[13] = fea.get(13, 0) + cia
            elif year > 1943 and year <= 1953:
                fea[6] = fea.get(6, 0) + 1
                fea[14] = fea.get(14, 0) + cia
            elif year > 1933 and year <= 1943:
                fea[7] = fea.get(7, 0) + 1
                fea[15] = fea.get(15, 0) + cia
    # fea3_10_11_18_19[0] = fea.get(0, 0)
    # fea3_10_11_18_19[1] = fea.get(1, 0)
    # fea3_10_11_18_19[2] = fea.get(2, 0)
    # fea3_10_11_18_19[3] = fea.get(3, 0)
    # fea3_10_11_18_19[4] = fea.get(4, 0)
    # fea3_10_11_18_19[5] = fea.get(5, 0)
    # fea3_10_11_18_19[6] = fea.get(6, 0)
    # fea3_10_11_18_19[7] = fea.get(7, 0)
    # fea3_10_11_18_19[8] = fea.get(8, 0)
    # fea3_10_11_18_19[9] = fea.get(9, 0)
    # fea3_10_11_18_19[10] = fea.get(10, 0)
    # fea3_10_11_18_19[11] = fea.get(11, 0)
    # fea3_10_11_18_19[12] = fea.get(12, 0)
    # fea3_10_11_18_19[13] = fea.get(13, 0)
    # fea3_10_11_18_19[14] = fea.get(14, 0)
    # fea3_10_11_18_19[15] = fea.get(15, 0)
    # fea3_10_11_18_19[16] = len(hids)
    # print '==============================================='
    # print 'fun => fea3..', fea3_10_11_18_19
    return fea, len(hids)


# 特征 20 学者发表论文所有期刊的所有论文总数；
def getFea20(hids):
    # print 'task3 ==> getFea20(hids)'
    global hid_hname
    global hname_hid_pcount
    hid_hname = get_hid_hname()
    hname_hid_pcount = get_hname_hid_pcount()
    res = 0
    for hid in hids:
        hname = hid_hname[hid]
        res += hname_hid_pcount[hname]['pcount']
    return res


def extractFeas(uids=[]):

    # print 'task3 ==> extractFeas()'
    # 要提取的特征：
    # 0 学者发表论文数；
    # 1 所有合作者人数；
    # 2 学者所有论文总引用数；
    # 3-10 学者从2013年往前每10年发表论文的总数；
    # 11-18 学者从2013年往前每10年发表论文的引用总数；
    # 19 学者发表论文的会议期刊数；
    # 20 学者发表论文所有期刊的所有论文总数；
    global uid_pids
    global uid_cit_train
    global uid_couids
    uid_pids = get_uid_pids()
    uid_cit_train = get_uid_cit_train()
    uid_couids = get_uid_couids()

    feas = []
    for uid in uids:
        fea = np.zeros((21,))
        # 0 学者发表论文数；
        fea[0] = len(uid_pids.get(uid, []))
        # 1 学者合作者人数；
        fea[1] = len(uid_couids.get(uid, []))
        # 2 学者所有论文总引用数
        fea[2] = getFea2(uid)
        # 3-10 从1930年起学者每10年发表论文的总数；
        # 11-18 从1930年起学者每十年发表论文的引用数；
        # 19 学者发表论文的会议期刊数；
        # 20 学者发表论文所有期刊的所有论文总数；
        fea3_10_11_18_19, fea[20] = getFea3_10_11_18_19(uid)
        fea[3] = fea3_10_11_18_19.get(0, 0)
        fea[4] = fea3_10_11_18_19.get(1, 0)
        fea[5] = fea3_10_11_18_19.get(2, 0)
        fea[6] = fea3_10_11_18_19.get(3, 0)
        fea[7] = fea3_10_11_18_19.get(4, 0)
        fea[8] = fea3_10_11_18_19.get(5, 0)
        fea[9] = fea3_10_11_18_19.get(6, 0)
        fea[10] = fea3_10_11_18_19.get(7, 0)
        fea[11] = fea3_10_11_18_19.get(8, 0)
        fea[12] = fea3_10_11_18_19.get(9, 0)
        fea[13] = fea3_10_11_18_19.get(10, 0)
        fea[14] = fea3_10_11_18_19.get(11, 0)
        fea[16] = fea3_10_11_18_19.get(12, 0)
        fea[17] = fea3_10_11_18_19.get(13, 0)
        fea[18] = fea3_10_11_18_19.get(14, 0)
        fea[19] = fea3_10_11_18_19.get(15, 0)
        feas.append(fea)
    return feas


def getDataFeas(istraindata=True):
    if istraindata:
        if not os.path.exists(utils.getPathFeaTraining(3)):
            global uid_cit_train
            uid_cit_train = get_uid_cit_train()
            feas = extractFeas(uid_cit_train.keys())
            f_feas_train = open(utils.getPathFeaTraining(3), 'w')
            fnames = ['f%d' % x for x in xrange(21)]
            f_feas_train.write('uid,cit,%s\n' % ','.join(fnames))
            for i, uid in enumerate(uid_cit_train.keys()):
                s = '%s,%s,%s\n' % (str(uid), str(uid_cit_train[uid]), ','.join([str(x) for x in feas[i]]))
                f_feas_train.write(s)
            f_feas_train.close()
            print 'feas %s saved success.' % utils.getPathFeaTraining(3)

        print 'reading data from file %s' % utils.getPathFeaTraining(3)
        data = pd.read_csv(utils.getPathFeaTraining(3))
        values = data.values
        np.random.shuffle(values)
        X = values[:, 2:].astype(np.float32)
        x_p = open(utils.getPathXtrain_p(), 'r').readlines()
        x_p = [np.array(line.strip().split(','), dtype=np.float32) for line in x_p]
        X = np.concatenate((X, x_p), 1)
        Y = values[:, 1].astype(np.int16)
        return X, Y
    else:
        if not os.path.exists(utils.getPathFeaVali(3)):
            global uid_vali
            uid_vali = np.array(get_uid_vali())
            print 'uid_vali.shape', uid_vali.shape
            feas = np.array(extractFeas(uid_vali))
            print 'feas.shape', feas.shape
            f_feas_vali = open(utils.getPathFeaVali(3), 'w')
            fnames = ['f%d' % x for x in xrange(21)]
            f_feas_vali.write('uid,%s\n' % ','.join(fnames))
            for i, uid in enumerate(uid_vali):
                s = '%s,%s\n' % (str(uid), ','.join([str(x) for x in feas[i]]))
                f_feas_vali.write(s)
            f_feas_vali.close()
            print 'feas %s saved success.' % utils.getPathFeaVali(3)
        data = pd.read_csv(utils.getPathFeaVali(3))
        values = data.values
        np.random.shuffle(values)
        X = values[:, 1:].astype(np.float32)
        x_p = open(utils.getPathXtest_p(), 'r').readlines()
        x_p = [np.array(line.strip().split(','), dtype=np.float32) for line in x_p]
        X = np.concatenate((X, x_p), 1)
        return X


def lr(retrain=False):
    X_train, Y_train = getDataFeas(istraindata=True)
    count = int(len(X_train) * 0.7)
    X_vali = X_train[count:]
    Y_vali = Y_train[count:]
    X_train = X_train[:count]
    Y_train = Y_train[:count]
    # X_vali = getDataFeas(istraindata=False)
    print 'X_train:', X_train.shape, '; Y_train:', Y_train.shape
    print 'X_vali:', X_vali.shape
    # if (retrain) or ((not retrain) and (not os.path.exists(utils.getPath_model(3)))):
    lm = linear_model.LinearRegression()
    lm.fit(X_train, Y_train)
        # Y_pred = regr.predict(diabetes_X_test)
        # print '训练完成'
        # 保存模型
        # lm.save_model(utils.getPath_model(3))
        # bst.dump_model(utils.getPath_xgb_dump())
        # print '模型保存完成'

    # print '加载模型，开始预测'
    # lm = linear_model.LinearRegression()
    # lm.load_model(utils.getPath_model(3))
    Y_pred = lm.predict(X_vali)
    Y_pred = [v if v >=0 else 0 for v in Y_pred]
    print '预测完成'
    f_res = open(utils.getPathRes(3,modelname='lr'), 'w')
    f_res.write('authorname\tcitation\n')
    names = open(utils.getPathValidationData(3)).readlines()
    del names[0]
    for i, name in enumerate(names):
        s = '%s\t%d\n' % (name.strip(), Y_pred[i])
        f_res.write(s)
    f_res.close()
    print 'task3 %s 结果保存成功。' % utils.getPathRes(3, modelname='lr')
    pingce(Y_vali, Y_pred)


def xbg(retrain=False):
    X_train, Y_train = getDataFeas(istraindata=True)
    X_vali = getDataFeas(istraindata=False)
    print 'X_train:', X_train.shape, '; Y_train:', Y_train.shape
    print 'X_vali:', X_vali.shape
    if (retrain) or ((not retrain) and (not os.path.exists(utils.getPath_model(3)))):
        dtrain = xgb.DMatrix(X_train, label=Y_train)
        num_round = 800
        params = {}
        # 定义学习任务及相应的学习目标，可选的目标函数如下：
        #   “reg:linear” –线性回归。
        #   “reg:logistic” –逻辑回归。
        #   “binary:logistic” –二分类的逻辑回归问题，输出为概率。
        #   “binary:logitraw” –二分类的逻辑回归问题，输出的结果为wTx。
        #   “count:poisson” –计数问题的poisson回归，输出结果为poisson分布。
        #       在poisson回归中，max_delta_step的缺省值为0.7。(used to safeguard optimization)
        #   “multi:softmax” –让XGBoost采用softmax目标函数处理多分类问题，同时需要设置参数num_class（类别个数）
        #   “multi:softprob” –和softmax一样，但是输出的是ndata * nclass的向量，可以将该向量reshape成ndata行nclass列的矩阵。每行数据表示样本所属于每个类别的概率。
        # “rank:pairwise” –set XGBoost to do ranking task by minimizing the pairwise loss
        params['objective'] = 'reg:linear'
        # 缺省值为0.3。为了防止过拟合，更细过程中用到的收缩步长。在每次提升计算后，算法会直接获取新特征的权重。eta通过缩减特征的权重使提升计算过程更加保守。
        # 取值范围[0,1]，通常最后设置eta为0.01-0.2
        params['eta'] = 0.1
        # 数的最大深度，缺省值为6。取值范围[1, 正无穷大]，指树的最大深度，深度越大则对数据的拟合程度越高。
        # 通常取值为3-10
        params['max_depth'] = 4

        params['eval_metric'] = 'rmse'
        # default=0, 取0表示打印出运行时信息，取1表示以缄默方式运行，不打印运行时信息。
        params['silent'] = 0
        plst = list(params.items())
        bst = xgb.train(plst, dtrain, num_round)
        print '训练完成'
        # 保存模型
        bst.save_model(utils.getPath_model(3))
        # bst.dump_model(utils.getPath_xgb_dump())
        print '模型保存完成'

    print '加载模型，开始预测'
    bst = xgb.Booster()
    bst.load_model(utils.getPath_model(3))
    X_vali = xgb.DMatrix(X_vali)
    Y_pred = bst.predict(X_vali)
    print '预测完成'
    f_res = open(utils.getPathRes(3, modelname='xgb'), 'w')
    f_res.write('authorname\tcitation\n')
    names = open(utils.getPathValidationData(3)).readlines()
    del names[0]
    for i, name in enumerate(names):
        count = Y_pred[i]
        if count < 0:
            count = 0
        s = '%s\t%d\n' % (name.strip(), count)
        f_res.write(s)
    f_res.close()
    print 'task3 %s 结果保存成功。' % utils.getPathRes(3, modelname='xgb')

def pingce(y_true, y_pred):
    res = 0.0

    for i, y in enumerate(y_true):
        if y == 0 and y_pred[i] == 0:
            pass
        else:
            res += float(abs(y - y_pred[i])) / float(max(y, y_pred[i]))
    score = 1 - 1.0 / float(len(y_true)) * res
    print 'score: %f' % score


if __name__ == '__main__':
    lr(retrain=True)
    # train(retrain=False)