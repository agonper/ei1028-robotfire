import re
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

FILE_NAME = "room_{}.txt"
N_ROOMS = 4
MARKERS = [("b", "."), ("r", "."), ("c", "."), ("y", ".")]


def normalize(features, type):
    min_v = 0
    max_v = 0
    if type == "ir":
        min_v = 100
        max_v = 800
    else:
        min_v = 0
        max_v = 100

    n_features = []
    for f in features:
        n_features.append((f - min_v) / (max_v - min_v))
    return features
    # return n_features


def generate_extra_features(feature):
    f = int(feature)
    return [f + 2, f + 1, f, f - 1, f - 2]


def file_parser(file):
    data_set = file.read()
    m = re.findall("\((\d*), (\d*), (\d*)\)", data_set)

    features = []
    for elem in m:
        features.append((elem[0], elem[1], elem[2]))
    return features


def load_rooms():
    rooms = []
    results = open('rooms.csv', 'w')
    results.write("Left value, Right value, Center value, Class\n")

    for i in range(N_ROOMS):
        room = i + 1
        file_name = FILE_NAME.format(room)
        file = open(file_name, "r")
        features = file_parser(file)

        print(len(features))

        lV_features = []
        cV_features = []
        rV_features = []
        for (lV, cV, rV) in features:
            lV_features += generate_extra_features(lV)
            cV_features += generate_extra_features(cV)
            rV_features += generate_extra_features(rV)
            results.write("{0}, {1}, {2}, {3}\n".format(lV, rV, cV, i))

        room = (lV_features, cV_features, rV_features)
        n_room = []
        for values in room:
            values_np = np.asarray(values)
            n_values = (values_np - values_np.mean()) / values_np.std()
            n_room.append(n_values)
        room = tuple(n_room)
        rooms.append(room)
        file.close()

    results.close()
    return rooms


def main():
    rooms = load_rooms()

    fig2 = plt.figure(1)
    ax = fig2.add_subplot(111, projection='3d')

    fig = plt.figure(2)

    for i, (lV_features, cV_features, rV_features) in enumerate(rooms):
        (c, m) = MARKERS[i]
        room = i + 1
        ax.scatter(lV_features, rV_features, cV_features, c=c, marker=m)

        plt.subplot(4, 1, room)
        plt.plot(range(len(lV_features)), lV_features)

        plt.subplot(4, 1, room)
        plt.plot(range(len(cV_features)), cV_features)

        plt.subplot(4, 1, room)
        plt.plot(range(len(rV_features)), rV_features)
        plt.title("Room {}".format(room))

    ax.set_xlabel('Left values')
    ax.set_ylabel('Rigth values')
    ax.set_zlabel('Center values')

    plt.show()


if __name__ == "__main__":
    main()
