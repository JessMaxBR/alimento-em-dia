"""Copiar para o arquivo WSGI indicado na aba Web do PythonAnywhere."""
import sys
path = '/home/jessicakelenmaximiano/alimento_em_dia'
if path not in sys.path:
    sys.path.insert(0, path)
from wsgi import application
