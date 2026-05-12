from flask import Flask, render_template, request, redirect, session
from flask_mail import Mail
import pymysql
import os

app = Flask(__name__)

# ==================================================
# SECRET KEY
# ==================================================

app.secret_key = os.environ.get('SECRET_KEY', 'ncc_secret_key')


# ==================================================
# MYSQL CONFIGURATION (RAILWAY READY)
# ==================================================

MYSQL_HOST = os.environ.get('MYSQLHOST')
MYSQL_USER = os.environ.get('MYSQLUSER')
MYSQL_PASSWORD = os.environ.get('MYSQLPASSWORD')
MYSQL_DB = os.environ.get('MYSQLDATABASE')

# Railway sometimes gives empty MYSQLPORT
MYSQL_PORT = int(os.environ.get('MYSQLPORT', 3306))


# ==================================================
# EMAIL CONFIGURATION
# ==================================================

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

# CHANGE THESE
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'

mail = Mail(app)


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():

    connection = pymysql.connect(

        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,

        cursorclass=pymysql.cursors.DictCursor

    )

    return connection


# ==================================================
# HOME PAGE
# ==================================================

@app.route('/')
def home():

    return render_template('register.html')


# ==================================================
# SUCCESS PAGE
# ==================================================

@app.route('/success')
def success():

    return render_template('success.html')


# ==================================================
# REGISTER STUDENT
# ==================================================

@app.route('/register', methods=['POST'])
def register():

    try:

        full_name = request.form['full_name']
        date_of_birth = request.form['date_of_birth']
        ncc_year = request.form['ncc_year']
        camp_name = request.form['camp_name']
        college_name = request.form['college_name']
        regiment_number = request.form['regiment_number']
        email = request.form['email']
        phone = request.form['phone']

        connection = get_connection()

        cur = connection.cursor()

        # =========================================
        # CHECK DUPLICATES
        # =========================================

        cur.execute("""

        SELECT * FROM cadets

        WHERE
        email=%s
        OR phone=%s
        OR regiment_number=%s

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
            connection.close()

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

                <h2>Cadet Already Registered</h2>

                <a href="/">

                    <button>Go Back</button>

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

        connection.commit()

        cur.close()
        connection.close()

        return render_template('success.html')

    except Exception as e:

        return f"""

        <h1 style='color:red;text-align:center;margin-top:50px;'>

        ERROR:<br><br>

        {str(e)}

        </h1>

        """


# ==================================================
# ADMIN LOGIN PAGE
# ==================================================

@app.route('/admin_login')
def admin_login():

    return render_template('admin_login.html')


# ==================================================
# ADMIN LOGIN
# ==================================================

@app.route('/admin_login', methods=['POST'])
def admin_login_post():

    username = request.form['username']
    password = request.form['password']

    connection = get_connection()

    cur = connection.cursor()

    cur.execute(

        "SELECT * FROM admin WHERE username=%s AND password=%s",

        (username, password)

    )

    admin = cur.fetchone()

    cur.close()
    connection.close()

    if admin:

        session['admin'] = username

        return redirect('/dashboard')

    return """

    <h2 style='color:red;text-align:center;margin-top:50px;'>

    Invalid Login

    </h2>

    """


# ==================================================
# ADMIN DASHBOARD
# ==================================================

@app.route('/dashboard')
def dashboard():

    if 'admin' not in session:

        return redirect('/admin_login')

    connection = get_connection()

    cur = connection.cursor()

    cur.execute(

        "SELECT * FROM cadets ORDER BY id DESC"

    )

    data = cur.fetchall()

    cur.close()
    connection.close()

    return render_template(

        'admin_dashboard.html',

        data=data

    )


# ==================================================
# DELETE STUDENT
# ==================================================

@app.route('/delete/<int:id>')
def delete(id):

    if 'admin' not in session:

        return redirect('/admin_login')

    connection = get_connection()

    cur = connection.cursor()

    cur.execute(

        "DELETE FROM cadets WHERE id=%s",

        (id,)

    )

    connection.commit()

    cur.close()
    connection.close()

    return redirect('/dashboard')


# ==================================================
# EDIT STUDENT PAGE
# ==================================================

@app.route('/edit/<int:id>')
def edit(id):

    if 'admin' not in session:

        return redirect('/admin_login')

    connection = get_connection()

    cur = connection.cursor()

    cur.execute(

        "SELECT * FROM cadets WHERE id=%s",

        (id,)

    )

    student = cur.fetchone()

    cur.close()
    connection.close()

    return render_template(

        'edit_student.html',

        student=student

    )


# ==================================================
# UPDATE STUDENT
# ==================================================

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

    connection = get_connection()

    cur = connection.cursor()

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

    connection.commit()

    cur.close()
    connection.close()

    return redirect('/dashboard')


# ==================================================
# LOGOUT
# ==================================================

@app.route('/logout')
def logout():

    session.pop('admin', None)

    return redirect('/admin_login')


# ==================================================
# HEALTH CHECK
# ==================================================

@app.route('/health')
def health():

    return "APP RUNNING"


# ==================================================
# RUN FLASK APP
# ==================================================

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 5000))

    app.run(
        host='0.0.0.0',
        port=port
    )