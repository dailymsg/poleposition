# PolePosition

A FastAPI project scaffolder for building enterprise-grade APIs.

Create a new FastAPI project in seconds:

```bash
poleposition startproject myapp
```

[![PyPI version](https://img.shields.io/pypi/v/poleposition.svg)](https://pypi.org/project/poleposition/)
[![Python](https://img.shields.io/pypi/pyversions/poleposition.svg)](https://pypi.org/project/poleposition/)
[![License](https://img.shields.io/github/license/erenertem/poleposition)](LICENSE)

---

## Why PolePosition?

Starting a FastAPI project should be fast, clean, and predictable.

PolePosition provides:

* A scalable project structure
* Environment-based configuration
* Built-in logging
* Testing setup
* A ready-to-run FastAPI application

No boilerplate. No setup friction.

---

## Why not just FastAPI?

FastAPI is excellent, but starting a new project often involves:

* Recreating the same structure
* Setting up logging and configuration
* Organizing modules manually

PolePosition removes that overhead by providing a clean, production-ready starting point out of the box.

---

## Installation

```bash
uv tool install poleposition
```

or

```bash
pip install poleposition
```

---

## Quickstart

```bash
poleposition startproject myapp
cd myapp

# setup environment
cp .env.example .env

# install dependencies
uv sync

# run the app
uv run fastapi dev src/myapp/main.py
```

Open your API documentation at:

```
http://127.0.0.1:8000/docs
```

---

## Project Structure

```
myapp/
├─ pyproject.toml
├─ .env.example
├─ src/
│  └─ myapp/
│     ├─ main.py
│     ├─ api/
│     │  └─ routes/
│     │     └─ status.py
│     └─ core/
│        ├─ config.py
│        └─ logging.py
└─ tests/
```

---

## Status Endpoint

Check if your service is running:

```http
GET /api/v1/status
```

```json
{
  "status": "ok",
  "service": "myapp",
  "environment": "development",
  "version": "0.1.0"
}
```

---

## Philosophy

PolePosition is built around a few principles:

* Minimal — no unnecessary abstractions
* Opinionated — sensible defaults
* Extensible — easy to grow into larger systems

The CLI is intentionally lightweight, avoiding heavy templating engines.

---

## Roadmap

* [ ] Project name validation
* [ ] `poleposition add module`
* [ ] JSON logging support
* [ ] Docker support
* [ ] Production-ready presets

---

## Contributing

Contributions are welcome.
Feel free to open an issue or submit a pull request.

---

## License

MIT
