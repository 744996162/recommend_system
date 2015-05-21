__author__ = 'Administrator'
import os
import sys
import random


path = os.getcwd()
parent_path = os.path.dirname(path)

sys.path.append(parent_path)

def getData():
    file_in = open(parent_path + "/data_small/ratings.dat")

    # UserID::MovieID::Rating::Timestamp
    # 1::3408::4::978300275

    for line in file_in:
        strArr = line.strip().split("\t")
        userid = strArr[0]
        movieid = strArr[1]
        rating = float(strArr[2])
        Timestamp = strArr[3]
        print(userid, movieid, rating)
        pass

    pass

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

if __name__ == "__main__":
    getData()
