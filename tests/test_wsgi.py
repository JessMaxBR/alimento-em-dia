import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from models import Estoque


class WSGITest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / 'test.db'
        self.stock = Estoque(self.db)
        # Load controller without creating a production database.
        source = Path(__file__).resolve().parents[1] / 'wsgi.py'
        with patch('models.Estoque', return_value=self.stock), patch('pathlib.Path.mkdir'):
            self.ns = {'__file__': str(source)}
            exec(compile(source.read_text(), str(source), 'exec'), self.ns)
        self.food = dict(nome='Arroz', categoria='Grãos e massas', unidade='kg',
                         quantidade='2', validade='2027-01-01', local='Despensa')

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, path, data=None, token=True):
        body = json.dumps(data).encode() if data is not None else b''
        env = {'PATH_INFO': path, 'REQUEST_METHOD': 'POST' if data is not None else 'GET',
               'CONTENT_TYPE': 'application/json', 'CONTENT_LENGTH': str(len(body)),
               'wsgi.input': io.BytesIO(body),
               'HTTP_X_CSRF_TOKEN': self.ns['TOKEN'] if token else ''}
        result = []
        body = b''.join(self.ns['application'](env, lambda s, h: result.append(s)))
        return result[0], body

    def test_public_and_private_files(self):
        for path in ('/', '/app.js', '/style.css'):
            self.assertEqual(self.call(path)[0], '200 OK')
        for path in ('/models.py', '/schema.sql', '/data/alimentos.db', '/../models.py'):
            self.assertEqual(self.call(path)[0], '404 Not Found')

    def test_token_required(self):
        self.assertEqual(self.call('/api/alimentos', self.food, False)[0], '403 Forbidden')
        self.assertEqual(self.stock.painel()['alimentos'], [])

    def test_transaction_and_persistence(self):
        self.assertEqual(self.call('/api/alimentos', self.food)[0], '201 Created')
        self.assertEqual(self.call('/api/alimentos/1/movimentar', dict(tipo='consumo', quantidade='0.5'))[0], '200 OK')
        self.assertEqual(self.call('/api/alimentos/1/movimentar', dict(tipo='consumo', quantidade='9'))[0], '400 Bad Request')
        state = Estoque(self.db).painel()
        self.assertEqual(state['alimentos'][0]['quantidade_mil'], 1500)
        self.assertEqual(len(state['movimentos']), 1)
        self.assertEqual(json.loads(self.call('/api/painel')[1])['alimentos'][0]['quantidade_mil'], 1500)

    def test_invalid_json_object(self):
        self.assertEqual(self.call('/api/alimentos', [1, 2])[0], '400 Bad Request')
