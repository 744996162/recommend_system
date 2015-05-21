__author__ = 'Administrator'
import os
import sys
import random
from collections import defaultdict

path = os.getcwd()
parent_path = os.path.dirname(path)

sys.path.append(parent_path)

def getData():
    file_in = open(parent_path + "/data_small/ratings.dat")

    # UserID::MovieID::Rating::Timestamp
    # 1::3408::4::978300275
    d_data = defaultdict(set)
    for line in file_in:
        strArr = line.strip().split("\t")
        userid = strArr[0]
        movieid = strArr[1]
        rating = float(strArr[2])
        Timestamp = strArr[3]
        # print(userid, movieid, rating)
        d_data[userid].add(movieid)
    return d_data

def splitData(data, M, k, seed):
    d_test = defaultdict(set)
    d_train = defaultdict(set)
    random.seed(seed)
    for userid, itemid_set in data:
        if random.randint(0, M) == k:
            d_test[userid] = itemid_set
        else:
            d_train[userid] = itemid_set
    return d_train, d_test
    pass


def data_show(d_data):
    for key, value in d_data.items():
        print(key,value)
    pass

if __name__ == "__main__":
    d_data = getData()
    train
    data_show(d_data)
    # print(d_data)