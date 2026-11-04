# Instalação e hospedagem

## Requisitos
Python 3.12, biblioteca padrão, SQLite fornecido com Python. Não é necessário pip. O servidor local usa apenas 127.0.0.1.

## Windows
Na pasta extraída, abra o Terminal e execute `py -3 app.py`. Abra http://127.0.0.1:8765/ e mantenha o terminal aberto. Se o lançador py não existir, use `python app.py` com Python instalado.

## macOS e Linux
Na pasta do projeto execute `python3 app.py`. Abra http://127.0.0.1:8765/. Para parar, Ctrl+C. No macOS, permita ao Terminal acessar Downloads caso o sistema solicite.

## PythonAnywhere
1. Crie a aplicação Web com configuração manual e Python 3.12.
2. Envie e extraia a pasta do projeto em `/home/SEU_USUARIO/alimento_em_dia`.
3. No arquivo WSGI indicado na aba Web, use o conteúdo de `pythonanywhere_wsgi.py`, ajustando o caminho para sua conta.
4. Os arquivos `wsgi.py`, `models.py`, `schema.sql` e a pasta `static` devem estar na pasta do projeto. Não execute `app.py` em console para manter a aplicação hospedada.
5. Clique em Save e depois Reload na aba Web. Ative Force HTTPS no painel e recarregue.
6. Abra o endereço HTTPS e teste cadastro, saída, validação de saldo e persistência.

Se a aplicação atual já funciona com o controlador inteiro no arquivo WSGI do provedor, essa separação é opcional. Faça backup da configuração antes de mudar. Não sobrescreva o banco para atualizar código.

## Banco e backup
Cada ambiente grava em `data/alimentos.db`. Para uma cópia consistente com a aplicação em uso, execute na pasta do projeto:

```python
import sqlite3
with sqlite3.connect('data/alimentos.db') as origem:
    with sqlite3.connect('backup_alimentos.db') as destino:
        origem.backup(destino)
```

Baixe o backup e mantenha-o fora do GitHub. Restaurar um backup substitui o estoque; interrompa gravações antes da restauração. O ZIP distribuído não inclui banco ou dados de visitantes.

## Manutenção
Renove o plano gratuito pelo botão Run until 1 month from today antes da data exibida no painel. Se houver erro, consulte Error log na aba Web. Após alterações de código, use Reload. O token muda ao recarregar: visitantes devem atualizar a página.

Referência: https://help.pythonanywhere.com/pages/WebAppBasics/
