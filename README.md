# Mladi filozof

## Lokalni razvoj

```powershell
py dev.py
```

Za drugi port:

```powershell
py dev.py --port 8080
```

## TODO

- popravi "18-mladi-filozof-je-bežao-od-ljudi" ne prikazuje novu sliku
- dodati novo
- ukloniti redne brojeve fajlova?
- čitati i eventualno lektorisati
    - Proveriti reči poput „kadgod”, „gdegod” i slično. Može i zajedno i odvojeno.
- pokušati prelom teksta u stihove
- razmotriti tematski redosled zbirke prema predlozeni-redosled.md.


## ČIŠĆENJE SLIKA

magick mladifilozof-drvo.jpg -colorspace Gray -contrast-stretch 0%x10% mladifilozof-drvo.png
magick mladifilozof-drvo.jpg -colorspace Gray -level 5%,95% -contrast-stretch 0%x5% mladifilozof-drvo.png
magick mladifilozof-drvo.jpg -colorspace Gray -level 5%,95% -median 3 -contrast-stretch 0%x5% mladifilozof-drvo.png
magick mladifilozof-drvo.jpg -colorspace Gray -white-threshold 88% mladifilozof-drvo.png
magick mladifilozof-drvo.jpg -colorspace Gray -level 8%,92% -contrast-stretch 0%x3% mladifilozof-drvo.png
magick mladifilozof-drvo.jpg -colorspace Gray -white-threshold 82% mladifilozof-drvo.png

## Poziv crtačima

Drugari umetnici,

Nameravam da štampam zbirku refleksivne poezije koju sam napisao pre više od pola života. Možete je naći ovde: 
https://mudroljub.github.io/mladifilozof

Oduvek sam zamišljao da uz svaki zapis ide i neki crtež, nalik stripu, i tu mi treba vaša pomoć.

PRAVILA KONKURSA su sledeća: 
- Crtež treba da ima neke veze sa tekstom (izuzetak je naslovnica). Možete nacrtati novu ilustraciju ili iskoristiti postojeću, ako se lepo uklapa.
- Štampaće se crno-belo i crteže treba pripremiti za štampu (da imaju jak kontrast i čistu pozadinu).
- Možete poslati crteža koliko hoćete (samo napomenite koji crtež je za koji tekst). 

Crteže šaljite na: mladifilozof@yahoo.com

KONKURS JE OTVOREN MESEC DANA. 

Nakon toga žiri će izabrati po jedan crtež za svaki tekst i jedan za naslovnicu. Ja ću u potpunosti organizovati i finansirati izdanje knjige, a potom i promociju, sa izložbom crteža izabranih autora.

Nadam se da će od svega ovoga ispasti nešto zanimljivo :)
