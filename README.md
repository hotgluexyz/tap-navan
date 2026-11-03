# tap-navan

A [Singer](https://www.singer.io/) tap that extracts data from **Navan**. It is built with [hotglue-singer-sdk](https://github.com/hotgluexyz/HotglueSingerSDK) and speaks the standard Singer message protocol on stdout, so you can pair it with any compatible target.

## Features

- **REST**-style HTTP streams (see `client.py` / `streams.py`).
- **OAuth2** `client_credentials` grant via Hotglue (`access_token_support` on the tap).

- Configurable **`api_url`** and optional **`start_date`** (see [Configuration](#configuration)).
- Incremental sync via **`modified_timestamp`** (bookmark); API queries still use a `transaction_date` window.

### Streams

| Stream | Endpoint / notes | Primary key | Replication key |
| ------ | ---------------- | ----------- | ----------------- |
| `transactions` | `GET /expense/transactions` (`type=TRANSACTIONS,MANUAL_TRANSACTIONS,CONNECT`, `include_field_group=ERP`) — Navan cards, Connect cards, and manual reimbursements | `id` | `modified_timestamp` |

Pagination uses `has_next` with a numeric `page` query param. `transaction_date.from` / `transaction_date.to` are required and must fall within the last ~2 months (the tap clamps `start_date` accordingly).

## Requirements

- Python **3.10+** (see `requires-python` in `pyproject.toml`).

## Installation

1. **Clone** this repository and `cd` into the project directory.
2. **Create `config.json`** in the project root with your credentials and settings (see [Configuration](#configuration) for the fields and an example).
3. **Create a virtual environment** and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, use `.venv\Scripts\activate` instead of `source .venv/bin/activate`.

4. **Install the package** in editable mode:

```bash
pip install -e .
```

5. **Run the tap** (with the venv still activated):

```bash
tap-navan --help
```

## Configuration

| Setting | Type | Required | Default | Description |
| ------- | ---- | -------- | ------- | ----------- |
| `start_date` | string (datetime) | no | `2000-01-01T00:00:00Z` | Earliest `transaction_date` to sync (clamped to Navan's ~2-month lookback). |
| `api_url` | string | no | `https://api.navan.com/v1` | Base URL for the API. |
| `client_id` | string | yes | — | OAuth client ID. |
| `client_secret` | string | yes | — | OAuth client secret. |

Run `tap-navan --about` (or `tap-navan --about --format=markdown`) for the authoritative schema for your installed version.

### Example `config.json`

```json
{
  "start_date": "2000-01-01T00:00:00Z",
  "api_url": "https://api.navan.com/v1",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET"
}
```

Do not commit real credentials. Prefer environment variables or a secrets manager in production.

### Environment-based config

You can load settings from the process environment using `--config=ENV` (the SDK merges env into config). Env names follow the tap’s setting keys (see `tap-navan --about`).

## Usage

With your virtual environment **activated** and `config.json` in place:

Discover stream catalog:

```bash
tap-navan --config config.json --discover > catalog.json
```

Run a sync (with optional state):

```bash
tap-navan --config config.json --catalog catalog.json --state state.json
```

Pipe to any Singer target:

```bash
tap-navan --config config.json --catalog catalog.json | target-jsonl
```

Inspect built-in settings and stream metadata:

```bash
tap-navan --about
```

## API / documentation

TODO: Add your vendor’s base URLs, auth docs, and links (compare to the “API hosts” section in a finished tap README).


## License
MIT — see `LICENSE` and `pyproject.toml`.
