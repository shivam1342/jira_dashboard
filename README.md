# TaskPilot - Jira-like Task Management System

A comprehensive project management and task tracking system built with Flask, featuring role-based access control, real-time notifications, and collaborative task management.

## 🚀 Features

### Core Functionality
- **Role-Based Access Control (RBAC)**: 4 distinct roles - Admin, Manager, Developer, and Visitor
- **Project Management**: Create, edit, and manage multiple projects with team assignments
- **Task Management**: Complete task lifecycle with status tracking, priorities, and deadlines
- **Sprint Management**: Organize tasks into sprints for agile workflow
- **Team Collaboration**: Team creation, member management, and project assignments

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
- **Subtask Management**: Break down complex tasks into manageable subtasks
- **Task Calendar**: Visual calendar view of task deadlines
- **Soft Delete**: Recover deleted projects, teams, and tasks
- **Report Generation**: Team and project performance reports

### Security & Authentication
- Session-based authentication
- OTP-based password recovery via email
- Decorator-based route protection
- Role-specific access controls

## 📊 Technical Specifications

- **Backend**: Flask 3.x with Blueprint architecture
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Models**: 11 normalized models with 4 junction tables
- **API Endpoints**: 100+ RESTful endpoints
- **Templates**: 70+ responsive Jinja2 templates
- **Styling**: TailwindCSS for modern UI
- **Email**: Flask-Mailman with SMTP integration
- **Migrations**: Alembic for database versioning

## 🗂️ Database Schema

### Core Models
- **LoginInfo**: User authentication and roles
- **UserProfile**: Extended user information
- **Team**: Team management with soft delete
- **TeamMember**: Team membership with roles (Leader/Member)
- **Project**: Project details with summaries and priorities
- **TeamProject**: Many-to-many team-project relationships
- **Task**: Task details with status, priority, and deadlines
- **SubTask**: Hierarchical task breakdown
- **Note**: Threaded discussions on tasks
- **Notification**: User notification system
- **Sprint**: Sprint planning and tracking

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
- Organize sprints
- Resolve queries and issues
- Team lead assignment
- View team reports

### Developer
- View assigned projects and tasks
- Update task status
- Create subtasks
- Raise queries and issues
- Submit task reports
- Add notes and comments

### Visitor
- Read-only access
- View public projects
- Browse team structures
- No edit permissions

## 📁 Project Structure

```
jiradashboard/
├── app.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── models/                 # SQLAlchemy models
├── controllers/            # Business logic
│   ├── auth_controllers.py
│   ├── admin_controller.py
│   ├── manager_controller.py
│   ├── developer_controller.py
│   ├── common_controller.py
│   └── decorators.py       # Role-based decorators
├── routes/                 # Flask blueprints
├── templates/              # Jinja2 templates
│   ├── admin/
│   ├── manager/
│   ├── developer/
│   ├── auth/
│   └── partials/
├── static/                 # CSS and JavaScript
└── migrations/             # Alembic migrations
```

## 🔒 Security Features

- Password hashing (bcrypt recommended)
- Session-based authentication
- CSRF protection ready
- Role-based route protection
- OTP verification for password reset
- Soft delete for data recovery
- Environment-based configuration

## 📈 Future Enhancements

- [ ] WebSocket integration for real-time updates
- [ ] Dashboard merge (unified manager/developer view)
- [ ] Soft delete management UI
- [ ] Advanced sprint analytics
- [ ] File attachments for tasks
- [ ] Activity timeline
- [ ] Export reports to PDF/Excel

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Shivam**
- GitHub: [@shivam1342](https://github.com/shivam1342)

## 🙏 Acknowledgments

Built with Flask, SQLAlchemy, and modern web technologies to demonstrate full-stack development capabilities with enterprise-level features.
