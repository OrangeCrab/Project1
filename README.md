# Project1

**Đề tài: Time series forecasting Web app**
* Giáo viên hướng dẫn: Ts. Đinh Viết Sang
* Giao diện trang web:
<img width="1440" alt="Ảnh chụp Màn hình 2022-01-13 lúc 20 05 11" src="https://user-images.githubusercontent.com/68985886/149335455-fb376ef5-1c02-42f3-84ad-e9d7f1ec5bed.png">

* Project sử dụng:
  * Front-End: HTML, CSS, Js
  * Backend: Python
  * Api: FastApi

* Cài đặt: 
  * Các thư viện yêu cầu được trình bày trong file requirement.txt theo đúng thứ tự
  * Các bước cài đặt:
    - Cài đặt virtualenv
    - Tạo một virtualenv bằng lệnh:
      $ virtualenv [project_name] 
    - Khởi động virtualenv bằng lệnh:
      $ source [project_name]/bin/activate
    - Sau đó cài đặt các thư viện bằng lệnh pip
    - Khởi động server bằng lệnh:
      $ uvicorn [main_file_name]:app --reload
    - Tăt server bằng Ctrl+C / Control^+C
    - Thoát khỏi virtualenv bằng lệnh:
      $ deactivate
      
* Các bước sử dụng:
   - Sau khi khởi động server, truy cập http://127.0.0.1:8000 để vào trang web
   - Dữ liệu đầu vào: 01 file định dạng CSV (Comma Separated Values) với yêu cầu:
      + Trường đầu tiên chứa dữ liệu về thời gian của chuỗi thời gian
      + (Các) trường tiếp theo chứa dữ liệu
   -	Các bước thực hiện để dự báo:
      1.	B1: Tải file dữ liệu (với dữ liệu hợp lệ ở bước này, hiển thị ra đồ thị biểu diễn dữ liệu được tải lên, nếu không, hiện ra thông báo tương ứng)
      2.	B2: Chọn trường dữ liệu muốn dự đoán
      3.	B3: Chọn chu kỳ thời gian trong chuỗi lịch sử và số đơn vị thời gian muốn dự báo
      4.	B4: Chọn mô hình dự báo (nếu dữ liệu tại bước này hợp lệ, hiển thị ra được đồ thị trực quan cho dữ liệu dự đoán và đồ thị phân tích dữ liệu, nếu không,       đưa ra thông báo phù hợp)
      5.	B5: Có thể thực hiện lại bước 2, 3 cuối cùng là 4 để thay đổi nhu cầu dự báo dựa trên dữ liệu được tải lên ở bước 1


* Để phát triển thêm các mô hình dự báo khác
* Sinh viên thực hiện: Vũ Hồng Sơn - 20194161
* Email: son.vh194161@sis.hust.edu.vn



