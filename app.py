from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

CREATE_USERS_TABLE_QUERY = '''
CREATE TABLE users (
  id VARCHAR(100) NOT NULL,
  PRIMARY KEY (id)
);
'''

CREATE_CATEGORIES_TABLE_QUERY = '''
CREATE TABLE categories ( 
  uid VARCHAR(100) NOT NULL,
  id VARCHAR(100) NOT NULL,
  name VARCHAR(100) NOT NULL,
  weight FLOAT NOT NULL,
  PRIMARY KEY (uid, id),
  FOREIGN KEY (uid) REFERENCES users (id) ON DELETE CASCADE
);
'''

CREATE_ASSIGNMENTS_TABLE_QUERY = '''
CREATE TABLE assignments ( 
  uid VARCHAR(100) NOT NULL,
  cid VARCHAR(100) NOT NULL,
  id VARCHAR(100) NOT NULL,
  name VARCHAR(100) NOT NULL,
  score FLOAT NOT NULL,
  max_score FLOAT NOT NULL,
  PRIMARY KEY (uid, cid, id),
  FOREIGN KEY (uid, cid) REFERENCES categories (uid, id) ON DELETE CASCADE
);
'''

DATABASE_FILE_NAME = 'grade.db'

app = Flask(__name__)
CORS(app)
app.debug = True

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/ping')
def ping():
    return 'pong'

@app.route('/load/<username>', methods = ['GET'])
def load_grades(username):
    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()

    return jsonify({})

@app.route('/save', methods = ['POST'])
def save_grades():
    data = request.get_json()

    username = data['username']
    categories = data['categories']

    return jsonify({})

def create_table():
    if os.path.exists(DATABASE_FILE_NAME):
        return

    print('Created a connection!')
    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()

    cursor.execute(CREATE_USERS_TABLE_QUERY)
    cursor.execute(CREATE_CATEGORIES_TABLE_QUERY)
    cursor.execute(CREATE_ASSIGNMENTS_TABLE_QUERY)
    
    connection.commit()
    connection.close()

def insert_sample_data():
    if os.path.exists(DATABASE_FILE_NAME):
        return

    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()

    cursor.execute("INSERT INTO users VALUES('dannyhp1');")
    cursor.execute("INSERT INTO categories VALUES('dannyhp1', '0', 'exams', 35);")
    cursor.execute("INSERT INTO assignments VALUES('dannyhp1', '0', '0', 'midterm1', 90, 100);")
    cursor.execute("INSERT INTO assignments VALUES('dannyhp1', '0', '1', 'midterm2', 95, 100);")
    
    connection.commit()
    connection.close()


if __name__ == '__main__':
    app.run(port=5000)