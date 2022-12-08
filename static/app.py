from flask import Flask, request, render_template
from sklearn.feature_extraction.text import TfidfVectorizer 
import pickle
import nltk
import re 
import os
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import database_init


conn, cur = database_init.get_connection()

nltk.download('stopwords')
basedir = os.path.dirname(os.path.abspath(__file__))
# model_path = os.path.join(basedir, 'model')
pkl_file_model = os.path.join(basedir, 'DTC1.pkl')
pkl_file_cv = os.path.join(basedir, 'vectors.pkl')
classifier = pickle.load(open(pkl_file_model, 'rb'))
cv = TfidfVectorizer() 



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
@app.route("/index.html")
def index():
    return render_template('index.html')

@app.route('/results.html',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        print(request.form['result'])
        prediction = sentiment_review(request.form['result'])
        id = insert_into_db(request.form['result'],prediction)
        id = id[0]
        if prediction=='Positive':
            linker = "https://www.flaticon.com/svg/static/icons/svg/25/25297.svg"
        else:
            linker = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTQGrMjs792Df4SLOoJT2M0W1VHhK5f5JnlYg&usqp=CAU"
        return render_template('results.html', value=prediction, linker=linker, id=id)

@app.route('/reviews.html')
def reviews():
    movieReview = conn.execute('SELECT * FROM movieReview').fetchall()
    return render_template('reviews.html', posts=movieReview)

@app.route('/thanks.html',methods=['GET', 'POST'])
def thanks():
    print(100)
    if request.method == 'POST':
        cur.execute("UPDATE movieReview SET Userfeedback = ? WHERE ID = ?",(request.form['option'], request.form['ID']))
        conn.commit()  
    return render_template('thanks.html')

@app.route("/")
@app.route("/admin/index.html")
def indexa():
    return render_template('/admin/index.html')

@app.route('/results.html',methods = ['POST', 'GET'])


def resulta():
    if request.method == 'POST':
        print(request.form['admin/result'])
        prediction = sentiment_review(request.form['result'])
        id = insert_into_db(request.form['result'],prediction)
        id = id[0]
        if prediction=='Positive':
            linker = "https://www.flaticon.com/svg/static/icons/svg/25/25297.svg"
        else:
            linker = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTQGrMjs792Df4SLOoJT2M0W1VHhK5f5JnlYg&usqp=CAU"
        return render_template('results.html', value=prediction, linker=linker, id=id)

@app.route('/admin/reviews.html')
def reviewsa():
    movieReview = conn.execute('SELECT * FROM movieReview').fetchall()
    return render_template('reviews.html', posts=movieReview)

@app.route('/thanks.html',methods=['GET', 'POST'])
def thanksa():
    print(100)
    if request.method == 'POST':
        cur.execute("UPDATE movieReview SET Userfeedback = ? WHERE ID = ?",(request.form['option'], request.form['ID']))
        conn.commit()  
    return render_template('thanks.html')

if __name__ == "_main_":
    app.run(debug=True)
