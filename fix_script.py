import os
import re

file_path = r'D:\Companys\Neuralshield\Software\Neural Radar\NeuralRadar\app\gui\devicevault_page.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 1
text = text.replace('f"Data exported to:\n{path}")', 'f"Data exported to:\\n{path}")')
text = text.replace('f"Data exported to:\r\n{path}")', 'f"Data exported to:\\n{path}")')

# Fix 2
text = re.sub(r'f"Markdown report saved to:\r?\n\s+else:', 'f"Markdown report saved to:\\n{path}")\n        else:', text)

# Fix 3
text = re.sub(r'f"HTML report saved to:\r?\n\s+else:', 'f"HTML report saved to:\\n{path}")\n        else:', text)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Replaced!")
