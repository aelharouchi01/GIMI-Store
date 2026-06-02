"""Adopt V2 catalogue badges for every mapped product."""
import os, shutil, re, subprocess

V2_SRC = r'C:\Users\aelha\Downloads\gimi-store-assets\v2'
DST    = r'C:\Users\aelha\Downloads\gimi-store-assets\v2'  # write back to same folder with product-id names
BOOKS  = r'C:\Users\aelha\Downloads\gimi-store-assets\books'
HTML   = r'C:\Users\aelha\Downloads\gimi-store.html'

# product_id -> V2 image filename
MAP = {
    # ---------- Innovation Core ----------
    'cip-0':            'image3.png',
    'cip-1':            'image4.png',
    'cip-2':            'image5.png',
    'cip-mc':           'image6.png',
    'ccio-1':           'image7.png',
    'ccio-2':           'image8.png',
    'ccio-mc':          'image9.png',
    'cgis-1':           'image10.png',
    'cgit':             'image10.png',
    # 'cgt' is a Placeholder in V2 — keep current placeholder

    # ---------- Innovation Elective ----------
    'ip':               'image13.png',
    'pbcc':             'image3.png',   # reuse CIP-0 per user note
    'cdt-1':            'image14.png',
    'cdt-2':            'image14.png',
    'cdtt-3':           'image14.png',
    'caap':             'image15.jpg',
    'cga':              'image12.png',
    'cime':             'image16.png',
    'ctc':              'image17.png',
    'clc':              'image18.png',

    # ---------- Future Foresight ----------
    'cff-1':            'image19.png',
    'cff-2':            'image20.png',
    'cff-3':            'image21.png',
    'cff-4':            'image22.png',
    'cff-5':            'image23.png',

    # ---------- Leadership ----------
    'clf-1':            'image24.png',
    'cil':              'image24.png',

    # ---------- Consulting ----------
    'mci-1':            'image25.png',
    'mci-2':            'image26.png',
    'mci-3':            'image27.jpg',
    'mci-4':            'image28.png',

    # ---------- Books ----------
    'ffbok-1':          'image29.png',
    'ffbok-2':          'image30.png',
    'imbok-1':          'image31.png',
    'imbok-3':          'image32.png',
    'connectivate':     'image33.png',
    'healthovate':      'image34.png',
    'greenovate':       'image35.png',
    'game-changers':    'image36.png',
    'squiggly':         'image37.png',
    'ijis':             'image38.png',
    'idex':             'image39.png',
    'iso-book':         'image40.png',
    'technovate':       'image17.png',  # share with CTC per user note

    # ---------- Programs & Tools ----------
    'ipa-individual':   'image41.png',
    'ipa-corporate':    'image41.png',
    'mindset-index':    'image42.png',
    'oia-self':         'image44.png',
    'full-oia':         'image44.png',
    'eureka':           'image45.png',
    'service-tool':     'image46.png',
    'akaio':            'image47.png',
    # 'quickgrowth' placeholder in V2 — keep current 2x.jpeg
    'coaching':         'image49.png',
    'speech':           'image50.jpg',
    'academy':          'image51.png',
    'awards-individual':'image43.png',
    'awards-org':       'image43.png',

    # ---------- Memberships ----------
    'memb-student':     'image52.png',
    'memb-pro':         'image53.png',
    'thinktank':        'image54.jpeg',
    'memb-silver':      'image55.png',
    'memb-gold':        'image56.png',
    'memb-plat':        'image57.png',
    'memb-academia':    'image58.png',
}

# Step 1: copy & rename images so badge paths are clean
for pid, src_name in MAP.items():
    src_path = os.path.join(V2_SRC, src_name)
    if not os.path.exists(src_path):
        print(f'  MISS src {src_name} for {pid}'); continue
    ext = os.path.splitext(src_name)[1]
    dst_name = pid + ext
    dst_path = os.path.join(DST, dst_name)
    shutil.copy(src_path, dst_path)

# Step 2: update HTML badge paths for each mapped product
html = open(HTML, encoding='utf-8').read()
updated = []
for pid, src_name in MAP.items():
    ext = os.path.splitext(src_name)[1]
    new_path = f'gimi-store-assets/v2/{pid}{ext}'
    pat = re.compile(r"(mk\(\{ id:'" + re.escape(pid) + r"',.*?\}\))", re.DOTALL)
    m = pat.search(html)
    if not m:
        print(f'  no block for {pid}'); continue
    block = m.group(1)
    if "badge:" in block:
        new_block = re.sub(r"badge:'[^']*'", f"badge:'{new_path}'", block, count=1)
    else:
        new_block = re.sub(r"(\s+)description:",
                           lambda mo: mo.group(1) + f"badge:'{new_path}'," + mo.group(1) + "description:",
                           block, count=1)
    if new_block != block:
        html = html.replace(block, new_block)
        updated.append(pid)

open(HTML, 'w', encoding='utf-8').write(html)
print(f'\nUpdated {len(updated)} products')

# Step 3: validate JS
r = subprocess.run(['node','-e',
                    "const fs=require('fs');"
                    "const h=fs.readFileSync(String.raw`" + HTML + "`,'utf8');"
                    "const m=h.match(/<script>([\\s\\S]*?)<\\/script>/);"
                    "try{new Function(m[1]);console.log('JS OK')}catch(e){console.log('Err:',e.message)}"],
                   capture_output=True, text=True)
print(r.stdout.strip())

# Step 4: sync to deploy
shutil.copy(HTML, r'C:\Users\aelha\Downloads\gimi-store-deploy\index.html')
dst_v2 = r'C:\Users\aelha\Downloads\gimi-store-deploy\gimi-store-assets\v2'
if os.path.exists(dst_v2): shutil.rmtree(dst_v2)
shutil.copytree(V2_SRC, dst_v2)
print(f'Synced to deploy. V2 assets: {len(os.listdir(dst_v2))}')
