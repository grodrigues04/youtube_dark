# Pauta do dia: escolha dos temas dos Shorts

Você roda sozinho num container, sem ninguém para responder perguntas: nunca pergunte nada,
decida e siga. A pasta atual é a pasta de trabalho do dia ({{DATE}}).

A pesquisa de mercado de hoje está em `research/`:

- `research/highlights.json`: as 7 listas da Parte 11 (recomendações estratégicas finais), cada
  uma com 10 itens (`recommendations[].key`, `title`, `items[]`).
- `research/report.md`: o relatório completo (11 partes), para contexto, fatos e fontes.
- `research/previous-videos.json`: os temas dos vídeos dos últimos 30 dias (não repita).

Tarefa: escolher **um tema de cada uma das 7 listas** para virar um YouTube Short de até 1 minuto,
em pt-BR, para o público brasileiro (leia `/app/studio/prompts/regras-do-short.md` para saber o
que o vídeo precisa ter).

Critérios para escolher o item de cada lista:

- Potencial de prender o brasileiro em 3 segundos (curiosidade, surpresa, identificação).
- Funciona com o ângulo "cresce lá fora → pode chegar ao Brasil".
- Tem fatos e fontes no relatório para sustentar um vídeo (números, exemplos, nomes).
- Dá para mostrar com animações (números, comparação, lista, jornada entre países).
- Os 7 temas são diferentes entre si (um item que aparece em mais de uma lista só pode ser usado
  uma vez) e diferentes dos vídeos recentes.

Use Grep no `research/report.md` para achar os fatos de cada candidato. Não pesquise na web nesta
etapa.

Escreva `pauta.json` (UTF-8, pt-BR):

```json
{
  "date": "{{DATE}}",
  "videos": [
    {
      "index": 1,
      "category_key": "most_promising",
      "category_title": "As 10 oportunidades mais promissoras",
      "item_name": "nome do item exatamente como na lista",
      "theme": "tema do vídeo em uma frase",
      "angle": "o ângulo para o Brasil (o que é, onde cresce, por que importa aqui)",
      "origin_country": "país de origem/tração",
      "key_facts": [{"fact": "fato com número/nome", "source": "URL", "date": "data"}],
      "search_queries": ["termos para buscar no YouTube em pt, en e no idioma de origem"],
      "why": "por que esse item e não os outros da lista"
    }
  ]
}
```

`videos` tem exatamente 7 entradas, na ordem das listas (`most_promising`,
`overlooked_micro_niches`, `growth_6_12_months`, `best_balance`, `faceless_content`, `saas_ai`,
`adapt_to_brazil`), com `index` de 1 a 7. Cada vídeo com 3 a 6 `key_facts` com fonte.
