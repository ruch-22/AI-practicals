import numpy as np

class Perceptron:
    def __init__(self, learning_rate=0.01, n_iterations=100):  # fixed here
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.weights = None
        self.bias = None
        self.errors = []

    def _unit_step_function(self, x):
        return np.where(x >= 0, 1, -1)

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0

        for _ in range(self.n_iterations):
            n_misclassifications = 0
            for idx, x_i in enumerate(X):
                linear_output = np.dot(x_i, self.weights) + self.bias
                y_predicted = self._unit_step_function(linear_output)

                if y_predicted != y[idx]:
                    update = self.learning_rate * (y[idx] - y_predicted)
                    self.weights += update * x_i
                    self.bias += update
                    n_misclassifications += 1

            self.errors.append(n_misclassifications)
            if n_misclassifications == 0:
                break

    def predict(self, X):
        linear_output = np.dot(X, self.weights) + self.bias
        return self._unit_step_function(linear_output)

# Example Usage
if __name__ == "__main__":   # fixed here
    X = np.array([
        [0, 0],
        [0, 1],
        [1, 0],
        [1, 1]
    ])
    y = np.array([-1, -1, -1, 1])  # AND gate outputs

    perceptron = Perceptron(learning_rate=0.1, n_iterations=10)
    perceptron.fit(X, y)

    print("Perceptron training complete.")
    print(f"Final Weights: {perceptron.weights}")
    print(f"Final Bias: {perceptron.bias}")
    print(f"Errors per epoch: {perceptron.errors}")

    predictions = perceptron.predict(X)
    print(f"Predictions for X:\n{X}")
    print(f"Actual labels: {y}")
    print(f"Predicted labels: {predictions}")

    new_input = np.array([1, 0])
    predicted_label = perceptron.predict(new_input)
    print(f"Prediction for {new_input}: {predicted_label}")
