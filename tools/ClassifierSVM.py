from sklearn import svm

import csv
import numpy as np
import time
import random


def read_data():
    raw_data = []
    with open('rooms.csv', 'rb') as f:
        reader = csv.reader(f)
        reader.next()
        for lv, rv, cv, klass in reader:
            raw_data.append((int(lv), int(rv), int(cv), int(klass)))
        f.close()
    return raw_data


def add_extra_features(raw_data):
    samples = []
    for (lv, rv, cv, klass) in raw_data:
        samples.append((lv + 2, rv + 2, cv + 2, klass))
        samples.append((lv + 2, rv + 2, cv, klass))
        samples.append((lv + 2, rv, cv + 2, klass))
        samples.append((lv + 2, rv, cv, klass))
        samples.append((lv, rv + 2, cv + 2, klass))
        samples.append((lv, rv + 2, cv, klass))
        samples.append((lv, rv, cv + 2, klass))

        samples.append((lv + 1, rv + 1, cv + 1, klass))
        samples.append((lv + 1, rv + 1, cv, klass))
        samples.append((lv + 1, rv, cv + 1, klass))
        samples.append((lv + 1, rv, cv, klass))
        samples.append((lv, rv + 1, cv + 1, klass))
        samples.append((lv, rv + 1, cv, klass))
        samples.append((lv, rv, cv + 1, klass))

        samples.append((lv, rv, cv, klass))

        samples.append((lv, rv, cv - 1, klass))
        samples.append((lv, rv - 1, cv, klass))
        samples.append((lv, rv - 1, cv - 1, klass))
        samples.append((lv - 1, rv, cv, klass))
        samples.append((lv - 1, rv, cv - 1, klass))
        samples.append((lv - 1, rv - 1, cv, klass))
        samples.append((lv - 1, rv - 1, cv - 1, klass))

    return samples


def normalize_samples(data):
    lV_features = []
    rV_features = []
    cV_features = []
    klasses = []

    for lv, rv, cv, klass in data:
        lV_features.append(lv)
        rV_features.append(rv)
        cV_features.append(cv)
        klasses.append(klass)

    lV_features = np.asarray(lV_features)
    rV_features = np.asarray(rV_features)
    cV_features = np.asarray(cV_features)

    lV_mean = lV_features.mean()
    rV_mean = rV_features.mean()
    cV_mean = cV_features.mean()

    lV_std = lV_features.std()
    rV_std = rV_features.std()
    cV_std = cV_features.std()

    statistics = [(lV_mean, lV_std), (rV_mean, rV_std), (cV_mean, cV_std)]

    lV_features = (lV_features - lV_mean) / lV_std
    rV_features = (rV_features - rV_mean) / rV_std
    cV_features = (cV_features - cV_mean) / cV_std

    features = []
    for i in range(len(klasses)):
        features.append([lV_features[i], rV_features[i], cV_features[i]])
    return [features, klasses, statistics]


def normalize_features(features, statistics):
    n_features = []
    for i, [mean, std] in enumerate(statistics):
        n_features.append((features[i] - mean) / std)
    return n_features


def get_training_and_test_sets(X, y, ratio):
    samples = []
    for i in range(len(X)):
        samples.append(X[i] + [y[i]])
    random.shuffle(samples)
    train = samples[:int(len(samples) * (1 - ratio))]
    test = samples[:int(len(samples) * ratio)]

    Xtrain = []
    ytrain = []
    for [lV, rV, cV, klass] in train:
        Xtrain.append([lV, rV, cV])
        ytrain.append(klass)

    Xtest = []
    ytest = []
    for [lV, rV, cV, klass] in test:
        Xtest.append([lV, rV, cV])
        ytest.append(klass)

    return [Xtrain, ytrain, Xtest, ytest]


def main():
    print("######## Room detector v0.1 ########\n")
    raw_data = read_data()
    full_features = add_extra_features(raw_data)
    [X, y, statistics] = normalize_samples(full_features)
    [Xtrain, ytrain, Xtest, ytest] = get_training_and_test_sets(X, y, 0.25)

    print("---------------------------------------------------------")
    print("Original number of samples: {}".format(len(raw_data)))
    print("Expanded number of samples: {}".format(len(X)))
    print("Training set number of samples: {}".format(len(Xtrain)))
    print("Test set number of samples: {}".format(len(Xtest)))
    print("---------------------------------------------------------\n")

    start = time.time()
    print("---------------------------------------------------------")
    print("Training SVM...")
    classifier = svm.SVC(decision_function_shape='ovo')
    classifier.fit(Xtrain, ytrain)
    end = time.time()
    print("Training finished! Time elapsed: {}s".format(end-start))
    print("---------------------------------------------------------\n")

    print("---------------------------------------------------------")
    print("Training set score: {}%".format(classifier.score(Xtrain, ytrain) * 100))
    print("Test set score: {}%".format(classifier.score(Xtest, ytest) * 100))
    print("Cross-validation set score: {}%".format(classifier.score(X, y) * 100))
    print("---------------------------------------------------------\n")

    predictions = [([173, 318, 43], 2), ([183, 467, 37], 0), ([176, 179, 39], 3), ([216, 188, 40], 1)]
    passed = 0
    failed = 0
    print("---------------------------------------------------------")
    for (features, expected) in predictions:
        prediction = classifier.predict([normalize_features(features,statistics)])
        if prediction[0] == expected:
            passed += 1
        else:
            failed += 1
        print("Prediction for {0} (expected {1}): {2}".format(features, expected, prediction[0]))
    print("Assertion ratio: {}%".format(passed / 4 * 100))
    print("---------------------------------------------------------\n")


if __name__ == "__main__":
    main()
