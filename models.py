"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255), default='default_image_url.jpg')  

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='posts') 
    tags = db.relationship('Tag', secondary='post_tag', backref='posts_associated', cascade='all, delete-orphan', single_parent=True)
    tags_associated = db.relationship('Tag', secondary='post_tag', backref='posts', lazy='dynamic')
    
    def __repr__(self):
        return f"<Post {self.title} by User {self.user_id}>"

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  
    post = db.relationship('Post', secondary='post_tag', backref='tag')
    posts_associated_tags = db.relationship('Post', secondary='post_tag', backref='tags_associated_tags')

class PostTag(db.Model):
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)

   




    
