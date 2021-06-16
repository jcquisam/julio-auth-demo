from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm

app =Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'zoro123'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods=['GET','POST'])
def register_user():
    form= UserForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        email=form.email.data
        first_name=form.first_name.data
        last_name=form.last_name.data
        
        new_user = User.register(username,password,email,first_name,last_name)
        db.session.add(new_user)
        db.session.commit()
        session['username']= new_user.username
        flash(f'Welcome {new_user.username}!','success')
        return redirect(f'/users/{new_user.username}')

    return render_template('register.html', form= form)

@app.route('/login', methods=['GET','POST'])
def login_user():
    form= LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        user= User.authenticate(username,password)
        if user:
            session['username']=user.username
            return redirect(f'/users/{user.username}')
        else:
            flash('Invalid user/password', 'danger')
            # form.username.errors = ['Invalid user/password']

    return render_template('login.html',form=form)


@app.route('/users/<username>')
def info_user(username):
    if 'username' in session:
        print('Inside info user IF')
        user=User.query.get_or_404(username)
        feedbacks= Feedback.query.all()
        return render_template('userInfo.html',user=user, feedbacks=feedbacks)
    
    flash('You have to login first', 'danger')
    return redirect('/login')
    
@app.route('/logout')
def logout_user():
    session.pop('username')
    flash('GoodBye!', 'info')
    return redirect('/login')

@app.route('/users/<username>/delete',  methods=['POST'])
def delete_user(username):
    if 'username' not in session:
        return redirect('/login')
    user = User.query.get_or_404(username)
    if session['username'] == user.username:
        db.session.delete(user)
        db.session.commit()
        return redirect('/login')
    flash("You don't have permission to do that", 'danger')
    return redirect(f'/users/{username}')

@app.route('/users/<username>/feedback/add', methods=['GET','POST'])
def feedback_form(username):
    if 'username' not in session:
        return redirect('/login')

    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title=title,content=content,username=username)
        db.session.add(feedback)
        db.session.commit()
        return redirect(f'/users/{username}')
        
    return render_template('feedback.html', form=form, username=username)

@app.route('/feedback/<int:id>/update', methods=['GET','POST'])
def update_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    form = FeedbackForm()
    if session['username'] == feedback.user.username:
        if form.validate_on_submit():
            feedback.title= form.title.data
            feedback.content= form.content.data
            db.session.add(feedback)
            db.session.commit()
            return redirect(f'/users/{feedback.user.username}')
        else:
            return render_template('update.html', form=form)
    return redirect('/login')

@app.route('/feedback/<int:id>/delete', methods=['POST'])
def delete_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    if session['username'] == feedback.user.username:
        db.session.delete(feedback)
        db.session.commit()
        flash('Feedback Deleted','info')
        return redirect(f'/users/{feedback.user.username}')

    flash('You dont have permission to do that', 'danger')
    return redirect('/login')