"""Scripted sensor stimuli, not a dynamic conveyor/physics model."""

from dataclasses import asdict

from simulation.controller import Controller, Inputs


def scenario_steps(name):
    # All demo cycles explicitly reset and then start from a clear cell.
    steps = [
        (1, Inputs(reset=True)),
        (1, Inputs()),
        (1, Inputs(start=True)),
        (20, Inputs()),
    ]
    if name == "accept":
        steps += [
            (1, Inputs(station=True)),
            (10, Inputs()),
            (5, Inputs(accepted=True)),
            (1, Inputs()),
        ]
    elif name == "reject":
        steps += [
            (1, Inputs(station=True, metal=True)),
            (5, Inputs(station=True, pusher_home=False)),
            (1, Inputs(rejected=True, pusher_home=False, pusher_extended=True)),
            (5, Inputs(rejected=True, pusher_home=False)),
            (1, Inputs()),
        ]
    elif name == "feed-jam":
        steps += [(250, Inputs())]
    elif name == "interlock":
        steps += [(1, Inputs(permissive_ok=False)), (3, Inputs())]
    else:
        raise ValueError(f"Unknown scenario: {name}")
    return steps


def run_scenario(name):
    controller = Controller()
    rows = []
    for count, inputs in scenario_steps(name):
        for _ in range(count):
            outputs = controller.tick(inputs)
            rows.append({
                "time_ms": (len(rows) + 1) * controller.config.scan_ms,
                **{f"in_{k}": int(v) for k, v in asdict(inputs).items()},
                "state": controller.state.value,
                **{f"out_{k}": int(v) for k, v in asdict(outputs).items()},
                "fault": controller.fault or "",
                "accepted_count": controller.accepted_count,
                "rejected_count": controller.rejected_count,
            })
    return controller, rows
