import os
import unittest
from urlparse import urlparse

from werkzeug.security import generate_password_hash

# Configure our app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog import models
from blog.database import Base, engine, session

class TestViews(unittest.TestCase):
	def setUp(self):
		"""Test setup"""
		self.client = app.test_client()

		# Set up the tables in the database
		Base.metadata.create_all(engine)

		# Create an example user
		self.user = models.User(name="Alice", email="alice@example.com",
			password=generate_password_hash("test"))
		session.add(self.user)
		session.commit()

	def tearDown(self):
		"""Test teardown"""
		# Remove the tables and their data from the database
		Base.metadata.drop_all(engine)

	def simulate_login(self):
		with self.client.session_transaction() as http_session:
			http_session["user_id"] = str(self.user.id)
			http_session["_fresh"] = True

	def simulate_logout(self):
		with self.client.session_transaction() as http_session:
			http_session["user_id"] = str(self.user.id)
			http_session["_fresh"] = False

	def testAddPost(self):
		self.simulate_login()

		response = self.client.post("/post/add", data={
			"title": "Test Post",
			"content": "Test Content"
			})

		self.assertEqual(response.status_code, 302)
		self.assertEqual(urlparse(response.location).path, "/")
		posts = session.query(models.Post).all()
		self.assertEqual(len(posts), 1)

		post = posts[0]
		self.assertEqual(post.title, "Test Post")
		self.assertEqual(post.content, "<p>Test Content</p>\n")
		self.assertEqual(post.author, self.user)

	def testEditPost(self):
		self.testAddPost()

		response = self.client.post("/post/1/edit", data={
			"title": "Fake Post",
			"content": "Fake Content"
			})

		self.assertEqual(response.status_code, 302)
		self.assertEqual(urlparse(response.location).path, "/")
		posts = session.query(models.Post).all()
		self.assertEqual(len(posts), 1)

		post = posts[0]
		self.assertEqual(post.title, "Fake Post")
		self.assertEqual(post.content, "<p>Fake Content</p>\n")
		self.assertEqual(post.author, self.user)

	def testDeletePost(self):
		self.testAddPost()

		response = self.client.post("/post/1/delete")

		self.assertEqual(response.status_code, 302)
		self.assertEqual(urlparse(response.location).path, "/")
		posts = session.query(models.Post).all()
		self.assertEqual(len(posts), 0)

	def testLogout(self):
		self.testAddPost()

		self.simulate_logout()

		response = self.client.get("/post/1/edit")

		self.assertEqual(response.status_code, 302)
		self.assertEqual(urlparse(response.location).path, "/")
		post = session.query(models.Post).first()
		self.assertEqual(post.title, "Test Post")

		response = self.client.get("/post/1/delete")
		self.assertEqual(response.status_code, 302)
		self.assertEqual(urlparse(response.location).path, "/")
		posts = session.query(models.Post).all()
		self.assertEqual(len(posts), 1)
		self.assertEqual(posts[0].title, "Test Post")


if __name__ == "__main__":
	unittest.main()