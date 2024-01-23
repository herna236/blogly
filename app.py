from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from models import db, connect_db, User, Post, Tag
from flask_migrate import Migrate
import secrets
from flask_wtf.csrf import validate_csrf
from werkzeug.exceptions import abort
from wtforms import ValidationError
from flask_wtf.csrf import generate_csrf





app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['WTF_CSRF_SECRET_KEY'] = 'Aaron Hernandez'


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///models'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True


db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def home():
    try:
        users = User.query.all()
        return render_template('home.html', users=users)
    except Exception as e:
        print(f"Error querying users: {str(e)}")
        return render_template('error.html', error_message=str(e))

@app.route('/users/new', methods=['GET', 'POST'])
def add_user_form():
    if request.method == 'POST':
        new_user = User(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            image_url=request.form['image_url']
        )
        print(f"Received data from the form: {new_user.__dict__}")
        db.session.add(new_user)
        db.session.commit()  # Ensure the commit is done here
        print(f"User added to the database: {new_user.__dict__}")
        return redirect(url_for('home'))
    return render_template('add_user_form.html')


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.image_url = request.form['image_url']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit_user_form.html', user=user)

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/users/<int:user_id>', endpoint='view_user')
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user.id).all()
    csrf_token = generate_csrf()  

    return render_template('view_user.html', user=user, posts=posts, csrf_token=csrf_token)

@app.route('/users/<int:user_id>/posts/new', methods=['GET', 'POST'])
def add_post(user_id):
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()

    if request.method == 'POST':
        try:
            validate_csrf(request.form.get('csrf_token'))
        except ValidationError:
            abort(400, 'Invalid CSRF token')

        new_post = Post(
            title=request.form['title'],
            content=request.form['content'],
            user_id=user.id
        )
        db.session.add(new_post)

        selected_tags = request.form.getlist('tags')
        for tag_id in selected_tags:
            tag = Tag.query.get(tag_id)
            if tag:
                new_post.tags.append(tag)

        db.session.commit()
        flash('Post added successfully!', 'success')
        return redirect(url_for('view_user', user_id=user.id))

    csrf_token = generate_csrf()
    return render_template('add_post_form.html', user=user, tags=tags, csrf_token=csrf_token)


    

   
    

@app.route('/posts/<int:post_id>', endpoint='view_post')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(post.user_id)
    csrf_token = generate_csrf() 
    tags = post.tags_associated
    print(f"Tags associated with the post: {tags}")
    
    

    return render_template('view_post.html', post=post, user=user, tags=tags, csrf_token=csrf_token)



@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    csrf_token = generate_csrf()  
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('view_post', post_id=post.id))

    return render_template('edit_post_form.html', post=post, csrf_token=csrf_token)

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get(post_id)

    if post:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully!', 'success')
        return redirect(url_for('view_user', user_id=post.user_id))
    else:
        flash('Post not found!', 'error')
        return redirect(url_for('home'))

@app.route('/tags', methods=['GET', 'POST'])
def tags_list():
    tags = Tag.query.all()
    return render_template('tags_list.html', tags=tags)

@app.route('/tags/new', methods=['GET', 'POST'])
def new_tag():
    csrf_token = generate_csrf()  
    if request.method == 'POST':
        try:
            validate_csrf(request.form.get('csrf_token'))
        except ValidationError:
            abort(400, 'Invalid CSRF token')

        tag_name = request.form['tag_name']
        new_tag = Tag(name=tag_name)
        db.session.add(new_tag)
        db.session.commit()
    
        return redirect(url_for('tags_list'))

    csrf_token = generate_csrf()
    return render_template('new_tag_form.html', csrf_token=csrf_token)

@app.route('/tags/<int:tag_id>/posts')
def posts_by_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    posts = tag.posts.all()
    return render_template('posts_by_tag.html', tag=tag, posts=posts)


if __name__ == '__main__':
    app.run(debug=True)