import tensorflow as tf
from tensorflow.keras import applications, layers, models


class TNToolsModel(tf.keras.models.Model):
    """
    Model class for training a TwinNetwork. Triplet loss
    is calculated from embeddings generated by a CNN model.
    """
    def __init__(self, tn, loss_margin=0.5):
        super(TNToolsModel, self).__init__()
        self.loss_margin = loss_margin
        self.loss_tracker = tf.keras.metrics.Mean(name="loss")
        self.tn = tn

    def call(self, inputs):
        """
        Apply model to input data.
        """
        return self.tn(inputs)

    @property
    def metrics(self):
        """
        List model metrics.
        """
        return [self.loss_tracker]

    def test_step(self, data):
        """
        Perform following tasks as testing step:
        1. Get embedding distances
        2. Calculate loss
        """
        distance_ap, distance_an = self.tn(data)
        loss = tf.maximum(distance_ap + self.loss_margin - distance_an, 0.0)
        self.loss_tracker.update_state(loss)
        return {"loss": self.loss_tracker.result()}

    def train_step(self, data):
        """
        Perform following tasks as training step:
        1. Use tf.GradientTape to track automatically calculated
        derivatives/gradients
        2. Get embedding distances
        3. Calculate loss
        4. Access gradient
        5. Apply gradient on optimizer
        6. Update accuracy parameters
        """
        with tf.GradientTape() as tape:
            distance_ap, distance_an = self.tn(data)
            # The following corresponds to
            #
            loss = tf.maximum(
                distance_ap - distance_an + self.loss_margin, 0.0
            )

        grad = tape.gradient(loss, self.tn.trainable_weights)

        self.optimizer.apply_gradients(
            zip(grad, self.tn.trainable_weights)
        )
        self.loss_tracker.update_state(loss)
        return {"loss": self.loss_tracker.result()}


class TNToolsNetwork:
    """
    This class contains methods to create an embedding model and
    the corresponding Twin Network based on the ResNet50 architecture.
    """
    def __init__(self, img_size=224):
        self.distance_layer = TNToolsDistanceLayer()
        self.img_size = img_size
        self.layers_trainable = ["conv5_block1_out"]
        self.num_channels = 3
        self.shape_input = (self.img_size, self.img_size, self.num_channels)

    @staticmethod
    def callbacks_fn(checkpoint_filepath, tensorboard_logdir):
        """Create training callbacks."""
        model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
            filepath=checkpoint_filepath,
            save_weights_only=True,
            monitor='val_loss',
            mode='min',
            save_best_only=True)

        tensorboard_callback = tf.keras.callbacks.TensorBoard(
            log_dir=tensorboard_logdir
        )
        return model_checkpoint_callback, tensorboard_callback

    def fn_layers_input(self):
        """
        Convenience function to create three input layers.
        """
        anchor_input = tf.keras.layers.Input(name="anchor",
                                             shape=self.shape_input)
        positive_input = tf.keras.layers.Input(name="positive",
                                               shape=self.shape_input)
        negative_input = tf.keras.layers.Input(name="negative",
                                               shape=self.shape_input)
        return anchor_input, positive_input, negative_input

    def tn_embedding_make(self):
        """
        Create an embedding model with the ResNet50 architecture.
        """
        base_cnn = applications.resnet.ResNet50(
            weights="imagenet",
            input_shape=(self.img_size, self.img_size, self.num_channels),
            include_top=False
        )

        flatten = layers.Flatten()(base_cnn.output)
        dense1 = layers.Dense(512, activation="relu")(flatten)
        dense1 = layers.BatchNormalization()(dense1)
        dense2 = layers.Dense(256, activation="relu")(dense1)
        dense2 = layers.BatchNormalization()(dense2)
        output = layers.Dense(256)(dense2)

        embedding = models.Model(base_cnn.input, output, name="Embedding")

        trainable = False
        for layer in base_cnn.layers:
            if layer.name in self.layers_trainable:
                trainable = True
            layer.trainable = trainable

        return embedding

    def tn_network_resnet_make(self, model_embedding):
        """
        Instantiate a Twin Network based on the
        ResNet50 architecture.
        """
        model_embedding.name == 'Embedding_resnet50'

        anchor_input, positive_input, negative_input = self.fn_layers_input()

        distances = self.distance_layer(
            model_embedding(
                tf.keras.applications.resnet_v2.preprocess_input(
                    anchor_input)),
            model_embedding(
                tf.keras.applications.resnet_v2.preprocess_input(
                    positive_input)),
            model_embedding(
                tf.keras.applications.resnet_v2.preprocess_input(
                    negative_input)),
        )

        twin_network = tf.keras.models.Model(
            inputs=[anchor_input, positive_input, negative_input],
            name='twin_network_resnet50',
            outputs=distances
        )
        return twin_network


class TNToolsDistanceLayer(layers.Layer):
    """
    Layer class for calculation of distances between positive
    and anchor embeddings and negative and anchor embeddings.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def call(anchor, positive, negative):
        """
        Please note this function is named 'call', as it will be called
        in '__call__' after 'build()' has been called.
        """
        ap_distance = tf.reduce_sum(tf.square(anchor - positive), -1)
        an_distance = tf.reduce_sum(tf.square(anchor - negative), -1)
        return ap_distance, an_distance