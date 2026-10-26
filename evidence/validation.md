# Reference-model baseline

Baseline recorded on 26 October 2026 using Python 3.12.14 in the development environment. This is software-only evidence. No user-performed PLC, CAD, CAM or hardware work is implied.

| Check | Actual outcome |
| --- | --- |
| `python -m unittest discover -s tests -v` | 27 tests passed; subtests exercise multiple active states |
| Accept demo | READY; accepted=1; rejected=0; no fault |
| Reject demo | READY; accepted=0; rejected=1; no fault |
| Feed-jam demo | FAULT; accepted=0; rejected=0; FEED_TIMEOUT |
| Interlock demo | FAULT; accepted=0; rejected=0; INTERLOCK_OPEN |

The [test log](reference-test-run.txt) captures the actual local run. [Accept](accept-trace.csv) and [reject](reject-trace.csv) CSVs contain scripted input and resulting output/state sequences. Timestamps are logical scan time, not wall-clock measurements. Reproduce them with:

```bash
python -m simulation.run_demo --scenario accept --trace artifacts/accept.csv
python -m simulation.run_demo --scenario reject --trace artifacts/reject.csv
```

A GitHub Actions workflow is supplied separately. Its hosted status must be read from the Actions tab; the local results above do not prove that a hosted run succeeded.

## Limits of this evidence

- The tests validate the documented reference behavior for the supplied cases, not every possible physical event.
- Tests and demos call the Python controller; no PLC compiler or runtime was used.
- Ideal input sequences do not verify mechanical timing, stopping distance, sensing performance or safety.
- No simulation video, CAD result or CNC result has been fabricated to imply completion.

Use [the results template](results-template.md) for later implementation evidence. Add real observations and link their source files before updating project status.
