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

step6 : 根据用户id 和 recommendIdList,根据W[userid][recommendId],recommenIdList 计算出的每个ItemId的评分
        给出推荐列表topN
"""



path = os.getcwd()
parent_path = os.path.dirname(path)

sys.path.append(parent_path)


class Recommend(object):
    def __init__(self):
        self.data_path = parent_path + "/data_small/ratings.dat"
        # self.list_data = self.getData()
        self.list_train, self.list_data = self.splitData()

        pass

    def getData(self):
        file_in = open(self.data_path)
        # UserID::MovieID::Rating::Timestamp
        # 1::3408::4::978300275
        list_data = []
        for line in file_in:
            strArr = line.strip().split("\t")
            userid = strArr[0]
            movieid = strArr[1]
            list_data.append([userid, movieid])
        return list_data

    def splitData(self, M=10, k=3, seed=5):
        data = self.getData()
        list_test = []
        list_train = []
        random.seed(seed)
        for userid, itemid in data:
            if random.randint(0, M) == k:
                list_test.append([userid, itemid])
            else:
                list_train.append([userid, itemid])
        return list_train, list_test


    def getDict(self, list_data):
        dict_data = defaultdict(set)
        for userid, itemid in list_data:
            dict_data[userid].add(itemid)
        return dict_data


    def userSimilarity(self, dict_data):
        W = defaultdict(dict)
        for u in dict_data.keys():
            for v in dict_data.keys():
                if u == v:
                    continue
                W[u][v] = len(dict_data[u] & dict_data[v])
                W[u][v] /= math.sqrt(len(dict_data[u]) * len(dict_data[v]) * 1.0)
        return W


    def getRecommendUserIdList(self, w, userid, k):
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


    def getRecommendItemId(self, dict_data, dict_recommendUserId, userid, topN):

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


        recommendItemId = []
        temp = 0
        for itemid, value in list_last_out:
            if temp >= topN:
                break
            else:
                recommendItemId.append(itemid)
                temp += 1
            pass
        return recommendItemId


if __name__ == "__main__":



    pass