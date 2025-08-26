from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

# Create an instance of the Flask class
app = Flask(__name__)

# Database configuration
db_config = {
    'host': '127.0.0.1', 
    'user': 'root',
    'password': 'MyBugTrackerPassword123!', 
    'database': 'bug_tracker'
}

app.secret_key = b'\x080E\xec\x0bv]`\x9d\xe9\x7f\xa2i\xe5Uk\xc4a\x16\x857\x0e\xbd\xa0'

# Helper function to get a database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Define the route for the home page
@app.route('/')
def home():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get the sorting parameter from the URL, defaulting to 'created_at' if not present
        sort_by = request.args.get('sort', 'created_at')

        # Map the URL parameter to a valid SQL column name
        sort_map = {
            'priority': 'priority',
            'status': 'status',
            'created': 'created_at'
        }

        # Use the mapped value, or default to 'created_at' if the parameter is invalid
        order_by = sort_map.get(sort_by, 'created_at')

        # SQL query to select all bugs and sort them
        if order_by == 'priority':
            # This sorts 'High' first, then 'Medium', then 'Low'
            cursor.execute("SELECT * FROM bugs ORDER BY FIELD(priority, 'High', 'Medium', 'Low')")
        elif order_by == 'status':
            # This sorts 'Open' first, then 'In Progress', etc.
            cursor.execute("SELECT * FROM bugs ORDER BY FIELD(status, 'Open', 'In Progress', 'Resolved', 'Closed')")
        else:
            # Default sort by created date
            cursor.execute("SELECT * FROM bugs ORDER BY created_at DESC")
        
        bugs = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # We will pass the list of bugs to our HTML template
        return render_template('home.html', bugs=bugs)

    except mysql.connector.Error as err:
        return f"<h1>Error: Could not connect to the database.</h1><p>{err}</p>"
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            username = request.form['username']
            password = request.form['password']

            # Hash the password for security
            hashed_password = generate_password_hash(password)

            sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
            val = (username, hashed_password)
            cursor.execute(sql, val)

            conn.commit()
            cursor.close()
            conn.close()

            # Redirect to a login page or the home page after successful registration
            return redirect(url_for('home'))

        except mysql.connector.Error as err:
            return f"<h1>Error: Could not register user.</h1><p>{err}</p>"
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            username = request.form['username']
            password = request.form['password']

            # Find the user by username
            sql = "SELECT * FROM users WHERE username = %s"
            val = (username,)
            cursor.execute(sql, val)
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user and check_password_hash(user['password'], password):
                # Password is correct, store the user in the session
                session['user_id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('home'))
            else:
                # Login failed
                return "<h1>Invalid username or password.</h1>"

        except mysql.connector.Error as err:
            return f"<h1>Error: Could not log in.</h1><p>{err}</p>"
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('home'))    

@app.route('/add_bug', methods=['GET', 'POST'])
def add_bug():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = "INSERT INTO bugs (title, description, status, priority) VALUES (%s, %s, %s, %s)"
            val = (
                request.form['title'], 
                request.form['description'], 
                request.form['status'], 
                request.form['priority']
            )
            cursor.execute(sql, val)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Redirect to the home page after successful submission
            return redirect(url_for('home'))
            
        except mysql.connector.Error as err:
            return f"<h1>Error: Could not save the bug.</h1><p>{err}</p>"

    # This code will run for a GET request to display the form
    return render_template('add_bug.html')

@app.route('/delete_bug/<int:bug_id>', methods=['GET'])
def delete_bug(bug_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # SQL query to delete the bug with the given ID
        sql = "DELETE FROM bugs WHERE id = %s"
        val = (bug_id,)
        cursor.execute(sql, val)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Redirect to the home page after deletion
        return redirect(url_for('home'))
        
    except mysql.connector.Error as err:
        return f"<h1>Error: Could not delete the bug.</h1><p>{err}</p>"
    
@app.route('/edit_bug/<int:bug_id>', methods=['GET', 'POST'])
def edit_bug(bug_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            sql = "UPDATE bugs SET title = %s, description = %s, status = %s, priority = %s WHERE id = %s"
            val = (
                request.form['title'],
                request.form['description'],
                request.form['status'],
                request.form['priority'],
                bug_id
            )
            cursor.execute(sql, val)

            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('home'))

        except mysql.connector.Error as err:
            return f"<h1>Error: Could not update the bug.</h1><p>{err}</p>"
    else: # This is a GET request
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = "SELECT * FROM bugs WHERE id = %s"
            val = (bug_id,)
            cursor.execute(sql, val)
            
            bug = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if bug:
                return render_template('edit_bug.html', bug=bug)
            else:
                return "<h1>Bug not found.</h1>"
                
        except mysql.connector.Error as err:
            return f"<h1>Error: Could not fetch bug data.</h1><p>{err}</p>"

@app.route('/bug/<int:bug_id>')
def bug_detail(bug_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        sql = "SELECT * FROM bugs WHERE id = %s"
        val = (bug_id,)
        cursor.execute(sql, val)
        
        bug = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if bug:
            return render_template('bug_detail.html', bug=bug)
        else:
            return "<h1>Bug not found.</h1>"
            
    except mysql.connector.Error as err:
        return f"<h1>Error: Could not fetch bug data.</h1><p>{err}</p>"            

# Run the app
if __name__ == '__main__':
    app.run(debug=True)