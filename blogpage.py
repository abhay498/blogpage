from flask import Flask
from flask import render_template
from flask.ext.mysqldb import MySQL
from wtforms import Form
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')
    
@app.route('/articles')
def articles():

    cur = mysql.connection.cursor()
    result = cur.execute('SELECT * FROM articles')
    
    articles = cur.fetchall()
    
    if result > 0:
        return render_template('articles.html', articles = articles)
    else:
        return render_template('articles.html')

    
class RegistrationForm(Form):
    user_name = TextField('username', [validators.Length(min=4, max=20)])
    email = TextField('email',[validators.Length(min=4, max=20)])
    password = PasswordField('Password', [validators.Required(),
                                          validators.EqualTo('confirm', message="Paswwords do not match")])
    confirm = PasswordField('Confirm password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated July 16, 2019)', [validators.Required()])

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    
    if request.method == 'POST' and form.validate():
        user_name = form.user_name.data
        email = form.email.data
        password = sha256_crypt.encrypt((str(form.password.data)))
        
        cur = mysql.connection.cursor()
        result = cur.execute('SELECT * FROM users WHERE username = (%s)',
                    thwart(user_name))
        
        if int(len(result)) > 0:
            flash('Username is already registered')
            return render_template('register.html')
        else:
            cur.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)',
                        (thwart(user_name),thwart(password), thwart(email)))
            mysql.connection.commit()
            cur.close()
            mysql.connection.close()
            gc.collect()
            
			
			
    return render_template('register.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/logout')    
def logout():
    return render_template('login.html')
    
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/add_article')
def add_article():
    return render_template('add_article.html')
    
@app.route('/edit_article')
def edit_article():
    return render_template('edit_article.html')
    
@app.route('/delete_article')
def delete_article():
    return redirect(url_for('dashboard'))
    
if __name__ == '__main__':
    app.run(debug=True)
    