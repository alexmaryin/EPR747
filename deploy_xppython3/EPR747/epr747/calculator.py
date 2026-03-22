import bisect

# =========================
# TABLES (from QRH - United 747-200 Derate Procedure)
# =========================

TEMP_GRID_F = [60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120]
PA_GRID_KFT = [0, 1, 2, 3, 4, 5, 6, 7, 8]

# MAX TAKEOFF THRUST - EPR (1 PACK ON, nacelle anti-ice on or off)
# Source: United 747-200 QRH Derate Procedure
# For 3 packs OFF, increase EPR by 0.01
MAX_EPR_TABLE = [
    [1.59, 1.58, 1.56, 1.55, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],  # 0 kft
    [1.59, 1.58, 1.56, 1.55, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],  # 1 kft
    [1.58, 1.58, 1.56, 1.55, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],  # 2 kft
    [1.57, 1.57, 1.56, 1.55, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],  # 3 kft
    [1.56, 1.56, 1.56, 1.55, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],  # 4 kft
    [1.55, 1.55, 1.55, 1.55, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],  # 5 kft
    [1.54, 1.54, 1.54, 1.54, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],  # 6 kft
    [1.53, 1.53, 1.53, 1.53, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],  # 7 kft
    [1.52, 1.52, 1.52, 1.52, 1.52, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],  # 8 kft
]

# REDUCED TAKEOFF THRUST (DERATE TABLE)
# Complete table from PDF including all entries down to 1.42
REDUCED_EPR_TABLE = {
    1.59: [1.59, 1.58, 1.56, 1.55, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.45, 1.45],
    1.58: [1.58, 1.58, 1.56, 1.55, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.44],
    1.57: [1.57, 1.57, 1.56, 1.55, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.43],
    1.56: [1.56, 1.56, 1.56, 1.55, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],
    1.55: [1.55, 1.55, None, 1.55, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],
    1.54: [1.54, 1.54, None, 1.54, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],
    1.53: [1.53, 1.53, None, None, 1.53, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],
    1.52: [1.52, 1.52, None, None, None, 1.52, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],
    1.51: [1.51, 1.51, None, None, None, None, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],
    1.50: [1.50, None, None, None, None, None, 1.50, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],
    1.49: [None, None, None, None, None, None, 1.49, 1.49, 1.47, 1.46, 1.45, 1.44, 1.42],
    1.48: [None, None, None, None, None, None, None, 1.48, 1.47, 1.46, 1.45, 1.44, 1.42],
    1.47: [None, None, None, None, None, None, None, 1.47, 1.47, 1.46, 1.45, 1.44, 1.42],
    1.46: [None, None, None, None, None, None, None, None, 1.46, 1.46, 1.45, 1.44, 1.42],
    1.45: [None, None, None, None, None, None, None, None, None, 1.45, 1.45, 1.44, 1.42],
    1.44: [None, None, None, None, None, None, None, None, None, None, 1.44, 1.44, 1.42],
    1.43: [None, None, None, None, None, None, None, None, None, None, None, 1.43, 1.42],
    1.42: [None, None, None, None, None, None, None, None, None, None, None, None, 1.42],
}

# Minimum temperatures for derate (°F) - below these, derate is not allowed
# Based on PDF restrictions: ambient temp below -47°F (-44°C)
MIN_AMBIENT_TEMP_F = -47  # Derate not allowed below -47°F (-44°C)

# Minimum runway length for derate (feet)
MIN_RUNWAY_LENGTH_FT = 7000

# =========================
# FLAPS CONFIGURATION
# =========================

# Available flap settings for takeoff (degrees)
AVAILABLE_FLAPS = [10, 20]
DEFAULT_FLAPS = 10

# Runway-limited takeoff weight (k lbs) at 80°F for HKG RWY 31 (9491 ft)
# Extracted from PDF: Hong Kong takeoff performance tables
# Note: These are example values - actual tables vary by airport/runway
RUNWAY_LIMIT_BASE_80F = {
    10: 719.6,  # Flaps 10: 719.6k lbs at 80°F
    20: 744.1,  # Flaps 20: 744.1k lbs at 80°F (allows ~24.5k lbs more)
}

# Climb-limited takeoff weight (k lbs)
# From PDF: Climb limits decrease with higher flap settings
CLIMB_LIMIT_WEIGHT = {
    10: 840.0,  # Flaps 10: 840k lbs climb limit
    20: 811.0,  # Flaps 20: 811k lbs climb limit (lower due to drag)
}

# Temperature correction for runway-limited weight (k lbs per °F above 80°F)
# Approximate from PDF table data
RUNWAY_LIMIT_TEMP_SLOPE = {
    10: -0.638,  # Flaps 10: weight decreases ~0.64k lbs/°F
    20: -0.727,  # Flaps 20: weight decreases ~0.73k lbs/°F
}

# Wind correction factors (lbs per knot)
# From PDF: Headwind/Tailwind corrections by flap setting
WIND_CORRECTION = {
    10: {
        'headwind': 1170,  # lbs/kt (increases limit weight)
        'tailwind': -4190,  # lbs/kt (decreases limit weight)
    },
    20: {
        'headwind': 3940,  # lbs/kt
        'tailwind': -3940,  # lbs/kt
    }
}


# =========================
# INTERPOLATION
# =========================

def interp(x, grid, values):
    """Linear interpolation with None value handling."""
    if x <= grid[0]:
        return values[0]
    if x >= grid[-1]:
        return values[-1]

    i = bisect.bisect_left(grid, x)
    x1, x2 = grid[i-1], grid[i]
    y1, y2 = values[i-1], values[i]

    # Handle None values - use the valid one
    if y1 is None and y2 is None:
        return None
    if y1 is None:
        return y2
    if y2 is None:
        return y1

    t = (x - x1) / (x2 - x1)
    return y1 + t * (y2 - y1)


def bilinear(pa_kft, temp_f):
    """Bilinear interpolation for MAX EPR from pressure altitude and temperature."""
    pa_kft = max(0, min(8, pa_kft))

    i = int(pa_kft)
    frac = pa_kft - i

    row1 = MAX_EPR_TABLE[i]
    row2 = MAX_EPR_TABLE[min(i + 1, 8)]

    v1 = interp(temp_f, TEMP_GRID_F, row1)
    v2 = interp(temp_f, TEMP_GRID_F, row2)

    if v1 is None or v2 is None:
        return None

    return v1 + frac * (v2 - v1)


def nearest_key(value, keys):
    """Find the nearest key value from a list of keys."""
    return min(keys, key=lambda x: abs(x - value))


def interp_reduced_epr(max_epr, temp_f):
    """
    Interpolate reduced EPR from the derate table.
    Uses bilinear interpolation between MAX EPR rows.
    """
    available_keys = sorted(REDUCED_EPR_TABLE.keys())
    
    # Find bracketing rows
    if max_epr <= available_keys[0]:
        row_values = REDUCED_EPR_TABLE[available_keys[0]]
        return interp(temp_f, TEMP_GRID_F, row_values)
    
    if max_epr >= available_keys[-1]:
        row_values = REDUCED_EPR_TABLE[available_keys[-1]]
        return interp(temp_f, TEMP_GRID_F, row_values)
    
    # Find the two bracketing max_epr values
    lower_key = None
    upper_key = None
    for key in available_keys:
        if key <= max_epr:
            lower_key = key
        elif upper_key is None:
            upper_key = key
            break
    
    if lower_key is None or upper_key is None:
        return None
    
    lower_values = REDUCED_EPR_TABLE[lower_key]
    upper_values = REDUCED_EPR_TABLE[upper_key]
    
    lower_result = interp(temp_f, TEMP_GRID_F, lower_values)
    upper_result = interp(temp_f, TEMP_GRID_F, upper_values)
    
    if lower_result is None and upper_result is None:
        return None
    if lower_result is None:
        return upper_result
    if upper_result is None:
        return lower_result
    
    # Interpolate between the two rows
    t = (max_epr - lower_key) / (upper_key - lower_key)
    return lower_result + t * (upper_result - lower_result)


# =========================
# RESTRICTION CHECKS
# =========================

def check_derate_restrictions(oat_c, runway_m, wind_headwind, wind_tailwind, 
                               runway_dry, mel_cdl_penalty, windshear_prob):
    """
    Check if reduced thrust takeoff is allowed per QRH restrictions.
    Returns (allowed: bool, reasons: list of strings)
    """
    reasons = []
    oat_f = oat_c * 9/5 + 32
    runway_ft = runway_m * 3.28084
    
    if oat_f < MIN_AMBIENT_TEMP_F:
        reasons.append(f"Ambient temp {oat_f:.0f}°F below minimum ({MIN_AMBIENT_TEMP_F}°F / -47°C)")
    
    if runway_ft < MIN_RUNWAY_LENGTH_FT:
        reasons.append(f"Runway length {runway_ft:.0f}ft below minimum ({MIN_RUNWAY_LENGTH_FT}ft)")
    
    if not runway_dry:
        reasons.append("Runway must be dry (grooved runway is considered dry)")
    
    if wind_tailwind > 0:
        reasons.append("Tailwind conditions - derate not allowed")
    
    if mel_cdl_penalty:
        reasons.append("MEL/CDL weight/performance penalties applied")
    
    if windshear_prob:
        reasons.append("Probability of windshear exists")
    
    return len(reasons) == 0, reasons


# =========================
# CLIMB EPR CALCULATION
# =========================

def calculate_climb_epr(pa_kft, temp_f):
    """
    Calculate maximum climb EPR based on field elevation and OAT.
    This is a simplified model - actual QRH would have a climb EPR table.
    Typical climb EPR is around 1.35-1.45 depending on altitude and temp.
    """
    # Simplified climb EPR model (typical for JT9D engines)
    # Base climb EPR at sea level, standard temp
    base_climb = 1.40
    
    # Decrease with altitude (approximately 0.02 per 1000 ft)
    altitude_correction = pa_kft * 0.02
    
    # Decrease with temperature (approximately 0.001 per °F above 59°F)
    temp_correction = max(0, (temp_f - 59)) * 0.001
    
    climb_epr = base_climb - altitude_correction - temp_correction
    
    return max(1.30, min(1.45, climb_epr))  # Clamp to reasonable range


# =========================
# PHYSICS MODEL
# =========================

def takeoff_distance(weight, thrust_ratio, pa_kft, temp_f):
    """
    Calculate required takeoff distance.
    More accurate model including altitude and temperature effects.
    """
    # Base distance for 300t at full thrust, sea level, standard temp
    base = 2800  # meters
    
    # Weight effect (squared relationship)
    weight_factor = (weight / 300) ** 2
    
    # Thrust effect (inverse relationship)
    thrust_factor = 1.0 / max(0.7, thrust_ratio)  # Limit to avoid extreme values
    
    # Altitude effect (density altitude - increases distance)
    altitude_factor = 1.0 + (pa_kft * 0.05)  # ~5% increase per 1000 ft
    
    # Temperature effect (increases distance)
    temp_factor = 1.0 + max(0, (temp_f - 59)) * 0.002  # ~0.2% per °F above standard
    
    return base * weight_factor * thrust_factor * altitude_factor * temp_factor


def thrust_ratio(reduced_epr, max_epr):
    """Calculate thrust ratio from EPR values."""
    if max_epr is None or max_epr <= 0:
        return 1.0
    return reduced_epr / max_epr


def v_speeds(weight, assumed_temp_f, oat_f, flaps):
    """
    Calculate V1, VR, V2 speeds.
    Per PDF: Use speeds at assumed temperature, but not less than V-minimum.
    Flap setting affects V-speeds (higher flaps = lower speeds).
    """
    # Flap correction factor (20 flaps = slightly lower speeds than 10 flaps)
    flap_correction = 0 if flaps == 10 else -2
    
    # Base V-speeds from weight (similar to 747 characteristics)
    v2_base = 140 + 0.2 * (weight - 250) + flap_correction
    vr_base = v2_base - 10
    v1_base = vr_base - 5

    # Temperature correction (higher temp = higher speeds)
    # For each 10°F above standard (59°F), increase by ~1 knot
    temp_correction = max(0, (assumed_temp_f - 59)) * 0.1

    v2 = v2_base + temp_correction
    vr = vr_base + temp_correction
    v1 = v1_base + temp_correction

    # Minimum speeds (simplified - actual QRH has V-min table)
    # Vary slightly by flap setting
    v2_min = 128 if flaps == 20 else 130
    vr_min = 118 if flaps == 20 else 120
    v1_min = 108 if flaps == 20 else 110

    # Use the HIGHEST of calculated vs minimum (per PDF procedure)
    return (
        round(max(v1, v1_min)),
        round(max(vr, vr_min)),
        round(max(v2, v2_min))
    )


def calculate_runway_limit_weight(flaps, temp_f, wind_headwind=0, wind_tailwind=0,
                                   runway_length_ft=9491, slope_pct=0):
    """
    Calculate runway-limited takeoff weight based on flap setting, temperature, and wind.
    Based on PDF Hong Kong RWY 31 tables.
    
    Args:
        flaps: Flap setting (10 or 20)
        temp_f: Temperature in °F
        wind_headwind: Headwind component in knots
        wind_tailwind: Tailwind component in knots
        runway_length_ft: Runway length in feet (default: HKG RWY 31 = 9491 ft)
        slope_pct: Runway slope percentage (default: 0)
    
    Returns:
        Runway-limited weight in k lbs
    """
    # Base weight at 80°F for reference runway (9491 ft)
    base_weight = RUNWAY_LIMIT_BASE_80F.get(flaps, 719.6)
    
    # Temperature correction (from 80°F reference)
    temp_delta = temp_f - 80
    temp_correction = RUNWAY_LIMIT_TEMP_SLOPE.get(flaps, -0.638) * temp_delta
    
    # Wind correction
    if wind_headwind > 0:
        wind_corr_lbs = WIND_CORRECTION[flaps]['headwind'] * wind_headwind
    elif wind_tailwind > 0:
        wind_corr_lbs = WIND_CORRECTION[flaps]['tailwind'] * wind_tailwind
    else:
        wind_corr_lbs = 0
    
    wind_correction_k = wind_corr_lbs / 1000  # Convert to k lbs
    
    # Runway length correction (approximate: proportional to available runway)
    reference_runway = 9491  # HKG RWY 31
    runway_factor = runway_length_ft / reference_runway
    
    # Slope correction (uphill = more weight allowed, downhill = less)
    # Approximate: 1% slope ≈ 2% weight adjustment
    slope_correction = slope_pct * 0.02 * base_weight
    
    # Calculate final limit
    limit_weight = (base_weight + temp_correction + wind_correction_k) * runway_factor + slope_correction
    
    return max(0, limit_weight)


def calculate_climb_limit_weight(flaps, pa_kft, temp_f):
    """
    Calculate climb-limited takeoff weight based on flap setting and conditions.
    From PDF: Climb limits are fixed but decrease with higher flap settings.
    
    Args:
        flaps: Flap setting (10 or 20)
        pa_kft: Pressure altitude in thousands of feet
        temp_f: Temperature in °F
    
    Returns:
        Climb-limited weight in k lbs
    """
    # Base climb limit at sea level, standard conditions
    base_climb_limit = CLIMB_LIMIT_WEIGHT.get(flaps, 840.0)
    
    # Altitude correction (climb performance decreases with altitude)
    # Approximate: 2% reduction per 1000 ft PA
    altitude_factor = 1.0 - (pa_kft * 0.02)
    
    # Temperature correction (climb performance decreases with temp)
    # Approximate: 0.5% reduction per °F above 59°F (ISA)
    temp_factor = 1.0 - max(0, (temp_f - 59)) * 0.005
    
    climb_limit = base_climb_limit * altitude_factor * temp_factor
    
    return max(0, climb_limit)


# =========================
# CORE CALCULATION
# =========================

def calculate(elevation_ft, qnh, oat_c, weight, runway_m,
              flaps=10, packs_off_3=False, runway_dry=True,
              wind_headwind=0, wind_tailwind=0,
              mel_cdl_penalty=False, windshear_prob=False,
              runway_slope_pct=0):
    """
    Calculate takeoff performance parameters per QRH procedure.

    Args:
        elevation_ft: Airport elevation in feet
        qnh: Altimeter setting in hPa
        oat_c: Outside air temperature in °C
        weight: Aircraft weight in tons
        runway_m: Runway length in meters
        flaps: Takeoff flap setting (10 or 20 degrees)
        packs_off_3: True if 3 packs OFF (adds 0.01 to max EPR)
        runway_dry: True if runway is dry
        wind_headwind: Headwind component in knots
        wind_tailwind: Tailwind component in knots
        mel_cdl_penalty: True if MEL/CDL penalties apply
        windshear_prob: True if windshear probability exists
        runway_slope_pct: Runway slope percentage (positive = uphill)

    Returns:
        Dictionary with calculation results
    """
    # Validate flap setting
    if flaps not in AVAILABLE_FLAPS:
        raise ValueError(f"Invalid flap setting. Available: {AVAILABLE_FLAPS}")
    
    # Calculate pressure altitude
    pa = elevation_ft + (1013.25 - qnh) * 30
    pa_kft = pa / 1000
    
    # Convert temperature
    oat_f = oat_c * 9/5 + 32
    runway_ft = runway_m * 3.28084
    
    # Calculate weight limits
    runway_limit_k_lbs = calculate_runway_limit_weight(
        flaps, oat_f, wind_headwind, wind_tailwind, runway_ft, runway_slope_pct
    )
    climb_limit_k_lbs = calculate_climb_limit_weight(flaps, pa_kft, oat_f)
    
    # Convert actual weight to k lbs for comparison
    weight_k_lbs = weight * 2.20462  # tons to k lbs
    
    # Determine limiting weight and temperature
    runway_limit_temp = oat_f  # Current temp for runway limit
    max_runway_temp = None  # Will find highest temp where weight is still allowable
    
    # Find maximum assumed temperature for runway-limited performance
    # (highest temp where actual weight <= runway limit)
    for temp_f_check in range(int(oat_f), 150):
        limit_at_temp = calculate_runway_limit_weight(
            flaps, temp_f_check, wind_headwind, wind_tailwind, runway_ft, runway_slope_pct
        )
        if weight_k_lbs <= limit_at_temp:
            max_runway_temp = temp_f_check
        else:
            break
    
    # Find maximum assumed temperature for climb-limited performance
    max_climb_temp = None
    for temp_f_check in range(int(oat_f), 150):
        limit_at_temp = calculate_climb_limit_weight(flaps, pa_kft, temp_f_check)
        if weight_k_lbs <= limit_at_temp:
            max_climb_temp = temp_f_check
        else:
            break
    
    # Check derate restrictions
    allowed, reasons = check_derate_restrictions(
        oat_c, runway_m, wind_headwind, wind_tailwind,
        runway_dry, mel_cdl_penalty, windshear_prob
    )
    
    # Calculate MAX EPR (1 PACK ON base)
    max_epr = bilinear(pa_kft, oat_f)
    
    # Apply packs correction if 3 packs OFF
    if packs_off_3 and max_epr is not None:
        max_epr += 0.01
    
    # Calculate climb EPR (minimum for reduced thrust)
    climb_epr = calculate_climb_epr(pa_kft, oat_f)
    
    # Find best assumed temperature using iterative method
    best = None
    
    # Determine the limiting assumed temperature (lower of runway vs climb limits)
    if max_runway_temp is not None and max_climb_temp is not None:
        max_assumed_temp_f = min(max_runway_temp, max_climb_temp)
    elif max_runway_temp is not None:
        max_assumed_temp_f = max_runway_temp
    elif max_climb_temp is not None:
        max_assumed_temp_f = max_climb_temp
    else:
        max_assumed_temp_f = int(oat_f)  # No derate possible
    
    # Iterate through possible assumed temperatures
    for temp_c in range(int(oat_c), min(60, int(max_assumed_temp_f / 1.8 - 32 * 5/9) + 10)):
        temp_f = temp_c * 9/5 + 32
        
        # Don't exceed the limiting temperature
        if temp_f > max_assumed_temp_f:
            break
        
        # Get reduced EPR for this assumed temperature
        reduced = interp_reduced_epr(max_epr, temp_f)
        
        if reduced is None:
            continue
        
        # Apply minimum constraint: reduced EPR >= climb EPR
        reduced = max(reduced, climb_epr)
        
        # Calculate thrust ratio and required distance
        tr = thrust_ratio(reduced, max_epr)
        dist = takeoff_distance(weight, tr, pa_kft, temp_f)
        
        # Check if runway is sufficient
        if dist <= runway_m:
            # Prefer higher assumed temperature (more derate, less engine wear)
            if best is None or temp_c > best[0]:
                best = (temp_c, reduced, dist)
    
    # Fallback if no valid assumed temperature found
    if best is None:
        best = (oat_c, max_epr, takeoff_distance(weight, 1.0, pa_kft, oat_f))
    
    assumed_temp_c, reduced_epr, dist_required = best
    
    # Calculate V-speeds
    assumed_temp_f = assumed_temp_c * 9/5 + 32
    v1, vr, v2 = v_speeds(weight, assumed_temp_f, oat_f, flaps)
    
    return {
        "PA_ft": round(pa),
        "PA_kft": round(pa_kft, 2),
        "OAT_C": round(oat_c, 1),
        "OAT_F": round(oat_f, 1),
        "FLAPS": flaps,
        "MAX_EPR": round(max_epr, 3) if max_epr else None,
        "CLIMB_EPR": round(climb_epr, 3),
        "ASSUMED_TEMP_C": assumed_temp_c,
        "ASSUMED_TEMP_F": round(assumed_temp_f, 1),
        "REDUCED_EPR": round(reduced_epr, 3),
        "THRUST_RATIO": round(thrust_ratio(reduced_epr, max_epr), 3),
        "DIST_REQUIRED_M": round(dist_required),
        "DIST_REQUIRED_FT": round(dist_required * 3.28084),
        "RUNWAY_AVAILABLE_M": runway_m,
        "RUNWAY_AVAILABLE_FT": round(runway_ft),
        "RUNWAY_LIMIT_WEIGHT": round(runway_limit_k_lbs, 1),
        "CLIMB_LIMIT_WEIGHT": round(climb_limit_k_lbs, 1),
        "ACTUAL_WEIGHT_K_LBS": round(weight_k_lbs, 1),
        "WEIGHT_MARGIN_K_LBS": round(min(runway_limit_k_lbs, climb_limit_k_lbs) - weight_k_lbs, 1),
        "V1": v1,
        "VR": vr,
        "V2": v2,
        "DERATE_ALLOWED": allowed,
        "RESTRICTION_REASONS": reasons,
        "PACKS_OFF_3": packs_off_3,
        "MAX_ASSUMED_TEMP_F": round(max_assumed_temp_f, 1),
    }


