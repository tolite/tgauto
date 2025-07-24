from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-here')

# 配置LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 模拟用户数据库
users = {
    "admin": generate_password_hash("admin123"),
    "support": generate_password_hash("support123")
}

# 用户类
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# 用户加载回调
@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# 模拟数据库路径
DB_PATH = os.environ.get('DB_PATH', 'data/db.json')

def load_db():
    """加载数据库"""
    try:
        if os.path.exists(DB_PATH):
            with open(DB_PATH, 'r') as f:
                return json.load(f)
        return {'users': {}, 'devices': {}, 'messages': [], 'settings': {}}
    except Exception as e:
        print(f"加载数据库失败: {e}")
        return {'users': {}, 'devices': {}, 'messages': [], 'settings': {}}

@app.route('/')
@login_required
def index():
    """首页"""
    db = load_db()
    user_count = len(db.get('users', {}))
    device_count = len(db.get('devices', {}))
    message_count = len(db.get('messages', []))
    
    return render_template('index.html', 
                          user_count=user_count,
                          device_count=device_count,
                          message_count=message_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and check_password_hash(users[username], password):
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/users')
@login_required
def users_page():
    """用户管理页面"""
    db = load_db()
    users_data = db.get('users', {}).values()
    
    # 格式化日期
    for user in users_data:
        if 'joined_at' in user:
            user['joined_at'] = datetime.fromisoformat(user['joined_at']).strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('users.html', users=users_data)

@app.route('/devices')
@login_required
def devices_page():
    """设备管理页面"""
    db = load_db()
    devices_data = db.get('devices', {}).values()
    
    # 格式化日期
    for device in devices_data:
        if 'registered_at' in device:
            device['registered_at'] = datetime.fromisoformat(device['registered_at']).strftime('%Y-%m-%d %H:%M:%S')
        if 'last_upload' in device and device['last_upload']:
            device['last_upload'] = datetime.fromisoformat(device['last_upload']).strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('devices.html', devices=devices_data)

@app.route('/messages')
@login_required
def messages_page():
    """消息记录页面"""
    db = load_db()
    messages = db.get('messages', [])
    
    # 分页处理
    page = request.args.get('page', 1, type=int)
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_messages = messages[start:end]
    
    # 格式化日期
    for msg in paginated_messages:
        if 'timestamp' in msg:
            msg['timestamp'] = datetime.fromisoformat(msg['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    
    total_pages = (len(messages) + per_page - 1) // per_page
    
    return render_template('messages.html', 
                          messages=paginated_messages,
                          page=page,
                          total_pages=total_pages)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_page():
    """设置页面"""
    db = load_db()
    settings = db.get('settings', {})
    
    if request.method == 'POST':
        # 处理设置更新
        new_settings = request.form.to_dict()
        db['settings'] = new_settings
        
        # 保存设置
        try:
            with open(DB_PATH, 'w') as f:
                json.dump(db, f, indent=4)
            return render_template('settings.html', settings=new_settings, success=True)
        except Exception as e:
            return render_template('settings.html', settings=settings, error=str(e))
    
    return render_template('settings.html', settings=settings)

@app.route('/api/users')
@login_required
def api_users():
    """获取用户API"""
    db = load_db()
    return jsonify(list(db.get('users', {}).values()))

@app.route('/api/devices')
@login_required
def api_devices():
    """获取设备API"""
    db = load_db()
    return jsonify(list(db.get('devices', {}).values()))

@app.route('/api/messages')
@login_required
def api_messages():
    """获取消息API"""
    db = load_db()
    return jsonify(db.get('messages', []))

@app.route('/api/send_message', methods=['POST'])
@login_required
def api_send_message():
    """发送消息API"""
    data = request.json
    chat_id = data.get('chat_id')
    text = data.get('text')
    
    if not chat_id or not text:
        return jsonify({'success': False, 'error': '缺少参数'})
    
    # 这里应该实现通过机器人API发送消息的逻辑
    # 为简化示例，我们只返回成功
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)    
