import os
from flask.ext.script import Manager

from blog import app
from blog.models import Post
from blog.database import session

manager = Manager(app)

@manager.command
def run():
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0',port=port)

@manager.command
def seed():
	content = """Lorem ipsum dolor sit amet, consectetur adipisicing elit. Tempora possimus odio aliquam perferendis beatae soluta ipsa, praesentium, rerum esse earum aspernatur blanditiis eaque, nam veritatis! Ut beatae ullam esse neque. """

	for i in range(25):
		post = Post(
			title = "Test Post #{}".format(i),
			content = content
			)
		session.add(post)
	session.commit()
if __name__ == '__main__':
	manager.run()