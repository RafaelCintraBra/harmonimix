"""Ponto de entrada.

    flask --app run init-db      # cria as tabelas
    flask --app run seed-demo    # (opcional) usuário de demonstração
    flask --app run run --debug  # inicia em http://127.0.0.1:5000
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
