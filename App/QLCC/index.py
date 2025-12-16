from flask import render_template

from QLCC import app, dao

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
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_account():
    return render_template('register.html')

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)