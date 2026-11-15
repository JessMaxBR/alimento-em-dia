"""Modelo: validações, persistência e regras de estoque. Quantidades em milésimos."""
import sqlite3
from contextlib import closing
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

CATEGORIAS = ('Frutas e verduras', 'Laticínios', 'Carnes e ovos', 'Grãos e massas', 'Bebidas', 'Outros')
LOCAIS = ('Geladeira', 'Congelador', 'Despensa')

def texto(value, label, maximum=80):
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= maximum:
        raise ValueError(f'{label}: preencha de 1 a {maximum} caracteres.')
    return value.strip()

def quantidade(value, permitir_zero=False):
    try:
        n = Decimal(str(value).replace(',', '.'))
        scaled = n * 1000
        if not n.is_finite() or (n < 0 if permitir_zero else n <= 0) or n > 100000 or scaled != scaled.to_integral_value():
            raise ValueError()
        return int(scaled)
    except (InvalidOperation, ValueError, TypeError):
        minimo = 'zero ou um valor positivo' if permitir_zero else 'um valor positivo'
        raise ValueError(f'Quantidade: use {minimo} até 100000, com até 3 casas decimais.') from None

def campos(data):
    nome = texto(data.get('nome'), 'Nome')
    categoria, unidade, local = data.get('categoria'), data.get('unidade'), data.get('local')
    if categoria not in CATEGORIAS or unidade not in ('un', 'kg', 'L') or local not in LOCAIS:
        raise ValueError('Selecione categoria, unidade e local válidos.')
    try:
        validade = date.fromisoformat(data.get('validade', '')).isoformat()
    except (ValueError, TypeError):
        raise ValueError('Informe uma data de validade válida.') from None
    return nome, categoria, unidade, validade, local

class Estoque:
    def __init__(self, path):
        self.path = str(path)
        with closing(self.conectar()) as db:
            db.executescript(Path(__file__).with_name('schema.sql').read_text())
            # Migração idempotente: preservar a unidade das saídas antigas.
            db.execute('BEGIN IMMEDIATE')
            try:
                columns = {r['name'] for r in db.execute('PRAGMA table_info(movimentos)')}
                if 'unidade' not in columns:
                    db.execute('ALTER TABLE movimentos ADD COLUMN unidade TEXT')
                db.execute('UPDATE movimentos SET unidade=(SELECT unidade FROM alimentos WHERE id=alimento_id) WHERE unidade IS NULL')
                db.commit()
            except Exception:
                db.rollback()
                raise

    def conectar(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        return db

    def adicionar(self, data):
        nome, categoria, unidade, validade, local = campos(data)
        qtd = quantidade(data.get('quantidade'))
        with closing(self.conectar()) as db, db:
            cursor = db.execute('INSERT INTO alimentos(nome,categoria,unidade,validade,local,quantidade_mil) VALUES(?,?,?,?,?,?)', (nome,categoria,unidade,validade,local,qtd))
            return cursor.lastrowid

    def editar(self, item_id, data):
        nome, categoria, unidade, validade, local = campos(data)
        with closing(self.conectar()) as db, db:
            db.execute('BEGIN IMMEDIATE')
            item = db.execute('SELECT * FROM alimentos WHERE id=?', (item_id,)).fetchone()
            if not item:
                raise LookupError('Alimento não encontrado.')
            # Não sobrescrever uma saída realizada enquanto o formulário estava aberto.
            if ('quantidade_anterior_mil' in data and
                    str(data['quantidade_anterior_mil']) != str(item['quantidade_mil'])) or (
                    'unidade_anterior' in data and data['unidade_anterior'] != item['unidade']):
                raise ValueError('O estoque mudou. Feche a edição, atualize a página e tente novamente.')
            qtd = quantidade(data['quantidade'], permitir_zero=True) if 'quantidade' in data else item['quantidade_mil']
            changed = qtd != item['quantidade_mil'] or unidade != item['unidade']
            db.execute('UPDATE alimentos SET nome=?,categoria=?,validade=?,local=?,quantidade_mil=?,unidade=? WHERE id=?',
                       (nome,categoria,validade,local,qtd,unidade,item_id))
            if changed:
                db.execute('INSERT INTO ajustes(alimento_id,quantidade_anterior_mil,quantidade_nova_mil,unidade_anterior,unidade_nova) VALUES(?,?,?,?,?)',
                           (item_id,item['quantidade_mil'],qtd,item['unidade'],unidade))

    def movimentar(self, item_id, data):
        qtd = quantidade(data.get('quantidade'))
        tipo = data.get('tipo')
        if tipo not in ('consumo', 'desperdicio'):
            raise ValueError('Tipo de movimentação inválido.')
        motivo = texto(data.get('motivo'), 'Motivo', 200) if tipo == 'desperdicio' else ''
        with closing(self.conectar()) as db, db:
            # A transação impede duas baixas simultâneas de ultrapassar o saldo.
            db.execute('BEGIN IMMEDIATE')
            item = db.execute('SELECT quantidade_mil,unidade FROM alimentos WHERE id=?', (item_id,)).fetchone()
            if not item:
                raise LookupError('Alimento não encontrado.')
            if qtd > item['quantidade_mil']:
                raise ValueError('A quantidade informada ultrapassa o saldo disponível.')
            db.execute('UPDATE alimentos SET quantidade_mil=quantidade_mil-? WHERE id=?', (qtd,item_id))
            db.execute('INSERT INTO movimentos(alimento_id,tipo,quantidade_mil,motivo,unidade) VALUES(?,?,?,?,?)', (item_id,tipo,qtd,motivo,item['unidade']))

    def painel(self, hoje=None):
        hoje = hoje or date.today()
        with closing(self.conectar()) as db:
            itens = [dict(r) for r in db.execute('SELECT * FROM alimentos ORDER BY validade,id')]
            movimentos = [dict(r) for r in db.execute('SELECT m.*,a.nome FROM movimentos m JOIN alimentos a ON a.id=m.alimento_id ORDER BY m.id DESC')]
            ajustes = [dict(r) for r in db.execute('SELECT j.*,a.nome FROM ajustes j JOIN alimentos a ON a.id=j.alimento_id ORDER BY j.id DESC')]
        for item in itens:
            dias = (date.fromisoformat(item['validade']) - hoje).days
            item['dias'] = dias
            item['situacao'] = 'Esgotado' if item['quantidade_mil'] == 0 else ('Vencido' if dias < 0 else ('Vence em breve' if dias <= 3 else 'No prazo'))
        resumo = {u: {'consumo': 0, 'desperdicio': 0} for u in ('un','kg','L')}
        for mov in movimentos:
            resumo[mov['unidade']][mov['tipo']] += mov['quantidade_mil']
        return {'alimentos': itens, 'movimentos': movimentos, 'resumo': resumo, 'hoje': hoje.isoformat(), 'ajustes': ajustes}

