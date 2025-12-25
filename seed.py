"""
Database Seed Script - Anime/Manhwa Themed Data
Populates database with realistic demo data for interviews and testing

Usage:
    python seed.py              # Add data (keeps existing)
    python seed.py --fresh      # Clear all data first, then seed
"""

import sys
import bcrypt
from datetime import datetime, timedelta
from app import app, db
from models.login_info import LoginInfo
from models.user_profile import UserProfile
from models.team import Team
from models.team_member import TeamMember, TeamRole
from models.project import Project
from models.task import Task, PriorityLevel, CompletionStatus
from models.sprints import Sprint
from models.note import Note
from models.notification import Notification

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def clear_all_data():
    """WARNING: Deletes all data from database"""
    print("🗑️  Clearing all existing data...")
    try:
        # Delete in reverse order of dependencies
        Notification.query.delete()
        Note.query.delete()
        Task.query.delete()
        Sprint.query.delete()
        Project.query.delete()
        TeamMember.query.delete()
        Team.query.delete()
        UserProfile.query.delete()
        LoginInfo.query.delete()
        db.session.commit()
        print("✅ All data cleared successfully")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error clearing data: {e}")
        raise e


def create_users_and_profiles():
    """Create all 50 users with profiles"""
    print("\n👥 Creating users and profiles...")
    
    # Team 1: Fairy Tail
    users_data = [
        # Fairy Tail (Team 1)
        ("natsu", "natsu", "Natsu Dragneel", "natsu.dragneel@fairytail.com", "9876543210", "Male", "manager"),
        ("lucy", "lucy", "Lucy Heartfilia", "lucy.heartfilia@fairytail.com", "9876543211", "Female", "developer"),
        ("erza", "erza", "Erza Scarlet", "erza.scarlet@fairytail.com", "9876543212", "Female", "developer"),
        ("gray", "gray", "Gray Fullbuster", "gray.fullbuster@fairytail.com", "9876543213", "Male", "developer"),
        ("happy", "happy", "Happy", "happy@fairytail.com", "9876543214", "Male", "developer"),
        
        # Castle (Team 2)
        ("shin", "shin", "Kim Shin", "kim.shin@castle.com", "9876543220", "Male", "manager"),
        ("do-chan", "do-chan", "Baek Do-chan", "baek.dochan@castle.com", "9876543221", "Male", "developer"),
        ("min-wook", "min-wook", "Choi Min-wook", "choi.minwook@castle.com", "9876543222", "Male", "developer"),
        ("young", "young", "Pyo Young", "pyo.young@castle.com", "9876543223", "Female", "developer"),
        ("jin-tae", "jin-tae", "Seo Jin-tae", "seo.jintae@castle.com", "9876543224", "Male", "developer"),
        
        # Nano Machine (Team 3)
        ("yeo-woon", "yeo-woon", "Cheon Yeo-woon", "cheon.yeowoon@nanomachine.com", "9876543230", "Male", "manager"),
        ("nano", "nano", "Nano", "nano@nanomachine.com", "9876543231", "Other", "developer"),
        ("marakim", "marakim", "Great Guardian Marakim", "marakim@nanomachine.com", "9876543232", "Male", "developer"),
        ("ku", "ku", "Mun Ku", "mun.ku@nanomachine.com", "9876543233", "Female", "developer"),
        ("yu-jong", "yu-jong", "Cheon Yu-jong", "cheon.yujong@nanomachine.com", "9876543234", "Male", "developer"),
        
        # Lookism (Team 4)
        ("hyung-seok", "hyung-seok", "Park Hyung-seok", "park.hyungseok@lookism.com", "9876543240", "Male", "manager"),
        ("eun-tae", "eun-tae", "Lee Eun-tae (Vasco)", "lee.euntae@lookism.com", "9876543241", "Male", "developer"),
        ("jin-sung", "jin-sung", "Lee Jin-sung (Zack Lee)", "lee.jinsung@lookism.com", "9876543242", "Male", "developer"),
        ("gun", "gun", "Gun Park", "gun.park@lookism.com", "9876543243", "Male", "developer"),
        ("goo", "goo", "Goo Kim", "goo.kim@lookism.com", "9876543244", "Male", "developer"),
        
        # One Piece (Team 5)
        ("luffy", "luffy", "Monkey D. Luffy", "luffy@onepiece.com", "9876543250", "Male", "manager"),
        ("zoro", "zoro", "Roronoa Zoro", "zoro@onepiece.com", "9876543251", "Male", "developer"),
        ("nami", "nami", "Nami", "nami@onepiece.com", "9876543252", "Female", "developer"),
        ("sanji", "sanji", "Vinsmoke Sanji", "sanji@onepiece.com", "9876543253", "Male", "developer"),
        ("robin", "robin", "Nico Robin", "robin@onepiece.com", "9876543254", "Female", "developer"),
        
        # Hanma Baki (Team 6)
        ("baki", "baki", "Baki Hanma", "baki.hanma@baki.com", "9876543260", "Male", "manager"),
        ("yujiro", "yujiro", "Yujiro Hanma", "yujiro.hanma@baki.com", "9876543261", "Male", "developer"),
        ("doppo", "doppo", "Doppo Orochi", "doppo.orochi@baki.com", "9876543262", "Male", "developer"),
        ("kaoru", "kaoru", "Kaoru Hanayama", "kaoru.hanayama@baki.com", "9876543263", "Male", "developer"),
        ("retsu", "retsu", "Retsu Kaioh", "retsu.kaioh@baki.com", "9876543264", "Male", "developer"),
        
        # Kengan Ashura (Team 7)
        ("ohma", "ohma", "Ohma Tokita", "ohma.tokita@kengan.com", "9876543270", "Male", "developer"),
        ("kazuo", "kazuo", "Kazuo Yamashita", "kazuo.yamashita@kengan.com", "9876543271", "Male", "developer"),
        ("raian", "raian", "Raian Kure", "raian.kure@kengan.com", "9876543272", "Male", "developer"),
        ("agito", "agito", "Agito Kanoh", "agito.kanoh@kengan.com", "9876543273", "Male", "developer"),
        ("gensai", "gensai", "Gensai Kuroki", "gensai.kuroki@kengan.com", "9876543274", "Male", "developer"),
        
        # The Eminence in Shadow (Team 8)
        ("cid", "cid", "Cid Kagenou", "cid.kagenou@shadow.com", "9876543280", "Male", "developer"),
        ("alpha", "alpha", "Alpha", "alpha@shadow.com", "9876543281", "Female", "developer"),
        ("beta", "beta", "Beta", "beta@shadow.com", "9876543282", "Female", "developer"),
        ("alexia", "alexia", "Alexia Midgar", "alexia.midgar@shadow.com", "9876543283", "Female", "developer"),
        ("aurora", "aurora", "Aurora", "aurora@shadow.com", "9876543284", "Female", "developer"),
        
        # Jujutsu Kaisen (Team 9)
        ("yuji", "yuji", "Yuji Itadori", "yuji.itadori@jjk.com", "9876543290", "Male", "developer"),
        ("satoru", "satoru", "Satoru Gojo", "satoru.gojo@jjk.com", "9876543291", "Male", "developer"),
        ("megumi", "megumi", "Megumi Fushiguro", "megumi.fushiguro@jjk.com", "9876543292", "Male", "developer"),
        ("nobara", "nobara", "Nobara Kugisaki", "nobara.kugisaki@jjk.com", "9876543293", "Female", "developer"),
        ("sukuna", "sukuna", "Ryomen Sukuna", "sukuna@jjk.com", "9876543294", "Male", "developer"),
        
        # Neon Genesis Evangelion (Team 10)
        ("shinji", "shinji", "Shinji Ikari", "shinji.ikari@nerv.com", "9876543300", "Male", "developer"),
        ("rei", "rei", "Rei Ayanami", "rei.ayanami@nerv.com", "9876543301", "Female", "developer"),
        ("asuka", "asuka", "Asuka Langley Soryu", "asuka.langley@nerv.com", "9876543302", "Female", "developer"),
        ("misato", "misato", "Misato Katsuragi", "misato.katsuragi@nerv.com", "9876543303", "Female", "developer"),
        ("gendo", "gendo", "Gendo Ikari", "gendo.ikari@nerv.com", "9876543304", "Male", "developer"),
    ]
    
    created_users = {}
    for username, password, name, email, phone, gender, role in users_data:
        # Create login info
        login = LoginInfo(
            username=username,
            password=hash_password(password),
            role=role,
            is_approved=True
        )
        db.session.add(login)
        db.session.flush()  # Get ID
        
        # Create profile
        profile = UserProfile(
            login_info_id=login.id,
            name=name,
            gmail=email,
            phone=phone,
            gender=gender
        )
        db.session.add(profile)
        created_users[username] = login.id
        
    db.session.commit()
    print(f"✅ Created {len(users_data)} users successfully")
    return created_users


def create_teams(user_ids):
    """Create 10 teams with members"""
    print("\n🏢 Creating teams...")
    
    teams_data = [
        ("Fairy Tail", "A guild of powerful mages known for their strong bonds and destructive magic.", 
         ["natsu", "lucy", "erza", "gray", "happy"], "natsu"),
        
        ("Castle", "Elite team handling high-stakes missions with precision and strategy.",
         ["shin", "do-chan", "min-wook", "young", "jin-tae"], "shin"),
        
        ("Nano Machine", "Advanced tech team pushing the boundaries of human enhancement.",
         ["yeo-woon", "nano", "marakim", "ku", "yu-jong"], "yeo-woon"),
        
        ("Lookism", "Diverse team tackling social justice and systemic challenges.",
         ["hyung-seok", "eun-tae", "jin-sung", "gun", "goo"], "hyung-seok"),
        
        ("One Piece", "Adventurous crew pursuing ambitious goals across uncharted territories.",
         ["luffy", "zoro", "nami", "sanji", "robin"], "luffy"),
        
        ("Hanma Baki", "Hardcore martial arts team focused on combat excellence.",
         ["baki", "yujiro", "doppo", "kaoru", "retsu"], "baki"),
        
        ("Kengan Ashura", "Corporate fighters handling business through underground matches.",
         ["ohma", "kazuo", "raian", "agito", "gensai"], None),  # No lead yet
        
        ("The Eminence in Shadow", "Shadow operatives working from the darkness.",
         ["cid", "alpha", "beta", "alexia", "aurora"], None),
        
        ("Jujutsu Kaisen", "Sorcerers battling curses and supernatural threats.",
         ["yuji", "satoru", "megumi", "nobara", "sukuna"], None),
        
        ("Neon Genesis Evangelion", "Pilots defending humanity against existential threats.",
         ["shinji", "rei", "asuka", "misato", "gendo"], None),
    ]
    
    created_teams = {}
    for team_name, description, members, lead_username in teams_data:
        # Get manager ID (first member is manager)
        manager_id = user_ids[members[0]]
        
        # Create team
        team = Team(
            name=team_name,
            manager_id=manager_id,
            description=description,
            is_deleted=False
        )
        db.session.add(team)
        db.session.flush()  # Get team ID
        
        # Add team members - all as developers (user will assign roles later)
        for member_username in members:
            team_member = TeamMember(
                team_id=team.id,
                user_id=user_ids[member_username],
                role=TeamRole.developer  # Everyone starts as developer
            )
            db.session.add(team_member)
        
        created_teams[team_name] = (team.id, manager_id, [user_ids[m] for m in members])
        
    db.session.commit()
    print(f"✅ Created {len(teams_data)} teams with members")
    return created_teams


def create_projects_and_tasks(teams_data, user_ids):
    """Create projects and tasks for select teams"""
    print("\n📁 Creating projects and tasks...")
    
    # Select 6 teams to get projects
    projects_config = [
        # Fairy Tail gets 2 projects
        ("Fairy Tail", [
            {
                "name": "Guild Hall Renovation",
                "description": "Modernize the guild hall infrastructure with magical enhancements and better facilities.",
                "summary": "Infrastructure upgrade project",
                "tasks": [
                    ("Design new guild hall layout", "Create architectural plans incorporating magical elements", PriorityLevel.high, CompletionStatus.completed),
                    ("Magical barrier installation", "Install protective barriers around the perimeter", PriorityLevel.high, CompletionStatus.in_progress),
                    ("Training facility construction", "Build state-of-the-art training grounds", PriorityLevel.medium, CompletionStatus.to_do),
                    ("Kitchen and dining upgrade", "Expand kitchen to handle 100+ members", PriorityLevel.low, CompletionStatus.to_do),
                ]
            },
            {
                "name": "S-Class Mage Trials",
                "description": "Organize and execute the annual S-Class mage promotion trials.",
                "summary": "Annual promotion event",
                "tasks": [
                    ("Trial location selection", "Scout and secure remote island for trials", PriorityLevel.high, CompletionStatus.completed),
                    ("Challenge design", "Create balanced challenges testing all magical abilities", PriorityLevel.high, CompletionStatus.in_progress),
                    ("Safety protocols", "Establish emergency response and healing stations", PriorityLevel.high, CompletionStatus.in_progress),
                ]
            }
        ]),
        
        # Castle gets 1 project
        ("Castle", [
            {
                "name": "Metropolitan Defense System",
                "description": "Implement city-wide surveillance and rapid response network.",
                "summary": "Urban security enhancement",
                "tasks": [
                    ("Network infrastructure", "Deploy communication towers and secure channels", PriorityLevel.high, CompletionStatus.completed),
                    ("AI threat detection", "Develop machine learning models for threat identification", PriorityLevel.high, CompletionStatus.in_progress),
                    ("Mobile response units", "Equip and train rapid deployment teams", PriorityLevel.medium, CompletionStatus.to_do),
                    ("Integration testing", "Test full system integration and response times", PriorityLevel.medium, CompletionStatus.to_do),
                ]
            }
        ]),
        
        # Nano Machine gets 2 projects
        ("Nano Machine", [
            {
                "name": "Neural Enhancement Protocol",
                "description": "Research and develop next-generation nanomachine integration techniques.",
                "summary": "Biotech R&D initiative",
                "tasks": [
                    ("Clinical trials Phase I", "Test basic nanomachine compatibility", PriorityLevel.high, CompletionStatus.completed),
                    ("Neural interface optimization", "Improve brain-nanomachine communication bandwidth", PriorityLevel.high, CompletionStatus.in_progress),
                    ("Side effect mitigation", "Research long-term health implications", PriorityLevel.high, CompletionStatus.in_progress),
                ]
            },
            {
                "name": "Martial Arts Database",
                "description": "Digitize and categorize all known martial arts techniques for nanomachine storage.",
                "summary": "Knowledge preservation system",
                "tasks": [
                    ("Ancient texts digitization", "Scan and translate historical martial arts scrolls", PriorityLevel.medium, CompletionStatus.completed),
                    ("3D motion capture", "Record master practitioners demonstrating techniques", PriorityLevel.medium, CompletionStatus.in_progress),
                    ("AI categorization", "Develop system to classify techniques by style and difficulty", PriorityLevel.low, CompletionStatus.to_do),
                ]
            }
        ]),
        
        # Lookism gets 1 project
        ("Lookism", [
            {
                "name": "Social Equality Platform",
                "description": "Build platform connecting victims of discrimination with legal and social support.",
                "summary": "Social justice web application",
                "tasks": [
                    ("Anonymous reporting system", "Secure submission portal for discrimination reports", PriorityLevel.high, CompletionStatus.completed),
                    ("Legal resource database", "Compile lawyers and organizations by case type", PriorityLevel.high, CompletionStatus.in_progress),
                    ("Community support forums", "Moderated safe spaces for sharing experiences", PriorityLevel.medium, CompletionStatus.to_do),
                    ("Mobile app development", "iOS/Android apps for on-the-go access", PriorityLevel.medium, CompletionStatus.to_do),
                ]
            }
        ]),
        
        # One Piece gets 2 projects
        ("One Piece", [
            {
                "name": "Grand Line Navigation System",
                "description": "Chart unpredictable currents and weather patterns across the Grand Line.",
                "summary": "Advanced maritime navigation",
                "tasks": [
                    ("Weather station deployment", "Install monitoring stations on key islands", PriorityLevel.high, CompletionStatus.completed),
                    ("Current mapping", "Use submarines to map underwater currents", PriorityLevel.high, CompletionStatus.in_progress),
                    ("AI prediction models", "Develop weather forecasting for the Grand Line", PriorityLevel.medium, CompletionStatus.in_progress),
                ]
            },
            {
                "name": "Thousand Sunny Upgrades",
                "description": "Enhance ship capabilities for New World challenges.",
                "summary": "Ship enhancement project",
                "tasks": [
                    ("Weapon systems upgrade", "Install Franky's latest cannon designs", PriorityLevel.medium, CompletionStatus.completed),
                    ("Energy efficiency", "Optimize cola-based propulsion system", PriorityLevel.low, CompletionStatus.to_do),
                    ("Aquarium expansion", "Expand fish tank for deeper sea creatures", PriorityLevel.low, CompletionStatus.to_do),
                ]
            }
        ]),
        
        # Hanma Baki gets 1 project
        ("Hanma Baki", [
            {
                "name": "Underground Arena Championship",
                "description": "Organize international underground fighting tournament.",
                "summary": "Global martial arts competition",
                "tasks": [
                    ("Fighter recruitment", "Scout and invite elite fighters worldwide", PriorityLevel.high, CompletionStatus.completed),
                    ("Arena preparation", "Reinforce underground arena for brutal matches", PriorityLevel.high, CompletionStatus.in_progress),
                    ("Medical staff", "Hire trauma surgeons and emergency response team", PriorityLevel.high, CompletionStatus.in_progress),
                    ("Broadcast rights", "Negotiate streaming deals for exclusive coverage", PriorityLevel.medium, CompletionStatus.to_do),
                ]
            }
        ]),
    ]
    
    project_count = 0
    task_count = 0
    
    for team_name, projects in projects_config:
        team_id, manager_id, member_ids = teams_data[team_name]
        
        for project_data in projects:
            # Create project
            project = Project(
                name=project_data["name"],
                description=project_data["description"],
                summary=project_data["summary"],
                manager_id=manager_id,
                owner_team_id=team_id,
                deadline=datetime.now() + timedelta(days=90),  # 3 months deadline
                is_deleted=False
            )
            db.session.add(project)
            db.session.flush()
            project_count += 1
            
            # Create tasks for this project
            for idx, (title, desc, priority, status) in enumerate(project_data["tasks"]):
                # Assign to random team member (not manager)
                assigned_to = member_ids[1 + (idx % (len(member_ids) - 1))]
                
                task = Task(
                    task_name=title,
                    description=desc,
                    priority=priority,
                    completion_status=status,
                    project_id=project.id,
                    assigned_to_user_id=assigned_to,
                    due_date=datetime.now() + timedelta(days=30),
                    is_deleted=False
                )
                db.session.add(task)
                task_count += 1
    
    db.session.commit()
    print(f"✅ Created {project_count} projects with {task_count} tasks")


def seed_database(fresh=False):
    """Main seeding function"""
    print("=" * 60)
    print("🌱 DATABASE SEEDING STARTED")
    print("=" * 60)
    
    with app.app_context():
        if fresh:
            clear_all_data()
        
        # Step 1: Create users
        user_ids = create_users_and_profiles()
        
        # Step 2: Create teams
        teams_data = create_teams(user_ids)
        
        # Step 3: Create projects and tasks
        create_projects_and_tasks(teams_data, user_ids)
        
        print("\n" + "=" * 60)
        print("✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📋 Login Credentials (username = password):")
        print("   Managers: natsu, shin, yeo-woon, hyung-seok, luffy, baki")
        print("   Developers: lucy, erza, gray, happy, do-chan, etc.")
        print("\n🔑 Try: username='natsu', password='natsu'")


if __name__ == "__main__":
    fresh = "--fresh" in sys.argv
    if fresh:
        confirm = input("⚠️  This will DELETE ALL DATA. Type 'YES' to confirm: ")
        if confirm != "YES":
            print("❌ Seeding cancelled")
            sys.exit(0)
    
    seed_database(fresh=fresh)
