from flask import Flask, render_template, request
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import pickle
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# Load your dataset
books_df = pickle.load(open('books.pkl', 'rb'))

# Assuming 'isbn' and 'title' columns in your dataset
knn_data = books_df[['isbn', 'title']]

# Convert categorical data to numeric data
le = LabelEncoder()
knn_data['isbn'] = le.fit_transform(knn_data['isbn'])
knn_data['title'] = le.fit_transform(knn_data['title'])

# Fit the KNN model
knn_model = NearestNeighbors(n_neighbors=5, algorithm='auto').fit(knn_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/search', methods=['POST', 'GET'])
def recommend():
    book_title = request.form.get('book_title')
    print("book_title: ", book_title)

    # Assuming 'title' column in your dataset
    book_index = books_df[books_df['title'].str.lower() == book_title.lower()].index
    if not book_index.empty:
        book_index = book_index[0]

        # Find nearest neighbors for the selected book
        _, indices = knn_model.kneighbors(knn_data.loc[[book_index]])

        # Get recommended book titles
        recommended_books = knn_data.loc[indices[0]]['title'].tolist()

        return render_template('recommend.html', recommended_books=recommended_books)
    else:
        return render_template('recommend.html', recommended_books=['Book Not Found'])

if __name__ == '__main__':
    app.run(debug=True)