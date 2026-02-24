import numpy as np
import joblib

from sklearn.feature_extraction.text import CountVectorizer
import tensorflow as tf

Sequential = tf.keras.models.Sequential
Dense = tf.keras.layers.Dense
to_categorical = tf.keras.utils.to_categorical

# -------- Dataset --------
data = [
"hello world",
"normal login",
"view page",

"' OR 1=1 --",
"SELECT * FROM users",
"DROP TABLE students",

"<script>alert(1)</script>",
"<img src=x onerror=alert(1)>"
]

labels = [
0,0,0,      # Normal
1,1,1,      # SQL
2,2         # XSS
]

# -------- Vectorize --------
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(data).toarray()

y = to_categorical(labels)

# -------- Neural Network --------
model = Sequential()
model.add(Dense(32, activation='relu', input_dim=X.shape[1]))
model.add(Dense(16, activation='relu'))
model.add(Dense(3, activation='softmax'))

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# -------- Train --------
model.fit(X, y, epochs=50, verbose=0)

# -------- Save --------
model.save("ai/deep_model.h5")
joblib.dump(vectorizer, "ai/vectorizer.pkl")

print("Deep model trained!")