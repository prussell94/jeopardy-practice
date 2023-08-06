from flask import Flask, render_template, request, session
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

class User_Answer(db.Model):
    tablename__ = 'user_answer'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    question_id = db.Column(db.Integer)
    given_question = db.Column(db.String(200), unique=True)
    user_answer = db.Column(db.String(200))

    def __init__(self, user_id, question_id, given_question, user_answer):
        self.user_id = user_id
        self.question_id = question_id
        self.given_question = given_question
        self.user_answer = user_answer


@app.route('/')
def index():
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
  
    # Fetch the data
    data = cur.fetchall()
  
    # close the cursor and connection
    cur.close()
    conn.close()
    session['answer_data'] = data
    # return Flask.redirect(Flask.url_for('submit'))
    return render_template('index.html', data=data)

@app.route('/submit', methods=['POST'])
def submit():
    # # Connect to the database
    # conn = psycopg2.connect(database="test_db",
    #                         user="root",
    #                         password="root",
    #                         host="localhost", port="5432")
  
    # # create a cursor
    # cur = conn.cursor()
  
    # # Select all products from the table
    # cur.execute('''SELECT
	# * FROM clues OFFSET floor(random() * (
	# 	SELECT
	# 		COUNT(*)
	# 		FROM clues))
    # LIMIT 1;''')
  
    # # Fetch the data
    # data = cur.fetchall()
    # print(data[0][-1])
  
    # # close the cursor and connection
    # cur.close()
    # conn.close()
    data = session.get("answer_data",None)
    if request.method == 'POST':
        answer= request.form['answer']
        correctAnswer = data[0][-1]
        if(answer == correctAnswer):
            return render_template("index.html", message='Correct!', data=data)
        else:
            return render_template("index.html", message='Incorrect!', data=data)

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run()