# Fábrica de episódios de palito

Peça ao Codex, por exemplo, **“Faça um episódio da fábrica sobre por que o café esfria, de um minuto, com a Thalita.”** O trabalho de direção começa escolhendo uma situação que mostre a resposta. Nesse exemplo, duas xícaras podem atravessar a mesma cena, uma com tampa e outra aberta. O manifesto guarda a fala, o gesto, o que acontece com cada objeto e a palavra que dispara a mudança.

O [exemplo de entrega no posto](exemplos/entrega/episodio.json) mostra um corte para Kraft, dois personagens do catálogo e um recibo que passa de mão. Veja como o intervalo de cada punho se sobrepõe no momento da entrega.

## Produzir um episódio

Execute os comandos a partir da pasta que contém `fabrica-palito`. A fábrica roda em Linux, macOS ou WSL com Python 3.10+, PyCairo, Pillow, FFmpeg com libx264/AAC e FFprobe. Para sintetizar uma nova tomada, use `edge-tts` com marcas de palavra e acesso à rede. Um animatic ou uma renderização com áudio local pode ser produzida offline.

1. Escreva a narração em UTF-8 com uma linha em branco entre planos. Crie a pasta do episódio. O comando distribui os parágrafos em um manifesto inicial e oferece uma composição de exemplo para editar.
2. Em `episodio.json`, substitua o livro e os gestos de exemplo por uma ação pertinente a cada fala. Defina voz e duração. Escolha um objeto que tenha estados visíveis antes e depois. Quando os desenhos locais não representarem o assunto, use a entrada de arte PNG ou acrescente a ilustração ao catálogo.
3. Faça uma prova do quadro em que o objeto muda de mãos ou de estado. Em exposições de dois quadros, confira também o quadro imediatamente anterior e o posterior. Ajuste o olhar ou o ponto de contato no manifesto.
4. Produza o MP4. O master recebe o nome da pasta. O comando mede a tomada, preserva toda a fala e verifica o arquivo codificado por decodificação completa. O mapa em `producao/mapa.json` guarda os cortes, as palavras de cada plano e o hash do master. Use `revisar` para extrair três quadros de cada plano do próprio MP4, com tempo e índice, em pranchas de até oito planos por página.

```bash
python3 -B fabrica-palito/fabrica.py novo fabrica-palito/episodios/cafe --roteiro roteiro.txt
python3 -B fabrica-palito/fabrica.py prova fabrica-palito/episodios/cafe --quadro 120 --tamanho 960x540 --saida /tmp/cafe.png
python3 -B fabrica-palito/fabrica.py produzir fabrica-palito/episodios/cafe
python3 -B fabrica-palito/fabrica.py revisar fabrica-palito/episodios/cafe
```

Para produzir uma fila de episódios, passe as pastas na ordem desejada. Para uma prévia sem som, acrescente `--mudo --tamanho 960x540`. A prévia recebe o sufixo `-animatic`. Ela usa as marcas da tomada local quando disponíveis e estima a duração de cada fala quando ainda não há gravação. O exemplo abaixo funciona offline.

```bash
python3 -B fabrica-palito/fabrica.py produzir fabrica-palito/exemplos/entrega --mudo --tamanho 960x540
python3 -B fabrica-palito/fabrica.py revisar fabrica-palito/exemplos/entrega --mudo
```

## Dirigir pelo manifesto

O palco tem **960 × 540 unidades**, com origem no canto superior esquerdo. A exportação usual dobra essas medidas para 1920 × 1080. O centro horizontal do personagem fica entre os pés. A posição de um objeto corresponde em geral ao centro da base. A lista de compras usa a borda superior, de onde o papel se desenrola.

| Campo | Uso |
| --- | --- |
| `versao`, `voz`, `ritmo` | Use a versão 1. A voz padrão é `pt-BR-ThalitaNeural`. Um valor como `"-4%"` deixa a leitura mais lenta. Mudanças de voz, ritmo ou texto criam uma tomada própria no cache. |
| `duracao_s`, `exposicao` | A duração é opcional. Sem alvo, o vídeo acompanha a faixa até o próximo quadro. A exportação interrompe com diagnóstico se a fala ultrapassar o alvo. Exposição 2 segura o desenho por dois quadros na entrega a 60 fps. Exposição 1 permite um desenho novo em cada quadro. |
| `audio`, `marcas` | Para voz humana ou uma mistura pronta, use caminhos relativos ao episódio. O JSON de marcas aceita `palavras` com `texto`, `inicio_s` e `fim_s`. Se fornecer `audio_sha256`, a fábrica confere a correspondência. Com áudio sem marcas, informe `inicio_s` em cada plano após o primeiro e use chaves numéricas. |
| `planos` | Cada plano tem `id` único, `fala`, `mundo` (`creme` ou `kraft`) e `elementos`. `entrada` aceita `corte` ou `folha`. A fala contínua determina os cortes pela primeira palavra de cada plano. Escreva os números por extenso para combinar com as marcas da voz. |
| `camera` | Use `[centro_x, centro_y, zoom]`. Uma trilha como `[[0,480,270,1],["@gaveta",515,298,1.22]]` aproxima a câmera até a palavra escolhida. |
| `elementos` | A lista segue a ordem de desenho, do fundo para a frente. Cada item tem `id`, `tipo` e `pos` no formato `[x,y,escala]`. `tela: true` fixa o item à tela, à frente da câmera. |
| `gestos`, `olhar` | Os gestos aceitam `repouso`, `abrir`, `indicar`, `pensar`, `andar`, `receber` e `surpresa`. A direção é `frente` igual a 1 ou -1. O deslocamento horizontal das pupilas usa `olhar`. |
| `toques` | Uma entrada como `{"de":"@abre","ate":1,"em":"lista","mao":"dir","offset":[0,0]}` prende a âncora do punho ao ponto na lista durante o intervalo. A mão e o objeto precisam estar no mesmo espaço de câmera. `offset` está em unidades de palco. |
| `valor`, `angulo`, `opacidade` | Use uma lista como `[1]` para valor fixo. O ângulo é em graus, a opacidade vai de zero a um. O significado de `valor` varia com o objeto. Na lista, controla o comprimento. Nos pacotes, varia de zero a seis. Na gaveta, vai da desordem à separação dos talheres. |

As trilhas também aceitam uma sequência de listas `[quando, valor…]`. Um número de 0 a 1 representa uma fração do plano. Uma marca como `"@link#2"` representa a segunda ocorrência dessa palavra **dentro da fala daquele plano**. A animação interpola entre as chaves na ordem escrita. Mantenha a posição ou o valor em duas chaves consecutivas para segurar um objeto enquanto o narrador prepara a ação.

### Elenco e objetos

- `ator` oferece os figurinos `guia`, `bia`, `lia`, `cliente`, `rapaz`, `atendente` e `padeiro`. O tipo `elenco` aceita `papel` de 1 a 40 (ou apelidos do catálogo como `"30_knight"`, `"32_businessman"`, `"34_courier"`, `"39_shopper"`) para usar os 40 bonecos Bean-Body sem boca da skill, incluindo transição de até sete quadros entre poses e até o ponto de contato (`toques`), `expressao` (`neutral`, `happy_eyes`, `determined`, `sad`), `colete: true` e acessórios de mão `prop_esq` / `prop_dir` (`squeegee`, `tire_gauge`, `magnifier`, `briefcase`, `tray`, `cane`, `grocery_bag`, `folder`).
- Há objetos para comércio e organização (`caixa`, `moeda`, `elo`, `bilhete`, `celular`, `gaveta`, `regua`, `cozinha`), cenas de atendimento (`fornada`, `balcao`, `saco`, `pao`, `pacotes`, `bandeja`, `lista`, `trigo`, `vitrine`), objetos de explicação (`livro`, `relogio`, `ficha`, `quebra_cabeca`, `arco_texto`, `placa`) e cenários de finanças/negócios (`posto`, `sedan`, `recepcao`, `cofre`, `predio`, `dinheiro`, `boleto`). O `rotulo` do celular seleciona `cadastro`, `gravar`, `produto` ou `painel`.
- Para mixar efeitos procedurais em cortes, viradas de papel e deixas de palavra usadas nas trilhas, indique `"sfx": true` ou `--sfx`. Para normalizar o volume integrado em duas passagens, indique `"lufs": -16` ou `--lufs -16`. A primeira passagem mede a faixa e a segunda aplica o alvo. O mapa registra quando a faixa não tem volume mensurável. A revisão lê o MP4 codificado e escreve `qa.json` com trechos escuros, trechos estáticos e, se houver som, o volume e pico medidos. Trechos sinalizados pedem inspeção porque a pausa pode ser intencional.
- Para usar uma imagem original do episódio, coloque o PNG na pasta e defina `{"id":"caneca","tipo":"imagem","arquivo":"caneca.png","pos":[555,357,0.6]}`. A âncora fica na base, ao centro. A imagem participa das mesmas trajetórias, escalas e contatos dos objetos vetoriais.

## Examinar outra referência

```bash
python3 -B fabrica-palito/analisar.py referencia.mp4 /tmp/medicao
python3 -B fabrica-palito/analisar.py referencia.mp4 /tmp/medicao --tira 3174 --quantidade 6
```

O primeiro comando registra todos os quadros com seus timestamps em `quadros.csv`. O segundo extrai vizinhos consecutivos da faixa original para uma prancha PNG. Os índices começam em zero. Por padrão, a medição compara quadros reduzidos a 256 × 144 e conta pixels cuja luminância variou ao menos 8 pontos de 255. O resumo agrupa as comparações por paridade e guarda os intervalos com grande mudança de imagem.
