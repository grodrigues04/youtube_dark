# Pauta do dia: escolha do tema do Short

Você roda sozinho num container, sem ninguém para responder perguntas: nunca pergunte nada,
decida e siga. A pasta atual é a pasta de trabalho do dia ({{DATE}}).

Todo dia sai **um** Short, feito a partir da pesquisa de mercado mais recente (sai de segunda a
quarta, de madrugada). Ela está em `research/`:

- `research/highlights.json`: a data da pesquisa (`date`) e as 7 listas da Parte 11
  (recomendações estratégicas finais), cada uma com 10 itens (`recommendations[].key`, `title`,
  `items[]`).
- `research/report.md`: o relatório completo, para contexto, fatos e fontes.
- `research/previous-videos.json`: **todos** os vídeos já feitos pelo canal, com `research_date`
  (a pesquisa de onde saíram), `category_key` (a lista), `item_name` e `theme`.

Tarefa: escolher **um** tema para virar um YouTube Short de até 1 minuto, em pt-BR, para o
público brasileiro (leia `/app/studio/prompts/regras-do-short.md` para saber o que o vídeo precisa
ter).

## Regras de escolha

1. **Nunca repetir tema.** O item escolhido não pode ser o mesmo assunto de nenhum vídeo de
   `previous-videos.json`, nem com outro nome (compare `item_name` e `theme`, não só o texto
   exato), mesmo que tenha vindo de uma pesquisa antiga.
2. **Uma lista por dia.** Entre os vídeos com `research_date` igual à data desta pesquisa, veja
   quais listas (`category_key`) já foram usadas. Escolha da primeira lista ainda não usada, na
   ordem: `most_promising`, `overlooked_micro_niches`, `growth_6_12_months`, `best_balance`,
   `faceless_content`, `saas_ai`, `adapt_to_brazil`. Se as 7 já foram usadas (a pesquisa nova
   ainda não saiu), volte ao começo da ordem e escolha outro item ainda não usado.
3. Dentro da lista, escolha o item com mais potencial:
   - prender o brasileiro em 3 segundos (curiosidade, surpresa, identificação);
   - funcionar com o ângulo "cresce lá fora → pode chegar ao Brasil";
   - ter fatos e fontes no relatório para sustentar um vídeo (números, exemplos, nomes);
   - dar para mostrar com animações (números, comparação, lista, jornada entre países).

Use Grep no `research/report.md` para achar os fatos do candidato. Não pesquise na web nesta
etapa.

Escreva `pauta.json` (UTF-8, pt-BR):

```json
{
  "date": "{{DATE}}",
  "research_date": "<research/highlights.json → date>",
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
      "why": "por que esse item, e por que ele não repete nenhum vídeo anterior"
    }
  ]
}
```

`videos` tem exatamente 1 entrada, com `index` 1 e 3 a 6 `key_facts` com fonte.
