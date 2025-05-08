from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime

DATA_FILE = 'submissions.json'

# Load existing submissions from file if it exists
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        submissions = json.load(f)
else:
    submissions = []


app = Flask(__name__)
app.secret_key = 'mydevkey'  # Needed for session management


# Route: Login Page
@app.route('/')
def home():
    return render_template('index.html')


# Route: Handle Login
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    session['username'] = username

    if username == 'teacher' and password == 'teacher':
        return redirect(url_for('teacher_portal'))
    else:
        return redirect(url_for('journal'))


# Route: Journal Page (Student)
@app.route('/journal')
def journal():
    return render_template('journal.html')


@app.route('/submit', methods=['POST'])
def submit():
    answer = request.form.get('answer')
    username = session.get('username', 'Unknown')
    mood = request.form.get('mood')   # default to gray if not selected

    timestamp = datetime.now().strftime("%-m/%-d/%Y %-I:%M:%S %p")

    new_submission = {
        'answer': request.form.get('answer'),
        'username': session.get('username', 'Unknown'),
        'mood': request.form.get('mood'),
        'timestamp': datetime.now().strftime("%-m/%-d/%Y %-I:%M:%S %p"),
        'bonus': False
    }

    submissions.append(new_submission)

    # Save to file
    with open(DATA_FILE, 'w') as f:
        json.dump(submissions, f)

    return render_template('journal.html', message=' Thank you for sharing your thoughts! 💬')

@app.route('/teacher')
def teacher_portal():
    if session.get('username') != 'teacher':
        return redirect(url_for('home'))

    # Track new submissions
    last_seen = session.get('last_seen_count', 0)
    new_count = len(submissions) - last_seen
    session['last_seen_count'] = len(submissions)

    return render_template('teacher.html', submissions=submissions, new_count=new_count)

# Route: Give Bonus to Student
@app.route('/give_bonus/<int:index>')
def give_bonus(index):
    if session.get('username') == 'teacher' and 0 <= index < len(submissions):
        submissions[index]['bonus'] = True
        with open(DATA_FILE, 'w') as f:
            json.dump(submissions, f)

    return redirect(url_for('teacher_portal'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8000)
