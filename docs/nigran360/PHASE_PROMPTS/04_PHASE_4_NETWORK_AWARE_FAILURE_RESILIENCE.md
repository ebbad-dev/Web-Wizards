# Phase 4 Prompt — Network-Aware and Failure-Resilient Examinations

Read the master prompt, SRS, architecture, data/migrations, security and testing docs, plus approved Phase 3 report. Execute **Phase 4 only**. This phase implements the selected innovation challenge 5.3.

## Objective

Reduce data loss and confusion during connection interruptions, refreshes and supported device recovery, without giving an unverified time extension or falsely reporting an answer as saved.

## Scope

1. Detect `online`/`offline` transitions and show a clear connection state.
2. Track each answer's state: unsaved, saving, saved, pending sync, sync failed/conflict.
3. Implement a bounded local pending-answer queue (prefer IndexedDB if suitable) with attempt ID, question ID, payload version/sequence and unique idempotency key.
4. Do not store authentication tokens in the queue.
5. Retry transient failures with bounded backoff while the attempt remains eligible; avoid infinite background retries and duplicate writes.
6. Reconcile pending answers using server response versions. Define deterministic behavior for out-of-order or stale writes.
7. On refresh/re-entry, restore server-acknowledged answers first and safely inspect any pending local queue for the same authenticated user/attempt.
8. Clear queued data after confirmed submission or an explicit expiry/cleanup path.
9. Make server acknowledgement the only condition for showing an answer as saved.
10. Expose a simple candidate-friendly explanation of what is saved locally versus saved on the server.

## Fairness and security rules

- Server UTC deadline is authoritative and immutable for the attempt.
- Do not pause the exam clock because the browser is offline.
- Do not extend time from client timestamps, local clock values or a client-provided remaining-time field.
- Do not accept arbitrary post-deadline answer changes based on local browser data.
- Do not claim that a browser-generated timestamp, hash chain or IndexedDB record can prove the moment an unsynced response was written.
- If a recovery grace/pause policy is proposed, stop and present a written policy with fairness/trust analysis for explicit approval before implementing it.
- Failed/pending answers must not silently disappear or be counted as server-saved.

## Required demonstrable scenario

1. Candidate starts an assigned exam.
2. Candidate answers a question; server acknowledges it.
3. Network is disconnected.
4. Candidate changes another answer; UI marks it pending, not saved.
5. Network reconnects before deadline; queue retries idempotently and server acknowledges the response.
6. Candidate refreshes; acknowledged responses are restored and no duplicate write is created.
7. A separate test advances beyond server deadline and verifies the server rejects new changes despite client clock manipulation.

Also test device/browser restart recovery to the extent supported by the local queue and browser environment. Explain limitations where local state is unavailable.

## Acceptance gate

- Offline/online/save states are clear and accurate.
- Idempotent retries create no duplicate response or score.
- Stale responses cannot overwrite newer versions silently.
- Server deadline enforcement is independent of browser clock.
- No time extension occurs due solely to connectivity loss.
- Failure scenario is demonstrable with an honest limitation statement.
- Full regressions pass. Complete report and stop before Phase 5.
