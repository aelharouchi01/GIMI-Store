import re, json
html = open('gimi-store.html', encoding='utf-8').read()
BS = chr(92)   # backslash
SQ = chr(39)   # single quote

def parse_blocks(s):
    res=[]; i=0
    while True:
        idx=s.find('mk({', i)
        if idx<0: break
        depth=1; j=idx+3
        while j<len(s) and depth>0:
            j+=1
            if s[j]=='{': depth+=1
            elif s[j]=='}': depth-=1
        block=s[idx+3:j+1]
        res.append(block[block.find('{'):block.rfind('}')+1])
        i=s.find(')', j)+1
    return res

def field(b, name):
    key = name + ":" + SQ
    pos = b.find(key)
    if pos < 0: return None
    k = pos + len(key); out=[]
    while k < len(b):
        c = b[k]
        if c == BS:
            out.append(b[k+1]); k += 2; continue
        if c == SQ:
            break
        out.append(c); k += 1
    return ''.join(out)

m = re.search(r'const PRODUCTS = \[([\s\S]*?)\n\];', html)
blocks = parse_blocks(m.group(1))
store = {}
for b in blocks:
    code = field(b,'code')
    if not code: continue
    store[code] = {
        'cert': field(b,'certDisplay'),
        'train': field(b,'trainDisplay'),
        'duration': field(b,'duration'),
        'desc': field(b,'description') or ''
    }
json.dump(store, open('store_parsed.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('Parsed', len(store), 'coded products')
print('CIP-1:', store.get('CIP-1'))
