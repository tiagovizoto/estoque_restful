from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///microblog.db')
session = scoped_session(sessionmaker(bind=engine))
metadata = MetaData(engine)
Base = declarative_base(metadata=metadata)
Base.query = session.query_property()

# M:N association table
followers = Table('followers', Base.metadata,
                  Column('follower_id', Integer, ForeignKey('User.id')),
                  Column('followed_id', Integer, ForeignKey('User.id'))
                  )


# User table
class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    nickname = Column(String(64), index=True, unique=True)
    email = Column(String(120), index=True, unique=True)
    posts = relationship('Post', backref='author', lazy='dynamic')
    about_me = Column(String(140))
    last_seen = Column(DateTime)
    followed = relationship('User',
                            secondary=followers,
                            primaryjoin=(followers.c.follower_id == id),
                            secondaryjoin=(followers.c.followed_id == id),
                            backref=backref('followers', lazy='dynamic'),
                            lazy='dynamic')

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self


# Posts Model
class Post(Base):
    __tablename__ = 'Post'
    id = Column(Integer, primary_key=True)
    body = Column(String(140))
    timestamp = Column(DateTime)
    user_id = Column(Integer, ForeignKey('User.id'))
    language = Column(String(5))


# Create stuff
metadata.create_all(engine)

# MA-SQLA
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema


class UserSchema(ModelSchema):
    followers = fields.Nested('self', default=None, many=True, exclude=('followers', 'followed', 'posts'))
    followed = fields.Nested('self', default=None, many=True, exclude=('followers', 'followed', 'posts'))
    posts = fields.Nested('PostSchema', default=None, many=True, exclude=('author'))

    class Meta:
        model = User
        sqla_session = session


class PostSchema(ModelSchema):
    author = fields.Nested('UserSchema', default=None, exclude=('followers', 'followed', 'posts'))

    class Meta:
        model = Post
        sqla_session = session


UserSerializer = UserSchema()
PostSerializer = PostSchema()

# Flask
from flask import Flask, jsonify, request

app = Flask(__name__)


# User routes
@app.route('/users', methods=['GET'])
def get_users():
    users = session.query(User)
    data, errors = UserSerializer.dump(users, many=True)
    if errors:
        return jsonify({"errors": errors})
    return jsonify({"users": data})


@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    user = session.query(User).filter(id == id)
    data, errors = UserSerializer.dump(user)
    if errors:
        return jsonify({"errors": errors})
    return jsonify({"user": data})


@app.route('/users', methods=['POST'])
def post_users():
    json = request.get_json()
    data, errors = UserSerializer.load(json).data
    if errors:
        return jsonify({"errors": errors})
    session.add(data)
    session.commit()
    user = UserSerializer.dump(data).data
    return jsonify(user)


# Post routes
@app.route('/posts', methods=['GET'])
def get_posts():
    posts = session.query(Post)
    data, errors = PostSerializer.dump(posts, many=True)
    if errors:
        return jsonify({"errors": errors})
    return jsonify({"posts": data})


@app.route('/posts/<id>', methods=['GET'])
def get_post(id):
    post = session.query(Post).filter(id == id)
    data, errors = PostSerializer.dump(post)
    if errors:
        return jsonify({"errors": errors})
    return jsonify({"post": data})


@app.route('/posts', methods=['POST'])
def post_posts():
    json = request.get_json()
    data, errors = PostSerializer.load(json).data
    if errors:
        return jsonify({"errors": errors})
    session.add(data)
    session.commit()
    user = PostSerializer.dump(data).data
    return jsonify(user)


# Populate DB
@app.route('/populate', methods=['GET'])
def populate():
    u1 = User(nickname='john', email='john@example.com')
    u2 = User(nickname='susan', email='susan@example.com')
    u3 = User(nickname='mary', email='mary@example.com')
    u4 = User(nickname='david', email='david@example.com')
    session.add_all([u1, u2, u3, u4])
    session.commit()

    # make four posts
    from datetime import datetime, timedelta
    utcnow = datetime.utcnow()
    session.add_all([
        Post(body="post from john", author=u1, timestamp=utcnow + timedelta(seconds=1)),
        Post(body="post from susan", author=u2, timestamp=utcnow + timedelta(seconds=2)),
        Post(body="post from mary", author=u3, timestamp=utcnow + timedelta(seconds=3)),
        Post(body="post from david", author=u4, timestamp=utcnow + timedelta(seconds=4))
    ])
    session.commit()

    # setup the followers
    session.add_all([
        u1.follow(u1),  # john follows himself
        u1.follow(u2),  # john follows susan
        u1.follow(u4),  # john follows david
        u2.follow(u2),  # susan follows herself
        u2.follow(u3),  # susan follows mary
        u3.follow(u3),  # mary follows herself
        u3.follow(u4),  # mary follows david
        u4.follow(u4)  # david follows himself
    ])
    session.commit()
    return ('Data populated')


# Run test server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)