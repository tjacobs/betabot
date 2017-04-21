from keras.models import Sequential
from keras.layers import Convolution2D, Dense, Activation, Flatten, Lambda, ELU, Dropout


def model():

	row, col, ch = 160, 120, 3

	# The model
	model = Sequential()
	model.ch_order = 'channel_first'
	model.add(Lambda(lambda x: x/127.5 - 1.0,
			input_shape=(col, row, ch),
			output_shape=(col, row, ch)))
	model.add(Convolution2D(24, kernel_size=(5, 5), strides=(2, 2), padding="same"))
	model.add(ELU())
	model.add(Convolution2D(36, kernel_size=(5, 5), strides=(2, 2), padding="same")) 
	model.add(ELU())
	model.add(Convolution2D(48, kernel_size=(3, 3), strides=(2, 2), padding="same"))
	model.add(ELU()) 
	model.add(Convolution2D(64, kernel_size=(3, 3), strides=(2, 2), padding="same"))
	model.add(Flatten())
	model.add(Dropout(.2)) 
	model.add(ELU())
	model.add(Dense(512))
	model.add(Dropout(.5)) 
	model.add(ELU())
	model.add(Dense(256))
	model.add(ELU()) 
	model.add(Dense(128))
	model.add(ELU())
	model.add(Dense(2))

	# Build and return it
	model.compile(optimizer="adam", loss="mse")
	return model

