import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TranzakcioLG:
    datum: str
    tipus: str
    kategoria: str
    megnevezes: str
    osszeg: int


def osszesites_lg(tetelek):
    bevetel = sum(tetel.osszeg for tetel in tetelek if tetel.tipus == "Bevétel")
    kiadas = sum(tetel.osszeg for tetel in tetelek if tetel.tipus == "Kiadás")
    return bevetel, kiadas, bevetel - kiadas


def penz_formaz_lg(osszeg):
    return f"{osszeg:,}".replace(",", " ") + " Ft"


def adatok_betoltese_lg(fajl):
    if not Path(fajl).exists():
        return []
    try:
        with open(fajl, "r", encoding="utf-8") as bemenet:
            adatok = json.load(bemenet)
        return [TranzakcioLG(**elem) for elem in adatok]
    except (OSError, ValueError, TypeError, KeyError) as hiba:
        raise RuntimeError(f"Nem sikerült beolvasni az adatokat: {hiba}") from hiba


def adatok_mentese_lg(fajl, tetelek):
    with open(fajl, "w", encoding="utf-8") as kimenet:
        json.dump([asdict(tetel) for tetel in tetelek], kimenet, ensure_ascii=False, indent=2)
