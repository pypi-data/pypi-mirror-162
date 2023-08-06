import ipywidgets as widgets
from IPython.core.display import clear_output
from ipywidgets import interactive, fixed, HBox, Layout, VBox
import pandas as pd
import numpy as np

widget_layout = Layout(align_items='center', width='90px')
box_layout = Layout(display='flex',
                    border='solid 1px',
                    width='720px')
style = {'description_width': '0px'}


class SingleStirrerWidget:
    def __init__(self, device, vial_number):
        self.device = device
        self.vial_number = vial_number
        self.slider = widgets.FloatSlider(0, min=0, max=1, step=0.01,
                                          orientation="vertical",
                                          description="%d" % vial_number,
                                          continuous_update=False,
                                          layout=Layout(width='30px'))
        self.slider.observe(self.handle_slider_change, names="value")
        self.max_button = widgets.Button(description="", icon="fa-blender", layout=Layout(width='40px'),
                                         tooltip="Max speed duty cycle - set this value below 1 if using 5V fans. Maximum speed at which the stirrer can spin stably")
        self.max_button.on_click(self.handle_max_button)
        self.high_button = widgets.Button(description="", icon="fa-fan", layout=Layout(width='40px'),
                                          tooltip="High speed duty cycle - vortex almost reaching bottom of vial")
        self.high_button.on_click(self.handle_high_button)
        self.low_button = widgets.Button(description="", icon="fa-sync-alt", layout=Layout(width='40px'),
                                         tooltip="Low speed duty cycle - little or no vortex")
        self.low_button.on_click(self.handle_low_button)
        self.stop_button = widgets.Button(description="", icon="fa-stop-circle", layout=Layout(width='40px'),
                                          tooltip="STOP stirrer")
        self.stop_button.on_click(self.handle_stop_button)
        self.calibrate = widgets.Checkbox(description="s", layout=Layout(width='40px'), tooltip="set current duty cycle as low/high/max at button press when this box is checked.",
                                          style={"description_width": "initial"})
        self.buttons = widgets.VBox([self.max_button, self.high_button, self.low_button,
                                     self.stop_button, self.calibrate])
        self.widget = HBox([self.slider, self.buttons], layout=Layout(align_items='center', width='85px'))

    def handle_stop_button(self, button):
        self.slider.value = 0

    def handle_max_button(self, button):
        if self.calibrate.value:
            self.device.calibration_fan_speed_to_duty_cycle[self.vial_number][3] = self.slider.value
            self.calibrate.value = False
            self.device.save()
        else:
            self.slider.value = self.device.calibration_fan_speed_to_duty_cycle[self.vial_number][3]

    def handle_high_button(self, button):
        if self.calibrate.value:
            self.device.calibration_fan_speed_to_duty_cycle[self.vial_number][2] = self.slider.value
            self.calibrate.value = False
            self.device.save()
        else:
            self.slider.value = self.device.calibration_fan_speed_to_duty_cycle[self.vial_number][2]

    def handle_low_button(self, button):
        if self.calibrate.value:
            self.device.calibration_fan_speed_to_duty_cycle[self.vial_number][1] = self.slider.value
            self.calibrate.value = False
            self.device.save()
        else:
            self.slider.value = self.device.calibration_fan_speed_to_duty_cycle[self.vial_number][1]

    def handle_slider_change(self, change):
        new_speed = change.new
        self.device.stirrers._set_duty_cycle(vial=self.vial_number, duty_cycle=new_speed)


class StirrerWidgets:
    def __init__(self, device):
        self.device = device

        self.max_all = widgets.Button(description="max RPM", icon="fa-blender")
        self.max_all.on_click(self.handle_all_max_button)

        self.high_all = widgets.Button(description="high RPM", icon="fa-fan")
        self.high_all.on_click(self.handle_all_high_button)

        self.low_all = widgets.Button(description="low RPM", icon="fa-sync-alt")
        self.low_all.on_click(self.handle_all_low_button)

        self.stop_all = widgets.Button(description="STOP stirrers", button_style="danger", icon="fa-stop-circle",
                                       tooltip="guess what this button does")
        self.stop_all.on_click(self.handle_all_stop_button)
        blank_space = widgets.Output(layout=Layout(width="40px"))
        self.set_button = widgets.ToggleButton(description="set", layout=Layout(width="60px",height="30px"), button_style="info",
                                               tooltip="toggle all set ticks", icon="cogs", value=False)
        self.set_button.observe(self.handle_set_button, names="value")
        self.control_all = HBox([self.stop_all, self.low_all, self.high_all, self.max_all, blank_space, self.set_button])
        self.stirrer_widgets = [SingleStirrerWidget(self.device, i) for i in range(1, 8)]
        self.slider_all = widgets.FloatSlider(description="STIRRERS", value=0, min=0, max=1, step=0.01,
                                              orientation="vertical", continuous_update=False)
        self.slider_all.observe(self.handle_master_change)

        self.stirrer_widgets_box = HBox([w.widget for w in self.stirrer_widgets])
        self.sliders = HBox([HBox([self.slider_all, blank_space]), self.stirrer_widgets_box])

        self.max_all.tooltip = self.stirrer_widgets[0].max_button.tooltip
        self.high_all.tooltip = self.stirrer_widgets[0].high_button.tooltip
        self.low_all.tooltip = self.stirrer_widgets[0].low_button.tooltip

        self.widget = VBox([self.sliders, self.control_all], layout=box_layout)

    def reset_master_slider(self):
        self.slider_all.unobserve_all()
        self.slider_all.value = 0
        self.slider_all.observe(self.handle_master_change)

    def handle_set_button(self, button):
        for w in self.stirrer_widgets:
            w.calibrate.value = self.set_button.value

    def handle_master_change(self, b):
        for v in range(7):
            self.stirrer_widgets_box.children[v].children[0].value = self.slider_all.value

    def handle_all_max_button(self, button):
        for w in self.stirrer_widgets:
            #             w.calibrate.value = False
            w.max_button.click()
        self.set_button.value = False
        self.reset_master_slider()

    def handle_all_high_button(self, button):
        for w in self.stirrer_widgets:
            #             w.calibrate.value = False
            w.high_button.click()
        self.set_button.value = False
        self.reset_master_slider()

    def handle_all_low_button(self, button):
        for w in self.stirrer_widgets:
            #             w.calibrate.value = False
            w.low_button.click()
        self.set_button.value = False
        self.reset_master_slider()

    def handle_all_stop_button(self, button):
        for w in self.stirrer_widgets:
            w.stop_button.click()
        self.device.stirrers.set_speed_all(0)
        self.set_button.value = False
        self.reset_master_slider()


class ValveButtons:
    def __init__(self, device, main_gui):
        self.main_gui = main_gui
        self.layout = Layout(align_items='center', width='85px', height="60px")
        self.device = device
        self.valve_buttons = []
        self.open_all = widgets.Button(description="OPEN all", icon="fa-tint", layout=Layout(width="105px"),
                                       tooltip="OPEN all valves")
        self.close_all = widgets.Button(description="CLOSE all", icon="fa-tint-slash", layout=Layout(width="105px"),
                                        tooltip="CLOSE all valves")
        # self.refresh_button = widgets.Button(icon="fa-sync-alt", tooltip="refresh valve states", layout=Layout(width="35px"))
        self.open_all.on_click(self.handle_open_all_button)
        self.close_all.on_click(self.handle_close_all_button)
        # self.refresh_button.on_click(self.refresh)
        for v in range(1, 8):
            button = widgets.ToggleButton(value=self.device.valves.is_open[v], icon="question",
                                          description="valve %d" % v, layout=self.layout, style=style,
                                          tooltip="toggle valve state")
            button.observe(handler=self.handle_valve_button, names=["value", "description"])
            self.valve_buttons += [button]
        self.box_valves = HBox(self.valve_buttons, layout=Layout(display='flex',
                                                                 align_items='stretch',
                                                                 # height='120px',
                                                                 width='670px'))
        self.all_valves = VBox([self.open_all, self.close_all], layout=Layout(display='flex',align_items='stretch',
                                                                                                   # height='120px',
                                                                                                   width='125px'))
        self.widget = HBox([self.all_valves, self.box_valves], layout=box_layout)
        self.update_button_states(0)

    def handle_valve_button(self, change):
        valve = int(change.owner.description[-1])
        is_open = change.owner.value
        self.box_valves.children[valve - 1].icon = "spinner"
        with self.main_gui.status_bar.output:
            if change["name"] == "value":
                if self.device.valves.is_open[valve] != is_open:
                    if self.device.locks_vials[valve].locked():
                        print("ERROR: v%d LOCKED" % valve)
                    else:
                        assert self.device.locks_vials[valve].acquire(timeout=10)
                        try:
                            self.device.valves.set_state(valve=valve, is_open=is_open)
                        finally:
                            self.device.locks_vials[valve].release()
        if self.device.valves.is_open[valve]:
            self.box_valves.children[valve - 1].icon = "tint"
        if self.device.valves.is_open[valve] is False:
            self.box_valves.children[valve - 1].icon = "tint-slash"
        self.update_button_states(0)

    def handle_open_all_button(self, b):
        self.open_all.icon = "fa-spinner"
        for v in range(1, 8):
            if not self.device.valves.is_open[v] is True:
                self.box_valves.children[v - 1].value = True
                if self.box_valves.children[v - 1].value is True:
                    self.box_valves.children[v - 1].unobserve_all()
                    self.box_valves.children[v - 1].value = False
                    self.box_valves.children[v - 1].observe(handler=self.handle_valve_button,
                                                            names=["value", "description"])
                    self.box_valves.children[v - 1].value = True
                else:
                    self.box_valves.children[v - 1].value = True
        self.open_all.icon = "fa-tint"

    def update_button_states(self, b):
        for valve in range(1, 8):
            if self.device.valves.is_open[valve] is not None:
                self.box_valves.children[valve - 1].value = self.device.valves.is_open[valve]
                if self.device.valves.is_open[valve]:
                    self.box_valves.children[valve - 1].icon = "tint"
                if self.device.valves.is_open[valve] is False:
                    self.box_valves.children[valve - 1].icon = "tint-slash"
            else:
                self.box_valves.children[valve - 1].icon = "question"

    def handle_close_all_button(self, b):
        self.close_all.icon = "fa-spinner"
        for v in range(1, 8):
            if not self.device.valves.is_open[v] is False:
                if self.box_valves.children[v - 1].value is False:
                    self.box_valves.children[v - 1].unobserve_all()
                    self.box_valves.children[v - 1].value = True
                    self.box_valves.children[v - 1].observe(handler=self.handle_valve_button,
                                                            names=["value", "description"])
                    self.box_valves.children[v - 1].value = False
                else:
                    self.box_valves.children[v - 1].value = False
        self.close_all.icon = "fa-tint-slash"


# class LaserWidget:
#     def __init__(self, device, main_gui):
#         self.device = device
#         self.laser_widgets = []
#         self.main_gui = main_gui
#
#         self.checkboxes = [widgets.Checkbox(value=False, description="Laser %d" % laser,
#                                             layout=widget_layout, style=style) for laser in range(1, 8)]
#         self.checkbox_to_laser = dict(zip(self.checkboxes, list(range(1, 8))))
#
#         for laser in range(1, 8):
#             self.checkboxes[laser - 1].observe(self.laser_trigger, names="value", type="change")
#         self.widget = HBox(self.checkboxes, layout=box_layout)
#
#     def laser_trigger(self, change):
#         try:
#             checkbox = change.owner
#             vial = self.checkbox_to_laser[checkbox]
#             if change.new is True:
#                 self.device.lasers.switch_on(vial)
#             #                 with self.output:
#             #                     print("turning on %d"%vial)
#             if change.new is False:
#                 self.device.lasers.switch_off(vial)
#         except:
#             with self.main_gui.status_bar.output:
#                 print("LASER %d ERROR" % vial)


class ADCWidget:
    def __init__(self, device):
        self.device = device
        self.adc_widgets = []
        self.outputs = {v: widgets.Output() for v in range(1, 8)}

        for photodiode in range(1, 8):
            button = widgets.Button(description='ADC %d' % photodiode, height="20px", layout=Layout(width='90px'))
            button.on_click(self.make_adc_button_function(photodiode))
            sub_box = VBox([button, self.outputs[photodiode]],
                           layout=Layout(align_items='center', width='110px', height="70px"))
            self.adc_widgets += [sub_box]
        self.widget = HBox(self.adc_widgets, layout=box_layout)

    def make_adc_button_function(self, photodiode):
        def button_function(b):
            with self.outputs[photodiode]:
                self.device.photodiodes.switch_to_vial(vial=photodiode)
                clear_output()
                mv, err = self.device.photodiodes.measure(gain=8, bitrate=16)
                print(mv, "\n±%.7f" % err)
        return button_function


class ODWidget:
    def __init__(self, device):
        self.device = device
        self.measure_all = widgets.Button(description="measure all", icon ="fa-eye", layout=Layout(width='140px', height="30px"))
        self.measure_all.tooltip = "All vials: measure laser signal, background signal and calculate OD if calibration data is available"
        self.measure_all.on_click(self.measure_all_button_action)

        self.measure_buttons = {vial: widgets.Button(description='OD %d' % vial, icon ="fa-eye",
                                                     tooltip = "Vial %d:\nmeasure laser signal, background signal and calculate OD if calibration data is available" % vial,
                                                     layout=Layout(width='80px', height="30px")) for vial in range(1, 8)}
        self.od_outputs = {v: widgets.Output() for v in range(1, 8)}

        for vial in range(1, 8):
            button = self.measure_buttons[vial]
            button.on_click(self.make_od_button_function(vial))

        self.bottom = HBox([VBox([self.measure_buttons[vial], self.od_outputs[vial]],
                       layout=Layout(align_items='center', width='110px', height="120px")) for vial in range(1,8)])
        self.widget = HBox([self.measure_all, self.bottom], layout=box_layout)

    def measure_all_button_action(self, button):
        for b in self.measure_buttons.values():
            b.click()

    def make_od_button_function(self, vial):
        def button_function(b):
            with self.od_outputs[vial]:
                clear_output()
                bg = self.device.od_sensors[vial].measure_background_intensity()[0]
                tr = self.device.od_sensors[vial].measure_transmitted_intensity()[0]
                sig = tr-bg
                print("sig:%4.1fmV\nbg:%3.1fmV" % (tr, bg))
                od = self.device.od_sensors[vial].calibration_function(sig)
                if od is not None:
                    print("OD:%.4f" % od)
                else:
                    print("OD:?")
        return button_function


class SinglePumpWidget:
    names = {1: "Fresh medium", 2: "Drug medium", 4: "Waste bottle"}
    colors = {1: "#FFFFAB", 2: "#FF8F00", 4: "#808080"}

    def __init__(self, pump, main_pump_widget):
        self.pump = pump
        self.main_pump_widget = main_pump_widget
        self.main_gui = main_pump_widget.main_gui
        self.pump_button = widgets.Button(description="Pump %d" % self.pump.pump_number, layout=Layout(width="150px"))
        self.pump_button.on_click(self.handle_pump_button)
        self.volume_bar = widgets.FloatProgress(value=300, min=0, max=5000, orientation="vertical",
                                                layout=Layout(height="140px", width="20px"))
        self.volume_bar.style.bar_color = self.colors[self.pump.pump_number]
        self.volume_text = widgets.FloatText(value=self.pump.stock_volume, description="Stock",
                                             description_tooltip="Stock volume [mL]", layout=Layout(width="120px"),
                                             style={'description_width': '45px', })
        self.conc_text = widgets.FloatText(value=self.pump.stock_volume, description="Conc.",
                                           description_tooltip="Stock drug concentration", layout=Layout(width="120px"),
                                           style={'description_width': '45px', })
        self.volume_text.observe(self.handle_volume_text, names=["value"])
        self.conc_text.observe(self.handle_conc_text, names=["value"])

        layout=Layout(width="180px")
        self.widget = VBox([HBox([self.volume_bar, VBox([self.volume_text, self.conc_text])]), self.pump_button],
                           layout=layout)
        if self.pump.pump_number in [1, 4]:
            self.widget = VBox([HBox([self.volume_bar, VBox([self.volume_text])]), self.pump_button],
                               layout=layout)
        self.update()

    def update(self):
        self.update_volume_bar()
        self.update_volume_conc_text()
        self.update_pump_button()

    def handle_volume_text(self, change):
        try:
            self.pump.stock_volume = change.new
            self.update_volume_bar()
        except:
            self.volume_text.disabled = True
            self.conc_text.disabled = True

    def handle_conc_text(self, change):
        self.pump.stock_concentration = change.new

        if self.pump.pump_number == 2:
            if pd.isnull(change.new):
                green = 128
            else:
                dose = change.new
                maxdose = 30
                dose = min(dose, maxdose)
                green = int((maxdose - dose) / maxdose * 255)

            self.volume_bar.style.bar_color = '#%02x%02x%02x' % (255, green, 64)
        self.update_volume_bar()

    def update_volume_conc_text(self):
        if not pd.isnull(self.pump.stock_volume):
            self.volume_text.disabled = False
            self.conc_text.disabled = False
            self.volume_text.value = self.pump.stock_volume
            self.conc_text.value = self.pump.stock_concentration

        else:
            if pd.isnull(self.pump.device.directory):
                self.volume_text.disabled = True
                self.conc_text.disabled = True
            else:
                self.volume_text.disabled = False
                self.conc_text.disabled = False
                self.volume_text.value = self.pump.stock_volume
                self.conc_text.value = self.pump.stock_concentration

    def update_volume_bar(self):
        vol = self.pump.stock_volume
        if pd.isnull(vol):
            self.volume_bar.value = -1
        else:
            self.volume_bar.value = vol

    def update_pump_button(self):
        if self.main_pump_widget.pumped_rotations.value == self.main_pump_widget.pumped_rotations.options[-1]:
            vol = self.main_pump_widget.pumped_volume.value
            rots = self.pump.calibration_function(mL=vol)
            if pd.isnull(rots):
                self.pump_button.disabled = True
                self.pump_button.tooltip = "Pump not calibrated"
            else:
                if self.pump_button.disabled:
                    self.pump_button.disabled = False
                self.pump_button.tooltip = "pump %.2f mL (%.3f rotations)" % (vol, rots)
        else:
            if self.main_pump_widget.pumped_rotations.value == self.main_pump_widget.pumped_rotations.options[-2]:
                if self.pump.pump_number == 4:
                    self.pump_button.disabled = False
                    self.pump_button.tooltip = "continuous vacuum"
                else:
                    self.pump_button.disabled = True
                    self.pump_button.tooltip = "continuous pumping only allowed for waste pump"
            else:
                rots = float(self.main_pump_widget.pumped_rotations.value.split()[0])
                self.pump_button.tooltip = "pump %s rotations" % (rots)
                if self.pump_button.disabled:
                    self.pump_button.disabled = False

    def handle_pump_button(self, button):
        with self.main_gui.status_bar.output:
            if self.main_pump_widget.pumped_rotations.value not in self.main_pump_widget.pumped_rotations.options[-2:]:
                rots = float(self.main_pump_widget.pumped_rotations.value.split()[0])
            else:
                if self.main_pump_widget.pumped_rotations.value == self.main_pump_widget.pumped_rotations.options[-2]:
                    self.pump.run(speed=0.1)
                    return
                else:
                    vol = self.main_pump_widget.pumped_volume.value
                    rots = self.pump.calibration_function(mL=vol)
            self.pump.move(n_rotations=rots)


class PumpWidget:
    def __init__(self, device, main_gui):
        self.device = device
        self.main_gui = main_gui
        self.pumped_rotations = widgets.RadioButtons(options=['0.05 rotations',
                                                  '0.5 rotations',
                                                  '1   rotation',
                                                  '5   rotations',
                                                  '10  rotations',
                                                  '50  rotations',
                                                  "∞",
                                                  "custom volume"], index=2, layout=Layout(width="150px"))
        self.pumped_volume = widgets.FloatText(description="volume [mL]", step=0.5, layout=Layout(width="140px"))
        self.pumped_volume.observe(self.change_volume)
        self.stop_button = widgets.Button(description="STOP pumps", button_style="danger", icon="fa-tint-slash",
                                          layout=Layout(width="150px"))
        self.stop_button.on_click(self.handle_emergency_stop_button)

        self.pumped_rotations.observe(self.change_volume)
        self.single_pump_widgets = {p: SinglePumpWidget(self.device.pumps[p], self) for p in [1, 2, 4]}
        self.widget = HBox([VBox([self.pumped_rotations, self.pumped_volume]),
                            VBox([HBox([p.widget for p in self.single_pump_widgets.values()]),
                                  self.stop_button])],layout=box_layout)

    def update(self):
        for spw in self.single_pump_widgets.values():
            spw.update()

    def disable_buttons(self, text="Pumping disabled"):
        for p in self.single_pump_widgets.values():
            p.pump_button.disabled = True
            p.pump_button.tooltip = text

    def enable_buttons(self):
        for p in self.single_pump_widgets.values():
            p.pump_button.disabled = False
            p.pump_button.tooltip = "Run pump %d" % p.pump_number

    def change_volume(self, button):
        for p in self.single_pump_widgets.values():
            p.update()

    def handle_emergency_stop_button(self, b):
        self.device.pump1.stop()
        self.device.pump2.stop()
        self.device.pump3.stop()
        self.device.pump4.stop()


# class PumpConfigWidget:
#
#     def __init__(self, device, main_gui):
#         layout = Layout(display='flex', width='170px')
#         style = {'description_width': '90px'}
#         self.device = device
#         self.refresh_button = widgets.Button(icon="fa-sync-alt", layout=Layout(width="40px"))
#         self.refresh_button.on_click(self.handle_refresh_button)
#         self.active_pumps = HBox([widgets.Checkbox(description="MAIN MEDIUM - pump 1", style=style, layout=layout, indent=False),
#                                   widgets.Checkbox(description="MEDIUM 2 - pump 2", style=style, layout=layout, indent=False),
#                                   widgets.Checkbox(description="MEDIUM 3 - pump 3", style=style, layout=layout, indent=False),
#                                   widgets.Checkbox(description="WASTE - pump 4", style=style, layout=layout, indent=False, disabled=True)])
#         stock_volume = [
#             widgets.FloatText(description="volume", description_tooltip="Volume in stock bottle [mL]", style=style,
#                               layout=layout),
#             widgets.FloatText(description="volume", description_tooltip="Volume in stock bottle [mL]", style=style,
#                               layout=layout),
#             widgets.FloatText(description="volume", description_tooltip="Volume in stock bottle [mL]", style=style,
#                               layout=layout),
#             widgets.FloatText(description="volume", description_tooltip="Free volume in waste bottle [mL]", style=style,
#                               layout=layout)]
#
#         self.stock_volume = HBox(stock_volume)
#         stock_concentration = [
#             widgets.FloatText(description="concentration", description_tooltip="", style=style, layout=layout),
#             widgets.FloatText(description="concentration", description_tooltip="medium 2 concentration", style=style,
#                               layout=layout),
#             widgets.FloatText(description="concentration", description_tooltip="medium 3 concentration", style=style,
#                               layout=layout),
#             widgets.FloatText(description="concentration", description_tooltip="", style=style, layout=layout,
#                               disabled=True)]
#         self.stock_concentration = HBox(stock_concentration)
#         self.handle_refresh_button(0)
#
#         self.stock_volume_widget_pump = {self.stock_volume.children[0]: self.device.pump1,
#                                          self.stock_volume.children[1]: self.device.pump2,
#                                          self.stock_volume.children[2]: self.device.pump3,
#                                          self.stock_volume.children[3]: self.device.pump4}
#         self.stock_conc_widget_pump = {self.stock_concentration.children[0]: self.device.pump1,
#                                        self.stock_concentration.children[1]: self.device.pump2,
#                                        self.stock_concentration.children[2]: self.device.pump3,
#                                        self.stock_concentration.children[3]: self.device.pump4}
#
#         if self.device.directory is None:
#             for p in range(4):
#                 self.stock_volume.children[p].disabled = True
#                 self.stock_concentration.children[p].disabled = True
#                 self.active_pumps.children[p].disabled = True
#             self.widget = widgets.Output()
#             with self.widget:
#                 print("Device directory not defined")
#         else:
#             for c in self.stock_volume.children:
#                 c.observe(self.update_stock_volume, names=["value"])
#             for c in self.stock_concentration.children:
#                 c.observe(self.update_stock_concentration, names=["value"])
#
#             for c in self.active_pumps.children:
#                 c.observe(self.handle_active_pumps_checkbox)
#
#             self.update_active_pumps_checkbox()
#             self.widget = VBox([self.refresh_button, self.active_pumps, self.stock_volume, self.stock_concentration])
#
#     def update_stock_volume(self, change):
#         self.stock_volume_widget_pump[change.owner].stock_volume = change.new
#         # self.device.pump1.stock_volume = self.stock_volume.children[0].value
#         # self.device.pump2.stock_volume = self.stock_volume.children[1].value
#         # self.device.pump3.stock_volume = self.stock_volume.children[2].value
#         # self.device.pump4.stock_volume = self.stock_volume.children[3].value
#
#     def update_stock_concentration(self, change):
#         self.stock_conc_widget_pump[change.owner].stock_concentration = change.new
#
#         # self.device.pump1.stock_concentration = self.stock_concentration.children[0].value
#         # self.device.pump2.stock_concentration = self.stock_concentration.children[1].value
#         # self.device.pump3.stock_concentration = self.stock_concentration.children[2].value
#         # self.device.pump4.stock_concentration = self.stock_concentration.children[3].value
#
#     def update_active_pumps_checkbox(self):
#         for p in [1, 2, 3, 4]:
#             if p in self.device.active_pumps:
#                 c = self.active_pumps.children[p - 1]
#                 c.unobserve_all()
#                 c.value = True
#                 c.observe(self.handle_active_pumps_checkbox)
#         self.disable_inactive_pumps()
#
#     def handle_active_pumps_checkbox(self, box):
#         self.device.active_pumps = [p for p in [1, 2, 3, 4] if self.active_pumps.children[p - 1].value]
#         self.disable_inactive_pumps()
#         self.device.save()
#
#     def disable_inactive_pumps(self):
#         for p in range(4):
#             if self.active_pumps.children[p].value:
#                 self.stock_volume.children[p].disabled = False
#                 if p != 3:
#                     self.stock_concentration.children[p].disabled = False
#
#             else:
#                 self.stock_volume.children[p].value = np.nan
#                 self.stock_concentration.children[p].value = np.nan
#                 self.stock_volume.children[p].disabled = True
#                 self.stock_concentration.children[p].disabled = True
#
#     def handle_refresh_button(self, b):
#         for i in range(4):
#             self.active_pumps.children[i].value = bool(i + 1 in self.device.active_pumps)
#
#         self.stock_volume.children[0].value = self.device.pump1.stock_volume
#         self.stock_volume.children[1].value = self.device.pump2.stock_volume
#         self.stock_volume.children[2].value = self.device.pump3.stock_volume
#         self.stock_volume.children[3].value = self.device.pump4.stock_volume
#         self.stock_concentration.children[0].value = self.device.pump1.stock_concentration
#         self.stock_concentration.children[1].value = self.device.pump2.stock_concentration
#         self.stock_concentration.children[2].value = self.device.pump3.stock_concentration
#         self.stock_concentration.children[3].value = self.device.pump4.stock_concentration

# class PumpWidget:
#     def __init__(self, device, main_gui):
#         self.device = device
#         self.main_gui = main_gui
#
#         pump_style = {'description_width': 'initial'}
#         self.rotations_sliders = {
#         pump: widgets.SelectionSlider(options=(0.03, 0.166, 0.33, 0.5, 0.66, 1, 2, 5, 10, 50), orientation="horizontal",
#                                       description="rotations", continuous_update=False,
#                                       style=pump_style, index=3) for pump in range(1, 5)}
#         run_buttons = {pump: widgets.Button(description="RUN pump %d" % pump, icon="fa-gas-pump") for pump in
#                        range(1, 5)}
#         run_buttons[1].on_click(self.run_pump1)
#         run_buttons[2].on_click(self.run_pump2)
#         run_buttons[3].on_click(self.run_pump3)
#         run_buttons[4].on_click(self.run_pump4)
#
#         box_pumps = []
#         for pump in range(1, 5):
#             box_pumps += [HBox([run_buttons[pump], self.rotations_sliders[pump]])]
#
#         emergency_stop = widgets.Button(description="STOP pumps", button_style="danger", icon="fa-tint-slash")
#         continuous_vacuum = widgets.Button(description="continuous vacuum", icon="fa-gas-pump", button_style="warning")
#         continuous_vacuum.on_click(self.handle_continuous_vacuum_button)
#         emergency_stop.on_click(self.handle_emergency_stop_button)
#
#         box_pumps += [HBox([continuous_vacuum, emergency_stop])]
#         box_pumps += [DilutionWidget(self.device).widget]
#         pumps_box_layout = Layout(display='flex',
#                                   flex_flow='column',
#                                   align_items='stretch',
#                                   border='solid 1px',
#                                   width='470px')
#         box_pumps = VBox(box_pumps, layout=pumps_box_layout)
#         self.widget = box_pumps
#
#     def run_pump1(self, b):
#         with self.main_gui.status_bar.output:
#             self.device.pump1.move(n_rotations=self.rotations_sliders[1].value)
#
#     def run_pump2(self, b):
#         with self.main_gui.status_bar.output:
#             self.device.pump2.move(n_rotations=self.rotations_sliders[2].value)
#
#     def run_pump3(self, b):
#         with self.main_gui.status_bar.output:
#             self.device.pump3.move(n_rotations=self.rotations_sliders[3].value)
#
#     def run_pump4(self, b):
#         with self.main_gui.status_bar.output:
#             self.device.pump4.move(n_rotations=self.rotations_sliders[4].value)
#
#     def handle_emergency_stop_button(self, b):
#         self.device.pump1.stop()
#         self.device.pump2.stop()
#         self.device.pump3.stop()
#         self.device.pump4.stop()
#         # self.device.emergency_stop()
#
#     def handle_continuous_vacuum_button(self, b):
#         assert self.device.valves.not_all_closed()
#         self.device.pump4.run(0.1)


class TopWidget:
    def __init__(self, device, main_device_gui):
        self.device = device
        self.main_device_gui = main_device_gui
        self.temp_output = widgets.Output()

        temp_button = widgets.Button(description="Temperature", icon="fa-temperature-low",
                                     tooltip="Display temperature")
        temp_button.on_click(self.temp_measure)
        self.refresh = widgets.Button(icon="fa-sync-alt", tooltip="refresh gui state", button_style="info",layout=Layout(width="35px"))
        self.refresh.on_click(self.handle_refresh_button)
        self.temp = HBox([temp_button, self.temp_output], layout=Layout(height="40px"))
        self.widget = HBox([self.refresh, self.temp])

    def handle_refresh_button(self, b):
        self.main_device_gui.box_valves.update_button_states(0)
        self.main_device_gui.box_pumps.update()

    def temp_measure(self, b):
        with self.temp_output:
            clear_output()
            cold, hot = self.device.thermometers.measure_temperature()
            print("Vials:\t%.2f °C\nBoard:\t%.2f °C" % (cold, hot))


class DeviceControl:
    def __init__(self, device, main_gui):
        self.device = device
        self.main_gui = main_gui
        if self.device is None:
            self.widget = widgets.Output()
            with self.widget:
                print("No device connected.")
        else:
            # self.box_concentrations = PumpWidget(device, self.main_gui)
            self.box_pumps = PumpWidget(device, main_gui=self.main_gui)
            self.box_temps = TopWidget(device=device, main_device_gui=self)

            self.box_stirrers = StirrerWidgets(device)
            # box_lasers = LaserWidget(device, main_gui).widget
            self.box_valves = ValveButtons(self.device, self.main_gui)
            # box_adc = ADCWidget(device).widget
            self.box_od = ODWidget(device)
            self.widget = VBox([self.box_temps.widget,
                                self.box_pumps.widget,
                                self.box_valves.widget,
                                self.box_stirrers.widget,
                                self.box_od.widget], disabled=True)
