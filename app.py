from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'synapseLearn_secret_key'  # for session & flash messages

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['synapseLearn']
users_collection = db['users']
selections_collection = db['user_selections']

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        if users_collection.find_one({"username": username}):
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        users_collection.insert_one({"username": username, "password": hashed_password})
        flash('Registration successful! You can login now.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('topic_selection'))
        else:
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Topic Selection Page
@app.route('/topic_selection', methods=['GET', 'POST'])
def topic_selection():
    if 'username' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    # Topics structured by category
    topics = {
        "Programming": ["Python", "Java", "C", "C++", "JavaScript", "R", "Go", "Rust"],
        "DS & Algorithms": ["Arrays", "Linked Lists", "Stacks & Queues", "Trees & Graphs", "Sorting & Searching", "Dynamic Programming"],
        "Web Development": ["HTML/CSS/JS", "Flask", "Django", "React", "REST APIs"],
        "Databases": ["SQL", "MongoDB", "PostgreSQL", "Redis"],
        "AI/ML": ["Supervised Learning", "Unsupervised Learning", "Neural Networks", "Deep Learning", "NLP", "Computer Vision"],
        "Cloud/DevOps": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD Pipelines"],
        "Cybersecurity": ["Networking Basics", "Cryptography", "Ethical Hacking"]
    }

    skill_levels = ['Beginner', 'Intermediate', 'Advanced']

    if request.method == 'POST':
        username = session['username']
        skill_level = request.form['skill_level']
        topic = request.form['topic']

        # Save selection in MongoDB
        selections_collection.update_one(
            {"username": username},
            {"$set": {"topic": topic, "skill_level": skill_level}},
            upsert=True
        )

        flash(f'Hello {username}! You selected {skill_level} level and topic: {topic}', 'success')
        return render_template('confirmation.html', name=username, skill_level=skill_level, topic=topic)

    return render_template('topic_selection.html', topics=topics, skill_levels=skill_levels)

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
