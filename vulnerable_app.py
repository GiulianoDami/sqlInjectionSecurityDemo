
from flask import Flask, request, render_template_string

app = Flask(__name__)

def setup_database():
    import sqlite3
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL)''')
    # Insert sample users (vulnerable to injection)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO users (username, password) VALUES (?, ?)", [
            ('admin', 'admin123'),
            ('user1', 'password1'),
            ('user2', 'password2')
        ])
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template_string('''
        <html>
        <body>
            <h1>Vulnerable Login</h1>
            <form method="POST" action="/login">
                Username: <input type="text" name="username"><br>
                Password: <input type="password" name="password"><br>
                <input type="submit" value="Login">
            </form>
        </body>
        </html>
    ''')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # VULNERABLE - STRING CONCATENATION (DANGER!)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return f"Login successful! Welcome, {username}"
    else:
        return "Login failed. Invalid credentials."

if __name__ == '__main__':
    setup_database()
    app.run(port=5000, debug=True)
