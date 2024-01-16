from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, connect_db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///models'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True


db.init_app(app)
migrate = Migrate(app, db)

# question here. Do i need to db.create_all() before each request? 
# without it the tables are deleted after i run test_flask/py
@app.before_request
def create_tables():
    with app.app_context():
        db.create_all()

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

@app.route('/users/<int:user_id>')
def view_user(user_id):
    print(f"Received user ID: {user_id}")
    user = User.query.get_or_404(user_id)
    return render_template('view_user.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)


