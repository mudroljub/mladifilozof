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

- čitati i lektorisati
    - Proveriti reči poput „kadgod”, „gdegod” i slično. Može i zajedno i odvojeno.
- pokušati prelom teksta u stihove
- dodavati prvu rečenicu na kraj gde ide
- razmotriti tematski redosled zbirke prema predlozeni-redosled.md.
- Mladi filozof se pretvorio u zver: boldovati drugu rečenicu umesto prve.


## ČIŠĆENJE SLIKA

magick hvala-drvetu.jpg -colorspace Gray -contrast-stretch 0%x10% hvala-drvetu.png
magick hvala-drvetu.jpg -colorspace Gray -level 5%,95% -contrast-stretch 0%x5% hvala-drvetu.png
magick hvala-drvetu.jpg -colorspace Gray -level 5%,95% -median 3 -contrast-stretch 0%x5% hvala-drvetu.png
magick hvala-drvetu.jpg -colorspace Gray -white-threshold 88% hvala-drvetu.png
magick hvala-drvetu.jpg -colorspace Gray -level 8%,92% -contrast-stretch 0%x3% hvala-drvetu.png
magick hvala-drvetu.jpg -colorspace Gray -white-threshold 82% hvala-drvetu.png

## Poziv crtačima

Drugari umetnici,

Nameravam da štampam zbirku refleksivne poezije koju sam napisao pre više od pola života. Možete je naći ovde: 
https://mudroljub.github.io/mladifilozof

Oduvek sam zamišljao da uz svaki zapis ide i neki crtež, nalik stripu, i tu mi treba vaša pomoć.

PRAVILA KONKURSA su sledeća: 
- Crtež treba da ima neke veze sa tekstom ili da bude naslovnica. Možete nacrtati novu ilustraciju ili iskoristiti postojeću, ako se lepo uklapa.
- Crteže pripremite za crno-belu štampu (da imaju jak kontrast i čistu pozadinu).
- Fajl crteža imenujte na sledeći način: Naziv pričice - vaše Ime i prezime.
- Možete poslati crteža koliko hoćete.

Crteže šaljite na: mladifilozof@yahoo.com

KONKURS JE OTVOREN MESEC DANA. 

Nakon toga, žiri će izabrati po jedan crtež za svaki tekst i jedan za naslovnicu. Ja ću u potpunosti organizovati i finansirati izdanje knjige, a potom i promociju, sa izložbom crteža izabranih autora.

Nadam se da će od svega ovoga ispasti nešto zanimljivo :)
