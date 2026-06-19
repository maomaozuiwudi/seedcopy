"""SeedCopy — 种草本地化引擎"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading, os, sys

base = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
sys.path.insert(0, base)
from engine import localize, MARKET_CONFIG

import json, datetime, hashlib
def _get_license():
    key_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else base, 'trial.key')
    today = datetime.date.today()
    if not os.path.exists(key_path):
        data = {'start': today.isoformat(), 'machine': hashlib.sha256(os.environ.get('COMPUTERNAME','').encode()).hexdigest()[:12]}
        try:
            with open(key_path, 'w', encoding='utf-8') as f: json.dump(data, f)
        except: pass
        return True, f'试用已激活 — 剩余 3 天', 3
    try:
        with open(key_path, 'r', encoding='utf-8') as f: data = json.load(f)
        start = datetime.date.fromisoformat(data['start'])
        remaining = max(0, 3 - (today - start).days)
        if remaining <= 0: return False, '试用已到期，请联系客服', 0
        return True, f'试用中 — 剩余 {remaining} 天', remaining
    except: return True, '试用中', 0

C = {
    'bg': '#1a1a2e', 'card': '#16213e', 'accent': '#e94560',
    'accent2': '#ff6b6b', 'text': '#eaeaea', 'text2': '#a0a0b0',
    'text3': '#6c6c80', 'border': '#2a2a4a', 'input_bg': '#0d1b36',
}
FONT = lambda s=11, b=False: ('Microsoft YaHei UI', s, 'bold' if b else 'normal')
FONTE = lambda s=11: ('Segoe UI', s)
MARKETS = ['US', 'UK', 'AU', 'CA', 'SG', 'MY']

class App:
    def __init__(self, root):
        self.root = root
        self.root.title('SeedCopy — Redshop Content Localizer')
        self.root.geometry('1300x820')
        self.root.minsize(1100, 700)
        self.root.configure(bg=C['bg'])
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self.root, bg=C['card'], height=56)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text='SeedCopy 种草本地化引擎', font=FONT(16, True), fg=C['accent2'],
                 bg=C['card']).pack(side=tk.LEFT, padx=20, pady=10)
        tk.Label(header, text='中文种草文案 → 多市场本地化英文 | Redshop卖家专用',
                 font=FONT(9), fg=C['text3'], bg=C['card']).pack(side=tk.LEFT, padx=8)

        main_area = tk.Frame(self.root, bg=C['bg'])
        main_area.pack(fill=tk.BOTH, expand=True, padx=15, pady=(10, 0))

        left_panel = tk.Frame(main_area, bg=C['card'], width=420)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        left_panel.pack_propagate(False)

        top_section = tk.Frame(left_panel, bg=C['card'])
        top_section.pack(fill=tk.X, padx=15, pady=(15, 0))

        tk.Label(top_section, text='中文种草文案', font=FONT(13, True),
                 fg=C['text'], bg=C['card']).pack(anchor='w')

        tk.Label(top_section, text='目标市场', font=FONT(9, True),
                 fg=C['text2'], bg=C['card']).pack(anchor='w', pady=(8, 3))

        market_row = tk.Frame(top_section, bg=C['card'])
        market_row.pack(fill=tk.X)
        self.market_vars = {}
        for mkt in MARKETS:
            var = tk.BooleanVar(value=(mkt in ['US']))
            self.market_vars[mkt] = var
            tk.Checkbutton(market_row, text=MARKET_CONFIG[mkt]['name'], variable=var,
                           font=FONT(9), fg=C['text2'], bg=C['card'],
                           selectcolor=C['card'], activebackground=C['card'],
                           activeforeground=C['accent2'], relief='flat'
                           ).pack(side=tk.LEFT, padx=(0, 6))

        action_row = tk.Frame(top_section, bg=C['card'])
        action_row.pack(fill=tk.X, pady=(8, 5))

        self.intensity_var = tk.StringVar(value='normal')
        tk.Label(action_row, text='种草力度', font=FONT(9, True),
                 fg=C['text2'], bg=C['card']).pack(side=tk.LEFT)
        for val, label in [('gentle', '轻'), ('normal', '标准'), ('strong', '强')]:
            tk.Radiobutton(action_row, text=label, variable=self.intensity_var, value=val,
                           font=FONT(9), fg=C['text2'], bg=C['card'],
                           selectcolor=C['card'], activebackground=C['card'],
                           activeforeground=C['accent2'], relief='flat',
                           indicatoron=0, padx=6, pady=2).pack(side=tk.LEFT, padx=(4, 0))

        self.deepl_var = tk.BooleanVar(value=True)
        tk.Checkbutton(action_row, text='翻译', variable=self.deepl_var,
                       font=FONT(9), fg='#0f9b58', bg=C['card'],
                       selectcolor=C['card'], activebackground=C['card'],
                       relief='flat').pack(side=tk.RIGHT, padx=(8, 0))

        self.btn = tk.Button(action_row, text='生 成', font=FONT(11, True),
                             bg=C['accent'], fg='white', relief='flat',
                             cursor='hand2', activebackground=C['accent2'],
                             padx=20, pady=6, command=self._go)
        self.btn.pack(side=tk.RIGHT)

        sep = tk.Frame(top_section, bg=C['border'], height=1)
        sep.pack(fill=tk.X, pady=(8, 0))

        input_frame = tk.Frame(left_panel, bg=C['input_bg'], relief='flat', borderwidth=1)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD,
            font=FONT(11), relief='flat', borderwidth=0,
            bg=C['input_bg'], fg=C['text'], insertbackground=C['accent2'],
            padx=12, pady=12)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        self.input_text.insert('1.0', '这个包包的质感真的绝了！真皮手工缝制，每一个细节都透着匠人的温度。\n'
            '背出去回头率超高，姐妹们都问我在哪买的。闭眼入不踩雷！\n\n'
            '新中式设计，宋代美学配色，非遗级别的手艺。越看越有味道，高级感拉满。')

        self.status_inline = tk.Label(left_panel, text='', font=FONT(9),
                                       fg=C['text3'], bg=C['card'])
        self.status_inline.pack(padx=15, pady=(0, 8))

        right_panel = tk.Frame(main_area, bg=C['bg'])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        info_bar = tk.Frame(right_panel, bg=C['card'], height=36)
        info_bar.pack(fill=tk.X)
        info_bar.pack_propagate(False)
        self.info_label = tk.Label(info_bar, text='就绪 — 粘贴文案后点击「生成」',
                                    font=FONT(10), fg=C['text2'], bg=C['card'])
        self.info_label.pack(side=tk.LEFT, padx=15)

        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.tabs = {}
        for mkt in MARKETS:
            tab = tk.Frame(self.notebook, bg=C['card'])
            self.notebook.add(tab, text=MARKET_CONFIG[mkt]['name'])
            tw = scrolledtext.ScrolledText(tab, wrap=tk.WORD, font=FONTE(11),
                                           relief='flat', borderwidth=0,
                                           bg=C['input_bg'], fg=C['text'],
                                           padx=15, pady=15)
            tw.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            tw.insert('1.0', f'（{MARKET_CONFIG[mkt]["name"]} 市场结果将显示在此）')
            self.tabs[mkt] = tw

        lic_ok, lic_msg, _ = _get_license()
        lic_text = lic_msg if lic_ok else f'⚠ {lic_msg}'
        lic_color = '#27ae60' if lic_ok else '#e74c3c'
        self.status_bar = tk.Label(self.root, text=lic_text, font=FONT(9),
                                    fg=lic_color, bg=C['card'],
                                    anchor='w', padx=15, pady=6)
        self.status_bar.pack(fill=tk.X, padx=15, pady=10)

    def _go(self):
        text = self.input_text.get('1.0', 'end-1c').strip()
        if not text:
            messagebox.showwarning('提示', '请先输入中文种草文案')
            return

        selected = [m for m, v in self.market_vars.items() if v.get()]
        if not selected:
            messagebox.showwarning('提示', '请至少选择一个目标市场')
            return

        intensity = self.intensity_var.get()
        use_deepl = self.deepl_var.get()

        self.btn.config(state=tk.DISABLED, text='翻译中...', bg=C['text3'])
        self.status_bar.config(text='正在调用翻译API...')
        self.status_inline.config(text='处理中...')

        for mkt in MARKETS:
            self.tabs[mkt].delete('1.0', tk.END)

        def worker():
            results = {}
            cache_body = cache_title = cache_back = ''
            for i, mkt in enumerate(selected):
                try:
                    if i == 0 and use_deepl:
                        r = localize(text, mkt, intensity, use_deepl=True)
                        cache_body = r.get('body', '')
                        cache_title = r.get('title', '')
                        cache_back = r.get('back_translation', '')
                    elif i > 0 and use_deepl:
                        r = localize(text, mkt, intensity, use_deepl=False)
                        r['body'] = cache_body
                        r['title'] = cache_title
                        r['back_translation'] = cache_back
                        r['deepl_used'] = True
                    else:
                        r = localize(text, mkt, intensity, use_deepl=False)
                    results[mkt] = r
                except Exception as e:
                    results[mkt] = {'error': str(e)}
            self.root.after(0, lambda: self._show(results))

        threading.Thread(target=worker, daemon=True).start()

    def _show(self, results):
        for mkt, r in results.items():
            tw = self.tabs[mkt]
            if 'error' in r:
                tw.insert('1.0', f'Error: {r["error"]}')
                continue
            tw.insert('1.0',
                f"TITLE\n{r['title']}\n\n"
                f"{'─' * 50}\n\n"
                f"HOOK\n{r['opening']}\n\n"
                f"{'─' * 50}\n\n"
                f"BODY\n{r['body']}\n\n"
                f"{'─' * 50}\n\n"
                f"CLOSING\n{r['closing']}\n\n"
                f"{'─' * 50}\n\n"
                f"CTA\n{r['cta']}\n")
            if r.get('back_translation'):
                tw.insert(tk.END,
                    f"\n{'─' * 50}\n"
                    f"BACK-TRANSLATION (seller verification)\n"
                    f"{r['back_translation']}\n")
            if r.get('tips'):
                tw.insert(tk.END, f"\n{'─' * 50}\n提示\n" + '\n'.join(r['tips']))
            if not r.get('deepl_used'):
                tw.insert(tk.END, f"\n{'─' * 50}\n⚠ 翻译API未启用，输出可能残留中文。请确保「翻译」开关已勾选。")

        deepl_label = '开' if self.deepl_var.get() else '关'
        self.info_label.config(text=f'翻译: {deepl_label} | {len(results)} 个市场')
        api_ok = any(r.get('deepl_used') for r in results.values())
        self.status_bar.config(text=f'完成 — {len(results)} 个市场已生成' + (' (API翻译)' if api_ok else ' (离线模式，可能残留中文)'))
        self.status_inline.config(text=f'{len(results)} 个市场完成')
        self.btn.config(state=tk.NORMAL, text='生 成', bg=C['accent'])

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == '__main__':
    main()
