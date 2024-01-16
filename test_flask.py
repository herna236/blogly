import unittest
from flask import url_for
from flask_testing import TestCase  
from app import app, db, User

class TestApp(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        return app

    def setUp(self):
        db.create_all()
        # Add a user for testing delete functionality
        test_user = User(first_name='Test', last_name='User', image_url='https://example.com')
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_home_route(self):
        response = self.client.get(url_for('home'))
        self.assert200(response)
    
    def test_edit_user_route(self):
        user_id = User.query.first().id
        response = self.client.get(url_for('edit_user', user_id=user_id))
        self.assert200(response)

    def test_add_user_form(self):
        data = {
            'first_name': 'Ben',
            'last_name': 'Johnson',
            'image_url': 'https://www.google.com',
        }
        response = self.client.post(url_for('add_user_form'), data=data, follow_redirects=True)
        self.assert200(response)
        self.assertIn(b'Ben Johnson', response.data)
    
    def test_delete_user(self):
        user_id = User.query.first().id
        response = self.client.post(url_for('delete_user', user_id=user_id), follow_redirects=True)
        
        self.assert200(response)
        self.assertNotIn(b'Test User', response.data)  
        self.assertIsNone(User.query.get(user_id))  

if __name__ == '__main__':
    unittest.main()
