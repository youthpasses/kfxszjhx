#coding: utf-8
from bs4 import BeautifulSoup
import utils
import urllib.request
import os
import re
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import codecs

def getHTMLWithURL(url):
    try:
        response = urllib.request.urlopen(url, timeout=5)
        return response.read()
    except:
        return ''

def getSearchpageHTMLWithUseridAndURL(userid, url):
    filepath = os.path.join(utils.getDirSearchpage(), 'searchpage_' + userid + '.txt')
    if not os.path.exists(filepath):
        print('get sphtml from %s' % url)
        html = getHTMLWithURL(url)
        f = open(filepath, 'w')
        f.write(html)
        f.close()
        return html
    print('get sphtml from %s' % filepath)
    html = '\n'.join(open(filepath, 'r').readlines())
    html = html.strip()
    if html == '':
        print('get sphtml from %s' % url)
        html = getHTMLWithURL(url)
        f = open(filepath, 'w')
        f.write(html)
        f.close()
        return html
    return html


def getHomepageHTMLWithUseridAndURLAndHpidx(userid, url, hpidx):
    filepath = os.path.join(utils.getDirHomepage(), 'homepage_' + userid + '_' + str(hpidx) +'.txt')
    if not os.path.exists(filepath):
        print('get homepage html from', url)
        html = getHTMLWithURL(url)
        f = open(filepath, 'w')
        f.write(html)
        f.close()
        return html
    html = '\n'.join(open(filepath, 'r').readlines())
    print('get homepage html from native')
    return html

def test():
    id = '54096c04dabfae8faa68e3da'
    search_results_page = 'http://166.111.7.106:8081/54096c04dabfae8faa68e3da.html'
    sphtml = getSearchpageHTMLWithUseridAndURL(id, search_results_page)
    # print 'sphtml:', sphtml
    # soup = BeautifulSoup(sphtml, "html5lib")
    # srgs = soup.find(attrs={'class', 'srg'})
    soup = BeautifulSoup(sphtml, 'html.parser')
    srgs = soup.find_all("h3", class_="r")[:2]
    if srgs:
        print('srgs:', len(srgs), srgs)
        # for i, srg in enumerate(srgs):
        #     # print str(x) + '/' + str(length), ' ==> ', i
        #     # fea = np.array(getFeatureWithSrg(id, srg, i, name, org), dtype=np.str)
        #     url = getUrlFromSrg(srg)
        #     getHomepageHTMLWithUseridAndURLAndHpidx(id, url, i)
    else:
        print('no srgs %s' % id)


def getPicFromHtml(html, name):
    # url中是否有名字
    # alt中是否有名字
    # url、alt中是否有logo, banner, upper, naviga
    # url中是否有profile
    # url后缀是否为svg
    imgs = re.findall('<img.*?>', html)
    name = name.lower().split(' ')

    for img in imgs:
        print('1', img)
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
        print(2, img)
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
        print(3, img)
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

def getPicWithUser(uid=None):
    name = 'Timothy L. Bailey'
    hpurl = 'https://med.unr.edu/directory/timothy-bailey?v=exp'
    html = getHTMLWithURL(hpurl).decode('utf-8')
    pic = getPicFromHtml(html, name)
    if pic != '' and pic[:4] != 'http':
        pic = '/'.join(hpurl.split('/')[:3]) + '/' + pic
    return pic


mailpattern = re.compile('[^\._:>\\-][\w\.-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+')
def getEmailWithUser(uid=None):
    # matilto
    # @ 正则匹配
    # 没有@，找 AT/at，结合email
    hpurl = 'https://www.researchgate.net/profile/Laurie_Stowe'
    html = getHTMLWithURL(hpurl).decode('utf8')
    # 判断 mailto
    print('mailto')
    if re.search('mailto:(.*?)"', html) != None:
        mailto = re.search('mailto:(.*?)"', html).group(1)
        if mailto != '':
            return mailto
    # 正则匹配
    print('re @')
    emails = mailpattern.findall(html)   #获取e-mail的link
    if emails != []:
        return emails[0]
    # 没有@，匹配 email
    print('re email')
    html = re.sub('<(.*?)>', '', html)
    for line in html.split('\n'):
        line = line.strip()
        if len(line) < 50:
            if 'email' in line or 'Email' in line or 'EMAIL' in line:
                print(line)
                line = re.sub('email|EMAIL|Email|:|"', '', line)
                return line
    # 没有email，匹配 at, AT, dot, DOT
    print('re at')
    for line in html.split('\n'):
        line = line.strip()
        if ('at' in line or 'AT' in line) and ('dot' in line or 'DOT' in line) and len(line) < 40:
            return line
    print('last')
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


if __name__ == '__main__':
    html = getHTMLWithURL('')
    org = 'Institute for Molecular Bioscience, The University of Queensland'
    print(getEmailWithUser())
    # a = [1,2,3,4,5]
    # for x in range(4, -1, -1):
    #     if a[x] % 2 == 0:
    #         del a[x]
    # print(a)