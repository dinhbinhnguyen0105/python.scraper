import phonenumbers
from phonenumbers import PhoneNumberMatcher

text = """
☘️☘️CHO THUÊ CĂN HỘ CHI LĂNG - 2 PHÒNG NGỦ - NỘI THẤT ĐẦY ĐỦ - ĐƯỜNG CHI LĂNG - PHƯỜNG 9 - ĐÀ LẠT - 8 TRIỆU/THÁNG
--------------------
☘️ Diện tích: 60m2 
☘️Kết cấu: 2PN, 2WC, 1pk, bếp, có ban công 
1 phòng 1 giường, 1 phòng giường tầng 
- Đầy đủ nội thất, tiện nghi, có thang máy, máy hút mùi, máy giặt, 2 tivi... 
 -Không cho nuôi thú cưng
-Cho khách nước ngoài thuê 
☘️Giá thuê: 8tr/tháng, cọc 1 đóng 1
-------------------------------------
📲Lh em xem trực tiếp: 07745.179.86 ( zalo em luôn mở)
Cám ơn ạ!
"""

for match in PhoneNumberMatcher(text, "VN"):
    print(match.raw_string)
