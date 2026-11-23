# Produção local por planos

Use este fluxo para a demo ou o MP4 final quando o episódio precisar de uma composição nova. São necessários Python 3.10+, PyCairo, FFmpeg com libx264/AAC e FFprobe. A voz sintética também usa o pacote `edge-tts` com suporte a marcas por palavra e acesso à rede. Um áudio gravado entra diretamente no render.

Nos comandos, `skill` aponta para a pasta que contém o `SKILL.md`. Guarde roteiro, composição, tomadas e marcas juntos quando o episódio precisar ser reaberto. Pilotos e folhas de contato podem ficar na pasta de trabalho temporária.

## Do roteiro à tomada

Com a síntese escolhida pelo usuário, gere um WAV e os tempos das palavras a partir da mesma leitura. O script reconhece o ambiente do `edge-tts` quando instalado pelo pipx. A mesma pasta de tomada pode ser reutilizada ao refazer as imagens. Uma mudança no texto, na voz ou no ritmo usa uma pasta de tomada nova. O exemplo a seguir parte de uma pasta de episódio nova. [Projeto edge-tts](https://github.com/rany2/edge-tts)

```bash
skill="$PWD/palito-youtube"
ep="episodios/circuito"
mkdir -p "$ep"
cp "$skill/assets/circuito.py" "$ep/cenas.py"
printf '%s\n' 'A lâmpada está apagada. Observe o contato. Um toque fecha o circuito e a lâmpada acende.' > "$ep/roteiro.txt"
python3 "$skill/scripts/gerar_locucao.py" "$ep/roteiro.txt" "$ep/voz" --voz pt-BR-ThalitaNeural
```

O WAV e o JSON ficam em `voz/locucao.wav` e `voz/palavras.json`. Os tempos contam desde a primeira amostra da tomada. Para gravação externa, use o arquivo recebido em `--audio`. Marcas correspondentes podem ser fornecidas em segundos no formato abaixo. Uma legenda por frase orienta o corte entre ideias. Confira o instante de contato pela palavra da gravação quando a ação exigir maior precisão.

```json
{"palavras": [{"texto": "fecha", "inicio_s": 4.0, "fim_s": 4.31}]}
```

## Da tomada ao vídeo

```bash
python3 "$skill/scripts/renderizar.py" "$ep/cenas.py" "$ep/prova.png" \
  --audio "$ep/voz/locucao.wav" --marcas "$ep/voz/palavras.json" --quadro 0
python3 "$skill/scripts/renderizar.py" "$ep/cenas.py" "$ep/circuito.mp4" \
  --audio "$ep/voz/locucao.wav" --marcas "$ep/voz/palavras.json"
```

Por padrão, o último quadro cobre o fim do áudio. Para um pedido de um minuto, passe `--duracao 60`. A 60 fps, isso produz exatamente 3.600 quadros. Se o alvo cair entre dois quadros, o comando informa a duração mais próxima que cubra a fala. Se a voz passar do limite, ajuste o roteiro, o ritmo ou um silêncio identificado na gravação. Se sobrar tempo, use-o para uma ação demonstrativa ou um fecho com intenção. Uma tomada curta pode precisar de mais conteúdo para sustentar o minuto.

Para testar somente a atuação, o exemplo aceita `--duracao 6` sem áudio nem marcas. Use `--tamanho 960x540` para um piloto rápido. A saída padrão é 1920×1080/60. A composição recebe o tamanho real, de modo que um pedido vertical pode ter enquadramento próprio. Para comparar dois renders do mesmo arquivo, gere as versões em caminhos diferentes. Ao reutilizar o caminho, o novo resultado substitui o anterior somente após a conclusão da escrita e, no MP4, da verificação.

## Como escrever outro episódio

Use [a composição do circuito](../assets/circuito.py) como exemplo de gesto e câmera. Use a prova muda perto de 4 s ou gere uma versão narrada com os comandos acima. Crie as ações e os objetos do novo tema. As palavras “Observe” e “fecha” pertencem ao roteiro do exemplo.

- O arquivo Python expõe `montar(tempo)`. Carregue fundos, fontes e imagens nessa função e devolva pares `(inicio_global, desenhar)`. O primeiro início é zero. Cada plano vai até o início do próximo ou até `tempo.total`, com o fim exclusivo.
- Cada função `desenhar(ctx, quadro_local)` recebe um contexto Cairo e um inteiro contado do início do plano. Calcule a pose pelo quadro recebido, inclusive quando ele for solicitado isoladamente. `tempo.fps`, `tempo.largura` e `tempo.altura` descrevem a composição. `tempo.quadro(3.1)` devolve o quadro que contém o instante 3,1 s.
- `tempo.palavra("fecha")` devolve o quadro **global** do início da palavra. Para animar dentro do plano, subtraia o quadro inicial desse plano. Em repetições, use `tempo.palavra("lâmpada", 2)` ou limite a busca com `depois_de=inicio_do_plano` (inclusivo). Uma marca ausente ou ambígua gera uma mensagem com o termo.
- Para encenar com o elenco do canal, importe `draw_puppet_30` da biblioteca indicada em [sincronismo e entrega](sincronismo-e-entrega.md). O exemplo incluso demonstra um gesto desenhado especificamente para o objeto. O dedo e o botão usam o mesmo ponto de contato. A mudança no circuito acontece no quadro da palavra “fecha”.
- O render verifica cadência, resolução, número de quadros, presença e duração do áudio e decodificação integral. Para conferir o gesto, use `--quadro` com a marca menos um, a própria marca e a marca mais um. Reveja o resultado no MP4 efetivamente exportado. Se houver uma mixagem posterior, repita a conferência no último arquivo gerado.
