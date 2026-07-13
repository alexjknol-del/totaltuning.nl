# Total Tuning

Statische website voor Total Tuning, een onafhankelijk magazine over
carstyling en cartuning. De site wordt opgebouwd door een kleine Python-generator
die markdown-artikelen en Jinja2-templates omzet naar kant-en-klare HTML in de map
`public/`. Die map is alles wat Cloudflare Pages hoeft te serveren.

## Mappenstructuur

```
totaltuning/
├── generate.py            Generator. Bovenin staat alle configuratie (SITE, NAV, footer, categorieën).
├── requirements.txt       Python-pakketten (jinja2, markdown).
├── .gitignore
├── content/
│   ├── articles/          De blogartikelen als .md-bestanden met frontmatter.
│   └── pages/             Privacybeleid, cookiebeleid en disclaimer als .md.
├── templates/             Jinja2-templates (base, home, nieuws, artikel, over, partners, contact, 404).
├── static/                CSS, favicon, robots.txt, _headers, _redirects. Wordt 1-op-1 naar public/ gekopieerd.
└── public/                De gegenereerde website. Dit is de map die live gaat.
```

## Lokaal bouwen

Eenmalig de pakketten installeren:

```
pip install -r requirements.txt
```

Daarna de site bouwen:

```
python generate.py
```

De volledige website staat dan in `public/`. Lokaal bekijken kan met een
simpele webserver:

```
cd public
python -m http.server 8000
```

Vervolgens in de browser naar `http://localhost:8000`.

## Nieuw artikel toevoegen

1. Maak een nieuw `.md`-bestand aan in `content/articles/`, bijvoorbeeld
   `07-velgen.md`.
2. Zet bovenin een frontmatter-kop tussen twee regels met drie streepjes:

```
---
title: Lichtmetalen velgen, waar op te letten
slug: lichtmetalen-velgen-waar-op-te-letten
date: 2026-06-25
category: Exterieur
excerpt: Een korte samenvatting van twee zinnen die op de nieuwsoverzichtspagina verschijnt.
read_minutes: 5
---
```

3. Schrijf daaronder het artikel in gewone markdown.
4. De `category` bepaalt onder welk kopje het artikel op de nieuwspagina komt.
   Bestaande categorieën zijn Exterieur, Onderstel, Verlichting, Uitlaat en
   Interieur. Een categorie die hier niet tussen staat (zoals "Algemeen")
   verschijnt bovenaan.
5. Bouw de site opnieuw met `python generate.py` en commit de wijzigingen.

De `slug` bepaalt de URL: `/nieuws/lichtmetalen-velgen-waar-op-te-letten/`.

## Deployen naar GitHub en Cloudflare Pages

### Eerst naar GitHub

```
git init
git add .
git commit -m "Eerste versie Total Tuning"
git branch -M main
git remote add origin https://github.com/alexjknol-del/totaltuning.git
git push -u origin main
```

### Daarna koppelen aan Cloudflare Pages

Er zijn twee manieren. Optie A is het simpelst en wordt aangeraden.

#### Optie A, aanbevolen: zonder build (de map public/ wordt meegecommit)

De map `public/` zit al in de repository, dus Cloudflare hoeft niets te bouwen.

1. Cloudflare Dashboard, Workers & Pages, Create application, Pages,
   Connect to Git.
2. Kies de repository.
3. Framework preset: **None**.
4. Build command: **leeglaten**.
5. Build output directory: **public**.
6. Save and Deploy.

Voordeel: er draait geen build op Cloudflare, dus er kan ook niets misgaan in
die build. Nadeel: na elke contentwijziging moet `python generate.py` lokaal
gedraaid worden en moet `public/` worden meegecommit.

#### Optie B: Cloudflare bouwt zelf

1. Framework preset: **None**.
2. Build command: `pip install -r requirements.txt && python generate.py`
3. Build output directory: **public**.

Voordeel: alleen de bron hoeft gecommit te worden, Cloudflare bouwt `public/`
zelf. Bij deze optie kan `public/` desgewenst in `.gitignore` worden gezet.

### Domein koppelen

1. In het Pages-project naar Custom domains.
2. Voeg `totaltuning.nl` toe en volg de stappen.
3. Voeg ook `www.totaltuning.nl` toe. Het bestand `static/_redirects`
   stuurt `www` automatisch met een 301 door naar de versie zonder `www`, dus
   die laatste is de hoofdvariant.

### Mailbox

De contactpagina laat bezoekers mailen naar `info@totaltuning.nl`. Zorg
dat die mailbox bestaat bij de mailprovider voordat de site live gaat,
anders komt post niet aan.

## Aanpassen van vaste teksten

- Naam, domein, e-mailadres en tagline staan bovenin `generate.py` in de
  `SITE`-dictionary.
- Het menu staat in `NAV`.
- De juridische teksten (privacy, cookies, disclaimer) staan als markdown in
  `content/pages/`.
- De vormgeving staat volledig in `static/css/style.css`.

## SEO-notitie over de webshoplinks

De site verwijst op een paar plekken naar Carstyle.nl en Extreme-Carstyling.nl.
Die links staan nu als gewone (dofollow) links met `rel="noopener"`. Mochten
deze plaatsingen op enig moment een commerciële of betaalde afspraak worden,
dan is het netjes om `rel="sponsored"` toe te voegen om binnen de richtlijnen
van Google voor commerciële links te blijven. Zolang het redactionele
aanbevelingen zijn, is dofollow verdedigbaar. Dat is een eigen afweging.
