# LoopForge AI 다국어 언어 선택기 자동 삽입 스크립트
# 실행: PowerShell에서 D:\loopforge\inject_lang_switcher.ps1

$BASE = "D:\loopforge"

# ── 언어별 설정
$LANG_MAP = @{
  "index.html" = "ko"
  "id.html"    = "id"
  "ja.html"    = "ja"
  "th.html"    = "th"
  "vi.html"    = "vi"
}

# ── CSS 스니펫 (nav에 추가할 스타일)
$CSS_SNIPPET = @'
/* ── LANG SWITCHER ── */
.lang-switcher{position:relative;margin-left:1rem;}
.lang-btn{display:flex;align-items:center;gap:.4rem;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);color:var(--text);padding:.38rem .9rem;border-radius:6px;font-size:.82rem;font-weight:600;cursor:pointer;transition:.2s;white-space:nowrap;}
.lang-btn:hover{background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.22);}
.lang-btn .flag{font-size:1rem;line-height:1;}
.lang-btn .chevron{font-size:.6rem;color:var(--muted);transition:transform .2s;margin-left:.2rem;}
.lang-switcher.open .chevron{transform:rotate(180deg);}
.lang-dropdown{display:none;position:absolute;top:calc(100% + 8px);right:0;background:#1a1a1a;border:1px solid rgba(255,255,255,.12);border-radius:10px;padding:.4rem;min-width:160px;box-shadow:0 16px 40px rgba(0,0,0,.5);z-index:999;}
.lang-switcher.open .lang-dropdown{display:block;animation:fadeDown .15s ease;}
@keyframes fadeDown{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}
.lang-option{display:flex;align-items:center;gap:.7rem;padding:.5rem .8rem;border-radius:7px;cursor:pointer;transition:.15s;text-decoration:none;color:var(--text);font-size:.85rem;}
.lang-option:hover{background:rgba(255,255,255,.07);}
.lang-option.active{background:rgba(0,229,160,.1);color:var(--accent);}
.lang-option .flag{font-size:1.1rem;}
.lang-option .lang-native{font-size:.75rem;color:var(--muted);margin-left:auto;}
@media(max-width:768px){.lang-btn .lang-label{display:none;}}
/* ── END LANG SWITCHER ── */
'@

# ── HTML 스니펫 (nav-cta 버튼 앞에 삽입)
$HTML_SNIPPET = @'
<div class="lang-switcher" id="langSwitcher">
<button class="lang-btn" id="langBtn" aria-label="언어 선택" aria-expanded="false">
<span class="flag" id="currentFlag">🇰🇷</span>
<span class="lang-label" id="currentLangLabel">한국어</span>
<span class="chevron">▼</span>
</button>
<div class="lang-dropdown" role="menu">
<a href="/" class="lang-option" data-lang="ko" role="menuitem"><span class="flag">🇰🇷</span><span class="lang-name">한국어</span><span class="lang-native">KR</span></a>
<a href="/id.html" class="lang-option" data-lang="id" role="menuitem"><span class="flag">🇮🇩</span><span class="lang-name">Indonesia</span><span class="lang-native">ID</span></a>
<a href="/ja.html" class="lang-option" data-lang="ja" role="menuitem"><span class="flag">🇯🇵</span><span class="lang-name">日本語</span><span class="lang-native">JA</span></a>
<a href="/th.html" class="lang-option" data-lang="th" role="menuitem"><span class="flag">🇹🇭</span><span class="lang-name">ภาษาไทย</span><span class="lang-native">TH</span></a>
<a href="/vi.html" class="lang-option" data-lang="vi" role="menuitem"><span class="flag">🇻🇳</span><span class="lang-name">Tiếng Việt</span><span class="lang-native">VI</span></a>
</div>
</div>
'@

# ── JS 템플릿 (CURRENT_LANG은 파일별로 치환)
$JS_TEMPLATE = @'
<script>
(function(){
var CURRENT_LANG='__LANG__';
var LANGS={ko:{flag:'🇰🇷',label:'한국어',file:'/'},id:{flag:'🇮🇩',label:'Indonesia',file:'/id.html'},ja:{flag:'🇯🇵',label:'日本語',file:'/ja.html'},th:{flag:'🇹🇭',label:'ภาษาไทย',file:'/th.html'},vi:{flag:'🇻🇳',label:'Tiếng Việt',file:'/vi.html'}};
var f=document.getElementById('currentFlag'),l=document.getElementById('currentLangLabel');
if(f&&LANGS[CURRENT_LANG]){f.textContent=LANGS[CURRENT_LANG].flag;l.textContent=LANGS[CURRENT_LANG].label;}
document.querySelectorAll('.lang-option').forEach(function(el){el.classList.toggle('active',el.getAttribute('data-lang')===CURRENT_LANG);});
var sw=document.getElementById('langSwitcher'),btn=document.getElementById('langBtn');
if(btn){btn.addEventListener('click',function(e){e.stopPropagation();var o=sw.classList.toggle('open');btn.setAttribute('aria-expanded',o);});}
document.addEventListener('click',function(){if(sw)sw.classList.remove('open');});
document.querySelectorAll('.lang-option').forEach(function(el){el.addEventListener('click',function(){localStorage.setItem('lf_lang',el.getAttribute('data-lang'));});});
var saved=localStorage.getItem('lf_lang');
if(!saved){var bl=(navigator.language||'ko').split('-')[0];var sp=['ko','id','ja','th','vi'];if(sp.indexOf(bl)!==-1&&bl!==CURRENT_LANG){localStorage.setItem('lf_lang',bl);window.location.href=LANGS[bl].file;}}
})();
</script>
'@

# ── 메인 처리
foreach ($file in $LANG_MAP.Keys) {
    $filePath = Join-Path $BASE $file
    $lang     = $LANG_MAP[$file]

    if (-not (Test-Path $filePath)) {
        Write-Host "⚠ 파일 없음: $file" -ForegroundColor Yellow
        continue
    }

    # 백업
    $backupPath = $filePath -replace '\.html$', "_backup_$(Get-Date -Format 'yyyyMMdd_HHmm').html"
    Copy-Item $filePath $backupPath
    Write-Host "💾 백업: $(Split-Path $backupPath -Leaf)" -ForegroundColor Gray

    # 파일 읽기 (UTF-8)
    $content = [System.IO.File]::ReadAllText($filePath, [System.Text.Encoding]::UTF8)

    # 이미 삽입됐는지 확인
    if ($content -match 'lang-switcher') {
        Write-Host "⏭ 이미 삽입됨, 스킵: $file" -ForegroundColor Cyan
        continue
    }

    # [1] CSS 삽입 — </style> 첫 번째 바로 앞
    $content = $content -replace '(</style>)', "$CSS_SNIPPET`$1"

    # [2] HTML 삽입 — nav-cta 클래스 링크 바로 앞
    $content = $content -replace '(<a[^>]+class="[^"]*nav-cta[^"]*")', "$HTML_SNIPPET`$1"

    # [3] JS 삽입 — </body> 바로 앞
    $JS = $JS_TEMPLATE -replace '__LANG__', $lang
    $content = $content -replace '(</body>)', "$JS`$1"

    # 파일 저장 (UTF-8 BOM 없이)
    [System.IO.File]::WriteAllText($filePath, $content, (New-Object System.Text.UTF8Encoding $false))

    Write-Host "✅ 완료: $file (lang=$lang)" -ForegroundColor Green
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  다국어 선택기 삽입 완료!" -ForegroundColor Green
Write-Host "  브라우저에서 각 파일 열어 확인하세요." -ForegroundColor White
Write-Host "==================================" -ForegroundColor Cyan
pause
