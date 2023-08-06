import tensorflow as tf
from tensorflow.keras import datasets


def load_data():
    r"""loading the cifar10 datasets."""
    (x_train, y_train), (x_test, y_test) = datasets.cifar10.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0

    train_ds = (
        tf.data.Dataset.from_tensor_slices((x_train, y_train)).shuffle(10000).batch(32)
    )

    test_ds = tf.data.Dataset.from_tensor_slices((x_test, y_test)).batch(32)

    return train_ds, test_ds


class Trainer:
    r"""."""

    def __init__(self):
        self.epochs = 5
        self.model = tf.keras.models.Sequential(
            [
                tf.keras.layers.Flatten(input_shape=(32, 32, 3)),
                tf.keras.layers.Dense(3000, activation="relu"),
                tf.keras.layers.Dense(1000, activation="relu"),
                tf.keras.layers.Dense(10),
            ]
        )
        self.loss_object = tf.keras.losses.SparseCategoricalCrossentropy(
            from_logits=True
        )
        self.optimizer = tf.keras.optimizers.Adam()

        # Select metrics to measure the loss and the accuracy of the model.
        self.train_loss = tf.keras.metrics.Mean(name="train_loss")
        self.train_acc = tf.keras.metrics.SparseCategoricalAccuracy(
            name="train_accuracy"
        )

        # datasets.
        self.train_ds, self.test_ds = load_data()

    @tf.function
    def _train_step(self, images, labels):
        with tf.GradientTape() as tape:

            predictions = self.model(images, training=True)
            loss = self.loss_object(labels, predictions)

        gradients = tape.gradient(loss, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))

        self.train_loss(loss)
        self.train_acc(labels, predictions)

    def train(self):
        for epoch in range(self.epochs):
            self.train_loss.reset_states()
            self.train_acc.reset_states()

            for images, labels in self.train_ds:
                self._train_step(images, labels)

        print(
            f"Epoch {epoch + 1}, "
            f"Loss: {self.train_loss.result()}, "
            f"Accuracy: {self.train_acc.result() * 100}"
        )
