Ladics Gábor D7MOR4

Feladat leírása:
Grafikus felületű Python-alkalmazás bevételek és kiadások kezelésére. 
A programmal tételek vehetők fel és törölhetők, lista típus szerint szűrhető, és megtekinthető az összes-, aktuális havi egyenleg. 
A tételek a helyi `adatok.json` fájlban tárolódnak.

Modulok és használt függvények:
- Tanult modul: `tkinter` – `Tk()`, `Button`/`ttk.Button`, `messagebox.showerror()`, `messagebox.askyesno()`; grafikus felület és eseménykezelés.
- Bemutatandó modul: `datetime` – `date.today()`, `datetime.strptime()`, `timedelta()`; dátumkezelés és havi szűrés.
- Saját modul: `lg_seged.py` – `osszesites_lg()`, `penz_formaz_lg()`, `adatok_betoltese_lg()`, `adatok_mentese_lg()`.
- Egyéb beépített modulok: `json` (`load`, `dump`), `dataclasses` (`dataclass`, `asdict`), `pathlib` (`Path`).

Osztályok:
`TranzakcioLG`: egy bevételi vagy kiadási tétel adatai.
`KoltsegNyilvantartoLG`: az alkalmazás ablakát és eseményeit kezeli.