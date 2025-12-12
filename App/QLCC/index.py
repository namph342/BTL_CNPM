from flask import render_template

from QLCC import app


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login_account():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_account():
    return render_template('register.html')



if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)