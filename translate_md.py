import re
import time
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='zh-CN', target='vi')

def translate_markdown(file_path):
    print(f"Translating {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    total = len(lines)
    for i, line in enumerate(lines):
        if re.search(r'[\u4e00-\u9fa5]', line):
            # preserve leading whitespace
            leading = len(line) - len(line.lstrip())
            prefix = line[:leading]
            content = line.strip()
            
            # Simple line translation.
            # To protect markdown syntax like [text](url), let's just translate the whole line
            # Google Translate is generally decent with preserving markdown links if they are simple
            try:
                res = translator.translate(content)
                time.sleep(0.05)
                new_lines.append(prefix + res + '\n')
                print(f"[{i}/{total}]")
            except Exception as e:
                print("Error:", e)
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"Done {file_path}")

translate_markdown('E:/GitHub/edgetunnel/README.md')
translate_markdown('E:/GitHub/edgetunnel/CHANGELOG')
