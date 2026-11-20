# Catálogo de cenas do estúdio

O vídeo é montado a partir de `video.json`. Cada cena tem `type`, `narration` (texto falado, pt-BR)
e os campos do tipo. Campos opcionais em toda cena: `highlight` (palavras pintadas de destaque no
texto e nas legendas), `emoji`, `sfx` (`whoosh`, `pop`, `ding`, `riser`, `boom` ou null),
`palette` (troca a paleta só nesta cena).

| type | Campos | O que aparece |
|---|---|---|
| `hook` | `text` (até 7 palavras) | Palavras batendo na tela uma a uma, câmera tremendo, emoji gigante. Para o gancho. |
| `statement` | `title`, `subtitle?` | Título grande com marca-texto + subtítulo + emoji. |
| `stat` | `value` (número), `prefix?` ("R$ "), `suffix?` ("%", " mil", "x"), `decimals?`, `label` | Número contando de 0 até o valor dentro de um anel que enche, confete no fim. |
| `list` | `title`, `items` (até 4 `{emoji, text}`) | Cartões coloridos entrando alternados da esquerda e da direita. |
| `compare` | `title?`, `left` e `right` (`{title, emoji, items[até 3]}`) | Duas colunas (ex.: "Lá fora" × "Brasil") com selo VS girando. |
| `journey` | `from` `{flag, label}`, `to` `{flag, label}`, `text` | Bandeira de origem → bandeira do Brasil, com emoji viajando num arco. Ideal para "chegando ao Brasil". |
| `steps` | `title`, `steps` (até 4 textos curtos) | Passo a passo numerado, cada passo pulando na tela. |
| `question` | `text` | Pergunta grande com o emoji (ou "?") balançando. |
| `reveal` | `teaser`, `reveal` | Frase de suspense e depois a resposta saindo do desfoque com confete. |
| `cta` | `text`, `subtext?` (texto do botão) | Chamada final com botão vermelho pulsando e sino. |

Campos globais de `video.json`: `palette` (`neon`, `sunset`, `ocean`, `candy`, `lime`, `fire`),
`voice` (`pt-BR-AntonioNeural`, `pt-BR-FranciscaNeural` ou `pt-BR-ThalitaMultilingualNeural`),
`rate` (velocidade da voz, ex. `"+10%"`), `music` (arquivo de `/music`, ou null) e `music_volume`.

Exemplo:

```json
{
  "palette": "neon",
  "voice": "pt-BR-AntonioNeural",
  "rate": "+12%",
  "music": null,
  "scenes": [
    {"type": "hook", "text": "O Japão paga pra você dormir", "highlight": ["dormir"], "emoji": "😴", "sfx": "boom",
     "narration": "No Japão tem gente pagando pra dormir. E não é hotel."},
    {"type": "stat", "value": 300, "prefix": "+", "suffix": "%", "label": "buscas em 6 meses", "emoji": "📈", "sfx": "riser", "palette": "sunset",
     "narration": "As buscas por isso cresceram trezentos por cento em seis meses."},
    {"type": "journey", "from": {"flag": "🇯🇵", "label": "Japão"}, "to": {"flag": "🇧🇷", "label": "Brasil"}, "text": "Ainda ninguém faz aqui", "highlight": ["ninguém"], "emoji": "✈️", "sfx": "whoosh",
     "narration": "E aqui no Brasil quase ninguém faz isso ainda."},
    {"type": "cta", "text": "Quer a próxima antes de todo mundo?", "subtext": "Segue o canal", "emoji": "🔔", "sfx": "ding",
     "narration": "Segue pra ver a próxima tendência antes de todo mundo."}
  ]
}
```

Para uma ideia visual que nenhum tipo cobre, a produção pode criar um tipo novo só para aquele
vídeo com `tools/custom-studio.sh` (cópia do estúdio em React/Remotion dentro da pasta do vídeo).
