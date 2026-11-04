# Diagramas complementares

Os blocos Mermaid podem ser visualizados no GitHub. Os diagramas de classes, sequência e atividade estão em projeto.md.

## Casos de uso UML

![Diagrama de casos de uso](casos_de_uso.svg)

O ator interage com seis casos de uso dentro do limite do sistema. Desperdício exige motivo como regra de validação.

## Mapa funcional complementar

Este fluxograma representa o ator e as funcionalidades; não usa a notação gráfica formal de casos de uso UML.

```mermaid
flowchart TD
U[Usuário doméstico ou avaliador] --> C[Cadastrar lote]
U --> E[Editar metadados]
U --> Q[Consultar estoque e alertas]
U --> S[Registrar saída]
U --> R[Consultar histórico e relatório]
S --> CO[Consumo]
S --> D[Desperdício com motivo]
```

| Caso | Pré-condição | Resultado / exceção |
|---|---|---|
| Cadastrar lote | Formulário aberto | Novo lote; rejeita campos inválidos |
| Editar lote | Lote existente | Metadados atualizados; unidade imutável |
| Consultar | Página aberta | Busca, filtro e alertas |
| Registrar saída | Lote com saldo | Saldo reduzido e histórico; rejeita excesso |
| Consultar relatório | Página aberta | Totais separados por unidade e histórico |

## Entidades e relacionamentos

```mermaid
erDiagram
ALIMENTOS ||--o{ MOVIMENTOS : possui
ALIMENTOS {
 int id PK
 string nome
 string categoria
 string unidade
 int quantidade_mil
 string validade
 string local
 string criado_em
}
MOVIMENTOS {
 int id PK
 int alimento_id FK
 string tipo
 int quantidade_mil
 string motivo
 string criado_em
}
```

## Navegação e mensagens

```mermaid
flowchart TD
P[Painel: estoque e alertas] --> C[Formulário de cadastro ou edição]
P --> S[Formulário de saída]
C --> V{Dados válidos?}
S --> V
V -->|Sim| P
V -->|Não| E[Mensagem no formulário]
E --> V
P --> H[Histórico e totais na mesma página]
```

Cancelar retorna ao painel sem gravação. Durante envio o botão fica desativado. Saldo insuficiente mostra mensagem e preserva o estoque; desperdício exige motivo. O código da interface em static/ é o protótipo funcional. Não foi realizado estudo formal de usabilidade.
