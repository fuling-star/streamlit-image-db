# -*- coding: utf-8 -*-
import os
import sqlite3
from datetime import datetime
import streamlit as st

# ========== 1. 目录与数据库初始化 ==========
DB_FILE = "data.db"
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS item (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            content     TEXT,
            image_path  TEXT,
            create_time TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ========== 2. 业务函数 ==========
def add_item(title, content, image_file):
    """新增一条记录，image_file 是 streamlit 上传的文件对象，可为 None"""
    image_path = ""
    if image_file is not None:
        # 用时间戳重命名，避免同名覆盖
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        ext = os.path.splitext(image_file.name)[1].lower()
        filename = ts + ext
        full_path = os.path.join(UPLOAD_DIR, filename)
        with open(full_path, "wb") as f:
            f.write(image_file.getbuffer())
        image_path = full_path

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO item (title, content, image_path, create_time) VALUES (?, ?, ?, ?)",
        (title, content, image_path, now)
    )
    conn.commit()
    conn.close()
    return True

def list_items():
    """返回所有记录"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, image_path, create_time FROM item ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

# ========== 3. 界面 ==========
st.set_page_config(page_title="图文信息库", page_icon="📁")
st.title("📁 图文信息库")

tab1, tab2 = st.tabs(["➕ 新增", "📋 列表"])

# --- 新增页 ---
with tab1:
    with st.form("add_form", clear_on_submit=True):
        title = st.text_input("标题 *")
        content = st.text_area("内容")
        image = st.file_uploader("图片（可选）", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("保存")

        if submitted:
            if not title.strip():
                st.warning("标题不能为空")
            elif image is not None and image.size > 5 * 1024 * 1024:
                st.warning("图片不能超过 5MB")
            else:
                add_item(title.strip(), content, image)
                st.success("保存成功！")

# --- 列表页 ---
with tab2:
    rows = list_items()
    if not rows:
        st.info("暂无记录，先去「新增」里添加一条吧")
    else:
        st.write(f"共 {len(rows)} 条记录")
        for r in rows:
            rid, title, content, image_path, create_time = r
            with st.expander(f"[{rid}] {title} — {create_time}"):
                st.write(content if content else "（无内容）")
                if image_path and os.path.exists(image_path):
                    st.image(image_path, width=300)
                else:
                    st.caption("无图片")
