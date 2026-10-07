# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Đỗ Nguyễn Ngọc Long |
| MSSV | 2A202602390 |
| Lớp / Khóa | K4 - L3B |
| Repo GitHub | https://github.com/ngoclongdo/K4-L3L4-Track2-Day21-CI-CD-for-AI-Systems |
| Ngày nộp | 10/7/2026 |

---

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.7109 | 0.8780 |
| 2 | 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 3 | 200 | 0.1 | 5 | 0.7149 | 0.8740 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`.

**Lý do:** Bộ siêu tham số ở lần chạy 3 đạt chỉ số `f1_score` cao nhất (0.7149), vượt qua ngưỡng quy định của Quality Gate (>= 0.65). Mặc dù lần chạy 1 có `accuracy` cao hơn một chút (0.8780 so với 0.8740), nhưng `f1_score` của lần 3 lại tốt hơn rõ rệt trên lớp thiểu số (thu nhập > 50K), cho thấy accuracy cao nhất không đồng nghĩa với khả năng phân loại tốt nhất trên dữ liệu mất cân bằng. Quan sát thực tế cho thấy sự đánh đổi: khi giảm `n_estimators` và `learning_rate` (lần 2), mô hình bị underfitting khiến `f1_score` sụt giảm mạnh xuống 0.6051; trong khi đó việc tăng độ sâu cây lên 5 cùng 200 estimators giúp mô hình nắm bắt tốt hơn các đặc trưng phức tạp.

---

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Tập dữ liệu Adult / Census Income có phân bố lớp mất cân bằng nghiêm trọng: chỉ khoảng 24,8% số người có thu nhập cao (`target = 1`), trong khi 75,2% thuộc nhóm thu nhập thấp (`target = 0`). Nếu một mô hình dự đoán nhãn 0 cho mọi mẫu mà không học được bất kỳ quy luật nào, độ chính xác (accuracy) vẫn đạt tới 75,2%, gây hiểu nhầm về hiệu quả thực tế. 

Do đó, Quality Gate cần đặt trên chỉ số F1-score của riêng lớp dương (`target = 1`), đo lường sự cân bằng hài hòa giữa Precision (độ chuẩn xác khi dự đoán thu nhập cao) và Recall (khả năng bao quát, tránh bỏ sót người thu nhập cao). Trong mã nguồn, không sử dụng `average="weighted"` hay `average="macro"` vì việc tính trung bình sẽ bị lớp đa số (75,2%) lấn át và che lấp hiệu năng phân loại thực tế trên lớp thiểu số.

---

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Lỗi xác thực AWS CLI và DVC remote | Access Key cũ bị hết hạn hoặc thiếu quyền | Tạo IAM User mới, cấu hình Access Key vào AWS CLI và cấp quyền AmazonS3FullAccess |
| Lỗi import Cython loss khi service khởi động | Khác biệt phiên bản scikit-learn giữa máy local (1.4.2) và VM (1.7.2) khi unpickle model | Cài đặt chính xác phiên bản `scikit-learn==1.4.2` trên Cloud VM để đồng nhất môi trường |
| Lỗi parse private key ở bước SSH deploy | Action appleboy/ssh-action kén định dạng OpenSSH private key | Chuyển sang sử dụng lệnh OpenSSH client chuẩn của hệ điều hành Linux trong workflow |

---

## 4. So Sánh Bước 2 và Bước 3 (bắt buộc, 2 - 3 câu)

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (chỉ `train_batch1` - 22.361 mẫu) | 0.7149 | 0.8740 |
| Bước 3 (thêm `train_batch2` - 44.722 mẫu) | 0.7354 | 0.8820 |

**Nhận xét:** Khi bổ sung thêm 22.361 mẫu dữ liệu mới (`train_batch2`), cả `f1_score` và `accuracy` đều có sự cải thiện nhẹ (F1 tăng từ 0.7149 lên 0.7354, Accuracy tăng từ 87,40% lên 88,20%). Do hai tập dữ liệu được lấy từ cùng một nguồn điều tra dân số và có cùng phân phối, sự gia tăng F1 chủ yếu phản ánh việc mô hình học thêm được một số trường hợp biên của lớp thiểu số khi số lượng mẫu tăng gấp đôi. Quan trọng nhất, quy trình Continuous Training đã chứng minh tính tự động hóa hoàn chỉnh: chỉ cần cập nhật con trỏ DVC là GitHub Actions tự động kích hoạt huấn luyện lại và deploy model mới lên máy chủ EC2.

