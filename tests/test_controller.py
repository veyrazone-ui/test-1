import unittest

from simulation.controller import Config, Controller, Inputs, State
from simulation.scenarios import run_scenario


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.c = Controller()

    def step(self, **kwargs):
        return self.c.tick(Inputs(**kwargs))

    def start_cycle(self):
        self.step(reset=True)
        self.step()
        self.step(start=True)
        self.step()

    def assert_motion_off(self, out):
        self.assertFalse(out.conveyor)
        self.assertFalse(out.extend)

    def to_state(self, state):
        self.c = Controller()
        self.start_cycle()
        if state == State.ACCEPT:
            self.step(station=True)
        elif state in (State.EXTEND, State.RETRACT):
            self.step(station=True, metal=True)
            if state == State.RETRACT:
                self.step(pusher_home=False, pusher_extended=True)
        self.assertEqual(self.c.state, state)

    def test_boot_and_start_without_reset_do_not_move(self):
        self.assert_motion_off(self.step(start=True))
        self.assertEqual(self.c.state, State.STOPPED)

    def test_reset_alone_never_starts_motion(self):
        self.assert_motion_off(self.step(reset=True))
        self.assertEqual(self.c.state, State.READY)

    def test_simultaneous_start_and_reset_cannot_restart(self):
        self.assert_motion_off(self.step(start=True, reset=True))
        self.assertEqual(self.c.state, State.STOPPED)

    def test_accept_demo_counts_one(self):
        c, _ = run_scenario("accept")
        self.assertEqual((c.state, c.accepted_count, c.rejected_count), (State.READY, 1, 0))

    def test_reject_demo_counts_one(self):
        c, _ = run_scenario("reject")
        self.assertEqual((c.state, c.accepted_count, c.rejected_count), (State.READY, 0, 1))

    def test_sensor_high_does_not_count_until_passage_finishes(self):
        self.to_state(State.ACCEPT)
        for _ in range(30):
            self.step(accepted=True)
        self.assertEqual(self.c.accepted_count, 0)
        self.step()
        for _ in range(30):
            self.step()
        self.assertEqual(self.c.accepted_count, 1)

    def test_station_must_clear_before_count(self):
        self.to_state(State.ACCEPT)
        self.step(accepted=True, station=True)
        self.step(station=True)
        self.assertEqual(self.c.accepted_count, 0)
        self.step()
        self.assertEqual(self.c.accepted_count, 1)

    def test_classification_is_latched_at_station(self):
        self.to_state(State.ACCEPT)
        self.step(metal=True, accepted=True)
        self.step(metal=True)
        self.assertEqual((self.c.accepted_count, self.c.rejected_count), (1, 0))

    def test_held_start_does_not_repeat_cycle(self):
        self.step(reset=True)
        self.step(start=True)
        self.step(start=True, station=True)
        self.step(start=True, accepted=True)
        self.step(start=True)
        self.assert_motion_off(self.step(start=True))
        self.assertEqual(self.c.state, State.READY)
        self.step()
        self.assertTrue(self.step(start=True).conveyor)

    def test_stop_overrides_start(self):
        self.step(reset=True)
        self.assert_motion_off(self.step(start=True, stop=True))
        self.assertEqual(self.c.state, State.STOPPED)

    def test_stop_in_each_active_state_requires_reset(self):
        for state in (State.FEED, State.ACCEPT, State.EXTEND, State.RETRACT):
            with self.subTest(state=state):
                self.to_state(state)
                self.assert_motion_off(self.step(stop=True))
                self.assert_motion_off(self.step(start=True))
                self.assertEqual(self.c.state, State.STOPPED)
                self.assertEqual(self.c.accepted_count + self.c.rejected_count, 0)

    def test_interlock_in_each_active_state_latches(self):
        for state in (State.FEED, State.ACCEPT, State.EXTEND, State.RETRACT):
            with self.subTest(state=state):
                self.to_state(state)
                self.assert_motion_off(self.step(permissive_ok=False))
                self.assert_motion_off(self.step())
                self.assertEqual((self.c.state, self.c.fault), (State.FAULT, "INTERLOCK_OPEN"))

    def test_fault_reset_requires_clear_cell_and_new_edge(self):
        self.start_cycle()
        self.step(permissive_ok=False)
        self.step(reset=True, station=True)
        self.step(reset=True)
        self.assertEqual(self.c.state, State.FAULT)
        self.step()
        self.assert_motion_off(self.step(reset=True))
        self.assertEqual(self.c.state, State.READY)

    def test_bad_permissive_blocks_reset(self):
        self.step(permissive_ok=False)
        self.step(reset=True, permissive_ok=False)
        self.assertEqual(self.c.state, State.FAULT)

    def test_start_with_occupied_cell_faults(self):
        self.step(reset=True)
        self.assert_motion_off(self.step(start=True, station=True))
        self.assertEqual(self.c.fault, "START_NOT_CLEAR")

    def test_conflicting_limits_or_exits_fault(self):
        for inputs, fault in (({"pusher_extended": True}, "LIMIT_CONFLICT"),
                              ({"accepted": True, "rejected": True}, "EXIT_CONFLICT")):
            with self.subTest(fault=fault):
                self.c = Controller()
                self.assert_motion_off(self.step(**inputs))
                self.assertEqual(self.c.fault, fault)

    def test_wrong_exit_faults_without_counting(self):
        for state, sensor in ((State.FEED, "accepted"), (State.ACCEPT, "rejected"),
                              (State.EXTEND, "accepted"), (State.RETRACT, "accepted")):
            with self.subTest(state=state):
                self.to_state(state)
                self.assert_motion_off(self.step(**{sensor: True}))
                self.assertEqual(self.c.fault, "UNEXPECTED_EXIT")
                self.assertEqual(self.c.accepted_count + self.c.rejected_count, 0)

    def test_home_feedback_loss_stops_conveyor(self):
        for state in (State.FEED, State.ACCEPT):
            with self.subTest(state=state):
                self.to_state(state)
                self.assert_motion_off(self.step(pusher_home=False))
                self.assertEqual(self.c.fault, "PUSHER_NOT_HOME")

    def test_all_active_states_have_timeouts(self):
        for state, duration in ((State.FEED, 5000), (State.ACCEPT, 3000),
                                (State.EXTEND, 1000), (State.RETRACT, 1000)):
            with self.subTest(state=state):
                self.to_state(state)
                remaining = (duration - self.c.elapsed_ms) // 20
                for _ in range(remaining - 1):
                    self.step()
                self.assertEqual(self.c.state, state)
                self.assert_motion_off(self.step())
                self.assertEqual(self.c.fault, f"{state.value}_TIMEOUT")

    def test_station_on_timeout_boundary_is_too_late(self):
        self.start_cycle()
        while self.c.elapsed_ms < 4980:
            self.step()
        self.assert_motion_off(self.step(station=True))
        self.assertEqual(self.c.fault, "FEED_TIMEOUT")

    def test_station_one_scan_before_timeout_is_accepted(self):
        self.start_cycle()
        while self.c.elapsed_ms < 4960:
            self.step()
        self.step(station=True)
        self.assertEqual(self.c.state, State.ACCEPT)

    def test_reject_needs_exit_passage_and_home_feedback(self):
        self.to_state(State.EXTEND)
        self.step(pusher_home=False, pusher_extended=True, rejected=True)
        self.step(pusher_home=False)
        self.assertEqual(self.c.rejected_count, 0)
        self.step()
        self.assertEqual(self.c.rejected_count, 1)

    def test_first_fault_survives_stop_and_secondary_fault(self):
        self.start_cycle()
        self.step(permissive_ok=False)
        self.step(stop=True, pusher_extended=True)
        self.assertEqual(self.c.fault, "INTERLOCK_OPEN")

    def test_reset_preserves_completed_counts(self):
        self.c, _ = run_scenario("accept")
        self.step(stop=True)
        self.step(reset=True)
        self.assertEqual(self.c.accepted_count, 1)

    def test_repeated_cycles_count_exactly_once_each(self):
        self.step(reset=True)
        for _ in range(100):
            self.step(start=True)
            self.step(station=True)
            self.step(accepted=True)
            self.step()
        self.assertEqual((self.c.accepted_count, self.c.rejected_count), (100, 0))

    def test_all_demo_traces_obey_output_interlock(self):
        for name in ("accept", "reject", "feed-jam", "interlock"):
            with self.subTest(scenario=name):
                _, rows = run_scenario(name)
                for row in rows:
                    self.assertFalse(row["out_conveyor"] and row["out_extend"])
                    if row["state"] in ("STOPPED", "READY", "FAULT"):
                        self.assertEqual((row["out_conveyor"], row["out_extend"]), (0, 0))

    def test_timer_configuration_rejects_invalid_values(self):
        for kwargs in ({"scan_ms": 0}, {"scan_ms": -1}, {"scan_ms": True},
                       {"feed_timeout_ms": 21}, {"accept_timeout_ms": 1.5}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Config(**kwargs)


if __name__ == "__main__":
    unittest.main()
