from ext import db
from models import User, NewsPost
from app import create_app
import sqlalchemy as sa

def update_database():
    app = create_app()
    with app.app_context():
        # Check if the column already exists
        inspector = sa.inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('news_post')]
        if 'image_file' not in columns:
            print("Adding image_file column to news_post table...")
            with db.engine.connect() as conn:
                conn.execute(sa.text('ALTER TABLE news_post ADD COLUMN image_file VARCHAR(100)'))
                conn.commit()
            print("Database schema updated successfully!")
        else:
            print("The image_file column already exists in the news_post table.")

if __name__ == '__main__':
    update_database() 