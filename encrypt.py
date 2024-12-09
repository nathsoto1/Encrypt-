from flask import Flask, render_template, request, redirect, flash
import os
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

# Flask App Setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# Encryption Helper Functions
def encrypt(text, s):
    result = ""
    for char in text:
        if char.isalpha():
            shift_base = 65 if char.isupper() else 97
            result += chr((ord(char) - shift_base + s) % 26 + shift_base)
        else:
            result += char
    return result

def decrypt(text, s):
    return encrypt(text, -s)

# Database Setup
DATABASE = 'passwords.db'
SHIFT = 4  # Simple encryption key

def init_db():
    if not os.path.exists(DATABASE):
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE passwords (
                                id INTEGER PRIMARY KEY,
                                account TEXT NOT NULL,
                                password TEXT NOT NULL)''')
            conn.commit()

# Routes
@app.route('/')
def index():
    # Fetch all accounts and decrypted passwords
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, account, password FROM passwords')
        records = cursor.fetchall()
        passwords = [{"id": row[0], "account": row[1], "password": decrypt(row[2], SHIFT)} for row in records]
    return render_template('index.html', passwords=passwords)

@app.route('/add', methods=['POST'])
def add_password():
    account = request.form.get('account')
    password = request.form.get('password')
    if not account or not password:
        flash("Account and password are required!", "error")
        return redirect('/')
    
    encrypted_password = encrypt(password, SHIFT)
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO passwords (account, password) VALUES (?, ?)', (account, encrypted_password))
        conn.commit()
    
    flash("Password added successfully!", "success")
    return redirect('/')

@app.route('/delete/<int:password_id>', methods=['POST'])
def delete_password(password_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM passwords WHERE id = ?', (password_id,))
        conn.commit()
    
    flash("Password deleted successfully!", "success")
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)