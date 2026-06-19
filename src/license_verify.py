import hashlib, hmac, struct, time, os, sys

_SECRET_SEED = b"SeedCopy2026Secret!@#"
_SECRET_SALT = b"SeedCopySalt2026_##"
_HMAC_SALT_1 = hashlib.sha256(b'enc_v2_sc' + _SECRET_SEED).digest()[:16]
_HMAC_SALT_2 = hashlib.sha256(b'auth_v2_sc' + _SECRET_SEED).digest()[:16]
CROCKFORD = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
_B32_REV = {c: i for i, c in enumerate(CROCKFORD)}

def _derive_keys():
    master = hashlib.pbkdf2_hmac('sha256', _SECRET_SEED, _SECRET_SALT, 200_000, dklen=64)
    enc_key = hmac.new(master[:32], _HMAC_SALT_1, 'sha256').digest()
    auth_key = hmac.new(master[32:], _HMAC_SALT_2, 'sha256').digest()
    return enc_key, auth_key

def _hmac_ctr(data, key, nonce):
    result = bytearray()
    for i in range(0, len(data), 32):
        counter = struct.pack('>QQ', nonce, i // 32)
        ks = hmac.new(key, counter, 'sha256').digest()
        for a, b in zip(data[i:i + 32], ks):
            result.append(a ^ b)
    return bytes(result)

def _b32_decode(s):
    s = s.upper().replace('-', '').replace(' ', '').lstrip('﻿')
    if s.startswith('SCP'): s = s[3:]
    # Strip leading zeros added by keygen padding (23 bytes = 37 base32 chars)
    # Only strip pad zeros, never strip natural base32 digits
    EXPECTED = 37
    while len(s) > EXPECTED and s.startswith('0'):
        s = s[1:]
    bits = bit_len = 0; result = []
    for c in s:
        if c not in _B32_REV: raise ValueError(f'Invalid: {c}')
        bits = (bits << 5) | _B32_REV[c]; bit_len += 5
        while bit_len >= 8: bit_len -= 8; result.append((bits >> bit_len) & 0xFF)
    return bytes(result)

def _customer_id(name):
    return struct.unpack('>H', hashlib.sha256(name.encode()).digest()[:2])[0]

def _find_license_file():
    if getattr(sys, 'frozen', False):
        p = os.path.join(os.path.dirname(sys.executable), 'license.key')
        if os.path.isfile(p): return p
    for d in [os.getcwd(), os.path.dirname(os.path.abspath(__file__))]:
        p = os.path.join(d, 'license.key')
        if os.path.isfile(p): return p
    return None

PREFIX = 'SCP'

def _try_decode_key(key_str):
    """Try to decode and validate a single key. Returns dict or None."""
    try: combined = _b32_decode(key_str)
    except: return None
    if len(combined) != 23: return None
    nonce, ciphertext, sig = struct.unpack('>H', combined[:2])[0], combined[2:17], combined[17:23]
    _, auth_key = _derive_keys()
    if not hmac.compare_digest(sig, hmac.new(auth_key, b'\x01' + combined[:17], 'sha256').digest()[:6]):
        return None
    enc_key, _ = _derive_keys()
    payload = _hmac_ctr(ciphertext, enc_key, nonce)
    if len(payload) != 15: return None
    version, expire_ts, cid, _ = struct.unpack('>BIH8s', payload)
    now = int(time.time())
    expire_str = 'Permanent' if expire_ts >= 0xFFFFFF00 else time.strftime('%Y-%m-%d', time.localtime(expire_ts))
    remaining_sec = max(0, expire_ts - now) if expire_ts < 0xFFFFFF00 else -1
    remaining_days = remaining_sec // 86400 if remaining_sec >= 0 else -1
    return {'expire_str': expire_str, 'remaining_days': remaining_days,
            'remaining_sec': remaining_sec, 'cid': cid}

def get_license_info():
    path = _find_license_file()
    if not path: return {'status': 'no_license', 'message': '未找到 license.key'}
    try:
        with open(path, 'r', encoding='utf-8-sig') as f: content = f.read().strip()
    except: return {'status': 'invalid', 'message': '无法读取 license.key'}
    if not content: return {'status': 'invalid', 'message': 'license.key 为空'}
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    # Scan all lines for a key with our prefix, pair with next line as customer
    for i, line in enumerate(lines):
        if line.startswith(PREFIX + '-'):
            key_str = line
            customer_str = lines[i + 1] if i + 1 < len(lines) and not lines[i + 1].startswith(PREFIX + '-') else ''
            result = _try_decode_key(key_str)
            if result is None: continue
            name_ok = not customer_str or _customer_id(customer_str) == result['cid']
            if not name_ok: continue
            return {'status': 'valid', 'customer': customer_str,
                    'expire_str': result['expire_str'],
                    'remaining_days': result['remaining_days'],
                    'name_ok': True,
                    'expired': result['remaining_sec'] == 0 and result['remaining_sec'] >= 0}
    # No valid key found for this tool
    return {'status': 'invalid', 'message': f'未找到 {PREFIX} 许可（license.key 中可能只有其他工具的密钥）'}

def check_license():
    info = get_license_info(); s = info.get('status', 'invalid')
    if s == 'no_license': return False, '未找到许可文件\n\n请将 license.key 放在程序目录'
    if s == 'invalid': return False, f"许可无效: {info.get('message', '')}"
    if info.get('remaining_days', 0) >= 0 and info.get('expired', False):
        return False, f"许可已到期 ({info['expire_str']})\n\n请联系客服续期"
    if not info.get('name_ok', True): return False, '客户名不匹配'
    return True, ''
