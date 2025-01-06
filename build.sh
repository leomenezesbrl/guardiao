#!/usr/bin/env bash
# Exit on error
set -o errexit

# Instala as dependências
pip install -r requirements.txt

# Coleta os arquivos estáticos
python manage.py collectstatic --noinput

# Aplica as migrações do banco de dados
python manage.py migrate
