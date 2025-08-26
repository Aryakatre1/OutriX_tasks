Simple Bug Tracker
A Simple Web-Based Bug Tracking System
This project is a basic, single-user bug tracking system built as a web application. It allows a user to log new bugs, view a list of all existing bugs, and update the status of each bug. The application is designed to be lightweight and easy to set up for personal use or a small-scale project.

Technologies Used
Backend: Python 3 with the Flask framework

Database: MySQL

Frontend: HTML and CSS

Features
Add New Bug: A form to submit new bug reports with a title, description, and initial status.

View All Bugs: A dashboard that displays a list of all reported bugs.

Update Bug Status: An option to change the status of a bug (e.g., from Open to In Progress or Closed).

Project Structure
.
├── app.py          # Main Flask application file
├── static/
│   └── css/
│       └── style.css   # Styles for the web pages
├── templates/
│   ├── add_bug.html    # Page to add a new bug
│   ├── bug_detail.html # Page to view bug details
│   ├── edit_bug.html   # Page to edit a bug
│   ├── home.html       # The main dashboard
│   ├── login.html      # Login page
│   └── register.html   # Registration page
└── README.md

Setup and Installation
Prerequisites: Ensure you have Python 3 and MySQL installed on your system.

Install Python Libraries: Open your terminal or command prompt, navigate to the project directory, and install the required libraries using pip:

pip install Flask mysql-connector-python

Database Configuration:

Create a MySQL database named bugtracker.

Create a table named bugs with the following columns:

CREATE TABLE bugs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50)
);

Open app.py and update the database connection details (host, user, password, and database name) to match your MySQL setup.

Run the Application:

From your terminal, run the app.py file:

python app.py

Access the Application: Open your web browser and navigate to http://127.0.0.1:5000 to use the bug tracker.
