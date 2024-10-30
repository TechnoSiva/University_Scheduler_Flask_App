from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, DateField
from wtforms.validators import InputRequired, Length

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a3d2e9b1c2f3d8e7f4b6a9c1b8f2e5d1' 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# In-memory database of users and their roles
users = {
    'admin': {'password': 'adminpass', 'role': 'admin'},
    'student': {'password': 'studentpass', 'role': 'student'}
}

# Temporary storage for courses, instructors, rooms, and time slots
initial_courses = ['AIML', 'FLAT', 'OOAD', 'OS', 'DE']
instructors = ['Dr. Niranjan Panigrahi', 'Dr. Debasish Mohapatra', 'Mrs. Sasmita Rani Behera', 'Mrs. Ranumayee Sing', 'Dr. Rashmi Ranjan Sahoo']
rooms = ['Room 413 A', 'Room 413 B']
time_slots = ['10:00-11:00', '11:00-12:00', '12:00-1:00', '2:00-3:00', '3:00-4:00', '4:00-5:00']

# Temporary storage for scheduled courses
scheduled_courses = []

class User(UserMixin):
    def __init__(self, username, role):
        self.id = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    user = users.get(user_id)
    if user:
        return User(user_id, user['role'])
    return None

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = users.get(username)
        if user and user['password'] == password:
            login_user(User(username, user['role']), remember=form.remember.data)
            flash('Login successful!')
            return redirect(url_for('scheduler'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/scheduler', methods=['GET', 'POST'])
@login_required
def scheduler():
    global scheduled_courses
    if request.method == 'POST':
        course = request.form['course']
        instructor = request.form['instructor']
        room = request.form['room']
        time_slot = request.form['time_slot']
        date = request.form['date']
        
        # Check for conflicts
        conflict_message = is_conflict(course, instructor, room, time_slot, date, scheduled_courses)
        if conflict_message:
            flash(f"Error: {conflict_message}", 'error')
        else:
            # If no conflicts, add the course to the schedule
            scheduled_courses.append({
                'course': course,
                'instructor': instructor,
                'room': room,
                'time_slot': time_slot,
                'date': date
            })
            flash("Course added successfully!", 'success')

    # Render scheduler with all current courses, instructors, rooms, and time slots
    return render_template('scheduler.html', courses=initial_courses, instructors=instructors, rooms=rooms, time_slots=time_slots, scheduled_courses=scheduled_courses)

def is_conflict(course, instructor, room, time_slot, date, scheduled_courses):
    for scheduled in scheduled_courses:
        if (scheduled['date'] == date and
                scheduled['time_slot'] == time_slot and
                (scheduled['room'] == room or scheduled['instructor'] == instructor)):
            return f"Conflict with {scheduled['course']} on {date} at {time_slot}."
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
