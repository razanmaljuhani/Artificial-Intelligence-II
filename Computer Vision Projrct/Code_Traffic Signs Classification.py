# -*- coding: utf-8 -*-
"""CPCS-432 - Project Code - Group No.3 - Traffic Signs Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ftSWMaUR_bbrqj2QHX86oJCFGK2i15bY
"""

#Import the libraries
import os
import glob
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

import tensorflow as tf

TEST_SIZE=0.1
SEED=0
BATCH_SIZE=64

#Initialize the random number generator; the random number generator needs a number to start with (a seed value), to be able to generate a random number
tf.random.set_seed(SEED)

#Mount the Google Drive to Google Colab
from google.colab import drive
drive.mount('/content/drive/')

#Upload the dataset label
labels_df = pd.read_csv('/content/drive/MyDrive/archive/labels.csv')
print(labels_df.sample(10))

#Create a label map
label_map = dict(labels_df.values)
print(label_map)

#Upload the dataset
image_list = list(Path('/content/drive/MyDrive/archive/traffic_Data/DATA').glob(r'**/*.png'))
labels = list(map(lambda path: os.path.split(os.path.split(path)[0])[1], image_list))

#Create dataframe with path of images and labels
image_series = pd.Series(image_list).astype(str)
labels_series = pd.Series(labels).astype(str)
frame = {'image':image_series, 'label':labels_series}
image_df = pd.DataFrame(frame)
image_df.info()
print(image_df.sample(5))

#Plot to show the number of images for each label
count_labels = image_df.groupby(['label']).size()
plt.figure(figsize=(17,5))
plt.ylabel('count images')
sns.barplot(x=count_labels.index, y=count_labels, palette="rocket")

"""Some labels contain very few image instances. If you apply random partitioning to training and validation, there is a chance that the training set will not reflect the entire general population. Let's split into training and validation only for the part where the number of image instances is higher than SPLIT_MINIMUM_COUNT"""

SPLIT_MINIMUM_COUNT = 10

#Splitting the dataset

#Allocate a  dataset that has at least SPLIT_MINIMUM_COUNT_IMAGES of images
#split_df: dataframe for train
#train1_df: dataframe for drop
def split_dataset(df, rate=SPLIT_MINIMUM_COUNT):

  count_labels = df.groupby(['label']).size()
  count_labels_df = count_labels.to_frame(name='count_images').reset_index()

  drop_label_list = list(
      count_labels_df['label'].\
      loc[count_labels_df['count_images']<SPLIT_MINIMUM_COUNT]
  )

  drop_df = df.copy()
  split_df = df.copy()

  for index, row in df.iterrows():
    if str(row.label) in drop_label_list:
      split_df = split_df.drop(index)
    else:
      drop_df = drop_df.drop(index)

  return split_df, drop_df


#Train test split where test_df has minimum 1 image in all labels in random split. 
def custom_train_test_split(df):
  
    labels = df.label.unique()
    print(labels)
    test_df = pd.DataFrame()

    for label in labels:
      label_samples = df.loc[df.label==label]
      test_df = test_df.append(label_samples.sample(len(label_samples)//10+1,
                               random_state=SEED))
    
    train_df = df.drop(list(test_df.index), axis=0)
    test_df = test_df.sample(frac=1, random_state=SEED)
    train_df = train_df.sample(frac=1, random_state=SEED)

    return train_df, test_df

#Splitting the dataset
split_df, _ = split_dataset(image_df)
train_df, test_df = custom_train_test_split(split_df)
train, val = custom_train_test_split(train_df)

#Count the number of the classes
train_labels = train_df.groupby(['label']).size()
NUM_CLASSES = len(train_labels)

#Plot samples from the train dataset
fig, axes = plt.subplots(2,4, figsize=(16, 7))
for idx, ax in enumerate(axes.flat):
    ax.imshow(plt.imread(train_df.image.iloc[idx]))
    ax.set_title(train_df.label.iloc[idx])
plt.tight_layout()
plt.show()

"""Train model (Transfer Learning)"""

train_generator = tf.keras.preprocessing.image.ImageDataGenerator(
    preprocessing_function=tf.keras.applications.efficientnet.preprocess_input,
    rotation_range = 10,
    width_shift_range=0.2,
    height_shift_range=0.2,
    fill_mode='constant',
    shear_range=0.1,
    zoom_range=0.2,
)

test_generator = tf.keras.preprocessing.image.ImageDataGenerator(
    preprocessing_function=tf.keras.applications.efficientnet.preprocess_input,
)

#Define the dataframe for each set

train_images = train_generator.flow_from_dataframe(
    dataframe=train_df,
    x_col='image',
    y_col='label',
    color_mode='rgb',
    class_mode='categorical',
    target_size=(128, 128),
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=SEED,
)

val_images = test_generator.flow_from_dataframe(
    dataframe=val,
    x_col='image',
    y_col='label',
    color_mode='rgb',
    class_mode='categorical',
    target_size=(128, 128),
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=SEED,
)


test_images = test_generator.flow_from_dataframe(
    dataframe=test_df,
    x_col='image',
    y_col='label',
    color_mode='rgb',
    class_mode='categorical',
    target_size=(128, 128),
    batch_size=BATCH_SIZE,
   
)

#Create the model
def create_model(input_shape=(128,128,3)):

#Load EfficientNet without last layer and add Dense and ouput Dense with NUM_CLASSES units

  inputs = tf.keras.layers.Input(input_shape)

  base_model = tf.keras.applications.EfficientNetB0(
      include_top=False,
      weights='imagenet',
      pooling='avg'
  )
  base_model.trainable = False
  
  x = base_model(inputs)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.Dense(512, activation='relu')(x)
  #x = tf.keras.layers.Dropout(0.2)(x)
  #x = tf.keras.layers.Dense(256, activation='relu')(x)
  outputs = tf.keras.layers.Dense(NUM_CLASSES, activation='softmax')(x)

  return tf.keras.models.Model(inputs, outputs)

model = create_model()

#Compile the mdoel to define the loss function, the optimizer and the metrics
model.compile(
    optimizer='Adam',
    loss='categorical_crossentropy',
    metrics=['acc'],
)

callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3, restore_best_weights=True)

#Fitting the model on the dataset
history = model.fit(
    train_images,
    epochs=40,
    validation_data=val_images,
    callbacks=[callback]
)

#Plotting the train and the validation accuracy per each epoch
plt.figure(figsize=(12,5))
plt.plot(history.history['acc'], label='train_acc')
plt.plot(history.history['val_acc'], label='val_acc')
plt.title('Accuracy plot')
plt.xlabel('epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

#Plotting the train and the validation loss per each epoch
plt.figure(figsize=(12,5))
plt.plot(history.history['loss'], label='train_loss')
plt.plot(history.history['val_loss'], label='val_loss')
plt.title('Loss plot')
plt.xlabel('epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

#Plotting the train validation accuracy per each epoch
plt.figure(figsize=(12,5))
plt.plot(history.history['val_acc'], label='val_acc')
plt.title('Validation accuracy')
plt.xlabel('epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

#Plotting the train validation loss per each epoch
plt.figure(figsize=(12,5))
plt.plot(history.history['val_loss'], label='loss_acc')
plt.title('Validation loss')
plt.xlabel('epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

from pandas._libs.tslibs.conversion import precision_from_unit
#Score and accuracy of the testing set
score, accuracy = model.evaluate(test_images)
print(f'Test score: {round(score,4)}, Test accuracy: {round(accuracy,4)}')

#Test dataframe
test_df

#Traffic signs prediction
im = Image.open("/content/drive/MyDrive/archive/traffic_Data/DATA/22/022_1_0001.png")
im = im.resize((128,128))
im_array = np.array(im)
im_array = np.expand_dims(im_array, axis = 0)
pred = model.predict(im_array)
print(pred)
pred_labels = tf.argmax(pred, axis = -1)
print(pred_labels)

#The predicted label of the image
pred_labels = tf.argmax(pred, axis = -1)
print(pred_labels)

#Predict the label of the testing set
pred=model.predict(test_images)
print(pred)


pred_labels = tf.argmax(pred, axis = -1)
print(pred_labels)

#The label of the testing dataset
test_labels= test_df.label
print(test_labels)