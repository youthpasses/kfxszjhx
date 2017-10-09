# coding: utf-8

import os
import utils
import numpy as np


# 两个作者合作次数, {'0_1': 2, '2_10':1, '1_3':2...}
coauthor_count = {}
# 作者的合作者, {0:[1,4,6], 1:[0,2,3,9,10], 2:[1,5,9,10,]...}
coauthor_list = {}
# 作者标签, {0:[1,20,21], 1:[3,1,34]...}
uid_tags = {}
# 作者name与id映射
name_uid = {}
# 标签id
tag_tid = {}
# 保存uid_vaild
uid_vali = []


# 作者name与id映射
# def get_name_uid():
#     if name_uid == {}:
#         if not os.path.exists(utils.getPathNameuid()):
#             k = 0
#             f_name_uid = open(utils.getPathNameuid(), 'w')
#             for i, line in enumerate(open(utils.getPathTrainingData(2), 'r').readlines()):
#                 if i % 3 == 0:
#                     name = line.strip()
#                     name_uid[name] = k
#                     f_name_uid.write('%s,%d\n' % (name, k))
#                     k += 1
#             for i, line in enumerate(open(utils.getPathValidationData(2), 'r').readlines()):
#                 name = line.strip()
#                 if name != '':
#                     name_uid[name] = k
#                     f_name_uid.write('%s,%d\n' % (name, k))
#                     k += 1
#             f_name_uid.close()
#         else:
#             for line in open(utils.getPathNameuid(), 'r'):
#                 line = line.strip().split(',')
#                 name_uid[line[0]] = int(line[1])
#     return name_uid





# name_uid 必须从papers中获取
def get_name_uid():
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
            for line in open(utils.getPathNameuid(), 'r'):
                line = line.strip().split(',')
                name_uid[line[0]] = int(line[1])
    return name_uid


def get_uid_with_name(name):
    name_uid = get_name_uid()
    try:
        return name_uid[name]
    except:
        return -1


def get_taglist_with_uid(uid):
    uid_tags = get_uid_tags()
    try:
        return uid_tags[uid]
    except:
        return []

def init():
    # name_uid = get_name_uid()
    k = 0
    path_papers = utils.getPathPapers()
    for line in open(path_papers, 'r'):
        k += 1
        if line[:2] == '#@':
            line = line.strip()
            names = line[2:].split(',')
            names = [name.strip() for name in names]
            for i in xrange(0, len(names) - 1):
                uid1 = get_uid_with_name(names[i])
                if uid1 != -1:
                    for j in xrange(i+1, len(names)):
                        uid2 = get_uid_with_name(names[j])
                        if uid2 != -1:
                            v1 = coauthor_list.get(uid1, [])
                            if uid2 not in v1:
                                v1.append(uid2)
                            coauthor_list[uid1] = v1
                            v2 = coauthor_list.get(uid2, [])
                            if uid1 not in v2:
                                v2.append(uid1)
                            coauthor_list[uid2] = v2
                            key = str(min(uid1, uid2)) + '_' + str(max(uid1, uid2))
                            coauthor_count[key] = coauthor_count.get(key, 0) + 1
    # 保存coauthor_count
    path_coauthor_count = utils.getPathCoauthorCount()
    f_coauthor_count = open(path_coauthor_count, 'w')
    print 'coauthor_count len: ', len(coauthor_count.keys())
    for n1n2 in coauthor_count.keys():
        f_coauthor_count.write('%s,%d\n' % (n1n2, coauthor_count[n1n2]))
    print 'file %s saved success.' % path_coauthor_count
    # 保存coauthor_list
    path_coauthor_list = utils.getPathCoauthorlist()
    f_path_coauthor_list = open(path_coauthor_list, 'w')
    print 'coauthor_list len: ', len(coauthor_list.keys())
    for uid in coauthor_list.keys():
        value = np.array(coauthor_list[uid], dtype=str)
        f_path_coauthor_list.write('%d:%s\n' % (uid, ','.join(value)))
    print 'file %s saved success.' % path_coauthor_list


# 作者的合作者, {0:[1,4,6], 1:[0,2,3,9,10], 2:[1,5,9,10,]...}
# coauthor_list = {}
def get_coauthor_list():
    print '==> getCoauthor_list()'
    global coauthor_list
    if coauthor_list == {}:
        path_coauthor_list = utils.getPathCoauthorlist()
        if not os.path.exists(path_coauthor_list):
            init()
            return coauthor_list
        else:
            for line in open(path_coauthor_list, 'r'):
                line = line.strip().split(':')
                coauthor_list[int(line[0])] = np.array(line[1].split(','), dtype=int)
            return coauthor_list
    return coauthor_list

# 两个作者合作次数, {'0_1': 2, '2_10':1, '1_3':2...}
# coauthor_count = {}
def get_coauthor_count():
    print '==> get_coauthor_count()'
    last = []
    global coauthor_count
    if coauthor_count == {}:
        path_coauthor_count = utils.getPathCoauthorCount()
        if not os.path.exists(path_coauthor_count):
            init()
            return coauthor_count
        else:
            for line in open(path_coauthor_count, 'r'):
                line = line.strip().split(',')
                try:
                    coauthor_count[line[0]] = int(line[1])
                except:
                    print line
                    print ','.join(last)
                    break
                last = line
            return coauthor_count
    return coauthor_count


# 标签编号
def get_tag_tid():
    print '==>  get_tagid():'
    global tag_tid
    if tag_tid == {}:
        for i, line in enumerate(open(utils.getPathDataLabel(), 'r').readlines()):
            line = line.strip()
            tag_tid[line] = i
    return tag_tid

# 作者标签, {0:[1,20,21], 1:[3,1,34]...}
# uid_tags = {}
def get_uid_tags():
    print '==> get_uid_tags()'
    global name_uid
    global uid_tags
    name_uid = get_name_uid()
    tagid = get_tag_tid()
    if uid_tags == {}:
        path_training = utils.getPathTrainingData(2)
        temp = []
        for line in open(path_training, 'r'):
            line = line.strip()
            if line == '':
                uid = name_uid[temp[0]]
                tags = temp[1].split(',')
                tags = [tagid[x] for x in tags]
                uid_tags[uid] = tags
                temp = []
            else:
                temp.append(line)
    return uid_tags

def get_uid_vali():
    print '==> get_uid_vali()'
    global name_uid
    global uid_vali
    name_uid = get_name_uid()

    if uid_vali == []:
        path_vali = utils.getPathValidationData(2)
        for line in open(path_vali, 'r'):
            line = line.strip()
            if line != '':
                uid_vali.append(name_uid[line])
    return uid_vali


def print_uid_vali_tags(uid_vali_tags):
    for uid in uid_vali_tags.keys()[:10]:
        print uid, uid_vali_tags[uid]

def get_uid_name():
    global name_uid
    name_uid = get_name_uid()
    uid_name = {}
    for name in name_uid.keys():
        uid_name[name_uid[name]] = name
    return uid_name

def get_tid_tag():
    global tag_tid
    tag_tid = get_tag_tid()
    tid_tag = {}
    for tag in tag_tid.keys():
        tid_tag[tag_tid[tag]] = tag
    return tid_tag


def method1():
    global coauthor_count
    global coauthor_list
    global uid_tags
    global uid_vali
    i = 0
    uid_vali_tags = {}
    coauthor_list = get_coauthor_list()
    coauthor_count = get_coauthor_count()
    uid_tags = get_uid_tags()
    uid_vali = get_uid_vali()
    # 没有合作者的学者
    uid_vali_noco = []
    uid_vali_withco = []
    for uid in uid_vali:
        try:
            uid_co = coauthor_list[uid]
            uid_vali_withco.append(uid)
        except:
            uid_vali_noco.append(uid)
    print 'count of uid_vali_noco: %d' % len(uid_vali_noco)
    print 'uid_vali noco: ', uid_vali_noco
    print 'count of uid_vali_withco: %d' % len(uid_vali_withco)

    while(i < 15):
        print '===================step:%d========================' % i
        print_uid_vali_tags(uid_vali_tags)
        # 对有合作者的学者进行处理
        for uid in uid_vali_withco:
            # tags = uid_vali_tags.get(uid, {})
            tags = {}
            for uid_co in coauthor_list[uid]:
                co_count = coauthor_count[str(min(uid, uid_co)) + '_' + str(max(uid, uid_co))]
                if uid_co in uid_vali_withco:
                    # 合作者也在验证集中
                    tag_count_co = uid_vali_tags.get(uid_co, {})
                    if tag_count_co != {}:
                        tag_count_co = sorted(tag_count_co.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
                        for tag_co in tag_count_co[:5]:
                            tags[tag_co[0]] = tags.get(tag_co[0], 0) + co_count
                elif uid_co in uid_tags.keys():
                    # 合作者不在验证集中，合作者在训练数据集中，合作者有自己的tags
                    for tag_co in uid_tags[uid_co]:
                        tags[tag_co] = tags.get(tag_co, 0) + co_count
                else:
                    # print '%d的合作者%d不在训练集也不在验证集，合作者在paper中。' % (uid, uid_co)
                    pass
            uid_vali_tags[uid] = tags
        i += 1
    # 保存
    f_vali_tags = open(utils.getPathValiTags(), 'w')
    for uid in uid_vali_withco:
        tags = uid_vali_tags[uid]
        tags = sorted(tags.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        s = str(uid)
        for item in tags:
            s += ',%d:%d' % (item[0], item[1])
        s += '\n'
        f_vali_tags.write(s)
    f_vali_tags.close()
    print 'file %s saved success.' % utils.getPathValiTags()
    f_res_task2 = open(utils.getPathRes(2), 'w')
    uid_name = get_uid_name()
    tid_tag = get_tid_tag()
    for uid in uid_vali:
        s = uid_name[uid]
        try:
            tags = uid_vali_tags[uid]
            tags = sorted(tags.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
            for item in tags[:5]:
                s += '\t%s' % tid_tag[item[0]]
        except:
            pass
        s += '\n'
        f_res_task2.write(s)
    f_res_task2.close()
    print 'file %s saved success.' % utils.getPathRes(2)


# 没有合作者的学者id
def handle_uid_vali_noco():
    uid_vali_noco = [734851, 734997, 1577117, 1566017, 985158, 1068326, 424556, 620685, 345293, 981975]



# 有合作者，但合作者不在train data和 vali data中，只在papers中
def handle_uid_vali_inpapers():
    uid_vali_in_papers = []


if __name__ == '__main__':
    method1()
