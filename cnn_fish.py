# -*- coding: utf-8 -*-
"""CNN_fish.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10OuSHiiUI7W2bk9e6KYPC1WaGn4YJkme
"""

from matplotlib import pyplot as plt
import numpy as np
import tensorflow as tf
import seaborn as sns # in case
import cv2
import os
import rarfile
import pickle

from joblib import load as joblibLoad
from joblib import dump as joblibdump

from tensorflow.keras import layers, models, optimizers, losses, metrics
from tensorflow.keras.preprocessing.image import ImageDataGenerator

import os
from sklearn.model_selection import train_test_split
import shutil

source_directory = 'C:\\Users\\thedu\\OneDrive\\Documents\\machine_learning\\CNN_dataset\\extracted_folder\\'

train_dir = './train/'
test_dir = './test/'
val_dir = './validation/'

os.makedirs(train_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)

class_directories = [os.path.join(source_directory, f) for f in os.listdir(source_directory)]

for class_dir in class_directories:
    class_name = os.path.basename(class_dir)

    os.makedirs(os.path.join(train_dir, class_name), exist_ok=True)
    os.makedirs(os.path.join(test_dir, class_name), exist_ok=True)
    os.makedirs(os.path.join(val_dir, class_name), exist_ok=True)

    images = [os.path.join(class_dir, img) for img in os.listdir(class_dir)]

    train_images, test_val_images = train_test_split(images, test_size=0.2, random_state=42)
    test_images, val_images = train_test_split(test_val_images, test_size=0.5, random_state=42)

    for img in train_images:
        shutil.copy(img, os.path.join(train_dir, class_name, os.path.basename(img)))

    for img in test_images:
        shutil.copy(img, os.path.join(test_dir, class_name, os.path.basename(img)))

    for img in val_images:
        shutil.copy(img, os.path.join(val_dir, class_name, os.path.basename(img)))

train_datagen = ImageDataGenerator(rescale=1./255)
val_datagen = ImageDataGenerator(rescale=1./255)

train_dataset = train_datagen.flow_from_directory(
    'C:\\Users\\thedu\\OneDrive\\Documents\\machine_learning\\CNN_dataset\\train',
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    color_mode='rgb',
    seed=42
)

val_dataset = train_datagen.flow_from_directory(
    'C:\\Users\\thedu\\OneDrive\\Documents\\machine_learning\\CNN_dataset\\validation',
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    color_mode='rgb',
    seed=42
)

test_dataset = train_datagen.flow_from_directory(
    'C:\\Users\\thedu\\OneDrive\\Documents\\machine_learning\\CNN_dataset\\test',
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    color_mode='rgb',
    seed=42
)

test_dataset.image_shape

def create_model(activation, dimension):
    model = models.Sequential()
    model.add(layers.InputLayer(dimension))

    # New architecture with 3 layers
    model.add(layers.Conv2D(64, 3, activation=activation, padding='same'))
    model.add(layers.MaxPooling2D(pool_size=2, padding='valid'))

    model.add(layers.Conv2D(128, 3, activation=activation, padding='same'))
    model.add(layers.MaxPooling2D(pool_size=2, padding='valid'))

    model.add(layers.Conv2D(256, 3, activation=activation, padding='same'))
    model.add(layers.MaxPooling2D(pool_size=2, padding='valid'))

    # Flatten
    model.add(layers.Flatten())

    # FCN
    model.add(layers.Dense(256, activation=activation))
    model.add(layers.Dropout(0.3))
    model.add(layers.Dense(256, activation=activation))
    model.add(layers.Dropout(0.3))

    # Output
    model.add(layers.Dense(8, activation='softmax'))

    model.summary()
    model.compile(
        optimizer=optimizers.Adam(learning_rate=0.0001),
        loss=losses.CategoricalCrossentropy(from_logits=False),
        metrics=[
            metrics.CategoricalAccuracy(),
            metrics.Recall(),
            metrics.Precision(),
            metrics.AUC(),
            metrics.TruePositives(),
            metrics.TrueNegatives(),
            metrics.FalseNegatives(),
            metrics.FalsePositives()
        ]
    )

    return model

model = create_model('relu',train_dataset.image_shape)

history = model.fit(
    train_dataset,
    steps_per_epoch=train_dataset.samples // train_dataset.batch_size,
    epochs=30,
    validation_data=val_dataset,
    validation_steps=val_dataset.samples // val_dataset.batch_size
)

# Save the training history to a file
history_file_path = 'C:\\Users\\thedu\\OneDrive\\Documents\\machine_learning\\CNN_dataset\\results\\history_DL_example.pkl'
with open(history_file_path, 'wb') as file:
    pickle.dump(history.history, file)

# Save the model in the native Keras format
model_file_path = 'C:\\Users\\thedu\\OneDrive\\Documents\\machine_learning\\CNN_dataset\\results\\DL_example'
model.save(model_file_path)

# Load the training history from the file
with open(history_file_path, 'rb') as f:
    history = pickle.load(f)

print(history)

from matplotlib import pyplot as plt

plt.plot(history['loss'])

plt.plot(history['categorical_accuracy'])

plt.plot(history['recall_27'])

plt.plot(history['auc_8'])

plt.plot(history['precision_27'])

def get_best_epoch(history):
    max_precision_epoch = history['precision_27'].index(max(history['precision_27'])) + 1
    max_recall_epoch = history['recall_27'].index(max(history['recall_27'])) + 1
    best_epoch = min(max_precision_epoch, max_recall_epoch)
    precision_at_best_epoch = history['precision_27'][best_epoch - 1]
    recall_at_best_epoch = history['recall_27'][best_epoch - 1]
    f1_score = 2 * (precision_at_best_epoch * recall_at_best_epoch) / (precision_at_best_epoch + recall_at_best_epoch)
    print("Best epoch with highest precision and recall:", best_epoch)
    print("Precision at best epoch:", precision_at_best_epoch)
    print("Recall at best epoch:", recall_at_best_epoch)
    print(f"F1 Score: {f1_score}")


get_best_epoch(history)