# Implementation results template — not completed results

Copy this file for a real test session; replace the empty fields after running it.

| Session field | Actual value |
| --- | --- |
| Date and person performing the test | |
| Commit tested | |
| Python / PLC IDE / library version | |
| Device target and task period | |
| Simulation or physical equipment | |
| Known deviations from requirements | |

| Requirement / case | Input sequence and expected behavior | Actual observation | Pass / fail / not run | Evidence link |
| --- | --- | --- | --- | --- |
| R01 startup | Start cannot move from STOPPED; Reset only establishes READY | | Not run | |
| R03–R05 normal routes | One accept and one reject, confirmed passage | | Not run | |
| R07 timeout | Missing feedback faults at documented limit | | Not run | |
| R08–R09 interruption | Stop/permissive loss; clear, reset, separate Start | | Not run | |
| R10 feedback checks | Conflicting limits and wrong exit fault | | Not run | |
| Repeatability | 20 alternating PLC cycles; accepted=10, rejected=10 | | Not run | |
| CAD | Layout, clearance and exported drawing reviewed | | Not run | |
| CAM, if attempted | Setup and toolpath simulation reviewed | | Not run | |

## Engineering reflection

- What was changed and why?
- What failed first, and what evidence explained the failure?
- What tradeoff was accepted?
- What did the author implement or verify personally, and what assistance was used?
- What remains untested?
