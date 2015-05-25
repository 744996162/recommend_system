#coding=utf-8
__author__ = 'Administrator'
import os
import sys
import random
from collections import defaultdict
import math
from numpy import *


"""
step1 : 解析原始数据，数据格式为list_data = [(userid,itemid),(userid,itemid)..]

step2 : 分解数据, 分为训练集和测试集 splitData
        list_train_data = [(userid,itemid),(userid,itemid)..]
        list_test_data = [(userid,itemid),(userid,itemid)..]

step3 : 将数据转化为 defaultdict(set)  getDict()
        {userid1:set([itemid1,itemid2,..]), userid1:set([itemid1,itemid2,..])}

step4 : 计算出邻接矩阵W
        W = defaultdict(dict)
        {userid1:{userid1:value1, userid2:value2,...}, userid2:{userid1:value1, userid2:value2},..}

step5 : 通过邻接矩阵，计算与用户最接近的用户K个用户 recommendIdList
        getRecommendIdList()

step6 : 结合用户id 和 recommendIdList,根据W[userid][recommendId], recommenIdList 计算出的每个ItemId的评分
        给出推荐列表topN
"""



path = os.getcwd()
parent_path = os.path.dirname(path)

sys.path.append(parent_path)

def getData():
    file_in = open(parent_path + "/data_small/ratings.dat")
    # file_in = open(parent_path + "/data/ratings.dat")
    # UserID::MovieID::Rating::Timestamp
    # 1::3408::4::978300275
    list_data = []
    for line in file_in:
        strArr = line.strip().split("\t")
        # strArr = line.strip().split("::")
        userid = strArr[0]
        movieid = strArr[1]
        rating = float(strArr[2])
        Timestamp = strArr[3]
        # print(userid, movieid, rating)
        list_data.append([userid, movieid])
    return list_data


def splitData(data, M, k, seed):
    list_test = []
    list_train = []
    random.seed(seed)
    for userid, itemid in data:
        if random.randint(0, M) == k:
            list_test.append([userid, itemid])
        else:
            list_train.append([userid, itemid])
    return list_train, list_test

def getDict(list_data):
    dict_data = defaultdict(set)
    for userid, itemid in list_data:
        dict_data[userid].add(itemid)
    return dict_data



def userSimilarity(dict_data):
    W = defaultdict(dict)
    for u in dict_data.keys():
        for v in dict_data.keys():
            if u == v:
                continue
            W[u][v] = len(dict_data[u] & dict_data[v])
            if W[u][v] == 0:
                W[u][v] = 0
            else:
                W[u][v] /= math.sqrt(len(dict_data[u]) * len(dict_data[v]) * 1.0)
    return W


def userSimilarity_IIF(dict_data):
    W = defaultdict(dict)
    for u in dict_data.keys():
        for v in dict_data.keys():
            if u == v:
                continue
            W[u][v] = len(dict_data[u] & dict_data[v])/(math.log(1 + len(dict_data[v])))
            if W[u][v] == 0:
                W[u][v] = 0
            else:
                W[u][v] /= math.sqrt(len(dict_data[u]) * len(dict_data[v]) * 1.0)
    return W

def userSimilarity_plus(dict_data):
    dict_item = defaultdict(set)
    """
    dict_data:
    {userid1:set([itemid1,itemid2,..]), userid1:set([itemid1,itemid2,..])}

    dict_item is a dict:
    {itemid1:set[userid1,userid2,..],itemid2:set[userid1,userid4,..],..}

    """

    for userid, itemid_set in dict_data.items():
        for itemid in itemid_set:
            dict_item[itemid].add(userid)

    N = defaultdict(int)
    C = defaultdict(dict)

    for itemid, userid_set in dict_item.items():
        for u_userid in userid_set:
            N[u_userid] += 1
            for v_userid in userid_set:
                if u_userid == v_userid:
                    continue
                try:
                    C[u_userid][v_userid] += 1
                except KeyError:
                    C[u_userid][v_userid] = 0
                    C[u_userid][v_userid] += 1
                pass
    W = defaultdict(dict)
    for u_userid, user_dict in C.items():
        for v_userid, value in user_dict.items():
           W[u_userid][v_userid] = value/math.sqrt(N[u_userid]*N[v_userid])
    return W


def userSimilarity2(dict_data):

    dict_item = defaultdict(set)
    """
    dict_data:
    {userid1:set([itemid1,itemid2,..]), userid1:set([itemid1,itemid2,..])}

    dict_item is a dict:
    {itemid1:set[userid1,userid2,..],itemid2:set[userid1,userid4,..],..}

    """

    for userid, itemid_set in dict_data.items():
        for itemid in itemid_set:
            dict_item[itemid].add(userid)

    C = defaultdict(dict)
    N = defaultdict(int)

    for itemid, set_users in dict_item.items():
        for u in set_users:
            N[u] += 1
            for v in set_users:
                C[u][v] = 0

    for itemid, set_users in dict_item.items():
        for u in set_users:
            N[u] += 1
            for v in set_users:
                if u == v:
                    continue
                C[u][v] += 1 / math.log(1 + len(set_users))

    W = defaultdict(dict)
    for u_userid, related_users in C.items():
        for v_userid, value in related_users:
            W[u_userid][v_userid] = value / math.sqrt(N[u_userid] * N[v_userid])

    return W


def userSimilarity_new(train):

    """build inverse table for item_users"""
    item_object = dict()
    for userid, item in train:
        for itemid in item.keys():
            if itemid not in item_object:
                item_object[itemid] = set()
            item_object[itemid].add(userid)

    """calculate co-rated items between users"""

    C = dict()
    N = dict()
    for itemid, users in item_object.items():
        for u in users:
            N[u] += 1
            for v in users:
                if u == v:
                    continue
                C[u][v] += 1

    W = dict()
    for u, relate_users in C.items():
        for v in relate_users.items():
            W[u][v] = C[u][v] / math.sqrt(N[u]*N[v])
    return W


def getRecommendUserIdList(w, userid, k):
    """
    w is the line matrix ,data_struct W = defaultdict(dict)
    userid is users is
    k is the number of recommend users number
    """
    user_dict = w[userid]

    sorted_dict = sorted(user_dict.items(), key=lambda d: d[1], reverse=True)
    dict_recommendUserId = {}
    temp = 0
    for userid, value in sorted_dict:
        if temp >= k:
            break
        else:
            dict_recommendUserId[userid] = value
            temp += 1
    return dict_recommendUserId


def getRecommendItemId(dict_data, dict_recommendUserId, userid, topN):
    """
    dict_data 为输入数据 {userid1:set([itemid1,itemid2,..]), userid1:set([itemid1,itemid2,..])}
    dict_recommendUserId 为相似的用户列表
    topN 为推荐的数量
    """

    # temp_value 存储临时值
    temp_value = defaultdict(list)
    user_itemid_set = dict_data[userid]

    for similar_userid, value in dict_recommendUserId.items():
        itemid_set = dict_data[similar_userid]
        for itemid in itemid_set:
            temp_value[itemid].append(value)

    dict_itemid = dict()

    for itemid, valuelist in temp_value.items():
        if itemid in user_itemid_set:
            continue
            pass
        dict_itemid[itemid] = sum(valuelist)

    list_last_out = sorted(dict_itemid.items(), key=lambda d: d[1], reverse=True)


    list_recommendItemId = []
    temp = 0
    for itemid, value in list_last_out:
        if temp >= topN:
            break
        else:
            list_recommendItemId.append(itemid)
            temp += 1
        pass
    return list_recommendItemId



def data_show(list_data):
    for i in list_data:
        print(i)
    pass

list_data = getData()
list_train, list_test = splitData(list_data, M=8, k=3, seed=8)
dict_train = getDict(list_train)
dict_test = getDict(list_test)
W = userSimilarity(dict_train)
# W = userSimilarity_plus(dict_train)
# W = userSimilarity_IIF(dict_train)

def recommendMain(userid, k=3, topN=5):
    dict_recommendUserId = getRecommendUserIdList(W, userid, k=k)
    list_recommendItemId = getRecommendItemId(dict_train, dict_recommendUserId, userid, topN=topN)
    return list_recommendItemId



def recall(dict_train, dict_test, k=3, topN=5):
    hit = 0
    all = 0

    for userid in dict_train.keys():
        test_item_set = dict_test[userid]
        list_recommendItemId = recommendMain(userid, k, topN)

        for recommendItemId in list_recommendItemId:
            if recommendItemId in test_item_set:
                hit += 1
        all += len(test_item_set)
    return hit / (all*1.0)

"正确率"
def precision(dict_train, dict_test, k=3, topN=5):

    hit = 0
    all = 0
    for userid in dict_train.keys():
        test_item_set = dict_test[userid]
        list_recommendItemId = recommendMain(userid, k, topN)
        for recommendItemId in list_recommendItemId:
            if recommendItemId in test_item_set:
                hit += 1
        all += topN
    return hit/(all*1.0)

"覆盖率"
def coverage(dict_train, k=3, topN=5):
    recommend_items = []
    all_items = []

    for userid in dict_train.keys():
        for item in dict_train[userid]:
            all_items.append(item)
        list_recommendItemId = recommendMain(userid, k, topN)
        for recommendItemId in list_recommendItemId:
            recommend_items.append(recommendItemId)
    recommend_items_set = set(recommend_items)
    all_items_set = set(all_items)
    return len(recommend_items_set) / (len(all_items_set)*1.0)

def index(k, topN):

    recall1 = recall(dict_train, dict_test, k=k, topN=topN)
    precision1 = precision(dict_train, dict_test, k=k, topN=topN)
    coverage1 = coverage(dict_train, k=k, topN=topN)
    F1 = 2 * precision1 * recall1 / (precision1 + recall1)
    print("K", k, "topN", topN,"F1", F1, "recall:", recall1, "precision:", precision1,"coverage:", coverage1)
    # print("precision:", precision1)
    # print("coverage:", coverage1)


if __name__ == "__main__":

    # recall = recall(dict_train, dict_test, k=3, topN=5)
    # precision = precision(dict_train, dict_test, k=3, topN=5)
    # coverage = coverage(dict_train, k=3, topN=5)

    # print("recall:", recall)
    # print("precision:", precision)
    # print("coverage:", coverage)
    # index(k=3, topN=5)
    # index(k=10, topN=5)
    index(k=20, topN=5)
    # index(k=30, topN=5)
    index(k=40, topN=5)
    # index(k=50, topN=5)
    # index(k=60, topN=5)
    index(k=80, topN=5)


    # index(k=3, topN=10)
    # index(k=10, topN=10)
    # index(k=20, topN=10)
    # index(k=40, topN=10)
    # index(k=80, topN=10)


    # index(k=3, topN=20)
    # index(k=10, topN=20)

    index(k=20, topN=15)
    index(k=30, topN=15)

    #best
    index(k=40, topN=15)

    index(k=60, topN=15)
    index(k=80, topN=15)


    index(k=20, topN=20)

    # ('K', 30, 'topN', 20, 'F1', 0.15028947264778858, 'recall:', 0.1692840031940378, 'precision:', 0.13512747875354109, 'coverage:', 0.054252199413489736)
    index(k=30, topN=20)

    index(k=40, topN=20)
    index(k=60, topN=20)
    index(k=80, topN=20)
    # print(d_data)

# UserCF
# ('K', 20, 'topN', 5, 'F1', 0.10391189784474023, 'recall:', 0.06822819625587792, 'precision:', 0.21784702549575072, 'coverage:', 0.03421309872922776)
# ('K', 40, 'topN', 5, 'F1', 0.109992568069725, 'recall:', 0.07222074350102031, 'precision:', 0.23059490084985837, 'coverage:', 0.022605083088954057)
# ('K', 80, 'topN', 5, 'F1', 0.10634416593473414, 'recall:', 0.06982521515393487, 'precision:', 0.22294617563739377, 'coverage:', 0.015518084066471163)
# ('K', 20, 'topN', 15, 'F1', 0.14427519326654775, 'recall:', 0.1399166001242126, 'precision:', 0.14891406987724268, 'coverage:', 0.05840664711632453)
# ('K', 30, 'topN', 15, 'F1', 0.14775170394766934, 'recall:', 0.14328808446455504, 'precision:', 0.15250236071765816, 'coverage:', 0.04594330400782014)
# ('K', 40, 'topN', 15, 'F1', 0.1490325236722931, 'recall:', 0.1445302102741549, 'precision:', 0.1538243626062323, 'coverage:', 0.041666666666666664)
# ('K', 60, 'topN', 15, 'F1', 0.14711129408535747, 'recall:', 0.14266702155975514, 'precision:', 0.1518413597733711, 'coverage:', 0.03409090909090909)
# ('K', 80, 'topN', 15, 'F1', 0.14711129408535747, 'recall:', 0.14266702155975514, 'precision:', 0.1518413597733711, 'coverage:', 0.030303030303030304)
# ('K', 20, 'topN', 20, 'F1', 0.14895041550155566, 'recall:', 0.16777570756809512, 'precision:', 0.13392351274787537, 'coverage:', 0.06744868035190615)
# ('K', 30, 'topN', 20, 'F1', 0.15028947264778858, 'recall:', 0.1692840031940378, 'precision:', 0.13512747875354109, 'coverage:', 0.054252199413489736)
# ('K', 40, 'topN', 20, 'F1', 0.14965932810838484, 'recall:', 0.16857421701712358, 'precision:', 0.13456090651558072, 'coverage:', 0.04838709677419355)
# ('K', 60, 'topN', 20, 'F1', 0.1491079516364066, 'recall:', 0.16795315411232367, 'precision:', 0.13406515580736544, 'coverage:', 0.03983382209188661)
# ('K', 80, 'topN', 20, 'F1', 0.14950179197353392, 'recall:', 0.16839677047289503, 'precision:', 0.13441926345609065, 'coverage:', 0.0353128054740958)
#



# UserCF_IIF
# ('K', 20, 'topN', 5, 'F1', 0.09973720435489926, 'recall:', 0.06400578220366206, 'precision:', 0.22577903682719547, 'coverage:', 0.036973555337904015)
# ('K', 40, 'topN', 5, 'F1', 0.09873607808784883, 'recall:', 0.06336331513009959, 'precision:', 0.2235127478753541, 'coverage:', 0.023996082272282077)
# ('K', 80, 'topN', 5, 'F1', 0.09623326242022273, 'recall:', 0.06175714744619338, 'precision:', 0.21784702549575072, 'coverage:', 0.016405484818805095)
# ('K', 20, 'topN', 15, 'F1', 0.14720944362468535, 'recall:', 0.13620301959524575, 'precision:', 0.16015108593012276, 'coverage:', 0.06917238001958864)
# ('K', 30, 'topN', 15, 'F1', 0.1453866851835778, 'recall:', 0.13451654352714423, 'precision:', 0.15816808309726157, 'coverage:', 0.05435847208619001)
# ('K', 40, 'topN', 15, 'F1', 0.14434510893151636, 'recall:', 0.1335528429168005, 'precision:', 0.15703493862134088, 'coverage:', 0.04738001958863859)
# ('K', 60, 'topN', 15, 'F1', 0.1435639267424703, 'recall:', 0.13283006745904272, 'precision:', 0.15618508026440037, 'coverage:', 0.03770812928501469)
# ('K', 80, 'topN', 15, 'F1', 0.1421751584063883, 'recall:', 0.13154513331191778, 'precision:', 0.1546742209631728, 'coverage:', 0.03256611165523996)
# ('K', 20, 'topN', 20, 'F1', 0.14993225952130063, 'recall:', 0.1599743013170575, 'precision:', 0.14107648725212465, 'coverage:', 0.08080313418217434)
# ('K', 30, 'topN', 20, 'F1', 0.1505343971097396, 'recall:', 0.16061676839061997, 'precision:', 0.141643059490085, 'coverage:', 0.06476493633692458)
# ('K', 40, 'topN', 20, 'F1', 0.15158813788950773, 'recall:', 0.1617410857693543, 'precision:', 0.14263456090651558, 'coverage:', 0.056317335945151814)
# ('K', 60, 'topN', 20, 'F1', 0.14850218274875807, 'recall:', 0.15844844201734662, 'precision:', 0.13973087818696883, 'coverage:', 0.045298726738491675)
# ('K', 80, 'topN', 20, 'F1', 0.14413668523257564, 'recall:', 0.15379055573401862, 'precision:', 0.13562322946175637, 'coverage:', 0.03807541625857003)



