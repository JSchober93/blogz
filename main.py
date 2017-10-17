from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog1234@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['POST','GET'])
def index():
    blogposts = Blog.query.all()
    return render_template('blog.html', object_list=blogposts)

@app.route('/blog', methods=['POST', 'GET'])
def post():

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
            new_blog = Blog(blog_title,blog_body)
            db.session.add(new_blog)
            db.session.commit()  
            return redirect('/blog?id=' + str(new_blog.id))
    
    
    if request.method =='GET':
        blog_id = request.args.get('id')
        this_blog = Blog.query.get(int(blog_id))
        title = this_blog.title
        entry = this_blog.body
        return render_template('blog_post.html',post_title=title,post_body=entry)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    return render_template('newpost.html')

#@app.route('/blogpost', methods=['POST', 'GET'])



if __name__ == '__main__':
    app.run()