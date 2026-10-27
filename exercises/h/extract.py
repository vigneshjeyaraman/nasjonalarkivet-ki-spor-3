# extract.py - lag rapport over saksmapper
# bruk: python3 extract.py cases.csv 1990 [1999]
#
# Leser en semikolonseparert eksport (id;saksnr;tittel;dato;gradert;arkivdel)
# og skriver en rapport over saker i et årsintervall, gruppert på arkivdel.
# Utskriften skal være identisk med den gamle versjonen (se old-*.txt).
import csv
import sys

INGEN_SLUTT = 9999  # til-år når det ikke er oppgitt; overskriften ender da med "-"
MAKS_TITTEL = 40
STREK = "=" * 40
GRADERT_VERDIER = ("J", "j", "ja")

SAKSNR, TITTEL, DATO, GRADERT, ARKIVDEL = 1, 2, 3, 4, 5


def les_aar(argv):
    fra = int(argv[2])
    try:
        til = int(argv[3])
    except (IndexError, ValueError):
        til = INGEN_SLUTT
    return fra, til


def les_rader(filnavn):
    with open(filnavn, encoding="utf-8") as fil:
        return [r for r in csv.reader(fil, delimiter=";") if r[0] != "id"]


def aar_for(rad):
    """Året i datoen, eller None når datoen mangler eller ikke er et tall."""
    try:
        return int(rad[DATO][:4])
    except (IndexError, ValueError):
        return None


def arkivdel_for(rad):
    # Bare et helt tomt felt blir UKJENT. Et felt med bare mellomrom blir "".
    if rad[ARKIVDEL] == "":
        return "UKJENT"
    return rad[ARKIVDEL].strip().upper()


def kort_tittel(tittel):
    if len(tittel) > MAKS_TITTEL:
        return tittel[:MAKS_TITTEL - 3] + "..."
    return tittel


def grupper(rader, fra, til):
    """Returnerer saker per arkivdel, antall i intervallet og antall uten dato.

    Saker uten dato telles som hoppet over uansett intervall.
    """
    grupper = {}
    antall = 0
    hoppet = 0
    for rad in rader:
        aar = aar_for(rad)
        if aar is None:
            hoppet += 1
            continue
        if fra <= aar <= til:
            grupper.setdefault(arkivdel_for(rad), []).append(rad)
            antall += 1
    return grupper, antall, hoppet


def skriv_rapport(grupper, antall, hoppet, fra, til):
    slutt = "" if til == INGEN_SLUTT else str(til)
    print(f"Rapport saksmapper {fra}-{slutt}")
    print(STREK)
    for arkivdel in sorted(grupper):
        saker = grupper[arkivdel]
        print(f"{arkivdel} ({len(saker)})")
        for rad in sorted(saker, key=lambda r: r[DATO]):
            gradert = " [GRADERT]" if rad[GRADERT] in GRADERT_VERDIER else ""
            print(f"  {rad[SAKSNR]}  {rad[DATO]}  {kort_tittel(rad[TITTEL])}{gradert}")
    print(STREK)
    print(f"Totalt: {antall}")
    if hoppet > 0:
        print(f"Hoppet over (mangler dato): {hoppet}")


def main(argv):
    fra, til = les_aar(argv)
    rader = les_rader(argv[1])
    skriv_rapport(*grupper(rader, fra, til), fra, til)


if __name__ == "__main__":
    main(sys.argv)
