# youtube_dark

Todo dia às **6h**, este container faz **um** YouTube Short de até 1 minuto (100% em pt-BR, para o
público brasileiro) a partir da pesquisa completa mais recente do
[market_trends](../market_trends) (a edição A, de quinta à noite) e sobe no canal agendado para
ser publicado às **8h**. Ele nunca espera nem roda logo depois de uma pesquisa: usa a que já está
salva, e na sexta já pega a edição nova da quinta.

```
market_trends.researches (edição A mais recente) ──▶ research.py (root): exporta para /data/work/<data>/research
        │                                              (+ todos os vídeos já feitos, para não repetir tema)
        ▼
Claude "pauta" ──▶ pauta.json (1 tema nunca usado; uma lista da Parte 11 por dia)
        │
        ▼  outra sessão do Claude:
pesquisador-youtube ─▶ roteirista ⇄ critico (até 4 rodadas) ─▶ produção (Remotion + narração pt-BR)
        ─▶ hashtags + thumbnail + titulo (em paralelo) ─▶ metadata.json + READY
        │
        ▼
publish.py (root) ──▶ YouTube (privado, publicação agendada para 8h) + youtube_dark.videos no MongoDB
                  ──▶ apaga do disco o vídeo, a thumb, a narração e os frames
```

## Como funciona

- `runner/scheduler.sh` olha o relógio a cada 30s. Às 06:00, uma vez por dia (lock em
  `data/state/<data>.lock`), roda `runner/run_daily.sh`. Se o computador estava desligado às 6h,
  começa assim que o container voltar, mas só até 06:59 (depois disso o vídeo não ficaria pronto
  para as 8h, e o dia é pulado). A cada 10 minutos ele também tenta de novo os uploads pendentes.
- `run_daily.sh` exporta a edição A mais recente (`research.py export-latest`), roda a sessão de
  **pauta** (um tema que nunca virou vídeo, de uma lista da Parte 11 ainda não usada para essa
  pesquisa; com 7 listas e 7 dias até a próxima quinta, sai um vídeo de cada lista por semana) e
  depois a sessão do **vídeo** (`run.sh video <data> 1`).
- `publish.py` sobe o vídeo **privado, com publicação agendada** (`publishAt`) para as 8h
  (`YOUTUBE_PUBLISH_HOUR`). Assim ele aparece no canal às 8h mesmo com o computador desligado.
  Se o upload só acontecer depois das 7h45, fica para as 8h do dia seguinte.
- Depois do upload, o vídeo, a thumbnail, a narração (`assets/`) e os frames (`qa/`) são apagados
  do disco. Ficam só os textos em `data/work/<data>/videos/01/`: `tema.json`,
  `pesquisa-youtube.md`, `roteiro-vN.md` e `critica-vN.md` (histórico da discussão roteirista ×
  crítico), `roteiro-final.md`, `video.json`, `hashtags.json`, `titulo.json`, `metadata.json` e os
  marcadores `READY` → `UPLOADED` (id do vídeo) ou `FAILED`/`UPLOAD_FAILED`.

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

- **Projeto de API não verificado**: o YouTube pode travar como **privados** os vídeos enviados
  por projetos que não passaram pela auditoria (aí o agendamento das 8h não publica). Até agora os
  uploads deste projeto ficaram públicos normalmente; se isso mudar, peça a auditoria em
  https://support.google.com/youtube/contact/yt_api_form e publique pelo YouTube Studio.
- **Cota e limite de uploads por dia**: com 1 vídeo por dia não chega perto. Se o YouTube recusar
  (`quotaExceeded`/`uploadLimitExceeded`), o upload espera a cota renovar (05h de Brasília).
- **Thumbnail personalizada** exige o canal verificado por telefone
  (https://www.youtube.com/verify). Sem isso o vídeo sobe com a capa automática.

## Comandos úteis

```bash
# Teste do estúdio sem Claude e sem upload (narração, render, frames, thumbnail, busca)
docker exec youtube-dark /app/smoke-test.sh

# Rodar (ou retomar) o Short de hoje agora (pula o que já está pronto)
docker exec -e MANUAL_RUN=1 youtube-dark /app/run_daily.sh

# Subir agora os vídeos pendentes
docker exec youtube-dark /opt/runner/bin/python /app/publish.py

# Acompanhar
tail -f data/logs/$(date +%F).log data/logs/publish.log
```

`YOUTUBE_PUBLISH_HOUR` define a hora (Brasília) em que o YouTube publica o Short do dia.
