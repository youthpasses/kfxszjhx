# coding: utf-8

import os
import re
import utils
import urllib.request
from bs4 import BeautifulSoup
# from tqdm import tqdm
import numpy as np
import random
from sklearn import tree
from sklearn.linear_model import LogisticRegression
from sklearn import svm
import pandas as pd
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import codecs
from tqdm import tqdm
import sys

# reload(sys)
# sys.setdefaultencoding('utf8')

def getHTMLWithURL(url):
    if 'google' in url or 'facebook' in url or 'youtube' in url or 'twitter' in url or url[-3:] =='pdf':
        return ''
    try:
        response = urllib.request.urlopen(url, timeout=3)
        return response.read().decode('utf-8')
    except:
        return ''

def getSearchpageHTMLWithUseridAndURL(userid, url):
    print('searchpage: %s ==> %s' % (userid, url))
    filepath = os.path.join(utils.getDirSearchpage(), 'searchpage_' + userid + '.txt')
    if not os.path.exists(filepath):
        # print 'get searchpage from %s' % url
        html = getHTMLWithURL(url)
        f = open(filepath, 'w', encoding='utf-8')
        f.write(html)
        f.close()
        return html
    # print 'get searchpage from native.'
    html = '\n'.join(open(filepath, 'r', encoding='utf8').readlines())
    html = html.strip()
    if html == '':
        html = getHTMLWithURL(url)
        print('html:', html)
        f = open(filepath, 'w', encoding='utf-8')
        f.write(html)
        f.close()
        return html
    return html

def getHomepageHTMLWithUseridAndURLAndHpidx(userid, url, hpidx):
    filepath = os.path.join(utils.getDirHomepage(), 'homepage_' + userid + '_' + str(hpidx) +'.txt')
    if not os.path.exists(filepath):
        print('get homepage html from', url)
        html = getHTMLWithURL(url)
        f = open(filepath, 'w', encoding='utf-8')
        f.write(html)
        f.close()
        return html
    html = '\n'.join(open(filepath, 'r').readlines())
    # print 'get homepage html from native'
    return html

def getHomepageIdx(html, homepage):
    soup = BeautifulSoup(html, "html.parser")
    srg = soup.find(attrs={'class', 'srg'})
    if srg:
        for i, x in enumerate(srg):
            href = x.find('a')['href'].strip()
            if href == homepage:
                return i
    return -1

def getHomepageWithSearchpageAndHpidx(uid, searchpage, hpidx):
    html = getSearchpageHTMLWithUseridAndURL(uid, searchpage)
    soup = BeautifulSoup(html, 'html.parser')
    try:
        srg = list(soup.find(attrs={'class', 'srg'}))[hpidx]
        return srg.find('a')['href'].strip()
    except:
        return ''


def getUserHomepageIndex():
    # print 'getUserHomepageIndex()'
    userid_idx = {}
    lines = open(utils.getPathHomepageIndex(), 'r').readlines()
    for x in range(1, 22, 2):
        idx = x / 2
        line = lines[x].strip().split(',')
        for userid in line:
            userid_idx[userid] = idx
    return userid_idx

def getUserlist(traindata=True):
    # print 'getUserlist()'
    filepath = utils.getPathTrainingData(1)
    if not traindata:
        filepath = utils.getPathTestFinal(1)
    if traindata:
        userid_hpidx = getUserHomepageIndex()
    userlist = []
    user = []
    for line in codecs.open(filepath, 'r', encoding='utf-8'):
        line = line.strip().lower()
        if line == '':
            user_dic = {}
            for item in user:
                item = item.split(':')
                user_dic[item[0][1:]] = ':'.join(item[1:])
            userlist.append(user_dic)
            user = []
        else:
            user.append(line)
    return userlist



def getUrlFromSrg(srg):
    href = srg.find('a')['href'].strip()
    return href

######################################################################################
# 特征提取：

#     在list中idx, one-hot
def getFeature_idx(idx):
    f = np.zeros((10,), np.float32)
    f[idx] = 1.0
    return f


#     标题中是否存在学者名字
def getFeature_title_name(srg, name):
    title = srg.a.string
    name = name.split(' ')
    try:
        if name[0] in title or name[-1] in title:
            return [1.0]
        else:
            return [0.0]
    except:
        return [0.0]


#     url中是否含有“edu”
def getFeature_url(url, name):
    f = np.zeros((3,), np.float32)
    try:
        if 'edu' in url:
            f[0] = 1.0
    except:
        pass
    name = name.split(' ')
    try:
        if name[0] in url or name[-1] in url:
            f[1] = 1.0
    except:
        pass
    try:
        if 'profile' in url:
            f[2] = 1.0
    except:
        pass
    return f

#     homepage 是否含有？
#         学者名字
#         学者所在组织org
#         "university"
#         “department”
#         "school"
#         "institute"
#         "college"
#         "professor"
#         "director"
#         "personal webpage"
#         "email"
#         "phone"
#         "office"
#         "home"
#         "fax"
#         "address"
#         "profile"
#         "research"
#         “research topic”
#         "Research Interest"
#         "activities"
#         "projects"
#         "publication"
#         "selected publication"
#         "award"
#         "honor"
#         "academic"
#         "gallery"
#         "news"
def getFeature_homepage(hphtml, name, org):
    f = np.zeros((31,), np.float32)
    # name
    if name in hphtml:
        f[0] = 1.0
    # org
    org = org.split(',')
    if org[0].strip() in hphtml:
        f[1] = 1.0
    if org[-1].strip() in hphtml:
        f[2] = 1.0
    # university
    if 'university' in hphtml:
        f[3] = 1.0
    #         “department”
    if 'department' in hphtml:
        f[4] = 1.0
    #         "school"
    if 'school' in hphtml:
        f[5] = 1.0
    #         "institute"
    if 'institute' in hphtml:
        f[6] = 1.0
    #         "college"
    if 'college' in hphtml:
        f[7] = 1.0
    #         "professor"
    if 'professor' in hphtml:
        f[8] = 1.0
    #         "director"
    if 'director' in hphtml:
        f[9] = 1.0
    #         "personal webpage"
    if 'personal webpage' in hphtml:
        f[10] = 1.0
    #         "email"
    if 'email' in hphtml:
        f[11] = 1.0
    #         "phone"
    if 'phone' in hphtml:
        f[12] = 1.0
    #         "office"
    if 'office' in hphtml:
        f[13] = 1.0
    #         "home"
    if 'home' in hphtml:
        f[14] = 1.0
    #         "fax"
    if 'fax' in hphtml:
        f[15] = 1.0
    #         "address"
    if 'address' in hphtml:
        f[16] = 1.0
    #         "profile"
    if 'profile' in hphtml:
        f[17] = 1.0
    #         "research"
    if 'research' in hphtml:
        f[18] = 1.0
    #         “research topic”
    if 'research topic' in hphtml:
        f[19] = 1.0
    #         "Research Interest"
    if 'research interest' in hphtml:
        f[20] = 1.0
    #         "activities"
    if 'activities' in hphtml:
        f[21] = 1.0
    #         "projects"
    if 'projects' in hphtml:
        f[22] = 1.0
    #         "publication"
    if 'publication' in hphtml:
        f[23] = 1.0
    #         "selected publication"
    if 'selected publication' in hphtml:
        f[24] = 1.0
    #         "award"
    if 'award' in hphtml:
        f[25] = 1.0
    #         "honor"
    if 'honor' in hphtml:
        f[26] = 1.0
    #         "academic"
    if 'academic' in hphtml:
        f[27] = 1.0
    #         "gallery"
    if 'gallery' in hphtml:
        f[28] = 1.0
    #         "news"
    if 'news' in hphtml:
        f[29] = 1.0
    if 'e-mail' in hphtml:
        f[30] = 1.0
    return f


def getFeatureWithSrg(userid, srg, hpidx, name, org):
    f1 = np.array(getFeature_idx(hpidx), dtype=np.float32)
    f2 = np.array(getFeature_title_name(srg, name), dtype=np.float32)
    url = getUrlFromSrg(srg)
    f3 = np.array(getFeature_url(url, name), dtype=np.float32)
    hphtml = getHomepageHTMLWithUseridAndURLAndHpidx(userid, url, hpidx)
    f4 = np.array(getFeature_homepage(hphtml, name, org), dtype=np.float32)
    # print f1, f2, f3, f4
    f1 = np.concatenate((f1, f2), 0)
    f1 = np.concatenate((f1, f3), 0)
    f1 = np.concatenate((f1, f4), 0)
    return f1

def getRandomIndex(hpidx):
    a = -1
    b = -1
    while a == -1 or a == hpidx or b == -1 or b == hpidx or a == b:
        if a == -1 or a == hpidx:
            a = random.randint(0, 9)
        else:
            b = random.randint(0, 9)
    return a, b



# 获取所有训练数据中user的真实的homepage页面，保存在文件夹data/task1/homepage_1中
def get_homepage_true():
    userlist = getUserlist(traindata=True)
    for user_dic in userlist:
        id = user_dic['id']
        homepage = user_dic['homepage']
        html = getHTMLWithURL(homepage)
        filepath = os.path.join(utils.getDirHomepage_true(), 'homepage_%s_1.txt' % id)
        f = open(filepath, 'w', encoding='utf-8')
        f.write(html)
        f.close()


# 对预测结果进行分析
# def analysis_prediction(labels, predictions):
#     # print 'labels: ', labels
#     # print 'predictions: ', predictions
#     cm = confusion_matrix(labels, predictions)
#     print cm
#     print 'classification report:\n'
#     print classification_report(labels, predictions)
#     print 'F1 micro averaging: %f' % f1_score(labels, predictions, average='micro')
#     print 'Roc: %f' % roc_auc_score(labels, predictions)







    # pred = clf.predict(X_test)
    # analysis_prediction(Y_test, pred)

    # print '\n===============SVM=================='
    # clf = svm.SVC()
    # clf = clf.fit(X_train, Y_train)
    # pred = clf.predict(X_test)
    # analysis_prediction(Y_test, pred)

def getPicFromHtml(html, name):
    # url中是否有名字
    # alt中是否有名字
    # url、alt中是否有logo, banner, upper, naviga
    # url中是否有profile
    # url后缀是否为svg
    imgs = re.findall('<img.*?>', html)
    name = name.lower().split(' ')

    for img in imgs:
        try:
            src = re.search('src="(.*?)"', img).group(1)
        except:
            src = ''
        try:
            alt = re.search('alt="(.*?)"', img).group(1)
        except:
            alt = ''
        for n in name:
            if n in src or n in alt:
                return src
    for img in imgs:
        try:
            src = re.search('src="(.*?)"', img).group(1)
        except:
            src = ''
        try:
            alt = re.search('alt="(.*?)"', img).group(1)
        except:
            alt = ''
        if 'profile' in src or 'profile' in alt:
            return src
    count = len(imgs)
    for x in range(count - 1, -1, -1):
        img = imgs[x]
        try:
            src = re.search('src="(.*?)"', img).group(1)
        except:
            src = ''
        try:
            alt = re.search('alt="(.*?)"', img).group(1)
        except:
            alt = ''
        if 'logo' in src.lower() or 'logo' in alt.lower() or 'footer' in src.lower() or 'footer' in alt.lower() or src[-3:] == 'svg':
            del imgs[x]
    try:
        if imgs[0]:
            try:
                src = re.search('src="(.*?)"', img[0]).group(1)
            except:
                src = ''
            return src
        else:
            return ''
    except:
        return ''

def getPicWithUser(uname, homepage, html):
    pic = getPicFromHtml(html, uname)
    if pic != '' and pic[:4] != 'http':
        pic = '/'.join(homepage.split('/')[:3]) + '/' + pic
    return pic

mailpattern = re.compile('[^\._:>\\-][\w\.-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+')
def getEmailWithUser(uid, homepage, hpidx, html):
    # matilto
    # @ 正则匹配
    # 没有@，找 AT/at，结合email
    # hpurl = 'http://www2.rockefeller.edu/research/faculty/labheads/MitchellFeigenbaum/'
    # 判断 mailto
    hpurl = 'https://www.researchgate.net/profile/Laurie_Stowe'
    html = getHTMLWithURL(hpurl)
    # 判断 mailto
    if re.search('mailto:(.*?)"', html) != None:
        mailto = re.search('mailto:(.*?)"', html).group(1)
        if mailto != '':
            return mailto
    # 正则匹配
    emails = mailpattern.findall(html)  # 获取e-mail的link
    if emails != []:
        return emails[0]
    # 没有@，匹配 email
    html = re.sub('<(.*?)>', '', html)
    for line in html.split('\n'):
        line = line.strip()
        if len(line) < 50:
            if 'email' in line or 'Email' in line or 'EMAIL' in line:
                print(line)
                line = re.sub('email|EMAIL|Email|:|"', '', line)
                return line
    # 没有email，匹配 at, AT, dot, DOT
    for line in html.split('\n'):
        line = line.strip()
        if ('at' in line or 'AT' in line) and ('dot' in line or 'DOT' in line) and len(line) < 40:
            return line
    for line in html.split('\n'):
        line = line.strip()
        if ('at' in line or 'AT' in line) and '.' in line and len(line) < 40:
            return line
    return ''


def extract(html_doc):

    soup = BeautifulSoup(html_doc, 'html.parser')
    # remove unused tags
    for tag in soup.find_all(['header', 'footer', 'script', 'iframe', 'style']):
        tag.decompose()
    # for u in soup.find()
    html_doc_text=""
    for string in soup.strings:
        raw_str = string
        # print(raw_str)
        cleaned_str = re.sub(r'\n|\\xa0|\\u3000|\\u0020|\\r\\n|\\r|\\n', '', str(raw_str))
        cleaned_str = re.sub(r'\u3000|\xa0|\u0020', ' ', str(cleaned_str))
        cleaned_str.strip()
        html_doc_text += raw_str.strip() + " "

    html_doc_text = re.sub('\s+', ' ', html_doc_text)
    return html_doc_text

title_vocas = codecs.open("title_dict.txt","r","utf-8").readlines()
title_vocas = [s.strip() for s in title_vocas]
# print(title_vocas)
title_dic = {}
for v in title_vocas:
    title_dic.setdefault(v.strip(),len(v.strip()))
sorted_lst = sorted(title_dic.items(), key=lambda item: item[1], reverse=True)
title_vocas = [s[0] for s in sorted_lst]
# print(title_vocas)

def get_title(html_doc):
    '''
    find more titles
    '''
    text = extract(html_doc)
    result = []
    for d in title_vocas:
        if text.find(d)>=0:
            result.append(d)
    if len(result)>3:
        result = result[:3]
    return result

location_vocas = codecs.open("location_dict.txt","r","utf-8").readlines()
location_vocas = [s[:-2] for s in location_vocas]
location_dic = {}
for v in location_vocas:
    location_dic.setdefault(v.strip(),len(v.strip()))
sorted_lst = sorted(location_dic.items(), key=lambda item: item[1], reverse=True)
location_vocas = [s[0] for s in sorted_lst]
# print(location_vocas)

def get_location(html_doc, institute):
    '''
    需要非常注意的是location是要去定位机构地址，
    宁可找不到也不能错误定位。
    因为通过主页浏览发现机构地点的显示并不是每一个都有的
    '''
    pre_window = 20
    last_window = 50
    text = extract(html_doc)
    institue_keywords = institute.split(",")
    if len(institue_keywords) == 0:
        return []
    if len(institue_keywords) > 1:
        institue_keywords.append(institute)
    # st_ed_pos_list = []
    ed = len(text)
    texts = []
    for key in institue_keywords:
        start = 0
        while True:
            index = text.find(key, start)
            # if search string not found, find() returns -1
            # search is complete, break out of the while loop
            if index == -1:
                break
            pos1 = index - pre_window
            pos2 = index + len(key) + last_window
            if index < pre_window:
                pos1 = 0
            if index + len(key) + last_window > ed:
                pos2 = ed
            texts.append(text[pos1:pos2+1])
            # move to next possible start position
            start = index + 1
    # for text in texts:
    #     print(text)
    for d in location_vocas:
        for t in texts:
            if t.find(d)>=0:
                return d
    return ""

name_vocas = codecs.open("names.txt","r","utf-8").readlines()
name_vocas = [s[:-1] for s in name_vocas]

def get_Gender(name):
    names = name.split(" ")
    # print(names)
    # print(name_vocas)
    for k in name_vocas:
        for s in names:
            s = s.lower()
            if s == k.lower():
                return "f"
    return "m"


# 获取训练数据的特征
def getTrainFeas():
    # print 'getTrainFeas()'
    userlist = getUserlist(traindata=True)
    f_fea = open(utils.getPathFeaTraining(1), 'w', encoding='utf-8')
    f_fea.write('userid,label,idx0,idx1,idx2,idx3,idx4,idx5,idx6,idx7,idx8,idx9,title_name,url_edu,url_name,url_profile,'
                'hp_name,hp_org1,hp_org2,hp_university,hp_department,hp_school,hp_institute,hp_college,hp_professor,hp_director,'
                'hp_personal_webpage,hp_email,hp_phone,hp_office,hp_home,hp_fax,hp_address,hp_profile,hp_research,hp_research_topic,'
                'hp_research_interest,hp_activities,hp_projects,hp_publication,hp_selected_publications,hp_award,hp_honor,'
                'hp_academic,hp_gallery,hp_news,hp_e_mail\n')

    length = len(userlist)
    for x, user_dic in enumerate(userlist):
        if user_dic['hpidx'] != 10:
            id = user_dic['id']
            name = user_dic['name']
            org = user_dic['org']
            search_results_page = user_dic['search_results_page']
            hpidx = user_dic['hpidx']
            homepage = user_dic['homepage']

            sphtml = getSearchpageHTMLWithUseridAndURL(id, search_results_page)
            # soup = BeautifulSoup(sphtml, "html5lib")
            idx_1 = hpidx
            idx_00, idx_01 = getRandomIndex(idx_1)
            # srgs = soup.find(attrs={'class', 'srg'})
            soup = BeautifulSoup(sphtml, 'html.parser')
            srgs = soup.find_all("h3", class_="r")[:2]
            # print str(x) + '/' + str(length), idx_1, idx_00, idx_01
            if srgs:
                for i, srg in enumerate(srgs):
                    label = 0
                    if i == idx_1 or i == idx_00 or i == idx_01:
                        # print str(x) + '/' + str(length), ' ==> ', i
                        if i == idx_1:
                            label = 1
                        fea = np.array(getFeatureWithSrg(id, srg, i, name, org), dtype=np.str)
                        s = str(id) + ',' + str(label) + ',' + ','.join(fea) + '\n'
                        f_fea.write(s)
            else:
                print('no srgs %s' % id)

    print('file', utils.getPathFeaTraining(), 'saved successed.')

# 获取vali中feas
def getValiFeas():
    # print 'getValiFeas()'
    userlist = getUserlist(traindata=False)
    f_fea = open(utils.getPathFeaVali(1), 'w')
    f_fea.write(
        'userid,idx,idx0,idx1,idx2,idx3,idx4,idx5,idx6,idx7,idx8,idx9,title_name,url_edu,url_name,url_profile,'
        'hp_name,hp_org1,hp_org2,hp_university,hp_department,hp_school,hp_institute,hp_college,hp_professor,hp_director,'
        'hp_personal_webpage,hp_email,hp_phone,hp_office,hp_home,hp_fax,hp_address,hp_profile,hp_research,hp_research_topic,'
        'hp_research_interest,hp_activities,hp_projects,hp_publication,hp_selected_publications,hp_award,hp_honor,'
        'hp_academic,hp_gallery,hp_news,hp_e_mail\n')

    length = len(userlist)
    for x, user_dic in enumerate(tqdm(userlist)):
        id = user_dic['id']
        name = user_dic['name']
        org = user_dic['org']
        search_results_page = user_dic['search_results_page']
        sphtml = getSearchpageHTMLWithUseridAndURL(id, search_results_page)
        # soup = BeautifulSoup(sphtml)
        # srgs = soup.find(attrs={'class', 'srg'})
        soup = BeautifulSoup(sphtml, 'html.parser')
        srgs = soup.find_all("h3", class_="r")[:2]
        # print str(x) + '/' + str(length), idx_1, idx_00, idx_01
        if srgs:
            for i, srg in enumerate(srgs):
                if i <=9:
                    # print str(x) + '/' + str(length), ' ==> ', i
                    fea = np.array(getFeatureWithSrg(id, srg, i, name, org), dtype=np.str)
                    s = '%s,%d,%s\n' % (id, i, ','.join(fea))
                    # print s
                    f_fea.write(s)
                else:
                    break
    print('file', utils.getPathFeaVali(1), 'saved successed.')


# def getUseInfoWithUseridAndHpidx(userid, hpurl, hpidx=0, ):
#     html = getHomepageHTMLWithUseridAndURLAndHpidx(userid, hpurl, hpidx)

def train():
    # 训练数据
    data_train = pd.read_csv(utils.getPathFeaTraining(1))
    values_train = data_train.values
    np.random.shuffle(values_train)
    X_train = values_train[:, 2:].astype(float)
    Y_train = values_train[:, 1].astype(int)

    # 需要预测数据
    data_vali = pd.read_csv(utils.getPathFeaVali(1))
    values_vali = data_vali.values
    X_vali = values_vali[:, 2:].astype(float)

    for i in range(len(X_vali)):
        for j in range(len(X_vali[i])):
            if np.isnan(X_vali[i][j]):
                print(i, j, 'nan')
                X_vali[i][j] = 0.0

    # X_vali = []
    # lines = open(utils.getPathFeaVali(1), 'r').readlines()
    # del lines[0]
    # for line in lines:
    #     line = line.strip().split(',')
    #     print len(line)
        # X_vali.append(line)
    # X_vali = np.array(X_vali, dtype=np.float32)

    # count = int(len(Y)*0.7)
    # X_train = X[:count]
    # X_test = X[count:]
    # Y_train = Y[:count]
    # Y_test = Y[count:]

    # print X_train.dtype, Y_train.dtype
    # print len(X_train), len(Y_train)
    # print X_train.shape, Y_train.shape

    # print '\n===============决策树==============='
    # clf = tree.DecisionTreeClassifier()
    # clf = clf.fit(X_train, Y_train)
    # pred = clf.predict(X_test)
    # analysis_prediction(Y_test, pred)

    print('\n===============逻辑回归==============')
    clf = LogisticRegression()
    clf = clf.fit(X_train, Y_train)
    Pred_vali = clf.predict_proba(X_vali)

    f_vali_proba = open(utils.getPathValiHpIdxProba(), 'w')
    f_vali_proba.write('id,idx,proba\n')
    for i, line in enumerate(values_vali):
        s = '%s,%s,%f\n' % (values_vali[i][0], values_vali[i][1], Pred_vali[i][1])
        f_vali_proba.write(s)
    print('预测结果proba已保存本地, %s' % utils.getPathValiHpIdxProba())

    # 根据每个user的10个url的proba确定homepage
    f_vali_hpidx = open(utils.getPathValiHpPredIdx(), 'w')
    f_vali_hpidx.write('id,hpidx\n')
    probas = []
    lines = open(utils.getPathValiHpIdxProba(), 'r').readlines()
    del lines[0]
    for i, line in enumerate(lines):
        # print '\n'
        # print line
        line = line.strip().split(',')
        try:
            if line[1] == '1':
                probas.append(line[2])
                probas = np.array(probas, dtype=np.float32)
                f_vali_hpidx.write('%s,%d\n' % (line[0], np.argmax(probas)))
                probas = []
            else:
                probas.append(line[2])
        except:
            pass
    print('homepage预测结果保存本地，%s' % utils.getPathValiHpPredIdx())

def extractInfo(hpidxis0=True):
    userlist_vali = getUserlist(traindata=False)[:50]
    f_res_task1 = open(utils.getPathRes(1), 'w')
    f_res_task1.write('expert_id\thomepage_url\tgender\tposition\tperson_photo\temail\tlocation\n')
    if not hpidxis0:
        uid_hpidx_lines = open(utils.getPathValiHpPredIdx(), 'r').readlines()
        del uid_hpidx_lines[0]
        for i, line in enumerate(uid_hpidx_lines):
            user_dic = userlist_vali[i]
            user_dic['hpidx'] = int(line.strip().split(',')[1])
            user_dic['homepage'] = getHomepageWithSearchpageAndHpidx(user_dic['id'], user_dic['search_results_page'],
                                                                     user_dic['hpidx'])
            html = getHomepageHTMLWithUseridAndURLAndHpidx(user_dic['id'], user_dic['homepage'], user_dic['hpidx'])
            user_dic['pic'] = getPicWithUser(user_dic['name'], user_dic['homepage'], html)
            user_dic['email'] = getEmailWithUser(user_dic['id'], user_dic['homepage'], user_dic['hpidx'], html)
            user_dic['gender'] = get_Gender(user_dic['name'])
            user_dic['position'] = (';'.join(get_title(html)))
            user_dic['location'] = get_location(html, user_dic['org'])
            s = '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
            user_dic['id'], user_dic['homepage'], user_dic['gender'], user_dic['position'], user_dic['pic'],
            user_dic['email'], user_dic['location'])
            f_res_task1.write(s)
    else:
        for user_dic in tqdm(userlist_vali):
            user_dic['hpidx'] = 0
            user_dic['homepage'] = getHomepageWithSearchpageAndHpidx(user_dic['id'], user_dic['search_results_page'],
                                                                     user_dic['hpidx'])
            html = getHomepageHTMLWithUseridAndURLAndHpidx(user_dic['id'], user_dic['homepage'], user_dic['hpidx'])
            # html = html.decode('utf-8')
            user_dic['pic'] = getPicWithUser(user_dic['name'], user_dic['homepage'], html)
            user_dic['email'] = getEmailWithUser(user_dic['id'], user_dic['homepage'], user_dic['hpidx'], html)
            user_dic['gender'] = get_Gender(user_dic['name'])
            positon = ';'.join(get_title(html))
            positon = re.sub('\n|\r', '', positon)
            user_dic['position'] = positon
            user_dic['location'] = get_location(html, user_dic['org'])
            s = '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
                user_dic['id'], user_dic['homepage'], user_dic['gender'], user_dic['position'], user_dic['pic'],
                user_dic['email'], user_dic['location'])
            f_res_task1.write(s)
    print('file %s saved successed.' % utils.getPathRes(1))


def add():
    f = open(utils.getPathRes(1), 'wb+')
    userlist_vali = getUserlist(traindata=False)
    count = len(f.readlines()) - 1
    for i, user_dic in enumerate(userlist_vali):
        if i + 1 > count:
            s = '%s\t\t\t\t\t\t\n' % user_dic['id']
            f.write(s.encode('utf8'))
    f.close()
    print('add finished.')


if __name__ == '__main__':
    # getValiFeas()
    # train()
    extractInfo(hpidxis0=True)
    # html = getHTMLWithURL('http://166.111.7.106:8081/53f43a7edabfaec09f1a3e5a.html')
    # soup = BeautifulSoup(html, 'html5lib')
    # srg = list(soup.find(attrs={'class', 'srg'}))
    # print srg[0].find('a')['href'].strip()
    # add()









#####################################################
# 本题的关键在于如何找到学者正确的个人主页。
#
# 特征提取：
#     在list中idx, one-hot
#     标题中是否存在学者名字
#     url中是否含有“edu”
#     url中是否含有学者名字
#     url中是否含有“profile”
#     homepage 是否含有？
#         学者名字
#         学者所在组织org
#         "university"
#         “department”
#         "school"
#         "institute"
#         "professor"
#         "personal webpage"
#         "email"
#         "phone"
#         "office"
#         "home"
#         "fax"
#         "address"
#         "profile"
#         "research"
#         “research topic”
#         "Research Interest"
#         "publication"
#         "selected publication"
#         "award"
#         "honor"
#         "academic"
#         "gallery"
#         "news"



