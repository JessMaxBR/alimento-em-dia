# Alimento em Dia

Projeto acadêmico de controle doméstico de alimentos e validade, preparado para Jessica, RGM 39390934. Versão para publicação: 04/11/2026. Tema novo; a continuidade com o Projeto Integrador I e a aceitação acadêmica precisam ser verificadas com o tutor.

## Repositório

https://github.com/JessMaxBR/alimento-em-dia

## Acesso online

https://jessicakelenmaximiano.eu.pythonanywhere.com/

Demonstração com dados fictícios. Todos os visitantes consultam e alteram o mesmo estoque. Os registros do computador local não são transferidos automaticamente. A hospedagem gratuita exige renovação periódica no painel.

## Documentação

- [Manual do usuário](docs/manual_usuario.md)
- [Projeto e dicionário de dados](docs/projeto.md)
- [Diagramas complementares](docs/diagramas.md)
- [Instalação e hospedagem](docs/hospedagem.md)
- [Rastreabilidade das exigências](docs/entrega.md)
- [Testes](docs/testes.md)

## Abra no Mac

1. Extraia o ZIP com dois cliques e encontre a pasta `alimento_em_dia`.
2. Instale Python 3.11 ou superior, se necessário, pelo instalador oficial em https://www.python.org/downloads/macos/ (versão estável, não prévia).
3. Abra o aplicativo Terminal. Digite `cd ` (com um espaço), arraste a pasta `alimento_em_dia` para o Terminal e pressione Enter.
4. Digite `python3 app.py` e pressione Enter.
5. Abra http://127.0.0.1:8765 no Safari ou Chrome. Deixe o Terminal aberto.
6. Para encerrar, volte ao Terminal e pressione Control+C. Para reabrir, repita os passos 3 a 5.

Não é preciso instalar bibliotecas com pip. A interface precisa do servidor: abrir `index.html` diretamente não executa o sistema.

Se aparecer “command not found”, instale Python e reabra o Terminal. Se aparecer “Address already in use”, use `PORT=8766 python3 app.py` e abra http://127.0.0.1:8766. Se houver outro erro, guarde a mensagem completa para diagnóstico.

## Primeiro teste

Cadastre um lote de arroz com 2,5 kg e validade futura. Registre consumo de 0,5 kg: o saldo deve ficar em 2 kg. Registre desperdício de 0,25 kg com um motivo: o saldo deve ficar em 1,75 kg. Busque “arroz” e confira o relatório e o histórico. Esses registros são exemplos de teste, não resultados de uma pesquisa.

## Manual de uso

- Cadastrar alimento: preencha nome, categoria, local, quantidade, unidade e validade.
- Cada lote tem uma validade. Compras com validades diferentes devem ter cadastros separados.
- Editar: corrige nome, categoria, local e validade. Quantidade e unidade ficam bloqueadas para preservar o histórico. Novas compras são novos lotes.
- Registrar saída: escolha consumo ou desperdício; informe quantidade. Desperdício exige motivo.
- Quantidade aceita até três casas decimais. O saldo não pode ficar negativo.
- Alertas: vencido = data anterior a hoje; vence em breve = hoje até três dias à frente; no prazo = mais de três dias. Saldo zero aparece como esgotado.
- Busca por nome e filtros ajudam a localizar os lotes; todos são ordenados pela validade.
- O relatório soma consumo e desperdício separadamente em kg, L e unidades. Ele não estima economia nem comprova redução de desperdício.
- Cancelar fecha o formulário sem salvar. Confira as saídas antes de confirmar: esta versão não tem estorno.

## Dados e limites

Os dados ficam no arquivo `data/alimentos.db`, criado na primeira execução. Feche o sistema antes de copiar esse arquivo como backup. Não apague essa pasta se quiser manter o histórico. A versão distribuída começa vazia.

O modo local é individual. O modo hospedado é uma demonstração pública com estoque compartilhado, sem login. Não há notificações por e-mail ou API externa. O endereço 127.0.0.1 só funciona no computador onde o servidor está aberto. Para avaliação remota, cada avaliador pode baixar o código e executá-lo no próprio computador, com Python, ou operar por acesso remoto autorizado. Um link do GitHub contém código; não equivale a uma aplicação hospedada.

O servidor usa a data local do computador para os alertas e grava timestamps em UTC no banco. Os registros não incluem dados pessoais dos avaliadores. Não exponha este servidor à internet: ele foi limitado a 127.0.0.1.

## Organização MVC

- Model: `models.py` e `schema.sql` (validação, regras e SQLite).
- View: `static/index.html`, `style.css`, `app.js` (interface).
- Controller: `app.py` no modo local e `wsgi.py` no modo hospedado (rotas HTTP e respostas).
- `tests/`: testes automáticos de regras e integração HTTP.
- `docs/`: planejamento, modelagem, formulários, roteiro e pendências.

## Executar testes

Na pasta do projeto: `python3 -m unittest discover -s tests -v`.
Consulte o resultado real da execução inicial em `docs/resultado_testes.txt`. Testes automáticos não substituem testes com os cinco avaliadores nem testes visuais no seu Mac.

## GitHub e entrega

1. Crie um repositório na sua conta GitHub.
2. Envie os arquivos de código, documentação e testes, mantendo as pastas. Não envie `data/`, caches nem informações pessoais sem necessidade.
3. Dê ao tutor acesso ao repositório, conforme a orientação da faculdade.
4. Colete as cinco avaliações reais usando o formulário. Consolide as respostas em um PDF.
5. Registre as melhorias realmente realizadas, com evidências e resultados de novos testes.
6. Grave a tela com sua própria narração e o sistema em funcionamento. O roteiro está em `docs/roteiro_video.md`.
7. Anexe a documentação e informe os links do código e do vídeo no campo de entrega, conforme as instruções do tutor e o limite de 50 MB mostrado na plataforma.

## Fontes técnicas

- Python para macOS: https://www.python.org/downloads/macos/
- SQLite em Python: https://docs.python.org/3/library/sqlite3.html
- Enunciado fornecido: “Projeto Integrador Transdisciplinar em Engenharia de Software II”, Prof. Me. Artur Marques. Releia a atividade de entrega do AVA antes do envio.

## Situação da entrega

Código e documentos iniciais preparados com auxílio de IA. A estudante deve estudar, executar, revisar e adaptar o material, conforme as regras da instituição. Não há alegação de avaliações humanas, gravação ou aprovação já realizadas. Veja `docs/pendencias.md`.
