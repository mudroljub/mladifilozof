# Mladi Filozof

Sajt se pravi iz čistih UTF-8 tekstova u folderu `tekstovi/`.

```powershell
py build.py
```

Komanda obnavlja `index.html`, `stranice/*.html` i `assets/site.css`.

- Tekstovi direktno u `tekstovi/` postaju zasebne stranice.
- Fajlovi sa brojem na početku prate taj redosled u sadržaju.
- Fajlovi sa prefiksom `xx-` prikazuju se na kraju.
- Podfolderi, uključujući `tekstovi/novo/`, služe za radne tekstove i ne objavljuju se.
