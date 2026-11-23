# Pesquisa de skills públicas e referências técnicas

Pesquisa feita em 23 de novembro de 2026 em repositórios com materiais em inglês, chinês, espanhol e indonésio. A identidade visual vem da skill local `palito youtube`. As fontes abaixo informaram decisões de direção, sincronismo e checagem.

## Skills públicas consultadas

| Skill | Prática aproveitada no Palito Codex |
| --- | --- |
| [stickman-video, de nispa](https://github.com/nispa/stickman-video/blob/main/SKILL.md) | Encaixar a encenação em uma locução gravada e usar marcações pontuais para acontecimentos ligados à fala. |
| [stick-motion, de cafermutluozkan](https://github.com/cafermutluozkan/stick-motion/blob/main/SKILL.md) | Fixar o pé de apoio no espaço da cena e calcular a pose em função do tempo. |
| [stick-figure-film, de lauroguedes](https://github.com/lauroguedes/stick-figure-film-skill) | Usar quadros amostrados para conferir poses, enquadramentos e continuidade antes da exportação completa. |
| [explainer-video, de lubomier](https://github.com/lubomier/explainer-video-skill/blob/main/explainer-video/SKILL.md) | Especificar fala, cenário, ação, objetos e câmera por plano e mostrar visualmente o conceito explicado. |
| [hand-drawn-explainer-video-nikola, de hi-nikola](https://github.com/hi-nikola/hand-drawn-explainer-video-nikola) | Compartilhar entre elementos vetoriais, gráficos e legenda a linha do tempo da narração real. |
| [anything2explainer, de Vincentwei1021](https://github.com/Vincentwei1021/anything2explainer/blob/main/SKILL.md) | Organizar os planos em cenas programáveis que possam ser conferidas e corrigidas separadamente. |
| [codex-motions-movie, de silenveritas](https://github.com/silenveritas/codex-motions-movie) | Referência em indonésio para continuidade visual de personagens entre cenas em uma produção vertical. |
| [edicion-video, de jalvarez-tech](https://github.com/jalvarez-tech/video-creator-producto/blob/main/manuales/edicion-video/SKILL.md) | Referência em espanhol para escolher o movimento pela intenção do plano e manter a voz à frente da mixagem. |

## Documentação técnica e pedagógica

- Para composição em React, veja as [skills oficiais do Remotion](https://github.com/remotion-dev/skills) e a documentação de [quadro atual](https://www.remotion.dev/docs/use-current-frame).
- Para medição de mídia, detecção de pausas e verificação das trilhas exportadas, consulte [FFprobe](https://ffmpeg.org/ffprobe.html) e [`silencedetect` no FFmpeg](https://ffmpeg.org/ffmpeg-filters.html#silencedetect).
- Se um episódio se beneficiar de alinhamento automático de palavra em uma máquina compatível, confira requisitos, idioma e limitações do [WhisperX](https://github.com/m-bain/whisperX).
- O princípio de apresentar uma informação visual junto à explicação correspondente orienta o disparo de eventos na fala. A sinalização e a coerência ajudam a escolher o que destacar e o que retirar do plano. [Mayer e Fiorella, The Cambridge Handbook of Multimedia Learning](https://www.cambridge.org/core/books/abs/cambridge-handbook-of-multimedia-learning/principles-for-reducing-extraneous-processing-in-multimedia-learning/F29A19FCD34C542806F736E0661C05F5)
