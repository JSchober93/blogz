from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:pass1234@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
   
@app.route('/', methods=['GET'])
def index():
    blogger_list = User.query.all()
    return render_template('index.html', blogger_list=blogger_list)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    
    if request.args.get('id'):
       
        blog = Blog.query.filter_by(id=request.args.get('id')).first()
        user = User.query.filter_by(id=blog.owner_id).first()
        title = blog.title
        body = blog.body
        return render_template('blog_post.html',post_title=title,post_body=body, user=user)
    
    elif request.args.get('user'):
       
        user = User.query.filter_by(id=request.args.get('user')).first()
        blogs = Blog.query.filter_by(owner_id=request.args.get('user'))
        return render_template('singleUser.html', blogs=blogs, user=user)
          
    blog_posts = Blog.query.all()
    users = User.query.all()
    return render_template('blog.html', blog_posts=blog_posts, users=users)
    
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':

        title_error = ''
        body_error = '' 
        blog_title = request.form['title']
        blog_body = request.form['body'] 

        if blog_title == '':
            title_error = 'This blog needs a title!'
        if blog_body == '':
            body_error = 'This blog needs some sustenance!'

        if title_error != '' or body_error != '':
            return render_template('newpost.html', title_error=title_error, body_error=body_error, title=blog_title, body=blog_body)
        else:   
            new_blog = Blog(blog_title,blog_body,owner)
            db.session.add(new_blog)
            db.session.commit()  
            return redirect('/blog?id=' + str(new_blog.id))

    return render_template('newpost.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        user_error = ''
        password_error = ''
        verify_error = ''
        
        if username == '':
            username_error = 'Username field is empty'
        elif len(username) < 3:
            username_error = 'Username is too short (min:3)'
        elif username == existing_user:
            username_error = 'That name has already been taken'

        if password == '':
            password_error = 'Password field is empty'
        elif len(password) < 3:
            password_error = 'Password is too short (min:3)'
        elif password != verify:
            password_error = 'These fields do not match'
            verify_error = 'These fields do not match'
        
        if verify == '':
            verify_error = 'Please verify you typed your password correctly'
        
        
        
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        username_error = ''
        password_error = ''

        if user and user.password == password:
            session['username'] = username          
            return redirect('/newpost')
        elif user and user.password != password:
            password_error = 'Password is incorrect, please try again'
        elif user and user.username != username:
            username_error = 'Username is incorrect or you do not have an account'
        return render_template('login.html', username=username, username_error=username_error, password_error=password_error)

    return render_template('login.html') 

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')





if __name__ == '__main__':
    app.run()