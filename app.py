from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import psycopg2

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:root@localhost:5432/test_db'

else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

def createFilterMaterializedView():
        # Connect to the database
        conn = psycopg2.connect(database="test_db",
                            user="root",
                            password="root",
                            host="localhost", port="5432")
  
        # create a cursor
        cur = conn.cursor()

        # cur.execute(
        #     "CREATE INDEX IF NOT EXISTS season_answer (user_answer, given_question, user_id, question_id, correct_answer, is_user_correct, category) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        #       (answer, question, 1, question_id, correctAnswer, isAnswerCorrect, category))
        
        cur.execute(
        "-- Create MATERIALIZED VIEW IF NOT EXISTS clues_with_games_and_seasons_mv AS SELECT distinct clues.id, game_id, value, categorytitle, clue, response, season_id, season_name FROM cluesjoin games ON clues.game_id=games.idjoin seasons ON games.season_id=seasons.id;")

        # # close the cursor and connection
        cur.close()
        conn.close()


class User_Answer(db.Model):
    tablename__ = 'user_answer'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    question_id = db.Column(db.Integer)
    given_question = db.Column(db.String(400))
    user_answer = db.Column(db.String(200))
    correct_answer = db.Column(db.String(200))
    is_user_correct = db.Column(db.Boolean)
    category = db.Column(db.String(200))

    def __init__(self, user_id, question_id, given_question, user_answer, correct_answer, is_user_correct, category):
        self.user_id = user_id
        self.question_id = question_id
        self.given_question = given_question
        self.user_answer = user_answer
        self.correct_answer = correct_answer
        self.is_user_correct = is_user_correct
        self.category = category


@app.route('/')
def index():
    print("----test-------")
    # filter()
    # Connect to the database
    conn = psycopg2.connect(database="test_db",
                            user="root",
                            password="root",
                            host="localhost", port="5432")
  
    # create a cursor
    cur = conn.cursor()
  
    # Select all products from the table
    cur.execute('''SELECT
	* FROM clues OFFSET floor(random() * (
		SELECT
			COUNT(*)
			FROM clues))
    LIMIT 1;''')
  
    # # Fetch the data
    data = cur.fetchall()

    # Select all products from the table
    cur.execute('''SELECT DISTINCT * from seasons
        order by start_date;''')
  
    # Fetch the data
    seasons = cur.fetchall()

    cur.execute('''select DISTINCT value from clues order by value asc;''')

    clue_values = cur.fetchall()

    # cur.execute('''select distinct categorytitle from clues group by categorytitle order by categorytitle desc;''')
    cur.execute('''select distinct categorytitle from clues order by categorytitle desc;''')

    categories = cur.fetchall()
  
    # # close the cursor and connection
    cur.close()
    conn.close()

    session['answer_data'] = data
    session['seasons'] = seasons
    session['clue_values'] = clue_values
    return render_template('index.html', data=data, seasons=seasons, clue_values=clue_values, categories=categories)
    # return render_template('index.html', data=data)

@app.route('/process-filter', methods=['POST'])
def process_filter():
    print(request.get_data)
    from_season = request.form.get("from_season")
    to_season = request.form.get("to_season")
    category = request.form.get("category")
    from_value = request.form.get("from_value")
    to_value = request.form.get("to_value")
    print(from_season)
    print(to_season)
    print(category)
    print(from_value)
    print(to_value)
    # print(from_season)
    # data = req# retrieve the data sent from JavaScript
    # process the data using Python code
    # result = data['value'] * 2
          # Connect to the database
    conn = psycopg2.connect(database="test_db",
                            user="root",
                            password="root",
                            host="localhost", port="5432")
  
    # create a cursor
    cur = conn.cursor()
  
    # Select all products from the table
    cur.execute('''SELECT
	* FROM clues_with_games_and_seasons_mv WHERE season_id BETWEEN (%s) AND (%s) AND value BETWEEN (%s) AND (%s) OFFSET random() * (SELECT
			COUNT(*)
			FROM clues_with_games_and_seasons_mv WHERE season_id BETWEEN (%s) AND (%s) AND value BETWEEN (%s) AND (%s)) 
			LIMIT 1;''', (12, 15, 1200, 2000, 12, 15, 1200, 2000))
  
    # # Fetch the data
    filtered_data = cur.fetchall()

    print('rendering mainmenu') 

    session['answer_data'] = filtered_data

    print(filtered_data)

    return render_template("index.html", filtered_data=filtered_data, message="Correct!")

    return jsonify(from_season=from_season) # return the result to JavaScript

@app.route("/filtered",methods=["POST"]) 
def index_with_filter():
    print("inside function") 
    # from_season = request.form["from_season"]
    # to_season = request.form['to_season']
    # category = request.form['category']
    # from_value = request.form['from_value']
    # to_value = request.form['to_value']

      # Connect to the database
    conn = psycopg2.connect(database="test_db",
                            user="root",
                            password="root",
                            host="localhost", port="5432")
  
    # create a cursor
    cur = conn.cursor()
  
    # Select all products from the table
    cur.execute('''SELECT
	* FROM clues_with_games_and_seasons_mv WHERE season_id BETWEEN (%s) AND (%s) AND value BETWEEN (%s) AND (%s) OFFSET random() * (SELECT
			COUNT(*)
			FROM clues_with_games_and_seasons_mv WHERE season_id BETWEEN (%s) AND (%s) AND value BETWEEN (%s) AND (%s)) 
			LIMIT 1;''', (12, 15, 1200, 2000, 12, 15, 1200, 2000))
  
    # # Fetch the data
    filtered_data = cur.fetchall()

    print('rendering mainmenu') 

    session['answer_data'] = filtered_data

    print(filtered_data)

    return render_template("index.html", filtered_data=filtered_data, message="Correct!")



# @app.route('/filtered', methods=['POST'])
# def filter():

#     data = session.get("answer_data",None)

    # from_season = request.form['from season']
    # from_season=request.form['from season']
    # to_season=request.form['to season']

    # print(from_season)
    # return render_template("index.html", data=data)
    # return render_template("index.html", data=data)

# @app.route('/filter', methods=['POST'])
# def filter():
#     print("filtering....")

#     # createFilterMaterializedView()
#     from_season=request.form['from season']
#     to_season=request.form['to season']

#     print(from_season)
#     print(to_season)

#         # Connect to the database
#     conn = psycopg2.connect(database="test_db",
#                             user="root",
#                             password="root",
#                             host="localhost", port="5432")
  
#     # create a cursor
#     cur = conn.cursor()
  
#     # Select all products from the table
#     cur.execute('''SELECT
# 	* FROM clues OFFSET floor(random() * (
# 		SELECT
# 			COUNT(*)
# 			FROM clues
#                 WHERE ))
#     LIMIT 1;''')
  
#     # Fetch the data
#     data = cur.fetchall()
  
#     # close the cursor and connection
#     cur.close()
#     conn.close()

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json() # retrieve the data sent from JavaScript
    # process the data using Python code
    result = data['value'] * 2
    return jsonify(result=result) # return the result to JavaScript

@app.route('/', methods=['POST'])
def submit():
    data = session.get("answer_data",None)
    if request.method == 'POST':
        answer= request.form['answer']
        correctAnswer = data[0][-1]
        question = data[0][-2]
        question_id = data[0][0]
        # answer=answer.lower().replace('the ', '')
        correctAnswer=correctAnswer.lower().replace('the ', '').replace('<', '')
        isAnswerCorrect = answer == correctAnswer
        category = data[0][5]

        # Connect to the database
        conn = psycopg2.connect(database="test_db",
                            user="root",
                            password="root",
                            host="localhost", port="5432")
  
        # create a cursor
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO user_answer (user_answer, given_question, user_id, question_id, correct_answer, is_user_correct, category) VALUES (%s, %s, %s, %s, %s, %s, %s)",
              (answer, question, 1, question_id, correctAnswer, isAnswerCorrect, category))
    
        conn.commit()

        if(isAnswerCorrect):
            return render_template("index.html", message='Correct!', data=data)
        else:
            return render_template("index.html", message='Incorrect!', data=data)
        
@app.route('/filter', methods=['POST'])
def submit_filter():
    data=session.get("answer_data", None)
    if request.method == 'POST':
        answer= request.form['answer']
        correctAnswer = data[0][-1]
        question = data[0][-2]
        question_id = data[0][0]
        # answer=answer.lower().replace('the ', '')
        correctAnswer=correctAnswer.lower().replace('the ', '').replace('<', '')
        isAnswerCorrect = answer == correctAnswer
        category = data[0][5]

        # Connect to the database
        conn = psycopg2.connect(database="test_db",
                            user="root",
                            password="root",
                            host="localhost", port="5432")
  
        # create a cursor
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO user_answer (user_answer, given_question, user_id, question_id, correct_answer, is_user_correct, category) VALUES (%s, %s, %s, %s, %s, %s, %s)",
              (answer, question, 1, question_id, correctAnswer, isAnswerCorrect, category))
    
        conn.commit()

        if(isAnswerCorrect):
            return render_template("index.html", message='Correct!', data=data)
        else:
            return render_template("index.html", message='Incorrect!', data=data)

# //Use a function to put duplicate code and ensure that submit, index and filter are very similar
if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run()