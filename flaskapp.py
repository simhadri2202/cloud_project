from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Used for session management

def get_db():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.path.join(BASE_DIR, "test_database.db")

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    return conn,c
def close_db(conn):
    conn.commit()
    conn.close()

conn,c = get_db()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (username TEXT, password TEXT, firstname TEXT, lastname TEXT, email TEXT)''')
close_db(conn)

@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/register',methods = ['GET'])
def register():
    return render_template('register.html')

@app.route('/register_data', methods=['POST'])
def store_user():
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    address = request.form['address']
    
    conn,c = get_db()
    c.execute("INSERT INTO users (username, password, f_name, l_name, email,address) VALUES (?, ?, ?, ?, ?,?)",
              (username, password, first_name, last_name, email,address))
    close_db(conn)

    return redirect(url_for('display_user', username = username))


@app.route('/diplay_user/<username>')
def display_user(username):
    conn,c = get_db()
    c.execute("select username,f_name,l_name,email,address from users where username = ?",(username,))
    user = c.fetchone()
    if user:
        return render_template('user_details.html', user=user)
    return "User not found!", 404

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_check', methods=['POST'])
def login_check():
    user_name = request.form['username']
    password = request.form['password']
    print(user_name)
    conn,c = get_db()
    c.execute("select username,password from users where username = ?",(user_name,))
    user = c.fetchone()
    close_db(conn)

    if user and user[1] == password:
        session['user'] = user_name
        return redirect(url_for('display_user', username=user_name))
    return "Invalid credentials!", 401

@app.route('/log_out')
def logout():
    return render_template('log_out.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        file.save(os.path.join('uploads', file.filename))
        word_count = count_words(os.path.join('uploads', file.filename))
        return render_template('user_details.html', word_count=word_count)

def count_words(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        words = content.split()
        return len(words)

if __name__ == '__main__':
    app.run(debug=True)
