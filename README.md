📌 Jira-Style Task Manager — Flask + PostgreSQL
A full-featured project and task management system with Role-Based Access Control (RBAC) for Admin, Manager, Developer, and Viewer roles. Inspired by Jira, it allows structured project planning, team assignment, task tracking, and communication — all built with Flask, PostgreSQL, and modern web technologies.

🚀 Features
Role-Based Access Control (RBAC) — Admin, Manager, Developer, Viewer

Project Management — Create, edit, approve, and archive projects

Task Management — Assign tasks, track statuses (To Do, In Progress, Done), set priorities & deadlines

Team Assignment — Admin assigns managers and developers to specific projects

User Authentication — Secure login & signup with hashed passwords

Email Notifications — Integrated with Flask-Mail for task updates and approvals

Clean Modular Architecture — Follows MVC with controllers/, routes/, models/, templates/, and static/ directories for scalability

🛠️ Tech Stack
Frontend: HTML, CSS, JavaScript, Bootstrap, Jinja2 Templates

Backend: Python, Flask, Flask-Mail

Database: PostgreSQL (via SQLAlchemy ORM)

Other Tools: Flask-Login, Flask-WTF, Werkzeug Security

📂 Folder Structure

Jira-Task-Manager/
│── app.py
│── requirements.txt
│── config.py
│
├── controllers/      # Business logic
├── routes/           # Flask routes for each module
├── models/           # SQLAlchemy models
├── templates/        # HTML templates (Jinja2)
├── static/           # CSS, JS, images
└── utils/            # Helper functions (email, authentication)
⚡ Installation & Setup

# 1️⃣ Clone the repository
git clone https://github.com/yourusername/jira-task-manager.git
cd jira-task-manager

# 2️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Configure database in config.py
SQLALCHEMY_DATABASE_URI = "postgresql://username:password@localhost/jira_task_manager"

# 5️⃣ Run migrations (if using Flask-Migrate)
flask db init
flask db migrate
flask db upgrade

# 6️⃣ Start the server
flask run
📧 Email Notifications
This project uses Flask-Mail for email alerts.
Configure the SMTP settings in config.py:

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your-email@gmail.com'
MAIL_PASSWORD = 'your-password'

📈 Scalability & Optimization
Modular architecture for maintainability

Separate layers for business logic and routes
