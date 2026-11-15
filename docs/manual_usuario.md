# Manual do usuário — Alimento em Dia

## Acessar

Abra https://jessicakelenmaximiano.eu.pythonanywhere.com/ no navegador. A demonstração compartilha os registros entre visitantes. Use alimentos fictícios. O aplicativo local tem outro banco.

## Cadastrar

Clique em Cadastrar alimento. Informe nome, categoria, local, quantidade positiva, unidade e validade. Salve. Um lote representa uma compra com a mesma validade; compras diferentes podem gerar novos lotes. Valores decimais admitem até três casas.

## Consultar e editar

Pesquise pelo nome e selecione a situação. A lista é ordenada por validade. Editar permite corrigir nome, categoria, local, validade, quantidade atual e unidade. Informe o saldo que existe agora; não há conversão automática entre unidades. As saídas anteriores mantêm sua unidade original. Mudanças de saldo ou unidade aparecem em Histórico de correções, sem contar como consumo ou desperdício. Se outra pessoa alterar o saldo durante a edição, atualize a página e abra novamente o formulário. Não há exclusão nem estorno nesta versão.

## Registrar saída

Clique em Registrar saída no alimento. Selecione Consumo ou Desperdício e a quantidade. Para desperdício, informe o motivo. Confirme e confira o saldo. Quantidade maior que o saldo é rejeitada. Cancelar fecha sem gravar.

## Alertas

Vencido: validade anterior à data do servidor. Vence em breve: hoje até três dias à frente. No prazo: mais de três dias. Esgotado: saldo zero. São alertas das datas cadastradas, não avaliações de segurança alimentar. Com o filtro Em estoque, os lotes esgotados deixam de aparecer.

## Relatório e histórico

Role a página para ver as movimentações e os totais. Quilos, litros e unidades são somados separadamente. O sistema não calcula valor financeiro ou redução real de desperdício.

## Exemplo de teste

Cadastre Arroz, Grãos e massas, Despensa, 2 kg, validade futura. Consuma 0,5 kg e confira saldo 1,5 kg. Tente consumir 2 kg: deve aparecer erro e o saldo deve permanecer igual. Registre desperdício de 0,5 kg com motivo Teste: o saldo deve ficar 1 kg. Atualize a página e confira a persistência.

## Problemas comuns

Se aparecer Atualize a página antes de salvar, atualize e repita a operação. Se o site estiver desativado, a responsável deve renovar a hospedagem. Se os dados mudarem, outro visitante pode ter alterado o estoque compartilhado. Registre a mensagem e uma captura de tela para relatar um erro.
