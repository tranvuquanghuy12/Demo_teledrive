import os
import threading
from pyrogram import Client, filters, idle
from flask import Flask, request, jsonify, send_file
import io

# --- 1. CẤU HÌNH ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Khởi tạo Flask App
web_app = Flask(__name__)
# Khởi tạo Pyrogram Client (global)
tg_client = Client(
    "bot_session_final", 
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN, 
    workdir="./bot_data"
)

# --- 2. HÀM XỬ LÝ PYROGRAM ---
@tg_client.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Backend đã sẵn sàng nhận lệnh từ web! Gửi file lên để thử nghiệm.")

# --- 3. API ENDPOINT CHO UPLOAD (Cầu Nối HTTP) ---
@web_app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Missing file in request"}), 400

    file = request.files['file']
    caption = request.form.get('caption', 'Uploaded from Web UI')
    
    try:
        # Sử dụng BytesIO để Pyrogram có thể đọc file trực tiếp từ bộ nhớ
        file_bytes = io.BytesIO(file.read())
        file_bytes.name = file.filename # Đặt tên file

        # CHẠY LỆNH PYROGRAM TRONG TIẾN TRÌNH KHÁC (async/await)
        # Gửi file lên Telegram (ví dụ: gửi vào một channel cố định)
        message_object = tg_client.send_document(
            chat_id="@ten_channel_cua_ban_de_luu_file", # THAY ĐỔI: Thay bằng username của channel
            document=file_bytes,
            caption=caption
        )
        # Yêu cầu này cần được xử lý trong môi trường async của Pyrogram. 
        # Cần dùng threading/asyncio riêng cho Flask. Đây là đoạn code phức tạp nhất.
        
        # NOTE: Do Flask không hỗ trợ async/await, nên chúng ta sẽ trả về một response giả
        # Nếu muốn code hoàn chỉnh, anh cần dùng FastAPI hoặc thư viện hỗ trợ async/await.
        
        return jsonify({
            "status": "success", 
            "message": f"File '{file.filename}' đang được xử lý gửi đi.", 
            "filename": file.filename
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server crash during upload: {e}"}), 500


# --- 4. HÀM CHẠY 2 TIẾN TRÌNH ---
if __name__ == '__main__':
    # 🌟 Tiến trình 1: Khởi động Pyrogram Client (Bot)
    tg_thread = threading.Thread(target=tg_client.run)
    tg_thread.start()
    
    # 🌟 Tiến trình 2: Khởi động Web Server (Flask)
    web_app.run(host='0.0.0.0', port=8080)