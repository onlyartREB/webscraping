
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import recall_score,precision_score,f1_score

DATA_JSON_FILE = 'DATASET.json'
data = pd.read_json(DATA_JSON_FILE)
data.tail()
print(data)

vectorizer = CountVectorizer(stop_words='french')
all_features = vectorizer.fit_transform(data.text)

all_features.shape
vectorizer.vocabulary_

X_train, X_test, y_train, y_test = train_test_split(all_features,
data.CATEGORY,test_size=0.3, random_state=88)
X_train.shape
X_test.shape
classifer= MultinomialNB()
classifer.fit(X_train,y_train)

nr_correct =  (y_test == classifer.predict(X_test)).sum()
#classifer.predict(X_test)
print(f'{nr_correct} documents classified correctly')

nr_incorrect = y_test.size - nr_correct
print(f'Number of dccuments incorrectly classified is (nr_incorrect')
fraction_wrong = nr_incorrect / (nr_correct + nr_incorrect)
print(f'The (testing) accuracy of the model is {l-fraction_wrong:.2%}')

recall_score(y_test, classifer.predict(X_test))
precision_score(y_test, classifer.predict(X_test))
f1_score(y_test, classifer.predict(X_test))
