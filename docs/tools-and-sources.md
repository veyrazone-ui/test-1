# Tools, setup and official references

References checked on 26 October 2026. Record the versions actually installed; vendor downloads and licensing can change.

## Python baseline

Install Python 3.12 and Git, clone the repository, then run the README commands. No `pip install` is needed for the reference model. The local baseline was checked with Python 3.12.14. Other interpreter versions have not been established by that local run.

- [Python unittest documentation](https://docs.python.org/3/library/unittest.html): standard-library testing and test discovery.
- [Python downloads](https://www.python.org/downloads/): official installers.

## PLC stage

Use **CODESYS Development System V3** for the documented route. Create a Standard Project with a supported target and Structured Text, a single application and a cyclic task initially set to 20 ms. Work with symbolic variables and IDE simulation; this starter does not require a fieldbus or a paid plant simulator.

The vendor lists a free Development System download and Windows requirements; the product page recommends 8 GB RAM and 12 GB available disk space. On a modest laptop, start with a watch list and small project, and run CAD separately. These published requirements do not guarantee performance on a particular laptop.

Compile, log out if necessary, select **Online → Simulation**, then **Online → Login** and run the application. Follow the vendor instructions if the installed version differs. IDE simulation and the separately installed SoftPLC runtime are different execution paths: the free IDE download is not a promise of an unrestricted runtime license.

- [CODESYS Development System V3](https://store.codesys.com/en/codesys.html): download, platform and system requirements.
- [CODESYS licensing overview](https://store.codesys.com/en/howto_applicationbasedlicenses): development system versus runtime licensing.
- [Testing in Simulation Mode](https://content.helpme-codesys.com/en/CODESYS%20Development%20System/_cds_testing_in_simulation_mode.html): testing without a physical device.
- [TON timer](https://content.helpme-codesys.com/en/libs/Standard/Current/Timer/TON.html): timer input, elapsed time and output semantics.
- [R_TRIG](https://content.helpme-codesys.com/en/libs/Standard/Current/Trigger/R_TRIG.html): rising-edge detector.

## CAD and optional CAM

FreeCAD is an open-source parametric modeler. Use a small assembly/layout and a mounting plate for this project. Its CAM workbench supports generating CNC instructions from models; the selected machine, tool setup and postprocessor still need independent validation before any machining.

- [FreeCAD features](https://www.freecad.org/features.php): parametric modeling, exchange formats and workbenches.
- [FreeCAD downloads](https://www.freecad.org/downloads.php): official packages.
- [FreeCAD CAM workbench](https://wiki.freecad.org/CAM_Workbench): manufacturing workflow documentation.

## Repository checks

The workflow uses GitHub-hosted runners, checkout and setup-python, with repository contents read permission. It runs the same Python test command as the local quick start. It does not install or test CODESYS or FreeCAD.

- [actions/checkout](https://github.com/actions/checkout)
- [actions/setup-python](https://github.com/actions/setup-python)

No software purchase is needed to run the Python starter. Check the vendor's current terms before adopting optional runtime or visualization products.
