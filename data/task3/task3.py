# coding: utf-8

import os
import utils
from tqdm import tqdm
import numpy as np

# 所有paper的name id
# pname_pid = {}
# 获取会议信息，{'会议名': {'hid': 会议id, 'pcount': 论文数量}...}
hname_hid_pcount = {}
# 学者的所有paper的pid，{0:[3,5,8], 1:[1,9,10]...}
uid_pids = {}
# 作者name与id映射
name_uid = {}

# pid_info, {pid: {'pname': '', 'uids':{0,1,2..}, 'hid': 1, 'year': 2008, 'cit':29}}
pid_info = {}

# 训练数据
uid_cit_train = {}


# 获取会议信息，{'会议名': {'hid': 会议id, 'pcount': 论文数量}...}
def get_hname_hid_pcount():
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
                s = '%s,%d,%d\n' % (hname, hid_pcount['hid'], hid_pcount['pcount'])
                f.write(s)
            f.close()
            print 'file %s saved success.' % path
        else:
            for line in open(path, 'r'):
                line = line.strip().split(',')  #第一个是会议名称，第二个是会议id，第三个是投稿数量
                hid_pcount = {}
                hid_pcount['hid'] = int(line[1])
                hid_pcount['pcount'] = int(line[2])
                hname_hid_pcount[line[0]] = hid_pcount
    return hname_hid_pcount

# name_uid 必须从papers中获取
def get_name_uid():
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
            for line in open(utils.getPathNameuid(), 'r'):
                line = line.strip().split(',')
                name_uid[line[0]] = int(line[1])
    return name_uid



# 学者的所有paper的pid，{0:[3,5,8], 1:[1,9,10]...}
# uid_pids = {}
# 作者name与id映射
# name_uid = {}

# pid_info, {pid: {'pname': '', 'uids':{0,1,2..}, 'hid': 1, 'year': 2008, 'cia':90, 'pids_cia': [10,78,63...]}}
# pid_info = {}


def init():
    hname_hid_pcount = get_hname_hid_pcount()
    name_uid = get_name_uid()
    one = []
    for ll in open(utils.getPathPapers(), 'r'):
        ll = ll.strip()
        if ll == '':
            pid = int(line[0][6:])
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
                        pids = uid_pids.get(uid, [])
                        pids.append(pid)
                        uid_pids[uid] = pids
                    info['uids'] = uids
                elif line[:2] == '#t':
                    # 发表年份
                    year = int(line[2:])
                    if (year >= 2013):
                        continue
                    info['year'] = int(line[2:])
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
        else:
            one.append(ll)
    f_uid_pids = open(utils.getPathUid_pids(), 'w')
    for uid in uid_pids.keys():
        pids = [str(pid) for pid in uid_pids[uid]]
        s = '%d:%s\n' % (uid, ','.join(pids))
        f_uid_pids.write(s)
    print 'file %s saved successed.' % utils.getPathUid_pids()
    f_pid_info = open(utils.getPathPid_info(), 'w')
    for pid in pid_info.keys():
        info = pid_info[pid]
        s = str(pid) + '\n'
        f_pid_info.write(s)
        s = ''
        for info_key in info.keys():
            if info_key == 'pname':
                s += 'pname:' + info[info_key] + ';'
            elif info_key == 'hid':
                s += 'hid:' + str(info[info_key]) + ';'
            elif info_key == 'year':
                s += 'year:' + str(info[info_key]) + ';'
            elif info_key == 'cia':
                s += 'cia:' + str(info[info_key]) + ';'
            elif info_key == 'uids':
                s += 'uids:' + ','.join([str(uid) for uid in info[info_key]]) + ';'
            elif info_key == 'pids_cia':
                s += 'pids_cia:' + ','.join([str(pid_cia) for pid_cia in info_key[info_key]]) + ';'
            s = s[:len(s)-1]
            s += '\n'
        f_pid_info.write(s)
    print 'file %s saved successed.' % utils.getPathPid_info()


# {pid: {'pname': '', 'uids':{0,1,2..}, 'hid': 1, 'year': 2008, 'cia':90, 'pids_cia': [10,78,63...]}}
def get_pid_info():



def get_uid_pids():
    if uid_pids == {}:
        if not os.path.exists(utils.getPathUid_pids()):
            init()
        else:
            for line in open(utils.getPathUid_pids(), 'w'):
                line = line.strip().split(':')
                pids = [int(pid) for pid in line[1].split(',')]
                uid_pids[int(line[0])] = pids
    return uid_pids



# 训练数据
# uid_cit_train = {}
def get_uid_cit_train():
    name_uid = get_name_uid()
    lines = open(utils.getPathTrainingData(3), 'r').readlines()
    del lines[0]
    for line in tqdm(lines):
        line = line.strip().split(',')
        uid_cit_train[name_uid[line[0]]] = int(line[1])
    return uid_cit_train



def extractFeas():
    # 要提取的特征：
    # 0 学者发表论文数；
    # 1 所有合作者人数；
    # 2 学者所有论文总引用数；
    # 3-12 从1930年起学者每10年发表论文的总数；
    # 13-22 从1930年起学者每十年发表论文的引用数；
    # 23 学者发表论文的会议期刊数；
    # 24 学者发表论文所有期刊的所有论文总数；


    uid_pids = get_uid_pids()
    hname_hid_pcount = get_hname_hid_pcount()
    uid_cit_train = get_uid_cit_train()

    X = []
    for uid in uid_cit_train.keys():
        feas = np.zeros((25,))
        # 0 学者发表论文数；
        feas[0] = len(uid_pids[uid])
        # 1 所有合作者人数；
