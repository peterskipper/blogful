import os
import unittest

# Configure our app to use the testing configuration
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

import blog
from blog.database import engine, Base, session
from blog.models import *
from werkzeug.security import generate_password_hash

class ModelsTest(unittest.TestCase):
	def setUp(self):
		Base.metadata.create_all(engine)
		alice = User(name="Alice", email="alice@example.com",
			password=generate_password_hash("atest"))
		bob = User(name="Bob", email="bob@example.com",
			password=generate_password_hash("btest"))
		session.add_all([alice, bob])
		session.commit()
		post1 = Post(title="Alice's Title", content="Alice's Content",
			author_id=alice.id)
		post2 = Post(title="Bob's Title", content="Bob's Content",
			author_id=bob.id)
		session.add_all([post1, post2])
		session.commit()

	def tearDown(self):
		Base.metadata.drop_all(engine)

	def testAdds(self):
		posts = session.query(Post).all()
		self.assertEqual(len(posts), 2)
		users = session.query(User).all()
		self.assertEqual(len(users),2)
		alice = session.query(User).filter(User.name == "Alice").one()
		self.assertEqual(alice.id, 1)
		post1 = session.query(Post).filter(Post.title == "Alice's Title").one()
		self.assertEqual(post1.id, 1)

	def testRead(self):
		alice = session.query(User).filter(User.name == "Alice").one()
		self.assertEqual(alice.email, "alice@example.com")
		post2 = session.query(Post).filter(Post.id == 2).one()
		self.assertEqual(post2.content, "Bob's Content")

	def testUpdate(self):
		carol = session.query(User).filter(User.name == "Alice").one()
		carol.name = "Carol"
		session.add(carol)
		session.commit()
		temp = session.query(User).filter(User.id == 1).one()
		self.assertEqual(temp.name, "Carol")

	def testDelete(self):
		bob = session.query(User).filter(User.name == "Bob").one()
		session.delete(bob)
		session.commit()
		temp = session.query(User).filter(User.name == "Bob").first()
		self.assertIsNone(temp)

	def testRelationships(self):
		alice = session.query(User).filter(User.name == "Alice").one()
		post1 = session.query(Post).filter(Post.title == "Alice's Title").one()
		self.assertEqual(alice.posts[0].title, "Alice's Title")
		self.assertEqual(post1.author.name, "Alice")
		session.delete(alice)
		session.commit()
		self.assertIsNone(post1.author)


if __name__ == "__main__":
	unittest.main()