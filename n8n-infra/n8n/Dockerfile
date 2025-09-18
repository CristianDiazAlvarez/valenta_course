FROM n8nio/n8n:latest

USER root
# Instala Python y paquetes *Python ya empaquetados* por Alpine
RUN apk add --no-cache \
    python3 py3-pip build-base libpq \
    py3-boto3 py3-pandas py3-openpyxl py3-sqlalchemy py3-psycopg2 py3-pymysql

USER node
