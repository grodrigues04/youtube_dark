# youtube_dark

Todo dia, logo depois que a pesquisa das **5h** do [market_trends](../market_trends) termina, este
container escolhe um tema de cada uma das 7 listas da Parte 11 da pesquisa, produz um YouTube
Short de até 1 minuto para cada um (100% em pt-BR, para o público brasileiro) e publica no canal.

```
market_trends.researches (status completed) ──▶ research.py (root): exporta para /data/work/<data>/research
        │
        ▼
Claude "pauta" ──▶ pauta.json (7 temas, 1 por lista da Parte 11)
        │
        ▼  para cada tema, uma sessão separada do Claude:
pesquisador-youtube ─▶ roteirista ⇄ critico (até 4 rodadas) ─▶ produção (Remotion + narração pt-BR)
        ─▶ hashtags + thumbnail + titulo (em paralelo) ─▶ metadata.json + READY
        │
        ▼
publish.py (root) ──▶ YouTube (pt-BR) + youtube_dark.videos no MongoDB
```

## Como funciona

- `runner/scheduler.sh` olha o relógio a cada 30s. A partir das 05:00, uma vez por dia (lock em
  `data/state/<data>.lock`), roda `runner/run_daily.sh`. Se o computador estava desligado às 5h,
  começa assim que o container voltar (até 22h59). A cada 10 minutos ele também tenta de novo os
  uploads pendentes.
- `run_daily.sh` espera a pesquisa do dia ficar `completed` no MongoDB (desiste às 23h ou se ela
  falhar), exporta o relatório, roda a sessão de **pauta** e depois **uma sessão do Claude por
  vídeo** (`run.sh video <data> <n>`), subindo cada vídeo assim que fica pronto.
- Cada vídeo fica em `data/work/<data>/videos/<NN>/`: `tema.json`, `pesquisa-youtube.md`,
  `roteiro-vN.md` e `critica-vN.md` (histórico da discussão roteirista × crítico),
  `roteiro-final.md`, `video.json`, `props.json`, `assets/` (narração), `qa/` (frames conferidos),
  `video.mp4`, `thumbnail.jpg`, `hashtags.json`, `titulo.json`, `metadata.json` e os marcadores
  `READY` → `UPLOADED` (id do vídeo) ou `FAILED`/`UPLOAD_FAILED`.

### Agentes (`studio/agents/`, instalados em `~/.claude/agents` do container)

| Agente | Papel |
|---|---|
| `pesquisador-youtube` | Busca vídeos do tema no YouTube (pt, en e idioma de origem) com `yt-dlp`, lê detalhes e transcrições, acha a lacuna para o Brasil. |
| `roteirista` | Escreve o roteiro seguindo `prompts/gatilhos-mentais.md` (primeiros 3–8s), `prompts/regras-do-short.md` e os tipos de cena do estúdio. |
| `critico` | Exige gancho forte, recompensa rápida, algo novo a cada 2–3s, animações coloridas, pt-BR natural (sem cara de tradução), R$ e referências do Brasil; dá nota e reescritas; só aprova com nota ≥ 8 e gancho ≥ 9. |
| `hashtags` | Hashtags e tags em pt-BR coerentes com o tema. |
| `thumbnail` | Capa 1080x1920, renderizada e conferida visualmente. |
| `titulo` | Título com palavras-chave de busca em pt-BR. |

### Estúdio de vídeo (`studio/remotion/`, `studio/tools/`)

- [Remotion](https://www.remotion.dev/) (React) com uma biblioteca de cenas animadas: `hook`,
  `statement`, `stat` (número contando), `list`, `compare` (lá fora × Brasil), `journey`
  (bandeira de origem → Brasil), `steps`, `question`, `reveal`, `cta`. Fundo em gradiente animado,
  legendas sincronizadas palavra por palavra, barra de progresso, flash e confete nas viradas.
  Catálogo em `studio/prompts/catalogo-de-cenas.md`.
- `tools/prepare.py`: narração pt-BR com `edge-tts` (vozes Antonio, Francisca e Thalita), tempos
  de cada palavra para as legendas e duração das cenas; recusa vídeo acima de 58s.
- `tools/render.sh`, `tools/frames.sh` (frames para o Claude conferir), `tools/thumbnail.sh`,
  `tools/custom-studio.sh` (cena nova só para um vídeo), `tools/youtube_search.py`.
- Efeitos sonoros sintetizados com ffmpeg no build. Música de fundo é opcional: coloque mp3 com
  licença de uso no YouTube em `music/` (fora do git) e o Claude pode escolher uma.

## Segurança

O Claude lê páginas e vídeos que podem ter prompt injection. O container começa como root, com a
`MONGO_URI` e as credenciais do YouTube; `run-as-claude-user.sh` roda o Claude como `node` com
ambiente limpo (só o token do Claude). Quem fala com o MongoDB e com o YouTube são
`research.py` e `publish.py`, como root. O Claude roda com `--dangerously-skip-permissions`
porque precisa do Bash para renderizar, mas dentro do container e sem nenhum segredo além do
próprio token.

## Configuração

```bash
cp .env.example .env    # token do Claude e MONGO_URI (o mesmo Atlas do market_trends)
docker compose up -d --build
```

### Autorizar o YouTube (uma vez)

O upload usa a YouTube Data API v3 (OAuth). A senha da conta nunca fica no projeto.

1. Em https://console.cloud.google.com crie um projeto (ex.: `youtube-dark`) e ative a
   **YouTube Data API v3**.
2. **Tela de consentimento OAuth**: tipo *Externo*, preencha nome e e-mail, adicione o e-mail do
   canal como usuário de teste e depois clique em **Publicar app** (em "Teste" o token expira em
   7 dias).
3. **Credenciais → Criar credencial → ID do cliente OAuth → App para computador**. Baixe o JSON
   para esta pasta como `client_secret.json` (fica fora do git).
4. Rode no computador (abre o navegador; entre com a conta do canal e aceite o aviso de app não
   verificado):

   ```bash
   uv run --with google-auth-oauthlib python runner/auth_youtube.py client_secret.json
   docker compose up -d
   ```

Limites do YouTube que valem saber:

- **Projeto de API não verificado**: o YouTube deixa como **privados** os vídeos enviados por
  projetos que não passaram pela auditoria. Para publicar como público, peça a auditoria em
  https://support.google.com/youtube/contact/yt_api_form (enquanto isso, os vídeos sobem e ficam
  privados; dá para torná-los públicos no YouTube Studio).
- **Cota diária** (10.000 unidades por padrão): cada upload consome uma fatia grande dela, então
  7 vídeos podem passar do limite. O que não couber sobe sozinho depois que a cota renova
  (05h de Brasília). Dá para pedir aumento de cota no mesmo formulário, ou usar `VIDEO_COUNT`.
- **Thumbnail personalizada** exige o canal verificado por telefone
  (https://www.youtube.com/verify). Sem isso o vídeo sobe com a capa automática.

## Comandos úteis

```bash
# Teste do estúdio sem Claude e sem upload (narração, render, frames, thumbnail, busca)
docker exec youtube-dark /app/smoke-test.sh

# Rodar (ou retomar) os Shorts de hoje agora (pula os vídeos que já têm READY)
docker exec -e MANUAL_RUN=1 youtube-dark /app/run_daily.sh

# Produzir só um vídeo da pauta de hoje
docker exec youtube-dark /app/run.sh video $(date +%F) 3

# Subir agora os vídeos pendentes
docker exec youtube-dark /opt/runner/bin/python /app/publish.py

# Acompanhar
tail -f data/logs/$(date +%F).log data/logs/publish.log
```

`YOUTUBE_PRIVACY_STATUS` (`public`, `unlisted`, `private`) define a visibilidade dos uploads, e
`VIDEO_COUNT` quantos Shorts por dia (1 por lista da Parte 11, máximo 7).
