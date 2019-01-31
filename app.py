from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'imdb_data'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/imdb_data'

mongo = PyMongo(app)

@app.route('/movie', methods=['GET'])
def get_all_movies():
  movies = mongo.db.movies_data
  output = []
  for movie in movies.find({}):
      output.append({
                'movie_id' : movie['movie_id'],
                'title' : movie['title'],
                'year' : movie['year'],
                'genres' : movie['genres'],
                'imdb_rating' : movie['imdb_rating'],
                'metascore' : movie['metascore'],
                'directors_ids' : movie['directors_ids'],
                'imdb_rating' : movie['imdb_rating'],
                'runtime' : movie['runtime'],
                'budget' : movie['budget'],
                'countrys' : movie['countrys']
                })
  return jsonify({'result' : output})

@app.route('/movie/<id>', methods=['GET'])
def get_one_movie(id):
  movies = mongo.db.movies_data
  movie = movies.find_one_or_404({'movie_id' : id})
  output = {
            'movie_id' : movie['movie_id'],
            'title' : movie['title'],
            'year' : movie['year'],
            'genres' : movie['genres'],
            'imdb_rating' : movie['imdb_rating'],
            'metascore' : movie['metascore'],
            'directors_ids' : movie['directors_ids'],
            'imdb_rating' : movie['imdb_rating'],
            'runtime' : movie['runtime'],
            'budget' : movie['budget'],
            'countrys' : movie['countrys']
            }
  return jsonify({'result' : output})

@app.route('/director', methods=['GET'])
def get_all_directors():
  directors = mongo.db.directors_data
  output = []
  for director in directors.find({}):
      output.append({
                'id' : director['id'],
                'name' : director['name'],
                'born_date' : director['born_date'],
                'nationality' : director['nationality'],
                'gender' : director['gender'],
                })
  return jsonify({'result' : output})

@app.route('/director/<id>', methods=['GET'])
def get_one_director(id):
   directors = mongo.db.directors_data
   director = directors.find_one_or_404({'id' : id})
   output = {
             'id' : director['id'],
             'name' : director['name'],
             'born_date' : director['born_date'],
             'nationality' : director['nationality'],
             'gender' : director['gender'],
             }
   return jsonify({'result' : output})

if __name__ == '__main__':
    app.run(debug=True)
