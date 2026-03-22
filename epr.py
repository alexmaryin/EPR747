"""Compatibility wrapper + CLI for EPR747.

Core calculator logic lives in epr747/calculator.py so XPPython3 deployment can
ship a single PI_*.py plugin file plus one dedicated subdirectory.
"""

from epr747.calculator import AVAILABLE_FLAPS, DEFAULT_FLAPS, calculate

__all__ = ["calculate"]


if __name__ == "__main__":
    print("=== B747-200 MINI EFB (QRH Derate Procedure) ===\n")

    elev = float(input("Elevation (ft): "))
    qnh = float(input("QNH (hPa): "))
    oat = float(input("OAT (°C): "))
    weight = float(input("Weight (tons): "))
    runway = float(input("Runway length (m): "))

    flaps_input = input("Flaps (10/20) [10]: ").strip()
    flaps = int(flaps_input) if flaps_input else DEFAULT_FLAPS
    if flaps not in AVAILABLE_FLAPS:
        print(f"Invalid flap setting. Using default: {DEFAULT_FLAPS}")
        flaps = DEFAULT_FLAPS

    packs_input = input("3 packs OFF? (y/N): ").strip().lower()
    packs_off = packs_input == "y"

    dry_input = input("Runway dry? (Y/n): ").strip().lower()
    runway_dry = dry_input != "n"

    wind_hw = float(input("Headwind (kts) [0]: ").strip() or 0)
    wind_tw = float(input("Tailwind (kts) [0]: ").strip() or 0)

    res = calculate(
        elev,
        qnh,
        oat,
        weight,
        runway,
        flaps=flaps,
        packs_off_3=packs_off,
        runway_dry=runway_dry,
        wind_headwind=wind_hw,
        wind_tailwind=wind_tw,
    )

    print("\n" + "=" * 45)
    print("=== RESULT ===")
    print("=" * 45)

    if not res["DERATE_ALLOWED"]:
        print("\nDERATE NOT ALLOWED:")
        for reason in res["RESTRICTION_REASONS"]:
            print(f"   - {reason}")
        print()

    print(f"Pressure Altitude:    {res['PA_ft']} ft ({res['PA_kft']} kft)")
    print(f"OAT:                  {res['OAT_C']}°C / {res['OAT_F']}°F")
    print(f"Flaps:                {res['FLAPS']}°")
    print(f"Weight:               {weight} t ({res['ACTUAL_WEIGHT_K_LBS']}k lbs)")
    print()
    print(f"Runway Limit Weight:  {res['RUNWAY_LIMIT_WEIGHT']}k lbs")
    print(f"Climb Limit Weight:   {res['CLIMB_LIMIT_WEIGHT']}k lbs")
    print(f"Weight Margin:        {res['WEIGHT_MARGIN_K_LBS']}k lbs")
    print()
    print(
        f"MAX EPR:              {res['MAX_EPR']}"
        f"{' (3 packs OFF)' if res['PACKS_OFF_3'] else ' (1 pack ON)'}"
    )
    print(f"Climb EPR (min):      {res['CLIMB_EPR']}")
    print()
    print(f"Assumed Temperature:  {res['ASSUMED_TEMP_C']}°C / {res['ASSUMED_TEMP_F']}°F")
    print(f"Reduced EPR:          {res['REDUCED_EPR']}")
    print(f"Thrust Ratio:         {res['THRUST_RATIO']} ({res['THRUST_RATIO'] * 100:.0f}%)")
    print()
    print(f"Takeoff Distance:     {res['DIST_REQUIRED_M']} m / {res['DIST_REQUIRED_FT']} ft")
    print(f"Runway Available:     {res['RUNWAY_AVAILABLE_M']} m / {res['RUNWAY_AVAILABLE_FT']} ft")
    print()
    print(f"V1:                   {res['V1']} knots")
    print(f"VR:                   {res['VR']} knots")
    print(f"V2:                   {res['V2']} knots")
    print("=" * 45)
