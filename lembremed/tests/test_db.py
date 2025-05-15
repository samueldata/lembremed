from django.db import connections
from django.db.utils import OperationalError
import pytest

@pytest.mark.django_db
def test_database_connection():
    """Testa se a conexão com o banco de dados está funcionando."""
    db_conn = connections['default']
    try:
        db_conn.cursor()
    except OperationalError as e:
        pytest.fail(f"Não foi possível conectar ao banco de dados: {e}")

@pytest.mark.django_db
def test_required_tables_exist():
    """Testa se as tabelas esperadas existem no banco de dados."""
    db_conn = connections['default']
    with db_conn.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = ['lembremed_medicamento', 'lembremed_apresentacao']
        for table in expected_tables:
            assert table in tables, f"A tabela {table} não existe no banco de dados."