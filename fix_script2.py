import os

file_path = r'D:\Companys\Neuralshield\Software\Neural Radar\NeuralRadar\app\gui\devicevault_page.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('f"Markdown report saved to:\n{path}")', 'f"Markdown report saved to:\\n{path}")')
text = text.replace('f"HTML report saved to:\n{path}")', 'f"HTML report saved to:\\n{path}")')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Replaced 2!")
