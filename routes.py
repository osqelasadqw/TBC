from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, current_app
from flask_login import login_user, current_user, logout_user, login_required
from ext import db
from models import User, NewsPost
from forms import RegistrationForm, LoginForm, NewsPostForm
import os
import secrets
from werkzeug.utils import secure_filename

# Blueprint definitions
main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
news = Blueprint('news', __name__)

# ფოტოებს კარგად ვერ ვინახავდი და GPT დავიხმარე>
def save_image(form_image):
    if not form_image:
        return None
    
    srandom_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_filename = srandom_hex + f_ext
    image_path = os.path.join(current_app.root_path, 'static/uploads', image_filename)
    
    # Create uploads directory if it doesn't exist
    os.makedirs(os.path.join(current_app.root_path, 'static/uploads'), exist_ok=True)
    
    # Save the image
    form_image.save(image_path)
    
    return image_filename

# Main routes
@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = NewsPost.query.order_by(NewsPost.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)


@main.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')

# Authentication routes
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@auth.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')

# News routes
@news.route('/news')
def news_list():
    page = request.args.get('page', 1, type=int)
    posts = NewsPost.query.order_by(NewsPost.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('news.html', title='News', posts=posts, category=None)

@news.route('/news/<int:post_id>')
def news_detail(post_id):
    post = NewsPost.query.get_or_404(post_id)
    return render_template('news_detail.html', title=post.title, post=post)

@news.route('/news/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = NewsPostForm()
    if form.validate_on_submit():
        image_file = None
        if form.image.data:
            image_file = save_image(form.image.data)
            
        post = NewsPost(
            title=form.title.data,
            summary=form.summary.data,
            content=form.content.data,
            category=form.category.data,
            author=current_user,
            image_file=image_file
        )
        db.session.add(post)
        db.session.commit()
        flash('Your news post has been created!', 'success')
        return redirect(url_for('news.news_list'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')

@news.route('/news/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = NewsPost.query.get_or_404(post_id)
    if post.author != current_user and not current_user.is_admin:
        abort(403)
    form = NewsPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.summary = form.summary.data
        post.content = form.content.data
        post.category = form.category.data
        
        if form.image.data:
            image_file = save_image(form.image.data)
            post.image_file = image_file
            
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('news.news_detail', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.summary.data = post.summary
        form.content.data = post.content
        form.category.data = post.category
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

@news.route('/news/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = NewsPost.query.get_or_404(post_id)
    if post.author != current_user and not current_user.is_admin:
        abort(403)
    
    # Delete associated image if exists
    if post.image_file:
        try:
            image_path = os.path.join(current_app.root_path, 'static/uploads', post.image_file)
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            # Log error but continue with post deletion
            print(f"Error deleting image: {e}")
    
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('news.news_list'))

# Admin routes
@news.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    posts = NewsPost.query.order_by(NewsPost.date_posted.desc()).all()
    return render_template('admin.html', title='Admin Panel', users=users, posts=posts) 