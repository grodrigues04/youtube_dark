# Produção do Short {{INDEX}} de {{DATE}}

Você roda sozinho num container, sem ninguém para responder perguntas: nunca pergunte nada,
decida e siga. A pasta atual é a pasta deste vídeo. Nela está `tema.json` (o tema escolhido da
pesquisa de mercado mais recente); o relatório completo está em `../../research/report.md`.

O vídeo é um YouTube Short de **no máximo 1 minuto**, **100% em pt-BR para o público
brasileiro**. As regras estão em `/app/studio/prompts/regras-do-short.md` (leia inteiro agora) e
os tipos de cena em `/app/studio/prompts/catalogo-de-cenas.md` (leia inteiro agora).

Você coordena os agentes (ferramenta Agent, com o `subagent_type` indicado) e faz a produção.
Passe sempre o caminho absoluto da pasta do vídeo para os agentes. Siga as etapas na ordem:

## 1. Pesquisa no YouTube

Agent `pesquisador-youtube` → `pesquisa-youtube.md`.

## 2. Roteiro com crítica (até 4 rodadas)

1. Agent `roteirista`: escrever `roteiro-v1.md`.
2. Agent `critico`: analisar `roteiro-v1.md` → `critica-v1.md`.
3. Se a última linha da crítica for `VEREDITO: REVISAR`, Agent `roteirista` escreve a versão
   seguinte respondendo a crítica, e o `critico` analisa de novo. Repita até `VEREDITO: APROVADO`
   ou até a 4ª versão do roteiro (na 4ª, o roteirista aplica todas as mudanças obrigatórias da
   última crítica e ela vira a final).
4. Copie a versão final para `roteiro-final.md`.

A produção **só começa depois** do `roteiro-final.md` pronto.

## 3. Produção do vídeo (você mesmo)

1. Monte `video.json` seguindo **fielmente** o `roteiro-final.md`: mesma ordem de cenas, mesma
   narração (palavra por palavra), mesmos tipos, textos, destaques, emojis, SFX e paletas.
   Se houver músicas em `/music` (`ls /music`), pode escolher uma que combine (volume 0.08–0.15);
   senão `"music": null`.
   A narração é corrida (seção "Narração corrida, sem pausas" de `regras-do-short.md`): se o
   roteiro final ainda tiver reticências ou frases de uma palavra só, troque por vírgula ou emende
   na frase seguinte, sem mudar o sentido.
2. `python3 /app/studio/tools/prepare.py .` — gera a narração pt-BR (já sem as pausas da voz) e
   `props.json`. Se passar do tempo máximo, enxugue a narração mantendo o sentido do roteiro e
   rode de novo.
3. `bash /app/studio/tools/render.sh .` — gera `video.mp4` (leva alguns minutos).
4. Controle de qualidade: `bash /app/studio/tools/frames.sh . 0.3 1.5 3 6 9` e mais 4 a 6
   segundos espalhados até o fim (um por cena). Abra cada imagem de `qa/` com Read e confira:
   texto inteiro dentro da tela, sem sobreposição com as legendas, legível, emojis renderizados,
   cores fortes, nada vazio ou parado. Corrija `video.json` (texto menor, menos itens, outro
   tipo de cena) e repita 2–4 até ficar bom (no máximo 3 renderizações).
5. O vídeo final é `video.mp4` (≤ 60s). Não mexa mais nele depois daqui.

## 4. Título, hashtags e thumbnail (em paralelo)

Com o vídeo pronto, chame **numa única mensagem** os três agentes:

- `hashtags` → `hashtags.json`
- `thumbnail` → `thumbnail.json` e `thumbnail.jpg`
- `titulo` → `titulo.json`

## 5. Metadados para o upload

Escreva `metadata.json`:

```json
{
  "title": "<titulo.json → titulo>",
  "description": "<2 a 4 linhas em pt-BR: o que a pessoa aprende + ângulo Brasil + CTA para seguir o canal; uma linha em branco; as hashtags de hashtags.json separadas por espaço>",
  "tags": ["<hashtags.json → tags>"],
  "hashtags": ["<hashtags.json → hashtags>"],
  "language": "pt-BR",
  "video": "video.mp4",
  "thumbnail": "thumbnail.jpg",
  "theme": "<tema.json → theme>",
  "category_key": "<tema.json → category_key>"
}
```

Confira: título ≤ 100 caracteres, descrição ≤ 4500 caracteres, sem `<` ou `>`, tudo em pt-BR.
Por fim, crie o arquivo vazio `READY`. Só crie `READY` quando `video.mp4`, `thumbnail.jpg` e
`metadata.json` estiverem prontos e conferidos. O upload para o YouTube é feito depois, por outro
processo (você não tem acesso à conta).

Se algo impedir o vídeo de ficar pronto, escreva o motivo em `FAILED` e encerre.
