from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import os

app = Flask(__name__)

app.secret_key = 'ncc_secret_key'

# =========================================
# MYSQL CONFIGURATION
# =========================================

app.config['MYSQL_HOST'] = os.getenv('MYSQLHOST')
app.config['MYSQL_USER'] = os.getenv('MYSQLUSER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQLPASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQLDATABASE')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQLPORT'))

mysql = MySQL(app)

# =========================================
# EMAIL CONFIGURATION
# =========================================

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

# CHANGE YOUR EMAIL HERE
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'

# ADD APP PASSWORD HERE
app.config['MAIL_PASSWORD'] = 'your_app_password'

mail = Mail(app)

# =========================================
# HOME PAGE
# =========================================

@app.route('/')
def home():

    return render_template('register.html')


# =========================================
# SUCCESS PAGE
# =========================================

@app.route('/success')
def success():

    return render_template('success.html')


# =========================================
# REGISTER STUDENT
# =========================================

@app.route('/register', methods=['POST'])
def register():

    full_name = request.form['full_name']
    date_of_birth = request.form['date_of_birth']
    ncc_year = request.form['ncc_year']
    camp_name = request.form['camp_name']
    college_name = request.form['college_name']
    regiment_number = request.form['regiment_number']
    email = request.form['email']
    phone = request.form['phone']

    cur = mysql.connection.cursor()

    # =========================================
    # CHECK DUPLICATES
    # =========================================

    cur.execute("""

    SELECT * FROM cadets

    WHERE

    email=%s
    OR
    phone=%s
    OR
    regiment_number=%s

    """, (

        email,
        phone,
        regiment_number

    ))

    existing_user = cur.fetchone()

    # =========================================
    # DUPLICATE FOUND
    # =========================================

    if existing_user:

        cur.close()

        return """

        <html>

        <head>

            <title>Duplicate Entry</title>

            <style>

                body{

                    background:#000;
                    color:white;
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    height:100vh;
                    font-family:Arial;
                    flex-direction:column;
                }

                h2{

                    color:red;
                    margin-bottom:20px;
                }

                button{

                    padding:12px 25px;
                    border:none;
                    background:#00ff88;
                    color:black;
                    border-radius:10px;
                    font-size:16px;
                    cursor:pointer;
                    font-weight:bold;
                }

                a{
                    text-decoration:none;
                }

            </style>

        </head>

        <body>

            <h2>
                Cadet Already Registered
            </h2>

            <a href="/">

                <button>
                    Go Back
                </button>

            </a>

        </body>

        </html>

        """

    # =========================================
    # INSERT STUDENT
    # =========================================

    cur.execute("""

    INSERT INTO cadets
    (
        full_name,
        date_of_birth,
        ncc_year,
        camp_name,
        college_name,
        regiment_number,
        email,
        phone
    )

    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)

    """, (

        full_name,
        date_of_birth,
        ncc_year,
        camp_name,
        college_name,
        regiment_number,
        email,
        phone

    ))

    mysql.connection.commit()

    cur.close()

    return render_template('success.html')


# =========================================
# ADMIN LOGIN PAGE
# =========================================

@app.route('/admin_login')
def admin_login():

    return render_template('admin_login.html')


# =========================================
# ADMIN LOGIN
# =========================================

@app.route('/admin_login', methods=['POST'])
def admin_login_post():

    username = request.form['username']
    password = request.form['password']

    cur = mysql.connection.cursor()

    cur.execute(

        "SELECT * FROM admin WHERE username=%s AND password=%s",

        (username, password)

    )

    admin = cur.fetchone()

    cur.close()

    if admin:

        session['admin'] = username

        return redirect('/dashboard')

    return "Invalid Login"


# =========================================
# ADMIN DASHBOARD
# =========================================

@app.route('/dashboard')
def dashboard():

    if 'admin' not in session:

        return redirect('/admin_login')

    cur = mysql.connection.cursor()

    cur.execute(

        "SELECT * FROM cadets ORDER BY id DESC"

    )

    data = cur.fetchall()

    cur.close()

    return render_template(

        'admin_dashboard.html',

        data=data

    )


# =========================================
# DELETE STUDENT
# =========================================

@app.route('/delete/<int:id>')
def delete(id):

    if 'admin' not in session:

        return redirect('/admin_login')

    cur = mysql.connection.cursor()

    cur.execute(

        "DELETE FROM cadets WHERE id=%s",

        (id,)

    )

    mysql.connection.commit()

    cur.close()

    return redirect('/dashboard')


# =========================================
# EDIT STUDENT PAGE
# =========================================

@app.route('/edit/<int:id>')
def edit(id):

    if 'admin' not in session:

        return redirect('/admin_login')

    cur = mysql.connection.cursor()

    cur.execute(

        "SELECT * FROM cadets WHERE id=%s",

        (id,)

    )

    student = cur.fetchone()

    cur.close()

    return render_template(

        'edit_student.html',

        student=student

    )


# =========================================
# UPDATE STUDENT
# =========================================

@app.route('/update/<int:id>', methods=['POST'])
def update(id):

    if 'admin' not in session:

        return redirect('/admin_login')

    full_name = request.form['full_name']
    date_of_birth = request.form['date_of_birth']
    ncc_year = request.form['ncc_year']
    camp_name = request.form['camp_name']
    college_name = request.form['college_name']
    regiment_number = request.form['regiment_number']
    email = request.form['email']
    phone = request.form['phone']

    cur = mysql.connection.cursor()

    cur.execute("""

    UPDATE cadets SET

    full_name=%s,
    date_of_birth=%s,
    ncc_year=%s,
    camp_name=%s,
    college_name=%s,
    regiment_number=%s,
    email=%s,
    phone=%s

    WHERE id=%s

    """, (

        full_name,
        date_of_birth,
        ncc_year,
        camp_name,
        college_name,
        regiment_number,
        email,
        phone,
        id

    ))

    mysql.connection.commit()

    cur.close()

    return redirect('/dashboard')


# =========================================
# ADMIN LOGOUT
# =========================================

@app.route('/logout')
def logout():

    session.pop('admin', None)

    return redirect('/admin_login')


# =========================================
# RUN FLASK SERVER
# =========================================

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )