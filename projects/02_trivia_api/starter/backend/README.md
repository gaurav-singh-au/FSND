# The Great Fullstack Trivia

Udacity is invested in creating bonding experiences for its employees and students. Udacity, in consultation with some team members have created a webpage to manage the trivia app and play the game.

This application:
1. Display questions - both all questions and by category. Questions show the question, category and difficulty rating by default and can show/hide the answer.
2. Delete questions - Ability to delete any questions
3. Add questions and require that they include question, answer text, difficulty ratings and categories.
4. Ability to search for questions based on a text query string.
5. Play the quiz game, randomizing either questions for all categories or within a specific category.

All backend code follows [PEP8 style guidelines](https://www.python.org/dev/peps/pep-0008/). 


## Getting Started

### Pre-requisites and Local Development 
Developers using this project should already have Python3, pip and node installed on their local machines.

#### Backend

From the backend folder run `pip install requirements.txt`. All required packages are included in the requirements file. 

To run the application run the following commands: 
```
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

These commands put the application in development and directs our application to use the `__init__.py` file in our flaskr folder. Working in development mode shows an interactive debugger in the console and restarts the server whenever changes are made. If running locally on Windows, look for the commands in the [Flask documentation](http://flask.pocoo.org/docs/1.0/tutorial/factory/).

The application is run on `http://127.0.0.1:5000/` by default and is a proxy in the frontend configuration. 

#### Frontend

From the frontend folder, run the following commands to start the client: 
```
npm install // only once to install dependencies
npm start 
```

By default, the frontend will run on localhost:3000. 

### Tests
In order to run tests navigate to the backend folder and run the following commands: 

```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

The first time you run the tests, omit the dropdb command. 

All tests are kept in that file and should be maintained as updates are made to app functionality. 

## API Reference

### Getting Started
- Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `http://127.0.0.1:5000/`, which is set as a proxy in the frontend configuration. 
- Authentication: This version of the application does not require authentication or API keys. 

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found
- 422: Not Processable 
- 500: Method Not Allowed
### Endpoints 
#### GET /questions
- General:
    - Returns a list of question objects, success value, total number of questions, list of categories and current category
    - Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1. 
- Sample: `curl http://127.0.0.1:5000/books`

``` {
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": "Science",
  "questions": [
    {
      "answer": "Maya Angelou",
      "category": 4,
      "difficulty": 2,
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    },
    {
      "answer": "Muhammad Ali",
      "category": 4,
      "difficulty": 1,
      "id": 9,
      "question": "What boxer's original name is Cassius Clay?"
    },
    {
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    },
    {
      "answer": "Tom Cruise",
      "category": 5,
      "difficulty": 4,
      "id": 4,
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    },
    {
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3,
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    },
    {
      "answer": "Brazil",
      "category": 6,
      "difficulty": 3,
      "id": 10,
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    },
    {
      "answer": "Uruguay",
      "category": 6,
      "difficulty": 4,
      "id": 11,
      "question": "Which country won the first ever soccer World Cup in 1930?"
    },
    {
      "answer": "George Washington Carver",
      "category": 4,
      "difficulty": 2,
      "id": 12,
      "question": "Who invented Peanut Butter?"
    },
    {
      "answer": "Lake Victoria",
      "category": 3,
      "difficulty": 2,
      "id": 13,
      "question": "What is the largest lake in Africa?"
    },
    {
      "answer": "The Palace of Versailles",
      "category": 3,
      "difficulty": 3,
      "id": 14,
      "question": "In which royal palace would you find the Hall of Mirrors?"
    }
  ],
  "success": true,
  "total_questions": 19
}
```
#### GET /categories
- General:
    - Returns a list of category objects and success value
- Sample: `curl http://127.0.0.1:5000/books`
```
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "success": true
}
```

#### GET /categories/category_id/questions
- General:
    - Returns all questions, success, total number of questions and current category for the specific input category id. If there are no questions in that category then a 404 error is returned.
- Sample: `curl http://127.0.0.1:5000/categories/1/questions`
```
{
  "current_category": "Science",
  "questions": [
    {
      "answer": "The Liver",
      "category": 1,
      "difficulty": 4,
      "id": 20,
      "question": "What is the heaviest organ in the human body?"
    },
    {
      "answer": "Alexander Fleming",
      "category": 1,
      "difficulty": 3,
      "id": 21,
      "question": "Who discovered penicillin?"
    },
    {
      "answer": "Blood",
      "category": 1,
      "difficulty": 4,
      "id": 22,
      "question": "Hematology is a branch of medicine involving the study of what?"
    }
  ],
  "success": true,
  "total_questions": 3
}
```

#### POST /questions/add
- General:
    - Creates a new question using the submitted question,answer, difficulty and category.
    - Returns to an empty form after submission
    - Returns True if succeeded else a 422 error.

```
{
  "success": true,
}
```
#### POST /questions/search
- General:
    - Provides a list of questions that match specific text given as an input. It is case insensitive. Also returns success, total_questions found and current category as empty string.
    - example when searching for "ice"
```
{
	'success': True, 
	'questions': [
	{
		'id': 4, 
		'question': 'What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?', 
		'answer': 'Tom Cruise', 
		'category': 5, 
		'difficulty': 4
	}], 
	'total_questions': 1, 
	'current_category': ''
}
```

#### POST /quizzes
- General:
    - Returns a random question from the input category that hasn't been asked previously in that round. If there are no questions remaining it returns None to terminate the quiz.
    - Expects as input a list of previous question ids and a category. Category id 0 is considered as "All".

#### DELETE /questions/{question_id}/delete
- General:
    - Deletes the question of the given ID if it exists. Returns the deleted question and success value. 
- `curl http://127.0.0.1:5000/questions/27/delete`
```
{
 "question": {
		'id': 27, 
		'question': 'What is my name?', 
		'answer': 'Mathswizard', 
		'category': 4, 
		'difficulty': 1
		},
 "success": true
}
```

## Deployment N/A

## Authors
Yours truly, Gaurav Singh

## Acknowledgements 
Greta tutorials at Udacity and Google search :) ! 
