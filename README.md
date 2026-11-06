# tap-navan

A [Singer](https://www.singer.io/) tap that extracts data from **Navan**. It is built with [hotglue-singer-sdk](https://github.com/hotgluexyz/HotglueSingerSDK) and speaks the standard Singer message protocol on stdout, so you can pair it with any compatible target.

## Features

- **REST**-style HTTP streams (see `client.py` / `streams.py`).
- **OAuth2** `client_credentials` grant via Hotglue (`access_token_support` on the tap).

- Configurable **`api_url`**, optional **`start_date`**, and **`start_date_override`** (see [Configuration](#configuration)).
- Incremental sync via **`modified_timestamp`** bookmark, applied as Navan **`date_modified.from` / `date_modified.to`** query filters.

### Streams

| Stream | Endpoint / notes | Primary key | Replication key |
| ------ | ---------------- | ----------- | ----------------- |
| `transactions` | `GET /expense/transactions` (`type=TRANSACTIONS,MANUAL_TRANSACTIONS,CONNECT`, `include_field_group=ERP,BOOKING`) — Navan cards, Connect cards, and manual reimbursements | `id` | `modified_timestamp` |

Includes travel-linked fields `trip_uuid`, `trip_name`, and `trip_purpose` (from the `BOOKING` field group / `booking_details`, promoted to the record root).

Pagination uses `has_next` with the response `next_cursor` passed as the `cursor` query param. Requests filter with `date_modified.from` / `date_modified.to` (bookmark or Navan ~2-month lookback). Because those filters are day-granular, the tap also drops records at or before the bookmark timestamp. Config `start_date` is only applied when `start_date_override` is true.

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
| `start_date` | string (datetime) | no | `2000-01-01T00:00:00Z` | Earliest `date_modified` when `start_date_override` is true (clamped to Navan's ~2-month lookback). |
| `start_date_override` | boolean | no | `false` | When true, use `start_date` as `date_modified.from`. When false, use the stream bookmark or Navan lookback and ignore `start_date`. |
| `api_url` | string | no | `https://api.navan.com/v1` | Base URL for the API. |
| `client_id` | string | yes | — | OAuth client ID. |
| `client_secret` | string | yes | — | OAuth client secret. |

Run `tap-navan --about` (or `tap-navan --about --format=markdown`) for the authoritative schema for your installed version.

### Example `config.json`

```json
{
  "start_date_override": false,
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
