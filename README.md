# ER-Sp-Dashboard

Tablero personal: tipos de cambio (EUR, USD, CLP, UYU) y agenda deportiva semanal en hora peninsular.

- Web: https://gervasio93.github.io/ER-Sp-Dashboard/
- `template.html`: la página. `data/fx.json`: histórico de divisas. `data/eventos.json`: calendario deportivo.
- `python3 build.py` actualiza divisas y genera `index.html`.
- Al abrir la web, los tipos de cambio del día se consultan en vivo.
