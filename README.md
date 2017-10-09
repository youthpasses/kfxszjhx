# 2017开放学术精准画像21/398

https://biendata.com/competition/scholar/

共有三个task

## 任务1: 学者画像信息抽取

学者画像信息具体包括学者的主页地址、性别、职位等。随着互联网越来越普及，与学者相关的网页的数量和内容的丰富度和复杂度都大大增加，其中包含了学者的大量冗余信息，通过整合互联网上多种来源的学者数据，采用合适的机器学习模型，获得学者的精准信息是一项潜在有效的学者画像技术。

任务1有两步：一是对searchpage的用户主页进行判别，此为一个二分类问题；二是在找到主页后，从主页中提取照片链接pic、邮箱email、性别gender、职位position、地区location信息。

#### 1.1 主页判别

特征：
    在list中idx, one-hot
    标题中是否存在学者名字
    url中是否含有“edu”
    url中是否含有学者名字
    url中是否含有“profile”
    homepage 是否含有？
        学者名字
        学者所在组织org
        "university"
        “department”
        "school"
        "institute"
        "professor"
        "personal webpage"
        "email"
        "phone"
        "office"
        "home"
        "fax"
        "address"
        "profile"
        "research"
        “research topic”
        "Research Interest"
        "publication"
        "selected publication"
        "award"
        "honor"
        "academic"
        "gallery"
        "news"

模型：尝试过决策树、SVM、LR，LR效果最好准确率85%左右。

#### 1.2 学者信息提取

###### 1.2.1 照片链接pic

正则找到所有<img...>，src+alt判断学者姓名、profile、logo、footer、svg，若pic前缀不为http需要截取homepage目录进行补充。

###### 1.2.2 邮箱email

"mailto" ==> @ 正则匹配 ==> email 正则匹配 ==> at, AT, dot, DOT 正则匹配+长度<40 ==> at, AT, . 正则匹配+长度<40

###### 1.2.3 性别gender

维护一个女孩名字字典 + 照片cnn判别

##### 1.2.3 职称position

从train数据中提取所有的position，得到一个字典。从学者主页的txt中进行匹配，原则是就长不就短。

##### 1.2.4 地区location

与1.2.3同


## 任务2：学者兴趣标签发现

根据合作者的兴趣标签对vali中学者兴趣标签进行更新
扩展：可对每个会议做一个兴趣标签的聚类。然后在对学者的兴趣标签更新。

## 任务3：学者未来学术影响力预测

特征：
    0 学者发表论文数；
    1 所有合作者人数；
    2 学者所有论文总引用数；
    3-10 学者从2013年往前每10年发表论文的总数；
    11-18 学者从2013年往前每10年发表论文的引用总数；
    19 学者发表论文的会议期刊数；
    20 学者发表论文所有期刊的所有论文总数；

模型：xgboost，效果较差0.2+，改为线性回归0.33。
