EPR747 XPPython3 Deployment Package
====================================
B747-200 Derate Calculator Plugin for X-Plane 12

PREREQUISITES
-------------
1. X-Plane 12.00 or later
2. XPPython3 plugin installed:
   - Download from: https://github.com/uglydwarf/x-plane_plugins
   - Install to: <X-Plane>/Resources/plugins/XPPython3/

INSTALLATION
------------
1. Copy these files to: <X-Plane>/Resources/plugins/PythonPlugins/

   Result structure:
   PythonPlugins/
   ├── PI_EPR747.py
   └── epr747/
       ├── __init__.py
       └── calculator.py

2. Start X-Plane 12 (or reload plugins if already running)
3. The plugin will appear under the "Plugins" menu as "EPR747 >"

USAGE
-----
1. Select Plugins > EPR747 > Open Calculator
2. Adjust input parameters:
   - Elevation, QNH, OAT
   - Weight, Runway length
   - Wind components, Runway slope
   - Flap setting (10 or 20)
   - Configuration options (packs, runway condition, etc.)
3. Click "Calculate" for takeoff performance data
4. Results include:
   - MAX/REDUCED/CLIMB EPR
   - Assumed temperature
   - Thrust ratio
   - Takeoff distance required
   - Weight limits and margin
   - V1/VR/V2 speeds

TECHNICAL NOTES
---------------
- Reads X-Plane datarefs for auto-population (elevation, QNH, OAT, weight, flaps)
- Click "Refresh from Sim" to update from current flight state
- No datarefs are written - plugin is display-only
- Calculator uses official United 747-200 QRH derate procedure
- Based on JT9D-7J engine performance tables

TROUBLESHOOTING
---------------
- If plugin doesn't appear, check X-Plane Log.txt for errors
- Ensure XPPython3 is loaded before this plugin
- Verify Python 3.10+ compatibility

VERSION
-------
1.0 - Initial release with QRH derate procedure
