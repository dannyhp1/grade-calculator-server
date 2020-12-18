from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import os

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DATABASE_FILE_NAME = '%s/grade.db' % CURRENT_DIRECTORY

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

app = Flask(__name__)
CORS(app)
app.debug = True

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/ping')
def ping():
    return jsonify({ 'status': 'healthy', 'service': 'grade-calculator' })

@app.route('/download-data', methods = ['GET'])
def download_data():
    try:
        return send_file(DATABASE_FILE_NAME, attachment_filename='grade.db')
    except Exception as e:
        return jsonify({ 'error': e })

@app.route('/load/<username>', methods = ['GET'])
def load_grades(username):
    # If tables do not exist, create it now.
    initialize_tables()

    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()

    # Get user.
    query = 'SELECT id FROM users WHERE id = ?'
    cursor.execute(query, (username,))

    username = None
    for (id) in cursor:
        username = id[0]

    # If user does not exist in database, return not found.
    if username is None:
        connection.close()

        # Frontend incorrectly checks status in response message (rip).
        return jsonify(
            status=404,
            message='The username does not exist.'
        )
    
    max_category_id = 0
    categories = []

    # If the username exists, get the categories the user created.
    query = 'SELECT MAX(id) FROM categories WHERE uid = ?'
    cursor.execute(query, (username,))

    for (results) in cursor:
        max_category_id = int(results[0]) + 1

    query = 'SELECT * FROM categories WHERE uid = ?'
    cursor.execute(query, (username,))

    results = cursor.fetchall()
    
    for category in results:
        [uid, category_id, category_name, category_weight] = category
        
        # max_id will be the next available assignment ID. 
        max_assignment_id = 0

        query = 'SELECT MAX(id) FROM assignments WHERE uid = ? and cid = ?'
        cursor.execute(query, (username, category_id,))

        for (results) in cursor:
            max_assignment_id = int(results[0]) + 1 if results[0] != None else 0
        
        assignments = [ ]

        query = 'SELECT * FROM assignments WHERE uid = ? and cid = ?'
        cursor.execute(query, (username, category_id,))

        all_assignments = cursor.fetchall()

        for assignment in all_assignments:
            [uid, cid, assignment_id, assignment_name, assignment_score, assignment_max] = assignment
            assignments.append([assignment_id, assignment_name, assignment_score, assignment_max])

        categories.append([category_id, category_name, category_weight, max_assignment_id, assignments])

    cursor.close()
    connection.close()
    return jsonify(
        status=200,
        username=username,
        max_category=max_category_id,
        categories=categories
    )

@app.route('/save', methods = ['POST'])
def save_grades():
    # If tables do not exist, create it now.
    initialize_tables()

    data = request.get_json()

    username = data['username']
    categories = data['categories']

    # If there are no categories, do not wipe data and ignore.
    if len(categories) == 0:
        connection.close()
        
        return jsonify(
            status=200,
            message='No data to be stored. No action was taken.'
        )

    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()

    # Get user.
    query = 'SELECT id FROM users WHERE id = ?'
    cursor.execute(query, (username,))

    username = None
    for (id) in cursor:
        username = id[0]

    # If the username already exists, clear all of the user's data.
    if username is not None:
        query = 'DELETE FROM users WHERE id = ?' 
        cursor.execute(query, (username,))

    username = data['username']

    query = 'INSERT INTO users VALUES(?)'
    cursor.execute(query, (username,))

    for category in categories:
        category_id, name, weight, assignments = category['id'], category['name'], category['weight'], category['assignments']

        query = 'INSERT INTO categories VALUES(?, ?, ?, ?)'
        cursor.execute(query, (username, category_id, name, weight))

        for assignment in assignments:
            assignment_id, assignment_name, assignment_score, assignment_max = assignment['id'], assignment['name'], assignment['score'], assignment['max']

            query = 'INSERT INTO assignments VALUES(?, ?, ?, ?, ?, ?)'
            cursor.execute(query, (username, category_id, assignment_id, assignment_name, assignment_score, assignment_max))

    # Only commit at the end -- all or nothing.
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify(
        status=200,
        message='Data was successfully stored for ' + username + '.',
    )

def create_table():
    print('Creating a table!')
    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()

    cursor.execute(CREATE_USERS_TABLE_QUERY)
    cursor.execute(CREATE_CATEGORIES_TABLE_QUERY)
    cursor.execute(CREATE_ASSIGNMENTS_TABLE_QUERY)
    
    connection.commit()
    connection.close()

def insert_sample_data():
    print('Inserting sample data!')
    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()

    cursor.execute("INSERT INTO users VALUES('phamdann');")
    cursor.execute("INSERT INTO categories VALUES('phamdann', '0', 'midterms', 40);")
    cursor.execute("INSERT INTO assignments VALUES('phamdann', '0', '0', 'Midterm 1', 90, 100);")
    cursor.execute("INSERT INTO assignments VALUES('phamdann', '0', '1', 'Midterm 2', 95, 100);")
    cursor.execute("INSERT INTO categories VALUES('phamdann', '1', 'final', 60);")
    cursor.execute("INSERT INTO assignments VALUES('phamdann', '1', '0', 'Final Exam', 100, 100);")
    
    connection.commit()
    connection.close()

def initialize_tables():
    if os.path.exists(DATABASE_FILE_NAME):
        return
    
    print('There is currently no database. Creating it now...')
    create_table()
    insert_sample_data()

if __name__ == '__main__':
    app.run(port=5000)