from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, make_response
import sqlite3
import os
from datetime import datetime
import random
import string

app = Flask(__name__)
app.secret_key = 'supersecretkey'
SECRET_FILE = 'secret.txt'

def generate_session_token(length=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

DATABASE = 'database.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, description TEXT, status TEXT, assigned_to TEXT, start_time TEXT, end_time TEXT)''')
    cursor.execute('''INSERT OR IGNORE INTO users (id, username, password, role) VALUES (1, "admin", "admin123", "admin")''')
    conn.commit()
    conn.close()


@app.route('/.../.../.../secret.txt')
def secret_file():
    if 'username' in session:
        return send_file('secret.txt', as_attachment=True)
    return "Unauthorized access."

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            if ';' in password or '--' in password:
                cursor.executescript(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}';")
            else:
                cursor.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
            
            user = cursor.fetchone()
        except sqlite3.OperationalError as e:
            conn.close()
            flash(f"SQL Error: {e}", "error")
            return render_template('login.html')

        conn.close()

        if user:
            session['username'] = user[1]
            session['role'] = user[3]

            session_token = generate_session_token()
            session['session_token'] = session_token  

            response = make_response(redirect(url_for('admin_page') if user[3] == 'admin' else url_for('user_page')))
            response.set_cookie('session_token', session_token, httponly=False) 
            return response
        else:
            flash("Invalid Username or Password. Please try again.", "error")
    
    return render_template('login.html')


@app.route('/reset_db')
def reset_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.executescript('''
    DROP TABLE IF EXISTS users;
    CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT);
    INSERT INTO users (id, username, password, role) VALUES (1, 'admin', '1', 'admin');
    INSERT INTO users (id, username, password, role) VALUES (2, 'user1', 'userpass', 'user');
    ''')
    conn.commit()
    conn.close()
    flash("Database has been reset successfully. Admin password set to '1'.", "success")
    return redirect(url_for('login'))

    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'user' 

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            flash("Username already exists. Please choose a different username.", "error")
            return redirect(url_for('register'))
        
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        conn.close()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')
@app.route('/user_page', methods=['GET', 'POST'])
def user_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        assigned_to = session['username']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title, description, status, assigned_to, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?)", (title, description, status, assigned_to, start_time, end_time))
        conn.commit()
        conn.close()
        flash("Task added successfully!")
        return redirect(url_for('user_page'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE assigned_to = ?", (session['username'],))
    tasks = cursor.fetchall()
    conn.close()

    static_tasks = [
        {"title": "1. Login to the admin page", "description": "Go to the admin page and log in as an administrator.", "status": "Not started"},
        {"title": "2. Break table with users", "description": "Try to perform SQL injection and break the table.", "status": "Not started"},
        {"title": "3. Populate user database with bots", "description": "Use a script to populate the database with bot users.", "status": "Not started"},
        {"title": "4. Find secret.txt file", "description": "Find the secret.txt file and get the hidden phrase.", "status": "Not started"},
        {"title": "5.  Steal session token", "description": "Gain access to user_page without entering any data.", "status": "Not started"}
    ]

    if request.method == 'POST':
        entered_phrase = request.form.get('secret_phrase')
        if not os.path.exists(SECRET_FILE):
            flash("Secret file not found. Please check the file path.", "error")
            return render_template('user_page.html', tasks=tasks, static_tasks=static_tasks, username=session['username'])
        
        try:
            with open(SECRET_FILE, 'r', encoding='utf-8') as f:
                correct_phrase = f.read().strip()
        except Exception as e:
            flash(f"Error reading the secret file: {e}", "error")
            return render_template('user_page.html', tasks=tasks, static_tasks=static_tasks, username=session['username'])
        
        if entered_phrase == correct_phrase:
            flash("Successfully completed, congratulations!", "success")
        else:
            flash("Incorrect phrase. Try again.", "error")

    return render_template('user_page.html', tasks=tasks, static_tasks=static_tasks, username=session['username'])

@app.route('/admin_page')
def admin_page():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    return render_template('admin.html', users=users)

@app.route('/view_tasks/<int:user_id>')
def view_tasks(user_id):
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE assigned_to = (SELECT username FROM users WHERE id = ?)", (user_id,))
    tasks = cursor.fetchall()
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    username = cursor.fetchone()[0]
    conn.close()

    return render_template('view_tasks.html', tasks=tasks, username=username)

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE assigned_to = (SELECT username FROM users WHERE id = ?)", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash("User and their tasks deleted successfully.", "success")
    return redirect(url_for('admin_page'))

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']
        new_role = request.form['role']

        cursor.execute("UPDATE users SET username = ?, password = ?, role = ? WHERE id = ?", (new_username, new_password, new_role, user_id))
        conn.commit()
        conn.close()
        flash("User updated successfully.", "success")
        return redirect(url_for('admin_page'))

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return render_template('edit_user.html', user=user)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        old_password = request.form['old_password']
        new_username = request.form['new_username']
        new_password = request.form['new_password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (session['username'], old_password))
        user = cursor.fetchone()
        if user:
            cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (new_username, new_password, user[0]))
            session['username'] = new_username
            flash("Profile updated successfully.", "success")
            conn.commit()
        else:
            flash("Old password is incorrect. Unable to update profile.", "error")
        conn.close()
        return redirect(url_for('settings'))

    return render_template('settings.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)



