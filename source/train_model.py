import time
import glob
import keras
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image

import brain_model


def load_training_data():

	X = [] # Images
	y = [] # (left velocity, right velocity)
	
	filenames = glob.glob( "memories/*.jpg" )
	for filename in filenames:
		image = Image.open( filename )
		image_array = np.array( image )
		X.append( image_array )
		y.append( ( 0, 1 ) )	

	filenames = glob.glob( "memories2/*.jpg" )
	for filename in filenames:
		image = Image.open( filename )
		image_array = np.array( image )
		X.append( image_array )
		y.append( ( 1, 0 ) )	

	return np.array(X), np.array(y)

def train():

	model = brain_model.model()

	callbacks = [
		keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, verbose=0),
		keras.callbacks.ModelCheckpoint("best_brain.model", monitor='val_loss', save_best_only=True, verbose=0)
	]

	# Load training data
	X, y = load_training_data()
	print( "Found %d memories" % len(X) )

	# Train!
	history = model.fit(X, y, epochs=20, batch_size=10, validation_split=0.2, callbacks=callbacks)

	model.save( "brain.model" )


train()

