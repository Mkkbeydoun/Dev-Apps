from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
from flask import session

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///komado.db'

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'

db = SQLAlchemy(app)
mail = Mail(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    notifications = db.relationship('Notification', backref='user', lazy=True)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50))
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='In Progress')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tasks = db.relationship('Task', backref='project', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='To Do')
    due_date = db.Column(db.DateTime)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def send_notification(user, message, type='system'):
    notification = Notification(
        user_id=user.id,
        message=message,
        type=type
    )
    db.session.add(notification)
    
    msg = Message(
        'Komado Portal Notification',
        sender='your-email@gmail.com',
        recipients=[user.email]
    )
    msg.body = message
    mail.send(msg)
    db.session.commit()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            error_message = "Invalid username or password. Please contact your organization's administrator to reset your password."
            return render_template('login.html', error=error_message)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/admin/profile', methods=['GET', 'POST'])
def admin_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        if user.role == 'Admin':
            user.username = request.form.get('username')
            user.email = request.form.get('email')
        if request.form.get('new_password'):
            user.password = request.form.get('new_password')
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('admin_profile.html', user=user)

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/add', methods=['POST'])
def add_user():
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
    new_user = User(
        username=request.form.get('username'),
        password=request.form.get('password'),
        email=request.form.get('email'),
        role=request.form.get('role')
    )
    db.session.add(new_user)
    db.session.commit()
    
    # Send welcome notification
    send_notification(
        new_user,
        f"Welcome to Komado Portal! Your account has been created with role: {new_user.role}",
        "system"
    )
    return redirect(url_for('admin_users'))

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        if request.form.get('password'):
            user.password = request.form.get('password')
        db.session.commit()
        
        # Send update notification
        send_notification(
            user,
            "Your account details have been updated by an administrator.",
            "system"
        )
        return redirect(url_for('admin_users'))
    
    return render_template('edit_user.html', user=user)

@app.route('/admin/users/delete/<int:user_id>')
def delete_user(user_id):
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_users'))

@app.route('/notifications')
def get_notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    notifications = Notification.query.filter_by(
        user_id=session['user_id'],
        read=False
    ).order_by(Notification.created_at.desc()).all()
    return jsonify([{
        'id': n.id,
        'message': n.message,
        'type': n.type,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for n in notifications])

@app.route('/notifications/mark-read/<int:notification_id>')
def mark_notification_read(notification_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == session['user_id']:
        notification.read = True
        db.session.commit()
    return jsonify({'success': True})

@app.route('/projects')
def projects():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    projects = Project.query.all()
    return render_template('projects.html', user=user, projects=projects)

@app.route('/create_project', methods=['POST'])
def create_project():
    if 'user_id' not in session or session['role'] not in ['Admin', 'Manager']:
        return redirect(url_for('login'))
    
    project = Project(
        title=request.form.get('title'),
        description=request.form.get('description'),
        manager_id=session['user_id']
    )
    db.session.add(project)
    db.session.commit()
    return redirect(url_for('projects'))

@app.route('/edit_project/<int:project_id>', methods=['POST'])
def edit_project(project_id):
    if 'user_id' not in session or session['role'] not in ['Admin', 'Manager']:
        return redirect(url_for('login'))
    
    project = Project.query.get_or_404(project_id)
    project.title = request.form.get('title')
    project.description = request.form.get('description')
    project.status = request.form.get('status')
    db.session.commit()
    return redirect(url_for('projects'))

@app.route('/delete_project/<int:project_id>')
def delete_project(project_id):
    if 'user_id' not in session or session['role'] not in ['Admin', 'Manager']:
        return redirect(url_for('login'))
    
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('projects'))

@app.route('/update_task_status/<int:task_id>', methods=['POST'])
def update_task_status(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task = Task.query.get_or_404(task_id)
    task.status = request.form.get('status')
    db.session.commit()
    return jsonify({'success': True})

@app.route('/add_task/<int:project_id>', methods=['POST'])
def add_task(project_id):
    if 'user_id' not in session or session['role'] not in ['Admin', 'Manager']:
        return redirect(url_for('login'))
    
    task = Task(
        title=request.form.get('title'),
        description=request.form.get('description'),
        assigned_to=request.form.get('assigned_to'),
        project_id=project_id,
        due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
    )
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('projects'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=4000)
