# Verification plan

## Levels of evidence

1. **Python reference tests:** implemented and runnable now. They check the documented control contract using ideal Boolean inputs.
2. **PLC-in-IDE tests:** planned. Repeat the cases on the compiled ST implementation; Python results do not count as PLC results.
3. **CAD/CAM checks:** planned. Inspect geometry and any optional toolpaths independently of control software.
4. **Hardware tests:** out of scope. No physical response time, safety or reliability claim is made.

## Requirement-to-test mapping

Test names below refer to methods in `tests/test_controller.py` without the `test_` prefix. Several methods test multiple states with subtests.

| Requirement | Python checks | PLC replay / result to record |
| --- | --- | --- |
| R01 startup | `boot_and_start_without_reset_do_not_move`, `reset_alone_never_starts_motion`, `simultaneous_start_and_reset_cannot_restart` | Start with zero outputs; attempt Start; then Reset; verify READY still has zero outputs |
| R02 one cycle | `held_start_does_not_repeat_cycle`, `repeated_cycles_count_exactly_once_each` | Hold Start across a completed cycle; verify no second feed until release/repress |
| R03 routing | `accept_demo_counts_one`, `reject_demo_counts_one`, `classification_is_latched_at_station` | Replay both routes; change the material bit after route selection |
| R04 accept count | `sensor_high_does_not_count_until_passage_finishes`, `station_must_clear_before_count` | Hold accept high; count stays zero; clear it and station; count becomes one |
| R05 reject count | `reject_needs_exit_passage_and_home_feedback`, `reject_demo_counts_one` | Confirm extended, reject passage and home in sequence; missing any element must not count |
| R06 output exclusion | `all_demo_traces_obey_output_interlock` | Inspect every state; record that motor and extend commands are never simultaneous |
| R07 bounded waits | `all_active_states_have_timeouts`, `station_on_timeout_boundary_is_too_late`, `station_one_scan_before_timeout_is_accepted` | Withhold each expected completion; capture configured delay and observed timer transition |
| R08 interruption | `stop_overrides_start`, `stop_in_each_active_state_requires_reset`, `interlock_in_each_active_state_latches` | Apply Stop/permissive loss in FEED, ACCEPT, EXTEND and RETRACT; outputs off on evaluation |
| R09 reset | `fault_reset_requires_clear_cell_and_new_edge`, `bad_permissive_blocks_reset`, `start_with_occupied_cell_faults` | Try reset with blocked path, bad permissive and held Reset; verify all denied until eligible new edge |
| R10 plausibility | `conflicting_limits_or_exits_fault`, `wrong_exit_faults_without_counting`, `home_feedback_loss_stops_conveyor` | Inject each contradictory/unexpected condition; preserve counts and show the fault |
| R11 diagnostics | `first_fault_survives_stop_and_secondary_fault`, `reset_preserves_completed_counts` | Add a second fault and Stop; first reason remains; completed counts survive recovery |
| R12 reproducibility | Four CLI demos plus the complete unit suite | Save software versions, commands, actual results and trace files |

## How to run the reference checks

```bash
python -m unittest discover -s tests -v
python -m simulation.run_demo --scenario reject --trace artifacts/reject.csv
```

`artifacts/` is ignored by Git. Copy only reviewed, useful results into `evidence/`. The committed CSV examples are reproducible logical traces, not measurements of a physical conveyor. Their `time_ms` field is elapsed simulated scan time.

## PLC replay procedure

1. Record IDE version, Standard library version, device target and cyclic task period.
2. Compile the PLC project, enable IDE simulation and establish the documented initial inputs. Do not map physical outputs.
3. Use the symbolic I/O names and state contract. First replay the normal scenarios; then the fault cases in the table.
4. For precise timing/boundary cases, use a deterministic ST test-sequence POU or a scripted scan counter. Manual watch-list clicks are suitable for coarse scenarios, not a 20 ms boundary claim.
5. Capture the input/state/output/count sequence, expected result, actual result and pass/fail status. Keep failed runs and the subsequent fix when useful.
6. Inspect timer semantics carefully. A TON timer is not automatically identical to the reference counter; document state entry timing and any one-scan offset before declaring equivalence.
7. After each fix, rerun the affected case and the normal-cycle/Stop/reset checks.

Additional PLC completion target: 20 alternating accept/reject cycles with counts of 10/10, no phantom counts and no simultaneous conveyor/extend command. This target is **not a completed PLC test**.

## Mechanical and optional manufacturing gates

CAD: inspect belt/part/pusher envelopes, sensor adjustment and mounting access; check dimensions and units in the exported drawing; reopen the STEP export to inspect geometry. Compare the nominal travel calculations with chosen sensor positions.

CAM: inspect stock, origin, clamps, tool reach and clearance; simulate the operation sequence; inspect remaining material and toolpath warnings. A simulated toolpath is not machine clearance approval. Record a real machine/postprocessor only if one has actually been selected and checked.
