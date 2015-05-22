#coding=utf-8
__author__ = 'Administrator'
import os
import sys
import random
from collections import defaultdict
import math



"""
step1 : 解析原始数据，数据格式为list_data = [(userid,itemid),(userid,itemid)..]

step2 : 分解数据, 分为训练集和测试集 splitData
        list_train_data = [(userid,itemid),(userid,itemid)..]
        list_test_data = [(userid,itemid),(userid,itemid)..]

step3 : 将数据转化为 defaultdict(set)  getDict()
        {userid1:set([itemid1,itemid2,..]), userid1:set([itemid1,itemid2,..])}

step4 : 计算出邻接矩阵W
        W = defaultdict(dict)
        {userid1:{itemid1:value1,itemid2:value2,...}, userid2:{itemid1:value1,itemid2:value2},..}

step5 : 通过邻接矩阵，计算与用户最接近的用户K个用户 recommendIdList
        getRecommendIdList()

step6 : 结合用户id 和 recommendIdList,根据W[userid][recommendId],recommenIdList 计算出的每个ItemId的评分
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
            W[u][v] /= math.sqrt(len(dict_data[u]) * len(dict_data[v]) * 1.0)
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



def data_show(list_data):
    for i in list_data:
        print(i)
    pass

list_data = getData()
list_train, list_test = splitData(list_data, M=8, k=3, seed=3)
dict_train = getDict(list_train)
dict_test = getDict(list_test)
W = userSimilarity(dict_train)

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
    index(k=20, topN=10)
    index(k=40, topN=10)
    index(k=80, topN=10)


    # index(k=3, topN=20)
    # index(k=10, topN=20)
    index(k=20, topN=20)
    index(k=40, topN=20)
    index(k=80, topN=20)
    # print(d_data)