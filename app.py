from flask import Flask, request, session, render_template, redirect, url_for, flash, abort, send_file
import os, re, subprocess

from config import Config
from mysql.models import db, User, File, FileGroup, UserGroup, Comment
from forms import LoginForm, RegisterForm, UploadForm, ShareForm, DownloadForm, CommentForm, AdminCommandForm

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

base_upload_dir = '/var/uploads'

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('logout'))
    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):

            session['role'] = user.get_role()
            session['username'] = form.username.data
            if session['role'] == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('dashboard'))
        else:
            flash('Wrong creds...')
    return render_template('login.html', form=form)

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(username=form.username.data).first():
            flash('This username is invalid. Please choose a different one.', 'error')
            return redirect(url_for('register'))

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        os.makedirs(os.path.join(base_upload_dir, user.username), 660, False)

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/auth/logout', methods=['GET'])
def logout():
    session.pop('role', None)
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/a/dashboard', methods=['GET'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    uploaded_files = user.get_uploaded_files()
    shared_files = user.get_shared_files()

    for file in uploaded_files + shared_files:
        for comment in file.comments:
            comment.author_username = User.query.get(comment.get_author()).username
    
    return render_template('dashboard.html', uploaded_files=uploaded_files, shared_files=shared_files)

@app.route('/a/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        group_name = form.group_name.data or 'default'
        
        user_id = User.query.filter_by(username=session['username']).first().id

        upload_dir = os.path.join(base_upload_dir, session['username'], group_name)
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = file.filename
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        group = FileGroup.query.filter_by(group_name=group_name, creator_id=user_id).first()
        if not group:
            group = FileGroup(group_name=group_name, creator_id=user_id)
            db.session.add(group)
            db.session.commit()
               
        new_file = File(filename=filename, filepath=filepath, uploaded_by=user_id, group_id=group.id)
        db.session.add(new_file)
        db.session.commit()
        
        return redirect(url_for('dashboard'))
    
    return render_template('upload.html', form=form)

@app.route('/a/share', methods=['GET', 'POST'])
def share():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_id = User.query.filter_by(username=session['username']).first().id

    form = ShareForm()

    file_groups = FileGroup.query.filter_by(creator_id=user_id).all()
    form.file_group.choices = [(group.id, group.group_name) for group in file_groups]

    users = User.query.filter(User.id != user_id).all()
    form.user.choices = [(user.id, user.username) for user in users]

    if form.validate_on_submit():
        selected_group_id = form.file_group.data
        selected_user_id = form.user.data

        user_group = UserGroup.query.filter_by(user_id=selected_user_id, group_id=selected_group_id).first()
        if not user_group:
            new_user_group = UserGroup(user_id=selected_user_id, group_id=selected_group_id)
            db.session.add(new_user_group)
            db.session.commit()
        else:
            flash('This file group is already shared with the selected user.')
            return redirect(url_for('share'))

        return redirect(url_for('dashboard'))

    return render_template('share.html', form=form)

@app.route('/a/download', methods=['GET', 'POST'])
def download():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    form = DownloadForm()

    uploaded_files = user.get_uploaded_files()
    shared_files = user.get_shared_files()
    accessible_files = uploaded_files + shared_files

    form.file.choices = [(file.id, file.filename) for file in accessible_files]

    if form.validate_on_submit():
        file_id = form.file.data
        file = File.query.get(file_id)

        if file and (file.uploaded_by == user.id or UserGroup.query.filter_by(user_id=user.id, group_id=file.group_id).first()):
            return send_file(file.filepath, as_attachment=True)
        else:
            abort(403)

    return render_template('download.html', form=form)

@app.route('/a/comment', methods=['GET', 'POST'])
def comment():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_id = User.query.filter_by(username=session['username']).first().id

    form = CommentForm()

    uploaded_files = File.query.filter_by(uploaded_by=user_id).all()
    
    shared_groups = UserGroup.query.filter_by(user_id=user_id).all()
    shared_files = File.query.filter(File.group_id.in_([group.group_id for group in shared_groups])).all()

    all_files = uploaded_files + shared_files
    form.file.choices = [(file.id, file.filename) for file in all_files]

    if form.validate_on_submit():
        selected_file_id = form.file.data
        comment_text = form.comment.data

        new_comment = Comment(file_id=selected_file_id, user_id=user_id, comment=comment_text)
        db.session.add(new_comment)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('comment.html', form=form)

@app.route('/a/admin', methods=['GET', 'POST'])
def admin():
    if session['role'] != 'admin':
        return redirect(url_for('dashboard'))
    form = AdminCommandForm()
    result = None

    if form.validate_on_submit():
        command = form.command.data
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            result = e.output

    return render_template('admin.html', form=form, result=result)



@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
    os.makedirs(base_upload_dir, bool=True)


"""
from web import create_app

app = create_app()

if __name__=='__main__':
    app.run(host="0.0.0.0", port=80)
"""
