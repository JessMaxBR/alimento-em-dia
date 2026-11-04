PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS alimentos (
 id INTEGER PRIMARY KEY,
 nome TEXT NOT NULL CHECK(length(trim(nome)) BETWEEN 1 AND 80),
 categoria TEXT NOT NULL,
 unidade TEXT NOT NULL CHECK(unidade IN ('un','kg','L')),
 quantidade_mil INTEGER NOT NULL CHECK(quantidade_mil >= 0),
 validade TEXT NOT NULL,
 local TEXT NOT NULL,
 criado_em TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS movimentos (
 id INTEGER PRIMARY KEY,
 alimento_id INTEGER NOT NULL REFERENCES alimentos(id),
 tipo TEXT NOT NULL CHECK(tipo IN ('consumo','desperdicio')),
 quantidade_mil INTEGER NOT NULL CHECK(quantidade_mil > 0),
 motivo TEXT NOT NULL DEFAULT '',
 criado_em TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_validade ON alimentos(validade);
CREATE INDEX IF NOT EXISTS idx_movimento_alimento ON movimentos(alimento_id);
