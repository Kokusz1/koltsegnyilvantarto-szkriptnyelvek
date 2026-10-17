import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from pathlib import Path

from lg_seged import TranzakcioLG, osszesites_lg, penz_formaz_lg, adatok_betoltese_lg, adatok_mentese_lg


ADATFAJL = Path(__file__).with_name("adatok.json")


class KoltsegNyilvantartoLG:
    def __init__(self, root):
        self.root = root
        self.root.title("Magyar költségnyilvántartó")
        self.root.geometry("850x630")
        self.root.minsize(740, 540)
        self.tetelek = adatok_betoltese_lg(ADATFAJL)
        self.tipus = tk.StringVar(value="Kiadás")
        self.kategoria = tk.StringVar(value="Élelmiszer")
        self.datum = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.megnevezes = tk.StringVar()
        self.osszeg = tk.StringVar()
        self.szuro = tk.StringVar(value="Összes")
        self.felulet_letrehozasa()
        self.lista_frissitese()

    def felulet_letrehozasa(self):
        keret = ttk.Frame(self.root, padding=16)
        keret.pack(fill="both", expand=True)
        ttk.Label(keret, text="Bevétel- és kiadásnyilvántartó", font=("Arial", 20, "bold")).pack(anchor="w", pady=(0, 12))

        urlap = ttk.LabelFrame(keret, text="Új tétel hozzáadása", padding=12)
        urlap.pack(fill="x")
        urlap.columnconfigure(1, weight=1)
        urlap.columnconfigure(3, weight=1)

        ttk.Label(urlap, text="Megnevezés:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(urlap, textvariable=self.megnevezes).grid(row=0, column=1, sticky="ew", padx=(6, 14))
        ttk.Label(urlap, text="Összeg (Ft):").grid(row=0, column=2, sticky="w")
        ttk.Entry(urlap, textvariable=self.osszeg).grid(row=0, column=3, sticky="ew", padx=(6, 0))

        ttk.Label(urlap, text="Típus:").grid(row=1, column=0, sticky="w", pady=5)
        tipus_mezo = ttk.Combobox(urlap, textvariable=self.tipus, values=["Bevétel", "Kiadás"], state="readonly")
        tipus_mezo.grid(row=1, column=1, sticky="ew", padx=(6, 14))
        ttk.Label(urlap, text="Kategória:").grid(row=1, column=2, sticky="w")
        ttk.Combobox(urlap, textvariable=self.kategoria, values=["Élelmiszer", "Lakhatás", "Közlekedés", "Szórakozás", "Fizetés", "Egyéb"], state="readonly").grid(row=1, column=3, sticky="ew", padx=(6, 0))

        ttk.Label(urlap, text="Dátum (ÉÉÉÉ-HH-NN):").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(urlap, textvariable=self.datum).grid(row=2, column=1, sticky="ew", padx=(6, 14))
        ttk.Button(urlap, text="Tétel hozzáadása", command=self.tetel_hozzaadasa).grid(row=2, column=3, sticky="e")

        lista_fejlec = ttk.Frame(keret)
        lista_fejlec.pack(fill="x", pady=(16, 6))
        ttk.Label(lista_fejlec, text="Rögzített tételek", font=("Arial", 13, "bold")).pack(side="left")
        ttk.Label(lista_fejlec, text="Szűrés:").pack(side="left", padx=(18, 6))
        szuro_mezo = ttk.Combobox(lista_fejlec, textvariable=self.szuro, values=["Összes", "Bevétel", "Kiadás"], state="readonly", width=12)
        szuro_mezo.pack(side="left")
        szuro_mezo.bind("<<ComboboxSelected>>", lambda esemeny: self.lista_frissitese())
        ttk.Button(lista_fejlec, text="Kijelölt tétel törlése", command=self.kijelolt_torlese).pack(side="right")

        tabla_keret = ttk.Frame(keret)
        tabla_keret.pack(fill="both", expand=True)
        oszlopok = ("datum", "tipus", "kategoria", "megnevezes", "osszeg")
        self.tabla = ttk.Treeview(tabla_keret, columns=oszlopok, show="headings", selectmode="browse")
        feliratok = {"datum": "Dátum", "tipus": "Típus", "kategoria": "Kategória", "megnevezes": "Megnevezés", "osszeg": "Összeg"}
        for oszlop in oszlopok:
            self.tabla.heading(oszlop, text=feliratok[oszlop])
            self.tabla.column(oszlop, width=110 if oszlop != "megnevezes" else 220, anchor="e" if oszlop == "osszeg" else "w")
        gorgeto = ttk.Scrollbar(tabla_keret, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=gorgeto.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        gorgeto.pack(side="right", fill="y")

        self.osszefoglalo = ttk.Label(keret, text="", font=("Arial", 11, "bold"))
        self.osszefoglalo.pack(anchor="w", pady=(12, 4))
        self.havi_osszefoglalo = ttk.Label(keret, text="")
        self.havi_osszefoglalo.pack(anchor="w")
        ttk.Label(keret, text="A tételek automatikusan az adatok.json fájlba mentődnek.").pack(anchor="w", pady=(12, 0))

    def tetel_hozzaadasa(self):
        try:
            megnevezes = self.megnevezes.get().strip()
            if not megnevezes:
                raise ValueError("Add meg a tétel megnevezését!")
            osszeg = int(self.osszeg.get().replace(" ", ""))
            if osszeg <= 0:
                raise ValueError("Az összeg pozitív egész szám legyen!")
            datum = datetime.strptime(self.datum.get().strip(), "%Y-%m-%d").date()
            tetel = TranzakcioLG(datum.isoformat(), self.tipus.get(), self.kategoria.get(), megnevezes, osszeg)
        except ValueError as hiba:
            messagebox.showerror("Hibás adat", str(hiba))
            return
        self.tetelek.append(tetel)
        if not self.mentes():
            self.tetelek.pop()
            return
        self.megnevezes.set("")
        self.osszeg.set("")
        self.lista_frissitese()

    def kijelolt_torlese(self):
        kijeloles = self.tabla.selection()
        if not kijeloles:
            messagebox.showinfo("Nincs kijelölés", "Először jelölj ki egy tételt!")
            return
        if not messagebox.askyesno("Törlés megerősítése", "Biztosan törlöd a kijelölt tételt?"):
            return
        index = int(kijeloles[0])
        tetel = self.tetelek.pop(index)
        if not self.mentes():
            self.tetelek.insert(index, tetel)
            return
        self.lista_frissitese()

    def mentes(self):
        try:
            adatok_mentese_lg(ADATFAJL, self.tetelek)
            return True
        except OSError as hiba:
            messagebox.showerror("Mentési hiba", f"Nem sikerült menteni az adatokat: {hiba}")
            return False

    def lista_frissitese(self):
        for elem in self.tabla.get_children():
            self.tabla.delete(elem)
        for index, tetel in enumerate(self.tetelek):
            if self.szuro.get() not in ("Összes", tetel.tipus):
                continue
            self.tabla.insert("", "end", iid=str(index), values=(tetel.datum, tetel.tipus, tetel.kategoria, tetel.megnevezes, penz_formaz_lg(tetel.osszeg)))
        bevetel, kiadas, egyenleg = osszesites_lg(self.tetelek)
        self.osszefoglalo.config(text=f"Összes bevétel: {penz_formaz_lg(bevetel)}  |  Összes kiadás: {penz_formaz_lg(kiadas)}  |  Egyenleg: {penz_formaz_lg(egyenleg)}")
        mai_nap = date.today()
        honap_kezdete = mai_nap.replace(day=1)
        kovetkezo_honap = (honap_kezdete.replace(day=28) + timedelta(days=4)).replace(day=1)
        havi_tetelek = [tetel for tetel in self.tetelek if honap_kezdete <= date.fromisoformat(tetel.datum) < kovetkezo_honap]
        havi_bevetel, havi_kiadas, havi_egyenleg = osszesites_lg(havi_tetelek)
        self.havi_osszefoglalo.config(text=f"Aktuális hónap ({mai_nap.year}. {mai_nap.month}.): bevétel {penz_formaz_lg(havi_bevetel)}, kiadás {penz_formaz_lg(havi_kiadas)}, egyenleg {penz_formaz_lg(havi_egyenleg)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = KoltsegNyilvantartoLG(root)
    root.mainloop()
