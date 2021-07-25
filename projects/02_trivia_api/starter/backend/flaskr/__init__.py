import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json

from models import setup_db, Question, Category, find_questions

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    # print("page number is : ", page)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [ques.format() for ques in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after
    completing the TODOs
    '''
    CORS(app)

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''

    @app.route('/categories')
    def getAllCategories():
        categories = {cat.id: cat.type for cat in Category.query.all()}
        # print(categories[0])

        return jsonify({
                        'success': True,
                        'categories': categories
        })

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three
    pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions')
    def getQuestions():
        selection = Question.query.all()
        # print(len(selection))
        current_questions = paginate_questions(request, selection)
        # print(request.args)
        if len(current_questions) == 0:
            abort(404)

        categories = {cat.id: cat.type for cat in Category.query.all()}
        # print(categories[0])

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(Question.query.all()),
          'categories': categories,
          'current_category': categories[1]
        })

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>/delete',
               methods=['DELETE'])
    def deleteQuestion(question_id):
        try:
            ques = Question.query.filter(Question.id == question_id).all()[0]
            # print(ques.format())
            ques.delete()
            return jsonify({
                'success': True,
                'question': ques.format()
            })
        except:
            abort(400)

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at
    the end of the last page
    of the questions list in the "List" tab.
    '''
    @app.route('/add', methods=['POST'])
    def submitQuestions():
        sterm = request.data.decode("utf-8")
        data = json.loads(request.data.decode("utf-8"))
        new_ques = Question(data['question'],
                            data['answer'],
                            data['category'],
                            data['difficulty'])
        new_ques.insert()
        try:
            new_ques.insert()
            return jsonify({
              'success': True
            })
        except:
            abort(404)

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/questions/search', methods=['POST'])
    def findQuestions():
        sterm = request.data.decode("utf-8")
        term = json.loads(sterm)['searchTerm']
        ques = find_questions('%'+term+'%')
        if len(ques) == 0:
            abort(404)

        return jsonify({
          'success': True,
          'questions': [q.format() for q in ques],
          'total_questions': len(ques),
          'current_category': ''
        })

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:cat_id>/questions')
    def getByCategory(cat_id):
        cat = Category.query.get(cat_id)
        if not cat:
            abort(404)
        selection = Question.query.filter(Question.category == cat.id).all()
        # print(len(selection))
        if len(selection) == 0:
            abort(404)

        return jsonify({
          'success': True,
          'questions': [q.format() for q in selection],
          'total_questions': len(selection),
          'current_category': cat.type
        })

    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    def nextQuestion():
        sterm = request.data.decode("utf-8")
        term = json.loads(sterm)
        # print(term)
        if 'previous_questions' not in term or 'quiz_category' not in term:
            abort(500)
        prev_questions = term['previous_questions']
        cat = term['quiz_category']['id']
        if cat != 0:
            selection = Question.query.filter(Question.category == cat).filter(
                ~Question.id.in_(prev_questions)
                ).all()
        else:
            selection = Question.query.filter(
                ~Question.id.in_(prev_questions)
                ).all()

        next_q = None
        if len(selection) > 0:
            random.shuffle(selection)
            next_q = selection[0].format()

        return jsonify({
          'success': True,
          'previousQuestions': prev_questions,
          'question': next_q,
          'current_category': term['quiz_category']['type']
        })

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
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

    return app
