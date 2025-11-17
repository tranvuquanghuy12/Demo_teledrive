import os
import io  # 🌟 FIX 1: IMPORT IO
from contextlib import asynccontextmanager
from pyrogram import Client
from fastapi import FastAPI, UploadFile, HTTPException, Form # 🌟 FIX 2: IMPORT FORM
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# --- CẤU HÌNH ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
STORAGE_CHAT_ID = int(os.environ.get('CHAT_ID', 0))

# Khởi tạo Client (global)
tg_client = Client(
    "bot_session_final", 
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN, 
    workdir="./bot_data"
)

# 🌟 FIX 3: Dùng "lifespan" (hàng mới) thay cho "on_event" (hàng cũ)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Khởi động ---
    if STORAGE_CHAT_ID == 0:
        print("!!! LỖI NGHIÊM TRỌNG: Biến CHAT_ID chưa được set trong file .env !!!")
    else:
        print("Pyrogram Client starting...")
        await tg_client.start()
        print("Pyrogram Client connected successfully.")
    
    yield # <--- Server sẽ chạy ở đây

    # --- Tắt ---
    print("Pyrogram Client stopping...")
    await tg_client.stop()

# Khởi tạo FastAPI App
web_app = FastAPI(title="TeleDrive API", lifespan=lifespan)

# FIX LỖI CORS
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API ENDPOINT (HÀNG THẬT) ---
@web_app.post("/api/upload")
async def upload_file(file: UploadFile, caption: str = Form("Uploaded from Web UI")):
    
    if not tg_client.is_connected:
         raise HTTPException(status_code=503, detail="Telegram client is not running.")
         
    try:
        file_bytes = io.BytesIO(await file.read())
        file_bytes.name = file.filename
        file_bytes.seek(0) # Đã fix lỗi "con trỏ"
        
        print(f"Bắt đầu upload file: {file.filename}...")
        
        await tg_client.send_document(
            chat_id=STORAGE_CHAT_ID,
            document=file_bytes,
            caption=caption
        )
        
        print(f"Upload thành công: {file.filename}")
        return {"status": "success", "filename": file.filename}
    
    except Exception as e:
        print(f"Upload Failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload Failed: {str(e)}")

# --- API PING (Để kiểm tra) ---
@web_app.get("/ping")
def ping():
    return {"pong": True, "client_running": tg_client.is_connected}

# --- RUNNER (Chạy Uvicorn) ---
if __name__ == '__main__':
    uvicorn.run(web_app, host="0.0.0.0", port=8080)