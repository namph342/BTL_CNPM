import json
import random
from datetime import datetime, timedelta
from enum import Enum as EnumRole

from flask_login import UserMixin
from sqlalchemy import Column, Integer, Float, String, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship

from QLCC import db, app


class Base(db.Model):
    __abstract__ = True
    id = db.Column(Integer, primary_key=True, autoincrement=True)

    def __str__(self):
        return str(self.name)


class Canho(Base):
    name = db.Column(String(100), nullable=False)
    price = db.Column(Float, nullable=False, default=0)
    acreage = db.Column(Integer, nullable=False)
    capacity = db.Column(Integer, nullable=False)
    image = db.Column(String(1000),
                      default="https://res.cloudinary.com/dy1unykph/image/upload/v1743062897/isbvashxe10kdwc3n1ei.png")
    status = db.Column(String(50), nullable=False)
    hopdong = relationship('Hopdong', backref="Canho", lazy=True)


class Hopdong(Base):
    start_date = db.Column(DateTime, nullable=False, default=datetime.now)
    end_date = db.Column(DateTime, nullable=False)
    status = db.Column(String(50), nullable=False)
    client_id = db.Column(Integer, ForeignKey('user.id'), nullable=False)
    room_id = db.Column(Integer, ForeignKey('canho.id'), nullable=False)
    hoadon = relationship('Hoadon', backref="Hopdong", lazy=True)


class UserRole(EnumRole):
    ADMIN = 0
    USER = 1
    SECURITY = 2


class User(Base, UserMixin):
    name = db.Column(String(100), nullable=False)
    phonenumber = db.Column(String(100))
    email = db.Column(String(100))
    username = db.Column(String(100), nullable=False, unique=True)
    password = db.Column(String(100), nullable=False)
    role = db.Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    avatar = db.Column(String(1000),
                       default="https://res.cloudinary.com/dhmt3nfpz/image/upload/v1766058336/default-avatar-profile-icon-social-media-user-photo-in-flat-style-vector_ci4kl9.jpg")
    hopdong = relationship('Hopdong', backref="User", lazy=True)
    suco = relationship('Suco', backref="User", lazy=True)


class Hoadon(Base):
    name = db.Column(String(100), nullable=False)
    created_date = db.Column(DateTime, nullable=False, default=datetime.now)
    payment_status = db.Column(String(50), nullable=False)
    hopdong_id = Column(Integer, ForeignKey('hopdong.id'), nullable=False)
    chitiethoadon = relationship('Chitiethoadon', backref="Hoadon", lazy=True)


class Chitiethoadon(Base):
    name = db.Column(String(100), nullable=False)
    apartment_patment = db.Column(String(100), nullable=False)
    electric_old = db.Column(Integer, nullable=False)
    electric_new = db.Column(Integer, nullable=False)
    water_old = db.Column(Integer, nullable=False)
    water_new = db.Column(Integer, nullable=False)
    electric_fee = db.Column(Integer, nullable=False)
    water_fee = db.Column(Integer, nullable=False)
    Total_fee = db.Column(Integer, nullable=False)
    hoadon_id = Column(Integer, ForeignKey('hoadon.id'), nullable=False)


class Suco(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False) # Loại sự cố
    description = db.Column(db.Text, nullable=False) # Chi tiết
    status = db.Column(db.String(50), default="Chờ tiếp nhận")
    created_date = db.Column(db.DateTime, default=datetime.now)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class CauHinh(Base):
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    electric_fee = db.Column(Integer, default=3500)
    water_fee = db.Column(Integer, default=15000)
    internet_fee = db.Column(Integer, default=100000)

class NoiQuy(Base):
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    content = db.Column(String(500), nullable=False)

class NhatKy(Base):

    ma_log = db.Column(String(20), nullable=False) # LOG001
    nguoi_ten = db.Column(String(100), nullable=False)
    phong = db.Column(String(20))
    thoi_gian = db.Column(DateTime, default=datetime.now)
    loai = db.Column(String(20)) # Ra / Vào
    doi_tuong = db.Column(String(20)) # Cư dân / Khách

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        with open("data/canho.json", encoding="utf-8") as f:
            apartment = json.load(f)
            for a in apartment:
                db.session.add(Canho(**a))

        import hashlib

        password = hashlib.md5("123".encode('utf-8')).hexdigest()
        u1 = User(name="management", username='management', password=password, role=UserRole.ADMIN)
        u2 = User(name="security", username='security', password=password, role=UserRole.SECURITY)
        c1 = User(name="Nguyễn Văn A", username='user1', password=password)
        c2 = User(name="Trần Thị B", username='user2', password=password)
        c3 = User(name="Lê Văn C", username='user3', password=password)
        c4 = User(name="Bui Van D", username='user4', password=password)
        db.session.add_all([u1, u2, c1, c2, c3, c4])
        db.session.commit()

        clients = [c1, c2, c3, c4]
        phong_da_thue = Canho.query.filter(Canho.status == "Đã thuê").all()

        for client, phong in zip(clients, phong_da_thue):
            start = datetime.now() - timedelta(days=30)
            end = datetime.now() + timedelta(days=180)

            hd = Hopdong(
                start_date=start,
                end_date=end,
                status="Đang thuê",
                client_id=client.id,
                room_id=phong.id
            )

            db.session.add(hd)

        db.session.commit()

        for hd in Hopdong.query.filter(Hopdong.status == "Đang thuê").all():
            phong = hd.Canho

            current_time_str = datetime.now().strftime('%m%Y')
            ma_hoa_don = f"INV-{phong.name}-{current_time_str}"

            da_thanh_toan = random.choice([True, False])
            trang_thai_hd = "Đã thanh toán" if da_thanh_toan else "Chưa thanh toán"

            hoa_don = Hoadon(
                name=ma_hoa_don,
                created_date=datetime.now(),
                payment_status=trang_thai_hd,
                hopdong_id=hd.id
            )

            db.session.add(hoa_don)
            db.session.flush()

            e_old = random.randint(100, 500)
            e_new = e_old + random.randint(30, 100)
            w_old = random.randint(50, 200)
            w_new = w_old + random.randint(5, 20)

            tien_dien = (e_new - e_old) * 3500
            tien_nuoc = (w_new - w_old) * 15000
            tong_tien = tien_dien + tien_nuoc + int(phong.price)

            chi_tiet = Chitiethoadon(
                name=f"DT-{phong.name}-{current_time_str}",
                apartment_patment="Chuyển khoản" if da_thanh_toan else "Tiền mặt",
                electric_old=e_old, electric_new=e_new,
                water_old=w_old, water_new=w_new,
                electric_fee=3500, water_fee=15000,
                Total_fee=tong_tien,
                hoadon_id=hoa_don.id
            )

            db.session.add(chi_tiet)

        db.session.commit()

        list_phong = Canho.query.all()

        if list_phong and u1:


            # D. TẠO SỰ CỐ
            cac_loi = [
                ("Hỏng điều hòa", "Điều hòa kêu to, không mát"),
                ("Rò rỉ nước", "Vòi nước nhà vệ sinh bị rỉ"),
                ("Mất wifi", "Mạng chập chờn không vào được"),
                ("Kẹt khóa cửa", "Khóa cửa chính bị kẹt khó mở"),
                ("Bóng đèn cháy", "Đèn phòng ngủ bị cháy")
            ]

            for _ in range(5):
                loi_random = random.choice(cac_loi)
                su_co = Suco(
                    name=loi_random[0],
                    description=loi_random[1],
                    status=random.choice(['Chưa xử lý', 'Đang xử lý']),
                    client_id=u1.id
                )
                db.session.add(su_co)

            db.session.commit()

            ch = CauHinh(electric_fee=3500, water_fee=15000, internet_fee=100000)
            db.session.add(ch)
            list_nq = [
                "Giữ gìn vệ sinh chung, không vứt rác bừa bãi.",
                "Không gây ồn ào sau 22h đêm.",
                "Đóng tiền phòng trước ngày 5 hàng tháng.",
                "Ra vào cổng nhớ đóng cửa cẩn thận."
            ]
            for content in list_nq:
                db.session.add(NoiQuy(content=content))
            db.session.commit()

            logs = [
                {"ma": "LOG001", "ten": "Nguyễn Văn A", "phong": "A101", "loai": "Ra", "dt": "Cư dân"},
                {"ma": "LOG002", "ten": "Trần Thị B", "phong": "A102", "loai": "Vào", "dt": "Cư dân"},
                {"ma": "LOG003", "ten": "Lê Văn C", "phong": "B201", "loai": "Ra", "dt": "Cư dân"},
                {"ma": "LOG004", "ten": "Khách của A101", "phong": "A101", "loai": "Vào", "dt": "Khách"},
                {"ma": "LOG005", "ten": "Phạm Thị D", "phong": "B203", "loai": "Vào", "dt": "Cư dân"},
                {"ma": "LOG006", "ten": "Hoàng Văn E", "phong": "C301", "loai": "Ra", "dt": "Cư dân"}
            ]
            for l in logs:
                db.session.add(
                    NhatKy(ma_log=l['ma'], nguoi_ten=l['ten'], phong=l['phong'], loai=l['loai'], doi_tuong=l['dt']))
            db.session.commit()
