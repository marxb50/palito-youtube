# Sincronismo e entrega

## Medição e alinhamento

Com a locução disponível, execute a partir da raiz da skill e direcione o resultado para a pasta de trabalho do episódio. O utilitário usa Python 3, FFmpeg e FFprobe e seleciona a primeira faixa de áudio.

```bash
python3 scripts/inspecionar_audio.py "/caminho/para/locucao.wav" > "/caminho/do/episodio/audio-medido.json"
```

`duracao_s` e `amostras_por_canal` medem a faixa decodificada. Para montar a imagem, divida `amostras_apresentadas` por `stream_audio.taxa_amostragem_hz`. Essa contagem respeita a duração sinalizada quando o último bloco AAC de um MP4/M4A contém preenchimento. O tempo zero é a primeira amostra decodificada. Se a faixa vier de um vídeo a ser corrigido, confira o deslocamento dessa faixa em relação à imagem antes de transferir as marcas. Ajuste `--ruido-db` e `--pausa-minima` se o piso de ruído ou o ritmo exigir. Os intervalos em `pausas` indicam regiões de escuta. Localize palavras pela tomada correspondente, por alinhamento local ou por conferência manual. Em uma faixa com música, pode haver fala pausada sem silêncio detectável.

Monte um mapa de planos em planilha, Markdown ou no formato do motor. Num projeto existente, ajuste o mapa que o render já consome. Use uma base de tempo comum para áudio, pose, câmera, elementos na tela, legenda e efeitos.

| Plano | Intervalo | Fala/âncora | Ação e foco | Câmera/som |
| --- | --- | --- | --- | --- |
| 02 | 00:02.250–00:05.000 | “separe uma ficha” em 00:03.100, conferido na voz | Mão fecha na ficha em “ficha”, ficha acompanha a mão | Plano médio, toque curto no contato |

- Distinga âncoras **conferidas**, **estimadas** e **provisórias**. Compare legenda ou transcrição com a voz em trechos do início, meio e fim antes de confiar nelas. Para palavras repetidas, restrinja a busca ao trecho e confira a ocorrência.
- Se cada trecho tiver uma tomada separada, use a posição real de inserção de cada clipe na faixa montada. Some esse deslocamento às marcas locais depois de ajustar respiros e pausas. Confira a primeira palavra do segundo trecho e a última do episódio para detectar desvio acumulado.
- Converta limites para quadros uma vez, com início inclusivo e fim exclusivo. A 60 fps, 00:02.250 começa no quadro 135 e 00:05.000 começa no 300. Valide que os planos tenham duração positiva, que o fim de um coincida com o início do próximo onde houver corte contínuo e que as âncoras estejam dentro do plano. Transições sobrepostas devem ter intervalo explícito.
- Cubra a gravação até o último som útil. Para a duração sem cauda, calcule a quantidade de quadros arredondando para cima `duração × fps`. Registre qualquer extensão de fechamento separadamente.

## Composição e render

Para um episódio novo em PyCairo, o [renderizador incluído](producao-local.md) usa o mesmo desenho no quadro de prova e no MP4. As orientações de composição e mixagem a seguir também se aplicam a projetos existentes.

- Se houver um projeto compatível, use seu pipeline. Para produção local do canal, confira `python3 -c 'import cairo'` e a disponibilidade de FFmpeg/FFprobe. Use `scripts/puppet_30.py` para o elenco e `scripts/scenes_and_props.py` para cenários, objetos e prancheta. Importe a biblioteca na composição do episódio com um caminho relativo ao projeto. Os desenhos locais usam como base 1920×1080, então refaça a distribuição de tela ao mudar a proporção.
- `scripts/stickman_engine.py` contém uma demonstração de sete cenas de investimento. Confira o código como exemplo de desenho e codificação, e componha cada episódio novo com os próprios planos. Separe a pose, câmera e objetos pelo tempo local do plano. O analisador antigo calcula cortes estimados pelo tamanho do texto e pelas pausas, o que pode gerar intervalos inválidos com locuções curtas.
- Se as bibliotecas do canal estiverem indisponíveis, crie uma composição vetorial simples com PyCairo ou Canvas/SVG. Use Remotion quando o projeto já tiver esse motor, ou quando a produção pedir uma timeline editável em React. Construa poses a partir do quadro e extraia amostras pontuais sem renderizar o episódio inteiro. Mantenha semente e estado determinísticos para reproduzir correções.
- Preserve a locução como faixa principal. Se houver efeitos ou música, mantenha-os em faixas separadas até a mixagem, baixe o fundo onde houver fala e ouça palavras encobertas ou picos. Escolha a entrada e saída da mistura pelo mesmo relógio da imagem.

Se a composição já exportou vídeo mudo e a locução começa no quadro zero, este exemplo gera MP4 H.264/AAC. Garanta que `imagem.mp4` cubra toda a fala, inclusive o último quadro, antes de aplicar `-shortest`.

```bash
ffmpeg -hide_banner -i imagem.mp4 -i locucao.wav \
  -map 0:v:0 -map 1:a:0 -c:v libx264 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -af apad -shortest -movflags +faststart final.mp4

ffprobe -v error -show_entries \
  'stream=codec_type,codec_name,width,height,avg_frame_rate,nb_frames,channels,duration:format=duration' \
  -of json final.mp4
ffmpeg -v error -xerror -i final.mp4 -map 0:v:0 -map 0:a:0 -f null -
```

## Conferência

- Confira o arquivo exportado. Verifique codec, faixa de voz, resolução, fps e duração em relação ao mapa e à locução. Faça a leitura completa para detectar erros de decodificação.
- Inspecione no arquivo final as trocas de cenário, as poses de contato e as telas com números ou texto. Ouça o começo, as palavras que disparam ações e a última frase quando houver reprodução disponível. Meça o pico no áudio AAC já codificado se houver distorção ou pouca margem no mix. Ao remisturar, substitua a faixa, exporte novamente e refaça a conferência na cópia que será entregue.
- Na revisão, registre o que foi inspecionado visualmente, o que foi ouvido e o que foi medido por ferramenta. Uma folha de quadros permite conferir o enquadramento e o contato. Para avaliar fluidez e inteligibilidade, use a reprodução do trecho com som.
- Entregue o MP4 ou o material solicitado com um caminho utilizável. Se o episódio foi pedido editável, inclua a composição e seu mapa de planos com os ativos necessários.
