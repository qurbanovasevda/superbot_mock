# SuperChat — Phase 1

One unified chat for flights, shopping and cinema, backed by the five official
mock JSON datasets. Python 3.11+ is required. Rules mode works offline;
Gemini mode requires an API key and internet access.

## Install and run

Run from the project directory in Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe run.py
```

If the environment is already installed, use only the final two commands.
Open http://127.0.0.1:8000 for chat, /health for readiness and /docs for REST API.
Stop with Ctrl+C. Dependencies need internet at installation; the running
application uses local datasets and SQLite. In Gemini mode, chat requests also
call Google; rules mode makes no model requests.
On macOS/Linux use python3, .venv/bin/python and the same arguments.

## Gemini configuration

Create a local `.env` in the project root, alongside `run.py`:

```dotenv
SUPERCHAT_CHAT_MODE=llm
GEMINI_API_KEY=YOUR_PRIVATE_KEY
GEMINI_MODEL=gemini-3.5-flash-lite
```

Use your billing-disabled Free Tier project key. Never commit or share `.env`.
The model name alone cannot guarantee free usage. Existing terminal environment
variables override `.env`, including empty values. Restart after configuration
changes. `/health` should show `chat_mode: llm` and `llm_configured: true`;
this confirms configuration, not successful provider access.
See `docs/LLM_SETUP.md` for details. Set `SUPERCHAT_CHAT_MODE=rules` for offline mode.

## Features

- Flights: route/date, airline, price, stops and departure-time filters; sorting,
  details, comparison, quantity-based mock reservation and current availability.
- Shopping: keyword/category/brand/color/price filters, rating/price/name sorting,
  stock, comparisons, session cart and totals.
- Cinema: title/genre/language/rating/date filters, cinema listing, venue/date/time
  showtime search, availability and mock ticket reservations.
- Conversation: seven routing categories, cross-domain switches, independent
  mixed-request constraints, ordinal references, per-domain state and persistent
  history. Gemini also retains explicitly stated durable preferences. Missing flight destination/date is collected through follow-up turns.
- UI: unified chat, cards, booking confirmation, cart removal, reservations,
  local session restoration and a responsive layout.

See docs/CHAT_COMMANDS.md for supported English phrasing, docs/DEMO.md for the
five-minute walkthrough, and docs/TECHNICAL_REPORT.md for architecture and limits.
Older STAGE documents describe historical versions, not current delivery status.

## Project layout

| Path | Responsibility |
|---|---|
| app/main.py | FastAPI startup, routes, error handling and health |
| app/ui.py | Self-contained web page, no frontend build step |
| app/chat.py | Offline intent routing, context and conversation persistence |
| app/llm_chat.py | Gemini planning, checked execution and single-call answer drafts |
| check_phase1.py | Local-server acceptance scenarios and latency measurements |
| app/api.py | Validated domain and session REST endpoints |
| app/config.py | Data/database paths and fixed reference date |
| app/models.py | Validated official dataset models |
| app/repositories/ | Read-only dataset loading and repository contracts |
| app/services/ | Catalog operations, SQLite carts and atomic bookings |
| data/ | Unmodified official JSON files |
| tests/ | Foundation, API, domain and multi-turn tests |
| docs/ | Reports, command reference and demonstration |
| var/ | Local runtime database, not source data |

## Data and state

Reference date: 2026-11-02. Currency: AZN. Airport timestamps are local;
flight duration_min is authoritative. Showtimes link movie_id and cinema_id.
No seat numbers, real payment or real booking are generated.

Runtime state lives in var/superchat.sqlite3. To reset the entire demo, stop the
server and deliberately remove that file. This removes every saved session,
cart, conversation and mock reservation. New conversation creates an independent
session but does not reset globally consumed seats.

Reservation transactions prevent overselling; REST request_key retries are
idempotent. Chat commands are separate actions and do not support automatic
transport retry deduplication. Cart PUT/add sets an absolute quantity. Carts
check stock but do not reserve it. Stored source seat counts are immutable;
availability endpoints, Gemini search/details/comparisons and REST detail/comparison
responses expose adjusted inventory.

## Verification and remaining limits

99 automated tests passed in the development environment on 2026-11-02. One
non-failing Starlette/httpx deprecation warning remains. These tests use mocked
provider responses; they do not measure live Gemini speed or interpretation quality.
A local installation with different test files can report a different count.

The historical rules-router development evaluation is 41/44 (93.18%); see
`docs/ROUTING_RESULTS.md`. This is neither a held-out benchmark nor a Gemini score.
To collect current local-server checks, leave the server running and use another
terminal in the project directory:

```powershell
.\.venv\Scripts\python.exe check_phase1.py --run-live
```

This sends 14 messages in eight new sessions, uses Gemini quota in LLM mode,
and saves `phase1_live_results.json`. It stops on backend/network errors. Passes
check routing labels and minimal result structure, not full answer correctness.
Review responses manually in the browser using `docs/DEMO.md`. Browser/mobile
acceptance and measured live Gemini latency remain open until actually checked.

Gemini uses one remote request per ordinary turn; Confirm/Cancel for pending
writes are local. The plan and draft answer share that request. Backend operations
execute after planning; unsupported IDs/numbers in drafts trigger a verified
summary instead. This is partial factual validation, not proof of every claim.
Preferences are bounded verbatim user statements; applying them depends on planning.

Gemini plans select English, Azerbaijani or Russian replies from the user message,
persisting the selected language for short follow-ups and local confirmation.
Backend summaries and common confirmation templates are localized. Catalog names
and UI labels keep their original spelling. Full multilingual parity is not yet
measured; voice, image search and round trips are not implemented. Phase 2 data-provider APIs
are excluded. Session IDs are demo identifiers, not authentication. Use one
Uvicorn worker; conversation locking is process-local and can queue requests.
Earlier technical-report/acceptance snapshots may describe the rules-only build;
they must be revised before final submission.

## Dependency sources

- FastAPI: https://github.com/fastapi/fastapi (MIT)
- Pydantic: https://github.com/pydantic/pydantic (MIT)
- Uvicorn: https://github.com/Kludex/uvicorn (BSD-3-Clause)
- pytest: https://github.com/pytest-dev/pytest (MIT, development)
- HTTPX: https://github.com/encode/httpx (BSD-3-Clause, development)

Official organizer files supply requirements and catalog records. SQLite is used
through Python's standard library. Gemini is accessed using standard-library HTTPS;
no provider SDK is installed.
