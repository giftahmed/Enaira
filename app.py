from flask import Flask, request, render_template
from sklearn.feature_extraction.text import TfidfVectorizer 
import database_init
import pickle
import nltk
import re 
import os
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


conn, cur = database_init.get_connection()

nltk.download('stopwords')
basedir = os.path.dirname(os.path.abspath(__file__))
# # model_path = os.path.join(basedir, 'model')
# pkl_file_model = os.path.join(basedir, 'DTC1.pkl')
# pkl_file_cv = os.path.join(basedir, 'vectors.pkl')
# model = pickle.load(open(pkl_file_model, 'rb'))
# cv = TfidfVectorizer() 


basedir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(basedir, 'model')
pkl_file = os.path.join(model_path, 'models.pkl')
load_model = pickle.load(open(pkl_file, 'rb'))
model = load_model['model']
cv = load_model['vectorizer']



def cleardb():
    conn.execute("DELETE FROM movieReview")
    conn.commit()
    pass

# with open("models.pkl",'rb') as f:
 #       pkl = pickle._Unpickler(f)
  #      pkl.encoding = 'latin1'
   #     model = pkl.load()
    #    cv = pickle.load(open('vectorizer'))
        
#with open("models.pkl",'rb') as f:
 #        load_model = pickle.load(open(pkl_file,
  #       classifier = load_model['model']
   #      cv = load_model['vectorizer']    
   

        

def sentiment_review(sample_message, model):
    if sample_message is None or sample_message == "":
        return "Try again"
    sample_message = re.sub(pattern='[^a-zA-Z]',repl=' ', string = sample_message)
    sample_message = sample_message.lower()
    sample_message_words = sample_message.split()
    sample_message_words = [word for word in sample_message_words if not word in set(stopwords.words('english'))]
    ps = PorterStemmer()
    final_message = [ps.stem(word) for word in sample_message_words]
    final_message = ' '.join(final_message)
    temp = cv.transform([final_message]).toarray()
    pred = model.predict(temp)
    if pred[0] == 0:
        return "Negative"
    else:
        return "Positive"



def insert_into_db(movie_review,pred):
    cur.execute("INSERT INTO movieReview (Review, Prediction) VALUES (?, ?)",(movie_review,pred))
    conn.commit()
    id = conn.execute('SELECT last_insert_rowid()').fetchall()[0]
    return id


app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/results.html',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        print(request.form['message'])
        prediction = sentiment_review(request.form['message'],model)
        id = insert_into_db(request.form['message'],prediction)
        id = id[0]
        if not prediction == "":
            output = sentiment_review(prediction, model)[0]
            if output.lower() == 'positive':
                return render_template('index.html', result = 'Great! Positive Review', message = prediction) #positive
            else:
                return render_template('index.html', result = 'Ohhh No! Negetive Review', message = prediction) #negative
        else:
            return render_template('index.html')
    else:
        return render_template('index.html')

if __name__ == "_main_":
    app.run(debug=True)



