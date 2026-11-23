---
name: palito-youtube
description: Cria e revisa storyboards, animatics e vídeos explicativos com personagens palito sem boca. Use para encenar roteiros, sincronizar gestos com locução, estudar uma referência quadro a quadro ou produzir episódios em lote com a fábrica local. Inclui 40 personagens, cenários em papel creme e Kraft, render em MP4 e revisão técnica.
---

# Palito YouTube

Use a [fábrica de episódios](./fabrica-palito/GUIA.md) para produzir vídeos horizontais a partir de um manifesto editável. Use o [renderizador PyCairo](./references/producao-local.md) quando a cena precisar de desenho ou comportamento próprio. Se o pedido for só de roteiro ou storyboard, entregue um mapa com fala, ação, objeto, câmera e consequência visível.

## Direção e produção

1. Escolha uma ação que demonstre a fala. Sustente o mesmo objeto entre planos quando ele passa de mão ou muda de estado. Use olhos, sobrancelhas e posição do corpo para atuar. O elenco não tem boca. [Direção visual](./references/direcao-visual.md)
2. Separe papel creme para apresentação e gráficos, papel Kraft para situações encenadas. Pode trocar de papel com uma mão puxando a folha quando a transição ajudar a leitura. Câmera e pontos de contato acompanham a ação. [Câmera e transições](./references/camera_and_transitions_guide.md)
3. Se houver locução, use a duração da faixa inteira e associe palavras importantes aos quadros de ação. Para síntese, use a voz pedida e guarde as marcas da mesma tomada. Se o usuário já tiver áudio, o roteiro, a gravação e as marcas precisam corresponder. [Sincronismo e entrega](./references/sincronismo-e-entrega.md)
4. Faça uma prova ao redor dos contatos e das trocas de cena. Depois de exportar, decodifique o MP4 inteiro e confira as pranchas do arquivo final. O relatório automático aponta regiões escuras, estáticas e níveis de áudio para revisão. Confira intenção, fluidez e inteligibilidade no trecho correspondente.

## Fábrica local

O manifesto usa um palco de 960 × 540. A saída padrão é 1920 × 1080 a 60 fps. Com `exposicao: 2`, o desenho avança geralmente a cada dois quadros e a contagem recomeça nas chaves de animação. `@palavra` e `@palavra#2` localizam a palavra dentro do plano. A opção `--mudo` cria um animatic e estima os tempos quando a gravação ainda não existe.

- Use `fabrica.py novo` para abrir um episódio a partir de parágrafos. Edite seus planos e use `prova` para conferir um quadro. `produzir` exporta um ou mais episódios. `revisar` gera uma prancha de quadros e `qa.json`. [Comandos e campos do manifesto](./fabrica-palito/GUIA.md)
- Use `tipo: elenco` com o número, alias ou nome completo de um dos 40 personagens. Um contato prende a âncora do punho ao objeto durante o intervalo. Confira o ângulo dos dedos e o encaixe do acessório visualmente. [Catálogo do elenco](./references/character_catalog_30.md)
- Para “quadro a quadro”, rode `analisar.py` para medir todos os PTS e a diferença de luminância. Use `--tira` para examinar quadros consecutivos perto de ações e cortes. Informe resolução, limiar e quais momentos passaram por inspeção visual. [Análise de referência](./fabrica-palito/GUIA.md#examinar-outra-referência)

Para ajustar uma prova em Python com voz, passe `--audio` e, se disponíveis, `--marcas`. Para uma prova muda, use `--duracao 6 --quadro 240` no [exemplo do circuito](./assets/circuito.py). Para um animatic editável por manifesto, veja a [entrega no posto](./fabrica-palito/exemplos/entrega/episodio.json). A documentação complementar reúne práticas de direção e sincronização de outros projetos. [Referências técnicas](./references/pesquisa.md)
