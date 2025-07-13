from app import create_app
from ext import db
from models import User, NewsPost
from werkzeug.security import generate_password_hash

def create_database():
    app = create_app()
    
    with app.app_context():
        # Create database tables
        db.create_all()
        print("Database tables created successfully.")
        
        # Check if admin user exists, if not create one
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")
        
        # Create a regular test user
        test_user = User.query.filter_by(username='user').first()
        if not test_user:
            test_user = User(
                username='user',
                email='user@example.com',
                password_hash=generate_password_hash('user123'),
                is_admin=False
            )
            db.session.add(test_user)
            db.session.commit()
            print("Test user created successfully.")
        else:
            print("Test user already exists.")
        
        # Create some sample news posts
        if NewsPost.query.count() == 0:
            sample_posts = [
                {
                    'title': 'Welcome to News Portal',
                    'summary': 'This is our first news post. Welcome to our news portal!',
                    'content': 'Welcome to our news portal! This is a sample post to get you started. You can create your own news posts after registering and logging in.',
                    'category': 'News',
                    'user_id': admin.id
                },
                {
                    'title': 'New Technology Trends in 2023',
                    'summary': 'Discover the latest technology trends that will shape the future.',
                    'content': 'Artificial Intelligence, Machine Learning, and Blockchain continue to be the leading technologies in 2023. Companies are investing heavily in these areas to stay competitive.',
                    'category': 'News',
                    'user_id': admin.id
                },
                {
                    'title': 'Sports Update: Championship Finals',
                    'summary': 'The championship finals are set to begin next week with top teams competing.',
                    'content': 'The championship finals will feature the top teams from around the country. The matches will be broadcast live on major networks and streaming platforms.',
                    'category': 'News',
                    'user_id': test_user.id
                }
            ]
            
            for post_data in sample_posts:
                post = NewsPost(
                    title=post_data['title'],
                    summary=post_data['summary'],
                    content=post_data['content'],
                    category=post_data['category'],
                    user_id=post_data['user_id']
                )
                db.session.add(post)
            
            db.session.commit()
            print("Sample news posts created successfully.")
        else:
            print("News posts already exist.")

if __name__ == '__main__':
    create_database()
    print("Database initialization completed.") 