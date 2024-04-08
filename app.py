from flask import Flask, render_template, request
import pickle
import numpy as np
import difflib

popular_movies = pickle.load(open('popular_movies1.pkl', 'rb'))
transf = pickle.load(open('transf1.pkl', 'rb'))
books = pickle.load(open('books1.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores1.pkl', 'rb'))

app = Flask(__name__)


def find_book_index(book_name):
    # Convert all book names to lowercase for case-insensitive comparison
    lower_case_book_names = [name.lower() for name in transf.index]

    # Find closest match using difflib
    match = difflib.get_close_matches(book_name.lower(), lower_case_book_names, n=1, cutoff=0.8)

    # If a close match is found, return its index
    if match:
        return lower_case_book_names.index(match[0])
    else:
        return None


@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_movies['Book-Title'].values),
                           author=list(popular_movies['Book-Author'].values),
                           image=list(popular_movies['Image-URL-M'].values),
                           votes=list(popular_movies['num_votes'].values),
                           rating=list(popular_movies['avg_rating'].values),
                           isbn=list(popular_movies['ISBN'].values)
                           )


@app.route('/recommend')
def recommend():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=['POST'])
def recommend_books():
    user_input = request.form.get('user_input')

    # Find the index of the book (case-insensitive and approximate match)
    ind = find_book_index(user_input)

    if ind is None:
        return "Book not found. Please enter a valid book name."

    similar_mov = sorted(list(enumerate(similarity_scores[ind])), key=lambda x: x[1], reverse=True)[1:6]
    data = []
    for i in similar_mov:
        item = []
        temp_df = books[books['Book-Title'] == transf.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        data.append(item)
    return render_template('recommend.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
