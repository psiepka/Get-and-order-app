import os, re
from app import app, db
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, login_user, current_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
from app.forms import LoginForm, PostForm, RegistrationForm, EditProfileForm, CompanyForm, BuildForm
from app.models import User, Post, Company, Build, followers


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()



@app.route('/index')
@login_required
def index():
    posts = current_user.followed_posts()
    return render_template('index.html', posts=posts, title='HomePage')


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.nickname.data).first()
        if user == None or not user.check_password(form.password.data):
            flash('Bad username or password mate! :(')
            return redirect(url_for('login'))
        flash('Congrats now you are logged as {}, remeber me={}'.format(form.nickname.data, form.remeber_me.data))
        login_user(user, remember=form.remeber_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('blog')
        return redirect(next_page)
    return render_template('login.html', form=form, title='Log in' )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/registration',  methods=['GET','POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(nickname=form.nickname.data, name=form.name.data, surname=form.surname.data,
                    phone=form.phone.data, gender=form.gender.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats you register in our app ! ')
        return redirect(url_for('login'))
    return render_template('registration.html', form=form, title='Register in ')


@app.route('/user/<nickname>')
@login_required
def profile_user(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    return render_template('profile_user.html', user=user, title=nickname+' profile')


@app.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.nickname)
    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        current_user.description = form.description.data
        current_user.phone = form.phone.data
        current_user.gender = form.gender.data
        current_user.linkedin = form.linkedin.data
        if form.avatar.data:
            ex = [i for i in re.split("\W+", app.config['IMAGES']) if len(i)>1]
            f_img = os.path.join('app', 'static', 'upload', 'avatar', 'avatar_' + str(current_user.id) + '.')
            for extension in ex:
                if os.path.exists(f_img + extension):
                    os.remove(f_img + extension)
            f = form.avatar.data
            f_ext = f.filename.rsplit('.',1)[1].lower()
            filename = secure_filename('avatar '+str(current_user.id)+'.'+f_ext)
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], 'avatar', filename
            ))
        if form.curriculum_vitae.data:
            f = form.curriculum_vitae.data
            f_ext = f.filename.rsplit('.',1)[1]
            filename = secure_filename('cv '+str(current_user.id)+'.'+f_ext)
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], 'cv', filename
            ))
        db.session.commit()
        flash('You changes are save on profile')
        return redirect(url_for('profile_user', nickname=current_user.nickname))
    elif request.method == 'GET':
        form.nickname.data = current_user.nickname
        form.gender.data = current_user.gender
        form.description.data = current_user.description
        form.phone.data = current_user.phone
        form.linkedin.data = current_user.linkedin
    return render_template('edit_profile.html', form=form, title='Edit profile')


@app.route('/companies')
def companies():
    comp = [
        {
            'name':'STRABAG',
            'description':'mosty, drogi, koleje'
        },
        {
            'name':'TORPOL',
            'description':' KOoleje'
        }
    ]
    companies = Company.query.all()
    return render_template('companies.html', companies=companies, title='Companies')



@app.route('/companies/add', methods=['GET','POST'])
@login_required
def add_company():
    form = CompanyForm()
    if form.validate_on_submit():
        if current_user.admin:
            company = Company(name=form.name.data, description=form.description.data,
                            web_page=form.web_page.data, verified=True)
        else:
            company = Company(name=form.name.data, description=form.description.data,
                                web_page=form.web_page.data)
        db.session.add(company)
        db.session.commit()
        flash('Congratulation you create company!')
        return redirect(url_for('companies'))
    return render_template('add_company.html', form=form, title='Create Company')


@app.route('/companies/<int:company_id>', methods=['GET','POST'])
def profile_company(company_id):
    company = Company.query.filter_by(id=company_id).first_or_404()
    posts = Post.query.filter_by(private_company=False, company_forum=company, build_forum=None).order_by(Post.timestamp.desc())
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user, company_forum=company)
        db.session.add(post)
        db.session.commit()
        flash('You post is now avaible ')
        return redirect(url_for('profile_company', company_id=company.id))
    return render_template('profile_company.html', form=form, posts=posts, company=company, title=company.name+' profile')


@app.route('/companies/<int:company_id>/employees')
@login_required
def employees(company_id):
    company = Company.query.filter_by(id=company_id).first_or_404()
    return render_template('employees.html', company=company, title=company.name+' employees')


@app.route('/builds')
def builds():
    builds = Build.query.all()
    b = [
        {
            'name':'DROGA KONIN',
            'specification':'Odcinek 15 km, wymiana rur metr od drogi, wyminan nawierzchni',
            'worth':10000,
            'place':'Konin',
            'contractor':{'name':'Kogucik'}
        },
        {
            'name':'Koleje Poz-War',
            'specification':'Odcinek w chuj dlugi, częściowo do wymiany tory, niektóre mosty odnowione',
            'worth':5000000000,
            'place':'Poznan, Konin, Kutno, Warszawa',
            'contractor':{'name':'TORPOL'}
        }
    ]
    return render_template('builds.html', builds=builds, title='All builds')


@app.route('/builds/add', methods=['GET','POST'])
@login_required
def add_build():
    form = BuildForm()
    if form.validate_on_submit():
        if current_user.admin or current_user.worker_id.admin:
            build = Build(name=form.name.data, specification=form.specification.data,
                        category=form.category.data, worth=form.worth.data, place=form.place.data,
                        creater=current_user, verified=True)
        else:
            build = Build(name=form.name.data, specification=form.specification.data,
                            category=form.category.data, worth=form.worth.data, place=form.place.data,
                            creater=current_user)
        db.session.add(build)
        db.session.commit()
        flash('Congratulation you create your own build!')
        return redirect(url_for('builds'))
    return render_template('add_build.html', form=form, title='Create Build')


@app.route('/builds/<int:build_id>', methods=['GET','POST'])
def profile_build(build_id):
    build = Build.query.filter_by(id=build_id).first_or_404()
    posts = Post.query.filter_by(build_forum=build, private_company=False).order_by(Post.timestamp.desc())
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user, build_forum=build)
        db.session.add(post)
        db.session.commit()
        flash('You post is now avaible ')
    return render_template('profile_build.html', build=build, form=form, posts=posts, title=build.name)


@app.route('/', methods=['GET','POST'])
@app.route('/blog', methods=['GET','POST'])
def blog():
    posts = Post.query.filter_by(private_company=False, build_forum=None, company_forum=None).order_by(Post.timestamp.desc())
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('You post is now avaible ')
        return redirect(url_for('blog'))
    return render_template('blog.html', posts=posts, form=form,  title='MicroBlog')


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cant follow yourself!')
        return redirect(url_for('profile_user', nickname=nickname))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(nickname))
    return redirect(url_for('profile_user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cant unfollow yourself!')
        return redirect(url_for('profile_user', nickname=nickname))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are  not following {}!'.format(nickname))
    return redirect(url_for('profile_user', nickname=nickname))