from flask import Flask, render_template, request


# Это callable WSGI-приложение
app = Flask(__name__)

users = ['mike', 'mishel', 'adel', 'keks', 'kamila']


@app.route('/')
def hello_world():
    return 'Hello!'


@app.route('/users')
def get_users():
    term = request.args.get('term', '')
    filtered_users = filter(
        lambda user: term.lower() in user, users)

    return render_template(
        'users/index.html',
        users=filtered_users,
        search=term,
      )


@app.route('/courses/<id>')
def courses(id):
    return f'Course id: {id}'


@app.route('/users/<id>')
def users_(id):
    return render_template(
        'users/show.html',
        id=id,
    )
