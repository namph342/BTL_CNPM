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
        """
        Gom dữ liệu từ DB → trả về dict để render dashboard (tổng quan)
        """

        # ===== 1. THỐNG KÊ PHÒNG =====
        total_rooms = Canho.query.count()

        # Check lại status trong DB: ví dụ 'DA_THUE'
        rented_rooms = Canho.query.filter(
            Canho.status == 'DA_THUE'
        ).count()

        empty_rooms = total_rooms - rented_rooms

        # ===== 2. THỐNG KÊ NGƯỜI THUÊ =====
        total_tenants = User.query.filter(
            User.role == UserRole.USER
        ).count()

        # ===== 3. DOANH THU THÁNG HIỆN TẠI =====
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

        # ===== 4. HÓA ĐƠN CHƯA THANH TOÁN =====
        unpaid_bills = Hoadon.query.filter(
            Hoadon.payment_status == 'unpaid'
        ).count()

        # ===== 5. HỢP ĐỒNG SẮP HẾT HẠN (30 NGÀY) =====
        today = datetime.now()
        next_30_days = today + timedelta(days=30)

        expiring_contracts = Hopdong.query.filter(
            Hopdong.end_date >= today,
            Hopdong.end_date <= next_30_days
        ).order_by(
            Hopdong.end_date.asc()
        ).limit(5).all()

        # ===== DEBUG (có thể xóa khi ổn) =====
        print("TOTAL ROOMS =", total_rooms)
        print("RENTED ROOMS =", rented_rooms)
        print("EMPTY ROOMS =", empty_rooms)
        print("TOTAL TENANTS =", total_tenants)
        print("MONTHLY REVENUE =", monthly_revenue)
        print("UNPAID BILLS =", unpaid_bills)

        # ===== TRẢ VỀ DATA CHO TEMPLATE =====
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
    """"
    Hàm này giả lập việc lấy dữ liệu từ Database.

    """
    data = [
        {
            "ma_phong": "A101",
            "trang_thai": "Đã thuê",
            "so_nguoi": "3/4",
            "gia_thue": "3,500,000",
            "hop_dong": "31/12/2025"
        },
        {
            "ma_phong": "A102",
            "trang_thai": "Đã thuê",
            "so_nguoi": "4/4",
            "gia_thue": "4,000,000",
            "hop_dong": "15/01/2026"
        },
        {
            "ma_phong": "A103",
            "trang_thai": "Trống",
            "so_nguoi": "0/4",
            "gia_thue": "3,500,000",
            "hop_dong": "-"
        },
        {
            "ma_phong": "B201",
            "trang_thai": "Đã thuê",
            "so_nguoi": "2/4",
            "gia_thue": "3,800,000",
            "hop_dong": "28/02/2026"
        },
         {
            "ma_phong": "B202",
            "trang_thai": "Trống",
            "so_nguoi": "0/4",
            "gia_thue": "3,500,000",
            "hop_dong": "-"
        }
    ]
    return data
if __name__ == "__main__":
    with app.app_context():
        print(auth_user("user", "123"))