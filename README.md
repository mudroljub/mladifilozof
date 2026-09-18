# Mladi filozof

## Lokalni razvoj

```powershell
py dev.py
```

Za drugi port:

```powershell
py dev.py --port 8080
```

## Slike

U `slike.json` se slika povezuje sa stranicom preko njenog sluga (naziva `.txt`
fajla bez nastavka). Svaka stavka ima naziv fajla iz `slike/` i obavezni `alt`
opis. Stranica bez stavke ostaje bez slike.

## TODO

- ukloniti redne brojeve fajlova?
- čitati i eventualno lektorisati
    - Proveriti reči poput „kadgod”, „gdegod” i slično. Može i zajedno i odvojeno.
- pokušati prelom teksta u stihove
- razmotriti tematski redosled zbirke prema predlozeni-redosled.md.
