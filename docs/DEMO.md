# Phase 1 demonstration and browser checks

Start `python run.py`, open http://127.0.0.1:8000 and select New conversation.
Check `/health` and confirm the intended mode. Gemini access needs a configured
key and internet; rules mode is offline. Do not display the key or `.env`.
Dates resolve against 2 November 2026. All catalog data and reservations are mock.

## Five-minute target walkthrough

Timing is a target; rehearse using measured Gemini latency before presenting.
Do not claim a five-minute completion until a rehearsal actually fits.

1. Flights: `Flights from Baku to Istanbul on Friday`.
   Then `The cheaper one, is it direct?` Check exact prices/stops against cards.
2. Switch to Cinema: `What is playing tonight?` Inspect movies and dates.
3. Switch to Shopping: `Show me laptops`.
   Then `The second one, is it in stock?` Verify the reference and stock.
4. Return to Cinema: `Back to cinema. The sci-fi one, any seats on Saturday?`
   If several films match, expect clarification rather than an arbitrary booking.
5. Switch back to Shopping: `Headphones under 100 AZN`.
   Use Add to cart, verify the total, refresh, then remove it. The button sets
   absolute quantity one; it does not increment an existing quantity.

This includes at least three domain switches in one shared conversation.

## Additional acceptance checks

- Mixed: `I need a flight to Istanbul on 6 November and a backpack for the trip.`
  Both domains should appear with independent filters.
- Ambiguity: `Show me something good.` Expect one useful clarifying question.
- Out of scope: `What is the weather in Ganja?` Expect a polite scope explanation.
- New conversation: `Book two seats.` Expect clarification, no reservation.
- Preference: `I always prefer direct flights`. Change topics several times,
  then request flights. Verify direct-flight filtering; explicitly requesting
  connecting flights should override that preference for the current request.
- Reservation: select a known flight/showtime, request two seats, then Cancel.
  Inventory and reservations must be unchanged. Repeat and Confirm; exactly one
  booking should appear. Ask details again and verify seats decreased by two.
- Refresh: history, cart and reservations should restore in the same session.
- Narrow browser to phone width: inspect cards, input, buttons and side panels.
- Measure actual response time. A successful HTTP status alone does not prove
  correct routing, useful clarification or a factually correct explanation.

Reservations consume global mock inventory across sessions. New conversation
creates a separate session but does not restore seats. Reset the database only
when intentionally discarding all local sessions, carts and bookings.

## Automated local-server smoke checks

Leave the server running and open a second terminal in `D:\superchat`:

```powershell
.\.venv\Scripts\python.exe check_phase1.py --run-live
```

This uses 14 chat turns in eight fresh sessions and saves `phase1_live_results.json`.
It consumes Gemini quota when LLM mode is enabled. It checks labels and minimal
result structure, not complete semantic correctness. Keep manual findings separate
from the old rules-router accuracy. No live result is claimed before execution.
