from datetime import datetime
import difflib
import glob
import io
import json
import math
import os
import random
import re
from collections import Counter
from PIL import Image, ImageEnhance
from flask import Flask, jsonify, render_template_string, request

# --- Termux Tesseract Binary Path Auto-Fix ---
TERMUX_TESSERACT_PATH = "/data/data/com.termux/files/usr/bin/tesseract"
try:
    import pytesseract
    if os.path.exists(TERMUX_TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = TERMUX_TESSERACT_PATH
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Safe Import for PyPDF2
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

app = Flask(__name__)

# Upload folder config completely removed for pure RAM processing

active_ai = None
current_model_name = "None"
startup_notice = ""
selected_model_val = "v3.6"
selected_memory_file = ""

def check_tensorflow():
    try:
        import tensorflow
        return True
    except ImportError:
        return False

def get_valid_memory_files():
    valid = []
    for f in glob.glob("ai_memory_*.json"):
        if os.path.exists(f) and os.path.getsize(f) >= 50:
            valid.append(f)
    valid.sort(key=lambda x: os.path.getsize(x), reverse=True)
    return valid

def load_ai_engine(model_type="v3.6", force_new=False, target_memory=None):
    global active_ai, current_model_name, startup_notice, selected_model_val, selected_memory_file

    tf_available = check_tensorflow()
    requested_v4 = model_type == "v4.0"

    if requested_v4 and not tf_available:
        model_type = "v3.6"
        selected_model_val = "v3.6"
        startup_notice = "⚠️ Cannot switch to v4.0 (Neural): TensorFlow library is not installed! Auto-fallback to v3.6 Legacy."
    else:
        selected_model_val = model_type
        startup_notice = ""

    try:
        existing_files = glob.glob("ai_memory_*.json")
        for f in existing_files:
            if os.path.exists(f) and os.path.getsize(f) < 50:
                try:
                    os.remove(f)
                except Exception:
                    pass

        valid_files = get_valid_memory_files()
        target_file = (
            target_memory
            if target_memory
            else (valid_files[0] if valid_files and not force_new else None)
        )
        extracted_name = "user"

        if target_file:
            filename_only = os.path.basename(target_file).replace(".json", "")
            parts = filename_only.split("_")
            if (
                len(parts) >= 3
                and parts[0] == "ai"
                and parts[1] == "memory"
            ):
                extracted_name = parts[2]

        selected_memory_file = target_file if target_file else ""

        if model_type == "v4.0" and tf_available:
            import main_engine as engine_module

            active_ai = engine_module.MainAIEngine(user_name=extracted_name)
            current_model_name = "v4.0 (TensorFlow Neural)"
            startup_notice = f"TensorFlow Engine loaded. File: {target_file if target_file else 'New'} ({extracted_name.capitalize()})"
        else:
            import v5_6_AI_engine as engine_module

            if target_file and not force_new:
                active_ai = engine_module.MainAIEngine(user_name=extracted_name)
                active_ai.memory_file = target_file
                active_ai.load_memory()
                current_model_name = "v3.6 (Legacy Lightweight)"
                if not (requested_v4 and not tf_available):
                    startup_notice = f"Switched to v3.6. Memory Loaded: {target_file} ({extracted_name.capitalize()})"
            else:
                random_id = random.randint(1000, 9999)
                new_file_name = f"ai_memory_{extracted_name}_{random_id}.json"
                active_ai = engine_module.MainAIEngine(user_name=extracted_name)
                active_ai.memory_file = new_file_name
                active_ai.memory_db = []
                active_ai.save_memory()
                selected_memory_file = new_file_name
                current_model_name = "v3.6 (Legacy Lightweight)"
                if not (requested_v4 and not tf_available):
                    startup_notice = f"Switched to v3.6. Nayi file bani: {new_file_name}"

    except Exception as e:
        active_ai = None
        current_model_name = "Error"
        startup_notice = f"Error loading engine: {str(e)}"

initial_model = "v4.0" if check_tensorflow() else "v3.6"
load_ai_engine(initial_model)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Infinity AI Hub</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body {
            height: 100%; width: 100%;
            background: #09090b; color: #ececec;
            font-family: 'Inter', -apple-system, sans-serif;
            overflow: hidden; -webkit-user-select: none; user-select: none;
        }
        .app-wrapper { display: flex; flex-direction: column; height: 100dvh; width: 100%; position: relative; }
        header { 
            background: #09090b; padding: 14px 18px; 
            display: flex; justify-content: space-between; align-items: center; 
            flex-shrink: 0; z-index: 10; border-bottom: 1px solid #18181b;
        }
        .icon-btn {
            background: #18181b; border: 1px solid #27272a; color: #e4e4e7;
            width: 38px; height: 38px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; font-size: 16px; transition: background 0.2s;
        }
        .icon-btn:hover { background: #27272a; }
        .brand-title { font-size: 15px; font-weight: 600; color: #f4f4f5; letter-spacing: -0.3px; }

        .sidebar-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7); backdrop-filter: blur(4px);
            z-index: 99; opacity: 0; pointer-events: none; transition: opacity 0.3s ease;
        }
        .sidebar-overlay.active { opacity: 1; pointer-events: auto; }
        .sidebar {
            position: fixed; top: 0; left: -300px; width: 290px; height: 100%;
            background: #0e0e11; border-right: 1px solid #1f1f23; z-index: 100;
            display: flex; flex-direction: column; padding: 20px 16px; gap: 16px;
            transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .sidebar.active { left: 0; }
        .sidebar-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 6px; }
        .sidebar-title { font-size: 16px; font-weight: 700; color: #fff; }
        .btn-new-chat {
            background: #18181b; color: #fff; border: 1px solid #27272a;
            padding: 12px; border-radius: 12px; font-weight: 600; font-size: 13px;
            cursor: pointer; display: flex; align-items: center; gap: 8px; transition: all 0.2s;
        }
        .btn-new-chat:hover { background: #27272a; border-color: #3f3f46; }
        .sidebar-section-title {
            font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px;
            color: #71717a; font-weight: 600; margin-top: 8px; display: flex; justify-content: space-between;
        }
        .sidebar-section-title span { font-size: 9px; color: #52525b; text-transform: none; }
        .memory-list-container { display: flex; flex-direction: column; gap: 6px; overflow-y: auto; flex: 1; }
        .memory-item {
            display: flex; align-items: center; gap: 10px; padding: 12px 14px;
            background: #141417; border: 1px solid #1f1f24; border-radius: 10px;
            cursor: pointer; font-size: 13px; color: #a1a1aa; transition: all 0.2s; position: relative;
        }
        .memory-item:hover { background: #1c1c21; color: #fff; }
        .memory-item.active { background: #1e1b4b; border-color: #4f46e5; color: #c7d2fe; font-weight: 600; }

        .chat-container { 
            flex: 1; overflow-y: auto; -webkit-overflow-scrolling: touch;
            padding: 16px; display: flex; flex-direction: column; gap: 12px; 
            max-width: 800px; width: 100%; margin: 0 auto; -webkit-user-select: text; user-select: text;
        }
        .message { padding: 12px 16px; border-radius: 14px; max-width: 85%; line-height: 1.5; word-break: break-word; font-size: 14px; display: flex; flex-direction: column; gap: 8px; }
        .user-msg { background: #4f46e5; align-self: flex-end; color: #ffffff; border-bottom-right-radius: 4px; }
        .ai-msg { background: #141417; align-self: flex-start; border: 1px solid #232328; color: #d1d5db; border-bottom-left-radius: 4px; white-space: pre-wrap; }
        .notice-msg { 
            background: rgba(234, 179, 8, 0.08); border: 1px solid rgba(234, 179, 8, 0.25); 
            color: #fde047; align-self: center; font-size: 12px; text-align: center; width: 100%; border-radius: 10px;
        }

        .loading-loader-msg { display: flex; flex-direction: row; align-items: center; gap: 8px; width: fit-content; }
        .typing-dots { display: flex; align-items: center; gap: 5px; }
        .typing-dots span {
            width: 7px; height: 7px; background-color: #6366f1; border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        .typing-dots span:nth-child(3) { animation-delay: 0s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0.3); opacity: 0.4; }
            40% { transform: scale(1); opacity: 1; }
        }
        .loading-text { font-size: 13px; color: #a1a1aa; font-weight: 500; }

        .attachment-preview-badge {
            display: flex; align-items: center; gap: 8px; background: rgba(0,0,0,0.25);
            padding: 6px 10px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);
            max-width: 100%; width: fit-content;
        }
        .attachment-preview-badge img { width: 50px; height: 50px; object-fit: cover; border-radius: 6px; }
        .attachment-preview-badge .file-icon-box {
            width: 38px; height: 38px; background: #27272a; border-radius: 8px;
            display: flex; align-items: center; justify-content: center; font-size: 18px;
        }
        .attachment-filename { font-size: 12px; font-weight: 500; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; max-width: 180px; }

        .input-wrapper { padding: 12px 16px 20px 16px; background: #09090b; flex-shrink: 0; width: 100%; max-width: 800px; margin: 0 auto; }
        .input-box { display: flex; flex-direction: column; padding: 10px 14px; background: #131316; border: 1px solid #232328; border-radius: 18px; gap: 10px; transition: border-color 0.2s; }
        .input-box:focus-within { border-color: #3f3f46; }

        .preview-bar { display: none; align-items: center; gap: 10px; padding: 4px; background: #1c1c21; border-radius: 12px; border: 1px solid #2a2a32; width: fit-content; position: relative; }
        .preview-bar.active { display: flex; }
        .preview-thumb { width: 44px; height: 44px; border-radius: 8px; object-fit: cover; }
        .preview-doc-icon { width: 44px; height: 44px; background: #27272a; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .preview-title { font-size: 12px; color: #e4e4e7; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 500; }
        .btn-remove-preview { background: #27272a; border: none; color: #a1a1aa; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 12px; margin-right: 4px; transition: all 0.2s; }
        .btn-remove-preview:hover { background: #ef4444; color: #fff; }

        input[type="text"] { width: 100%; padding: 4px; border: none; background: transparent; color: #fff; outline: none; font-size: 14px; -webkit-user-select: text; user-select: text; }
        input[type="text"]::placeholder { color: #52525b; }
        .input-actions { display: flex; justify-content: space-between; align-items: center; }

        .action-group { display: flex; align-items: center; gap: 8px; }

        .btn-action-label {
            width: 32px; height: 32px; background: #1c1c21; border: 1px solid #2c2c34;
            color: #e4e4e7; border-radius: 50%; display: flex; align-items: center; justify-content: center;
            cursor: pointer; font-size: 16px; transition: all 0.2s; user-select: none; margin: 0;
        }
        .btn-action-label:hover { background: #27272a; border-color: #3f3f46; }

        .model-badge-btn {
            background: #1c1c21; color: #e4e4e7; border: 1px solid #2c2c34;
            padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 500;
            display: flex; align-items: center; gap: 6px; cursor: pointer; transition: all 0.2s;
        }
        .model-badge-btn:hover { background: #27272a; border-color: #3f3f46; }

        button.send-btn { 
            width: 32px; height: 32px; background: #4f46e5; color: white; border: none; 
            border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 14px; transition: background 0.2s; 
        }
        button.send-btn:hover { background: #4338ca; }

        .modal-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.75); backdrop-filter: blur(5px); z-index: 200;
            display: none; align-items: center; justify-content: center; padding: 20px;
        }
        .modal-overlay.active { display: flex; }
        .modal-card {
            background: #121216; border: 1px solid #27272d; border-radius: 20px;
            width: 100%; max-width: 380px; padding: 22px; display: flex; flex-direction: column; gap: 16px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.6); animation: modalIn 0.2s ease-out;
        }
        @keyframes modalIn { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
        .modal-header { display: flex; justify-content: space-between; align-items: center; }
        .modal-title { font-size: 16px; font-weight: 600; color: #fff; }
        .modal-body { display: flex; flex-direction: column; gap: 10px; }
        .modal-text { font-size: 13px; color: #a1a1aa; line-height: 1.5; }
        .modal-text b { color: #f43f5e; }
        .model-card-option {
            background: #18181d; border: 1px solid #232328; border-radius: 12px;
            padding: 12px 14px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;
        }
        .model-card-option:hover { background: #22222a; border-color: #3f3f46; }
        .model-card-option.selected { background: #1e1b4b; border-color: #6366f1; }
        .model-opt-info h4 { font-size: 14px; color: #f4f4f5; font-weight: 600; }
        .model-opt-info p { font-size: 11px; color: #a1a1aa; margin-top: 2px; }
        .modal-input { width: 100%; background: #18181d; border: 1px solid #27272a; padding: 12px 14px; border-radius: 10px; color: #fff; outline: none; font-size: 14px; }
        .modal-input:focus { border-color: #4f46e5; }
        .modal-actions-row { display: flex; gap: 10px; margin-top: 4px; }
        .modal-btn-confirm { flex: 1; background: #4f46e5; color: #fff; border: none; padding: 12px; border-radius: 10px; font-weight: 600; font-size: 13px; cursor: pointer; transition: background 0.2s; text-align: center; }
        .modal-btn-confirm:hover { background: #4338ca; }
        .modal-btn-secondary { flex: 1; background: #1c1c21; color: #e4e4e7; border: 1px solid #2c2c34; padding: 12px; border-radius: 10px; font-weight: 600; font-size: 13px; cursor: pointer; transition: background 0.2s; text-align: center; }
        .modal-btn-secondary:hover { background: #27272a; }
        .modal-btn-cancel { flex: 1; background: #1f1f24; color: #d4d4d8; border: 1px solid #2e2e36; padding: 12px; border-radius: 10px; font-weight: 600; font-size: 13px; cursor: pointer; transition: background 0.2s; }
        .modal-btn-cancel:hover { background: #27272f; }
        .modal-btn-danger { flex: 1; background: #e11d48; color: #fff; border: none; padding: 12px; border-radius: 10px; font-weight: 600; font-size: 13px; cursor: pointer; transition: background 0.2s; }
        .modal-btn-danger:hover { background: #be123c; }
    </style>
    </head>
<body>
    <div class="sidebar-overlay" id="overlay" onclick="toggleSidebar()"></div>

    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span class="sidebar-title">Infinity AI Hub</span>
            <button class="icon-btn" onclick="toggleSidebar()">✕</button>
        </div>
        <button class="btn-new-chat" onclick="openNewFileModal()">
            <span>➕</span> New JSON Memory
        </button>
        <div class="sidebar-section-title">
            <span>Saved Memories</span>
            <span>(Hold to Delete)</span>
        </div>
        <div class="memory-list-container" id="memory-list">
            {% for mf in memory_files %}
                <div class="memory-item {% if mf == current_memory %}active{% endif %}" 
                     data-file="{{ mf }}"
                     onmousedown="startPress(this)" 
                     onmouseup="endPress(this)" 
                     onmouseleave="cancelPress(this)"
                     ontouchstart="startPress(this)" 
                     ontouchend="endPress(this)"
                     ontouchcancel="cancelPress(this)">
                    <span>💾</span>
                    <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ mf }}</span>
                </div>
            {% endfor %}
        </div>
    </div>

    <input type="file" id="attach-file-input" accept="image/*,.pdf" style="display: none;" onchange="handleFileSelected(event)">

    <div class="modal-overlay" id="settingsModal" onclick="closeModal('settingsModal', event)">
        <div class="modal-card">
            <div class="modal-header">
                <div class="modal-title">Settings & System Info</div>
                <button class="icon-btn" onclick="closeModalDirect('settingsModal')">✕</button>
            </div>
            <div class="modal-body">
                <div class="modal-text">
                    <p><b>Active Model:</b> <span id="setting-active-model">{{ selected_val }}</span></p>
                    <p style="margin-top: 6px;"><b>Memory File:</b> <span id="setting-active-mem">{{ current_memory }}</span></p>
                    <p style="margin-top: 6px;"><b>PDF & OCR Modules:</b> PyPDF2 & PyTesseract Active</p>
                </div>
                <div class="modal-actions-row">
                    <button class="modal-btn-confirm" onclick="openModal('modelModal'); closeModalDirect('settingsModal');">Switch Engine</button>
                    <button class="modal-btn-secondary" onclick="exportChatHistory()">📥 Export Chat</button>
                </div>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="modelModal" onclick="closeModal('modelModal', event)">
        <div class="modal-card">
            <div class="modal-header">
                <div class="modal-title">Select AI Engine</div>
                <button class="icon-btn" onclick="closeModalDirect('modelModal')">✕</button>
            </div>
            <div class="modal-body">
                <div class="model-card-option {% if selected_val == 'v4.0' %}selected{% endif %}" onclick="selectModel('v4.0')">
                    <div class="model-opt-info">
                        <h4>v4.0 (Neural Engine)</h4>
                        <p>TensorFlow deep-learning classifier with embeddings</p>
                    </div>
                    <span>🧠</span>
                </div>
                <div class="model-card-option {% if selected_val == 'v3.6' %}selected{% endif %}" onclick="selectModel('v3.6')">
                    <div class="model-opt-info">
                        <h4>v3.6 (Smart Legacy)</h4>
                        <p>Fast keyword similarity engine (Zero-dependency)</p>
                    </div>
                    <span>⚡</span>
                </div>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="newFileModal" onclick="closeModal('newFileModal', event)">
        <div class="modal-card">
            <div class="modal-header">
                <div class="modal-title">Create New Memory</div>
                <button class="icon-btn" onclick="closeModalDirect('newFileModal')">✕</button>
            </div>
            <div class="modal-body">
                <input type="text" id="new-username-input" class="modal-input" placeholder="Enter owner name (e.g. alex)">
                <button class="modal-btn-confirm" onclick="submitNewJson()">Create File</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="deleteModal" onclick="closeModal('deleteModal', event)">
        <div class="modal-card">
            <div class="modal-header">
                <div class="modal-title">Delete Memory File?</div>
                <button class="icon-btn" onclick="closeModalDirect('deleteModal')">✕</button>
            </div>
            <div class="modal-body">
                <p class="modal-text">Are you sure you want to permanently delete <b id="target-delete-filename"></b>? Action irreversible.</p>
                <div class="modal-actions-row">
                    <button class="modal-btn-cancel" onclick="closeModalDirect('deleteModal')">Cancel</button>
                    <button class="modal-btn-danger" onclick="confirmDeleteMemory()">Delete</button>
                </div>
            </div>
        </div>
    </div>

    <div class="app-wrapper">
        <header>
            <button class="icon-btn" onclick="toggleSidebar()">☰</button>
            <div class="brand-title">Infinity AI Hub</div>
            <button class="icon-btn" onclick="openModal('settingsModal')">⚙️</button>
        </header>

        <div class="chat-container" id="chat-box">
            {% if notice %}
            <div class="message notice-msg">{{ notice }}</div>
            {% endif %}
            <div class="message ai-msg"><span>Hey bro! Smart Image OCR 🖼️ & PDF Reader 📄 are fully active! 😎</span></div>
        </div>

        <div class="input-wrapper">
            <div class="input-box">
                <div class="preview-bar" id="attachment-preview">
                    <div id="preview-content-box"></div>
                    <span class="preview-title" id="preview-file-name">filename.pdf</span>
                    <button class="btn-remove-preview" onclick="removeSelectedFile()">✕</button>
                </div>

                <input type="text" id="user-input" placeholder="Message Infinity AI..." autofocus>
                
                <div class="input-actions">
                    <div class="action-group">
                        <label for="attach-file-input" class="btn-action-label" title="Attach Image or PDF">➕</label>
                        <div class="model-badge-btn" onclick="openModal('modelModal')">
                            <span id="model-badge-text">{% if selected_val == 'v4.0' %}🔴 v4.0 (Neural){% else %}⚡ v3.6 (Legacy){% endif %}</span>
                            <span style="font-size: 10px;">▼</span>
                        </div>
                    </div>

                    <button class="send-btn" onclick="sendMessage()">➔</button>
                </div>
            </div>
        </div>
    </div>
    <script>
        const chatBox = document.getElementById('chat-box');
        const userInput = document.getElementById('user-input');
        let currentSelectedModel = "{{ selected_val }}";
        let currentSelectedMemory = "{{ current_memory }}";
        
        let selectedFile = null;
        let pressTimer = null;
        let isLongPressTriggered = false;
        let fileToDelete = "";

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('active');
            document.getElementById('overlay').classList.toggle('active');
        }

        function openModal(id) { document.getElementById(id).classList.add('active'); }
        function closeModalDirect(id) { document.getElementById(id).classList.remove('active'); }
        function closeModal(id, event) {
            if (event.target.id === id) closeModalDirect(id);
        }

        function openNewFileModal() {
            toggleSidebar();
            openModal('newFileModal');
            setTimeout(() => document.getElementById('new-username-input').focus(), 100);
        }

        userInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') sendMessage();
        });

        function handleFileSelected(event) {
            const file = event.target.files[0];
            if (!file) return;

            selectedFile = file;
            const previewBar = document.getElementById('attachment-preview');
            const previewBox = document.getElementById('preview-content-box');
            const previewName = document.getElementById('preview-file-name');

            previewName.innerText = file.name;
            previewBox.innerHTML = '';

            if (file.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.className = 'preview-thumb';
                previewBox.appendChild(img);
            } else {
                const iconBox = document.createElement('div');
                iconBox.className = 'preview-doc-icon';
                iconBox.innerText = '📄';
                previewBox.appendChild(iconBox);
            }

            previewBar.classList.add('active');
        }

        function removeSelectedFile() {
            selectedFile = null;
            document.getElementById('attach-file-input').value = '';
            document.getElementById('attachment-preview').classList.remove('active');
        }

        function appendMessage(text, sender, isNotice = false, attachment = null) {
            const div = document.createElement('div');
            div.className = isNotice ? 'message notice-msg' : `message ${sender === 'user' ? 'user-msg' : 'ai-msg'}`;

            if (attachment) {
                const badge = document.createElement('div');
                badge.className = 'attachment-preview-badge';
                if (attachment.type === 'image') {
                    badge.innerHTML = `<img src="${attachment.src}" /><span class="attachment-filename">${attachment.name}</span>`;
                } else {
                    badge.innerHTML = `<div class="file-icon-box">📄</div><span class="attachment-filename">${attachment.name}</span>`;
                }
                div.appendChild(badge);
            }

            if (text) {
                const textSpan = document.createElement('span');
                textSpan.innerText = text;
                div.appendChild(textSpan);
            }

            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function showLoadingIndicator(messageText = 'Analyzing...') {
            const loaderDiv = document.createElement('div');
            loaderDiv.id = 'active-loading-indicator';
            loaderDiv.className = 'message ai-msg loading-loader-msg';
            loaderDiv.innerHTML = `
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <span class="loading-text">${messageText}</span>
            `;
            chatBox.appendChild(loaderDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function removeLoadingIndicator() {
            const loader = document.getElementById('active-loading-indicator');
            if (loader) loader.remove();
        }

        async function sendMessage() {
            const text = userInput.value.trim();
            const fileToUpload = selectedFile;

            if (!text && !fileToUpload) return;

            let fileAttachmentObj = null;
            if (fileToUpload) {
                fileAttachmentObj = {
                    name: fileToUpload.name,
                    type: fileToUpload.type.startsWith('image/') ? 'image' : 'pdf',
                    src: fileToUpload.type.startsWith('image/') ? URL.createObjectURL(fileToUpload) : null
                };
            }

            appendMessage(text, 'user', false, fileAttachmentObj);
            userInput.value = '';
            removeSelectedFile();

            try {
                if (fileToUpload) {
                    const isImg = fileToUpload.type.startsWith('image/');
                    showLoadingIndicator(isImg ? 'Scanning image...' : 'Reading PDF file...');

                    const formData = new FormData();
                    formData.append('file', fileToUpload);
                    formData.append('user_query', text);

                    const endpoint = fileToUpload.name.toLowerCase().endsWith('.pdf') ? '/upload_pdf' : '/upload_image';
                    const fileRes = await fetch(endpoint, { method: 'POST', body: formData });
                    const fileData = await fileRes.json();

                    removeLoadingIndicator();
                    appendMessage(fileData.reply, 'ai');
                    return;
                }

                if (text) {
                    showLoadingIndicator('Thinking...');
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: text })
                    });
                    const data = await response.json();
                    
                    removeLoadingIndicator();
                    appendMessage(data.reply, 'ai');
                }
            } catch (err) {
                removeLoadingIndicator();
                appendMessage("Communication error with local engine!", 'ai', true);
            }
        }

        function exportChatHistory() {
            closeModalDirect('settingsModal');
            const messages = chatBox.querySelectorAll('.message');
            if (messages.length === 0) return;

            let exportText = "=== Infinity AI Hub - Chat Export ===\\n\\n";
            messages.forEach(msg => {
                if (msg.classList.contains('user-msg')) {
                    exportText += `[User]: ${msg.innerText}\\n\\n`;
                } else if (msg.classList.contains('ai-msg')) {
                    exportText += `[AI Engine]: ${msg.innerText}\\n\\n`;
                }
            });

            const blob = new Blob([exportText], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chat_export_${new Date().toISOString().slice(0, 10)}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        async function selectModel(modelType) {
            closeModalDirect('modelModal');
            const response = await fetch('/switch_model', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: modelType, memory: currentSelectedMemory })
            });
            const data = await response.json();
            
            currentSelectedModel = data.selected_val;
            document.getElementById('model-badge-text').innerText = data.selected_val === 'v4.0' ? '🔴 v4.0 (Neural)' : '⚡ v3.6 (Legacy)';
            document.getElementById('setting-active-model').innerText = data.selected_val;
            
            if (data.notice) appendMessage(data.notice, 'ai', true);
        }

        function startPress(elem) {
            isLongPressTriggered = false;
            pressTimer = setTimeout(() => {
                isLongPressTriggered = true;
                const fileName = elem.getAttribute('data-file');
                promptDeleteModal(fileName);
            }, 600);
        }

        function endPress(elem) {
            clearTimeout(pressTimer);
            if (!isLongPressTriggered) {
                const fileName = elem.getAttribute('data-file');
                selectMemory(fileName);
            }
        }

        function cancelPress(elem) { clearTimeout(pressTimer); }

        function promptDeleteModal(fileName) {
            fileToDelete = fileName;
            document.getElementById('target-delete-filename').innerText = fileName;
            openModal('deleteModal');
        }

        async function confirmDeleteMemory() {
            closeModalDirect('deleteModal');
            if (!fileToDelete) return;

            const response = await fetch('/delete_memory', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ memory_file: fileToDelete, model: currentSelectedModel })
            });
            const data = await response.json();
            
            if (data.notice) appendMessage(data.notice, 'ai', true);

            if (data.status === 'success') {
                currentSelectedMemory = data.current_memory;
                document.getElementById('setting-active-mem').innerText = data.current_memory;
                renderMemoryList(data.memory_files, data.current_memory);
            }
            fileToDelete = "";
        }

        async function selectMemory(memoryFileName) {
            toggleSidebar();
            const response = await fetch('/switch_memory', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ memory_file: memoryFileName, model: currentSelectedModel })
            });
            const data = await response.json();
            currentSelectedMemory = data.current_memory;
            document.getElementById('setting-active-mem').innerText = data.current_memory;
            
            document.querySelectorAll('.memory-item').forEach(el => {
                if (el.getAttribute('data-file') === memoryFileName) el.classList.add('active');
                else el.classList.remove('active');
            });

            if (data.notice) appendMessage(data.notice, 'ai', true);
        }

        function renderMemoryList(memoryFiles, activeFile) {
            const container = document.getElementById('memory-list');
            container.innerHTML = '';
            memoryFiles.forEach(file => {
                const div = document.createElement('div');
                div.className = `memory-item ${file === activeFile ? 'active' : ''}`;
                div.setAttribute('data-file', file);
                div.onmousedown = function() { startPress(this); };
                div.onmouseup = function() { endPress(this); };
                div.onmouseleave = function() { cancelPress(this); };
                div.ontouchstart = function() { startPress(this); };
                div.ontouchend = function() { endPress(this); };
                div.ontouchcancel = function() { cancelPress(this); };
                div.innerHTML = `<span>💾</span><span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${file}</span>`;
                container.appendChild(div);
            });
        }

        async function submitNewJson() {
            const userName = document.getElementById('new-username-input').value.trim() || 'user';
            closeModalDirect('newFileModal');
            document.getElementById('new-username-input').value = '';

            const response = await fetch('/create_new_json', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_name: userName })
            });
            const data = await response.json();
            if (data.notice) appendMessage(data.notice, 'ai', true);

            if (data.memory_files) {
                currentSelectedMemory = data.current_memory;
                document.getElementById('setting-active-mem').innerText = data.current_memory;
                renderMemoryList(data.memory_files, data.current_memory);
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    valid_mems = get_valid_memory_files()
    return render_template_string(
        HTML_TEMPLATE,
        model_name=current_model_name,
        notice=startup_notice,
        selected_val=selected_model_val,
        memory_files=valid_mems,
        current_memory=selected_memory_file,
    )

@app.route("/switch_model", methods=["POST"])
def switch_model():
    try:
        data = request.json or {}
        model_type = data.get("model", "v3.6")
        target_mem = data.get("memory", None)
        load_ai_engine(model_type, target_memory=target_mem)
        return jsonify(
            {
                "status": "success",
                "model_name": current_model_name,
                "notice": startup_notice,
                "selected_val": selected_model_val,
                "current_memory": selected_memory_file,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "notice": str(e)})

@app.route("/switch_memory", methods=["POST"])
def switch_memory():
    try:
        data = request.json or {}
        target_mem = data.get("memory_file", "")
        model_type = data.get("model", "v3.6")

        if target_mem and os.path.exists(target_mem):
            load_ai_engine(model_type, target_memory=target_mem)
            return jsonify(
                {
                    "status": "success",
                    "notice": f"Switched active memory to: {target_mem}",
                    "current_memory": selected_memory_file,
                }
            )
        return jsonify({"status": "error", "notice": "File not found!"})
    except Exception as e:
        return jsonify({"status": "error", "notice": str(e)})

@app.route("/delete_memory", methods=["POST"])
def delete_memory():
    global selected_memory_file
    try:
        data = request.json or {}
        target_mem = data.get("memory_file", "")
        model_type = data.get("model", "v3.6")

        if not target_mem or not os.path.exists(target_mem):
            return jsonify({"status": "error", "notice": "Memory file not found!"})

        os.remove(target_mem)

        valid_files = get_valid_memory_files()
        next_mem = valid_files[0] if valid_files else None
        load_ai_engine(model_type, target_memory=next_mem)

        return jsonify(
            {
                "status": "success",
                "notice": f"🗑️ Deleted '{target_mem}' successfully.",
                "memory_files": valid_files,
                "current_memory": selected_memory_file,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "notice": f"Error deleting file: {str(e)}"})

@app.route("/create_new_json", methods=["POST"])
def create_new_json():
    global active_ai, startup_notice, current_model_name, selected_model_val, selected_memory_file
    try:
        import v5_6_AI_engine as engine_module

        data = request.json or {}
        custom_name = data.get("user_name", "user").strip().lower()
        if not custom_name:
            custom_name = "user"

        random_id = random.randint(1000, 9999)
        new_file_name = f"ai_memory_{custom_name}_{random_id}.json"

        active_ai = engine_module.MainAIEngine(user_name=custom_name)
        active_ai.memory_file = new_file_name
        active_ai.memory_db = []
        active_ai.save_memory()

        all_files = glob.glob("ai_memory_*.json")
        for f in all_files:
            if os.path.exists(f) and os.path.getsize(f) < 50:
                try:
                    os.remove(f)
                except Exception:
                    pass

        valid_files = get_valid_memory_files()

        if valid_files:
            best_file = valid_files[0]
            filename_only = os.path.basename(best_file).replace(".json", "")
            parts = filename_only.split("_")
            extracted_name = (
                parts[2]
                if (
                    len(parts) >= 3
                    and parts[0] == "ai"
                    and parts[1] == "memory"
                )
                else custom_name
            )

            active_ai = engine_module.MainAIEngine(user_name=extracted_name)
            active_ai.memory_file = best_file
            active_ai.load_memory()
            selected_memory_file = best_file
            startup_notice = f"Khali file delete. Memory loaded: {best_file}"
        else:
            selected_memory_file = new_file_name
            startup_notice = f"Nayi file load ho gayi: {new_file_name}"

        return jsonify(
            {
                "status": "success",
                "notice": startup_notice,
                "model_name": current_model_name,
                "memory_files": get_valid_memory_files(),
                "current_memory": selected_memory_file,
            }
        )
    except Exception as e:
        return jsonify(
            {"status": "error", "notice": f"Error creating JSON: {str(e)}"}
        )

# --- UPDATED OCR ROUTE (PRESERVES TABLE LINES & MULTI-TYPE CONTEXT) ---
@app.route("/upload_image", methods=["POST"])
def upload_image():
    global active_ai
    try:
        if "file" not in request.files:
            return jsonify({"status": "error", "reply": "No file uploaded."})

        file = request.files["file"]
        user_query = request.form.get("user_query", "").strip() or request.form.get("prompt", "").strip()

        if file.filename == "":
            return jsonify({"status": "error", "reply": "No file selected."})

        extracted_text = ""
        try:
            image_bytes = file.read()
            img = Image.open(io.BytesIO(image_bytes))

            gray_img = img.convert("L")
            enhancer = ImageEnhance.Contrast(gray_img)
            enhanced_img = enhancer.enhance(2.0)

            if OCR_AVAILABLE:
                # PSM 11 for proper table line extraction
                raw_text = pytesseract.image_to_string(enhanced_img, config=r"--oem 3 --psm 11").strip()
                clean_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
                extracted_text = "\n".join(clean_lines)

        except Exception as ocr_err:
            extracted_text = ""

        filename = file.filename

        # RAM Context Sync with Timestamp for latest file priority
        if active_ai and hasattr(active_ai, "memory_db"):
            doc_entry = {
                "tag": "image_context",
                "patterns": [f"image {filename.lower()}", "photo", "pic", "screenshot", "photo","ise ma kya hai","isame kya hai", "kya hai","iske baare mein"],
                "responses": [extracted_text[:2000]],
                "full_text": extracted_text,
                "source": filename,
                "timestamp": datetime.now().timestamp()
            }
            active_ai.memory_db.append(doc_entry)

        if user_query:
            if active_ai and hasattr(active_ai, "respond"):
                reply_msg = active_ai.respond(user_query)
            else:
                reply_msg = f"Image read ho gayi. Question: {user_query}"
            return jsonify({"status": "success", "reply": reply_msg})

        reply_msg = f"Bhai tune ye **{filename}** image bheji hai, iska kya karoon? Iske baare mein kuch poochhna hai ya decode karoon?"
        return jsonify({"status": "success", "reply": reply_msg})

    except Exception as e:
        return jsonify({"status": "error", "reply": f"Image Processing Error: {str(e)}"})

# --- UPDATED PDF ROUTE (TIMESTAMPS FOR LATEST FILE PRIORITY) ---
@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    global active_ai
    try:
        if PyPDF2 is None:
            return jsonify({"status": "error", "reply": "⚠️ PyPDF2 library environment me installed nahi hai!"})

        if "file" not in request.files:
            return jsonify({"status": "error", "reply": "No file part in request."})

        file = request.files["file"]
        user_query = request.form.get("user_query", "").strip() or request.form.get("prompt", "").strip()

        if file.filename == "":
            return jsonify({"status": "error", "reply": "No file selected."})

        if file and file.filename.lower().endswith(".pdf"):
            pdf_bytes = io.BytesIO(file.read())
            reader = PyPDF2.PdfReader(pdf_bytes)
            
            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"

            extracted_text = extracted_text.strip()

            if active_ai and hasattr(active_ai, 'memory_db'):
                doc_entry = {
                    "tag": "pdf_context",
                    "patterns": [f"pdf {file.filename.lower()}", "pdf summary", "document","pdf summary", "document","ise ma kya hai","isame kya hai", "kya hai", "iske baare mein"],
                    "responses": [extracted_text[:2000]],
                    "full_text": extracted_text,
                    "source": file.filename,
                    "timestamp": datetime.now().timestamp()
                }
                active_ai.memory_db.append(doc_entry)

            if user_query:
                if active_ai and hasattr(active_ai, "respond"):
                    reply_msg = active_ai.respond(user_query)
                else:
                    reply_msg = f"PDF process ho gaya. Question: {user_query}"
                return jsonify({"status": "success", "reply": reply_msg})

            reply_msg = f"Bhai tune ye **{file.filename}** PDF bheja hai, iska kya karoon? Is baare mein kuch poochhna hai?"
            return jsonify({"status": "success", "reply": reply_msg})

        return jsonify({"status": "error", "reply": "Keval .pdf files supported hain!"})
    except Exception as e:
        return jsonify({"status": "error", "reply": f"PDF processing error: {str(e)}"})

@app.route("/chat", methods=["POST"])
def chat():
    global active_ai
    try:
        data = request.json or {}
        user_msg = data.get("message", "").strip()

        if not user_msg:
            return jsonify({"reply": "Kuch likho toh sahi, bro!"})

        if active_ai and hasattr(active_ai, 'respond'):
            try:
                reply = active_ai.respond(user_msg)
                if reply:
                    return jsonify({"reply": reply})
            except Exception as eng_err:
                print(f"Engine Error: {eng_err}")

        reply = f"Aapne kaha: '{user_msg}'. Direct processing active!"
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Server Glitch Handled Safely: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
