"""XPPython3 plugin: EPR747 calculator window for X-Plane 12.

Drop this file and the epr747/ subdirectory into:
  X-Plane 12/Resources/plugins/PythonPlugins/

XPPython3 prerequisites / deployment notes (official docs):
- Requires X-Plane 12.00+ and XPPython3 for XP12.
- Install XPPython3 under:
    <X-Plane>/Resources/plugins/XPPython3/
- Third-party Python plugins are loaded from:
    <X-Plane>/Resources/plugins/PythonPlugins/
- Plugin entry file must be named PI_*.py
- Do not place third-party plugin files in XPPython3 internal folders.
- References:
    https://xppython3.readthedocs.io/en/latest/development/deployment.html
    https://xppython3.readthedocs.io/en/latest/usage/installation_plugin.html

Design constraints:
- Window opens from Plugins menu.
- No frame-loop or periodic callbacks for calculations.
- All work is triggered by explicit user actions.
- Read available sim/model parameters when window opens or on Refresh.
- Display results in plugin UI only (no writes to sim/model datarefs).

Copyright (c) 2026 Alex Maryin <java.ul@gmail.com>
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from XPPython3 import xp

FT_PER_M = 3.28084
HPA_PER_INHG = 33.8638866667


class PythonInterface:
    def __init__(self):
        self.Name = "EPR747"
        self.Sig = "epr747.plugin.xppython3"
        self.Desc = "B747-200 derate calculator UI"

        self.menu_id = None
        self.window = None

        self.widgets: Dict[str, Any] = {}
        self.result_lines = []

        self.dr_elevation_m = None
        self.dr_qnh_inhg = None
        self.dr_oat_c = None
        self.dr_weight_kg = None
        self.dr_flap_deg = None

        self.calculate_func = None
        self.import_error = None

    # ---------------------------
    # XPPython3 lifecycle
    # ---------------------------

    def XPluginStart(self):
        self._resolve_calculator_import()
        self._find_datarefs()

        # Creates "EPR747 >" under Plugins menu.
        self.menu_id = xp.createMenu("EPR747", handler=self._menu_handler, refCon="main")
        xp.appendMenuItem(self.menu_id, "Open Calculator", "open")
        xp.appendMenuItem(self.menu_id, "Close Calculator", "close")

        return self.Name, self.Sig, self.Desc

    def XPluginStop(self):
        self._destroy_window()
        if self.menu_id:
            xp.destroyMenu(self.menu_id)
            self.menu_id = None

    def XPluginEnable(self):
        return 1

    def XPluginDisable(self):
        self._destroy_window()

    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
        pass

    # ---------------------------
    # Setup helpers
    # ---------------------------

    def _resolve_calculator_import(self):
        try:
            from epr747.calculator import calculate

            self.calculate_func = calculate
            self.import_error = None
        except Exception as exc:  # pragma: no cover
            self.calculate_func = None
            self.import_error = f"Cannot import epr747.calculator.calculate: {exc}"

    def _find_datarefs(self):
        # Common X-Plane 12 datarefs used only for read/prefill.
        self.dr_elevation_m = self._find_first_dataref([
            "sim/flightmodel/position/elevation",
        ])
        self.dr_qnh_inhg = self._find_first_dataref([
            "sim/weather/barometer_sealevel_inhg",
            "sim/cockpit2/gauges/actuators/barometer_setting_in_hg_pilot",
        ])
        self.dr_oat_c = self._find_first_dataref([
            "sim/weather/temperature_ambient_c",
            "sim/cockpit2/temperature/outside_air_temp_degc",
        ])
        self.dr_weight_kg = self._find_first_dataref([
            "sim/flightmodel/weight/m_total",
        ])

    # ---------------------------
    # Menu + window
    # ---------------------------

    def _menu_handler(self, menuRefCon, itemRefCon):
        if menuRefCon != "main":
            return

        if itemRefCon == "open":
            self._open_window()
        elif itemRefCon == "close":
            self._destroy_window()

    def _open_window(self):
        if self.window:
            return

        self.window = self._create_widget_window()
        self._refresh_fields_from_sim()
        self._set_results([
            "EPR747 ready.",
            "Adjust values, then click Calculate.",
        ])

    def _destroy_window(self):
        if self.window:
            xp.destroyWidget(self.window["widgetID"], 1)
            self.window = None
            self.widgets = {}
            self.result_lines = []

    def _create_widget_window(self):
        window = {"widgetID": None, "widgets": {}}

        left = 120
        top = 730
        right = 740
        bottom = 120

        window["widgetID"] = xp.createWidget(
            left,
            top,
            right,
            bottom,
            1,
            "EPR747 Derate Calculator",
            1,
            0,
            xp.WidgetClass_MainWindow,
        )
        xp.addWidgetCallback(window["widgetID"], self._widget_callback)
        xp.setWidgetProperty(window["widgetID"], xp.Property_MainWindowHasCloseBoxes, 1)

        # Build form rows.
        row_y = top - 35
        row_step = 28
        label_x = left + 12
        field_x1 = left + 245
        field_x2 = right - 16

        def add_text_row(key: str, label: str, default_value: str):
            nonlocal row_y
            xp.createWidget(
                label_x,
                row_y,
                field_x1 - 8,
                row_y - 18,
                1,
                label,
                0,
                window["widgetID"],
                xp.WidgetClass_Caption,
            )
            widget_id = xp.createWidget(
                field_x1,
                row_y,
                field_x2,
                row_y - 20,
                1,
                default_value,
                0,
                window["widgetID"],
                xp.WidgetClass_TextField,
            )
            xp.setWidgetProperty(widget_id, xp.Property_TextFieldType, xp.TextEntryField)
            window["widgets"][key] = widget_id
            row_y -= row_step

        add_text_row("elevation_ft", "Elevation (ft)", "0")
        add_text_row("qnh_hpa", "QNH (hPa)", "1013.25")
        add_text_row("oat_c", "OAT (C)", "15")
        add_text_row("weight_t", "Weight (metric tons)", "300")
        add_text_row("runway_m", "Runway length (m)", "3000")
        add_text_row("headwind", "Headwind (kts)", "0")
        add_text_row("tailwind", "Tailwind (kts)", "0")
        add_text_row("runway_slope_pct", "Runway slope (%)", "0")

        # Flap selector as dedicated radio controls.
        xp.createWidget(
            label_x,
            row_y,
            field_x1 - 8,
            row_y - 18,
            1,
            "Flaps",
            0,
            window["widgetID"],
            xp.WidgetClass_Caption,
        )
        flap10_id = xp.createWidget(
            field_x1,
            row_y,
            field_x1 + 90,
            row_y - 20,
            1,
            "10",
            0,
            window["widgetID"],
            xp.WidgetClass_Button,
        )
        flap20_id = xp.createWidget(
            field_x1 + 100,
            row_y,
            field_x1 + 190,
            row_y - 20,
            1,
            "20",
            0,
            window["widgetID"],
            xp.WidgetClass_Button,
        )
        for widget_id in (flap10_id, flap20_id):
            xp.setWidgetProperty(widget_id, xp.Property_ButtonType, xp.RadioButton)
            xp.setWidgetProperty(widget_id, xp.Property_ButtonBehavior, xp.ButtonBehaviorRadioButton)
        window["widgets"]["flaps_10"] = flap10_id
        window["widgets"]["flaps_20"] = flap20_id
        xp.setWidgetProperty(flap10_id, xp.Property_ButtonState, 1)
        xp.setWidgetProperty(flap20_id, xp.Property_ButtonState, 0)
        row_y -= row_step

        # Checkbox rows.
        def add_checkbox_row(key: str, label: str, checked: bool):
            nonlocal row_y
            button_id = xp.createWidget(
                label_x,
                row_y,
                field_x2,
                row_y - 20,
                1,
                label,
                0,
                window["widgetID"],
                xp.WidgetClass_Button,
            )
            xp.setWidgetProperty(button_id, xp.Property_ButtonType, xp.RadioButton)
            xp.setWidgetProperty(button_id, xp.Property_ButtonBehavior, xp.ButtonBehaviorCheckBox)
            xp.setWidgetProperty(button_id, xp.Property_ButtonState, 1 if checked else 0)
            window["widgets"][key] = button_id
            row_y -= row_step

        add_checkbox_row("packs_off_3", "3 packs OFF", False)
        add_checkbox_row("runway_dry", "Runway dry", True)
        add_checkbox_row("mel_cdl_penalty", "MEL/CDL penalty", False)
        add_checkbox_row("windshear_prob", "Windshear probability", False)

        # Action buttons.
        buttons_top = row_y - 4
        refresh_btn = xp.createWidget(
            label_x,
            buttons_top,
            label_x + 170,
            buttons_top - 24,
            1,
            "Refresh from Sim",
            0,
            window["widgetID"],
            xp.WidgetClass_Button,
        )
        calc_btn = xp.createWidget(
            label_x + 185,
            buttons_top,
            label_x + 320,
            buttons_top - 24,
            1,
            "Calculate",
            0,
            window["widgetID"],
            xp.WidgetClass_Button,
        )
        close_btn = xp.createWidget(
            label_x + 335,
            buttons_top,
            label_x + 430,
            buttons_top - 24,
            1,
            "Close",
            0,
            window["widgetID"],
            xp.WidgetClass_Button,
        )

        window["widgets"]["refresh_btn"] = refresh_btn
        window["widgets"]["calc_btn"] = calc_btn
        window["widgets"]["close_btn"] = close_btn

        # Result captions area.
        results_top = buttons_top - 34
        xp.createWidget(
            label_x,
            results_top,
            field_x2,
            results_top - 18,
            1,
            "Results",
            0,
            window["widgetID"],
            xp.WidgetClass_Caption,
        )

        self.result_lines = []
        line_y = results_top - 22
        for idx in range(11):
            line_widget = xp.createWidget(
                label_x,
                line_y,
                field_x2,
                line_y - 16,
                1,
                "",
                0,
                window["widgetID"],
                xp.WidgetClass_Caption,
            )
            self.result_lines.append(line_widget)
            line_y -= 17

        self.widgets = window["widgets"]
        return window

    # ---------------------------
    # UI callbacks
    # ---------------------------

    def _widget_callback(self, inMessage, inWidget, inParam1, inParam2):
        if not self.window:
            return 0

        # Close box in main window.
        if inMessage == xp.Message_CloseButtonPushed and inWidget == self.window["widgetID"]:
            self._destroy_window()
            return 1

        # Push button press event: inParam1 carries clicked widget id.
        if inMessage == xp.Msg_PushButtonPressed:
            if inParam1 == self.widgets.get("refresh_btn"):
                self._refresh_fields_from_sim()
                self._set_results(["Inputs refreshed from available sim datarefs."])
                return 1
            if inParam1 == self.widgets.get("flaps_10"):
                self._set_flaps_selector(10)
                return 1
            if inParam1 == self.widgets.get("flaps_20"):
                self._set_flaps_selector(20)
                return 1
            if inParam1 == self.widgets.get("calc_btn"):
                self._calculate_from_ui()
                return 1
            if inParam1 == self.widgets.get("close_btn"):
                self._destroy_window()
                return 1

        return 0

    # ---------------------------
    # Sim -> UI prefill
    # ---------------------------

    def _refresh_fields_from_sim(self):
        if not self.window:
            return

        # Elevation
        elev_m = self._safe_get_float(self.dr_elevation_m)
        if elev_m is not None:
            self._set_text("elevation_ft", f"{elev_m * FT_PER_M:.0f}")

        # QNH
        qnh_inhg = self._safe_get_float(self.dr_qnh_inhg)
        if qnh_inhg is not None:
            self._set_text("qnh_hpa", f"{qnh_inhg * HPA_PER_INHG:.2f}")

        # OAT
        oat_c = self._safe_get_float(self.dr_oat_c)
        if oat_c is not None:
            self._set_text("oat_c", f"{oat_c:.1f}")

        # Weight
        weight_kg = self._safe_get_float(self.dr_weight_kg)
        if weight_kg is not None:
            self._set_text("weight_t", f"{weight_kg / 1000.0:.1f}")

        # Flap selection heuristic from actual flap deflection.
        flap_deg = self._safe_get_float(self.dr_flap_deg)
        if flap_deg is not None:
            # If using handle ratio fallback, convert to an approximate degree.
            if flap_deg <= 1.0:
                flap_deg *= 30.0
            flap_sel = 20 if flap_deg >= 15.0 else 10
            self._set_flaps_selector(flap_sel)

    # ---------------------------
    # Calculation
    # ---------------------------

    def _calculate_from_ui(self):
        if self.calculate_func is None:
            msg = self.import_error or "Calculator backend not available"
            self._set_results([msg])
            return

        try:
            inputs = self._read_inputs()
        except ValueError as exc:
            self._set_results([f"Input error: {exc}"])
            return

        try:
            res = self.calculate_func(**inputs)
        except Exception as exc:
            self._set_results([f"Calculation error: {exc}"])
            return

        lines = [
            f"PA: {res['PA_ft']} ft | OAT: {res['OAT_C']} C / {res['OAT_F']} F | Flaps: {res['FLAPS']}",
            f"MAX EPR: {res['MAX_EPR']} | CLIMB EPR: {res['CLIMB_EPR']} | REDUCED EPR: {res['REDUCED_EPR']}",
            f"Assumed Temp: {res['ASSUMED_TEMP_C']} C / {res['ASSUMED_TEMP_F']} F",
            f"Thrust Ratio: {res['THRUST_RATIO'] * 100:.0f}%",
            f"Distance Req: {res['DIST_REQUIRED_M']} m ({res['DIST_REQUIRED_FT']} ft)",
            f"Runway Avail: {res['RUNWAY_AVAILABLE_M']} m ({res['RUNWAY_AVAILABLE_FT']} ft)",
            f"Runway Limit Wt: {res['RUNWAY_LIMIT_WEIGHT']}k lbs",
            f"Climb Limit Wt: {res['CLIMB_LIMIT_WEIGHT']}k lbs",
            f"Actual Wt: {res['ACTUAL_WEIGHT_K_LBS']}k lbs | Margin: {res['WEIGHT_MARGIN_K_LBS']}k lbs",
            f"V1/VR/V2: {res['V1']} / {res['VR']} / {res['V2']} kt",
        ]

        if not res["DERATE_ALLOWED"]:
            reasons = "; ".join(res["RESTRICTION_REASONS"]) or "Restrictions apply"
            lines.append(f"Derate NOT allowed: {reasons}")
        else:
            lines.append("Derate allowed under entered conditions")

        self._set_results(lines)

    def _read_inputs(self) -> Dict[str, Any]:
        flaps = 20 if self._is_checked("flaps_20") else 10

        return {
            "elevation_ft": float(self._get_text("elevation_ft")),
            "qnh": float(self._get_text("qnh_hpa")),
            "oat_c": float(self._get_text("oat_c")),
            "weight": float(self._get_text("weight_t")),
            "runway_m": float(self._get_text("runway_m")),
            "flaps": flaps,
            "packs_off_3": self._is_checked("packs_off_3"),
            "runway_dry": self._is_checked("runway_dry"),
            "wind_headwind": float(self._get_text("headwind")),
            "wind_tailwind": float(self._get_text("tailwind")),
            "mel_cdl_penalty": self._is_checked("mel_cdl_penalty"),
            "windshear_prob": self._is_checked("windshear_prob"),
            "runway_slope_pct": float(self._get_text("runway_slope_pct")),
        }

    def _set_flaps_selector(self, flaps: int):
        xp.setWidgetProperty(self.widgets["flaps_10"], xp.Property_ButtonState, 1 if flaps == 10 else 0)
        xp.setWidgetProperty(self.widgets["flaps_20"], xp.Property_ButtonState, 1 if flaps == 20 else 0)

    # ---------------------------
    # Widget utility helpers
    # ---------------------------

    def _get_text(self, key: str) -> str:
        widget_id = self.widgets[key]
        return xp.getWidgetDescriptor(widget_id).strip()

    def _set_text(self, key: str, value: str):
        widget_id = self.widgets[key]
        xp.setWidgetDescriptor(widget_id, value)

    def _is_checked(self, key: str) -> bool:
        widget_id = self.widgets[key]
        return xp.getWidgetProperty(widget_id, xp.Property_ButtonState) == 1

    def _set_results(self, lines):
        if not self.result_lines:
            return

        lines = list(lines)[: len(self.result_lines)]
        while len(lines) < len(self.result_lines):
            lines.append("")

        for widget_id, text in zip(self.result_lines, lines):
            xp.setWidgetDescriptor(widget_id, text)

    @staticmethod
    def _safe_get_float(dataref) -> Optional[float]:
        if not dataref:
            return None
        try:
            value = xp.getDataf(dataref)
            if value is None:
                return None
            return float(value)
        except Exception:
            return None

    @staticmethod
    def _find_first_dataref(candidates):
        for ref_name in candidates:
            ref = xp.findDataRef(ref_name)
            if ref:
                return ref
        return None
