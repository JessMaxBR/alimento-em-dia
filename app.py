"""Controlador HTTP local. Execute com python3 app.py e abra o endereço exibido."""
import json
import os
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from models import Estoque

ROOT = Path(__file__).resolve().parent

def criar_servidor(db_path, port=8765):
    estoque = Estoque(db_path)
    token = secrets.token_urlsafe(32)

    class Controller(BaseHTTPRequestHandler):
        def responder(self, data, status=200, mime='application/json; charset=utf-8'):
            content = json.dumps(data, ensure_ascii=False).encode() if isinstance(data, dict) else data
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(content)

        def host_valido(self):
            return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')

        def do_GET(self):
            if not self.host_valido():
                return self.responder({'erro':'Acesso permitido somente pelo endereço local.'}, 403)
            route = urlsplit(self.path).path
            if route == '/api/painel':
                return self.responder({**estoque.painel(), 'token': token})
            files = {'/': ('index.html','text/html'), '/app.js': ('app.js','text/javascript'), '/style.css': ('style.css','text/css')}
            if route not in files:
                return self.responder({'erro':'Página não encontrada.'}, 404)
            name, mime = files[route]
            return self.responder((ROOT/'static'/name).read_bytes(), mime=mime+'; charset=utf-8')

        def do_POST(self):
            if not self.host_valido() or not secrets.compare_digest(self.headers.get('X-CSRF-Token',''), token):
                return self.responder({'erro':'Atualize a página antes de salvar.'},403)
            if self.headers.get_content_type() != 'application/json':
                return self.responder({'erro':'Formato esperado: JSON.'},415)
            try:
                size = int(self.headers.get('Content-Length','0'))
                if not 0 < size <= 8192:
                    raise ValueError('Requisição vazia ou muito grande.')
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError('Dados inválidos.')
                route = urlsplit(self.path).path
                if route == '/api/alimentos':
                    return self.responder({'id':estoque.adicionar(data)},201)
                parts = route.strip('/').split('/')
                if len(parts) == 4 and parts[:2] == ['api','alimentos'] and parts[3] in ('editar','movimentar'):
                    item_id = int(parts[2])
                    getattr(estoque, parts[3])(item_id, data)
                    return self.responder({'ok':True})
                return self.responder({'erro':'Operação não encontrada.'},404)
            except LookupError as exc:
                return self.responder({'erro':str(exc)},404)
            except (ValueError, TypeError) as exc:
                return self.responder({'erro':str(exc)},400)
            except Exception:
                self.log_error('Erro interno ao processar operação')
                return self.responder({'erro':'Não foi possível salvar. Tente novamente.'},500)

    return ThreadingHTTPServer(('127.0.0.1',port), Controller)

if __name__ == '__main__':
    data_dir = ROOT/'data'
    data_dir.mkdir(exist_ok=True)
    try:
        server = criar_servidor(data_dir/'alimentos.db', int(os.environ.get('PORT','8765')))
        print(f'\nAlimento em Dia: http://127.0.0.1:{server.server_port}\nMantenha este terminal aberto. Para encerrar: Ctrl+C.\n', flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nSistema encerrado. Seus dados continuam salvos.')
