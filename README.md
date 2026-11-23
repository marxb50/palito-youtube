# Palito YouTube

Skill em português para fazer vídeos explicativos com palitinhos sem boca. A fábrica local gera MP4 em 1080p a 60 fps e guarda a direção do episódio em JSON. Também acompanha personagens, movimento de câmera, contatos entre mãos e objetos e mudanças sincronizadas com a fala. [Ler a skill](palito-youtube/SKILL.md) · [Guia da fábrica](palito-youtube/fabrica-palito/GUIA.md)

## Faça uma prova

Use Linux, macOS ou WSL com Python 3.10+, PyCairo, Pillow, FFmpeg com libx264/AAC e FFprobe. Para gerar uma locução neural, instale também `edge-tts` com suporte a marcas de palavra. Você pode usar a fábrica com sua própria gravação.

```bash
git clone https://github.com/marxb50/palito-youtube.git
cd palito-youtube

python3 -B palito-youtube/fabrica-palito/fabrica.py produzir \
  palito-youtube/fabrica-palito/exemplos/entrega --mudo --tamanho 960x540
python3 -B palito-youtube/fabrica-palito/fabrica.py revisar \
  palito-youtube/fabrica-palito/exemplos/entrega --mudo
```

Essa prova leva seis segundos. Ela acompanha a entrega de um recibo, do primeiro movimento do frentista à hora em que o cliente segura o papel. O MP4 mudo fica na pasta do exemplo. As pranchas e o relatório ficam em `producao/` ao lado do vídeo. [Exemplo editável](palito-youtube/fabrica-palito/exemplos/entrega/episodio.json)

Para usar a skill em outro projeto, copie a pasta interna `palito-youtube` inteira para a pasta de skills do seu agente. Ela inclui os scripts, a fábrica e o catálogo com quarenta personagens. [Catálogo](palito-youtube/references/character_catalog_30.md)
