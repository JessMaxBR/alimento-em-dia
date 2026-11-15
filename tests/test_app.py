import json
import tempfile
import threading
import unittest
from datetime import date
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from models import Estoque
from app import criar_servidor

def alimento(**changes):
    return dict(nome='Arroz',categoria='Grãos e massas',unidade='kg',quantidade='2.5',validade='2026-11-07',local='Despensa',**changes)

class ModeloTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'test.db'
        self.model=Estoque(self.path)
    def tearDown(self): self.tmp.cleanup()
    def test_persistencia(self):
        self.model.adicionar(alimento())
        self.assertEqual(Estoque(self.path).painel()['alimentos'][0]['quantidade_mil'],2500)
    def test_consumo_e_desperdicio(self):
        item=self.model.adicionar(alimento())
        self.model.movimentar(item,dict(tipo='consumo',quantidade='0.5'))
        self.model.movimentar(item,dict(tipo='desperdicio',quantidade='0.25',motivo='Dano na embalagem'))
        p=self.model.painel()
        self.assertEqual(p['alimentos'][0]['quantidade_mil'],1750)
        self.assertEqual(p['resumo']['kg'],{'consumo':500,'desperdicio':250})
    def test_excesso_nao_altera_saldo_nem_historico(self):
        item=self.model.adicionar(alimento())
        with self.assertRaises(ValueError):self.model.movimentar(item,dict(tipo='consumo',quantidade=3))
        self.assertEqual(self.model.painel()['alimentos'][0]['quantidade_mil'],2500)
        self.assertEqual(self.model.painel()['movimentos'],[])
    def test_quantidades_invalidas(self):
        for n in ['-1','0','NaN','Infinity','0.0001','abc','100001']:
            with self.subTest(n=n), self.assertRaises(ValueError):
                data=alimento();data['quantidade']=n;self.model.adicionar(data)
    def test_datas_e_nome_invalidos(self):
        for key,value in [('validade','2026-02-30'),('nome',' '),('local','X')]:
            data=alimento();data[key]=value
            with self.assertRaises(ValueError):self.model.adicionar(data)
    def test_limites_validade(self):
        for value in ['2026-11-03','2026-11-04','2026-11-07','2026-11-08']:
            data=alimento();data['validade']=value;self.model.adicionar(data)
        self.assertEqual([i['situacao'] for i in self.model.painel(date(2026,11,4))['alimentos']],['Vencido','Vence em breve','Vence em breve','No prazo'])
    def test_esgotado(self):
        item=self.model.adicionar(alimento());self.model.movimentar(item,dict(tipo='consumo',quantidade='2.5'))
        self.assertEqual(self.model.painel()['alimentos'][0]['situacao'],'Esgotado')
    def test_motivo_obrigatorio(self):
        item=self.model.adicionar(alimento())
        with self.assertRaises(ValueError):self.model.movimentar(item,dict(tipo='desperdicio',quantidade=1))
    def test_edicao_e_unidade(self):
        item=self.model.adicionar(alimento());data=alimento();data['nome']='Arroz integral';self.model.editar(item,data)
        self.assertEqual(self.model.painel()['alimentos'][0]['nome'],'Arroz integral')
        data['unidade']='L'
        self.model.editar(item,data)
        self.assertEqual(self.model.painel()['alimentos'][0]['unidade'],'L')
    def test_item_inexistente(self):
        with self.assertRaises(LookupError):self.model.movimentar(999,dict(tipo='consumo',quantidade=1))
    def test_unidades_separadas(self):
        for unit in ['kg','L']:
            data=alimento();data['unidade']=unit;item=self.model.adicionar(data);self.model.movimentar(item,dict(tipo='consumo',quantidade=1))
        p=self.model.painel()['resumo'];self.assertEqual(p['kg']['consumo'],1000);self.assertEqual(p['L']['consumo'],1000)

class HTTPTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.server=criar_servidor(Path(self.tmp.name)/'db',0)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.base=f'http://127.0.0.1:{self.server.server_port}'
        self.token=json.load(urlopen(self.base+'/api/painel'))['token']
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()
    def request(self,route,data,token=True):
        headers={'Content-Type':'application/json'}
        if token:headers['X-CSRF-Token']=self.token
        return urlopen(Request(self.base+route,data=json.dumps(data).encode(),headers=headers))
    def test_fluxo_http(self):
        with self.request('/api/alimentos',alimento()) as r:self.assertEqual(r.status,201);item=json.load(r)['id']
        with self.request(f'/api/alimentos/{item}/movimentar',dict(tipo='consumo',quantidade=1)) as r:self.assertEqual(r.status,200)
        self.assertEqual(json.load(urlopen(self.base+'/api/painel'))['alimentos'][0]['quantidade_mil'],1500)
    def test_post_sem_token(self):
        with self.assertRaises(HTTPError) as ctx:self.request('/api/alimentos',alimento(),False)
        self.assertEqual(ctx.exception.code,403)
    def test_validacao_http(self):
        with self.assertRaises(HTTPError) as ctx:self.request('/api/alimentos',{})
        self.assertEqual(ctx.exception.code,400)
    def test_arquivos_privados_nao_servidos(self):
        for path in ['/schema.sql','/app.py','/../models.py']:
            with self.subTest(path=path),self.assertRaises(HTTPError) as ctx:urlopen(self.base+path)
            self.assertEqual(ctx.exception.code,404)
    def test_frontend_disponivel(self):
        for path in ['/','/app.js','/style.css']:
            with urlopen(self.base+path) as r:self.assertEqual(r.status,200);self.assertGreater(len(r.read()),100)

if __name__=='__main__':unittest.main()

