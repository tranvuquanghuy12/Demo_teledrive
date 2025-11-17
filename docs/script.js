// --- CẤU HÌNH SERVER ---
const TELEDRIVE_API = 'http://127.0.0.1:8080';

/* ===============================
      HÀM HỖ TRỢ
================================*/
async function safeJSON(response) {
    const text = await response.text();
    try {
        return text ? JSON.parse(text) : {};
    } catch { return {}; }
}
function getCleanText(el) {
    return el ? el.textContent.trim() : "";
}

/* ===============================
      HÀM LOAD CONTENT
================================*/
window.loadContent = async function(id, title) {
    // --- Breadcrumb & Menu ---
    if (!title) {
        const item = document.querySelector(`li[data-target="${id}"]`);
        title = getCleanText(item) || "Thông tin";
        if (item) {
            document.querySelectorAll('#guide-menu li').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        }
    }
    const bc = document.getElementById('breadcrumb-current');
    if (bc) bc.innerText = title;

    const contentDisplay = document.getElementById('content-display');
    contentDisplay.innerHTML = `<div class="loader"></div>`;

    await new Promise(r => setTimeout(r, 200));

    try {
        /* ===============================
              TRANG UPLOAD FILE (MỚI)
        ================================= */
        if (id === 'upload_page') {
            contentDisplay.innerHTML = `
                <div class="post-content" style="max-width: 600px; margin: 0 auto;">
                    <h2 style="text-align:center; color:#1abc9c;"><i class="fas fa-upload"></i> Tải File Lên Telegram</h2>
                    <form id="upload-form" onsubmit="event.preventDefault(); handleUpload(this);">
                        <div class="form-group" style="margin-bottom: 20px;">
                            <label for="file-upload-input" style="display:block; margin-bottom: 5px;">1. Chọn File:</label>
                            <input type="file" id="file-upload-input" name="file" required style="width: 100%; padding: 10px; border: 1px solid #ccc;">
                        </div>
                        <div class="form-group" style="margin-bottom: 20px;">
                            <label for="file-caption" style="display:block; margin-bottom: 5px;">2. Tiêu đề (Caption):</label>
                            <input type="text" id="file-caption" name="caption" class="form-control" placeholder="Tài liệu quan trọng..." style="width: 100%; padding: 10px; border: 1px solid #ccc;">
                        </div>
                        <button type="submit" style="width:100%; padding:12px; background:#1abc9c; color:white; border:none; cursor:pointer;">
                            Tải Lên (Upload)
                        </button>
                    </form>
                    <div id="upload-status" style="margin-top:20px; text-align:center;"></div>
                </div>
            `;
            return;
        }

        /* ===============================
              CÁC TRANG CÒN LẠI (TĨNH)
        ================================= */
        // Các trang 'overview', 'login' (giờ là tĩnh), 'about' v.v. sẽ được load từ đây
        const response = await fetch(`content/${id}.html`);
        if (!response.ok) throw new Error(`File 'content/${id}.html' not found`);
        const html = await response.text();
        contentDisplay.innerHTML = `<div class="post-content">${html}</div>`;

    } catch (error) {
        contentDisplay.innerHTML = `<div style="padding:20px; color:red;">Lỗi: ${error.message}</div>`;
        console.error(error);
    }
};

/* ===============================
      HÀM UPLOAD FILE (THẬT)
================================= */
window.handleUpload = async function(form) {
    const fileInput = document.getElementById('file-upload-input');
    const statusDiv = document.getElementById('upload-status');
    
    if (fileInput.files.length === 0) {
        statusDiv.innerText = "Vui lòng chọn file.";
        return;
    }

    const formData = new FormData(form);
    statusDiv.innerHTML = 'Đang tải lên... <i class="fas fa-spinner fa-spin"></i>';

    try {
        // Gọi API thật (/api/upload)
        const response = await fetch(`${TELEDRIVE_API}/api/upload`, {
            method: 'POST',
            body: formData,
            credentials: 'include' // Quan trọng để xử lý CORS nếu có
        });

        const result = await safeJSON(response);

        if (response.ok) {
            statusDiv.innerHTML = `<span style="color: green;">✅ Tải lên thành công! File: ${result.filename}</span>`;
        } else {
            statusDiv.innerHTML = `<span style="color: red;">❌ Lỗi ${response.status}: ${result.detail || 'Lỗi không xác định'}</span>`;
        }

    } catch (e) {
        statusDiv.innerHTML = `<span style="color: red;">❌ Lỗi kết nối server: ${e.message}</span>`;
    }
};

/* ===============================
             KHỞI TẠO
================================*/
document.addEventListener('DOMContentLoaded', () => {
    const guideMenu = document.getElementById('guide-menu');
    if (guideMenu) {
        guideMenu.addEventListener('click', (event) => {
            const clickedItem = event.target.closest('li');
            if (clickedItem) {
                const targetId = clickedItem.dataset.target;
                const title = getCleanText(clickedItem);
                loadContent(targetId, title);
            }
        });
    }
    loadContent('overview', 'Giới Thiệu Chung');

    window.triggerMenu = function(id) {
        loadContent(id);
    };
});