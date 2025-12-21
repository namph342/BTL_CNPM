import hashlib
import json
from datetime import timedelta, datetime

from sqlalchemy import func

from QLCC import app, db
from QLCC.models import Canho, User, Hopdong, Hoadon, Chitiethoadon, UserRole


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


class ReportService:
    @staticmethod
    def get_dashboard_data():
        total_rooms = Canho.query.count()
        rented_rooms = Canho.query.filter(Canho.status == 'DA_THUE').count()
        empty_rooms = total_rooms - rented_rooms
        total_tenants = User.query.filter(User.role == UserRole.USER).count()

        now = datetime.now()
        current_month = now.month
        current_year = now.year

        monthly_revenue = db.session.query(
            func.sum(Chitiethoadon.Total_fee)
        ).join(
            Hoadon, Chitiethoadon.hoadon_id == Hoadon.id
        ).filter(
            Hoadon.payment_status == 'paid',   # kiểm tra đúng string trong DB
            func.extract('month', Hoadon.created_date) == current_month,
            func.extract('year', Hoadon.created_date) == current_year
        ).scalar()

        monthly_revenue = monthly_revenue or 0


        unpaid_bills = Hoadon.query.filter(
            Hoadon.payment_status == 'unpaid'
        ).count()


        today = datetime.now()
        next_30_days = today + timedelta(days=30)

        expiring_contracts = Hopdong.query.filter(
            Hopdong.end_date >= today,
            Hopdong.end_date <= next_30_days
        ).order_by(
            Hopdong.end_date.asc()
        ).limit(5).all()

        return {
            "total_rooms": total_rooms,
            "rented_rooms": rented_rooms,
            "empty_rooms": empty_rooms,
            "total_tenants": total_tenants,
            "monthly_revenue": monthly_revenue,
            "unpaid_bills": unpaid_bills,
            "expiring_contracts": expiring_contracts
        }

# File: dao/phong_dao.py
def get_danh_sach_phong():
    """
    Lấy toàn bộ danh sách căn hộ từ Database MySQL
    """
    # Tương đương: SELECT * FROM canho;
    return Canho.query.all()

def get_danh_sach_hop_dong():

    data = [
        {
            "ma_hd": "HD001",
            "phong": "A101",
            "nguoi_thue": "Nguyễn Văn A",
            "gia_thue": "3,500,000",
            "tien_coc": "3,500,000",
            "ngay_bat_dau": "01/01/2025",
            "ngay_ket_thuc": "31/12/2025",
            "trang_thai_code": "warning", # Dùng mã để xử lý màu sắc
            "trang_thai_text": "Sắp hết hạn (20 ngày)"
        },
        {
            "ma_hd": "HD002",
            "phong": "A102",
            "nguoi_thue": "Trần Thị B",
            "gia_thue": "4,000,000",
            "tien_coc": "4,000,000",
            "ngay_bat_dau": "15/07/2025",
            "ngay_ket_thuc": "15/01/2026",
            "trang_thai_code": "success",
            "trang_thai_text": "Còn hạn (35 ngày)"
        },
        {
            "ma_hd": "HD003",
            "phong": "B201",
            "nguoi_thue": "Lê Văn C",
            "gia_thue": "3,800,000",
            "tien_coc": "2,000,000",
            "ngay_bat_dau": "01/09/2025",
            "ngay_ket_thuc": "28/02/2026",
            "trang_thai_code": "success",
            "trang_thai_text": "Còn hạn (79 ngày)"
        },
        {
            "ma_hd": "HD004",
            "phong": "B203",
            "nguoi_thue": "Phạm Thị D",
            "gia_thue": "3,700,000",
            "tien_coc": "3,700,000",
            "ngay_bat_dau": "10/09/2025",
            "ngay_ket_thuc": "10/03/2026",
            "trang_thai_code": "success",
            "trang_thai_text": "Còn hạn (89 ngày)"
        },
        {
            "ma_hd": "HD005",
            "phong": "C301",
            "nguoi_thue": "Hoàng Văn E",
            "gia_thue": "4,200,000",
            "tien_coc": "4,200,000",
            "ngay_bat_dau": "20/07/2025",
            "ngay_ket_thuc": "20/01/2026",
            "trang_thai_code": "success",
            "trang_thai_text": "Còn hạn (40 ngày)"
        }
    ]
    return data

def get_danh_sach_hoa_don():
    data = [
        {
            "ma_hd": "INV001",
            "phong": "A101",
            "thang": "12/2024",
            "tien_dien": "280,000",
            "tien_nuoc": "45,000",
            "tien_mang": "100,000",
            "tien_thue": "3,500,000",
            "tong_tien": "3,925,000",
            "trang_thai": "da_thanh_toan",
            "trang_thai_text": "Đã thanh toán"
        },
        {
            "ma_hd": "INV002",
            "phong": "A102",
            "thang": "12/2024",
            "tien_dien": "320,000",
            "tien_nuoc": "60,000",
            "tien_mang": "100,000",
            "tien_thue": "4,000,000",
            "tong_tien": "4,480,000",
            "trang_thai": "chua_thanh_toan",
            "trang_thai_text": "Chưa thanh toán"
        },
        {
            "ma_hd": "INV003",
            "phong": "B201",
            "thang": "12/2024",
            "tien_dien": "250,000",
            "tien_nuoc": "40,000",
            "tien_mang": "100,000",
            "tien_thue": "3,800,000",
            "tong_tien": "4,190,000",
            "trang_thai": "da_thanh_toan",
            "trang_thai_text": "Đã thanh toán"
        },
        {
            "ma_hd": "INV004",
            "phong": "B203",
            "thang": "12/2024",
            "tien_dien": "290,000",
            "tien_nuoc": "50,000",
            "tien_mang": "100,000",
            "tien_thue": "3,700,000",
            "tong_tien": "4,140,000",
            "trang_thai": "chua_thanh_toan",
            "trang_thai_text": "Chưa thanh toán"
        }
    ]
    return data


_thong_tin_cau_hinh = {
    "gia_dien": "3500",
    "gia_nuoc": "15000",
    "gia_internet": "100000",
    "so_nguoi_toi_da": "4"
}

def get_cau_hinh():

    return _thong_tin_cau_hinh

def update_cau_hinh(dien, nuoc, net):

    global _thong_tin_cau_hinh
    _thong_tin_cau_hinh["gia_dien"] = dien
    _thong_tin_cau_hinh["gia_nuoc"] = nuoc
    _thong_tin_cau_hinh["gia_internet"] = net

def get_hop_dong_ca_nhan():

    return {
        "so_phong": "A101",
        "nguoi_thue": "Nguyễn Văn A",
        "ngay_bat_dau": "01/01/2025",
        "ngay_ket_thuc": "31/12/2025",
        "tien_thue": "3,500,000",
        "tien_coc": "7,000,000",
        "so_nguoi": "3/4 người"
    }

def get_danh_sach_quy_dinh():

    return [
        {
            "tieu_de": "Giờ giấc",
            "noi_dung": "Giữ yên lặng từ 22h - 6h sáng hàng ngày",
            "icon": "bi-clock"
        },
        {
            "tieu_de": "An ninh",
            "noi_dung": "Không cho người lạ vào phòng không có sự cho phép",
            "icon": "bi-shield-lock"
        },
        {
            "tieu_de": "Vệ sinh",
            "noi_dung": "Giữ gìn vệ sinh chung, đổ rác đúng nơi quy định",
            "icon": "bi-trash"
        },
        {
            "tieu_de": "Thanh toán",
            "noi_dung": "Thanh toán tiền phòng trước ngày 5 hàng tháng",
            "icon": "bi-credit-card"
        },
        {
            "tieu_de": "Điện nước",
            "noi_dung": "Sử dụng tiết kiệm, báo cáo kịp thời nếu có sự cố",
            "icon": "bi-lightning"
        }
    ]

def get_hoa_don_chi_tiet_client():

    return {
        "thang": "12/2024",
        "trang_thai": "chua_thanh_toan",  # hoặc 'da_thanh_toan'
        "han_thanh_toan": "05/01/2025",

        "chi_tiet": [
            {
                "ten": "Tiền điện",
                "mota": "80 kWh x 3,500 đ",
                "thanh_tien": "280,000"
            },
            {
                "ten": "Tiền nước",
                "mota": "3 m³ x 15,000 đ",
                "thanh_tien": "45,000"
            },
            {
                "ten": "Tiền Internet",
                "mota": "Gói cố định",
                "thanh_tien": "100,000"
            },
            {
                "ten": "Tiền thuê phòng",
                "mota": "Tháng 12/2024",
                "thanh_tien": "3,500,000"
            }
        ],
        "tong_cong": "3,925,000"
    }

if __name__ == "__main__":
    with app.app_context():
        print(auth_user("user", "123"))