import json
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from models import Estoque

(ROOT / 'data').mkdir(exist_ok=True)
estoque = Estoque(ROOT / 'data' / 'alimentos.db')
TOKEN = secrets.token_urlsafe(32)
FILES = {'/': ('index.html', 'text/html'),
         '/app.js': ('app.js', 'text/javascript'),
         '/style.css': ('style.css', 'text/css')}


def application(environ, start_response):
    def responder(data, status='200 OK', mime='application/json'):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8') if isinstance(data, dict) else data
        start_response(status, [
            ('Content-Type', mime + '; charset=utf-8'),
            ('Content-Length', str(len(body))),
            ('Cache-Control', 'no-store'),
            ('X-Content-Type-Options', 'nosniff'),
            ('Content-Security-Policy', "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        ])
        return [body]

    route = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    try:
        if method == 'GET':
            if route == '/api/painel':
                return responder({**estoque.painel(), 'token': TOKEN})
            if route in FILES:
                name, mime = FILES[route]
                return responder((ROOT / 'static' / name).read_bytes(), mime=mime)
            return responder({'erro': 'Página não encontrada.'}, '404 Not Found')
        if method != 'POST':
            return responder({'erro': 'Método não permitido.'}, '405 Method Not Allowed')
        if not secrets.compare_digest(environ.get('HTTP_X_CSRF_TOKEN', ''), TOKEN):
            return responder({'erro': 'Atualize a página antes de salvar.'}, '403 Forbidden')
        if environ.get('CONTENT_TYPE', '').split(';')[0].strip() != 'application/json':
            return responder({'erro': 'Formato esperado: JSON.'}, '415 Unsupported Media Type')
        size = int(environ.get('CONTENT_LENGTH') or '0')
        if not 0 < size <= 8192:
            raise ValueError('Requisição vazia ou muito grande.')
        data = json.loads(environ['wsgi.input'].read(size))
        if not isinstance(data, dict):
            raise ValueError('Dados inválidos.')
        if route == '/api/alimentos':
            return responder({'id': estoque.adicionar(data)}, '201 Created')
        parts = route.strip('/').split('/')
        if len(parts) == 4 and parts[:2] == ['api', 'alimentos'] and parts[3] in ('editar', 'movimentar'):
            getattr(estoque, parts[3])(int(parts[2]), data)
            return responder({'ok': True})
        return responder({'erro': 'Operação não encontrada.'}, '404 Not Found')
    except LookupError as exc:
        return responder({'erro': str(exc)}, '404 Not Found')
    except (ValueError, TypeError) as exc:
        return responder({'erro': str(exc)}, '400 Bad Request')
    except Exception:
        import traceback
        traceback.print_exc(file=environ.get('wsgi.errors', sys.stderr))
        return responder({'erro': 'Erro interno. Consulte o registro de erros.'}, '500 Internal Server Error')
