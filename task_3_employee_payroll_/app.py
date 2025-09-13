import sqlite3
from flask import Flask, render_template, request, redirect, url_for

# Initialize Flask app
app = Flask(__name__)

# Define database file path
DATABASE = 'payroll.db'

def get_db_connection():
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def create_table():
    """Creates the employees table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            position TEXT NOT NULL,
            monthly_salary REAL NOT NULL,
            bonuses REAL,
            tax_rate REAL,
            deductions REAL
        );
    ''')
    conn.commit()
    conn.close()

# Create the database table on application start
create_table()

def calculate_net_salary(employee):
    """Calculates the final net salary for an employee."""
    monthly_salary = employee['monthly_salary']
    bonuses = employee['bonuses']
    tax_rate = employee['tax_rate']
    deductions = employee['deductions']
    
    # Gross salary is the sum of monthly salary and bonuses
    gross_salary = monthly_salary + bonuses
    
    # Calculate tax amount
    tax_amount = gross_salary * (tax_rate / 100)
    
    # Net salary is gross salary minus tax and other deductions
    net_salary = gross_salary - tax_amount - deductions
    
    return net_salary

@app.route('/')
def index():
    """Renders the form to add a new employee."""
    return render_template('add_employee.html')

@app.route('/add_employee', methods=['POST'])
def add_employee():
    """Handles the form submission and saves new employee to the database."""
    if request.method == 'POST':
        full_name = request.form['full_name']
        position = request.form['position']
        monthly_salary = float(request.form.get('monthly_salary', 0))
        bonuses = float(request.form.get('bonuses', 0))
        tax_rate = float(request.form.get('tax_rate', 0))
        deductions = float(request.form.get('deductions', 0))

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO employees (full_name, position, monthly_salary, bonuses, tax_rate, deductions) VALUES (?, ?, ?, ?, ?, ?)",
            (full_name, position, monthly_salary, bonuses, tax_rate, deductions)
        )
        conn.commit()
        conn.close()
        
        # Redirect to the main page after adding the employee
        return redirect(url_for('view_employees'))

@app.route('/employees')
def view_employees():
    """Fetches and displays employees from the database, with optional search filter."""
    conn = get_db_connection()
    
    # Get the search query from the URL, if it exists
    search_query = request.args.get('query', '')
    
    if search_query:
        # If there's a search query, filter the employees
        # Use LIKE and a wildcard (%) to find partial matches
        employees = conn.execute("SELECT * FROM employees WHERE full_name LIKE ?", ('%' + search_query + '%',)).fetchall()
    else:
        # If no search query, fetch all employees
        employees = conn.execute("SELECT * FROM employees").fetchall()
    
    # Create a list of dictionaries with all employee data and the calculated net salary
    employees_with_net_salary = []
    for employee in employees:
        employee_dict = dict(employee)
        employee_dict['net_salary'] = calculate_net_salary(employee_dict)
        employees_with_net_salary.append(employee_dict)
        
    conn.close()
    return render_template('view_employees.html', employees=employees_with_net_salary, search_query=search_query)

@app.route('/edit_employee/<int:employee_id>')
def edit_employee(employee_id):
    """Renders the edit form for a specific employee."""
    conn = get_db_connection()
    employee = conn.execute('SELECT * FROM employees WHERE employee_id = ?', (employee_id,)).fetchone()
    conn.close()
    if employee is None:
        # Handle case where employee is not found
        return redirect(url_for('view_employees'))
    return render_template('edit_employee.html', employee=employee)

@app.route('/update_employee/<int:employee_id>', methods=['POST'])
def update_employee(employee_id):
    """Handles the form submission for updating an employee's details."""
    if request.method == 'POST':
        full_name = request.form['full_name']
        position = request.form['position']
        monthly_salary = float(request.form.get('monthly_salary', 0))
        bonuses = float(request.form.get('bonuses', 0))
        tax_rate = float(request.form.get('tax_rate', 0))
        deductions = float(request.form.get('deductions', 0))

        conn = get_db_connection()
        conn.execute(
            "UPDATE employees SET full_name = ?, position = ?, monthly_salary = ?, bonuses = ?, tax_rate = ?, deductions = ? WHERE employee_id = ?",
            (full_name, position, monthly_salary, bonuses, tax_rate, deductions, employee_id)
        )
        conn.commit()
        conn.close()
        
        return redirect(url_for('view_employees'))

@app.route('/delete_employee/<int:employee_id>')
def delete_employee(employee_id):
    """Deletes an employee from the database."""
    conn = get_db_connection()
    conn.execute('DELETE FROM employees WHERE employee_id = ?', (employee_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('view_employees'))

if __name__ == '__main__':
    app.run(debug=True)








