import sys, re, os
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'D:\loopforge'

LANG_MAP = {
    'index.html': 'ko',
    'id.html': 'id',
    'ja.html': 'ja',
    'th.html': 'th',
    'vi.html': 'vi',
}

# 국기 이모지를 직접 UTF-8 문자열로 사용 (HTML 엔티티 X)
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

# 이모지를 JS 문자열로만 처리 — HTML에는 텍스트 placeholder만
HTML = """<div class="lang-switcher" id="langSwitcher">
<button class="lang-btn" id="langBtn" aria-expanded="false">
<span id="currentFlag" style="font-size:1.1rem"></span>
<span class="lang-label" id="currentLangLabel"></span>
<span class="chevron">&#9660;</span>
</button>
<div class="lang-dropdown">
<a href="/" class="lang-option" data-lang="ko"><span class="lf">&#127472;&#127479;</span><span>\ud55c\uad6d\uc5b4</span><span class="lang-native">KR</span></a>
<a href="/id.html" class="lang-option" data-lang="id"><span class="lf">&#127470;&#127465;</span><span>Indonesia</span><span class="lang-native">ID</span></a>
<a href="/ja.html" class="lang-option" data-lang="ja"><span class="lf">&#127471;&#127477;</span><span>\u65e5\u672c\u8a9e</span><span class="lang-native">JA</span></a>
<a href="/th.html" class="lang-option" data-lang="th"><span class="lf">&#127481;&#127469;</span><span>\u0e20\u0e32\u0e29\u0e32\u0e44\u0e17\u0e22</span><span class="lang-native">TH</span></a>
<a href="/vi.html" class="lang-option" data-lang="vi"><span class="lf">&#127483;&#127475;</span><span>Ti\u1ebfng Vi\u1ec7t</span><span class="lang-native">VI</span></a>
</div></div>"""

# JS: 이모지는 \uD83C\uDDF0 서로게이트 페어 방식으로 처리
JS_TPL = r"""<script>
(function(){
var C='__LANG__';
var KR='\uD83C\uDDF0\uD83C\uDDF7';
var ID='\uD83C\uDDEE\uD83C\uDDE9';
var JA='\uD83C\uDDEF\uD83C\uDDF5';
var TH='\uD83C\uDDF9\uD83C\uDDED';
var VI='\uD83C\uDDFB\uD83C\uDDF3';
var L={
  ko:{f:KR,l:'\uD55C\uAD6D\uC5B4',u:'/'},
  id:{f:ID,l:'Indonesia',u:'/id.html'},
  ja:{f:JA,l:'\u65E5\u672C\u8A9E',u:'/ja.html'},
  th:{f:TH,l:'\u0E20\u0E32\u0E29\u0E32\u0E44\u0E17\u0E22',u:'/th.html'},
  vi:{f:VI,l:'Ti\u1EBFng Vi\u1EC7t',u:'/vi.html'}
};
var cf=document.getElementById('currentFlag');
var cl=document.getElementById('currentLangLabel');
if(cf&&L[C]){cf.textContent=L[C].f;cl.textContent=L[C].l;}
document.querySelectorAll('.lang-option').forEach(function(e){
  e.classList.toggle('active',e.getAttribute('data-lang')===C);
});
var sw=document.getElementById('langSwitcher');
var btn=document.getElementById('langBtn');
if(btn){btn.addEventListener('click',function(e){
  e.stopPropagation();
  var o=sw.classList.toggle('open');
  btn.setAttribute('aria-expanded',o);
});}
document.addEventListener('click',function(){if(sw)sw.classList.remove('open');});
document.querySelectorAll('.lang-option').forEach(function(e){
  e.addEventListener('click',function(){localStorage.setItem('lf_lang',e.getAttribute('data-lang'));});
});
var s=localStorage.getItem('lf_lang');
if(!s){
  var b=(navigator.language||'ko').split('-')[0];
  var sp=['ko','id','ja','th','vi'];
  if(sp.indexOf(b)!==-1&&b!==C){localStorage.setItem('lf_lang',b);window.location.href=L[b].u;}
}
})();
</script>"""

for fname, lang in LANG_MAP.items():
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        print(f'SKIP (없음): {fname}')
        continue

    # 백업에서 원본 복원
    import glob
    backups = sorted(glob.glob(os.path.join(BASE, fname.replace('.html', '_backup_*.html'))))
    if backups:
        latest_backup = backups[-1]
        with open(latest_backup, encoding='utf-8') as f:
            html = f.read()
        print(f'복원: {os.path.basename(latest_backup)} -> {fname}')
    else:
        with open(path, encoding='utf-8') as f:
            html = f.read()
        # 이미 삽입된 거 제거
        html = re.sub(r'/\* LANG-SWITCHER-START \*/.+?/\* LANG-SWITCHER-END \*/', '', html, flags=re.DOTALL)
        html = re.sub(r'<div class="lang-switcher"[^>]*>.*?</div>\s*</div>', '', html, flags=re.DOTALL)
        html = re.sub(r'<script>\s*\(function\(\)\{[\s\S]*?var C=\'[a-z]{2}\'[\s\S]*?\}\)\(\);\s*</script>', '', html)

    # CSS 삽입
    html = html.replace('</style>', CSS + '</style>', 1)
    # HTML 삽입 — nav-cta 앞
    html = re.sub(r'(<a[^>]+class="[^"]*nav-cta[^"]*")', HTML + r'\1', html, count=1)
    # JS 삽입
    js = JS_TPL.replace('__LANG__', lang)
    html = html.replace('</body>', js + '</body>', 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'OK: {fname} (lang={lang})')

print('완료!')
