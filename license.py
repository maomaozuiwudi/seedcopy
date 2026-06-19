"""Radshop三件套 — 试用许可模块（3天试用期）"""
import os, sys, json, hashlib, datetime

def _get_key_path():
    """获取trial.key路径（EXE同目录或用户目录）"""
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        path = os.path.join(exe_dir, 'trial.key')
        return path
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trial.key')

def check_license():
    """检查试用状态。返回 (valid, message, remaining_days)"""
    key_path = _get_key_path()
    today = datetime.date.today()

    if not os.path.exists(key_path):
        # 首次运行，创建试用记录
        data = {'start': today.isoformat(), 'machine': hashlib.sha256(os.environ.get('COMPUTERNAME', 'unknown').encode()).hexdigest()[:12]}
        try:
            with open(key_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except:
            return False, '无法创建试用文件，请以管理员身份运行', 0
        remaining = 3
        return True, f'试用已激活 — 剩余 {remaining} 天', remaining

    try:
        with open(key_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        start = datetime.date.fromisoformat(data['start'])
        elapsed = (today - start).days
        remaining = max(0, 3 - elapsed)
        if remaining <= 0:
            return False, '试用已到期，请联系客服获取正式许可', 0
        return True, f'试用中 — 剩余 {remaining} 天', remaining
    except:
        return False, '试用文件损坏，请删除 trial.key 后重试', 0

def get_license_info():
    """获取许可信息用于显示"""
    valid, msg, remaining = check_license()
    return {'valid': valid, 'message': msg, 'remaining_days': remaining}
