__author__ = 'Administrator'
def Recommend(user, N):
    pass
    return None


def PrecisionRecall(test, N):
    hit = 0
    n_recall = 0
    n_precision = 0
    for user, items, in test.items:
        rank = Recommend(user, N)
        hit += len(rank & items)
        n_recall += len(items)
        n_precision += N
        return [hit / (1.0 * n_recall), hit / (1.0 * n_precision)]
