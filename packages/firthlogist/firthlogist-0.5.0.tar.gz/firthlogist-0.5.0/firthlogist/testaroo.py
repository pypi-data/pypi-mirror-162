import numpy as np
from firthlogist import FirthLogisticRegression, load_sex2
from scalene import scalene_profiler


def sex2():
    X = np.loadtxt('datasets/sex2.csv', skiprows=1, delimiter=",")
    y = X[:, 0]
    X = X[:, 1:]
    feature_names = ["age", "oc", "vic", "vicl", "vis", "dia"]
    return X, y, feature_names


def endometrial():
    X = np.loadtxt('datasets/endometrial.csv', skiprows=1, delimiter=",")
    y = X[:, -1]
    X = X[:, :-1]
    feature_names = ["NV", "PI", "EH"]
    return X, y, feature_names


if __name__ == '__main__':
    # X = np.load('../letter_img_X.npy')
    # y = np.load('../letter_img_y.npy')
    X, y, feature_names = endometrial()
    fl = FirthLogisticRegression(test_vars=[1, 2])
    # scalene_profiler.start()
    fl.fit(X, y)
    # print(fl.pvals_)
    # scalene_profiler.stop()
    fl.summary(feature_names)
    print(feature_names)
    # print(fl.coef_.shape)
    # print(fl.ci_)