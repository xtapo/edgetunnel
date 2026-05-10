import re
import time
from deep_translator import GoogleTranslator

print("Loading file...")
with open('E:/GitHub/edgetunnel/_worker.js', 'r', encoding='utf-8') as f:
    js_code = f.read()

# simple tokenization of strings, comments and code
token_pat = re.compile(
    r'(?P<mline_comment>/\*.*?\*/)|'
    r'(?P<sline_comment>//.*?$)|'
    r'(?P<string1>\'(?:\\.|[^\\\'])*\')|'
    r'(?P<string2>"(?:\\.|[^\\"])*")|'
    r'(?P<string3>`(?:\\.|[^\\`])*`)|'
    r'(?P<other>.+?)',
    re.DOTALL | re.MULTILINE
)

def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fa5]', text))

# prepare translator
translator = GoogleTranslator(source='zh-CN', target='vi')
translator_en = GoogleTranslator(source='zh-CN', target='en')

cache_vi = {}
def translate_vi(text):
    if not text.strip(): return text
    if not has_chinese(text): return text
    if text in cache_vi: return cache_vi[text]
    try:
        res = translator.translate(text)
        time.sleep(0.05)
        cache_vi[text] = res
        print(f"[VI] {text[:20]} -> {res[:20]}")
        return res
    except Exception as e:
        print("Error VI:", e)
        return text

cache_id = {}
def translate_id(text):
    if not has_chinese(text): return text
    if text in cache_id: return cache_id[text]
    try:
        # translation to English, then remove spaces to make it a valid identifier
        res = translator_en.translate(text)
        res = re.sub(r'[^a-zA-Z0-9_\u4e00-\u9fa5]', '_', res)
        # title case parts to look like pascalCase
        res = ''.join([w.capitalize() for w in res.split('_') if w])
        time.sleep(0.05)
        cache_id[text] = res
        print(f"[ID] {text} -> {res}")
        return res
    except Exception as e:
        print("Error ID:", e)
        return text

tokens = []
print("Tokenizing...")
for match in token_pat.finditer(js_code):
    group = match.lastgroup
    text = match.group(group)
    tokens.append((group, text))

new_tokens = []
print("Translating...")
total = len([t for t in tokens if has_chinese(t[1])])
current = 0

for group, text in tokens:
    if not has_chinese(text):
        new_tokens.append(text)
        continue
    current += 1
    if current % 50 == 0:
        print(f"Progress: {current}/{total}")
        
    if group in ['mline_comment', 'sline_comment', 'string1', 'string2', 'string3']:
        # if it's a string, we might just translate the whole thing?
        # for strings, it might contain formatting like `${url}` in template strings (`...`)
        # Google translate handles simple variables usually, but it can break ${}.
        # For safety, let's just translate the Chinese parts inside the string
        
        # split by chinese chunks vs non-chinese chunks to preserve ${} and HTML
        def repl_vi(m):
            return translate_vi(m.group(0))
            
        new_text = re.sub(r'[\u4e00-\u9fa5]+(.*?[\u4e00-\u9fa5]+)*', repl_vi, text)
        new_tokens.append(new_text)
    else:
        # other code (identifiers). Regex match chinese and translate to English without spaces.
        def repl_id(m):
            return translate_id(m.group(0))
        new_text = re.sub(r'[\u4e00-\u9fa5]+', repl_id, text)
        new_tokens.append(new_text)

new_js_code = ''.join(new_tokens)

with open('E:/GitHub/edgetunnel/_worker.js', 'w', encoding='utf-8') as f:
    f.write(new_js_code)

print("Done _worker.js!")
