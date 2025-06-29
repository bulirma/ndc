# NDC

NDC or Neume Dataset Collection is my school project in python.
It is tool to collect scoresheets of byzantine notation for my other project.

## License

NDC is free software, shared under the GPLv3 license.

## Installation

Clone with git

```bash
git clone https://github.com/bulirma/ndc.git
```

Check the version of python, version 3.13.3 was used.
Create virtual environment and install the requirements.

```bash
python -m venv venv
. ./bin/venv/activate
pip install -r requirements.txt
```

### Localization

Create lozalization binaries

```bash
make localize
```

### Create databaze

Apply migrations

```bash
make db-upgrade
```

## Run

To run the application you need to provide an encryption key for the database
by setting the `NDC_DB_SECRET_COL_KEY` variable either by

- `export` in shell
- setting in the `.env` file

```bash
export NDC_DB_SECRET_COL_KEY=top_secret
make run-dev
```
