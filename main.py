import os
from pyrogram import Client, filters, idle # Import idle để giữ bot chạy

# Lấy các key đã được xác nhận là có tồn tại
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN') # The crucial key for bot mode

# Kiểm tra (đã được xác nhận là OK)
if not all([API_ID, API_HASH, BOT_TOKEN]):
    print("FATAL ERROR: Environment variables are missing or undefined!")
    exit(1)

print("SUCCESS: All necessary API keys found. Initializing Bot Client...")

try:
    # KHỞI TẠO CLIENT DƯỚI DẠNG BOT (SỬ DỤNG TOKEN)
    # SỬA LỖI: Bỏ chế độ User Client để tránh hỏi SĐT
    app = Client(
        "bot_session_final", 
        api_id=int(API_ID),
        api_hash=API_HASH,
        bot_token=BOT_TOKEN, # <-- Dùng token để tránh Interactive Login
        workdir="./bot_data"
    )
    
    # Định nghĩa một lệnh đơn giản để kiểm tra
    @app.on_message(filters.command("start"))
    async def start_command(client, message):
        await message.reply_text("Server của anh đã chạy ngon lành! Em có thể bắt đầu lưu file!")

    print("Pyrogram Bot Client is starting and listening...")
    app.start() # Khởi động client
    idle()  # 🌟 FIX: Giữ client chạy liên tục
    app.stop()

except Exception as e:
    print(f"FATAL RUNTIME ERROR: Client failed to start. Error: {e}")