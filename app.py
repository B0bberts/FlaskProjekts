from flask import Flask, render_template, request, redirect, url_for
from peewee import SqliteDatabase, Model, CharField, IntegerField, FloatField
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Izveidojam datubāzi
db = SqliteDatabase('movies.db')

class Movie(Model):
    title = CharField()
    year = IntegerField()
    genre = CharField()
    rating = FloatField()
    views = IntegerField()

    class Meta:
        database = db

db.connect()
db.create_tables([Movie], safe=True)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/movies')
def movies():
    genre_filter = request.args.get('genre')
    if genre_filter:
        filtered_movies = Movie.select().where(Movie.genre == genre_filter)
    else:
        filtered_movies = Movie.select()

    genres = list(set(movie.genre for movie in Movie.select()))
    return render_template('movies.html', movies=filtered_movies, genres=genres, selected_genre=genre_filter)


@app.route('/visualize')
def visualize():
    movies = pd.DataFrame(list(Movie.select().dicts()))

    # Izveidojam reitingu histogrammu
    plt.figure(figsize=(8, 6))
    sns.histplot(movies['rating'], bins=10, kde=True)
    plt.xlabel('IMDb Reitings')
    plt.ylabel('Filmu skaits')
    plt.title('Filmu reitingu sadalījums')
    plt.savefig('static/rating_distribution.png')
    plt.close()

    # Izveidojam žanru sadalījuma joslu diagrammu
    plt.figure(figsize=(8, 6))
    sns.countplot(y=movies['genre'], order=movies['genre'].value_counts().index)
    plt.xlabel('Filmu skaits')
    plt.ylabel('Žanrs')
    plt.title('Filmu žanru sadalījums')
    plt.savefig('static/genre_distribution.png')
    plt.close()

    return render_template('visualize.html')
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join('uploads', file.filename)
            file.save(filepath)
            data = pd.read_csv(filepath)
            for _, row in data.iterrows():
                Movie.create(
                    title=row['Title'],
                    year=row['Year'],
                    genre=row['Genre'],
                    rating=row['Rating'],
                    views=row['Views']
                )
            return redirect(url_for('movies'))
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
