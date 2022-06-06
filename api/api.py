import flask
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask import url_for
from flask_httpauth import HTTPBasicAuth



app = flask.Flask(__name__)
app.config["DEBUG"] = True

#authentication
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'linda':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Ask Linda for the key'}), 401)

# Create some test data for our to do list 
tasks = [
    {'id': 1,
     'title': 'Read Medium Articles',
     'description': 'Read medium articles on software, product management, technology',
     'done': True},
    {'id': 2,
     'title': 'Learn Programming Skills',
     'description': 'Follow Web Development course on Udemy',
     'done': False},
    {'id': 3,
     'title': 'Learn Foundations of CS - Study Data Structures & Algorithms',
     'description': 'Watch CS50 course - intro to computer science https://learning.edx.org/course/course-v1:HarvardX+CS50+X/home',
     'done': False},
    {'id': 4,
     'title': 'Learn Extra Technical Skills',
     'description': 'Watch AWS and Lambdas course on Frontend Masters',
     'done': False},

]


@app.route('/', methods=['GET'])
def home():
    return "<h1>To do list </h1><p>This site is a prototype API for a simple to do list.</p>"

# A route to return all of the available entries in the todo list.
@app.route('/api/v1/projects/tasks/all', methods=['GET'])
@auth.login_required
def api_all():
    return jsonify(tasks)

# A route to return a specific entry in the todo list.
@app.route('/api/v1/projects/tasks/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})

#handling errors from html to json
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#Create a new entry
@app.route('/api/v1/projects/tasks', methods=['POST'])
@auth.login_required
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201

#Update entry
@app.route('/api/v1/projects/tasks/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})

#Delete an entry
@app.route('/api/v1/projects/tasks/<int:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task

@app.route('/api/v1/projects/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    return jsonify({'tasks': [make_public_task(task) for task in tasks]})

app.run()

