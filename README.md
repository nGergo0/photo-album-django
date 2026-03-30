# Felhőalapú Elosztott Rendszerek Labor - Photo Album

## Overview
A Photo Album egy Django alapú webalkalmazás, ahol a regisztrált felhasználók képeket nézegethetnek és tölthetnek fel.
Az alkalmazás konténerizált, ezért futtatható lokálisan Docker Compose-szal és a feladat elvárásainak megfelelően PaaS környezetben is. A választott platform: OpenShift.

## Funkciók
- Felhasználói regisztráció, bejelentkezés, kijelentkezés
- Képfeltöltés
- Képek listázása és rendezése (név vagy feltöltési dátum szerint)
- Kép részletező oldal
- Saját képek törlése (staff jogosultsággal bármely kép törölhető)
- Readiness endpoint adatbázis-kapcsolat-ellenőrzéssel: `/health/ready/`
- Django admin felület: `/admin`

## Tech Stack
- Python 3.12
- Django 5.2.11
- PostgreSQL
- Gunicorn
- Docker és Docker Compose
- OpenShift

## Lokális futtatás (Docker Compose)

### Indítás

```bash
docker compose up --build
```

### Admin felhasználó létrehozása (opcionális)

```bash
docker compose exec web python manage.py createsuperuser
```

### Leállítás

```bash
docker compose down
```

## Telepítés OpenShift-ben

Az open shift projekt létrehozása után először az adatbázis-szervert telepítettem egy postgres template segíségével. A postgres pvc-t használ az adatok tárolására.
Ezután az `Import from Git` funkcióval hoztam létre az Photo Album alkalmazást. A megfelelő konfigurációk után az alábbi erőforrások jöttek létre:
 - Deployment
 - Pod
 - Service
 - Route
 - BuildConfig

A Route-ban beállított publikus domain: [photo-album-photo-album-pibk75.apps.okd.fured.cloud.bme.hu](https://photo-album-photo-album-pibk75.apps.okd.fured.cloud.bme.hu/).

A médiafájlok perzisztens tárolására egy PVC volume-t csatoltam az alkalmazáshoz.

## Build
A container image buildelését az OpenShift végzi, amely GitHub webhook segítségével push hatására triggerelhető.

### Migrációk
A konténer indítási parancsa a Gunicorn start előtt futtatja a migrációkat.

## Konfiguráció
A konfigurációs változók mintája az [.env.example](.env.example) fájlban található.

## Admin felhasználó létrehozása OpenShift podban

```bash
python manage.py createsuperuser
```