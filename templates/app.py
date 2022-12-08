# Importing essential libraries
from flask import Flask, request, render_template
import pickle
import nltk
import re 
import os
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
nltk.download('stopwords')

basedir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(basedir, 'model')
pkl_file = os.path.join(model_path, 'models.pkl')
load_model = pickle.load(open(pkl_file, 'rb'))
classifier = load_model['model']
cv = load_model['vectorizer']


import ssl
try:
     _create_unverified_https_context =     ssl._create_unverified_context
except AttributeError:
     pass
else:
    ssl._create_default_https_context = _create_unverified_https_context



# Load the Decision Tree classifier model and CountVectorizer object from disk
# filename = 'DTC1.pkl'
# classifier = pickle.load(open(filename, 'rb'))
# cv = pickle.load(open('cv1-transform1.pkl','rb'))


def predict_review(sample_message, classifier):    
     sample_message = re.sub(pattern='[^a-zA-Z]',repl=' ', string = sample_message)
     sample_message = sample_message.lower()
     sample_message_words = sample_message.split()
     sample_message_words = [word for word in sample_message_words if not word in set(stopwords.words('english'))]
     ps = PorterStemmer()
     final_message = [ps.stem(word) for word in sample_message_words]
     final_message = ' '.join(final_message)
     temp = cv.transform([final_message]).toarray()
     return classifier.predict(temp)

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/result', methods=['POST'])
def predict():
    if request.method == 'POST':
        message = request.form["message"]
        if not message == "":
            if predict_review(message, classifier):
                return render_template('index.html', result = 'Great! Positive Review', message = message) #positive
            else:
                return render_template('index.html', result = 'Ohhh No! Negetive Review', message = message) #negative
        else:
            return render_template('index.html')
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)