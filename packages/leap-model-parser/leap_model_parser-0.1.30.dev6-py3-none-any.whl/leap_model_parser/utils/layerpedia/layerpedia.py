class Layerpedia:
    layer_mapping_dict = {
        'Activation': {'is_trainable': False, 'kernel_index': None},
        'ActivityRegularization': {'is_trainable': False, 'kernel_index': None},
        'Add': {'is_trainable': False, 'kernel_index': None},
        'AdditiveAttention': {'is_trainable': False, 'kernel_index': None},
        'Attention': {'is_trainable': False, 'kernel_index': None},
        'Average': {'is_trainable': False, 'kernel_index': None},
        'AveragePooling1D': {'is_trainable': False, 'kernel_index': None, "rank": 1},
        'AveragePooling2D': {'is_trainable': False, 'kernel_index': None, "rank": 2},
        'AveragePooling3D': {'is_trainable': False, 'kernel_index': None, "rank": 3},
        'BatchNormalization': {'is_trainable': False, 'kernel_index': None},
        'Concatenate': {'is_trainable': False, 'kernel_index': None},
        'Conv1D': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': 2, "rank": 1, 'enable_bigger_input_rank': True},
        'Conv2D': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': 3, "rank": 2, 'enable_bigger_input_rank': True},
        'Conv3D': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': 4, "rank": 3, 'enable_bigger_input_rank': True},
        'Conv1DTranspose': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': 1, "rank": 1, 'enable_bigger_input_rank': True},
        'Conv2DTranspose': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': 2, "rank": 2, 'enable_bigger_input_rank': True},
        'Conv3DTranspose': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': 3, "rank": 3, 'enable_bigger_input_rank': True},
        'ConvLSTM1D': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': None, "rank": 1, 'enable_bigger_input_rank': True},
        'ConvLSTM2D': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': None, "rank": 2, 'enable_bigger_input_rank': True},
        'ConvLSTM3D': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': None, "rank": 3, 'enable_bigger_input_rank': True},
        'SeparableConv1D': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': 2, "rank": 1, 'enable_bigger_input_rank': True},
        'SeparableConv2D': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': 3, "rank": 2, 'enable_bigger_input_rank': True},
        'SeparableConv3D': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': 4, "rank": 3, 'enable_bigger_input_rank': True},
        'DepthwiseConv1D': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': 2, "rank": 1, 'enable_bigger_input_rank': True},  # TODO: review
        'DepthwiseConv2D': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': 3, "rank": 2, 'enable_bigger_input_rank': True},  # TODO: review
        'DepthwiseConv3D': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': 4, "rank": 3, 'enable_bigger_input_rank': True},  # TODO: review
        'Cropping1D': {'is_trainable': False, 'kernel_index': None, "rank": 1},
        'Cropping2D': {'is_trainable': False, 'kernel_index': None, "rank": 2},
        'Cropping3D': {'is_trainable': False, 'kernel_index': None, "rank": 3},
        'Dense': {'is_trainable': True, 'filters_attr_name': 'units',  'kernel_index': 1},
        'Dot': {'is_trainable': False, 'kernel_index': None},
        'Dropout': {'is_trainable': False, 'kernel_index': None},
        'ELU': {'is_trainable': False, 'kernel_index': None},
        'Embedding': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': 0},
        'Flatten': {'is_trainable': False, 'kernel_index': None},
        'GRU': {'is_trainable': True, 'filters_attr_name': 'units',  'kernel_index': 1},
        'GRUCell': {'is_trainable': True, 'filters_attr_name': 'units',  'kernel_index': None},
        'GlobalAveragePooling1D': {'is_trainable': False, 'kernel_index': None, "rank": 1},
        'GlobalAveragePooling2D': {'is_trainable': False, 'kernel_index': None, "rank": 2},
        'GlobalAveragePooling3D': {'is_trainable': False, 'kernel_index': None, "rank": 3},
        'GlobalMaxPooling1D': {'is_trainable': False, 'kernel_index': None, "rank": 1},
        'GlobalMaxPooling2D': {'is_trainable': False, 'kernel_index': None, "rank": 2},
        'GlobalMaxPooling3D': {'is_trainable': False, 'kernel_index': None, "rank": 3},
        'LSTM': {'is_trainable': True, 'filters_attr_name': 'units',  'kernel_index': 1},
        'LSTMCell': {'is_trainable': True, 'filters_attr_name': 'units',  'kernel_index': None},
        'LayerNormalization': {'is_trainable': False, 'kernel_index': None},
        'LeakyReLU': {'is_trainable': False, 'kernel_index': None},
        'Masking': {'is_trainable': False, 'kernel_index': None},
        'MaxPooling1D': {'is_trainable': False, 'kernel_index': None, "rank": 1},
        'MaxPooling2D': {'is_trainable': False, 'kernel_index': None, "rank": 2},
        'MaxPooling3D': {'is_trainable': False, 'kernel_index': None, "rank": 3},
        'Maximum': {'is_trainable': False, 'kernel_index': None},
        'Minimum': {'is_trainable': False, 'kernel_index': None},
        'Multiply': {'is_trainable': False, 'kernel_index': None},
        'PReLU': {'is_trainable': False, 'kernel_index': None},
        'Permute': {'is_trainable': False, 'kernel_index': None},
        'RNN': {'is_trainable': False, 'kernel_index': None},
        'ReLU': {'is_trainable': False, 'kernel_index': None},
        'RepeatVector': {'is_trainable': False, 'kernel_index': None},
        'Reshape': {'is_trainable': False, 'kernel_index': None},
        'SimpleRNN': {'is_trainable': True, 'filters_attr_name': 'units',  'kernel_index': None},
        'SimpleRNNCell': {'is_trainable': True, 'filters_attr_name': 'units',  'kernel_index': None},
        'Softmax': {'is_trainable': False, 'kernel_index': None},
        'SpatialDropout1D': {'is_trainable': False, 'kernel_index': None, "rank": 1},
        'SpatialDropout2D': {'is_trainable': False, 'kernel_index': None, "rank": 2},
        'SpatialDropout3D': {'is_trainable': False, 'kernel_index': None, "rank": 3},
        'StackedRNNCells': {'is_trainable': False, 'kernel_index': None},
        'Subtract': {'is_trainable': True, 'filters_attr_name': 'filters',  'kernel_index': None},
        'ThresholdedReLU': {'is_trainable': False, 'kernel_index': None},
        'UpSampling1D': {'is_trainable': False, 'kernel_index': None, "rank": 1},
        'UpSampling2D': {'is_trainable': False, 'kernel_index': None, "rank": 2},
        'UpSampling3D': {'is_trainable': False, 'kernel_index': None, "rank": 3},
        'ZeroPadding1D': {'is_trainable': False, 'kernel_index': None, "rank": 1},
        'ZeroPadding2D': {'is_trainable': False, 'kernel_index': None, "rank": 2},
        'ZeroPadding3D': {'is_trainable': False, 'kernel_index': None, "rank": 3},
        'BinaryCrossentropy': {'is_trainable': False, 'kernel_index': None},
        'CategoricalCrossentropy': {'is_trainable': False, 'kernel_index': None},
        'CustomLoss': {'is_trainable': False, 'kernel_index': None},
        'CategoricalHinge': {'is_trainable': False, 'kernel_index': None},
        'CosineSimilarity': {'is_trainable': False, 'kernel_index': None},
        'Hinge': {'is_trainable': False, 'kernel_index': None},
        'Huber': {'is_trainable': False, 'kernel_index': None},
        'KLDivergence': {'is_trainable': False, 'kernel_index': None},
        'LogCosh': {'is_trainable': False, 'kernel_index': None},
        'MeanAbsoluteError': {'is_trainable': False, 'kernel_index': None},
        'MeanAbsolutePercentageError': {'is_trainable': False, 'kernel_index': None},
        'MeanSquaredError': {'is_trainable': False, 'kernel_index': None},
        'MeanSquaredLogarithmicError': {'is_trainable': False, 'kernel_index': None},
        'Poisson': {'is_trainable': False, 'kernel_index': None},
        'Reduction': {'is_trainable': False, 'kernel_index': None},
        'SparseCategoricalCrossentropy': {'is_trainable': False, 'kernel_index': None},
        'SquaredHinge': {'is_trainable': False, 'kernel_index': None},
        'Adadelta': {'is_trainable': False, 'kernel_index': None},
        'Adagrad': {'is_trainable': False, 'kernel_index': None},
        'Adam': {'is_trainable': False, 'kernel_index': None},
        'Adamax': {'is_trainable': False, 'kernel_index': None},
        'Ftrl': {'is_trainable': False, 'kernel_index': None},
        'Nadam': {'is_trainable': False, 'kernel_index': None},
        'RMSprop': {'is_trainable': False, 'kernel_index': None},
        'SGD': {'is_trainable': False, 'kernel_index': None},
        'Trainer': {'is_trainable': False, 'kernel_index': None},
        'Repeat': {'is_trainable': False, 'kernel_index': None},
        'MultiHeadAttention': {'is_trainable': True, 'filters_attr_name': '_key_dim', 'kernel_index': 2},
        'Gather': {'is_trainable': False, 'kernel_index': None},
        'Variable': {'is_trainable': True, 'kernel_index': None}
    }

    @staticmethod
    def get_layer_knowledge(layer_name: str):
        return Layerpedia.layer_mapping_dict.get(layer_name)
