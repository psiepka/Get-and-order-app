import os, re, jwt
from time import time
from datetime import datetime
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.types import Integer, String, Text, DateTime, Boolean, Date
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView
from app import app, db, login_manager, admin


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    """database for users in website
    Arguments:
        id -- invidiual unique id of user
        nickname -- unique for each user
        name
        surname
        education (optional)
        linkedin (optional)
        email (optional)
        gender
        phone (optional)
        description (optional)
        worker_id

    """
    id = Column(Integer, primary_key=True)
    nickname = Column(String(40), nullable=False, unique=True)
    name = Column(String(40), nullable=False)
    surname = Column(String(40), nullable=False)
    education = Column(String(40))
    linkedin = Column(String(100))
    email = Column(String(120), nullable=False, unique=True)
    password_hash = Column(String(128))
    gender = Column(String(20), nullable=False)
    phone = Column(Integer)
    last_seen = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    admin = Column(Boolean, default=False)
    posts = relationship('Post', backref='author', lazy='dynamic')
    worker_id = relationship('Employee', uselist=False, back_populates="user")
    creatures = relationship('Build', backref='creater', lazy='dynamic')
    followed = relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    job_recipient = relationship('JobApp',
                                foreign_keys='JobApp.offer_recipient',
                                backref='recipient', lazy='dynamic'
                                )
    last_jobapp_read = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {} {}>'.format(self.name, self.surname)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self):
        """
        Returns:
            str -- path to image file
        """
        ex = [i for i in app.config['IMAGES'].split() if len(i)>1]
        f_img = os.path.join('app', 'static', 'upload', 'avatar', 'avatar_' + str(self.id) + '.')
        img = os.path.join('..', 'static', 'upload', 'avatar', 'avatar_' + str(self.id)+'.')
        for extension in ex:
            if os.path.isfile(f_img + extension):
                return img + extension
        if self.gender == 'male':
            return os.path.join('..','static', 'img','male.jpg')
        else:
            return os.path.join('..','static', 'img','female.jpg')

    def curriculum_vitae(self):
        ex = [i for i in re.split("\W+", app.config['ALLOWED_EXTENSIONS']) if len(i)>1]
        f_cv = os.path.join('app', 'static', 'upload', 'cv', 'cv_' + str(self.id))
        cv = os.path.join('..', 'static' , 'upload', 'cv', 'cv_' + str(self.id))
        for extension in ex:
            if os.path.isfile(f_cv + '.' + extension):
                return cv + '.' + extension

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            return self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            return self.followed.remove(user)

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).filter_by(private_company=False).order_by(Post.timestamp.desc())

    def new_jobapp(self):
        last_read_time = self.last_jobapp_read or datetime(2000, 1, 1)
        return JobApp.query.filter_by(recipient=self).filter(
            JobApp.timestamp > last_read_time).count()

    def self_receive_offer(self):
        offers = JobApp.query.filter(JobApp.recipient == self)
        return offers.order_by(JobApp.timestamp.desc())

    def check_offer_user(self, user):
        offers = JobApp.query.join(JobApp.sender).join(Employee.firm).filter(Company.name == self.worker_id.firm.name, JobApp.recipient == user).order_by(JobApp.timestamp.desc())
        return offers

    def get_reset_password_token(self, expires_in=300):
        return jwt.encode(
            {'reset_password' : self.id, 'exp' : time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_passwordd_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    """post model database
    Arguments:
        body(str), author(id from User database), build_forum(id build from Build database-if post subject is build)
        company_forum(id of company from Company model-if subject of post is company), timestamp(default=utcnow),
        private_company(Boolean-True if post is only for company members)
    """
    id = Column(Integer, primary_key=True)
    body = Column(String(200), nullable=False)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'))
    build_id = Column(Integer, ForeignKey('build.id'))
    company_id = Column(Integer, ForeignKey('company.id'))
    private_company = Column(Boolean, default=False)

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Company(db.Model):
    """model database of building company
    Arguments:
        name : str, description : str, web_page : string, verified : boolean,
        workers:(list of employeers from Employee model)
        build:(list of build from Build model)
        posts:(list of posts from Post model)
        jobapp:(list of job aplication from JobApp model)
    """
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(1000))
    web_page = Column(String(100), unique=True)
    verified = Column(Boolean, default=False)
    workers = relationship('Employee', backref='firm', lazy='dynamic')
    builds = relationship('Build', backref='contractor', lazy='dynamic')
    posts = relationship('Post', backref='company_forum', lazy='dynamic')
    jobapp = relationship('JobApp', backref='company_id', lazy='dynamic')

    def __repr__(self):
        return "<Company {}>".format(self.name)

    def is_working(self, user):
        return user.worker_id in self.workers

    def number_workers(self):
        return self.workers.count()

    def add_build(self, building):
        if not building in self.builds.all():
            self.builds.append(building)

    def del_build(self, building):
        if building in self.builds.all():
            self.builds.remove(building)


employees = db.Table('employees',
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id')),
    db.Column('build_id', db.Integer, db.ForeignKey('build.id'))
)


class Employee(db.Model):
    """Worker model
    Arguments:
    user: user from User model,
    Position(str), salary(int), date_join(datetime)
    """
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='worker_id')
    company = Column(Integer, ForeignKey('company.id'))
    admin = Column(Boolean, default=False)
    position = Column(String(100), nullable=False)
    salary = Column(Integer)
    date_join = Column(DateTime, default=datetime.utcnow)
    builds = relationship("Build", secondary=employees, backref=db.backref('employers', lazy='dynamic'), lazy='dynamic')
    emp_mail = Column(String(200))
    emp_tel = Column(Integer)
    job_sender = relationship('JobApp', backref='sender', lazy='dynamic')

    def __repr__(self):
        return "<employee {}>".format(self.user.nickname)

    def is_building(self, build):
        return self.builds.filter(employees.c.build_id == build.id).count() > 0

    def add_build(self, build):
        if not self.is_building(build):
            self.builds.append(build)

    def del_build(self, build):
        if self.is_building(build):
            self.builds.remove(build)


class Build(db.Model):
    """model database of builds
    name:string, specification : string, category : string, worth : integer, place : string,
    post_date : datetime, start_date : datetime, verified : boolean, creater : user_id(from User model),
    contractor : build_id(from Build model), posts : contain all of posts belongs to this build(from Post model)
    """
    __tablename__ = 'build'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    specification = Column(String(2000), nullable=False)
    category = Column(String(200), nullable=False)
    worth = Column(Integer, nullable=False)
    place = Column(String(200), nullable=False)
    post_date = Column(DateTime, default=datetime.utcnow)
    start_date = Column(Date)
    end_date = Column(Date)
    verified = Column(Boolean, default=False)
    creater_id = Column(Integer, ForeignKey('user.id'))
    contractor_id = Column(Integer, ForeignKey('company.id'))
    posts = relationship('Post', backref='build_forum', lazy='dynamic')

    def __repr__(self):
        return "<Build {}>".format(self.name)


class JobApp(db.Model):
    """
    sender : (int) id from Employee model
    recipient : (int) id from User model
    salary : (int) money in $
    data_send : (datetime=time when we sending)
    position : (str)
    company_id : (int) id of company 
    """
    id = Column(Integer, primary_key=True)
    offer_sender = Column(Integer, ForeignKey('employee.id'))
    offer_recipient = Column(Integer, ForeignKey('user.id'))
    salary = Column(Integer, nullable=False)
    date_send = Column(DateTime, default=datetime.utcnow)
    position = Column(String(100), nullable=False)
    company = Column(Integer, ForeignKey('company.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Build, db.session))
admin.add_view(ModelView(Company, db.session))
admin.add_view(ModelView(Employee, db.session))
admin.add_view(ModelView(JobApp, db.session))
