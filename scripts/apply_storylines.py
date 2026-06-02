import json, re, subprocess
HTML = r'C:\Users\aelha\Downloads\gimi-store.html'
BS=chr(92); SQ=chr(39)
story = json.load(open('deck_storylines_clean.json', encoding='utf-8'))
CODE_TO_ID = {
 'IP':'ip','PBCC':'pbcc','CGIS-1':'cgis-1','CIP-0':'cip-0','CIP-1':'cip-1','CIP-2':'cip-2',
 'CIP-MC':'cip-mc','CCIO-1':'ccio-1','CCIO-2':'ccio-2','CCIO-MC':'ccio-mc','CGIT':'cgit','CGT':'cgt',
 'CDT-1':'cdt-1','CDT-2':'cdt-2','CDTT-3':'cdtt-3','CFF-1':'cff-1','CFF-2':'cff-2','CFF-3':'cff-3',
 'CFF-4':'cff-4','CFF-5':'cff-5','CLF-1':'clf-1','CIL':'cil','MCI-1':'mci-1','MCI-2':'mci-2',
 'MCI-3':'mci-3','MCI-4':'mci-4','CAAP':'caap','CGA':'cga','CIME':'cime','CTC':'ctc','CLC':'clc',
}
def js(s): return s.replace(BS,BS+BS).replace(SQ,BS+SQ)

html = open(HTML, encoding='utf-8').read()

def find_block(pid):
    start = html.find("mk({ id:'"+pid+"',")
    if start < 0: return None
    # brace-match
    i = html.find('{', start); depth=1; j=i
    while j < len(html) and depth>0:
        j+=1
        if html[j]=='{': depth+=1
        elif html[j]=='}': depth-=1
    return (start, j+1)

def replace_tagline(block, newval):
    key = "tagline:'"
    p = block.find(key)
    if p < 0: return block
    k = p + len(key); 
    # scan to closing quote respecting escapes
    while k < len(block):
        if block[k]==BS: k+=2; continue
        if block[k]==SQ: break
        k+=1
    return block[:p+len(key)] + newval + block[k:]

n=0
for code, pid in CODE_TO_ID.items():
    s = story.get(code)
    if not s: continue
    span = find_block(pid)
    if not span: print('no block', code); continue
    block = html[span[0]:span[1]]
    newblock = replace_tagline(block, js(s))
    if newblock != block:
        html = html[:span[0]] + newblock + html[span[1]:]
        n+=1

open(HTML,'w',encoding='utf-8').write(html)
print('Updated taglines:', n)
r = subprocess.run(['node','-e',
    "const fs=require('fs');const h=fs.readFileSync(String.raw`"+HTML+"`,'utf8');"
    "const m=h.match(/<script>([" + BS+"s"+BS+"S]*?)<"+BS+"/script>/);"
    "try{new Function(m[1]);console.log('JS OK')}catch(e){console.log('Err:',e.message)}"],
    capture_output=True, text=True)
print(r.stdout.strip(), r.stderr.strip()[:150])
