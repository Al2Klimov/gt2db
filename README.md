# gt2db

Collects **G**oogle **T**rends in**to** a **d**ata**b**ase.

## Setup

### Clone this repository

Requirement: git

```bash
git clone https://github.com/ManufakturaElfov/gt2db.git /opt/gt2db
```

### Create a PostgreSQL database

Requirement: postgresql

```bash
createuser -W gt
createdb -O gt gt
```

### Import SQL schema

```bash
psql -h 127.0.0.1 -U gt gt < /opt/gt2db/schema.sql
```

### Create a Python VEnv

Requirement: python3-venv

```bash
python3 -m venv /opt/gt2db/venv
```

### Install gt2db there

Requirements:

* gcc
* python3-dev
* libpq-dev

```bash
bash
. /opt/gt2db/venv/bin/activate
cd /opt/gt2db
python3 setup.py install
exit
```

### Integrate gt2db into systemd

```bash
cat <<EOF >/etc/systemd/system/gt2db.service
[Unit]
After=postgresql.service

[Service]
Environment=DB=postgresql://gt:123456@127.0.0.1/gt
ExecStart=/bin/bash -ec '. /opt/gt2db/venv/bin/activate; exec python3 -m gt2db.daemon'
User=nobody
Group=nogroup
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
```

### Start gt2db

```bash
systemctl enable gt2db
systemctl start gt2db
```

## Usage

### Connect to the database

```bash
psql -h 127.0.0.1 -U gt gt
```

### Insert the desired keywords

```postgresql
INSERT INTO keyword(keyword) VALUES ('Лилия Чанышева')
ON CONFLICT ON CONSTRAINT keyword_uk_keyword DO NOTHING;
```

### Watch the `searches` table

```postgresql
SELECT time, searches FROM searches WHERE keyword=
(SELECT id FROM keyword WHERE keyword='Лилия Чанышева');
```
