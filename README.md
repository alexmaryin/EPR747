# EPR747 - Boeing 747-200 Takeoff Performance Calculator

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight Electronic Flight Bag (EFB) tool for calculating reduced thrust takeoff parameters for the Boeing 747-200 with JT9D engines, based on the official United Airlines QRH Derate Procedure.

## Disclaimer

⚠️ **For simulation and educational purposes only.**

This project is designed for use with the **Felis Boeing 747-200** aircraft model in **X-Plane 12**.

- ❌ **Not certified for actual flight operations**
- ❌ **Not affiliated with Boeing, United Airlines, or X-Plane**
- ✅ Always use official airline QRH and approved EFB systems for real-world flight planning
- ✅ For real-world Boeing 747 operations, consult your airline's official performance manuals


## Features

- ✈️ **MAX EPR Calculation** - Bilinear interpolation from QRH tables (pressure altitude × temperature)
- 🔽 **Reduced Thrust (Derate)** - Assumed temperature method for engine wear reduction
- 🌡️ **Packs Configuration** - Supports 1 pack ON (base) and 3 packs OFF (+0.01 EPR)
- ⚠️ **Restriction Checks** - Validates derate eligibility per QRH (runway condition, length, windshear, etc.)
- 🎯 **V-Speeds** - V1, VR, V2 with temperature correction and minimum speed constraints
- 📏 **Takeoff Distance** - Weight, altitude, and temperature corrected calculations
- 🛫 **Climb EPR Constraint** - Ensures reduced EPR ≥ maximum climb EPR

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/epr747.git
cd epr747

# Activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the calculator
python epr.py
```

## Usage Example

```
=== B747-200 MINI EFB (QRH Derate Procedure) ===

Elevation (ft): 1000
QNH (hPa): 1013
OAT (°C): 25
Weight (tons): 280
Runway length (m): 3000
3 packs OFF? (y/N): n
Runway dry? (Y/n): y

========================================
Pressure Altitude:    1000 ft
MAX EPR:              1.542
Climb EPR (min):      1.362
Assumed Temperature:  43°C
Reduced EPR:          1.451 (94% thrust)
Takeoff Distance:     2997 m
V-speeds:             V1=135, VR=140, V2=150 knots
========================================
```

## Programmatic API

```python
from epr import calculate

result = calculate(
    elevation_ft=1000,
    qnh=1013,
    oat_c=25,
    weight=280,
    runway_m=3000,
    packs_off_3=False,
    runway_dry=True
)

print(f"Reduced EPR: {result['REDUCED_EPR']}")
print(f"V-speeds: V1={result['V1']}, VR={result['VR']}, V2={result['V2']}")
```

## Derate Restrictions

Per QRH, reduced thrust is **NOT ALLOWED** when:

- ❌ Ambient temperature below -47°F (-44°C)
- ❌ Runway length less than 7,000 feet
- ❌ Runway not dry (grooved runway is considered dry)
- ❌ Tailwind conditions
- ❌ MEL/CDL penalties applied
- ❌ Windshear probability exists
- ❌ Brakes deactivated, spare engine carried, or EPR indicator inoperative

## Input Parameters

| Parameter | Description | Units |
|-----------|-------------|-------|
| Elevation | Airport elevation | feet |
| QNH | Altimeter setting | hPa |
| OAT | Outside Air Temperature | °C |
| Weight | Aircraft takeoff weight | tons |
| Runway length | Available runway | meters |
| 3 packs OFF | Air conditioning packs | y/N |
| Runway dry | Surface condition | Y/n |

## Technical Details

### Data Sources

- **Aircraft:** Boeing 747-238B with JT9D-7J engines
- **Procedure:** United Airlines QRH Derate Procedure
- **Tables:** MAX EPR (1 pack ON), Reduced EPR (1.42-1.59)

### Algorithms

- **Pressure Altitude:** `PA = Elevation + (1013.25 - QNH) × 30`
- **MAX EPR:** Bilinear interpolation from 9×13 QRH table
- **Reduced EPR:** Interpolation from derate table with climb EPR constraint
- **Takeoff Distance:** Weight² × thrust⁻¹ × altitude × temperature factors
- **V-Speeds:** Weight-based with temperature correction and minimum limits

### Dependencies

- Python 3.14+
- Standard library only (`bisect` module)

## Testing

```bash
# Run built-in test cases
python -c "
from epr import calculate

# Test: Hong Kong RWY 31
res = calculate(33, 1013, 27, 305, 2893)
print(f'HKG: MAX EPR={res[\"MAX_EPR\"]}, Reduced={res[\"REDUCED_EPR\"]}')

# Test: Derate restriction (wet runway)
res = calculate(1000, 1013, 25, 300, 3000, runway_dry=False)
print(f'Wet runway allowed: {res[\"DERATE_ALLOWED\"]}')
"
```

## Project Structure

```
epr747/
├── epr.py                          # Main application
├── README.md                       # This file
├── QWEN.md                         # Detailed documentation
├── referene/
│   └── United derate procedure.pdf # QRH source document
├── .venv/                          # Virtual environment
└── .idea/                          # PyCharm configuration
```


## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please ensure calculations match official QRH data.

## References

- United Airlines Boeing 747-200 QRH - Reduced Takeoff Thrust Procedure
- Boeing 747-238B Performance Manual (JT9D-7J engines)
