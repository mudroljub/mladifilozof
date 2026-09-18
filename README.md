# Mladi filozof

Sajt se pravi iz čistih UTF-8 tekstova u folderu `tekstovi/`.

```powershell
py build.py
```

Komanda obnavlja `index.html`, `stranice/*.html` i `assets/site.css`.

- Tekstovi direktno u `tekstovi/` postaju zasebne stranice.
- Fajlovi sa brojem na početku prate taj redosled u sadržaju.
- Fajlovi sa prefiksom `xx-` prikazuju se na kraju.
- Podfolderi, uključujući `tekstovi/novo/`, služe za radne tekstove i ne objavljuju se.

## Lokalni razvoj

```powershell
py dev.py
```

Sajt će biti dostupan na `http://127.0.0.1:8000/`. Režim prati izmene u
`tekstovi/` i `build.py`, a zatim automatski obnavlja HTML. Prekid: `Ctrl+C`.

Za drugi port:

```powershell
py dev.py --port 8080
```

## TODO

- proveri je li prva rečenica u svakom fajlu zaseban pasus. ako nije izvesti me, bez menjanja.
- čitati i eventualno lektorisati
    - Proveriti reči poput „kadgod”, „gdegod” i slično. Može i zajedno i odvojeno.
- pokušati prelom teksta u stihove
- [ ] Razmotriti tematski redosled zbirke prema [izveštaju o tematskom redosledu](izvestaj-tematski-redosled.md).