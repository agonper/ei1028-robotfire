import sys
import pickle


class ClassifierSVMLoader:
    def __init__(self, file_name):
        config_file = open(file_name, "rb")
        [statistics, classifier] = pickle.load(config_file)
        self.statistics = statistics
        self.classifier = classifier

    def _normalize_features(self, features):
        n_features = []
        for i, [mean, std] in enumerate(self.statistics):
            n_features.append((features[i] - mean) / std)
        return n_features

    def predict(self, features):
        return self.classifier.predict([self._normalize_features(features)])[0]


def main():
    print("######## Room detector tester v0.1 ########\n")

    file_name = sys.argv[1]
    classifier = ClassifierSVMLoader(file_name)

    predictions = [([173, 318, 43], 2), ([183, 467, 37], 0), ([176, 179, 39], 3), ([216, 188, 40], 1)]
    passed = 0
    failed = 0
    print("---------------------------------------------------------")
    for (features, expected) in predictions:
        prediction = classifier.predict(features)
        if prediction == expected:
            passed += 1
        else:
            failed += 1
        print("Prediction for {0} (expected {1}): {2}".format(features, expected, prediction))
    print("Assertion ratio: {}%".format(passed / 4 * 100))
    print("---------------------------------------------------------\n")


if __name__ == "__main__":
    main()

