import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
import pickle
from tensorflow.keras.models import load_model

df = pd.read_csv('./crawling_data/naver_headline_news_20240125.csv')
print(df.head())
df.info()

X=df['titles']
Y=df['category']

with open ('./models/label_encoder.pickle', 'rb') as f:
    label_encoder = pickle.load(f)

label = label_encoder.classes_
print(label)

okt =Okt()

for i in range(len(X)):
    X[i] = okt.morphs(X[i], stem=True)



stopwords = pd.read_csv('./stopwords.csv', index_col=0)
for j in range(len(X)): #문장
    words = []
    for i in range(len(X[j])): #문장 내용 접근
        if len(X[j][i]) > 1: #단어가 한글자 보다 길면
            if X[j][i] not in list(stopwords['stopword']):
                words.append(X[j][i])
    X[j] = ' '.join(words)
#print(X[:5])
with open('./models/news_token.pickle', 'rb') as f:
    token = pickle.load(f)

tokened_x = token.texts_to_sequences(X) # 실제 단어들을 숫자로 이루어진 리스트로 바꿔줌.
for i in range(len(tokened_x)):
    if len(tokened_x[i]) > 27:
        tokened_x[i] = tokened_x[i][:27]

print(tokened_x)

x_pad = pad_sequences(tokened_x, 27)

model = load_model('./models/news_category_classification_model_0.9957272410392761.h5')
preds = model.predict(x_pad)

predicts = []
for pred in preds:
    most = label[np.argmax(pred)]
    pred[np.argmax(pred)] = 0
    second = label[np.argmax(pred)]
    predicts.append([most, second])
df['predict'] = predicts

print(df)

df['OX'] = 0
for i in range(len(df)):
    if df.loc[i, 'category'] in df.loc[i, 'predict']:
        df.loc[i, 'OX'] = 'O'
    else : df.loc[i, 'OX'] = 'X'

print(df['OX'].value_counts())
print(df['OX'].value_counts()/len(df))

