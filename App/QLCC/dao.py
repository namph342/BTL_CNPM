import hashlib
import json
from datetime import timedelta, datetime

from sqlalchemy import func

from QLCC import app, db
from QLCC.models import Canho, User, Hopdong, Hoadon, Chitiethoadon, UserRole, NoiQuy, CauHinh, NhatKy, Suco


def load_apartment_details():
    # with open("data/canho.json", encoding="utf-8") as f:
    #     details = json.load(f)
    #     return details
    return Canho.query.all()

def auth_user(username, password):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    return User.query.filter(User.username==username, User.password==password).first()

def add_user(name, username, password, avatar, email, phonenumber):
    password=hashlib.md5(password.encode("utf-8")).hexdigest()
    u = User(name=name, username=username, password=password, avatar=avatar, email = email, phonenumber = phonenumber)
    db.session.add(u)
    db.session.commit()

def get_user_by_id(id):
    return User.query.get(id)

def load_apartment_by_id(id):
    return Canho.query.get(id)

def get_danh_sach_hop_dong():
    # 1. Lấy tất cả hợp đồng, sắp xếp cái mới nhất lên đầu (id giảm dần)
    ds_hopdong = Hopdong.query.order_by(Hopdong.id.desc()).all()

    # 2. Xử lý logic hiển thị (tính ngày còn lại)
    result = []
    today = datetime.now()

    for hd in ds_hopdong:
        # Tính khoảng cách ngày: Ngày kết thúc - Hôm nay
        delta = hd.end_date - today
        days_left = delta.days

        # Logic màu sắc và trạng thái
        status_label = ""
        badge_class = ""  # Class màu của Bootstrap

        if days_left < 0:
            status_label = f"Đã quá hạn {abs(days_left)} ngày"
            badge_class = "danger"  # Màu đỏ
        elif days_left <= 30:
            status_label = f"Sắp hết hạn ({days_left} ngày)"
            badge_class = "warning text-dark"  # Màu vàng
        else:
            status_label = "Đang thuê"
            badge_class = "success"  # Màu xanh

        # Đóng gói dữ liệu để gửi sang HTML
        result.append({
            "obj": hd,  # Giữ object gốc để lấy tên User, Canho
            "start_fmt": hd.start_date.strftime('%d/%m/%Y'),
            "end_fmt": hd.end_date.strftime('%d/%m/%Y'),
            "status_label": status_label,
            "badge_class": badge_class
        })

    return result


def get_danh_sach_hoa_don():
    # 1. Lấy tất cả hóa đơn, sắp xếp mới nhất lên đầu
    ds_hoadon = Hoadon.query.order_by(Hoadon.created_date.desc()).all()

    result = []

    for hd in ds_hoadon:
        # --- LẤY TỔNG TIỀN ---
        # Vì quan hệ là One-to-Many (hoadon.chitiethoadon trả về 1 list),
        # nhưng logic của ta là 1 Hóa đơn chỉ có 1 Chi tiết tổng, nên ta lấy phần tử đầu tiên [0]
        tong_tien = 0
        if hd.chitiethoadon:
            tong_tien = hd.chitiethoadon[0].Total_fee

        # --- XỬ LÝ TRẠNG THÁI ---
        # Khớp với dữ liệu seed: 'Đã thanh toán' hoặc 'Chưa thanh toán'
        status_class = ""
        if hd.payment_status == 'Đã thanh toán':
            status_class = "success"  # Xanh
        else:
            status_class = "danger"  # Đỏ (Nợ)

        # --- ĐÓNG GÓI DỮ LIỆU ---
        result.append({
            "id": hd.id,
            "code": hd.name,  # Mã hóa đơn (Vd: INV-A101-122025)
            "created_date": hd.created_date.strftime('%d/%m/%Y'),

            # Lấy tên Phòng và Khách qua chuỗi quan hệ: Hoadon -> Hopdong -> Canho/User
            "room_name": hd.Hopdong.Canho.name,
            "client_name": hd.Hopdong.User.name,

            "total_money": "{:,.0f}".format(tong_tien),  # Format: 3,500,000
            "status": hd.payment_status,
            "status_class": status_class
        })

    return result
def get_chi_tiet_hoa_don_by_id(hoadon_id):
    # Lấy hóa đơn theo ID
    hd = Hoadon.query.get(hoadon_id)

    if not hd:
        return None

    # Lấy chi tiết (giả định 1 hóa đơn có 1 dòng chi tiết tổng như logic trước)
    chitiet = hd.chitiethoadon[0] if hd.chitiethoadon else None

    # Tính toán các con số để hiển thị
    tien_dien = 0
    tien_nuoc = 0
    tien_phong = 0

    if chitiet:
        tien_dien = (chitiet.electric_new - chitiet.electric_old) * chitiet.electric_fee
        tien_nuoc = (chitiet.water_new - chitiet.water_old) * chitiet.water_fee
        # Tiền phòng = Tổng - (Điện + Nước)
        tien_phong = chitiet.Total_fee - (tien_dien + tien_nuoc)

    return {
        "code": hd.name,
        "created_date": hd.created_date.strftime('%d/%m/%Y'),
        "client_name": hd.Hopdong.User.name,
        "client_phone": hd.Hopdong.User.phonenumber or "Không có",
        "room_name": hd.Hopdong.Canho.name,

        # Thông tin chi tiết điện nước
        "e_old": chitiet.electric_old if chitiet else 0,
        "e_new": chitiet.electric_new if chitiet else 0,
        "e_used": (chitiet.electric_new - chitiet.electric_old) if chitiet else 0,
        "e_fee": "{:,.0f}".format(chitiet.electric_fee) if chitiet else 0,
        "e_total": "{:,.0f}".format(tien_dien),

        "w_old": chitiet.water_old if chitiet else 0,
        "w_new": chitiet.water_new if chitiet else 0,
        "w_used": (chitiet.water_new - chitiet.water_old) if chitiet else 0,
        "w_fee": "{:,.0f}".format(chitiet.water_fee) if chitiet else 0,
        "w_total": "{:,.0f}".format(tien_nuoc),

        "room_price": "{:,.0f}".format(tien_phong),
        "total_final": "{:,.0f}".format(chitiet.Total_fee) if chitiet else 0,

        "payment_status": hd.payment_status
    }

def get_cauhinh():
    # Lấy dòng đầu tiên
    return CauHinh.query.first()


def update_gia_tien(e, w, i):
    # Lấy cấu hình ra sửa
    ch = CauHinh.query.first()
    if not ch:
        # Nếu chưa có thì tạo mới (đề phòng)
        ch = CauHinh()
        db.session.add(ch)

    # Cập nhật giá (ép kiểu int để tránh lỗi)
    ch.electric_fee = int(e) if e else 0
    ch.water_fee = int(w) if w else 0
    ch.internet_fee = int(i) if i else 0

    db.session.commit()


# --- XỬ LÝ NỘI QUY (Bảng NoiQuy) ---
def get_ds_noiquy():
    return NoiQuy.query.all()


def add_noiquy(noi_dung):
    if noi_dung:
        nq = NoiQuy(content=noi_dung)
        db.session.add(nq)
        db.session.commit()


def delete_noiquy(id_xoa):
    nq = NoiQuy.query.get(id_xoa)
    if nq:
        db.session.delete(nq)
        db.session.commit()


def get_hopdong_cua_user(user_id):
    """Lấy hợp đồng đang hiệu lực của một user cụ thể"""
    # Lấy hợp đồng mới nhất của user này
    hd = Hopdong.query.filter_by(client_id=user_id).order_by(Hopdong.id.desc()).first()

    if not hd:
        return None

    # Tính ngày còn lại
    today = datetime.now()
    days_left = (hd.end_date - today).days

    # Xử lý hiển thị
    status_label = ""
    badge_class = ""

    if days_left < 0:
        status_label = f"Đã hết hạn ({abs(days_left)} ngày)"
        badge_class = "danger"
    elif days_left <= 30:
        status_label = f"Sắp hết hạn ({days_left} ngày)"
        badge_class = "warning"
    else:
        status_label = "Đang hiệu lực"
        badge_class = "success"

    return {
        "id": hd.id,
        "room_name": hd.Canho.name,
        "room_price": "{:,.0f}".format(hd.Canho.price),
        "room_img": hd.Canho.image,
        "start_date": hd.start_date.strftime('%d/%m/%Y'),
        "end_date": hd.end_date.strftime('%d/%m/%Y'),
        "days_left": days_left,
        "status": status_label,
        "badge_class": badge_class,
        "deposit": "{:,.0f}".format(hd.Canho.price * 1)  # Giả sử cọc 1 tháng tiền phòng
    }


def get_hoadon_moi_nhat_cua_user(user_id):
    # Lấy hóa đơn mới nhất (sắp xếp theo ngày giảm dần)
    # Join bảng Hopdong để lọc đúng user_id
    hd = Hoadon.query.join(Hopdong).filter(Hopdong.client_id == user_id) \
        .order_by(Hoadon.created_date.desc()).first()

    if not hd:
        return None

    # Lấy chi tiết
    chitiet = hd.chitiethoadon[0] if hd.chitiethoadon else None

    if not chitiet:
        return None

    # Tính toán số liệu
    e_used = chitiet.electric_new - chitiet.electric_old
    e_total = e_used * chitiet.electric_fee

    w_used = chitiet.water_new - chitiet.water_old
    w_total = w_used * chitiet.water_fee

    # Giả sử tiền phòng lấy từ tổng trừ đi điện nước (hoặc lấy từ contract)
    # Ở đây mình tính ngược lại từ Total_fee cho khớp số liệu
    room_price = chitiet.Total_fee - (e_total + w_total + 100000)  # 100k là mạng fix cứng trong code seed

    # Tính ngày hạn nộp (ví dụ: ngày 5 tháng sau)
    due_date = hd.created_date.replace(day=5)
    # Logic đơn giản: cứ lấy ngày 5 của tháng tạo hóa đơn (demo)

    return {
        "name": hd.name,  # Ví dụ: Hóa đơn tháng 12/2024
        "status": hd.payment_status,
        "created_date": hd.created_date.strftime("tháng %m/%Y"),

        # Điện
        "e_usage": f"{e_used} kWh x {'{:,.0f}'.format(chitiet.electric_fee)} đ",
        "e_total": "{:,.0f}".format(e_total),

        # Nước
        "w_usage": f"{w_used} m³ x {'{:,.0f}'.format(chitiet.water_fee)} đ",
        "w_total": "{:,.0f}".format(w_total),

        # Mạng (Fix cứng theo seed data là 100k)
        "net_total": "100,000",

        # Phòng
        "room_total": "{:,.0f}".format(room_price),

        # Tổng
        "final_total": "{:,.0f}".format(chitiet.Total_fee),

        # Hạn đóng tiền
        "due_date": due_date.strftime("05/%m/%Y")
    }


def get_lich_su_thanh_toan(user_id):
    # 1. Lấy tất cả hóa đơn của user mà ĐÃ THANH TOÁN
    ds_hoadon = Hoadon.query.join(Hopdong).filter(
        Hopdong.client_id == user_id,
        Hoadon.payment_status == 'Đã thanh toán'
    ).order_by(Hoadon.created_date.desc()).all()

    result = []

    for hd in ds_hoadon:
        # Lấy chi tiết để biết số tiền và phương thức
        chitiet = hd.chitiethoadon[0] if hd.chitiethoadon else None

        tong_tien = chitiet.Total_fee if chitiet else 0
        phuong_thuc = chitiet.apartment_patment if chitiet else "Tiền mặt"

        # Giả lập Mã giao dịch (PAY...) dựa trên ID cho giống ảnh mẫu
        # Vì trong DB ta lưu mã là INV-...
        ma_giao_dich = f"PAY{hd.id:03d}"

        result.append({
            "trans_code": ma_giao_dich,  # Mã thanh toán (PAY001)
            "month": hd.created_date.strftime("%m/%Y"),  # Tháng (11/2024)
            "date": hd.created_date.strftime("%d/%m/%Y"),  # Ngày thanh toán
            "amount": "{:,.0f}".format(tong_tien),  # Số tiền
            "method": phuong_thuc,  # Phương thức (Chuyển khoản/Tiền mặt)
            "status": "Đã thanh toán"  # Trạng thái
        })

    return result


def search_cu_dan(kw=None):
    # Lấy tất cả User là cư dân (Role = 1)
    query = User.query.filter(User.role == UserRole.USER)

    if kw:
        # Tìm kiếm theo tên hoặc số điện thoại
        query = query.filter(User.name.contains(kw) | User.phonenumber.contains(kw))

    users = query.all()

    results = []
    for u in users:
        # Lấy thông tin phòng từ hợp đồng mới nhất
        hd = Hopdong.query.filter_by(client_id=u.id).order_by(Hopdong.id.desc()).first()
        room_name = hd.Canho.name if hd else "Chưa nhận phòng"

        results.append({
            "name": u.name,
            "room": room_name,
            "phone": u.phonenumber or "Chưa cập nhật",
            "avatar": u.avatar
        })
    return results

def get_all_logs():
    return NhatKy.query.order_by(NhatKy.id.desc()).all()

def add_suco(user_id, loai, mo_ta):
    new_sc = Suco(
        name=loai,
        description=mo_ta,
        status="Chờ tiếp nhận",
        client_id=user_id
    )
    db.session.add(new_sc)
    db.session.commit()

# Khách xem danh sách của mình
def get_suco_by_user(user_id):
    return Suco.query.filter_by(client_id=user_id).order_by(Suco.id.desc()).all()

# Bảo vệ xem tất cả
def get_all_suco():
    return Suco.query.order_by(Suco.id.desc()).all()

# Bảo vệ cập nhật trạng thái
def update_suco_status(id, status):
    sc = Suco.query.get(id)
    if sc:
        sc.status = status
        db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        print(auth_user("user", "123"))