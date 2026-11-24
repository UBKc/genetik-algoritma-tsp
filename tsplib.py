"""TSPLIB formatındaki .tsp dosyalarını okuma ve mesafe matrisi oluşturma."""
from pathlib import Path

import numpy as np

# TSPLIB sitesinde yayınlanan bilinen en iyi tur uzunlukları
OPTIMUM = {
    "berlin52": 7542,
    "eil51": 426,
    "st70": 675,
    "kroA100": 21282,
}


def tsp_oku(dosya_yolu):
    """NODE_COORD_SECTION altındaki koordinatları okur, (n, 2) dizi döndürür."""
    satirlar = Path(dosya_yolu).read_text().splitlines()
    koordinatlar = []
    okuyor = False

    for satir in satirlar:
        satir = satir.strip()
        if satir.startswith("NODE_COORD_SECTION"):
            okuyor = True
            continue
        if not okuyor or not satir or satir == "EOF":
            continue
        _, x, y = satir.split()[:3]
        koordinatlar.append((float(x), float(y)))

    return np.array(koordinatlar)


def mesafe_matrisi(koordinatlar):
    """EUC_2D mesafe: Öklid mesafesi en yakın tam sayıya yuvarlanıyor (TSPLIB kuralı)."""
    fark = koordinatlar[:, None, :] - koordinatlar[None, :, :]
    return np.floor(np.sqrt((fark ** 2).sum(axis=2)) + 0.5)


def tur_uzunlugu(tur, mesafe):
    """Tur kapalı kabul ediliyor, son şehirden ilk şehre dönüş de ekleniyor."""
    tur = np.asarray(tur)
    return float(mesafe[tur, np.roll(tur, -1)].sum())
