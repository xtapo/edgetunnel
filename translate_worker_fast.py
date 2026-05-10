import re
import socket
import time
# set default timeout to prevent hanging
socket.setdefaulttimeout(3)

from deep_translator import GoogleTranslator

print("Loading file...")
with open('E:/GitHub/edgetunnel/_worker.js', 'r', encoding='utf-8') as f:
    js_code = f.read()

# Tokenize into strings, comments and others
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

translator = GoogleTranslator(source='zh-CN', target='vi')

cache_vi = {}
def translate_vi(text):
    if not text.strip(): return text
    if not has_chinese(text): return text
    if text in cache_vi: return cache_vi[text]
    try:
        res = translator.translate(text)
        cache_vi[text] = res
        return res
    except Exception as e:
        print("Error VI:", text[:10], e)
        return text

tokens = []
for match in token_pat.finditer(js_code):
    tokens.append((match.lastgroup, match.group(match.lastgroup)))

new_tokens = []
strings_with_c = [t for t in tokens if t[0] in ['mline_comment', 'sline_comment', 'string1', 'string2', 'string3'] and has_chinese(t[1])]
total = len(strings_with_c)
print(f"Translating {total} string/comment tokens...")

current = 0
for group, text in tokens:
    if group in ['mline_comment', 'sline_comment', 'string1', 'string2', 'string3'] and has_chinese(text):
        current += 1
        if current % 10 == 0:
            print(f"Progress: {current}/{total}")
        
        def repl(m):
            return translate_vi(m.group(0))
        
        new_text = re.sub(r'[\u4e00-\u9fa5]+(?:[^\w\u4e00-\u9fa5A-Za-z0-9_\n]*[\u4e00-\u9fa5]+)*', repl, text)
        new_tokens.append(new_text)
    else:
        new_tokens.append(text)

with open('E:/GitHub/edgetunnel/_worker.js', 'w', encoding='utf-8') as f:
    f.write(''.join(new_tokens))

print("Done _worker.js!")
