"""
Flask Web Application demonstrating the Simple RDBMS
A task management system using our custom database
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from database_engine import DatabaseEngine
from rdbms import Column, DataType, Constraint

app = Flask(__name__)
app.secret_key = 'simple-rdbms-demo-secret-key'

# Initialize database and create tables
engine = DatabaseEngine()

def init_database():
    """Initialize the database with sample tables"""
    
    # Create users table
    create_users_sql = """
    CREATE TABLE users (
        id INT PRIMARY_KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE
    )
    """
    engine.execute(create_users_sql)
    
    # Create tasks table
    create_tasks_sql = """
    CREATE TABLE tasks (
        id INT PRIMARY_KEY,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT,
        user_id INT
    )
    """
    engine.execute(create_tasks_sql)
    
    # Insert sample data
    sample_users = [
        "INSERT INTO users (id, name, email) VALUES (1, 'Alice Johnson', 'alice@example.com')",
        "INSERT INTO users (id, name, email) VALUES (2, 'Bob Smith', 'bob@example.com')",
        "INSERT INTO users (id, name, email) VALUES (3, 'Carol Davis', 'carol@example.com')"
    ]
    
    sample_tasks = [
        "INSERT INTO tasks (id, title, description, status, user_id) VALUES (1, 'Complete project', 'Finish the RDBMS project', 'in_progress', 1)",
        "INSERT INTO tasks (id, title, description, status, user_id) VALUES (2, 'Write documentation', 'Create user manual', 'pending', 2)",
        "INSERT INTO tasks (id, title, description, status, user_id) VALUES (3, 'Test application', 'Run unit tests', 'completed', 1)",
        "INSERT INTO tasks (id, title, description, status, user_id) VALUES (4, 'Deploy to production', 'Deploy the web app', 'pending', 3)"
    ]
    
    for sql in sample_users + sample_tasks:
        engine.execute(sql)

# Initialize database on startup
init_database()

@app.route('/')
def index():
    """Home page showing overview"""
    # Get counts
    users_result = engine.execute("SELECT * FROM users")
    tasks_result = engine.execute("SELECT * FROM tasks")
    
    user_count = len(users_result.data) if users_result.data else 0
    task_count = len(tasks_result.data) if tasks_result.data else 0
    
    # Get recent tasks
    recent_tasks = engine.execute("SELECT * FROM tasks ORDER BY id DESC LIMIT 5")
    
    return render_template('index.html', 
                         user_count=user_count, 
                         task_count=task_count,
                         recent_tasks=recent_tasks.data[:5] if recent_tasks.data else [])

@app.route('/users')
def list_users():
    """List all users"""
    result = engine.execute("SELECT * FROM users")
    users = result.data if result.data else []
    
    return render_template('users/list.html', users=users)

@app.route('/users/new')
def new_user_form():
    """Show form to create new user"""
    return render_template('users/new.html')

@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    name = request.form.get('name')
    email = request.form.get('email')
    
    if not name:
        flash('Name is required', 'error')
        return redirect(url_for('new_user_form'))
    
    # Get next ID
    result = engine.execute("SELECT * FROM users")
    users = result.data if result.data else []
    next_id = max([user['id'] for user in users], default=0) + 1
    
    # Insert user
    sql = f"INSERT INTO users (id, name, email) VALUES ({next_id}, '{name}', '{email or ''}')"
    result = engine.execute(sql)
    
    if result.success:
        flash('User created successfully', 'success')
    else:
        flash(f'Error creating user: {result.message}', 'error')
    
    return redirect(url_for('list_users'))

@app.route('/users/<int:user_id>/edit')
def edit_user_form(user_id):
    """Show form to edit user"""
    result = engine.execute(f"SELECT * FROM users WHERE id = {user_id}")
    user = result.data[0] if result.data else None
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('list_users'))
    
    return render_template('users/edit.html', user=user)

@app.route('/users/<int:user_id>', methods=['POST'])
def update_user(user_id):
    """Update a user"""
    name = request.form.get('name')
    email = request.form.get('email')
    
    if not name:
        flash('Name is required', 'error')
        return redirect(url_for('edit_user_form', user_id=user_id))
    
    # Update user
    sql = f"UPDATE users SET name = '{name}', email = '{email or ''}' WHERE id = {user_id}"
    result = engine.execute(sql)
    
    if result.success:
        flash('User updated successfully', 'success')
    else:
        flash(f'Error updating user: {result.message}', 'error')
    
    return redirect(url_for('list_users'))

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete a user"""
    # First delete associated tasks
    engine.execute(f"DELETE FROM tasks WHERE user_id = {user_id}")
    
    # Then delete user
    result = engine.execute(f"DELETE FROM users WHERE id = {user_id}")
    
    if result.success:
        flash('User deleted successfully', 'success')
    else:
        flash(f'Error deleting user: {result.message}', 'error')
    
    return redirect(url_for('list_users'))

@app.route('/tasks')
def list_tasks():
    """List all tasks with user information"""
    # Get tasks and users separately, then join manually
    tasks_result = engine.execute("SELECT * FROM tasks")
    users_result = engine.execute("SELECT * FROM users")
    
    tasks = tasks_result.data if tasks_result.data else []
    users = users_result.data if users_result.data else []
    
    # Create user lookup dictionary
    user_lookup = {user['id']: user['name'] for user in users}
    
    # Add user_name to each task
    for task in tasks:
        task['user_name'] = user_lookup.get(task['user_id'], 'Unknown User')
    
    return render_template('tasks/list.html', tasks=tasks)

@app.route('/tasks/new')
def new_task_form():
    """Show form to create new task"""
    # Get users for dropdown
    users_result = engine.execute("SELECT * FROM users")
    users = users_result.data if users_result.data else []
    
    return render_template('tasks/new.html', users=users)

@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    title = request.form.get('title')
    description = request.form.get('description')
    status = request.form.get('status', 'pending')
    user_id = request.form.get('user_id')
    
    if not title:
        flash('Title is required', 'error')
        return redirect(url_for('new_task_form'))
    
    if not user_id:
        flash('User is required', 'error')
        return redirect(url_for('new_task_form'))
    
    # Get next ID
    result = engine.execute("SELECT * FROM tasks")
    tasks = result.data if result.data else []
    next_id = max([task['id'] for task in tasks], default=0) + 1
    
    # Insert task
    sql = f"INSERT INTO tasks (id, title, description, status, user_id) VALUES ({next_id}, '{title}', '{description or ''}', '{status}', {user_id})"
    result = engine.execute(sql)
    
    if result.success:
        flash('Task created successfully', 'success')
    else:
        flash(f'Error creating task: {result.message}', 'error')
    
    return redirect(url_for('list_tasks'))

@app.route('/tasks/<int:task_id>/edit')
def edit_task_form(task_id):
    """Show form to edit task"""
    # Get task
    task_result = engine.execute(f"SELECT * FROM tasks WHERE id = {task_id}")
    task = task_result.data[0] if task_result.data else None
    
    if not task:
        flash('Task not found', 'error')
        return redirect(url_for('list_tasks'))
    
    # Get users for dropdown
    users_result = engine.execute("SELECT * FROM users")
    users = users_result.data if users_result.data else []
    
    return render_template('tasks/edit.html', task=task, users=users)

@app.route('/tasks/<int:task_id>', methods=['POST'])
def update_task(task_id):
    """Update a task"""
    title = request.form.get('title')
    description = request.form.get('description')
    status = request.form.get('status')
    user_id = request.form.get('user_id')
    
    if not title:
        flash('Title is required', 'error')
        return redirect(url_for('edit_task_form', task_id=task_id))
    
    if not user_id:
        flash('User is required', 'error')
        return redirect(url_for('edit_task_form', task_id=task_id))
    
    # Update task
    sql = f"UPDATE tasks SET title = '{title}', description = '{description or ''}', status = '{status}', user_id = {user_id} WHERE id = {task_id}"
    result = engine.execute(sql)
    
    if result.success:
        flash('Task updated successfully', 'success')
    else:
        flash(f'Error updating task: {result.message}', 'error')
    
    return redirect(url_for('list_tasks'))

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Delete a task"""
    result = engine.execute(f"DELETE FROM tasks WHERE id = {task_id}")
    
    if result.success:
        flash('Task deleted successfully', 'success')
    else:
        flash(f'Error deleting task: {result.message}', 'error')
    
    return redirect(url_for('list_tasks'))

@app.route('/demo')
def demo_sql():
    """Demonstrate SQL queries"""
    # Run some demo queries
    queries = [
        ("Show all users", "SELECT * FROM users"),
        ("Show tasks with user names", "SELECT tasks.title, users.name FROM tasks JOIN users ON tasks.user_id = users.id"),
        ("Show pending tasks", "SELECT * FROM tasks WHERE status = 'pending'"),
        ("Count tasks by status", "SELECT status, COUNT(*) as count FROM tasks"),
        ("Show users with their task counts", "SELECT users.name, COUNT(tasks.id) as task_count FROM users JOIN tasks ON users.id = tasks.user_id")
    ]
    
    results = []
    for description, sql in queries:
        try:
            result = engine.execute(sql)
            results.append({
                'description': description,
                'sql': sql,
                'success': result.success,
                'message': result.message,
                'data': result.data[:10] if result.data else []  # Limit to 10 rows for display
            })
        except Exception as e:
            results.append({
                'description': description,
                'sql': sql,
                'success': False,
                'message': str(e),
                'data': []
            })
    
    return render_template('demo.html', results=results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
