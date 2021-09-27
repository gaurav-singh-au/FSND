import os
import sys
from flask import Flask, request, jsonify, abort, render_template
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Actor, Movie
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Headers',
#                           'Content-Type,Authorization,true')
#     response.headers.add('Access-Control-Allow-Methods',
#                           'GET,PUT,POST,DELETE,OPTIONS')
#     return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()


# ROUTES
'''
    GET /movies
        it should be a public endpoint
        it should contain only the movie.short() data representation
    returns status code 200 and json {"success": True, "movies": movies} where
    movies is the list of movies or appropriate status code indicating reason
    for failure
'''


@app.route('/movies', methods=['GET'])
def getAllMovies():
    movies = [movie.short() for movie in Movie.query.all()]
    print(movies)

    return jsonify({
                    'success': True,
                    'status_code': 200,
                    'movies': movies
    })


'''
    GET /actors
        it should be a public endpoint
        it should contain only the actor.short() data representation
    returns status code 200 and json {"success": True, "actors": actors} where
    actors is the list of actors or appropriate status code indicating reason
    for failure
'''


@app.route('/actors', methods=['GET'])
def getAllActors():
    actors = [actor.short() for actor in Actor.query.all()]
    print(actors)

    return jsonify({
                    'success': True,
                    'status_code': 200,
                    'actors': actors
    })

'''
    GET /all
        it should be a public endpoint
        it should contain only the actor.short() and movie.short() data
        representation
    returns status code 200 and json {"success": True, "movies":movies,
                                      "actors": actors} where
    movies is a list of movies and actors is the list of actors or
    appropriate status code indicating reason for failure
'''


@app.route('/', methods=['GET'])
def getAllMoviesActors():
    movies = [movie.short() for movie in Movie.query.all()]
    actors = [actor.short() for actor in Actor.query.all()]
    print(movies, actors)

    return jsonify({
                    'success': True,
                    'status_code': 200,
                    'movies': movies,
                    'actors': actors
    })

'''
    GET /movies
        it should be a public endpoint
        it contain only the movie data representation
    returns status code 200 and json {"success": True, "movies": movies} where
    movies is the list of movies or appropriate status code indicating reason
    for failure
'''


@app.route('/movies-full', methods=['GET'])
@requires_auth(permission='get:movies-full')
def getAllMoviesFull():
    try:
        movies = [movie.long() for movie in Movie.query.all()]
        print(movies)

        return jsonify({
                        'success': True,
                        'movies': movies
        }), 200
    except Exception as error:
        print(sys.exc_info())
        abort(404)

'''
    GET /actors
        it should be a public endpoint
        it contain only the actor data representation
    returns status code 200 and json {"success": True, "actors": actors} where
    actors is the list of actors or appropriate status code indicating reason
    for failure
'''


@app.route('/actors-full', methods=['GET'])
@requires_auth(permission='get:actors-full')
def getAllActorsFull():
    try:
        actors = [actor.long() for actor in Actor.query.all()]
        print(actors)

        return jsonify({
                        'success': True,
                        'actors': actors
        }), 200
    except Exception as error:
        print(sys.exc_info())
        abort(404)


'''
    POST /movies
        it should create a new row in the movies table
        it should require the 'post:movies' permission
        it should contain the movie.long() data representation
    returns status code 200 and json {"success": True, "movies": movie} where
    movie an array containing only the newly created movie
        or appropriate status code indicating reason for failure
'''


@app.route('/movies', methods=['POST'])
@requires_auth('post:movies')
def addNewMovie(jwt):
    data = request.get_json()
    req_title = data.get('title', None)
    req_release_date = data.get('release_date', None)
    try:
        movie = Movie(title=req_title, release_date=req_release_date)
        movie.insert()
        return jsonify({
            'success': True,
            'movies': [movie.long()]
        }), 200
    except:
        abort(422)

'''
    POST /actors
        it should create a new row in the actors table
        it should require the 'post:actors' permission
        it should contain the actor.long() data representation
    returns status code 200 and json {"success": True, "actors": actor} where
    actor an array containing only the newly created actor
        or appropriate status code indicating reason for failure
'''


@app.route('/actors', methods=['POST'])
@requires_auth('post:actors')
def addNewActor(jwt):
    data = request.get_json()
    req_name = data.get('name', None)
    req_age = data.get('age', None)
    req_gender = data.get('gender', None)
    try:
        actor = Actor(name=req_name, age=req_age, gender=req_gender)
        actor.insert()
        return jsonify({
            'success': True,
            'actors': [actor.long()]
        }), 200
    except:
        abort(422)

'''
    PATCH /movies/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:movies' permission
        it should contain the movie.long() data representation
    returns status code 200 and json {"success": True, "movies": movie} where
    movie an array containing only the updated movie
        or appropriate status code indicating reason for failure
'''


@app.route('/movies/<int:movie_id>', methods=['PATCH'])
@requires_auth('patch:movies')
def patchDrink(jwt, movie_id):
    data = request.get_json()
    req_title = data.get('title', None)
    req_release_date = data.get('release_date', None)
    try:
        movie = Movie.query.get(movie_id)
        movie.title = req_title
        movie.release_date = req_release_date
        movie.update()
        return jsonify({
            'success': True,
            'drinks': [movie.long()]
        }), 200
    except:
        abort(404)

'''
    PATCH /actors/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:actors' permission
        it should contain the actor.long() data representation
    returns status code 200 and json {"success": True, "actors": actor} where
    actor an array containing only the updated actor
        or appropriate status code indicating reason for failure
'''


@app.route('/actors/<int:actor_id>', methods=['PATCH'])
@requires_auth('patch:actors')
def patchActor(jwt, actor_id):
    data = request.get_json()
    req_name = data.get('name', None)
    req_age = data.get('age', None)
    req_gender = data.get('gender', None)
    try:
        actor = Actor.query.get(actor_id)
        actor.name = req_name
        actor.age = req_age
        actor.gender = req_gender
        actor.update()
        return jsonify({
            'success': True,
            'actors': [actor.long()]
        }), 200
    except:
        abort(404)

'''
    DELETE /movies/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:movies' permission
    returns status code 200 and json {"success": True, "delete": id} where id
    is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/movies/<int:movie_id>', methods=['DELETE'])
@requires_auth('delete:movies')
def deleteDrink(jwt, movie_id):
    try:
        movie = Movie.query.get(movie_id)
        movie.delete()
        return jsonify({
            'success': True,
            'delete': movie_id
        }), 200
    except:
        abort(404)

'''
    DELETE /actors/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:actors' permission
    returns status code 200 and json {"success": True, "delete": id} where id
    is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/actors/<int:actor_id>', methods=['DELETE'])
@requires_auth('delete:actors')
def deleteActor(jwt, actor_id):
    try:
        actor = Actor.query.get(actor_id)
        actor.delete()
        return jsonify({
            'success': True,
            'delete': actor_id
        }), 200
    except:
        abort(404)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
      }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
      }), 422


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
      }), 400


@app.errorhandler(500)
def not_found(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "wrong input paramters"
      }), 500


@app.errorhandler(405)
def not_found(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "method not allowed"
      }), 405


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
# if __name__ == '__main__':
#     app.run()