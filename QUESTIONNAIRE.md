# Interview Questionnaire — Jira Dashboard (Flask)

This file contains likely interviewer questions about your Flask Jira Dashboard project, model answers you can memorize or adapt, and code examples where appropriate. Use this as a cheat-sheet for interview prep and as a script during live interviews.

---

## Quick Tips Before Interview

- Start each answer by summarizing the high-level idea in 1 sentence.
- If asked to write code, explain the approach first, then write clean, tested code.
- When unsure, explain the brute-force approach, then iterate to optimizations.
- Relate algorithmic answers to your project when possible.

---

## Project Overview (One-liner)

"A Flask-based team/project/task management system with role-based access (admin, manager, developer, visitor), team/project many-to-many relationships, soft deletes, and basic email notifications using Flask-Mailman and SQLAlchemy as the ORM." 

Use the above sentence to open any project discussion.

---

**SECTION A — High-level Project Questions**

Q: Walk me through your project architecture.

A (script):
- "I used Flask with Blueprints to separate features by role: `auth`, `admin`, `manager`, `developer`, `visitor`, and `common`. Models are defined using SQLAlchemy in `models/` and migrations via Flask-Migrate. Controllers handle business logic and templates in `templates/` render views. The app uses environment variables for configuration, and SMTP credentials for email via Flask-Mailman."

Q: Why Flask and not Django?

A (script):
- "Flask offered lightweight control for me to structure blueprints and controllers explicitly. I wanted to implement authentication, authorization, and SQLAlchemy relationships myself to demonstrate understanding rather than relying on Django's admin and built-in features."

Q: What would you improve if this went to production?

A (script):
- "Hash passwords (already planned), add CSRF protection (Flask-WTF), switch to a production WSGI server (gunicorn), add distributed sessions or JWTs for scaling, add unit and integration tests (pytest), Dockerize, and add monitoring/logging (Sentry/Prometheus)."

---

**SECTION B — Database & Models**

Q: Explain your DB schema and relationships.

A (script):
- "Key models: `LoginInfo`, `UserProfile`, `Team`, `TeamMember` (junction), `Project`, `TeamProject` (junction), `Task`, `SubTask`, `Notification`, and `Note`.
  - Users (LoginInfo) have 1:1 profile.
  - Teams and Users are M:N via `TeamMember`.
  - Projects belong to a team (owner) and are shared with other teams via `TeamProject`.
  - Tasks belong to Projects and have many SubTasks.
  - Soft deletes are used with `is_deleted` flags. Enums enforce limited values for roles and statuses."

Q: Why use junction tables (TeamMember, TeamProject)?

A (script):
- "To keep normalized relational integrity and to allow additional metadata (like membership role) on relationships. It also makes queries and joins straightforward in SQLAlchemy and enforces uniqueness when required."

Q: Any problems with current DB design?

A (script):
- "Potential N+1 query issues in templates — solve with `joinedload()`; missing indexes on frequently filtered columns (`is_deleted`, `assigned_to_user_id`) — add `index=True`; Sprint model exists but not integrated with Task — add `sprint_id` or remove. Also add unique constraints for junction tables."

Code example — add an index to a column:

```python
# models/task.py (example)
assigned_to_user_id = db.Column(
    db.Integer,
    db.ForeignKey('login_info.id', ondelete='SET NULL'),
    nullable=True,
    index=True
)
is_deleted = db.Column(db.Boolean, default=False, index=True)
```

Q: How do you prevent N+1 queries?

A (script):
- "Use SQLAlchemy eager loading (`joinedload`, `subqueryload`) on relationships that will be iterated in templates, e.g., load `Task.assignee` and `assignee.profile` in one query."

Code example:

```python
from sqlalchemy.orm import joinedload

tasks = Task.query.options(
    joinedload(Task.assignee).joinedload(LoginInfo.profile)
).filter_by(project_id=project_id).all()
```

---

**SECTION C — Authentication & Security**

Q: How is authentication implemented?

A (script):
- "Session-based authentication: after validating credentials we set `session['user_id']`, `session['username']`, and `session['role']`. We have decorator functions (`admin_required`, `manager_required`, `developer_required`) that read the session and enforce access."

Q: Are passwords stored securely?

A (script):
- "Not originally — I will (and can) add `werkzeug.security.generate_password_hash` to hash passwords on signup and `check_password_hash` on login. For an existing DB, use a hybrid login strategy or run a one-time migration script to hash all current plain-text passwords."

Code example — hash on signup & check on login (hybrid-ready):

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Signup
hashed = generate_password_hash(raw_password)
user.password = hashed

# Login (hybrid)
if user.password.startswith('pbkdf2:'):
    ok = check_password_hash(user.password, provided_password)
else:
    ok = (user.password == provided_password)
    if ok:
        user.password = generate_password_hash(provided_password)
        db.session.commit()
```

Q: Should emails be hashed?

A (script):
- "No. Emails must be queryable for login, notifications, and contacting users. Hashing emails ruins functionality. Instead, secure transport (HTTPS) and access to DB should be controlled."

Q: How to prevent CSRF and XSS?

A (script):
- "Add Flask-WTF (CSRF token for forms). Sanitize user input before rendering and use Jinja2 autoescaping (default). For any user-submitted HTML, sanitize with `bleach`."

---

**SECTION D — Routes, Blueprints & Controllers**

Q: Why use Blueprints?

A (script):
- "Blueprints modularize the app by feature or role and keep routes and controllers organized; they make the codebase easier to navigate and allow blueprints to be reused or registered with different URL prefixes."

Q: Give an example of a decorator for authorization.

A (script + code):
- "We implemented `admin_required` which checks session role and redirects if unauthorized."

```python
from functools import wraps
from flask import session, redirect, url_for, flash

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated
```

Q: How do you test endpoints?

A (script):
- "Use Flask's test client and pytest. Create fixtures for app context and temporary DB, test key flows like signup, login, project creation, and ACL enforcement."

Example (pytest style):

```python
def test_signup_and_login(client, db_session):
    client.post('/auth/signup', data={...})
    resp = client.post('/auth/login', data={'username':'u','password':'p'})
    assert resp.status_code == 302
```

---

**SECTION E — SQLAlchemy & Common Query Questions**

Q: Write a query to get all projects accessible to a user via team membership.

A (script + code):
- "Join `TeamMember`, `TeamProject`, and `Project` to find projects for teams the user belongs to."

```python
projects = (
    Project.query
    .join(Project.team_links)          # TeamProject
    .join(TeamProject.team)
    .join(Team.members)
    .filter(TeamMember.user_id == user_id, Project.is_deleted == False)
    .distinct()
    .all()
)
```

Q: How do you add pagination?

A (script + code):
- Use Flask-SQLAlchemy `paginate` or `.limit().offset()`.

```python
page = request.args.get('page', 1, type=int)
pagination = Project.query.filter_by(is_deleted=False).paginate(page, per_page=10)
projects = pagination.items
```

Q: How to handle large-read reporting queries?

A (script):
- "Use efficient joins, projection of only required columns, DB indexes, and consider materialized views for heavy reports or perform them in background tasks and cache results."

---

**SECTION F — Emails & Background Tasks**

Q: How do you send emails and how to avoid blocking requests?

A (script):
- "Currently we use Flask-Mailman synchronous sends. For production, delegate to a background worker (Celery or RQ) so sending email doesn't block. Use transactional events (commit success triggers) to enqueue email tasks."

Code sketch using Celery:

```python
# tasks.py
from celery import Celery
celery = Celery(...)

@celery.task
def send_email_async(subject, body, to):
    # configure mail client and send
    pass

# in controller after commit
send_email_async.delay(subject, message, [user.email])
```

---

**SECTION G — Testing & CI/CD**

Q: What tests would you add first?

A (script):
- "Unit tests for models (validation), integration tests for signup/login flows, ACL tests for each role, and a few end-to-end tests for common user journeys. Use `pytest`, a test database, and CI to run tests on every push."

Q: How to add CI?

A (script):
- "Add a GitHub Actions workflow that runs `pytest`, lints code (`flake8`/`black`), and builds a Docker image. Optionally run static security scans."

---

**SECTION H — Deployment**

Q: How would you deploy this app?

A (script):
- "Dockerize the app, use `gunicorn` behind Nginx, host on cloud provider (Azure/AWS/GCP) with managed Postgres. Use environment variables for secrets, add logging and monitoring (Sentry/Prometheus), and run migrations as part of deployment pipeline. Use Redis for background jobs and caching."

Dockerfile sketch:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app:app", "-w", "4", "-b", "0.0.0.0:8000"]
```

---

**SECTION I — DSA & Algorithms (Interview Support)**

Q: If asked to solve a small algorithm (Two Sum), how to answer?

A (script + code):
- "Explain brute force (O(n^2)) then optimized solution with hashmap (O(n)). Then code it."

```python
# Two Sum (Python)
def two_sum(nums, target):
    seen = {}
    for i, val in enumerate(nums):
        want = target - val
        if want in seen:
            return [seen[want], i]
        seen[val] = i
    return None
```

Q: How to bridge DSA skills to your project?

A (script):
- "Discussing algorithmic patterns: I used hash maps for O(1) lookups when matching membership and JOIN optimization when querying relationships. When optimizing queries, the same logic applies — choose data structures that reduce repeated work."

---

**SECTION J — Common Hard Questions & Good Scripts**

Q: Explain soft deletes and pros/cons.

A (script):
- "Soft delete uses a boolean `is_deleted` flag instead of removing rows. Pros: ability to restore, audit trail, safe when foreign keys reference rows. Cons: every query must filter `is_deleted=False`, harder to keep DB clean, and indexes may need tuning. For critical tables, adding `deleted_at` and `deleted_by` helps auditing."

Q: What is an N+1 problem and how to fix it?

A (script):
- "N+1 occurs when you query a set of parent objects and then perform a new query for each parent's related object. Fix with eager loading in ORM, or restructure queries to join and fetch related rows in bulk."

Q: How would you migrate plain-text passwords to hashed passwords without downtime?

A (script + code):
- "Implement a hybrid login check that accepts both hashed and plain-text passwords and upgrades plain-text to a hash on successful login. Also run a migration script to hash all passwords if possible."

Migration script example (one-time):

```python
from app import app, db
from models.login_info import LoginInfo
from werkzeug.security import generate_password_hash

with app.app_context():
    for u in LoginInfo.query.all():
        if not u.password.startswith('pbkdf2:'):
            u.password = generate_password_hash(u.password)
    db.session.commit()
```

---

**SECTION K — Behavioral & Soft Questions (Short Scripts)**

Q: Tell me about a tough bug you fixed.

A (script):
- "I fixed an N+1 query problem on the project reports page by using `joinedload()` which reduced DB queries from O(N) to O(1) and improved page load time significantly. I wrote a unit test to ensure related data was loaded as expected."

Q: Why should we hire you?

A (script):
- "I build full-stack features end-to-end: data model, business logic, UI, and deployment. I prioritize maintainability, I can learn fast, and I can ship features quickly — which is exactly what teams need. I also actively improve weak areas like DSA."

---

## How to Use This File

- Memorize the one-line explanations and a few code snippets.
- Practice delivering answers out loud, timing each to 1-2 minutes.
- For coding screens, practice 10-20 easy DSA problems (you already have a foundation).

---

If you'd like, I can:
- Expand this into separate `project-questions.md` and `dsa-cheatsheet.md`.
- Generate a short PDF you can print and practice with.
- Create a short demo script with exact terminal commands to run the app for a live demo.

Good luck — tell me if you want this file adjusted/expanded for a specific company or role.

---

## GLOSSARY — Terms & Definitions

Use these short definitions when an interviewer asks technical terms; keep answers concise and follow with an example or why it matters.

- **N+1 Query Problem:** Occurs when an application runs one query to fetch N parent rows and then runs an additional query per parent to fetch related child rows (total 1 + N queries). It leads to poor performance. Fix with eager loading (e.g., `joinedload`) or batch joins.

- **Eager Loading vs Lazy Loading:** Eager loading fetches related objects in the same query (reduces round trips) while lazy loading fetches related data on access (may cause N+1). Use `joinedload()`/`subqueryload()` in SQLAlchemy to eager load.

- **CSRF (Cross-Site Request Forgery):** An attack where a user is tricked into submitting a request to a web app where they're authenticated. Prevent with CSRF tokens (Flask-WTF) and same-site cookie attributes.

- **XSS (Cross-Site Scripting):** Injecting malicious scripts into web pages viewed by others. Prevent by escaping user input (Jinja2 autoescape), sanitizing HTML (e.g., `bleach`), and using Content Security Policy (CSP).

- **SQL Injection:** Injection of malicious SQL through unsanitized input. Prevent using ORM parameterization, prepared statements, and input validation.

- **Soft Delete:** Marking records as deleted (e.g., `is_deleted=True`) instead of physical deletion. Pros: recoverability and audit; Cons: need to filter queries and manage storage growth.

- **CASCADE vs SET NULL (ondelete behavior):** `CASCADE` removes child rows when a parent is deleted; `SET NULL` keeps child rows but sets the foreign key to NULL. Choose based on whether child data is meaningful without the parent.

- **Junction Table (Many-to-Many):** A table that implements many-to-many relationships (e.g., `TeamMember`, `TeamProject`) and can store metadata about the relationship (role, timestamps).

- **Index:** Database structure that speeds up queries on columns. Add indexes on frequently filtered/sorted columns (e.g., FK columns, `is_deleted`, `created_at`).

- **Migration (Alembic/Flask-Migrate):** A version-controlled set of schema changes applied to the database. Use migrations to evolve schemas safely across environments.

- **Materialized View:** A cached result of a query stored like a table; useful for expensive reporting queries that change infrequently.

- **JWT vs Session:** JWT (stateless tokens) stores authentication data in signed tokens (client side); sessions typically store state on server or server-backed storage (Redis). JWTs scale horizontally but need careful revocation strategies.

- **Nginx + Gunicorn:** Typical production stack: Gunicorn serves WSGI app processes, Nginx acts as a reverse proxy handling SSL, static files, and buffering.

- **Celery / Background Workers:** Offload long-running tasks (emails, reports) to background workers to avoid blocking requests. Use Redis/RabbitMQ as broker.

- **Cache (Redis / Memcached):** Store frequently read data to reduce DB load (session store, computed counts, API responses). Use TTLs and cache invalidation strategies.

- **NATURAL JOIN vs Explicit JOIN:** Prefer explicit JOINs with ON conditions—avoid accidental cartesian products. SQLAlchemy warns when joins are ambiguous.

- **N+1 Warning Example (SQLAlchemy):** When you see many repeated queries in logs for related attributes in a loop, use `joinedload()`:

```python
from sqlalchemy.orm import joinedload
projects = Project.query.options(joinedload(Project.tasks)).all()
for p in projects:
    for t in p.tasks:  # tasks already loaded in the same query
        pass
```

---

If you want, I can shorten these definitions into flashcards or add them as a printable one-pager. Would you like flashcards next?
