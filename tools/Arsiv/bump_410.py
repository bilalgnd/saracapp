import os
import codecs

def bump(filepath, old_str, new_str):
    with codecs.open(filepath, 'r', 'utf-8') as f:
        t = f.read()
    t = t.replace(old_str, new_str)
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.write(t)

bump('C:/Users/bilal/SARACAPP/kasa_app.pyw', '4.0.9', '4.1.0')
bump('C:/Users/bilal/SARACAPP/templates/index.html', '4.0.9', '4.1.0')
bump('C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt', '4.0.9', '4.1.0')
bump('C:/Users/bilal/AndroidStudioProjects/saracapp/app/build.gradle.kts', 'versionName = "4.0.9"', 'versionName = "4.1.0"')
bump('C:/Users/bilal/AndroidStudioProjects/saracapp/app/build.gradle.kts', 'versionCode = 4009', 'versionCode = 4100')

kasa_pyw = 'C:/Users/bilal/SARACAPP/kasa_app.pyw'
with codecs.open(kasa_pyw, 'r', 'utf-8') as f:
    text = f.read()

old_route = '''@flask_app.route('/')
def ana_sayfa():
    return render_template('index.html')'''

new_route = '''@flask_app.route('/')
def ana_sayfa():
    return render_template('index.html')

@flask_app.route('/tv')
def tv_sayfa():
    return render_template('tv.html')'''

text = text.replace(old_route, new_route)

with codecs.open(kasa_pyw, 'w', 'utf-8') as f:
    f.write(text)

index_html = 'C:/Users/bilal/SARACAPP/templates/index.html'
with codecs.open(index_html, 'r', 'utf-8') as f:
    itext = f.read()

old_header = '''    <header class="app-header">
        <div class="logo">
            <span class="logo-text">SARAÇOĞLU</span>
            <span class="logo-sub">DÖNER <span>v4.1.0</span></span>
        </div>
        <div class="connection-status" id="connStatus"></div>
    </header>'''

new_header = '''    <header class="app-header">
        <div class="logo">
            <span class="logo-text">SARAÇOĞLU</span>
            <span class="logo-sub">DÖNER <span>v4.1.0</span></span>
        </div>
        <div style="display:flex; align-items:center; gap: 15px;">
            <a href="/tv" target="_blank" style="color:white; text-decoration:none; background:var(--primary-light); color:black; padding:8px 12px; border-radius:8px; font-weight:800; font-size:14px;">📺 TV Modu</a>
            <div class="connection-status" id="connStatus"></div>
        </div>
    </header>'''

itext = itext.replace(old_header, new_header)

with codecs.open(index_html, 'w', 'utf-8') as f:
    f.write(itext)

print("Bumped to 4.1.0 and injected TV routes.")
