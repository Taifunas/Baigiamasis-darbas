# Skelbiu.lt Sąsajos Programa

Ši Python programa yra grafinė naudotojo sąsaja, leidžianti atlikti paiešką, filtravimą, rūšiavimą ir skelbimų eksportą iš svetainės [skelbiu.lt](https://www.skelbiu.lt). Ji sukurta naudojant `PyQt6`, `Selenium`, `BeautifulSoup` ir kitas pagalbines bibliotekas.

---

## Funkcionalumas

- **Nuorodos tikrinimas**: Patikrina, ar įvesta Skelbiu.lt nuoroda yra veikianti.
- **Paieška**: Leidžia vykdyti paiešką pagal raktinius žodžius.
- **Kategorijų naršymas**: Parodo paieškos rezultatų kategorijas ir leidžia atidaryti pasirinktą kategoriją.
- **Filtravimas pagal kainą**: Filtruoja skelbimus pagal naudotojo nustatytas kainos ribas.
- **Rūšiavimas**: Rūšiuoja rezultatus pagal pasirinktą kriterijų.
- **Puslapių navigacija**: Leidžia naršyti tarp skelbimų puslapių.
- **Eksportavimas į CSV**: Leidžia išsaugoti pasirinktą skelbimų kiekį į CSV failą.

---

## Priklausomybės

Norint paleisti programą, būtina įdiegti šias bibliotekas:

- Python 3.8+
- `PyQt6`
- `requests`
- `selenium`
- `beautifulsoup4`

Taip pat reikalinga:

- **Google Chrome naršyklė**
- **ChromeDriver**, suderinamas su jūsų naršyklės versija (turi būti PATH'e arba projekto kataloge).

Priklausomybes galite įdiegti naudodami šią komandą:

```bash
pip install PyQt6 requests selenium beautifulsoup4
```

---

## Paleidimas

1. Įsitikinkite, kad turite įdiegtą `chromedriver` ir jis yra suderinamas su jūsų Google Chrome versija.
2. Paleiskite programą naudodami komandą:

   ```bash
   python main.py
   ```

3. Paleidimo metu atsidarys grafinė vartotojo sąsaja, leidžianti atlikti paieškas, filtruoti skelbimus ir juos eksportuoti.

---

## Eksportavimas į CSV

Programa leidžia išsaugoti skelbimus į failą `skelbimai.csv`. Eksportavimo procesas:

1. Įveskite maksimalų skelbimų kiekį, kurį norite išsaugoti.
2. Programa surinks duomenis iš kelių puslapių, kol pasieks įvestą kiekį arba baigsis puslapiai.
3. CSV faile bus šie stulpeliai:
   - **Pavadinimas**
   - **Kaina**

> **Pastaba**: Jei norimas skelbimų kiekis viršija rastų skelbimų skaičių, išsaugomi tik prieinami skelbimai.

---

## Papildoma Informacija

- Jei keičiasi Skelbiu.lt svetainės struktūra, gali prireikti atnaujinti selektorius (`By.ID`, `By.CSS_SELECTOR` ir pan.).
- Programa sukurta edukaciniais tikslais ir nėra skirta komerciniam naudojimui.
- Jei kyla problemų su `chromedriver`, patikrinkite, ar jo versija atitinka jūsų Google Chrome naršyklės versiją.

---

## Licencija

Šis projektas yra skirtas mokymosi tikslams ir neturi oficialios licencijos.