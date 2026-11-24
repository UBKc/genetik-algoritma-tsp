"""TSP çözüm yöntemleri: en yakın komşu, 2-opt ve genetik algoritma.

Turlar 0 numaralı şehirden başlayıp oraya dönüyor. Genetik algoritmada birey
sadece 1..n-1 şehirlerinin sırası, başlangıç şehri sabit (ödevdeki gibi).
"""
import random

import numpy as np


def en_yakin_komsu(mesafe, baslangic=0):
    """Her adımda henüz gidilmemiş en yakın şehre gider."""
    n = len(mesafe)
    tur = [baslangic]
    ziyaret = np.zeros(n, dtype=bool)
    ziyaret[baslangic] = True

    for _ in range(n - 1):
        satir = np.where(ziyaret, np.inf, mesafe[tur[-1]])
        sonraki = int(np.argmin(satir))
        tur.append(sonraki)
        ziyaret[sonraki] = True

    # Başlangıç şehri 0 olacak şekilde döndürülüyor
    i = tur.index(0)
    return tur[i:] + tur[:i]


def iki_opt(tur, mesafe):
    """2-opt yerel arama: iki kenarı çıkarıp aradaki parçayı ters çevirerek
    tur kısalıyorsa uygular, iyileşme kalmayana kadar devam eder."""
    tur = np.array(tur)
    n = len(tur)
    iyilesti = True

    while iyilesti:
        iyilesti = False
        for i in range(1, n - 1):
            a, b = tur[i - 1], tur[i]
            # i'den sonraki tüm j'ler için kazanç tek seferde hesaplanıyor
            j = np.arange(i + 1, n)
            c, d = tur[j], tur[(j + 1) % n]
            kazanc = mesafe[a, b] + mesafe[c, d] - mesafe[a, c] - mesafe[b, d]
            en_iyi = int(np.argmax(kazanc))
            if kazanc[en_iyi] > 1e-9:
                j = i + 1 + en_iyi
                tur[i:j + 1] = tur[i:j + 1][::-1]
                iyilesti = True

    return tur.tolist()


def _ox_crossover(p1, p2, rastgele):
    # Ordered Crossover: birinci ebeveynden bir parça alınıyor, kalan şehirler
    # ikinci ebeveyndeki sırayla dolduruluyor, böylece şehir tekrarı olmuyor
    boyut = len(p1)
    a, b = sorted(rastgele.sample(range(boyut), 2))
    cocuk = [None] * boyut
    cocuk[a:b] = p1[a:b]

    alinan = set(p1[a:b])
    kalan = [s for s in p2 if s not in alinan]
    idx = 0
    for i in range(boyut):
        if cocuk[i] is None:
            cocuk[i] = kalan[idx]
            idx += 1
    return cocuk


def _inversion_mutasyon(birey, oran, rastgele):
    # Rastgele bir parçayı ters çeviriyor (2-opt hamlesiyle aynı mantık)
    if rastgele.random() < oran:
        a, b = sorted(rastgele.sample(range(len(birey)), 2))
        birey[a:b] = birey[a:b][::-1]
    return birey


def _populasyon_mesafeleri(pop, mesafe):
    # Tüm popülasyonun tur uzunlukları tek numpy işlemiyle hesaplanıyor
    n_birey = len(pop)
    turlar = np.hstack([np.zeros((n_birey, 1), dtype=int), np.array(pop)])
    return mesafe[turlar, np.roll(turlar, -1, axis=1)].sum(axis=1)


def genetik_algoritma(
    mesafe,
    pop_boyutu=100,
    nesil=200,
    mutasyon=0.1,
    elitizm=2,
    secim="ilk20",
    turnuva_boyutu=5,
    yerel_arama=False,
    seed=0,
):
    """Genetik algoritma ile TSP çözümü.

    secim="ilk20": ödevdeki yöntem, ebeveynler en iyi 20 bireyden rastgele seçiliyor.
    secim="turnuva": her ebeveyn için popülasyondan turnuva_boyutu kadar birey
    çekilip en iyisi alınıyor, çeşitlilik daha uzun korunuyor.

    yerel_arama=True: memetik algoritma, üretilen her çocuğa 2-opt uygulanıyor.
    GA turun genel yapısını keşfediyor, 2-opt ise her bireyi en yakın yerel
    optimuma taşıyor.

    Döndürdüğü değerler: en iyi tur (0 ile başlayan), her nesildeki en iyi mesafe listesi
    """
    rastgele = random.Random(seed)
    sehirler = list(range(1, len(mesafe)))
    pop = [rastgele.sample(sehirler, len(sehirler)) for _ in range(pop_boyutu)]
    if yerel_arama:
        pop = [iki_opt([0] + b, mesafe)[1:] for b in pop]
    gecmis = []

    for _ in range(nesil):
        uzunluklar = _populasyon_mesafeleri(pop, mesafe)
        sira = np.argsort(uzunluklar)
        pop = [pop[i] for i in sira]
        uzunluklar = uzunluklar[sira]
        gecmis.append(float(uzunluklar[0]))

        yeni_pop = [list(b) for b in pop[:elitizm]]
        while len(yeni_pop) < pop_boyutu:
            if secim == "turnuva":
                # Popülasyon sıralı olduğu için en küçük indeks en iyi birey
                e1 = pop[min(rastgele.sample(range(pop_boyutu), turnuva_boyutu))]
                e2 = pop[min(rastgele.sample(range(pop_boyutu), turnuva_boyutu))]
            else:
                e1, e2 = rastgele.sample(pop[:20], 2)
            cocuk = _ox_crossover(e1, e2, rastgele)
            cocuk = _inversion_mutasyon(cocuk, mutasyon, rastgele)
            if yerel_arama:
                # 2-opt fonksiyonu 0 ile başlayan tam tur bekliyor
                cocuk = iki_opt([0] + cocuk, mesafe)[1:]
            yeni_pop.append(cocuk)
        pop = yeni_pop

    uzunluklar = _populasyon_mesafeleri(pop, mesafe)
    en_iyi = pop[int(np.argmin(uzunluklar))]
    gecmis.append(float(uzunluklar.min()))
    return [0] + list(en_iyi), gecmis
