# Planilhas de exemplo para importação

- `modelo-importacao.csv`: modelo com 3 faixas **fictícias**. Use-o como base para a sua planilha.
- `minha-playlist-PREENCHER.csv`: as 100 músicas da playlist do projeto, com título e artista.
  **BPM, tom e duração estão em branco** e precisam ser preenchidos antes de importar (ver abaixo).

## Jeito mais rápido: exportar do Rekordbox

Se as músicas estão no Rekordbox, não precisa preencher nada à mão:

1. Deixe visíveis as colunas **Track Title**, **Artist**, **BPM**, **Key** e **Time**.
2. Botão direito na playlist → **Exportar uma playlist para um arquivo** → **.txt**.
3. Importe o `.txt` em **Biblioteca → Importar CSV**. O tom em `Am`, `F#m` etc. é convertido para Camelot.

## Montando a planilha à mão

1. Abra o modelo no Excel ou no Google Planilhas.
2. Para cada música, preencha **título**, **artista** e **duração** (o Spotify mostra os três).
3. Descubra o **BPM** e o **tom** de cada música num software de DJ (Rekordbox, Serato, VirtualDJ)
   ou num site como Tunebat ou SongBPM. O tom pode ser Camelot (8A) ou notação musical (Am).
   Atenção: o BPM e o tom variam entre versões (Radio Edit, Club Mix, remix), então use a versão que você toca.
4. `genero` e `energia` (1 a 10) são opcionais.
5. Salve como **CSV** e importe em **Biblioteca → Importar CSV**.
