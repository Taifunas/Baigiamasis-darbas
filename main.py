import sys
import time
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMessageBox,
    QTableWidgetItem, QTableWidget
)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from skelbiu_ui import Ui_Form
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse, urlunparse

class SkelbiuApp(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Skelbiu.lt sąsaja")
        self.resize(600, 400)
        self.setupUi(self)

        self.driver = None
        self.pagrindinis_url = ""
        self.paskutinis_soup = None
        self.paskutinis_url = None

        if not isinstance(self.categories_table, QTableWidget):
            raise TypeError("categories_table turi būti QTableWidget!")

        for widget in [
            self.search_input, self.ieskoti, self.paieska_label,
            self.categories_table, self.back,
            self.min_price, self.max_price,
            self.min_price_label, self.max_price_label,
            self.filter_button, self.psl_skaicius,
            self.max_page, self.issaugoti_button
        ]:
            widget.setDisabled(True)

        self.checkBtn.clicked.connect(self.patikrinti_nuoroda)
        self.quit.clicked.connect(self.close)
        self.ieskoti.clicked.connect(self.ivesti_paieska)
        self.search_input.returnPressed.connect(self.ivesti_paieska)
        self.categories_table.cellClicked.connect(self.atidaryti_kategorija)
        self.back.clicked.connect(self.grizti_atgal)
        self.filter_button.clicked.connect(self.filtruoti_pagal_kaina)
        self.issaugoti_button.clicked.connect(self.issaugoti_i_csv)
        self.next_page.clicked.connect(lambda: self.eiti_i_puslapi("next"))
        self.page_back.clicked.connect(lambda: self.eiti_i_puslapi("prev"))
        self.rusiavimas_dropdown.currentIndexChanged.connect(self.taikyti_rusiavima)

    def taikyti_rusiavima(self):
        try:
            # Gauti pasirinktą "data-order" reikšmę
            data_order = self.rusiavimas_dropdown.currentData()
            if data_order is None or not self.driver:
                return

            # Ieškoti visų rūšiavimo <span> ir rasti atitinkamą
            spanai = self.driver.find_elements(By.CSS_SELECTOR, "#orderByLinks span")

            for span in spanai:
                if span.get_attribute("data-order") == data_order:
                    self.driver.execute_script("arguments[0].click();", span)
                    break

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "extended-info"))
            )
            time.sleep(1)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            self.atvaizduoti_skelbimus(soup)

        except Exception as e:
            QMessageBox.warning(self, "Klaida", f"Nepavyko taikyti rūšiavimo: {str(e)}")


    def eiti_i_puslapi(self, kryptis="next"):
        try:
            selector = f"a.pagination_link[rel='{kryptis}']"
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

            if not elements:
                if kryptis == "next":
                    QMessageBox.information(
                        self, "Puslapio nėra", f"Nėra daugiau puslapių į šią pusę."
                    )
                    return
                else:
                    return

            btn = elements[0]
            self.driver.execute_script("arguments[0].click();", btn)

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "extended-info"))
            )
            time.sleep(1)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            self.atvaizduoti_skelbimus(soup)
            #self.atnaujinti_rusiavima(soup)

        except Exception as e:
            QMessageBox.information(
                self, "Klaida", f"Klaida einant į puslapį '{kryptis}': {str(e)}"
            )

    def atnaujinti_rusiavima(self, soup):
        try:
            rikiavimas_blokas = soup.find("div", id="orderByLinks")
            spanai = rikiavimas_blokas.find_all("span")

            self.rusiavimas_dropdown.clear()  # Išvalyti prieš dedant naujus

            for span in spanai:
                tekstas = span.get_text(strip=True)
                data_order = span.get("data-order")
                if tekstas and data_order is not None:
                    self.rusiavimas_dropdown.addItem(tekstas, data_order)

            self.rusiavimas_dropdown.setDisabled(False)

        except Exception as e:
            print(f"Klaida atnaujinant rūšiavimą: {e}")
            self.rusiavimas_dropdown.setDisabled(True)


    def patikrinti_nuoroda(self):
        url = self.url.text().strip()
        if not url:
            QMessageBox.warning(self, "Tuščias laukas", "Įveskite nuorodą.")
            return
        if not url.startswith("http"):
            url = "https://" + url
        if "." not in url or " " in url:
            QMessageBox.warning(self, "Netinkamas formatas", "Įveskite tinkamos formos URL.")
            return

        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                QMessageBox.warning(self, "Nepavyko prisijungti", f"HTTP kodas: {r.status_code}")
                return
        except Exception:
            QMessageBox.critical(self, "Klaida", "Nepavyko pasiekti nuorodos.")
            return

        try:
            if self.driver:
                self.driver.quit()
            self.driver = webdriver.Chrome()
            self.driver.get(url)
            self.driver.maximize_window()
            time.sleep(2)
            self.pagrindinis_url = url

            try:
                slapukai = self.driver.find_element(By.ID, "onetrust-reject-all-handler")
                slapukai.click()
                time.sleep(1)
            except:
                pass

            self.search_input.setDisabled(False)
            self.ieskoti.setDisabled(False)
            self.paieska_label.setDisabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Klaida", f"Nepavyko prisijungti prie puslapio: {str(e)}")

    def ivesti_paieska(self):
        fraze = self.search_input.text().strip()
        if not fraze or not self.driver:
            return

        try:
            self.driver.get(self.pagrindinis_url)
            paieskos_laukas = self.driver.find_element(By.ID, "searchKeyword")
            paieskos_laukas.clear()
            paieskos_laukas.send_keys(fraze)
            ieskoti_mygtukas = self.driver.find_element(By.ID, "searchButton")
            ieskoti_mygtukas.click()
            time.sleep(2)

            try:
                rodyti_likusias_kategorijas = self.driver.find_element(By.ID, "show_rest_popular_categories")
                rodyti_likusias_kategorijas.click()
                time.sleep(2)
            except:
                pass

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            self.paskutinis_url = self.driver.current_url
            self.atvaizduoti_kategorijas(soup)

        except Exception as e:
            QMessageBox.warning(self, "Klaida", f"Nepavyko atlikti paieškos: {str(e)}")

    def atvaizduoti_kategorijas(self, soup):
        kategorijos = soup.find_all("a", class_="popular_categories_link")
        if not kategorijos:
            QMessageBox.information(self, "Nėra", "Pagal paiešką nerasta kategorijų.")
            return

        self.rusiavimas_dropdown.setDisabled(True)
        self.paskutinis_soup = soup
        self.categories_table.clear()
        self.categories_table.setColumnCount(1)
        self.categories_table.setRowCount(len(kategorijos))
        self.categories_table.setHorizontalHeaderLabels(["Kategorijos"])

        for i, kat in enumerate(kategorijos):
            tekstas = kat.get_text(strip=True)
            href = kat.get("href", "")
            item = QTableWidgetItem(tekstas)
            item.setData(1000, href)
            self.categories_table.setItem(i, 0, item)

        self.categories_table.setDisabled(False)
        self.back.setDisabled(False)
        self.atnaujinti_kainos_filtra_matomuma()

    def atidaryti_kategorija(self, row, column):
        item = self.categories_table.item(row, column)
        if not item:
            return

        href = item.data(1000)

        if href is None:
            return

        if not href.startswith("http"):
            href = self.pagrindinis_url.rstrip("/") + href

        try:
            self.driver.get(href)
            time.sleep(2)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            self.atvaizduoti_skelbimus(soup)
            self.atnaujinti_rusiavima(soup)
        except Exception as e:
            QMessageBox.warning(self, "Klaida", f"Nepavyko atidaryti kategorijos: {str(e)}")


    def atvaizduoti_skelbimus(self, soup):
        self.categories_table.clear()
        self.categories_table.setColumnCount(2)
        self.categories_table.setHorizontalHeaderLabels(["Pavadinimas", "Kaina"])

        skelbimu_blokai = soup.find_all("div", class_="extended-info")
        if not skelbimu_blokai:
            QMessageBox.information(self, "Nėra", "Šioje kategorijoje nerasta skelbimų.")
            return

        self.categories_table.setRowCount(len(skelbimu_blokai))

        for i, blokas in enumerate(skelbimu_blokai):
            title_div = blokas.find("div", class_="title")
            kaina_div = blokas.find("div", class_="price")

            pavadinimas = title_div.get_text(strip=True) if title_div else "Be pavadinimo"
            kaina = kaina_div.get_text(strip=True) if kaina_div else "Be kainos"

            self.categories_table.setItem(i, 0, QTableWidgetItem(pavadinimas))
            self.categories_table.setItem(i, 1, QTableWidgetItem(kaina))

        for widget in [self.max_page, self.issaugoti_button, self.psl_skaicius]:
            widget.setDisabled(False)

        self.atnaujinti_kainos_filtra_matomuma()

    def filtruoti_pagal_kaina(self):
        if not self.driver:
            QMessageBox.warning(self, "Klaida", "Puslapis dar nebuvo atidarytas.")
            return

        min_kaina = self.min_price.text().strip()
        max_kaina = self.max_price.text().strip()

        try:
            min_input = self.driver.find_element(By.ID, "costFromInput")
            max_input = self.driver.find_element(By.ID, "costTillInput")

            min_input.clear()
            max_input.clear()

            if min_kaina:
                min_input.send_keys(min_kaina)
            if max_kaina:
                max_input.send_keys(max_kaina)

            filter_btn = self.driver.find_element(By.ID, "searchButtonFilter")
            filter_btn.click()

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "extended-info"))
            )

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            self.atvaizduoti_skelbimus(soup)
            self.atnaujinti_rusiavima(soup)

        except Exception as e:
            QMessageBox.critical(self, "Klaida", f"Nepavyko atlikti filtravimo: {str(e)}")


    def issaugoti_i_csv(self):
        if not self.driver:
            QMessageBox.warning(self, "Klaida", "Puslapis dar nebuvo atidarytas.")
            return

        max_skelbimu_tekstas = self.max_page.text().strip()
        try:
            max_skelbimu = int(max_skelbimu_tekstas)
            if max_skelbimu <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Klaida", "Įveskite galiojantį skelbimų kiekį.")
            return

        visi_skelbimai = []
        bendra_kainu_suma = 0.0

        while len(visi_skelbimai) < max_skelbimu:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "extended-info"))
                )
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                skelbimu_blokai = soup.find_all("div", class_="extended-info")

                if not skelbimu_blokai:
                    break

                for blokas in skelbimu_blokai:
                    if len(visi_skelbimai) >= max_skelbimu:
                        break

                    title_div = blokas.find("div", class_="title")
                    kaina_div = blokas.find("div", class_="price")

                    pavadinimas = title_div.get_text(strip=True) if title_div else "Be pavadinimo"
                    kaina = kaina_div.get_text(strip=True) if kaina_div else "Be kainos"

                    visi_skelbimai.append((pavadinimas, kaina))

                    try:
                        kaina_val = float(kaina.replace("€", "").replace(" ", "").replace(",", "."))
                        bendra_kainu_suma += kaina_val
                    except:
                        pass

                if len(visi_skelbimai) < max_skelbimu:
                    try:
                        next_btn = self.driver.find_element(By.CSS_SELECTOR, "a.pagination_link[rel='next']")
                        self.driver.execute_script("arguments[0].click();", next_btn)
                        time.sleep(1)
                    except Exception:
                        break  # Jei nėra daugiau puslapių – sustojam

            except Exception as e:
                QMessageBox.warning(self, "Klaida", f"Klaida puslapyje: {str(e)}")
                break

        if not visi_skelbimai:
            QMessageBox.information(self, "Nėra duomenų", "Nėra skelbimų, kuriuos būtų galima išsaugoti.")
            return

        try:
            with open("skelbimai.csv", mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Pavadinimas", "Kaina"])
                writer.writerows(visi_skelbimai)

            papildoma_info = ""
            if len(visi_skelbimai) < max_skelbimu:
                papildoma_info = (
                    f"\n⚠️ Įvestas kiekis ({max_skelbimu}) viršijo rastų skelbimų skaičių.\n"
                    f"Išsaugota tik {len(visi_skelbimai)} skelbimų."
                )

            QMessageBox.information(
                self,
                "Išsaugota",
                f"Išsaugota {len(visi_skelbimai)} skelbimų į skelbimai.csv\n"
                f"Bendra skelbimų vertė: {bendra_kainu_suma:.2f} €{papildoma_info}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Klaida", f"Nepavyko išsaugoti CSV: {str(e)}")



    def grizti_atgal(self):
        if self.paskutinis_soup:
            self.atvaizduoti_kategorijas(self.paskutinis_soup)
        if self.paskutinis_url:
            try:
                self.driver.get(self.paskutinis_url)
            except Exception as e:
                QMessageBox.warning(self, "Klaida", f"Nepavyko grįžti atgal: {str(e)}")

    def atnaujinti_kainos_filtra_matomuma(self):
        rodyti_filtra = self.categories_table.columnCount() == 2
        for widget in [
            self.min_price, self.max_price,
            self.min_price_label, self.max_price_label,
            self.filter_button, self.issaugoti_button, self.max_page, self.psl_skaicius, self.next_page, self.page_back, self.rusiavimas_dropdown
        ]:
            widget.setDisabled(not rodyti_filtra)

    def closeEvent(self, event):
        if self.driver:
            self.driver.quit()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SkelbiuApp()
    window.show()
    sys.exit(app.exec())