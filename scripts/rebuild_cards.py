import re, json, subprocess
HTML = r'C:\Users\aelha\Downloads\gimi-store.html'
cards = json.load(open('deck_cards.json', encoding='utf-8'))
BS=chr(92); SQ=chr(39); BULLET=chr(0x2022)

# normalize recert bullet -> comma
def norm_recert(s):
    if not s: return s
    s = s.replace(chr(0x25CF),',').replace(BULLET,',').replace(' ,',',')
    return ' '.join(s.split())

CODE_TO_ID = {
 'IP':'ip','PBCC':'pbcc','CGIS-1':'cgis-1','CIP-0':'cip-0','CIP-1':'cip-1','CIP-2':'cip-2',
 'CIP-MC':'cip-mc','CCIO-1':'ccio-1','CCIO-2':'ccio-2','CCIO-MC':'ccio-mc','CGIT':'cgit','CGT':'cgt',
 'CDT-1':'cdt-1','CDT-2':'cdt-2','CDTT-3':'cdtt-3','CFF-1':'cff-1','CFF-2':'cff-2','CFF-3':'cff-3',
 'CFF-4':'cff-4','CFF-5':'cff-5','CLF-1':'clf-1','CIL':'cil','MCI-1':'mci-1','MCI-2':'mci-2',
 'MCI-3':'mci-3','MCI-4':'mci-4','CAAP':'caap','CGA':'cga','CIME':'cime','CTC':'ctc','CLC':'clc',
}
def js(s):
    return s.replace(BS,BS+BS).replace(SQ,BS+SQ)

html = open(HTML, encoding='utf-8').read()
n_changed=0
for code, pid in CODE_TO_ID.items():
    c = cards.get(code, {})
    exam = js(c.get('exam') or 'Online proctored MCQ')
    pas  = js(c.get('pass') or '70%')
    rec  = js(norm_recert(c.get('recert')) or '3-year cycle')
    crt  = js(c.get('certificate') or 'Digital certificate')
    new_details = ("{ 'Exam Format':'%s', 'Pass Threshold':'%s', "
                   "'Recertification':'%s', 'Certificate':'%s' }" % (exam,pas,rec,crt))
    # Replace the details:{...} object inside this product block
    pat = re.compile(r"(mk\(\{ id:'" + re.escape(pid) + r"',.*?details:)\{[^}]*\}(\}\))", re.DOTALL)
    m = pat.search(html)
    if not m:
        print('NO MATCH', code); continue
    html = html[:m.start()] + m.group(1) + new_details + m.group(2) + html[m.end():]
    n_changed += 1

# Fix masterclass modality (strip "Format") -> Live Virtual Cohort
for pid in ['cip-mc','ccio-mc']:
    pat = re.compile(r"(mk\(\{ id:'"+pid+r"',.*?modality:')[^']*(')", re.DOTALL)
    if pat.search(html):
        html = pat.sub(lambda m: m.group(1)+'Live Virtual Cohort'+m.group(2), html, count=1)
    else:
        # insert modality after target if missing — but mk default exists, so set via details? 
        pass

open(HTML,'w',encoding='utf-8').write(html)
print(f'Rebuilt details for {n_changed} products')

r = subprocess.run(['node','-e',
    "const fs=require('fs');const h=fs.readFileSync(String.raw`"+HTML+"`,'utf8');"
    "const m=h.match(/<script>([" + BS+"s"+BS+"S]*?)<"+BS+"/script>/);"
    "try{new Function(m[1]);console.log('JS OK')}catch(e){console.log('Err:',e.message)}"],
    capture_output=True, text=True)
print(r.stdout.strip(), r.stderr.strip()[:150])
