from pybrain.datasets import ClassificationDataSet
from pybrain.utilities import percentError
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure.modules import SoftmaxLayer
from pybrain.tools.customxml.networkwriter import NetworkWriter

# from pylab import figure, clf, show, hold, plot, legend, xlabel, ylabel
import pylab

import csv
import numpy as np
import time


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
    features = []
    for (lv, rv, cv, klass) in raw_data:
        features.append((lv + 2, rv + 2, cv + 2, klass))
        features.append((lv + 2, rv + 2, cv, klass))
        features.append((lv + 2, rv, cv + 2, klass))
        features.append((lv + 2, rv, cv, klass))
        features.append((lv, rv + 2, cv + 2, klass))
        features.append((lv, rv + 2, cv, klass))
        features.append((lv, rv, cv + 2, klass))

        features.append((lv + 1, rv + 1, cv + 1, klass))
        features.append((lv + 1, rv + 1, cv, klass))
        features.append((lv + 1, rv, cv + 1, klass))
        features.append((lv + 1, rv, cv, klass))
        features.append((lv, rv + 1, cv + 1, klass))
        features.append((lv, rv + 1, cv, klass))
        features.append((lv, rv, cv + 1, klass))

        features.append((lv, rv, cv, klass))

        features.append((lv, rv, cv - 1, klass))
        features.append((lv, rv - 1, cv, klass))
        features.append((lv, rv - 1, cv - 1, klass))
        features.append((lv - 1, rv, cv, klass))
        features.append((lv - 1, rv, cv - 1, klass))
        features.append((lv - 1, rv - 1, cv, klass))
        features.append((lv - 1, rv - 1, cv - 1, klass))

        features.append((lv, rv, cv - 2, klass))
        features.append((lv, rv - 2, cv, klass))
        features.append((lv, rv - 2, cv - 2, klass))
        features.append((lv - 2, rv, cv, klass))
        features.append((lv - 2, rv, cv - 2, klass))
        features.append((lv - 2, rv - 2, cv, klass))
        features.append((lv - 2, rv - 2, cv - 2, klass))

    return features


def normalize_features(data):
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

    lV_features = (lV_features - lV_features.mean()) / lV_features.std()
    rV_features = (rV_features - rV_features.mean()) / rV_features.std()
    cV_features = (cV_features - cV_features.mean()) / cV_features.std()

    features = []
    for i in range(len(klasses)):
        features.append((lV_features[i], rV_features[i], cV_features[i], klasses[i]))
    return features


def main():
    raw_data = read_data()
    # full_features = add_extra_features(raw_data)
    norm_features = normalize_features(raw_data)
    # norm_features = normalize_features(full_features)

    alldata = ClassificationDataSet(3, 1, nb_classes=4)
    for lv, rv, cv, klass in norm_features:
        alldata.addSample([lv, rv, cv], [klass])

    tstdata_temp, trndata_temp = alldata.splitWithProportion(0.25)

    tstdata = ClassificationDataSet(3, 1, nb_classes=4)
    for n in xrange(0, tstdata_temp.getLength()):
        tstdata.addSample(tstdata_temp.getSample(n)[0], tstdata_temp.getSample(n)[1])

    trndata = ClassificationDataSet(3, 1, nb_classes=4)
    for n in xrange(0, trndata_temp.getLength()):
        trndata.addSample(trndata_temp.getSample(n)[0], trndata_temp.getSample(n)[1])

    trndata._convertToOneOfMany()
    tstdata._convertToOneOfMany()

    fnn = buildNetwork(trndata.indim, 5, trndata.outdim, outclass=SoftmaxLayer)
    trainer = BackpropTrainer(fnn, dataset=trndata, momentum=0.1, verbose=True, weightdecay=0.01)

    epochs = []
    trnresults = []
    tstresults = []

    epoch = 0
    for i in range(100):
        STEP = 20
        trainer.trainEpochs(STEP)
        epoch += STEP
        trnresult = percentError(trainer.testOnClassData(), trndata['class'])
        tstresult = percentError(trainer.testOnClassData(dataset=tstdata), tstdata['class'])

        print "epoch: %4d" % trainer.totalepochs, \
            "  train error: %5.2f%%" % trnresult, \
            "  test error: %5.2f%%" % tstresult

        epochs.append(epoch)
        trnresults.append(trnresult)
        tstresults.append(tstresult)

    pylab.figure(1)
    pylab.clf()
    pylab.plot(epochs, trnresults, label='Training')
    pylab.hold(True)
    pylab.plot(epochs, tstresults, label='Testing')
    pylab.legend()
    pylab.xlabel('Epochs')
    pylab.ylabel('percentError')

    timestamp = "_".join(str(time.time()).split("."))
    filename = "results/room-detector-" + timestamp
    pylab.savefig(filename + '.png')
    NetworkWriter.writeToFile(fnn, filename + '.xml')

    pylab.show()


if __name__ == "__main__":
    main()
