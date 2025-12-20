from flask import render_template, request, redirect, url_for, session, flash
from flask_login import login_user, current_user, logout_user
from QLCC import models
from QLCC import app, dao, db, login_manager
from QLCC.models import UserRole, UserRole
import cloudinary.uploader

def chunk_list(data, size):
    result = []
    for i in range(0, len(data), size):
        result.append(data[i:i + size])
    return result

@app.route('/')
def index():
    p = dao.load_apartment_details()
    slides = chunk_list(p, 3)
    return render_template('index.html',p=p, slides=slides)

@app.route('/login', methods=['GET', 'POST'])
def login_account():

    if current_user.is_authenticated:
        return redirect('/')

    err_msg=None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username, password)

        if user:
            login_user(user)
            # Chia theo role
            if user.role == UserRole.ADMIN:
                return redirect("/management")
            elif user.role == UserRole.USER:
                return redirect("/client")
            elif user.role == UserRole.SECURITY:
                return redirect("/security")

        else:
            err_msg = 'Tai khoan hoac mat khau khong dung!'
    return render_template('login.html', err_msg=err_msg)

@app.route('/register', methods=['GET', 'POST'])
def register_account():
    err_msg = None

    if (request.method == "POST"):
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if password != confirm:
            err_msg = "Mat khau khong khop"
        else:
            name = request.form.get("name")
            username = request.form.get("username")
            avatar = request.files.get("avatar")
            email = request.form.get("email")
            phonenumber = request.form.get("phonenumber")
            file_path = None
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                file_path = res["secure_url"]
            try:
                flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
                dao.add_user(name, username, password, file_path, email, phonenumber)
                return redirect("/login")
            except:
                db.session.rollback()
                err_msg = "loi he thong"
    return render_template('register.html', err_msg=err_msg)

@app.route("/logout")
def logout_account():
    logout_user()
    return redirect("/")

@app.route('/apartment/<int:id>')
def apartment_details(id):
    a=dao.load_apartment_by_id(id)
    return render_template('apartment-details.html', apt=a)

@app.route('/management', methods=['GET', 'POST'])
def management():
    p = dao.get_user_by_id(1)
    return render_template('management/management.html', UserRole = UserRole, p=p)

@app.route('/client', methods=['GET', 'POST'])
def client():
    return render_template('client.html')

@app.route('/security', methods=['GET', 'POST'])
def security():
    return render_template('security.html')

@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)



if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)