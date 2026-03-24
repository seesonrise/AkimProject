import sys
import importlib

from app import app

def check_python_version():
    """Проверяет версию Python."""
    if sys.version_info < (3, 8):
        print(f"Ошибка: Требуется Python 3.8 или выше. Текущая версия: {sys.version}")
        sys.exit(1)
    print(f"Версия Python: {sys.version}")

def check_dependencies():
    """Проверяет установку основных зависимостей."""
    dependencies = [
        'flask',
        'flask_sqlalchemy',
        'flask_migrate',
        'flask_login',
        'flask_bcrypt',
        'bcrypt',
        'alembic',
        'sqlalchemy'
    ]
    missing = []
    for dep in dependencies:
        try:
            importlib.import_module(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        print(f"Ошибка: Отсутствуют зависимости: {', '.join(missing)}")
        print("Установите их с помощью: pip install -r requirements.txt")
        sys.exit(1)
    print("Все основные зависимости установлены.")

if __name__ == "__main__":
    check_python_version()
    check_dependencies()
    app.run(debug=True)
