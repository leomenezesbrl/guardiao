# Crie um script chamado fix_encoding.py

with open('backup.json', 'rb') as file:
    content = file.read()

with open('backup_fixed.json', 'w', encoding='utf-8') as file:
    file.write(content.decode('utf-8', errors='ignore'))
