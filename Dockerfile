# Sử dụng image Python Alpine nhẹ
FROM python:3.10-alpine
# Cài đặt các gói cần thiết
RUN apk update && apk add --no-cache git curl build-base
# Thiết lập thư mục làm việc
WORKDIR /app
# Sao chép file requirements.txt và cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Sao chép toàn bộ mã nguồn vào thư mục làm việc
COPY . .

# Lệnh mặc định để chạy bot
CMD ["python3", "main.py"]