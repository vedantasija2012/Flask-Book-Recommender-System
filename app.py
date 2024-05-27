from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pickle
import numpy as np

popular_df = pickle.load(open('./cosine_similarity/popular.pkl', 'rb'))
pt = pickle.load(open('./cosine_similarity/pt.pkl', 'rb'))
books = pickle.load(open('./cosine_similarity/books.pkl', 'rb'))
similarity_scores = pickle.load(open('./cosine_similarity/similarity_scores.pkl', 'rb'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book-recommender.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'mySecretKey'
db = SQLAlchemy(app)
is_user_logged_in = False

class User(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self) -> str:
        return f"{self.sno} - {self.username} - {self.password}"

def initialise_database():
    with app.app_context():
        db.create_all()

@app.route("/")
def index():
    if session.get('is_user_logged_in'):
        success_message = session.pop('success_message', None)
        return render_template('index.html', is_user_logged_in=True, success_message=success_message)
    else:
        return redirect('/login')

@app.route("/about")
def about():
    return render_template('about.html', 
    book_name = list(popular_df['Book-Title'].values),
    author = list(popular_df['Book-Author'].values),
    image = list(popular_df['Image-URL-M'].values),
    votes = list(popular_df['num_ratings'].values),
    rating = list(popular_df['avg_rating'].values),
    )

@app.route('/feedback', methods=["POST", "GET"])
def feedback():
    if request.method=="POST":
        username = request.form.get('name')
        email = request.form.get('email')
        feedback = request.form.get('feedback')
        if username=="" or email=="":
            flash("Enter Valid Credentials!", "warning")
            return redirect("/feedback")
        if feedback=="":
            flash("Enter Valid Query!", "warning")
            return redirect("/feedback")
        flash("Feedback Submitted Successfully!", "success")

    return render_template('feedback.html')

# username: user1
# password: password1
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=="POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if username=="" or password=="":
            flash("Please Enter Valid Username or Password", "warning")
            return redirect('/login')
            
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['is_user_logged_in']=True
            flash(f"Welcome Back! {username}", "success")
            session['success_message'] = f"Welcome Back! {username}"
            return redirect('/')
        else:
            flash("Invalid Username or Password. Try Again!", "danger")
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        if username=="" or password=="":
            return "Please Enter Valid Username or Password"
        
        # creating users and saving to database
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return 'User Registered Successfully!'
    return render_template('signup.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/search', methods=['post', 'get'])
def search():
    title = request.form.get('book_title')
    if title is not None:
        index = np.where(pt.index==title)[0][0]
    else:
        index = np.where(pt.index==title)[0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        
        data.append(item)

    print(data)
    return render_template('search.html', data=data)

@app.route('/search', methods=['post', 'get'])
def recommend(book_name):
    # index fetch
    index = np.where(pt.index==book_name)[0]
    similar_items = sorted(list(enumerate(similarity_scores[index])),key=lambda x:x[1],reverse=True)[1:5]
    
    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        
        data.append(item)
    return render_template('search.html', data=data)

if __name__=="__main__":
    initialise_database()
    app.run(debug=True)