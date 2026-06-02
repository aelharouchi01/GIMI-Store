import re, subprocess
HTML = r'C:\Users\aelha\Downloads\gimi-store.html'
html = open(HTML, encoding='utf-8').read()

# Add code field to the two masterclass products (insert right after id:'...',)
targets = {'cip-mc':'CIP-MC', 'ccio-mc':'CCIO-MC'}
changed = []
for pid, code in targets.items():
    pat = re.compile(r"(mk\(\{ id:'" + re.escape(pid) + r"',)(.*?\}\))", re.DOTALL)
    m = pat.search(html)
    if not m:
        print('no block', pid); continue
    head, body = m.group(1), m.group(2)
    if "code:'" in body:
        print(pid, 'already has code'); continue
    new = head + f" code:'{code}'," + body
    html = html.replace(m.group(0), new, 1)
    changed.append(code)

open(HTML, 'w', encoding='utf-8').write(html)
print('Added code to:', changed)

r = subprocess.run(['node','-e',
    "const fs=require('fs');const h=fs.readFileSync(String.raw`"+HTML+"`,'utf8');"
    "const m=h.match(/<script>([" + chr(92) + "s" + chr(92) + "S]*?)<" + chr(92) + "/script>/);"
    "try{new Function(m[1]);console.log('JS OK')}catch(e){console.log('Err:',e.message)}"],
    capture_output=True, text=True)
print(r.stdout.strip(), r.stderr.strip()[:150])
