from flask import render_template, request, redirect, url_for, session, flash
from flask_login import login_user, current_user, logout_user
from QLCC import models
from QLCC import app, dao, db, login_manager
from QLCC.dao import ReportService, get_danh_sach_phong, get_danh_sach_hop_dong, get_danh_sach_hoa_don, update_cau_hinh, \
    get_cau_hinh, get_hop_dong_ca_nhan, get_danh_sach_quy_dinh, get_hoa_don_chi_tiet_client
from QLCC.models import UserRole, UserRole, Canho, Hopdong, Hoadon, User, Chitiethoadon, Suco
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
                return redirect("/management/tong-quan")
            elif user.role == UserRole.USER:
                return redirect("/client/hop-dong")
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


@app.route('/management/tong-quan')
def tong_quan():
    # Logic lấy dữ liệu phải nằm ở đây
    dashboard_data = ReportService.get_dashboard_data()

    return render_template('/management/tongquan.html',
                        p=current_user,
                        UserRole=UserRole,
                        active_page='overview',
                        **dashboard_data)


@app.route('/management/phong')
def quanly_phong():

    ds_phong = get_danh_sach_phong()

    return render_template('management/quanlyphong.html',
                           list_phong=ds_phong,
                           active_page='rooms')

@app.route('/management/hop-dong')
def quanly_hopdong():
    # Lấy danh sách hợp đồng đã xử lý logic
    data = get_danh_sach_hop_dong()

    return render_template('management/hopdong.html',
                           list_hopdong=data,
                           active_page='contracts')
@app.route('/management/hoa-don')
def quanly_hoadon():
    ds_hoadon = get_danh_sach_hoa_don()

    return render_template('/management/hoadon.html',
                           list_hoadon=ds_hoadon,
                           active_page='billing')

@app.route('/management/cai-dat', methods=['GET', 'POST'])
def quanly_caidat():
    # NẾU LÀ POST (Admin bấm nút Lưu)
    if request.method == 'POST':
        # Lấy dữ liệu từ ô input có name="..."
        dien_moi = request.form.get('gia_dien')
        nuoc_moi = request.form.get('gia_nuoc')
        net_moi = request.form.get('gia_internet')

        # Gọi DAO để lưu lại
        update_cau_hinh(dien_moi, nuoc_moi, net_moi)

        # Load lại trang để thấy dữ liệu mới
        return redirect(url_for('quanly_caidat'))

    # NẾU LÀ GET (Chỉ hiển thị trang)
    data = get_cau_hinh()
    return render_template('/management/cai dat.html',
                           cauhinh=data,
                           active_page='settings')

@app.route('/client/hop-dong')
def client_hopdong():
    # 1. Thông tin hợp đồng
    contract = get_hop_dong_ca_nhan()

    # 2. Đơn giá dịch vụ (Lấy từ Admin cài đặt)
    prices = get_cau_hinh()

    # 3. Danh sách quy định
    rules = get_danh_sach_quy_dinh()

    return render_template('/client/hopdong.html',
                           hopdong=contract,
                           giaservice=prices,
                           quydinh=rules,
                           active_page='client_contract')

@app.route('/client/hoa-don')
def client_hoadon():
    # Lấy dữ liệu chi tiết
    invoice_data = get_hoa_don_chi_tiet_client()

    return render_template('/client/hoadon_thang.html',
                           hoadon=invoice_data,
                           active_page='client_invoice')

# @app.route('/client/lich-su')
# def client_lichsu():
#     return render_template('client/lichsu.html', active_page='client_history')
#
# @app.route('/client/su-co')
# def client_suco():
#     return render_template('client/suco.html', active_page='client_report')

@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)



if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)