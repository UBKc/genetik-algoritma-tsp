"""Yöntemleri 4 TSPLIB probleminde karşılaştırır.

Genetik algoritma rastgele olduğu için her ayar 10 farklı seed ile çalıştırılıyor,
ortalama ve en iyi sonuç raporlanıyor. Sapma (%) bilinen optimuma göre:
    (bulunan - optimum) / optimum * 100

Sonuçlar sonuclar/ klasörüne csv ve grafik olarak kaydediliyor.

Kullanım:
    python karsilastir.py
"""
import csv
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import tsplib
import yontemler

PROBLEMLER = ["eil51", "berlin52", "st70", "kroA100"]
SEEDLER = range(10)

GA_AYARLARI = {
    # Ödevde kullandığım ayarlar
    "GA (ödev ayarları)": dict(pop_boyutu=100, nesil=200, mutasyon=0.1, elitizm=2, secim="ilk20"),
    # Turnuva seçimi, daha büyük popülasyon ve daha uzun çalışma
    "GA (turnuva)": dict(pop_boyutu=300, nesil=2000, mutasyon=0.2, elitizm=2, secim="turnuva"),
    # Memetik: her çocuğa 2-opt, küçük popülasyon yetiyor
    "Memetik GA": dict(pop_boyutu=30, nesil=100, mutasyon=0.2, elitizm=2, secim="turnuva",
                       turnuva_boyutu=3, yerel_arama=True),
}

SONUC = Path("sonuclar")


def sapma(uzunluk, optimum):
    return (uzunluk - optimum) / optimum * 100


def main():
    SONUC.mkdir(exist_ok=True)
    satirlar = []
    gecmisler = {}
    en_iyi_turlar = {}

    for ad in PROBLEMLER:
        koordinat = tsplib.tsp_oku(f"veri/{ad}.tsp")
        mesafe = tsplib.mesafe_matrisi(koordinat)
        optimum = tsplib.OPTIMUM[ad]
        n = len(mesafe)
        print(f"\n=== {ad} ({n} şehir, optimum {optimum}) ===")

        # En yakın komşu her şehirden başlatılıyor, en iyisi alınıyor
        t0 = time.time()
        nn_turlar = [yontemler.en_yakin_komsu(mesafe, s) for s in range(n)]
        nn_uzunluk = [tsplib.tur_uzunlugu(t, mesafe) for t in nn_turlar]
        sure = (time.time() - t0) / n
        satirlar.append([ad, "En yakın komşu", min(nn_uzunluk), np.mean(nn_uzunluk), sure])

        # En yakın komşu + 2-opt, yine her başlangıç şehri için
        t0 = time.time()
        opt_uzunluk = [tsplib.tur_uzunlugu(yontemler.iki_opt(t, mesafe), mesafe) for t in nn_turlar]
        sure = (time.time() - t0) / n
        satirlar.append([ad, "En yakın komşu + 2-opt", min(opt_uzunluk), np.mean(opt_uzunluk), sure])

        for ga_adi, ayar in GA_AYARLARI.items():
            uzunluklar, uzunluklar_2opt, sureler = [], [], []
            for seed in SEEDLER:
                t0 = time.time()
                tur, gecmis = yontemler.genetik_algoritma(mesafe, seed=seed, **ayar)
                sureler.append(time.time() - t0)
                uzunluklar.append(tsplib.tur_uzunlugu(tur, mesafe))

                if ga_adi == "GA (turnuva)":
                    tur2 = yontemler.iki_opt(tur, mesafe)
                    uzunluklar_2opt.append(tsplib.tur_uzunlugu(tur2, mesafe))
                    if seed == 0:
                        gecmisler[ad] = gecmis
                elif seed == 0:
                    gecmisler[(ad, ga_adi)] = gecmis

                # berlin52 için memetik GA'nın bulduğu en iyi tur çizilecek
                if ad == "berlin52" and ga_adi == "Memetik GA":
                    if ad not in en_iyi_turlar or uzunluklar[-1] < tsplib.tur_uzunlugu(en_iyi_turlar[ad], mesafe):
                        en_iyi_turlar[ad] = tur

            optimum_sayisi = sum(u == optimum for u in uzunluklar)
            satirlar.append([ad, ga_adi, min(uzunluklar), np.mean(uzunluklar), np.mean(sureler)])
            print(f"{ga_adi}: {len(SEEDLER)} çalıştırmanın {optimum_sayisi} tanesi optimumu buldu")
            if uzunluklar_2opt:
                satirlar.append([ad, "GA (turnuva) + 2-opt", min(uzunluklar_2opt),
                                 np.mean(uzunluklar_2opt), np.mean(sureler)])

        for s in satirlar[-6:]:
            print(f"{s[1]:<26} en iyi {s[2]:>8.0f} (%{sapma(s[2], optimum):5.2f})"
                  f"   ortalama {s[3]:>9.1f} (%{sapma(s[3], optimum):5.2f})   {s[4]:.2f} sn")

    # CSV kaydı
    with open(SONUC / "karsilastirma.csv", "w", newline="", encoding="utf-8") as f:
        yazici = csv.writer(f)
        yazici.writerow(["problem", "yontem", "en_iyi", "ortalama", "en_iyi_sapma_yuzde",
                         "ortalama_sapma_yuzde", "sure_sn"])
        for ad, yontem, en_iyi, ort, sure in satirlar:
            opt = tsplib.OPTIMUM[ad]
            yazici.writerow([ad, yontem, int(en_iyi), round(ort, 1), round(sapma(en_iyi, opt), 2),
                             round(sapma(ort, opt), 2), round(sure, 3)])

    # Yakınsama grafiği: berlin52, üç GA ayarı
    plt.figure(figsize=(8, 4.5))
    cizgiler = [
        (gecmisler[("berlin52", "GA (ödev ayarları)")], "GA (ödev ayarları, 200 nesil)"),
        (gecmisler["berlin52"], "GA (turnuva, 2000 nesil)"),
        (gecmisler[("berlin52", "Memetik GA")], "Memetik GA (100 nesil)"),
    ]
    for gecmis, etiket in cizgiler:
        plt.plot(range(1, len(gecmis) + 1), gecmis, label=etiket)
    plt.axhline(tsplib.OPTIMUM["berlin52"], color="gray", linestyle="--", label="optimum (7542)")
    plt.xscale("log")
    plt.xlabel("Nesil (log ölçek)")
    plt.ylabel("En iyi tur uzunluğu")
    plt.title("berlin52 - yakınsama (seed 0)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(SONUC / "yakinsama_berlin52.png", dpi=120)

    # En iyi berlin52 turunun çizimi
    koordinat = tsplib.tsp_oku("veri/berlin52.tsp")
    mesafe = tsplib.mesafe_matrisi(koordinat)
    tur = en_iyi_turlar["berlin52"] + [en_iyi_turlar["berlin52"][0]]
    plt.figure(figsize=(7, 5))
    plt.plot(koordinat[tur, 0], koordinat[tur, 1], "-o", markersize=4)
    plt.title(f"berlin52 - Memetik GA, uzunluk {tsplib.tur_uzunlugu(tur[:-1], mesafe):.0f}")
    plt.tight_layout()
    plt.savefig(SONUC / "en_iyi_tur_berlin52.png", dpi=120)
    print("\nSonuçlar sonuclar/ klasörüne kaydedildi.")


if __name__ == "__main__":
    main()
