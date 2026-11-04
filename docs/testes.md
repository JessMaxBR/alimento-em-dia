# Verificação e validação

Execute `python3 -m unittest discover -s tests -v` na pasta do projeto. O resultado desta revisão está em resultado_testes_atual.txt. Os testes utilizam bases temporárias e não alteram o banco online.

Os 16 testes originais também foram executados pela estudante em Python 3.12 no PythonAnywhere, com OK, conforme captura fornecida em 04/11/2026. A captura da página confirma sua abertura no endereço público. Isso não certifica todas as operações da hospedagem nem substitui as cinco avaliações.

A revisão inclui testes WSGI de arquivos públicos/privados, criação, token, saída, rejeição de saldo insuficiente e persistência entre instâncias do modelo. A sintaxe JavaScript é verificada com node --check static/app.js.

## Registro manual a preencher

| Cenário | Esperado | Resultado observado / evidência |
|---|---|---|
| Cadastrar lote e atualizar | Registro persiste | Preencher |
| Editar validade | Alerta acompanha nova data | Preencher |
| Consumir 0,5 de 2 kg | Saldo 1,5 kg | Preencher |
| Consumir acima do saldo | Erro e saldo preservado | Preencher |
| Desperdiçar com motivo | Histórico e total atualizados | Preencher |
| Saída até zero | Situação esgotado | Preencher |
| Abrir no celular | Interface utilizável | Preencher |

Os dados fictícios do exemplo não comprovam redução real do desperdício. Registre apenas resultados efetivamente observados.
