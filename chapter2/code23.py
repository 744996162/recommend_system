#coding=utf-8
__author__ = 'Administrator'
import random
import math


def GetRecommendation(user, N):
    return None

def splitData(data, M, k, seed):
    test = []
    train = []
    random.seed(seed)
    for userid, item in data:
        if random.randint(0, M) == k:
            test.append([userid, item])
        else:
            train.append([userid, item])
    return train, test
    pass


def recall(train, test, N):
    hit = 0
    all = 0
    for user in train.key():
        tu = test[user]
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            if item in tu:
                hit += 1
        all += len(tu)
    return hit / (all*1.0)


"正确率"
def precision(train, test, N):
    hit = 0
    all = 0
    for user in train.key():
        tu = test[user]
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            if item in tu:
                hit += 1
        all += N
    return hit/(all*1.0)
    pass

"覆盖率"
def coverage(train, test, N):
    recommend_items = []
    all_items = []
    for user in train.keys():
        for item in train[user].keys:
            all_items.append(item)
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            recommend_items.append(item)
    recommend_items_set = set(recommend_items)
    all_items_set = set(all_items)
    return len(recommend_items_set) / (len(all_items_set)*1.0)


"余弦相似度"
def userSimilarity(train):
    W = dict()
    for u in train.keys():
        for v in train.keys():
            if u == v:
                continue
            W[u][v] = len(train[u] & train[v])
            W[u][v] /= math.sqrt(len(train[u]) * len(train[v]) * 1.0)
    return W



def userSimilarity_new(train):

    """build inverse table for item_users"""
    item_object = dict()
    for userid, item in train.items():
        for itemid in item.keys():
            if itemid not in item_object:
                item_object[itemid] = set()
            item_object[itemid].add(userid)
    pass



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
