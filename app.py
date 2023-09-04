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

@app.route('/test', methods=['GET','POST'])
def test():

    season = request.form.get("seasonI")
    question = request.form.get("questionI")
    category = request.form.get("categoryI")
    UserAnswer = request.form.get("user_answerI")
    correctAnswer = request.form.get("correct_answerI")
    print("please don't be the same-----------------")
    print(correctAnswer)
    isAnswerCorrect = request.form.get("isAnswerCorrect")
    questionId = request.form.get("questionIdI")

    print("---question id-----")

    print(season)
    print(question)
    print(category)

    # Connect to the database
    conn = psycopg2.connect(database="test_db",
                            user="root",
                            password="root",
                            host="localhost", port="5432")
  
    # create a cursor
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO user_answer (user_answer, given_question, user_id, question_id, correct_answer, is_user_correct, category) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (UserAnswer, question, 99, questionId, correctAnswer, isAnswerCorrect, category))
    
    conn.commit()

    return {"season": season} # return the result to JavaScript

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
  
    # Select random question
    cur.execute('''SELECT
	* FROM clues OFFSET floor(random() * (
		SELECT
			COUNT(*)
			FROM clues))
    LIMIT 1;''')
  
    # # Fetch the data
    data = cur.fetchall()

    season = request.form.get("season")
    question = request.form.get("question")
    question_id = request.form.get("question_id")

    print(season)
    print(question)
    print(question_id)

    print("---quesiton id-----")
    print(data[0][0])
    print(data)

    question_id = data[0][0]
    print(question_id)

    cur.execute('''Select season_name from clues_with_games_and_seasons_mv WHERE id = (%s);''', (question_id,))
    # cur.execute('''Select season_name from clues_with_games_and_seasons_mv WHERE id = 123;''')

    season = cur.fetchall()
    print(season[0][0])

    # Select all products from the table
    cur.execute('''SELECT DISTINCT * from seasons
        order by start_date;''')
  
    # Fetch the data
    seasons = cur.fetchall()

    print(seasons)
    print(len(seasons))

    season_dict = {}
    for i in range(0, len(seasons)):
        season_dict[seasons[i][1]] = seasons[i][0]

    print("season dict")
    print(season_dict)

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
    session['season_dict'] = season_dict
    session['clue_values'] = clue_values
    filtered_json=session['filtered_data']
    return render_template('index.html', data=data, correctAnswer=data[0][-1], seasons=season_dict, seasonOfQuestion=season[0][0], clue_values=clue_values, categories=categories, filtered_json=filtered_json)
    # return render_template('index.html', data=data)

@app.route('/process-filter', methods=['GET','POST'])
def process_filter():
    print("----printing -----process-filter")
    print(request.get_data)

    seasons = session['seasons']
    season_dict = session['season_dict']

    categoryI = request.form.get("categoryI")

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

    print(categoryI)
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

    print(seasons)
  
    if from_value == '':
        from_value=200
    if to_value == '':
        to_value=from_value
    # Select all products from the table
    cur.execute('''SELECT
	* FROM clues_with_games_and_seasons_mv WHERE season_id BETWEEN (%s) AND (%s) AND value BETWEEN (%s) AND (%s) OFFSET random() * (SELECT
			COUNT(*)
			FROM clues_with_games_and_seasons_mv WHERE season_id BETWEEN (%s) AND (%s) AND value BETWEEN (%s) AND (%s)) 
			LIMIT 1;''', (season_dict[to_season], season_dict[from_season], from_value, to_value, season_dict[to_season], season_dict[from_season], from_value, to_value))
  
    print(season_dict['Season 1'])
    # # Fetch the data
    filtered_data = cur.fetchall()

    print('rendering mainmenu') 

    session['filtered_data'] = filtered_data

    print(filtered_data)

    print("--------js filtering--------------------")
    print(filtered_data[0][5])

    

    data = {"category": filtered_data[0][3], "question": filtered_data[0][4], "correctAnswer": filtered_data[0][5], "value": filtered_data[0][2], "season": filtered_data[0][-1]}
    # filtered_data = [values for labels, values in data]

    # return render_template("index.html", filtered_data=filtered_data)

    return {"category": filtered_data[0][3], "questionId": filtered_data[0][0], "question": filtered_data[0][4], "correctAnswer": filtered_data[0][5], "value": filtered_data[0][2], "season": filtered_data[0][-1]} # return the result to JavaScript

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

    data = session.get("answer_data",None)
    print(data)


    session['filtered_data'] = filtered_data

    print(filtered_data)

    print("--------------------in filtering-------- /filtered")

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

# @app.route('/', methods=['POST'])
# def submit():
#     data = session.get("answer_data",None)
#     filtered_data=session.get('filtered_data', None)
#     season_dict = session['season_dict']
    
#     print("---check 1")
#     print(filtered_data)
#     if request.method == 'POST':
#         answer= request.form['answer']
#         correctAnswer = data[0][-1]
#         question = data[0][-2]
#         question_id = data[0][0]
#         # answer=answer.lower().replace('the ', '')
#         correctAnswer=correctAnswer.lower().replace('the ', '').replace('<', '')
#         print(answer)
#         print(correctAnswer)
#         print(answer == correctAnswer)
#         print("oh no")
#         isAnswerCorrect = answer == correctAnswer
#         category = data[0][5]

#         print('check 2-------')
#         print(filtered_data)
#         if filtered_data != None:
#             fCorrectAnswer=filtered_data[0][5]
#             fCorrectAnswer=fCorrectAnswer.lower().replace('the ', '').replace('<', '')
#             fQuestion=filtered_data[0][4]
#             fQuestion_id=filtered_data[0][0]
#             isFAnswerCorrect= answer == fCorrectAnswer
#             fCategory=filtered_data[0][3]

#         # Connect to the database
#         conn = psycopg2.connect(database="test_db",
#                             user="root",
#                             password="root",
#                             host="localhost", port="5432")
  
#         # create a cursor
#         cur = conn.cursor()

#         cur.execute(
#             "INSERT INTO user_answer (user_answer, given_question, user_id, question_id, correct_answer, is_user_correct, category) VALUES (%s, %s, %s, %s, %s, %s, %s)",
#               (answer, question, 99, question_id, correctAnswer, isAnswerCorrect, category))
    

#         cur.execute('''Select season_name from clues_with_games_and_seasons_mv WHERE id = (%s);''', (question_id,))
#         # cur.execute('''Select season_name from clues_with_games_and_seasons_mv WHERE id = 123;''')

#         season = cur.fetchall()
#         print(season[0][0])
        
#         conn.commit()

#         print(filtered_data)
#         print(isAnswerCorrect)
#         print(answer)
#         print(correctAnswer)
#         print(fCorrectAnswer)
#         print(isFAnswerCorrect)
#         # session['filtered_data'] = None
#         filtered_data=None
#         if(isAnswerCorrect):
#             return render_template("index.html", message='Correct!', correctAnswer=correctAnswer, seasonOfQuestion=season[0][0], seasons=season_dict, data=data, filtered_data=filtered_data)
#         else:
#             return render_template("index.html", message='Incorrect!', correctAnswer=correctAnswer, seasonOfQuestion=season[0][0], seasons=season_dict, data=data, filtered_data=filtered_data)
        
# @app.route('/filter', methods=['POST'])
# def submit_filter():
#     data=session.get("answer_data", None)
#     if request.method == 'POST':
#         answer= request.form['answer']
#         correctAnswer = data[0][-1]
#         question = data[0][-2]
#         question_id = data[0][0]
#         # answer=answer.lower().replace('the ', '')
#         correctAnswer=correctAnswer.lower().replace('the ', '').replace('<', '')
#         isAnswerCorrect = answer == correctAnswer
#         category = data[0][5]

#         # Connect to the database
#         conn = psycopg2.connect(database="test_db",
#                             user="root",
#                             password="root",
#                             host="localhost", port="5432")
  
#         # create a cursor
#         cur = conn.cursor()

#         print("-------inserting into database user answer and correct answer----------")
#         cur.execute(
#             "INSERT INTO user_answer (user_answer, given_question, user_id, question_id, correct_answer, is_user_correct, category) VALUES (%s, %s, %s, %s, %s, %s, %s)",
#               (answer, question, 1, question_id, correctAnswer, isAnswerCorrect, category))
    
#         conn.commit()

#         print("----------------in filtering--------------------------------")
#         if(isAnswerCorrect):
#             return render_template("index.html", message='Correct!', data=data)
#         else:
#             return render_template("index.html", message='Incorrect!', data=data)

# //Use a function to put duplicate code and ensure that submit, index and filter are very similar
if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run()