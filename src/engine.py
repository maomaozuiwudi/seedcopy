"""SeedCopy engine — Chinese 种草 → localized English"""
import json, os, sys, re, random

def _load_rules():
    base = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    with open(os.path.join(base, 'rules.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

MARKET_CONFIG = {
    'US': {'name': 'US', 'style': 'expressive'},
    'UK': {'name': 'UK', 'style': 'understated'},
    'AU': {'name': 'AU', 'style': 'casual'},
    'CA': {'name': 'CA', 'style': 'polite'},
    'SG': {'name': 'SG', 'style': 'enthusiastic'},
    'MY': {'name': 'MY', 'style': 'warm'},
}

# 基础中文词汇→英文（离线回退用）
_FALLBACK = {
    '这个': 'this', '那个': 'that', '一个': 'a', '包包': 'bag', '质感': 'texture',
    '真的': 'truly', '很好': 'very good', '非常好': 'excellent', '特别': 'especially',
    '完美': 'perfect', '精致': 'refined', '细腻': 'delicate', '柔软': 'soft',
    '舒服': 'comfortable', '漂亮': 'beautiful', '好看': 'good-looking',
    '耐用': 'durable', '实用': 'practical', '方便': 'convenient', '简单': 'simple',
    '干净': 'clean', '自然': 'natural', '独特': 'unique', '优雅': 'elegant',
    '时尚': 'stylish', '设计': 'design', '颜色': 'color', '面料': 'fabric',
    '材质': 'material', '品质': 'quality', '价格': 'price', '效果': 'effect',
    '皮肤': 'skin', '成分': 'ingredients', '味道': 'flavor', '香气': 'scent',
    '空间': 'space', '房间': 'room', '衣服': 'clothing', '裙子': 'dress',
    '裤子': 'pants', '鞋子': 'shoes', '项链': 'necklace', '精华': 'serum',
    '面霜': 'cream', '口红': 'lipstick', '香水': 'fragrance', '制作': 'made',
    '使用': 'using', '适合': 'suits', '搭配': 'pairs with', '提升': 'elevates',
    '显得': 'makes it look', '打造': 'creates', '营造': 'builds', '融入': 'blends',
    '和': 'and', '的': '', '了': '', '在': 'in', '是': 'is', '有': 'has',
    '让': 'makes', '给': 'gives', '带': 'brings', '用': 'with', '买': 'buy',
    '穿': 'wear', '看': 'look at', '说': 'say', '想': 'think', '喜欢': 'love',
    '推荐': 'recommend', '分享': 'share', '感觉': 'feel', '体验': 'experience',
    '很': 'very', '非常': 'very', '最': 'most', '更': 'more', '都': 'all',
    '也': 'also', '还': 'still', '只': 'only', '就': 'just', '才': 'only',
    '不': 'not', '没有': 'no', '可以': 'can', '可能': 'maybe', '需要': 'need',
    '想要': 'want', '值得': 'worth', '开始': 'start', '起来': 'up', '下来': 'down',
    '过来': 'over', '回去': 'back', '进来': 'in', '出去': 'out',
}

def _fallback_translate(text):
    """离线回退：逐词翻译残留中文"""
    if not _has_cn(text):
        return text
    # 替换中文标点
    for cp, ep in [('。', '.'), ('，', ','), ('！', '!'), ('？', '?'), ('；', ';'), ('：', ':'), ('、', ',')]:
        text = text.replace(cp, ep)
    # 最长匹配替换
    items = sorted(_FALLBACK.items(), key=lambda x: -len(x[0]))
    result = text
    for cn, en in items:
        if cn in result:
            result = result.replace(cn, f' {en} ')
    result = re.sub(r'\s{2,}', ' ', result).strip()
    return result

def _has_cn(text):
    return any('一' <= c <= '鿿' for c in text)

def localize(text, market='US', intensity='normal', use_deepl=False):
    rules = _load_rules()

    body = text
    deepl_used = False

    if use_deepl:
        try:
            from deepl import translate
            # 先做模式替换，把无法直译的中文换成英文
            prepped = _pattern_replace(text, market, rules)
            # 再翻译残留中文
            translated = translate(prepped, 'en')
            if translated and not _has_cn(translated):
                body = translated
                body = _enhance(body, market, rules)
                body = _apply_intensity(body, intensity, market)
                deepl_used = True
        except Exception:
            pass

    if not deepl_used:
        body = _pattern_replace(text, market, rules)
        # 无翻译时也要尽量消除中文：用规则回退翻译
        body = _fallback_translate(body)

    title = _gen_title(text, market)
    opening = _gen_opening(market)
    closing = _gen_closing(market)
    cta = _gen_cta(market, intensity)
    tips = ['Translation: Bing/Youdao' if deepl_used else 'Offline mode - patterns only']

    back_cn = ''
    if deepl_used:
        try:
            from deepl import translate
            bc = translate(body, 'zh')
            if bc and bc != body:
                back_cn = bc
        except Exception:
            pass

    return {
        'market': market, 'title': title, 'opening': opening,
        'body': body, 'closing': closing, 'cta': cta,
        'back_translation': back_cn, 'tips': tips, 'deepl_used': deepl_used,
    }

def _pattern_replace(text, market, rules):
    """Replace Chinese patterns with localized English"""
    items = []
    for cat in ['emotional_expressions', 'quality_claims', 'social_proof',
                 'action_prompts', 'cultural_references',
                 'fashion_apparel', 'beauty_skincare', 'home_lifestyle',
                 'food_drink', 'jewelry_accessories']:
        for item in rules.get(cat, []):
            if item['cn'] in text:
                loc = item.get('localized', {}).get(market) or item.get('localized', {}).get('US')
                if not loc and item.get('explanation'):
                    loc = item['explanation'].get(market) or item['explanation'].get('US')
                if loc:
                    items.append((item['cn'], loc, len(item['cn'])))

    # Longest match first
    items.sort(key=lambda x: -x[2])
    result = text
    seen = set()
    for cn, loc, _ in items:
        if cn not in seen:
            result = result.replace(cn, f' {loc} ')
            seen.add(cn)

    return re.sub(r'\s{2,}', ' ', result).strip()

def _enhance(text, market, rules):
    """Enhance MT output with better English"""
    fixes = [
        (r"buy(?:ing)? it (?:blindly|with your eyes closed)", "just grab it. thank me later"),
        (r"can't go wrong buying it", "I was skeptical too, but honestly"),
        (r"you can't go wrong", "you really can't miss with this one"),
    ]
    for pat, rep in fixes:
        text = re.sub(pat, rep, text, flags=re.IGNORECASE)

    boosts = {
        'really amazing': "honestly, I'm impressed",
        'very beautiful': 'actually stopped me mid-scroll',
        'genuine leather': "real leather that smells like a high-end boutique",
        'hand-stitched': "each stitch is so clean you could zoom in and still not find a flaw",
        'handmade': "you can feel the human touch",
        'well made': "built to outlast your obsession with it",
        'warmth of the craftsman': "you can tell the person who made this actually cared",
        'every detail exudes': 'the little details are what got me',
        'worth buying': "one of those rare finds you don't shut up about",
    }
    for plain, better in boosts.items():
        if re.search(re.escape(plain), text, re.IGNORECASE):
            text = re.sub(re.escape(plain), better, text, count=1, flags=re.IGNORECASE)

    text = re.sub(r'\b(really|truly|honestly|seriously|absolutely) (really|truly|honestly|seriously|absolutely) ', r'\1 ', text)
    return text

def _apply_intensity(text, intensity, market):
    if intensity == 'gentle':
        text = re.sub(r'!+', '.', text)
        text = re.sub(r"\bhonestly, I'm impressed\b", 'pretty nice tbh', text)
    elif intensity == 'strong':
        if not text.endswith('!') and not text.endswith('?'):
            text = text.rstrip('.') + '!'
        text = re.sub(r'\bpretty nice\b', 'honestly incredible', text)
        text = re.sub(r"\bI'm impressed\b", "I'm genuinely blown away", text)
    return text

def _gen_title(text, market):
    words = re.findall(r'[一-鿿]{2,4}', text)
    fill = words[0] if words else 'this product'
    templates = {
        'US': ["Why I'm obsessed with {}", "Found: a {} that actually delivers"],
        'UK': ["A rather lovely {} worth your attention"],
        'AU': ["Mate, this {} is the real deal"],
        'SG': ["This {} is a total game-changer"],
        'MY': ["This {} is worth every ringgit"],
    }
    return random.choice(templates.get(market, templates['US'])).format(fill)

def _gen_opening(market):
    return random.choice({
        'US': ["Okay, I need to talk about this.", "Found something that actually lives up to the hype."],
        'UK': ["Right then, let's have a look.", "I've been rather taken with something lately."],
        'AU': ["Alright, gotta share this one.", "Found a ripper. Here's the go."],
    }.get(market, ["Here's something worth sharing."]))

def _gen_closing(market):
    return random.choice({
        'US': ["Trust me on this one.", "10/10. No notes."],
        'UK': ["Rather good, this. Worth a gander."],
        'AU': ["Link's up. Give it a crack."],
    }.get(market, ["Definitely worth checking out."]))

def _gen_cta(market, intensity):
    ctas = {
        'US': {'gentle': ["Link in bio if you want to check it out."],
               'normal': ["Link's up. Trust me on this one."],
               'strong': ["RUN don't walk. Link in bio!"]},
        'UK': {'gentle': ["Have a look if you fancy."],
               'normal': ["Link's there if you're curious."]},
        'AU': {'gentle': ["Link's up if you're keen."],
               'normal': ["Give it a crack — link in bio."]},
        'SG': {'normal': ["Link in bio — grab before OOS!"],
               'strong': ["WHACK ONLY. Link in bio!"]},
        'MY': {'normal': ["Link in bio — faster go get before sold out!"]},
    }
    mkt_ctas = ctas.get(market, ctas['US'])
    picks = mkt_ctas.get(intensity, mkt_ctas.get('normal', ["Check it out."]))
    return random.choice(picks)
