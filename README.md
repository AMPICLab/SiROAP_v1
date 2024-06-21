# SiROAPv1

(c) Vishal Saxena, 2022

This is a work in progress and not for public use. 

## Installation
Copy the files and install the dependencies (PhotonTorch). GUI will neet some QT libraries to be installed.

## Things to Do:

1. Do a better job of handling I/O ports in the array, it's confusing and error-prone as of now.

2. Add a Thermal crosstalk model to the array. Change the simulator to simulate thermal crosstalk.

3. Add code for thermal crosstalk estimation and mitigation.

The code uses phase for the BTUs instead of using DAC power. However, it may not be an issue unless electrical nonidealities need to be modeled.

## References to Cite:

1. M. J. Shawon and V. Saxena, "A Silicon Photonic Reconfigurable Optical Analog Processor (SiROAP) with a 4x4 Optical Mesh," in IEEE International Solid State Circuits Conference (ISSCC), San Francisco, Feb 2023.

2. M. J. Shawon and V. Saxena, "A 7× 4 Silicon Photonic Reconfigurable Optical Analog Processor with Algorithmic Calibration," Optical Fiber Communication Conference (OFC), Optica Publishing Group, San Diego, CA, March 2024.

3. V. Saxena and M. J. Shawon, "Reconfigurable RF Photonic Processor Architecture using a Silicon Photonics MPW Platform," GOMACTech 2022, Miami, FL, Apr 2022.

## License:
The SiROAP source code is the sole property and copyright of Vishal Saxena and cannot be reused or adapted without written permission and license from the author.
