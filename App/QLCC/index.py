from flask import render_template, request, redirect, url_for, session, flash
from flask_login import login_user, current_user, logout_user, login_required
from QLCC import models
from QLCC import app, dao, db, login_manager
from QLCC.dao import ReportService, get_danh_sach_phong, get_danh_sach_hop_dong, get_danh_sach_hoa_don, \
    get_chi_tiet_hoa_don_by_id, \
    delete_noiquy, add_noiquy, update_gia_tien, get_cauhinh, get_ds_noiquy, get_hopdong_cua_user, \
    get_hoadon_moi_nhat_cua_user, get_lich_su_thanh_toan, search_cu_dan, get_all_logs

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
    data = get_danh_sach_hoa_don()

    return render_template('management/hoadon.html',
                               list_hoadon=data,
                               active_page='invoice')

@app.route('/invoice/print/<int:hoadon_id>')
def in_hoa_don(hoadon_id):
    # Lấy dữ liệu chi tiết
    invoice_data = get_chi_tiet_hoa_don_by_id(hoadon_id)
    if not invoice_data:
        return "Không tìm thấy hóa đơn", 404
    return render_template('management/mau_in_hoa_don.html', info=invoice_data)


@app.route('/management/cai-dat', methods=['GET', 'POST'])
def quanly_caidat():
    # 1. Xử lý LƯU GIÁ TIỀN
    if request.method == 'POST' and 'btn_update_price' in request.form:
        e = request.form.get('electric_fee')
        w = request.form.get('water_fee')
        i = request.form.get('internet_fee')
        update_gia_tien(e, w, i)
        return redirect(url_for('quanly_caidat'))

    # 2. Xử lý THÊM QUY ĐỊNH
    if request.method == 'POST' and 'btn_add_rule' in request.form:
        content = request.form.get('new_rule_content')
        add_noiquy(content)
        return redirect(url_for('quanly_caidat'))

    # GET: Lấy dữ liệu hiển thị
    setting = get_cauhinh()
    rules = get_ds_noiquy()

    # Kiểm tra nếu setting chưa có (lần đầu chạy) thì tạo object giả để không lỗi HTML
    if not setting:
        class FakeSetting:
            electric_fee = 0
            water_fee = 0
            internet_fee = 0

        setting = FakeSetting()

    return render_template('management/caidat.html',
                           setting=setting,
                           rules=rules,
                           active_page='settings')

@app.route('/management/cai-dat/delete-rule/<int:id>')
def xoa_quy_dinh(id):
    delete_noiquy(id)
    return redirect(url_for('quanly_caidat'))


@app.route('/client/hop-dong')
@login_required
def client_thongtin():
    # 1. Lấy Hợp đồng của user đang đăng nhập
    my_contract = get_hopdong_cua_user(current_user.id)

    # 2. Lấy Giá tiền (Cấu hình)
    setting = get_cauhinh()
    # Nếu chưa có cấu hình thì tạo object giả để không lỗi giao diện
    if not setting:
        class Fake: electric_fee = 0; water_fee = 0; internet_fee = 0

        setting = Fake()

    # 3. Lấy Danh sách Nội quy (Từng dòng)
    rules = get_ds_noiquy()

    return render_template('client/hopdong.html',
                           contract=my_contract,
                           setting=setting,
                           rules=rules,
                           active_page='client_contract')


@app.route('/client/hoa-don')
@login_required
def client_hoadon():
    # Lấy hóa đơn mới nhất
    invoice = get_hoadon_moi_nhat_cua_user(current_user.id)

    return render_template('client/hoadon_thang.html',
                           invoice=invoice,
                           active_page='client_invoice')


@app.route('/client/lich-su')
@login_required
def client_lichsu():
    # Lấy dữ liệu
    history_list = get_lich_su_thanh_toan(current_user.id)

    return render_template('client/lich_su.html',
                           history=history_list,
                           active_page='client_history')
# @app.route('/client/su-co')
# def client_suco():
#     return render_template('client/suco.html', active_page='client_report')

@app.route('/security/')
@login_required
def security_index():
    # Mới vào là nhảy vô soát vé luôn
    return redirect(url_for('security_soatve'))


@app.route('/security/soat-ve')
@login_required
def security_soatve():
    # Lấy từ khóa tìm kiếm từ ô input (nếu có)
    kw = request.args.get('keyword', '')

    # Gọi DAO để lấy danh sách cư dân dựa trên từ khóa
    residents = search_cu_dan(kw)

    return render_template('security/soat_ve.html',
                           residents=residents,
                           kw=kw,
                           active_page='sec_check')

@app.route('/security/nhat-ky')
@login_required
def security_nhatky():
    logs = get_all_logs()
    return render_template('security/ra_vao.html',
                           logs=logs,
                           active_page='sec_logs')

@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)



if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)