# tests/test_schemas_admin.py
from app_gestao.schemas.admin import AdminCreate
from app_gestao.schemas.user import UserCreate  # Mova para o topo aqui


def test_admin_create_schema_valido():
    data = {
        'username': 'admin_test',
        'email': 'admin@test.com',
        'password': 'secret_password',
    }

    admin = AdminCreate(**data)

    assert admin.username == data['username']
    assert admin.email == data['email']
    assert admin.password == data['password']


def test_admin_create_schema_heranca():
    # Agora a variável UserCreate já está disponível globalmente no arquivo
    assert issubclass(AdminCreate, UserCreate)
