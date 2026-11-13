import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from pathlib import Path


from lg_segedmodul import TranzakcioLG, osszesites_lg, penz_formaz_lg, adatok_betoltese_lg, adatok_mentese_lg
import calendar
import csv
import json
from tkinter import filedialog

ADATFAJL = Path(__file__).with_name("adatok.json")
FIZETESFAJL = Path(__file__).with_name("fizetes.json")

class KoltsegNyilvantartoLG:
    def __init__(self, root):
        self.root = root
        self.root.title("D7MOR4 költségnyilvántartó")
        self.root.geometry("800x640")
        self.root.minsize(800, 640)
        self.tetelek = adatok_betoltese_lg(ADATFAJL)
        self.tipus = tk.StringVar(value="Kiadás")
        self.kategoria = tk.StringVar(value="Élelmiszer")
        self.datum = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.megnevezes = tk.StringVar()
        self.osszeg = tk.StringVar()
        self.szuro = tk.StringVar(value="Összes")
        self.honap_szuro = tk.StringVar(value="Összes hónap")
        self.fizetes_beallitas = None
        if FIZETESFAJL.exists():
            with open(FIZETESFAJL, "r", encoding="utf-8") as fajl:
                self.fizetes_beallitas = json.load(fajl)
        if self.fizetes_beallitas:
            self.fizetesek_generalasa_lg()
        self.felulet_letrehozasa_lg()
        self.lista_frissitese_lg()
        if not self.tetelek and not self.fizetes_beallitas:
            self.root.after(100, self.elso_fizetes_bekerese_lg)

    def elso_fizetes_bekerese_lg(self):
        self.havi_fizetes_ablak_lg(elso=True)

    def felulet_letrehozasa_lg(self):
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
        ttk.Combobox(urlap, textvariable=self.kategoria, values=["Bevásárlás", "Lakhatás", "Utazás", "Szórakozás", "Fizetés","Hitel", "Edzés", "Előfizetések","Üzemanyag","Tömegközlekedés", "Ételek", "Italok","Fodrász","Gyógyszerek", "Egyéb"], state="readonly").grid(row=1, column=3, sticky="ew", padx=(6, 0))
        ttk.Label(urlap, text="Dátum:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(urlap, textvariable=self.datum).grid(row=2, column=1, sticky="ew", padx=(6, 14))
        ttk.Button(urlap, text="Tétel hozzáadása", command=self.tetel_hozzaadasa_lg).grid(row=2, column=3, sticky="e")
        lista_fejlec = ttk.Frame(keret)
        lista_fejlec.pack(fill="x", pady=(16, 6))
        ttk.Label(lista_fejlec, text="Rögzített tételek", font=("Arial", 13, "bold")).pack(side="left")
        ttk.Label(lista_fejlec, text="Szűrés:").pack(side="left", padx=(18, 6))
        szuro_mezo = ttk.Combobox(lista_fejlec, textvariable=self.szuro, values=["Összes", "Bevétel", "Kiadás"], state="readonly", width=12)
        szuro_mezo.pack(side="left")
        szuro_mezo.bind("<<ComboboxSelected>>", lambda esemeny: self.lista_frissitese_lg())
        ttk.Label(lista_fejlec,text="Hónap:").pack(side="left", padx=(12, 5))
        self.honap_mezo = ttk.Combobox(lista_fejlec,textvariable=self.honap_szuro,state="readonly", width=14)
        self.honap_mezo.pack(side="left")
        self.honap_mezo.bind("<<ComboboxSelected>>", lambda esemeny: self.lista_frissitese_lg())
        ttk.Button(lista_fejlec, text="Tétel törlés", command=self.kijelolt_torlese_lg).pack(side="right", padx=3)
        ttk.Button(lista_fejlec, text="Tétel szerkesztés", command=self.tetel_szerkesztese_lg).pack(side="right", padx=3)
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
        osszegzes_keret = ttk.Frame(keret)
        osszegzes_keret.pack(fill="x", pady=(12, 4))
        self.osszefoglalo = ttk.Label(osszegzes_keret,text="",font=("Arial", 11, "bold"))
        self.osszefoglalo.pack(side="left")
        self.egyenleg_cimke = tk.Label(osszegzes_keret,font=("Arial", 11, "bold"))
        self.egyenleg_cimke.pack(side="left", padx=8)
        havi_keret = ttk.Frame(keret)
        havi_keret.pack(fill="x")
        self.havi_osszefoglalo = ttk.Label(havi_keret,text="")
        self.havi_osszefoglalo.pack(side="left")
        self.havi_egyenleg_cimke = tk.Label(havi_keret,font=("Arial", 10, "bold"))
        self.havi_egyenleg_cimke.pack(side="left", padx=8)
        ttk.Label(keret, text="A tételek automatikusan az adatok.json fájlba mentődnek.").pack(anchor="w", pady=(12, 0))
        also_sav = ttk.Frame(keret)
        also_sav.pack(fill="x", pady=(12, 0))
        ttk.Button(also_sav, text="Havi fizetés", command=self.havi_fizetes_ablak_lg).pack(side="left", padx=3)
        ttk.Button(also_sav, text="Diagram", command=self.diagram_valasztasa_lg).pack(side="left", padx=3)
        ttk.Button(also_sav, text="Exportálás", command=self.csv_exportalas_lg).pack(side="right")
        ttk.Button(also_sav,text="Minden tétel törlése",command=self.minden_tetel_torlese_lg).pack(side="right", padx=5)

    def tetel_hozzaadasa_lg(self):
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
        if not self.mentes_lg():
            self.tetelek.pop()
            return
        self.megnevezes.set("")
        self.osszeg.set("")
        self.lista_frissitese_lg()

    def tetel_szerkesztese_lg(self):
        kijeloles = self.tabla.selection()

        if not kijeloles:
            messagebox.showinfo("Nincs kijelölés","Először jelölj ki egy tételt!")
            return
        index = int(kijeloles[0])
        tetel = self.tetelek[index]
        ablak = tk.Toplevel(self.root)
        ablak.title("Tétel szerkesztése")
        ablak.geometry("430x360")
        ablak.transient(self.root)
        ablak.grab_set()
        keret = ttk.Frame(ablak, padding=20)
        keret.pack(fill="both", expand=True)
        datum = tk.StringVar(value=tetel.datum)
        tipus = tk.StringVar(value=tetel.tipus)
        kategoria = tk.StringVar(value=tetel.kategoria)
        megnevezes = tk.StringVar(value=tetel.megnevezes)
        osszeg = tk.StringVar(value=str(tetel.osszeg))
        ttk.Label(keret, text="Dátum:").pack(anchor="w")
        ttk.Entry(keret, textvariable=datum).pack(fill="x")
        ttk.Label(keret, text="Típus:").pack(anchor="w")
        ttk.Combobox(keret,textvariable=tipus,values=["Bevétel", "Kiadás"],state="readonly").pack(fill="x")
        ttk.Label(keret, text="Kategória:").pack(anchor="w")
        ttk.Combobox(keret,textvariable=kategoria,values=["Bevásárlás", "Lakhatás", "Utazás", "Szórakozás", "Fizetés","Hitel", "Edzés", "Előfizetések","Üzemanyag","Tömegközlekedés", "Ételek", "Italok","Fodrász","Gyógyszerek", "Egyéb"]).pack(fill="x")
        ttk.Label(keret, text="Megnevezés:").pack(anchor="w")
        ttk.Entry(keret, textvariable=megnevezes).pack(fill="x")
        ttk.Label(keret, text="Összeg (Ft):").pack(anchor="w")
        ttk.Entry(keret, textvariable=osszeg).pack(fill="x")

        def mentes():
            try:
                uj_datum = datetime.strptime(datum.get(), "%Y-%m-%d").date().isoformat()
                uj_osszeg = int(osszeg.get().replace(" ", ""))
                if uj_osszeg <= 0 or not megnevezes.get().strip():
                    raise ValueError
            except ValueError:
                messagebox.showerror("Hibás adat","Ellenőrizd a dátumot, megnevezést és összeget!",parent=ablak)
                return
            uj_tetel = TranzakcioLG(uj_datum,tipus.get(),kategoria.get(),megnevezes.get().strip(),uj_osszeg)
            self.tetelek[index] = uj_tetel
            if not self.mentes_lg():
                self.tetelek[index] = tetel
                return
            self.lista_frissitese_lg()
            ablak.destroy()
        ttk.Button(keret,text="Módosítás mentése",command=mentes).pack(pady=15)

    def kijelolt_torlese_lg(self):
        kijeloles = self.tabla.selection()
        if not kijeloles:
            messagebox.showinfo("Nincs kijelölés", "Először jelölj ki egy tételt!")
            return
        if not messagebox.askyesno("Törlés megerősítése", "Biztosan törlöd a kijelölt tételt?"):
            return
        index = int(kijeloles[0])
        tetel = self.tetelek.pop(index)
        if not self.mentes_lg():
            self.tetelek.insert(index, tetel)
            return
        self.lista_frissitese_lg()

    def mentes_lg(self):
        try:
            adatok_mentese_lg(ADATFAJL, self.tetelek)
            return True
        except OSError as hiba:
            messagebox.showerror("Mentési hiba", f"Nem sikerült menteni az adatokat: {hiba}")
            return False

    def lista_frissitese_lg(self):
            honapok = sorted({tetel.datum[:7]for tetel in self.tetelek},reverse=True )
            honapok_lista = ["Összes hónap"] + honapok
            self.honap_mezo["values"] = honapok_lista
            if self.honap_szuro.get() not in honapok_lista:
                self.honap_szuro.set("Összes hónap")
            for elem in self.tabla.get_children():
                self.tabla.delete(elem)
            szurt_tetelek = []
            for index, tetel in enumerate(self.tetelek):
                if self.szuro.get() not in ("Összes",tetel.tipus):
                    continue
                if self.honap_szuro.get() != "Összes hónap" and not tetel.datum.startswith(self.honap_szuro.get() + "-"):
                    continue
                szurt_tetelek.append(tetel)
                self.tabla.insert("","end", iid=str(index),values=(tetel.datum,
                        tetel.tipus, tetel.kategoria, tetel.megnevezes, penz_formaz_lg(tetel.osszeg)))
            bevetel, kiadas, egyenleg = osszesites_lg(szurt_tetelek)
            self.osszefoglalo.config(
                text=( f"Bevétel: {penz_formaz_lg(bevetel)}  |  " f"Kiadás: {penz_formaz_lg(kiadas)}  |"))
            szin = "#188038" if egyenleg >= 0 else "#c5221f"
            self.egyenleg_cimke.config(text=f"Egyenleg: {penz_formaz_lg(egyenleg)}",fg=szin)
            mai_nap = date.today()
            aktualis_honap = mai_nap.strftime("%Y-%m")
            havi_tetelek = [tetel for tetel in self.tetelek if tetel.datum.startswith(aktualis_honap + "-")]
            havi_bevetel, havi_kiadas, havi_egyenleg = (osszesites_lg(havi_tetelek))

            self.havi_osszefoglalo.config(
                text=( f"Aktuális hónap ({aktualis_honap}): " f"Bevétel: {penz_formaz_lg(havi_bevetel)}  |  " f"Kiadás: {penz_formaz_lg(havi_kiadas)}  |"))
            havi_szin = ("#188038" if havi_egyenleg >= 0 else "#c5221f")
            self.havi_egyenleg_cimke.config(text=f"Egyenleg: {penz_formaz_lg(havi_egyenleg)}",fg=havi_szin)

    def fizetes_beallitas_mentese_lg(self):
        try:
            with open(FIZETESFAJL, "w", encoding="utf-8") as fajl:
                json.dump(self.fizetes_beallitas,fajl,ensure_ascii=False,indent=2)
            return True
        except OSError as hiba:
            messagebox.showerror("Mentési hiba",f"Nem sikerült menteni a fizetés beállításait: {hiba}")
            return False

    def fizetesek_generalasa_lg(self):
        if not self.fizetes_beallitas:
            return
        beallitas = self.fizetes_beallitas
        ma = date.today()
        ev, honap = map(int, beallitas["kezdet"].split("-"))
        kezdet = date(ev, honap, 1)
        rogzített = set(beallitas.get("rogzitett", []))
        uj_honapok = []
        uj_tetelek = []
        aktualis = kezdet
        while aktualis <= ma:
            honap_azonosito = aktualis.strftime("%Y-%m")
            fizetesi_nap = min(int(beallitas["nap"]),calendar.monthrange(aktualis.year,aktualis.month)[1])
            fizetesi_datum = aktualis.replace(day=fizetesi_nap)
            if (fizetesi_datum <= ma and honap_azonosito not in rogzített):
                uj_tetelek.append(TranzakcioLG(fizetesi_datum.isoformat(),"Bevétel","Fizetés","Havi fizetés",int(beallitas["osszeg"]))                )
                uj_honapok.append(honap_azonosito)
            aktualis = (aktualis.replace(day=28) + timedelta(days=4)).replace(day=1)
        if not uj_tetelek:
            return
        self.tetelek.extend(uj_tetelek)
        if not self.mentes_lg():
            del self.tetelek[-len(uj_tetelek):]
            return
        beallitas["rogzitett"] = sorted(rogzített.union(uj_honapok))
        self.fizetes_beallitas_mentese_lg()

    def havi_fizetes_ablak_lg(self, elso=False):
        ablak = tk.Toplevel(self.root)
        ablak.title("Havi fizetés beállítása")
        ablak.geometry("420x300")
        ablak.resizable(False, False)
        ablak.transient(self.root)
        ablak.grab_set()
        keret = ttk.Frame(ablak, padding=20)
        keret.pack(fill="both", expand=True)
        beallitas = self.fizetes_beallitas or {}
        fizetes = tk.StringVar(value=str(beallitas.get("osszeg", "")))
        nap = tk.StringVar(value=str(beallitas.get("nap", 5)))
        ttk.Label(keret,text="Havi fizetés",font=("Arial", 15, "bold")).pack(pady=(0, 15))
        ttk.Label(keret,text="Fizetés összege (Ft):").pack(anchor="w")
        ttk.Entry(keret,textvariable=fizetes).pack(fill="x", pady=(0, 12))
        ttk.Label(keret,text="Jóváírás napja (1–31):").pack(anchor="w")
        ttk.Entry(keret,textvariable=nap).pack(fill="x", pady=(0, 12))
        ttk.Label(keret,text="A módosítás a jövőbeli jóváírásokra érvényes.",wraplength=370).pack(anchor="w")

        def mentes_lg():
            try:
                osszeg = int(fizetes.get().replace(" ", ""))
                fizetesi_nap = int(nap.get())
                if osszeg <= 0 or not 1 <= fizetesi_nap <= 31:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Hibás adat","Pozitív összeget és 1–31 közötti napot adj meg!",parent=ablak)
                return
            regi_beallitas = self.fizetes_beallitas
            if regi_beallitas:
                uj_beallitas = dict(regi_beallitas)
                uj_beallitas["osszeg"] = osszeg
                uj_beallitas["nap"] = fizetesi_nap
            else:
                uj_beallitas = {"osszeg": osszeg,"nap": fizetesi_nap,"kezdet": date.today().strftime("%Y-%m"),"rogzitett": []}
            self.fizetes_beallitas = uj_beallitas
            if not self.fizetes_beallitas_mentese_lg():
                self.fizetes_beallitas = regi_beallitas
                return
            if elso:
                uj_tetel = TranzakcioLG(date.today().isoformat(),"Bevétel","Fizetés","Havi fizetés",osszeg)
                self.tetelek.append(uj_tetel)
                if not self.mentes_lg():
                    self.tetelek.pop()
                    self.fizetes_beallitas = regi_beallitas
                    return
                uj_beallitas["rogzitett"].append(date.today().strftime("%Y-%m"))
                self.fizetes_beallitas_mentese_lg()
            self.fizetesek_generalasa_lg()
            self.lista_frissitese_lg()
            ablak.destroy()
        ttk.Button(keret,text="Fizetés mentése",command=mentes_lg).pack(pady=15)
        if elso:ablak.protocol("WM_DELETE_WINDOW",self.root.destroy)

    def diagram_valasztasa_lg(self):
            ablak = tk.Toplevel(self.root)
            ablak.title("Diagram kiválasztása")
            ablak.geometry("330x180")
            ablak.resizable(False, False)
            ablak.transient(self.root)
            ablak.grab_set()
            ttk.Label(ablak, text="Milyen diagramot szeretnél?", font=("Arial", 12, "bold")).pack(pady=20)
            def megnyitas_lg(havi):
                ablak.destroy()
                self.diagram_megjelenitese_lg(havi)
            ttk.Button(ablak, text="Teljes időszak",command=lambda: megnyitas_lg(False)).pack(pady=5)
            ttk.Button(ablak,text="Havi diagram",ommand=lambda: megnyitas_lg(True)).pack(pady=5)

    def diagram_megjelenitese_lg(self, havi):
            if havi:
                honap = self.honap_szuro.get()
                if honap == "Összes hónap":
                    honap = date.today().strftime("%Y-%m")
                tetelek = [tetel for tetel in self.tetelek if tetel.datum.startswith(honap + "-")]
                cim = f"Havi diagram – {honap}"
            else:
                tetelek = self.tetelek
                cim = "Teljes időszak diagramja"
            bevetel, kiadas, egyenleg = osszesites_lg(tetelek)
            ablak = tk.Toplevel(self.root)
            ablak.title(cim)
            ablak.geometry("650x470")
            ttk.Label( ablak,text=cim,font=("Arial", 16, "bold")).pack(pady=15)
            vaszon = tk.Canvas(ablak,width=600,height=310,bg="white",highlightthickness=0)
            vaszon.pack(pady=10)
            adatok = [("Bevétel", bevetel, "#259b50"),("Kiadás", kiadas, "#d64545")]
            maximum = max(bevetel, kiadas, 1)
            for index, (nev, ertek, szin) in enumerate(adatok):
                x = 155 + index * 230
                magassag = 220 * ertek / maximum
                vaszon.create_rectangle(x, 250 - magassag,x + 110, 250,fill=szin,outline="" )
                vaszon.create_text(x + 55,265,text=nev,font=("Arial", 12, "bold"))
                vaszon.create_text(x + 55, max(15, 235 - magassag),text=penz_formaz_lg(ertek),font=("Arial", 10))
            egyenleg_szin = ("#188038" if egyenleg >= 0 else "#c5221f")
            ttk.Label(ablak,text="Összesített egyenleg:").pack()
            tk.Label(ablak,text=penz_formaz_lg(egyenleg),font=("Arial", 15, "bold"),fg=egyenleg_szin).pack(pady=5)

    def csv_exportalas_lg(self):
                fajlnev = filedialog.asksaveasfilename(title="Tételek exportálása",defaultextension=".csv",filetypes=[("CSV-fájl", "*.csv")],initialfile="koltsegnyilvantarto.csv")
                if not fajlnev:
                    return
                try:
                    with open(fajlnev, "w",newline="",encoding="utf-8-sig") as fajl:
                        iro = csv.writer(fajl, delimiter=";")
                        iro.writerow(["Dátum","Típus","Kategória","Megnevezés","Összeg (Ft)"])
                        for tetel in self.tetelek:
                            if (self.szuro.get() != "Összes"and tetel.tipus != self.szuro.get()):
                                continue
                            if (self.honap_szuro.get() != "Összes hónap" and not tetel.datum.startswith(self.honap_szuro.get() + "-")):
                                continue
                            iro.writerow([tetel.datum,tetel.tipus,tetel.kategoria,tetel.megnevezes,tetel.osszeg])
                    messagebox.showinfo("Sikeres exportálás","A CSV-fájl sikeresen elkészült!")
                except OSError as hiba:
                    messagebox.showerror("Exportálási hiba",str(hiba)),

    def minden_tetel_torlese_lg(self):
        if not self.tetelek:
            messagebox.showinfo("Nincs törölhető tétel","A lista már üres!")
            return
        megerosites = messagebox.askyesno(
            "Minden tétel törlése","Biztosan törölni szeretnéd az összes tételt?\n\n""Ez a művelet nem vonható vissza!" )
        if not megerosites:
            return
        try:
            adatok_mentese_lg(ADATFAJL, [])
        except OSError as hiba:
            messagebox.showerror("Törlési hiba",f"Nem sikerült törölni a tételeket: {hiba}")
            return
        self.tetelek.clear()
        self.lista_frissitese()
        messagebox.showinfo("Sikeres törlés","Minden tétel véglegesen törölve lett!")

if __name__ == "__main__":
    root = tk.Tk()
    app = KoltsegNyilvantartoLG(root)
    root.mainloop()
