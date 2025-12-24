# TaskPilot - Jira-like Task Management System

A comprehensive enterprise-grade project management and task tracking system built with Flask, featuring role-based access control, real-time Kanban boards, and collaborative task management.

## 🚀 Key Features

### Core Functionality
- **Role-Based Access Control (RBAC)**: 4 distinct roles - Admin, Manager, Developer, and Visitor
- **Project Management**: Full CRUD operations with team assignments and deadline tracking
- **Task Management**: Complete task lifecycle with status tracking, priorities, and due dates
- **Sprint Management**: Organize tasks into sprints for agile workflow
- **Team Collaboration**: Team creation, member management, and project assignments
- **🎯 Kanban Boards**: Interactive drag-and-drop task boards with status columns
  - Real-time status updates without page refresh
  - Separate boards for Managers and Developers
  - Visual workflow management (To Do, In Progress, Done, Blocked)

### Advanced Features
- **Notes System**: Thread-based discussions with 3 types:
  - 💬 Comments - General task discussions
  - ❓ Queries - Questions requiring manager attention
  - ⚠️ Issues - Problems that need resolution
- **Real-time Notifications**: In-app notification system with badge counter
  - Task assignments
  - Status changes
  - Query/Issue alerts
  - Resolution updates
- **Subtask Management**: Hierarchical task breakdown with individual status tracking
  - Manager: Full Kanban board for subtasks with drag-and-drop
  - Developer: Form-based subtask editing with validation
- **Task Calendar**: Visual calendar view of task deadlines
- **Soft Delete**: Recover deleted projects, teams, and tasks
- **Report Generation**: Team and project performance analytics

### Security & Authentication
- Session-based authentication with bcrypt password hashing
- OTP-based password recovery via email
- Decorator-based route protection
- Role-specific access controls
- CSRF protection on all API endpoints

## 📊 Technical Specifications

- **Backend**: Flask 3.x with MVC Blueprint architecture
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Models**: 11 normalized models with proper relationships
- **API Endpoints**: 100+ RESTful endpoints with CSRF protection
- **Templates**: 70+ responsive Jinja2 templates
- **Styling**: TailwindCSS for modern, responsive UI
- **Email**: Flask-Mailman with SMTP integration
- **Migrations**: Alembic for database versioning
- **Testing**: Pytest with 36 comprehensive test cases
- **Architecture**: Clean separation of concerns (MVC pattern)
  - Models: Database schema and relationships
  - Controllers: Business logic and data processing
  - Routes: Blueprint-based URL routing
  - Templates: Jinja2 with template inheritance

## 🗂️ Database Schema

### Core Models
- **LoginInfo**: User authentication and role management
- **UserProfile**: Extended user information (name, email, phone, gender)
- **Team**: Team management with soft delete support
- **TeamMember**: Team membership with roles (Leader/Member)
- **Project**: Project details with summaries, priorities, and deadlines
- **TeamProject**: Many-to-many team-project relationships
- **Task**: Task management with CompletionStatus and PriorityLevel enums
- **SubTask**: Hierarchical task breakdown with parent_task relationship
- **Note**: Threaded discussions on tasks (Comment/Query/Issue types)
- **Notification**: User notification system with read status tracking
- **Sprint**: Sprint planning with start/end dates and status tracking

### Key Relationships
- One-to-Many: Team → Projects, Project → Tasks, Task → SubTasks
- Many-to-Many: Teams ↔ Projects (via TeamProject junction table)
- Enums: CompletionStatus (to_do, in_progress, done, blocked), PriorityLevel (low, medium, high, critical)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shivam1342/jira_dashboard.git
   cd jira_dashboard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/dbname
   SECRET_KEY=your-secret-key-here
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

5. **Initialize database**
   ```bash
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

   Access at: `http://localhost:5000`

7. **Run tests** (Optional)
   ```bash
   python run_tests.py
   ```
   - 36 comprehensive test cases
   - Tests authentication, CRUD operations, role-based access
   - 25+ tests passing, demonstrating core functionality

## 👥 User Roles & Permissions

### Admin
- Full system access
- User and team management
- Project assignment to teams
- System-wide reports
- Password resets

### Manager
- Create and manage projects
- Assign tasks to developers
- **Dual Kanban boards** for tasks and subtasks
- Organize sprints
- Resolve queries and issues
- Team lead assignment
- View team reports
- Grant project access to teams
- Drag-and-drop task management

### Developer
- View assigned projects and tasks
- **Interactive Kanban board** for task status management
- Update task status via drag-and-drop
- **Edit subtasks** through validated forms
- Create and manage subtasks
- Raise queries and issues
- Submit task reports
- Add notes and comments
- Calendar view of task deadlines

### Visitor
- Read-only access
- View public projects
- Browse team structures
- No edit permissions

## 📁 Project Structure

```
jiradashboard/
├── app.py                  # Application entry point with CSRF config
├── forms.py                # Flask-WTF forms for validation
├── requirements.txt        # Python dependencies
├── pytest.ini              # Test configuration
├── run_tests.py            # Test runner script
├── test_app.py             # Comprehensive test suite (36 tests)
├── models/                 # SQLAlchemy models
│   ├── __init__.py
│   ├── login_info.py       # User authentication
│   ├── user_profile.py     # User details
│   ├── team.py             # Team management
│   ├── team_member.py      # Team membership
│   ├── project.py          # Project model
│   ├── task.py             # Task & SubTask models with enums
│   ├── note.py             # Discussion threads
│   ├── notification.py     # Notification system
│   └── sprints.py          # Sprint planning
├── controllers/            # Business logic layer
│   ├── auth_controllers.py # Authentication & password reset
│   ├── admin_controller.py # Admin operations
│   ├── manager_controller.py # Manager operations & Kanban APIs
│   ├── developer_controller.py # Developer ops & Kanban APIs
│   ├── common_controller.py # Shared functionality
│   ├── mailer.py           # Email services
│   └── decorators.py       # Role-based access decorators
├── routes/                 # Flask blueprints
│   ├── auth_routes.py
│   ├── admin_routes.py
│   ├── manager_routes.py
│   ├── developer_routes.py
│   └── common_routes.py
├── templates/              # Jinja2 templates
│   ├── base.html           # Base template
│   ├── admin/              # Admin views
│   ├── manager/            # Manager views with Kanban
│   ├── developer/          # Developer views with Kanban
│   ├── auth/               # Login/register
│   ├── errors/             # Error pages (404, 500)
│   └── partials/           # Reusable components
├── static/                 # Frontend assets
│   ├── css/
│   │   ├── main.css        # Global styles
│   │   ├── auth.css
│   │   ├── developer.css
│   │   ├── manager.css
│   │   └── sidebar.css
│   └── js/
│       └── sidebar-toggle.js
└── migrations/             # Alembic migrations
    ├── alembic.ini
    ├── env.py
    └── versions/           # Migration scripts
```

## 🔒 Security Features

- **Password Security**: bcrypt hashing with salt
- **Session Management**: Secure session-based authentication
- **CSRF Protection**: Flask-WTF CSRF tokens on forms, API endpoints exempted
- **Role-Based Access**: Decorator-enforced route protection (@admin_required, @manager_required, @developer_required)
- **OTP Verification**: Time-limited OTP for password reset via email
- **Soft Delete**: Data preservation with is_deleted flags
- **Input Validation**: Flask-WTF forms with DataRequired, Email validators
- **Environment Config**: Sensitive data in .env file (not committed)
- **SQL Injection Protection**: SQLAlchemy ORM parameterized queries
- **Access Control**: Ownership validation on all sensitive operations

## 📈 Technical Highlights

### Recent Implementation: Kanban Board System
- **Drag-and-Drop Interface**: Built with vanilla JavaScript for performance
- **API Design**: RESTful endpoints with CSRF exemption pattern
- **Status Management**: Enum-based status handling with getattr pattern
- **Real-time Updates**: Asynchronous fetch API calls with error handling
- **Role-Specific UX**: 
  - Managers get full Kanban boards for tasks and subtasks
  - Developers get task Kanban + form-based subtask editing
- **Security**: Ownership validation on all status updates

### Code Quality
- **MVC Architecture**: Clean separation of concerns
- **DRY Principle**: Reusable decorators, partials, and utilities
- **Error Handling**: Comprehensive try-catch blocks with logging
- **Database Normalization**: Proper relationships and foreign keys
- **Validation**: Flask-WTF forms with custom validators
- **Testing**: Pytest suite with fixtures and comprehensive coverage

## 🎯 Use Cases

1. **Software Development Teams**: Track features, bugs, and sprint progress
2. **Project Management**: Manage multiple projects with team assignments
3. **Agile Workflows**: Sprint planning with Kanban visualization
4. **Team Collaboration**: Centralized communication via notes and notifications
5. **Resource Planning**: Track developer workload and task assignments

## 📈 Future Enhancements

- [ ] WebSocket integration for real-time collaborative updates
- [ ] Dashboard merge (unified manager/developer view)
- [ ] Soft delete management UI with restore functionality
- [ ] Advanced sprint analytics and burndown charts
- [ ] File attachments for tasks with cloud storage
- [ ] Activity timeline and audit logs
- [ ] Export reports to PDF/Excel
- [ ] Email notifications for task assignments
- [ ] Mobile-responsive improvements
- [ ] Dark mode theme

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Shivam**
- GitHub: [@shivam1342](https://github.com/shivam1342)

## 🙏 Acknowledgments

Built with Flask, SQLAlchemy, and modern web technologies to demonstrate full-stack development capabilities with enterprise-level features including authentication, authorization, API design, database modeling, and interactive UI components.

---

**⭐ If you find this project useful, please consider giving it a star!**
