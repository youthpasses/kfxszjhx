import utils
import os
import urllib.request
import threading
from bs4 import BeautifulSoup

def getUserlist():
    # print 'getUserlist()'
    filepath = utils.getPathTestFinal(1)
    userlist = []
    user = []
    for line in open(filepath, 'r', encoding='utf-8'):
        line = line.strip().lower()
        if line == '':
            user_dic = {}
            for item in user:
                item = item.split(':')
                user_dic[item[0][1:]] = ':'.join(item[1:]).strip()
            userlist.append(user_dic)
            user = []
        else:
            user.append(line)
    return userlist

def getHTMLWithURL(url):
    if 'google' in url or 'facebook' in url or 'youtube' in url or 'twitter' in url or url[-3:] =='pdf':
        return ''
    try:
        response = urllib.request.urlopen(url, timeout=3)
        return response.read()
    except:
        return ''


def getSearchpageHTMLWithUseridAndURL(userid, url):
    filepath = os.path.join(utils.getDirSearchpage(), 'searchpage_' + userid + '.txt')
    if not os.path.exists(filepath):
        # print 'download searchpage from internet.'
        html = str(getHTMLWithURL(url)).encode('utf8')
        f = open(filepath, 'wb')
        f.write(html)
        f.close()
        # return html
    html = '\n'.join(open(filepath, 'r', encoding='utf-8').readlines())
    html = html.strip()
    if html == '':
        html = str(getHTMLWithURL(url)).encode('utf8')
        f = open(filepath, 'wb')
        f.write(html)
        f.close()
        return html
    return html


def getUrlFromSrg(srg):
    href = srg.find('a')['href'].strip()
    return href


def getHomepageHTMLWithUseridAndURLAndHpidx(userid, url, hpidx, x, length):
    filepath = os.path.join(utils.getDirHomepage(), 'homepage_' + userid + '_' + str(hpidx) +'.txt')
    if not os.path.exists(filepath):
        # print 'get homepage html from', url
        html = str(getHTMLWithURL(url)).encode('utf8')
        f = open(filepath, 'wb')
        f.write(html)
        f.close()


def handlePatchUserlist(left, userlist, allcount):
    # print 'thread %d' % threadid
    length = len(userlist)
    for x in range(length - 1, -1, -1):
        user_dic = userlist[x]
        id = user_dic['id']
        # print id, '=>', str(x) + '/' + str(length)
        search_results_page = user_dic['search_results_page']

        sphtml = getSearchpageHTMLWithUseridAndURL(id, search_results_page)
        # soup = BeautifulSoup(sphtml, "html5lib")
        # srgs = soup.find(attrs={'class', 'srg'})
        soup = BeautifulSoup(sphtml, 'html.parser')
        srgs = soup.find_all("h3", class_="r")[:1]

        # print str(x) + '/' + str(length * threadid)
        if srgs:
            for i, srg in enumerate(srgs):
                # print str(x) + '/' + str(length), ' ==> ', i
                # fea = np.array(getFeatureWithSrg(id, srg, i, name, org), dtype=np.str)
                url = getUrlFromSrg(srg)
                getHomepageHTMLWithUseridAndURLAndHpidx(id, url, i, x, length)
            print('%s ==> %d/%d' % (id, left + x, allcount))
        else:
            print('no srgs %s' % id)


def download():
    userlist = getUserlist()
    # count = int(len(userlist) / 3)
    # allcount = len(userlist)
    # handlePatchUserlist(0, userlist[:count], allcount)
    # handlePatchUserlist(count, userlist[count:count*2], allcount)
    # handlePatchUserlist(count*2, userlist[count*2:], allcount)

    threads = []
    count = int(len(userlist) / 3)
    allcount = len(userlist)
    for i in range(3):
        ul = userlist[i*count:(i + 1)*count]
        tx = threading.Thread(target=handlePatchUserlist, args=(count*i, ul, allcount))
        threads.append(tx)
    for t in threads:
        t.setDaemon(True)
        t.start()
    t.join()

if __name__ == '__main__':
    download()