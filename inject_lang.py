import sys, re
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'D:\loopforge'

LANG_MAP = {
    'index.html': 'ko',
    'id.html': 'id',
    'ja.html': 'ja',
    'th.html': 'th',
    'vi.html': 'vi',
}

CSS = """
/* LANG-SWITCHER-START */
.lang-switcher{position:relative;margin-left:1rem;}
.lang-btn{display:flex;align-items:center;gap:.4rem;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);color:var(--text);padding:.38rem .9rem;border-radius:6px;font-size:.82rem;font-weight:600;cursor:pointer;transition:.2s;white-space:nowrap;}
.lang-btn:hover{background:rgba(255,255,255,.1);}
.lang-btn .chevron{font-size:.6rem;color:var(--muted);transition:transform .2s;margin-left:.2rem;}
.lang-switcher.open .chevron{transform:rotate(180deg);}
.lang-dropdown{display:none;position:absolute;top:calc(100% + 8px);right:0;background:#1a1a1a;border:1px solid rgba(255,255,255,.12);border-radius:10px;padding:.4rem;min-width:160px;box-shadow:0 16px 40px rgba(0,0,0,.5);z-index:999;}
.lang-switcher.open .lang-dropdown{display:block;animation:fadeDown .15s ease;}
@keyframes fadeDown{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}
.lang-option{display:flex;align-items:center;gap:.7rem;padding:.5rem .8rem;border-radius:7px;cursor:pointer;transition:.15s;text-decoration:none;color:var(--text);font-size:.85rem;}
.lang-option:hover{background:rgba(255,255,255,.07);}
.lang-option.active{background:rgba(0,229,160,.1);color:var(--accent);}
.lang-option .lang-native{font-size:.75rem;color:var(--muted);margin-left:auto;}
@media(max-width:768px){.lang-btn .lang-label{display:none;}}
/* LANG-SWITCHER-END */
"""

HTML = """<div class="lang-switcher" id="langSwitcher">
<button class="lang-btn" id="langBtn" aria-expanded="false">
<span id="currentFlag">&#127472;&#127479;</span>
<span class="lang-label" id="currentLangLabel">&#54620;&#44397;&#50612;</span>
<span class="chevron">&#9660;</span>
</button>
<div class="lang-dropdown">
<a href="/" class="lang-option" data-lang="ko"><span>&#127472;&#127479;</span><span>&#54620;&#44397;&#50612;</span><span class="lang-native">KR</span></a>
<a href="/id.html" class="lang-option" data-lang="id"><span>&#127470;&#127465;</span><span>Indonesia</span><span class="lang-native">ID</span></a>
<a href="/ja.html" class="lang-option" data-lang="ja"><span>&#127471;&#127477;</span><span>&#26085;&#26412;&#35486;</span><span class="lang-native">JA</span></a>
<a href="/th.html" class="lang-option" data-lang="th"><span>&#127481;&#127469;</span><span>&#3616;&#3634;&#3625;&#3634;&#3652;&#3607;&#3618;</span><span class="lang-native">TH</span></a>
<a href="/vi.html" class="lang-option" data-lang="vi"><span>&#127483;&#127475;</span><span>Ti&#7871;ng Vi&#7879;t</span><span class="lang-native">VI</span></a>
</div></div>"""

JS_TPL = """<script>
(function(){{
var C='{lang}';
var L={{ko:{{f:'\\u1f1f0\\u1f1f7',l:'\\ud55c\\uad6d\\uc5b4',u:'/'}},id:{{f:'\\u1f1ee\\u1f1e9',l:'Indonesia',u:'/id.html'}},ja:{{f:'\\u1f1ef\\u1f1f5',l:'\\u65e5\\u672c\\u8a9e',u:'/ja.html'}},th:{{f:'\\u1f1f9\\u1f1ed',l:'\\u0e20\\u0e32\\u0e29\\u0e32\\u0e44\\u0e17\\u0e22',u:'/th.html'}},vi:{{f:'\\u1f1fb\\u1f1f3',l:'Ti\\u1ebfng Vi\\u1ec7t',u:'/vi.html'}}}};
var cf=document.getElementById('currentFlag'),cl=document.getElementById('currentLangLabel');
if(cf&&L[C]){{cf.textContent=L[C].f;cl.textContent=L[C].l;}}
document.querySelectorAll('.lang-option').forEach(function(e){{e.classList.toggle('active',e.getAttribute('data-lang')===C);}});
var sw=document.getElementById('langSwitcher'),btn=document.getElementById('langBtn');
if(btn){{btn.addEventListener('click',function(e){{e.stopPropagation();var o=sw.classList.toggle('open');btn.setAttribute('aria-expanded',o);}});}}
document.addEventListener('click',function(){{if(sw)sw.classList.remove('open');}});
document.querySelectorAll('.lang-option').forEach(function(e){{e.addEventListener('click',function(){{localStorage.setItem('lf_lang',e.getAttribute('data-lang'));}});}});
var s=localStorage.getItem('lf_lang');
if(!s){{var b=(navigator.language||'ko').split('-')[0];var sp=['ko','id','ja','th','vi'];if(sp.indexOf(b)!==-1&&b!==C){{localStorage.setItem('lf_lang',b);window.location.href=L[b].u;}}}}
}})();
</script>"""

import os
for fname, lang in LANG_MAP.items():
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        print(f'SKIP (없음): {fname}')
        continue
    with open(path, encoding='utf-8') as f:
        html = f.read()
    if 'lang-switcher' in html:
        print(f'SKIP (이미삽입): {fname}')
        continue
    # CSS 삽입
    html = html.replace('</style>', CSS + '</style>', 1)
    # HTML 삽입 — nav-cta 앞
    html = re.sub(r'(<a[^>]+class="[^"]*nav-cta[^"]*")', HTML + r'\1', html, count=1)
    # JS 삽입
    js = JS_TPL.format(lang=lang)
    html = html.replace('</body>', js + '</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'OK: {fname} (lang={lang})')

print('완료!')