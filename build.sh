#!/usr/bin/env bash
# Exit on error
set -o errexit

# Instala as dependências
echo "🔄 Instalando dependências..."
pip install -r requirements.txt

# Coleta arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

echo "🔄 Aplicando migrações..."
python manage.py migrate --no-input

# Cria superusuário automaticamente (se não existir)
echo "👤 Criando superusuário padrão (se não existir)..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()

username = 'admin'
email = 'admin@example.com'
password = 'admin123'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("✅ Superusuário criado com sucesso.")
else:
    print("⚠️ Superusuário já existe.")
EOF

echo "✅ Build concluído com sucesso!"
