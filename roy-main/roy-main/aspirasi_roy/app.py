from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

# ==============================
# Inisialisasi Flask App
# ==============================
app = Flask(__name__)
app.secret_key = 'secret123'

# ==============================
# Konfigurasi Folder & File
# ==============================
UPLOAD_FOLDER = 'static/uploads'
DATA_FILE = 'data_aspirasi.json'
USERS_FILE = 'users.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==============================
# Buat file JSON jika belum ada
# ==============================
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({"admin": [], "user": []}, f)

# ==============================
# Fungsi Data Aspirasi
# ==============================
def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ==============================
# Fungsi Data User/Admin
# ==============================
def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ==============================
# Dashboard User
# ==============================
@app.route('/', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login_user'))

    if request.method == 'POST':
        nama = request.form['nama']
        akun = session['user']   # otomatis ambil dari session
        deskripsi = request.form['deskripsi']
        gambar = request.files.get('gambar')

        filename = ""
        if gambar and gambar.filename != "":
            filename = secure_filename(gambar.filename)
            gambar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        data = load_data()

        aspirasi_baru = {
            "id": len(data) + 1,
            "nama": nama,
            "akun": akun,
            "gambar": filename,
            "deskripsi": deskripsi,
            "status": "Menunggu",
            "bukti": "",
            "tanggal": datetime.now().strftime("%d-%m-%Y %H:%M"),
            "feedback": "",          # ✅ TAMBAHAN
            "history": True 
        }
        

        data.append(aspirasi_baru)
        save_data(data)

        return redirect(url_for('dashboard'))

    return render_template('dashboard.html')

    # ==============================
# History Aspirasi (User)
# ==============================
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login_user'))

    data = load_data()
    user_data = [d for d in data if d['akun'] == session['user']]
    return render_template('terkirim.html', data=user_data)

# ==============================
# Aspirasi Terkirim (User)
# ==============================
@app.route('/terkirim')
def aspirasi_terkirim():
    if 'user' not in session:
        return redirect(url_for('login_user'))

    data = load_data()
    user_data = [d for d in data if d['akun'] == session['user']]
    return render_template('terkirim.html', data=user_data)

# ==============================
# Admin Panel
# ==============================
@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect(url_for('login_admin'))

    data = load_data()
    return render_template('admin.html', data=data)

# ==============================
# Konfirmasi Admin
# ==============================
@app.route('/admin/konfirmasi/<int:id>', methods=['POST'])
def konfirmasi(id):
    if 'admin' not in session:
        return redirect(url_for('login_admin'))

    data = load_data()

    for d in data:
        if d['id'] == id:
            d['status'] = "Diterima"

            bukti_file = request.files.get('bukti')
            if bukti_file and bukti_file.filename != "":
                filename = secure_filename(bukti_file.filename)
                bukti_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                d['bukti'] = filename

    save_data(data)
    return redirect(url_for('admin'))

@app.route('/dashboard2')
def dashboard2():
    if 'user' not in session:
        return redirect(url_for('login_user'))

    return render_template('dashboard2.html') 

    # ==============================
# Feedback Admin ke User
# ==============================
@app.route('/admin/feedback/<int:id>', methods=['POST'])
def feedback(id):
    if 'admin' not in session:
        return redirect(url_for('login_admin'))

    data = load_data()
    isi_feedback = request.form.get('feedback')

    for d in data:
        if d['id'] == id:
            d['feedback'] = isi_feedback

    save_data(data)
    return redirect(url_for('admin'))  

    # ==============================
# History User
# ==============================
@app.route("/history_user")
def history_user():

    with open("data_aspirasi.json", "r") as f:
        data = json.load(f)

    # kalau session ada → filter berdasarkan akun
    if "akun" in session:
        data_user = [d for d in data if d["akun"] == session["user"]]
    else:
        data_user = []

    return render_template("history_user.html", data=data_user)
    # ==============================
# History Admin
# ==============================
@app.route("/history_admin")
def history_admin():
    with open("data_aspirasi.json", "r") as f:
        data = json.load(f)

    return render_template("history_admin.html", data=data)
# ==============================
# Register User
# ==============================
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()

        for u in users['user']:
            if u['username'] == username:
                return "Username sudah terdaftar!"

        users['user'].append({
            "username": username,
            "password": password
        })

        save_users(users)
        return redirect(url_for('login_user'))

    return render_template('register_user.html')

# ==============================
# Login User
# ==============================
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()

        for u in users['user']:
            if u['username'] == username and u['password'] == password:
                session['user'] = username
                return redirect(url_for('dashboard2'))

        return "Username atau password salah!"

    return render_template('login_user.html')

# ==============================
# Register Admin
# ==============================
@app.route('/admin/register', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()

        for a in users['admin']:
            if a['username'] == username:
                return "Username admin sudah terdaftar!"

        users['admin'].append({
            "username": username,
            "password": password
        })

        save_users(users)
        return redirect(url_for('login_admin'))

    return render_template('register_admin.html')

# ==============================
# Login Admin
# ==============================
@app.route('/admin/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()

        for a in users['admin']:
            if a['username'] == username and a['password'] == password:
                session['admin'] = username
                return redirect(url_for('admin'))

        return "Username atau password admin salah!"

    return render_template('login_admin.html')

# ==============================
# Logout
# ==============================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_user'))

    

# ==============================
# Run App
# ==============================
if __name__ == '__main__':
    app.run(debug=True)