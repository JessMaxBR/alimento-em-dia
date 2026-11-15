import sqlite3
import test_app
from test_app import alimento
import test_wsgi
import unittest

class EdicaoTest(unittest.TestCase):
    setUp = test_app.ModeloTest.setUp
    tearDown = test_app.ModeloTest.tearDown
    def test_saldo_unidade_e_historico_preservados(self):
        i=self.model.adicionar(alimento())
        self.model.movimentar(i,dict(tipo='consumo',quantidade='0.5'))
        d=alimento();d.update(quantidade='4',unidade='un')
        self.model.editar(i,d)
        p=self.model.painel()
        self.assertEqual((p['alimentos'][0]['quantidade_mil'],p['alimentos'][0]['unidade']),(4000,'un'))
        self.assertEqual((p['movimentos'][0]['quantidade_mil'],p['movimentos'][0]['unidade']),(500,'kg'))
        self.assertEqual(p['resumo']['kg']['consumo'],500)
        self.assertEqual(p['resumo']['un']['consumo'],0)
        self.assertEqual(p['ajustes'][0]['quantidade_anterior_mil'],2000)
        self.model.movimentar(i,dict(tipo='consumo',quantidade='1'))
        self.assertEqual(self.model.painel()['resumo']['un']['consumo'],1000)
    def test_zero_e_rejeicao_atomica(self):
        i=self.model.adicionar(alimento());d=alimento();d['quantidade']='0'
        self.model.editar(i,d)
        self.assertEqual(self.model.painel()['alimentos'][0]['situacao'],'Esgotado')
        for q in ['-1','NaN','0.0001','100001','',None]:
            d['quantidade']=q;d['nome']='Não salvar'
            with self.assertRaises(ValueError):self.model.editar(i,d)
        self.assertEqual(self.model.painel()['alimentos'][0]['nome'],'Arroz')
        self.assertEqual(len(self.model.painel()['ajustes']),1)
    def test_formulario_desatualizado(self):
        i=self.model.adicionar(alimento());self.model.movimentar(i,dict(tipo='consumo',quantidade=1))
        d=alimento();d.update(quantidade_anterior_mil='2500',unidade_anterior='kg')
        with self.assertRaises(ValueError):self.model.editar(i,d)
        self.assertEqual(self.model.painel()['alimentos'][0]['quantidade_mil'],1500)
    def test_migracao_banco_antigo(self):
        old=self.path.parent/'old.db'
        with sqlite3.connect(old) as db:
            db.executescript('CREATE TABLE alimentos(id INTEGER PRIMARY KEY,nome TEXT,categoria TEXT,unidade TEXT,quantidade_mil INTEGER,validade TEXT,local TEXT); CREATE TABLE movimentos(id INTEGER PRIMARY KEY,alimento_id INTEGER,tipo TEXT,quantidade_mil INTEGER,motivo TEXT,criado_em TEXT);')
            db.execute("INSERT INTO alimentos VALUES(1,'Leite','Laticínios','L',1000,'2026-12-01','Geladeira')")
            db.execute("INSERT INTO movimentos VALUES(1,1,'consumo',500,'','2026-11-15')")
        from models import Estoque
        m=Estoque(old);Estoque(old)
        d=alimento();d.update(unidade='kg',quantidade='3');m.editar(1,d)
        self.assertEqual(m.painel()['movimentos'][0]['unidade'],'L')
        self.assertEqual(m.painel()['resumo']['L']['consumo'],500)

class EdicaoWSGITest(unittest.TestCase):
    setUp = test_wsgi.WSGITest.setUp
    tearDown = test_wsgi.WSGITest.tearDown
    call = test_wsgi.WSGITest.call
    def test_edicao_pela_api(self):
        self.call('/api/alimentos',self.food)
        d=dict(self.food,quantidade='4',unidade='L',quantidade_anterior_mil='2000',unidade_anterior='kg')
        self.assertEqual(self.call('/api/alimentos/1/editar',d)[0],'200 OK')
        self.assertEqual(self.stock.painel()['alimentos'][0]['quantidade_mil'],4000)
        self.assertEqual(self.call('/api/alimentos/1/editar',d)[0],'400 Bad Request')
