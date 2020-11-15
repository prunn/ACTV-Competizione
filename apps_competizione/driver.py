import ac
import acsys
import math
import functools
from .util.classes import Label, Value, Colors, Font
from .configuration import Configuration


class Driver:
    def __init__(self, app, identifier, is_touristenfahrten):
        name = ac.getDriverName(identifier)
        self.identifier = identifier
        self.is_multiplayer = ac.getServerIP() != ''
        self.last_ping=-1
        self.steam_id=None
        self.steam_id_changed=Value(None)
        self.skin_loaded=False
        self.is_touristenfahrten=is_touristenfahrten
        self.rowHeight = Configuration.ui_row_height
        self.race = False
        self.race_start_position = -1
        self.car_number = ""
        self.team_name = ""
        self.car_skin_path = ""
        self.font = Value(0)
        self.theme = Value(-1)
        self.row_height = Value(-1)
        self.hasStartedRace = False
        self.PitWindowStart=-1
        self.inPitFromPitLane = False
        self.isInPitLane = Value(False)
        self.isInPitLaneOld = False
        self.isInPitBox = Value(False)
        self.pit_window_active=False
        str_offset = " "
        self.final_y = 0
        self.ping_y_offset = 0
        self.isDisplayed = False
        self.firstDraw = False
        self.isAlive = Value(False)
        self.movingUp = False
        self.isCurrentVehicule = Value(False)
        self.qual_mode = Value(0)
        self.race_gaps = []
        self.realtime_gaps = [0] * 100
        self.bestLap_sectors = []
        self.bestLap_value = Value(0)
        self.finished = Value(False)
        self.bestLap = 0
        self.compact_mode = False
        self.bestLapServer = 0
        self.fullName = Value(name)
        self.shortName = name
        self.time = Value()
        self.gap = Value()
        self.raceProgress = 0
        self.race_current_sector = Value(0)
        self.race_standings_sector = Value(0)
        self.push_2_pass_status = Value(0)
        self.push_2_pass_left = Value(0)
        self.isInPit = Value(False)
        self.isInPitChanged = Value(False)
        self.completedLaps = Value()
        self.completedLapsChanged = False
        self.last_lap_visible_end = 0
        self.time_highlight_end = 0
        self.position_highlight_end = 0
        self.highlight = Value()
        self.pit_highlight_end = 0
        self.pit_stops_mandatory_done = False
        self.pit_stops_count = 0
        self.last_lap_in_pit = -1
        self.pit_highlight = Value()
        self.position = Value()
        self.position_offset = Value()
        self.carName = ac.getCarName(self.identifier)
        self.car_class_name = Colors.getClassForCar(self.carName)
        self.num_pos = 0
        self.showingFullNames = False
        fontSize = 28
        self.lbl_time = Label(app) \
            .set(w=self.rowHeight * 4.7, h=self.rowHeight,
                 x=self.rowHeight, y=0,
                 opacity=0)

        self.lbl_name = Label(app) \
            .set(w=self.rowHeight * 5, h=self.rowHeight,
                 x=self.rowHeight, y=0,
                 font_size=fontSize,
                 align="left",
                 opacity=0)
        self.lbl_name_txt = Label(app, str_offset + self.format_name_tlc(name)) \
            .set(w=self.rowHeight * 5, h=self.rowHeight,
                 x=self.rowHeight, y=0,
                 font_size=fontSize,
                 align="left",
                 opacity=0)
        self.lbl_position = Label(app) \
            .set(w=self.rowHeight, h=self.rowHeight,
                 x=0, y=0,
                 opacity=0)
        self.lbl_position_txt = Label(app, str(identifier + 1)) \
            .set(w=self.rowHeight, h=self.rowHeight,
                 x=0, y=0,
                 font_size=fontSize,
                 align="center",
                 opacity=0)
        self.lbl_pit_bg = Label(app) \
            .set(w=self.rowHeight * 0.6, h=self.rowHeight - 2,
                 x=self.rowHeight * 6, y=self.final_y + 2,
                 background=Colors.white(),
                 opacity=1)
        self.lbl_pit = Label(app, "P") \
            .set(w=self.rowHeight * 0.6, h=self.rowHeight - 2,
                 x=self.rowHeight * 6, y=self.final_y + 2,
                 font_size=fontSize - 3,
                 align="center",
                 opacity=0)
        self.lbl_tires_bg = Label(app) \
            .set(w=self.rowHeight * 0.6, h=self.rowHeight - 2,
                 x=self.rowHeight * 6, y=self.final_y + 2,
                 opacity=1)
        self.lbl_tires_txt = Label(app, "") \
            .set(w=self.rowHeight * 0.6, h=self.rowHeight - 2,
                 x=self.rowHeight * 6, y=self.final_y + 2,
                 font_size=fontSize - 3,
                 align="center",
                 opacity=0)
        self.lbl_status = Label(app) \
            .set(w=self.rowHeight * 2.8, h=2,
                 x=0, y=self.rowHeight - 2,
                 background=Colors.red(bg=True),
                 opacity=1)
        self.lbl_p2p = Label(app, "0") \
            .set(w=self.rowHeight * 0.55, h=self.rowHeight - 2,
                 x=self.rowHeight * 6, y=self.final_y + 2,
                 font_size=fontSize - 3,
                 align="center",
                 opacity=0)
        self.lbl_p2p.setAnimationSpeed("rgb", 0.08)
        self.lbl_pit.setAnimationSpeed("rgb", 0.08)
        self.lbl_position.setAnimationMode("y", "spring")
        self.lbl_position_txt.setAnimationMode("y", "spring")
        self.lbl_p2p.setAnimationMode("y", "spring")
        self.lbl_pit_bg.setAnimationMode("y", "spring")
        self.lbl_pit.setAnimationMode("y", "spring")
        self.lbl_tires_bg.setAnimationMode("y", "spring")
        self.lbl_tires_txt.setAnimationMode("y", "spring")
        self.lbl_time_txt = Label(app, "+0.000") \
            .set(w=self.rowHeight * 4.7, h=self.rowHeight,
                 x=self.rowHeight, y=0,
                 font_size=fontSize,
                 align="right",
                 opacity=0)
        self.lbl_logo_bg = Label(app) \
            .set(w=self.rowHeight * 2.8, h=2,
                 x=0, y=self.rowHeight - 2,
                 background=Colors.red(bg=True),
                 opacity=Colors.border_opacity())
        self.lbl_logo = Label(app) \
            .set(w=self.rowHeight * 2.8, h=2,
                 x=0, y=self.rowHeight - 2,
                 opacity=0)
        if self.is_multiplayer:
            self.lbl_ping_bg = Label(app) \
                .set(w=self.rowHeight * 2.8, h=2,
                     x=0, y=self.rowHeight - 2,
                     background=Colors.ping_bg(),
                     opacity=Colors.border_opacity())
            self.lbl_ping_status = Label(app) \
                .set(w=self.rowHeight * 2.8, h=0,
                     x=0, y=self.rowHeight - 2,
                     background=Colors.red(bg=True),
                     opacity=Colors.border_opacity())
        self.lbl_number = Label(app) \
            .set(w=self.rowHeight * 2.8, h=2,
                 x=0, y=self.rowHeight - 2,
                 background=Colors.white(bg=True),
                 opacity=Colors.border_opacity())
        self.lbl_number_txt = Label(app, str(identifier + 1)) \
            .set(w=self.rowHeight, h=self.rowHeight,
                 x=0, y=0,
                 font_size=fontSize,
                 align="center",
                 color=Colors.black_txt(),
                 opacity=0)
        self.set_name()
        self.lbl_time_txt.setAnimationSpeed("rgb", 0.08)
        self.lbl_name.setAnimationSpeed("w", 2)
        self.lbl_time.setAnimationSpeed("w", 2)
        self.lbl_name.setAnimationMode("y", "spring")
        self.lbl_name_txt.setAnimationMode("y", "spring")
        self.lbl_time.setAnimationMode("y", "spring")
        self.lbl_time_txt.setAnimationMode("y", "spring")
        self.lbl_logo_bg.setAnimationMode("y", "spring")
        self.lbl_status.setAnimationMode("y", "spring")
        if self.is_multiplayer:
            self.lbl_ping_bg.setAnimationMode("y", "spring")
            self.lbl_ping_status.setAnimationMode("y", "spring")
            self.lbl_ping_status.setAnimationMode("h", "spring")
        self.lbl_logo.setAnimationMode("y", "spring")
        self.lbl_number.setAnimationMode("y", "spring")
        self.lbl_number_txt.setAnimationMode("y", "spring")
        self.redraw_size()

        self.partial_func = functools.partial(self.on_click_func, driver=self.identifier)
        ac.addOnClickedListener(self.lbl_position.label, self.partial_func)
        ac.addOnClickedListener(self.lbl_name.label, self.partial_func)

    @classmethod
    def on_click_func(*args, driver=0):
        ac.focusCar(driver)

    def redraw_size(self):
        # Config
        self.row_height.setValue(Configuration.ui_row_height)
        self.theme.setValue(Colors.general_theme + Colors.theme_red + Colors.theme_green + Colors.theme_blue)
        self.font.setValue(Font.current)
        self.rowHeight = self.row_height.value
        font_size = Font.get_font_size(self.rowHeight + Font.get_font_offset())
        # Colors
        if self.theme.hasChanged():
            self.set_border()
            if self.pit_highlight.value:
                self.lbl_pit.set(color=Colors.tower_pit_highlight_txt(), animated=True, init=True)
            else:
                self.lbl_pit.set(color=Colors.tower_pit_txt(), animated=True, init=True)
            self.lbl_tires_bg.set(background=Colors.tower_tires_bg(), animated=True, init=True)
            self.lbl_tires_txt.set(color=Colors.tower_tires_txt(), animated=True, init=True)
            self.lbl_p2p.set(color=Colors.tower_position_odd_txt(), animated=True, init=True)
            if ((self.race and Configuration.race_mode==8) or (not self.race and Configuration.qual_mode==4)) and self.isCurrentVehicule.value:
                self.lbl_name.set(background=Colors.tower_driver_highlight_odd_bg(), animated=True, init=True)
                self.lbl_name_txt.set(color=Colors.tower_driver_highlight_odd_txt(), animated=True, init=True)
                self.lbl_time.set(background=Colors.tower_time_highlight_odd_bg(), animated=True, init=True)
                self.lbl_time_txt.set(color=Colors.tower_time_highlight_txt(), animated=True, init=True)
                self.lbl_position.set(background=Colors.tower_position_highlight_odd_bg(), animated=True, init=True)
                self.lbl_position_txt.set(color=Colors.tower_position_highlight_odd_txt(), animated=True, init=True)
                self.lbl_logo_bg.set(opacity=Colors.tower_border_default_bg_opacity(), animated=True, init=True)
            else:
                if self.isAlive.value:
                    self.lbl_name.set(background=Colors.tower_driver_odd_bg(), animated=True, init=True)
                    self.lbl_name_txt.set(color=Colors.tower_driver_odd_txt(), animated=True, init=True)
                    if self.isCurrentVehicule.value:
                        self.lbl_position.set(background=Colors.tower_position_highlight_odd_bg(), animated=True, init=True)
                        self.lbl_position_txt.set(color=Colors.tower_position_highlight_odd_txt(), animated=True, init=True)
                    else:
                        self.lbl_position.set(background=Colors.tower_position_odd_bg(), animated=True, init=True)
                        self.lbl_position_txt.set(color=Colors.tower_position_odd_txt(), animated=True, init=True)
                    self.lbl_time.set(background=Colors.tower_time_odd_bg(), animated=True, init=True)
                    self.lbl_time_txt.set(color=Colors.tower_time_odd_txt(), animated=True, init=True)
                    self.lbl_logo_bg.set(opacity=Colors.tower_border_default_bg_opacity(), animated=True, init=True)
                else:
                    self.lbl_name.set(background=Colors.tower_driver_retired_bg(), animated=True, init=True)
                    self.lbl_name_txt.set(color=Colors.tower_driver_retired_txt(), animated=True, init=True)
                    if self.isCurrentVehicule.value:
                        self.lbl_position.set(background=Colors.tower_position_highlight_odd_bg(), animated=True, init=True)
                        self.lbl_position_txt.set(color=Colors.tower_position_highlight_odd_txt(), animated=True, init=True)
                    else:
                        self.lbl_position.set(background=Colors.tower_position_retired_bg(), animated=True, init=True)
                        self.lbl_position_txt.set(color=Colors.tower_position_retired_txt(), animated=True, init=True)
                    self.lbl_time.set(background=Colors.tower_time_retired_bg(), animated=True, init=True)
                    self.lbl_time_txt.set(color=Colors.tower_time_retired_txt(), animated=True, init=True)
                    self.lbl_logo_bg.set(opacity=Colors.tower_border_default_bg_opacity_retired(), animated=True, init=True)
                    #if self.is_multiplayer:
                    #    self.lbl_ping_bg.hide()
                    #    self.lbl_ping_status.hide()

        # Names
        if Configuration.names >= 2:  # First Last
            self.show_full_name()
        else:  # TLC
            self.set_name()

        font_changed = self.font.hasChanged()
        #if self.row_height.hasChanged() or font_changed:
        # Fonts
        if font_changed:
            self.lbl_name_txt.update_font()
            self.lbl_position_txt.update_font()
            self.lbl_number_txt.update_font()
            self.lbl_pit.update_font()
            self.lbl_p2p.update_font()
            self.lbl_tires_txt.update_font()
        # UI
        #self.position.setValue(-1) + border_offset
        x=0
        self.lbl_position.set(w=self.rowHeight - 2, h=self.rowHeight - 2)
        self.lbl_position_txt.set(w=self.rowHeight - 2, h=self.rowHeight,
                              font_size=font_size)
        x+=self.rowHeight - 2
        self.lbl_name.set(w=self.get_name_width(),
                          h=self.rowHeight - 2,
                          x=x)
        self.lbl_name_txt.set(w=self.get_name_width(),
                              h=self.rowHeight,
                              x=x,
                              font_size=font_size)
        x+=self.get_name_width()
        if self.is_multiplayer:
            self.lbl_ping_bg.set(w=self.rowHeight*5/38, h=self.rowHeight - 2,
                                    x=x - self.rowHeight*5/38,
                                    y=self.final_y)
            self.lbl_ping_status.set(w=self.rowHeight*4/38,
                                    x=x - self.rowHeight*5/38,
                                    y=self.final_y + self.ping_y_offset)

        self.lbl_logo_bg.set(w=self.rowHeight - 2, h=self.rowHeight - 2,
                                x=x, y=self.final_y)
        self.lbl_logo.set(w=round((self.rowHeight - 2) *28/38), h=round((self.rowHeight - 2) *28/38),
                                x=x + (self.rowHeight - 2) *5/38,
                                y=self.final_y + (self.rowHeight - 2) *5/38)
        x += self.rowHeight - 2
        self.lbl_number.set(w=self.rowHeight*45/38, h=self.rowHeight - 2,
                                x=x,
                                y=self.final_y)
        self.lbl_number_txt.set(w=self.rowHeight*45/38, h=self.rowHeight - 2,
                                x=x,
                              font_size=font_size)
        x += self.rowHeight*45/38
        self.lbl_status.set(w=self.rowHeight*13/38, h=self.rowHeight - 2,
                                x=x, y=self.final_y)
        self.lbl_p2p.set(w=self.rowHeight*13/38, h=self.rowHeight - 2,
                         x=x,
                         font_size=font_size - self.rowHeight*6/38, animated=True)
        x += self.rowHeight*13/38
        self.lbl_time.set(w=self.get_time_width(),
                          h=self.rowHeight - 2,
                          x=x)
        self.lbl_time_txt.set(w=self.get_time_width() - self.rowHeight*18/38,
                          h=self.rowHeight,
                          x=x,
                          font_size=font_size, animated=True)
        #x += self.get_time_width()
        x = self.get_pit_x()
        self.lbl_pit_bg.set(w=self.rowHeight * 11/38, h=self.rowHeight - 2,
                         x=x - self.rowHeight * 11/38,
                         animated=True)
        self.lbl_pit.set(w=self.rowHeight * 14/38, h=self.rowHeight - 2,
                         x=x - self.rowHeight * 11/38,
                         font_size=font_size - self.rowHeight*8/38, animated=True)
        if self.is_compact_mode():
            x -= self.rowHeight * 11/38
        t = str(ac.getCarTyreCompound(self.identifier))
        if len(t) > 2:
            w = self.rowHeight * 15 / 38 * len(t) * 0.6
        elif len(t) > 1:
            w = self.rowHeight * 22 / 38
        else:
            w = self.rowHeight * 15 / 38
        self.lbl_tires_bg.set(w=w, h=self.rowHeight - 2,
                         x=x,
                         animated=True)
        self.lbl_tires_txt.set(w=w, h=self.rowHeight - 2,
                         x=x,
                         font_size=font_size - self.rowHeight*8/38, animated=True)

        if self.isDisplayed:
            self.final_y = self.num_pos * self.rowHeight
            self.lbl_name.setY(self.final_y, True)
            self.lbl_time.setY(self.final_y, True)
            self.lbl_name_txt.setY(self.final_y + Font.get_font_x_offset(), True)
            self.lbl_time_txt.setY(self.final_y + Font.get_font_x_offset(), True)
            self.lbl_position_txt.setText(str(self.position.value))
            self.lbl_position.setY(self.final_y, True)
            self.lbl_pit_bg.setY(self.final_y, True)
            self.lbl_tires_bg.setY(self.final_y, True)
            self.lbl_position_txt.setY(self.final_y + Font.get_font_x_offset(), True)
            self.lbl_number_txt.setY(self.final_y + Font.get_font_x_offset(), True)
            self.lbl_pit.setY(self.final_y + self.rowHeight*5/38 + Font.get_font_x_offset(), True)
            self.lbl_tires_txt.setY(self.final_y + self.rowHeight*5/38 + Font.get_font_x_offset(), True)
            self.lbl_p2p.setY(self.final_y + self.rowHeight*5/38 + Font.get_font_x_offset(), True)

            self.lbl_logo_bg.setY(self.final_y, True)
            self.lbl_status.setY(self.final_y, True)
            if self.is_multiplayer:
                self.lbl_ping_bg.setY(self.final_y, True)
                self.lbl_ping_status.setY(self.final_y + self.ping_y_offset, True)
            self.lbl_logo.setY(self.final_y + (self.rowHeight - 2) *5/38, True)
            self.lbl_number.setY(self.final_y, True)

    def show(self, needs_tlc=True, race=True, compact=False, realtime_target_laps=-1):
        self.race = race
        self.compact_mode = compact
        #Status
        if self.finished.value:
            self.lbl_status.set(background=Colors.tower_finish(), animated=True, init=True)
            self.lbl_p2p.hide()
        elif self.isAlive.value and not self.isInPit.value and ac.getCarState(self.identifier, acsys.CS.SpeedKMH) < 30 and (not self.race or (self.race and self.hasStartedRace)):
            self.lbl_status.set(background=Colors.status_stopped_ontrack(), animated=True, init=True) # yellow flag on driver
            if self.push_2_pass_left.value > 0:
                self.push_2_pass_status.setValue(-1)
        elif self.race and self.PitWindowStart >= 0 and not self.pit_stops_mandatory_done:
            self.lbl_p2p.setText("1").show()
            self.lbl_status.set(background=Colors.status_pitstop(), animated=True, init=True)
        else:
            # Push 2 Pass
            self.push_2_pass_status.setValue(ac.getCarState(self.identifier, acsys.CS.P2PStatus))
            if self.push_2_pass_status.value > 0:  # OFF = 0
                self.push_2_pass_left.setValue(ac.getCarState(self.identifier, acsys.CS.P2PActivations))
            if self.push_2_pass_status.value > 0 and self.push_2_pass_left.value > 0:
                if self.push_2_pass_status.hasChanged():
                    if self.push_2_pass_status.value == 1:  # COOLING = 1
                        self.lbl_status.set(background=Colors.tower_p2p_cooling(), animated=True, init=True)
                    elif self.push_2_pass_status.value == 2:  # AVAILABLE = 2
                        self.lbl_status.set(background=Colors.status_green(), animated=True, init=True)
                    elif self.push_2_pass_status.value == 3:  # ACTIVE = 3
                        self.lbl_status.set(background=Colors.tower_p2p_active(), animated=True, init=True)
                if self.push_2_pass_left.hasChanged():
                    self.lbl_p2p.setText(str(self.push_2_pass_left.value))
                self.lbl_p2p.show()
            else:
                self.lbl_p2p.hide()
                self.lbl_status.set(background=Colors.status_green(), animated=True, init=True)
        if self.showingFullNames and needs_tlc:
            self.set_name()
        elif not self.showingFullNames and not needs_tlc:
            self.show_full_name()
        if not self.isDisplayed:
            self.lbl_name.set(w=self.get_name_width())
            self.lbl_time.set(w=self.get_time_width())
            self.isDisplayed = True
        self.lbl_name.show()
        self.lbl_name_txt.show()
        self.lbl_status.show()

        if not self.is_compact_mode():
            self.lbl_time.show()
            self.lbl_time_txt.show()
        else:
            self.lbl_time.hide()
            self.lbl_time_txt.hide()

        self.lbl_logo_bg.show()
        if self.is_multiplayer:
            self.lbl_ping_bg.show()
            if not self.isAlive.value:
                self.lbl_ping_status.hide()
            else:
                if self.last_ping < 50:
                    ping_color = Colors.green_bg()
                    ping_height = self.rowHeight*6/38 - 2
                    self.ping_y_offset = self.rowHeight*32/38
                elif self.last_ping < 100:
                    ping_color = Colors.green_bg()
                    ping_height = self.rowHeight*12/38 - 2
                    self.ping_y_offset = self.rowHeight*26/38
                elif self.last_ping < 150:
                    ping_color = Colors.green_bg()
                    ping_height = self.rowHeight*16/38 - 2
                    self.ping_y_offset = self.rowHeight*22/38
                elif self.last_ping < 200:
                    ping_color = Colors.yellow(bg=True)
                    ping_height = self.rowHeight*22/38 - 2
                    self.ping_y_offset = self.rowHeight*16/38
                elif self.last_ping < 250:
                    ping_color = Colors.yellow(bg=True)
                    ping_height = self.rowHeight*22/38 - 2
                    self.ping_y_offset = self.rowHeight*16/38
                elif self.last_ping < 300:
                    ping_color = Colors.red(bg=True)
                    ping_height = self.rowHeight*28/38 - 2
                    self.ping_y_offset = self.rowHeight*10/38
                else:
                    ping_color = Colors.red(bg=True)
                    ping_height = self.rowHeight - 2
                    self.ping_y_offset = 0
                self.lbl_ping_status.set(y=self.final_y + self.ping_y_offset, h=ping_height,background=ping_color,animated=True).show()
        self.lbl_logo.show()
        self.lbl_number.show()

        self.lbl_position.show()
        self.lbl_position_txt.show()
        self.lbl_number_txt.show()
        if not self.isAlive.value and not self.finished.value:
            self.lbl_name_txt.setColor(Colors.tower_driver_retired_txt(), animated=True, init=True)
        elif self.isInPit.value or ac.getCarState(self.identifier, acsys.CS.SpeedKMH) > 30 or self.finished.value or (self.race and not self.hasStartedRace):
            if self.race and self.isCurrentVehicule.value and Configuration.race_mode==8: # and realtime
                self.lbl_name_txt.setColor(Colors.tower_driver_highlight_odd_txt(), animated=True, init=True)
            elif not self.isCurrentVehicule.value and self.race and realtime_target_laps > -1 and self.race_current_sector.value + 50 < realtime_target_laps:
                self.lbl_name_txt.setColor(Colors.tower_driver_blue_txt(), animated=True, init=True)
            elif not self.race and self.last_lap_in_pit==self.completedLaps.value and Configuration.qual_mode==4 and not self.is_touristenfahrten and not self.isInPit.value: # outlap
                self.lbl_name_txt.setColor(Colors.tower_driver_blue_txt(), animated=True, init=True)
            elif not self.isCurrentVehicule.value and self.race and realtime_target_laps > -1 and self.race_current_sector.value - 50 > realtime_target_laps:
                self.lbl_name_txt.setColor(Colors.tower_driver_lap_up_txt(), animated=True, init=True)
            else:
                self.lbl_name_txt.setColor(Colors.tower_driver_odd_txt(), animated=True, init=True)
        else:
            self.lbl_name_txt.setColor(Colors.tower_driver_stopped_txt(), animated=True, init=True)

    def update_pit(self, session_time):
        #if self.isInPit.hasChanged():
        if self.isInPit.value:
            if self.isInPit.hasChanged():
                self.pit_highlight_end = session_time - 5000

            self.lbl_tires_txt.hide()
            self.lbl_tires_bg.hide()
            x=self.get_pit_x()

            self.lbl_pit_bg.set(x=x - self.rowHeight * 11 / 38)
            self.lbl_pit.set(x=x - self.rowHeight * 11 / 38)

            self.lbl_pit.show()
            self.lbl_pit_bg.show()
        else:
            self.lbl_pit.hide()
            self.lbl_pit_bg.hide()
            if Configuration.show_tires:
                t = str(ac.getCarTyreCompound(self.identifier))
                x = self.get_pit_x()
                if self.is_compact_mode():
                    x-=self.rowHeight * 11 / 38
                if len(t) > 2:
                    w = self.rowHeight * 15 / 38 * len(t) * 0.6
                elif len(t) > 1:
                    w = self.rowHeight * 22 / 38
                else:
                    w = self.rowHeight * 15 / 38
                self.lbl_tires_bg.set(x=x,w=w, animated=True)
                self.lbl_tires_txt.set(x=x,w=w, animated=True)
                self.lbl_tires_txt.setText(t).show()
                self.lbl_tires_bg.show()
            else:
                self.lbl_tires_txt.hide()
                self.lbl_tires_bg.hide()

        if session_time == -1:
            self.pit_highlight_end = 0
        self.pit_highlight.setValue(self.pit_highlight_end != 0 and self.pit_highlight_end < session_time)
        if self.pit_highlight.hasChanged():
            if self.pit_highlight.value:
                self.lbl_pit.setColor(Colors.tower_pit_highlight_txt(), init=True)
            else:
                self.lbl_pit.setColor(Colors.tower_pit_txt(), animated=True, init=True)

    def hide(self, reset=False):
        self.lbl_position.hide()
        self.lbl_pit_bg.hide()
        self.lbl_tires_bg.hide()
        self.lbl_tires_txt.hide()
        self.lbl_position_txt.hide()
        self.lbl_number_txt.hide()
        self.lbl_pit.hide()
        self.lbl_p2p.hide()
        self.lbl_name.set(w=self.get_name_width())
        self.lbl_time.hide()
        self.lbl_time_txt.hide()
        self.lbl_logo_bg.hide()
        self.lbl_status.hide()
        if self.is_multiplayer:
            self.lbl_ping_bg.hide()
            self.lbl_ping_status.hide()
        self.lbl_logo.hide()
        self.lbl_number.hide()
        self.lbl_name.hide()
        self.lbl_name_txt.hide()
        self.isDisplayed = False
        if reset:
            self.finished.setValue(False)
            self.isInPit.setValue(False)
            self.isInPitChanged.setValue(False)
            self.firstDraw = False
            self.set_name()
            self.race_current_sector.setValue(0)
            self.race_standings_sector.setValue(0)
            self.race_gaps = []
            self.realtime_gaps = [0] * 100
            self.completedLaps.setValue(0)
            self.completedLapsChanged = False
            self.last_lap_visible_end = 0
            self.time_highlight_end = 0
            self.bestLap = 0
            self.pit_stops_mandatory_done = False
            self.pit_stops_count = 0
            self.bestLapServer = 0
            self.position_highlight_end = 0
            self.inPitFromPitLane = False
            self.pit_window_active=False
            self.hasStartedRace = False
            self.isInPitBox.setValue(False)
            self.push_2_pass_status.setValue(0)
            self.push_2_pass_left.setValue(0)
            self.last_lap_in_pit = -1
            self.raceProgress = 0

    def get_best_lap(self, lap=False):
        if lap:
            self.bestLap = lap
        if self.bestLapServer > 0 and self.bestLap > 0:
            if self.bestLapServer > self.bestLap:
                return self.bestLap
            else:
                return self.bestLapServer
        if self.bestLapServer > 0:
            return self.bestLapServer
        if self.bestLap > 0:
            return self.bestLap
        return 0

    def set_name(self):
        self.showingFullNames = False
        offset = " "
        if Configuration.names == 1:
            self.lbl_name_txt.setText(offset + self.format_name_tlc2(self.fullName.value))
        else:
            self.lbl_name_txt.setText(offset + self.format_name_tlc(self.fullName.value))
        if self.car_number != "" and self.car_number != "0":
            self.lbl_number_txt.setText(str(self.car_number))
        else:
            self.lbl_number_txt.setText(str(self.identifier))
        self.set_border()

    def set_border(self):
        #self.car_class_name = Colors.getClassForCar(self.carName,self.steam_id)
        self.lbl_logo_bg.set(background=Colors.logo_bg(),
                            init=True)
        self.lbl_logo.set(background=Colors.logo_for_car(self.carName,self.car_skin_path),
                            init=True)
        self.lbl_number.set(background=Colors.color_for_car_class(self.car_class_name),
                            init=True)
        self.lbl_number_txt.set(color=Colors.txt_color_for_car_class(self.car_class_name),
                            init=True)

    def show_full_name(self):
        offset = " "
        self.showingFullNames = True
        if Configuration.names == 4:
            self.lbl_name_txt.setText(offset + self.format_first_name(self.fullName.value))
        elif Configuration.names == 3:
            self.lbl_name_txt.setText(offset + self.format_last_name2(self.fullName.value))
        else:
            self.lbl_name_txt.setText(offset + self.format_last_name(self.fullName.value))

    def set_time(self, time, leader, session_time, mode, fastest_driver_sectors=[]):
        self.time.setValue(time)
        self.gap.setValue(time - leader)
        if self.time.hasChanged():
            self.time_highlight_end = session_time - 5000
        self.highlight.setValue(self.time_highlight_end != 0 and self.time_highlight_end < session_time)
        if self.highlight.value:
            if mode == 0 or mode == 2:
                mode = 1
        self.qual_mode.setValue(mode)
        if mode == 2: #----- sector? delta?
            splits = ac.getCurrentSplits(self.identifier)
            sector_time=best_time=pb_time=0
            for i,c in enumerate(splits):
                if c == 0:
                    break
                sector_time+=c
                if len(self.bestLap_sectors) > i:
                    pb_time += self.bestLap_sectors[i]
                if len(fastest_driver_sectors) > i:
                    best_time += fastest_driver_sectors[i]

            display_color = Colors.tower_time_qualification_highlight_txt()
            if self.finished.value:
                display_time = self.format_time(self.time.value)
            elif self.isInPit.value and self.time.value == 0:
                display_time = "--"
                display_color = Colors.tower_time_green_txt()
            elif self.isInPit.value:
                display_time = self.format_time(self.time.value)
            elif self.last_lap_in_pit==self.completedLaps.value and not self.is_touristenfahrten:
                display_time = "Out Lap"
                display_color = Colors.tower_time_green_txt()
            elif best_time > 0 and sector_time > 0:
                #if comparable
                if sector_time < best_time:
                    # Purple
                    display_time = "-" + self.format_time(best_time - sector_time)
                    display_color = Colors.tower_time_best_lap_txt()
                elif pb_time==0 or sector_time < pb_time:
                    # Green
                    display_time = "+" + self.format_time(sector_time - best_time)
                    display_color = Colors.tower_time_green_txt()
                else:
                    # Slow
                    display_time = "+" + self.format_time(sector_time - best_time)
                    display_color = Colors.tower_time_odd_txt()
            elif self.time.value == 0:
                display_time = "--"
                display_color = Colors.tower_time_green_txt()
            elif sector_time == 0:
                display_time = self.format_time(self.time.value)
            else:
                display_time = self.format_time(sector_time)

            self.lbl_time_txt.change_font_if_needed().setText(display_time).setColor(display_color)
        elif self.time.value == 0:
            self.lbl_time_txt.change_font_if_needed().setText("--").setColor(Colors.tower_time_green_txt())
        elif self.position.value == 1 or mode == 1:
            self.lbl_time_txt.change_font_if_needed().setText(self.format_time(self.time.value)).setColor(Colors.tower_time_qualification_highlight_txt())
        else:
            self.lbl_time_txt.change_font_if_needed().setText("+" + self.format_time(self.gap.value)).setColor(Colors.tower_time_odd_txt())

    def set_time_race(self, time, leader, session_time):
        if self.position.value == 1:
            self.lbl_time_txt.change_font_if_needed().setText("Lap " + str(time)).setColor(Colors.tower_time_odd_txt(), animated=True, init=True)
        else:
            self.lbl_time_txt.change_font_if_needed().setText("+" + self.format_time(leader - session_time)).setColor(Colors.tower_time_odd_txt(), animated=True, init=True)

    def set_time_race_battle(self, time, identifier, lap=False, intervals=False, realtime=False):
        if realtime :
            normal_color = Colors.tower_time_green_txt()
            if time > 0:
                normal_color = Colors.tower_time_odd_txt()
        else:
            #if self.isCurrentVehicule.value:
            #    normal_color = Colors.tower_time_highlight_txt()
            #else:
            normal_color = Colors.tower_time_odd_txt()
        if time == "DNF":
            self.lbl_time_txt.change_font_if_needed().setText("DNF").setColor(Colors.tower_time_retired_txt(), animated=True, init=True)
            self.lbl_name.set(background=Colors.tower_driver_retired_bg(), animated=True, init=True)
            self.lbl_name_txt.set(color=Colors.tower_driver_retired_txt(), animated=True, init=True)
            if self.isCurrentVehicule.value:
                self.lbl_position.set(background=Colors.tower_position_highlight_odd_bg(), animated=True, init=True)
                self.lbl_position_txt.set(color=Colors.tower_position_highlight_odd_txt(), animated=True, init=True)
            else:
                self.lbl_position.set(background=Colors.tower_position_retired_bg(), animated=True, init=True)
                self.lbl_position_txt.set(color=Colors.tower_position_retired_txt(), animated=True, init=True)
            self.lbl_time.set(background=Colors.tower_time_retired_bg(), animated=True, init=True)
            self.lbl_logo_bg.set(opacity=Colors.tower_border_default_bg_opacity_retired(), animated=True, init=True)
            self.lbl_number.set(opacity=Colors.tower_border_default_bg_opacity_retired(), animated=True, init=True)
        elif time == "--":
            self.lbl_time_txt.change_font_if_needed().setText("--.-").setColor(Colors.tower_time_green_txt(), animated=True, init=True)
        elif isinstance(time, str) and time.find("UP") >= 0:
            self.lbl_time_txt.change_font_if_needed(1).setText(time.replace("UP", u"\u25B2")).setColor(Colors.tower_time_place_gain_txt(), animated=True, init=True)
            #self.lbl_time_txt.change_font_if_needed(1).setText(u"\u25B2").setColor(Colors.tower_time_place_gain_txt(), animated=True, init=True)
        elif isinstance(time, str) and time.find("DOWN") >= 0:
            self.lbl_time_txt.change_font_if_needed(1).setText(time.replace("DOWN", u"\u25BC")).setColor(Colors.tower_time_place_lost_txt(), animated=True, init=True)
            #self.lbl_time_txt.change_font_if_needed(1).setText(u"\u25BC").setColor(Colors.tower_time_place_lost_txt(), animated=True, init=True)
        elif isinstance(time, str) and time.find("NEUTRAL") >= 0:
            self.lbl_time_txt.change_font_if_needed(1).setText(time.replace("NEUTRAL", u"\u25C0")).setColor(normal_color, animated=True, init=True)
        elif self.identifier == identifier or time == 600000:
            if ((self.race and Configuration.race_mode==8) or (not self.race and Configuration.qual_mode==4)) or time == 600000:# or self.completedLaps.value == 0
                self.lbl_time_txt.change_font_if_needed().setText("--.-").setColor(Colors.tower_time_green_txt(), animated=True, init=True)
            else:
                laps = " Lap"
                if self.completedLaps.value > 1:
                    laps += "s"
                laps = str(self.completedLaps.value) + laps
                self.lbl_time_txt.change_font_if_needed().setText(laps).setColor(Colors.tower_time_last_lap_txt(), animated=True, init=True)
        elif realtime :
            self.lbl_time_txt.change_font_if_needed().setText(self.format_time_realtime(time)).setColor(normal_color, animated=True, init=True)
        elif lap:
            str_time = "+" + str(math.floor(abs(time)))
            if abs(time) >= 2:
                str_time += " Laps"
            else:
                str_time += " Lap"
            self.lbl_time_txt.change_font_if_needed().setText(str_time).setColor(Colors.tower_time_last_lap_txt(), animated=True, init=True)
        elif identifier == -1:
            if (self.race and Configuration.race_mode < 5) or (not self.race and Configuration.qual_mode==4):
                if time <= ac.getCarState(self.identifier, acsys.CS.BestLap):
                    self.lbl_time_txt.change_font_if_needed().setText(self.format_time(time)).setColor(Colors.tower_time_best_lap_txt(), animated=True, init=True)
                else:
                    self.lbl_time_txt.change_font_if_needed().setText(self.format_time(time)).setColor(Colors.tower_time_last_lap_txt(), animated=True, init=True)
            elif Configuration.race_mode == 5:  # pit stops
                stops = " Stop"
                if time > 1:
                    stops += "s"
                stops = str(time) + stops
                self.lbl_time_txt.change_font_if_needed().setText(stops).setColor(Colors.tower_time_last_lap_txt(), animated=True, init=True)
            elif Configuration.race_mode == 6:  # tires
                self.lbl_time_txt.change_font_if_needed().setText(str(time)).setColor(Colors.tower_time_last_lap_txt(), animated=True, init=True)
            else:
                if time > 0:
                    self.lbl_time_txt.change_font_if_needed().setText(self.format_time(time)).setColor(Colors.tower_time_last_lap_txt(), animated=True, init=True)
                else:
                    self.lbl_time_txt.change_font_if_needed().setText("--.-").setColor(normal_color, animated=True, init=True)
        else:
            #if intervals:
            self.lbl_time_txt.change_font_if_needed().setText("+" + self.format_time(time)).setColor(normal_color, animated=True, init=True)
            #else:
            #    self.lbl_time_txt.change_font_if_needed().setText(self.format_time(time)).setColor(normal_color, animated=True, init=True)

    def optimise(self):
        if len(self.race_gaps) > 132:
            del self.race_gaps[0:len(self.race_gaps) - 132]

    def update_mandatory_pitstop(self,pit_window_active):
        self.steam_id_changed.setValue(self.steam_id)
        if self.steam_id_changed.hasChanged():
            self.car_class_name = Colors.getClassForCar(self.carName,self.steam_id)
            self.set_border()
        self.isInPitLane.setValue(bool(ac.isCarInPitline(self.identifier)))
        self.isInPitBox.setValue(bool(ac.isCarInPit(self.identifier)))
        pit_value = self.isInPitLane.value or self.isInPitBox.value or (self.is_touristenfahrten and 0.923 < self.raceProgress < 0.939) # or Nord Tourist 0.923 < position > 0.939
        self.isInPit.setValue(pit_value)
        if self.race:
            self.isInPitChanged.setValue(pit_value)
            if self.isInPitChanged.hasChanged() and pit_value and not self.finished.value:
                self.pit_stops_count += 1
            self.pit_window_active=pit_window_active
            if self.isInPitBox.hasChanged():
                if self.isInPitBox.value:
                    if not self.finished.value:
                        self.last_lap_in_pit = self.completedLaps.value
                    self.inPitFromPitLane = self.isInPitLaneOld
                    if self.pit_window_active and self.inPitFromPitLane:
                        self.pit_stops_mandatory_done = True
                else:
                    self.inPitFromPitLane = False
            self.isInPitLaneOld = self.isInPitLane.value
        elif pit_value and not self.finished.value:
            self.last_lap_in_pit = self.completedLaps.value


    def set_position(self, position, offset, battles, realtime=False):
        self.position.setValue(position)
        self.position_offset.setValue(offset)
        position_changed = self.position.hasChanged()
        if position_changed or self.position_offset.hasChanged() or self.isCurrentVehicule.hasChanged() or self.isAlive.hasChanged():
            if position_changed:
                if self.position.value < self.position.old:
                    self.movingUp = True
                else:
                    self.movingUp = False
                if self.position.old > 0:
                    self.position_highlight_end = True
            # move labels
            if realtime:
                self.num_pos = offset
            else:
                self.num_pos = position - 1 - offset
            self.final_y = self.num_pos * self.rowHeight
            # avoid long slide on first draw
            if not self.firstDraw:
                self.lbl_name.setY(self.final_y)
                self.lbl_name_txt.setY(self.final_y + Font.get_font_x_offset())
                self.lbl_position.setY(self.final_y)
                self.lbl_pit_bg.setY(self.final_y)
                self.lbl_tires_bg.setY(self.final_y)
                self.lbl_position_txt.setY(self.final_y + Font.get_font_x_offset())
                self.lbl_number_txt.setY(self.final_y + Font.get_font_x_offset())
                self.lbl_pit.setY(self.final_y + self.rowHeight*5/38 + Font.get_font_x_offset())
                self.lbl_tires_txt.setY(self.final_y + self.rowHeight*5/38 + Font.get_font_x_offset())
                self.lbl_p2p.setY(self.final_y + self.rowHeight*5/38 + Font.get_font_x_offset())
                self.lbl_time.setY(self.final_y)
                self.lbl_time_txt.setY(self.final_y + Font.get_font_x_offset())

                self.lbl_logo_bg.setY(self.final_y)
                self.lbl_status.setY(self.final_y)
                if self.is_multiplayer:
                    self.lbl_ping_bg.setY(self.final_y)
                    self.lbl_ping_status.setY(self.final_y + self.ping_y_offset)
                self.lbl_logo.setY(self.final_y + (self.rowHeight - 2) *5/38)
                self.lbl_number.setY(self.final_y)
                self.firstDraw = True

            self.lbl_position_txt.setText(str(self.position.value))
            self.lbl_name.setY(self.final_y, True)
            self.lbl_name_txt.setY(self.final_y + Font.get_font_x_offset(), True)
            self.lbl_position.setY(self.final_y, True)
            self.lbl_pit_bg.setY(self.final_y, True)
            self.lbl_tires_bg.setY(self.final_y, True)
            self.lbl_position_txt.setY(self.final_y + Font.get_font_x_offset(), True)
            self.lbl_number_txt.setY(self.final_y + Font.get_font_x_offset(), True)
            self.lbl_pit.setY(self.final_y + Font.get_font_x_offset() + self.rowHeight*5/38, True)  #  + self.rowHeight/10 +3
            self.lbl_tires_txt.setY(self.final_y + Font.get_font_x_offset() + self.rowHeight*5/38, True)  #  + self.rowHeight/10 +3
            self.lbl_p2p.setY(self.final_y + Font.get_font_x_offset() + self.rowHeight*5/38, True)  # + 5

            self.lbl_time.setY(self.final_y, True)
            self.lbl_time_txt.setY(self.final_y + Font.get_font_x_offset(), True)

            self.lbl_logo_bg.setY(self.final_y, True)
            self.lbl_status.setY(self.final_y, True)
            if self.is_multiplayer:
                self.lbl_ping_bg.setY(self.final_y, True)
                self.lbl_ping_status.setY(self.final_y + self.ping_y_offset, True)
            self.lbl_logo.setY(self.final_y + (self.rowHeight - 2) *5/38, True)
            self.lbl_number.setY(self.final_y, True)
            # ------------------- Colors -----------------
            if battles and ((self.race and Configuration.race_mode==8) or (not self.race and Configuration.qual_mode==4)) and self.isCurrentVehicule.value:
                self.lbl_name.set(background=Colors.tower_driver_highlight_odd_bg(), animated=True, init=True)
                self.lbl_name_txt.set(color=Colors.tower_driver_highlight_odd_txt(), animated=True, init=True)
                self.lbl_position.set(background=Colors.tower_position_highlight_odd_bg(), animated=True, init=True)
                self.lbl_position_txt.set(color=Colors.tower_position_highlight_odd_txt(), animated=True, init=True)
                #self.lbl_number_txt.set(color=Colors.black(), animated=True, init=True)
                self.lbl_time.set(background=Colors.tower_time_highlight_odd_bg(), animated=True, init=True)
                #self.lbl_time_txt.set(color=Colors.tower_time_highlight_txt(), animated=True, init=True)
                self.lbl_logo_bg.set(opacity=Colors.tower_border_default_bg_opacity(), animated=True, init=True)
                self.lbl_number.set(opacity=Colors.tower_border_default_bg_opacity(), animated=True, init=True)
            else:
                if self.isAlive.value:
                    self.lbl_name.set(background=Colors.tower_driver_odd_bg(), animated=True, init=True)
                    self.lbl_name_txt.set(color=Colors.tower_driver_odd_txt(), animated=True, init=True)
                    if self.isCurrentVehicule.value:
                        self.lbl_position.set(background=Colors.tower_position_highlight_odd_bg(), animated=True, init=True)
                        self.lbl_position_txt.set(color=Colors.tower_position_highlight_odd_txt(), animated=True, init=True)
                    else:
                        self.lbl_position.set(background=Colors.tower_position_odd_bg(), animated=True, init=True)
                        self.lbl_position_txt.set(color=Colors.tower_position_odd_txt(), animated=True, init=True)
                    self.lbl_time.set(background=Colors.tower_time_odd_bg(), animated=True, init=True)
                    #self.lbl_time_txt.set(color=Colors.tower_time_odd_txt(), animated=True, init=True)
                    self.lbl_logo_bg.set(opacity=Colors.tower_border_default_bg_opacity(), animated=True, init=True)
                    self.lbl_number.set(opacity=Colors.tower_border_default_bg_opacity(), animated=True, init=True)
                else:
                    self.lbl_name.set(background=Colors.tower_driver_retired_bg(), animated=True, init=True)
                    self.lbl_name_txt.set(color=Colors.tower_driver_retired_txt(), animated=True, init=True)
                    if self.isCurrentVehicule.value:
                        self.lbl_position.set(background=Colors.tower_position_highlight_odd_bg(), animated=True, init=True)
                        self.lbl_position_txt.set(color=Colors.tower_position_highlight_odd_txt(), animated=True, init=True)
                    else:
                        self.lbl_position.set(background=Colors.tower_position_retired_bg(), animated=True, init=True)
                        self.lbl_position_txt.set(color=Colors.tower_position_retired_txt(), animated=True, init=True)
                    #self.lbl_number_txt.set(color=Colors.black(), animated=True, init=True)
                    self.lbl_time.set(background=Colors.tower_time_retired_bg(), animated=True, init=True)
                    #self.lbl_time_txt.set(color=Colors.tower_time_retired_txt(), animated=True, init=True)
                    self.lbl_logo_bg.set(opacity=Colors.tower_border_default_bg_opacity_retired(), animated=True, init=True)
                    self.lbl_number.set(opacity=Colors.tower_border_default_bg_opacity_retired(), animated=True, init=True)




        self.fullName.setValue(ac.getDriverName(self.identifier))
        if self.fullName.hasChanged():
            # Reset
            self.set_name()
            self.bestLap = 0
            self.bestLapServer = 0
            '''
            self.finished.setValue(False)
            self.race_current_sector.setValue(0)
            self.race_standings_sector.setValue(0)
            self.race_gaps = []
            self.realtime_gaps = [0] * 100
            self.completedLaps.setValue(0)
            self.completedLapsChanged = False
            self.last_lap_visible_end = 0
            self.time_highlight_end = 0
            self.position_highlight_end = 0
            self.inPitFromPitLane = False
            self.hasStartedRace = False
            self.isInPitBox.setValue(False)
            self.isInPitChanged.setValue(False)
            '''

    def format_name_tlc(self, name):
        space = name.find(" ")
        if space > 0:
            name = name[space:]
        name = name.strip().upper()
        if len(name) > 2:
            return name[:3]
        return name

    def format_name_tlc2(self, name):
        first = ""
        if len(name) > 0:
            first = name[0].upper()
        space = name.find(" ")
        if space > 0:
            name = name[space:]
        name = name.strip().upper()
        if len(name) > 2 and len(first) > 0:
            return first + name[:2]
        if len(name) > 2:
            return name[:3]
        return name

    def format_last_name(self, name):
        space = name.find(" ")
        if space > 0:
            name = name[space:]
        name = name.strip()
        if len(name) > 12:
            return name[:13]
        return name

    def format_last_name2(self, name):
        first = ""
        if len(name) > 0:
            first = name[0].upper()
        space = name.find(" ")
        if space > 0:
            name = first.upper() + "." + name[space:]
        name = name.strip()
        if len(name) > 12:
            return name[:13]
        return name

    def format_first_name(self, name):
        space = name.find(" ")
        if space > 0:
            name = name[:space]
        name = name.strip()
        if len(name) > 12:
            return name[:13]
        return name

    def format_time(self, ms):
        s = ms / 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        # d,h=divmod(h,24)
        d = ms % 1000
        if math.isnan(s) or math.isnan(d) or math.isnan(m) or math.isnan(h):
            return ""
        if h > 0:
            return "{0}:{1}:{2}.{3}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2), str(int(d)).zfill(3))
        elif m > 0:
            return "{0}:{1}.{2}".format(int(m), str(int(s)).zfill(2), str(int(d)).zfill(3))
        else:
            return "{0}.{1}".format(int(s), str(int(d)).zfill(3))

    def format_time_realtime(self, ms):
        prefix = "+"
        if ms < 0:
            prefix = "-"
        ms = abs(ms)
        #time = "+"+str(time)
        s = ms / 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        # d,h=divmod(h,24)
        d = ms % 1000 / 100
        if math.isnan(s) or math.isnan(d) or math.isnan(m) or math.isnan(h):
            return "--.-"
        if h > 0:
            return prefix + "{0}:{1}:{2}.{3}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2), str(int(d)))
        elif m > 0:
            return prefix + "{0}:{1}.{2}".format(int(m), str(int(s)).zfill(2), str(int(d)))
        else:
            return prefix + "{0}.{1}".format(int(s), str(int(d)))

    def is_compact_mode(self):
        if not self.race and Configuration.qual_mode==3:# and not self.highlight.value:
            return True
        if self.race and Configuration.race_mode==7:
            return True
        if self.race and Configuration.race_mode==3 and self.compact_mode:
            return True
        return False

    def get_name_width(self):
        # Name
        if self.showingFullNames:  # Configuration.names >= 2:
            name_width = 170/38
        else:
            name_width = 58 / 38
        return self.rowHeight * name_width

    def get_time_width(self):
        if self.is_compact_mode():
            return 0
        return self.rowHeight * 101/38

    def get_pit_x(self):
        x = (self.rowHeight - 2) * 2 + self.get_name_width() + self.rowHeight * 58 / 38
        if self.is_compact_mode():
            x += self.rowHeight * 11 / 38
        else:
            x += self.get_time_width()
        return x

    def animate(self, session_time_left):
        if session_time_left == -1:
            self.time_highlight_end = 0
        # Anything that needs live changes
        '''
        if self.isDisplayed:
            # Push 2 Pass
            self.push_2_pass_status.setValue(ac.getCarState(self.identifier, acsys.CS.P2PStatus))
            if self.push_2_pass_status.value > 0:  # OFF = 0
                self.push_2_pass_left.setValue(ac.getCarState(self.identifier, acsys.CS.P2PActivations))
                if self.push_2_pass_status.hasChanged():
                    if self.push_2_pass_status.value == 1:  # COOLING = 1
                        self.lbl_status.set(background=Colors.tower_p2p_cooling(), animated=True, init=True)
                    elif self.push_2_pass_status.value == 2:  # AVAILABLE = 2
                        self.lbl_status.set(background=Colors.status_green(), animated=True, init=True)
                    elif self.push_2_pass_status.value == 3:  # ACTIVE = 3
                        self.lbl_status.set(background=Colors.tower_p2p_active(), animated=True, init=True)
                if self.push_2_pass_left.hasChanged():
                    self.lbl_p2p.setText(str(self.push_2_pass_left.value))

            self.highlight.setValue(self.time_highlight_end != 0 and self.time_highlight_end < session_time_left)
            if not self.race and self.isDisplayed:
                if self.highlight.hasChanged():
                    if self.highlight.value or Configuration.qual_mode==1:
                        self.lbl_time_txt.setColor(Colors.tower_time_qualification_highlight_txt(), animated=True, init=True)
                    else:
                        self.lbl_time_txt.setColor(Colors.tower_time_odd_txt(), animated=True, init=True)
                        
                self.lbl_name.set(w=self.get_name_width(), animated=True)
            
        '''
        self.lbl_position.animate()
        self.lbl_pit_bg.animate()
        self.lbl_tires_bg.animate()
        self.lbl_tires_txt.animate()
        self.lbl_position_txt.animate()
        self.lbl_number_txt.animate()
        self.lbl_pit.animate()
        self.lbl_p2p.animate()
        self.lbl_logo_bg.animate()
        self.lbl_status.animate()
        if self.is_multiplayer:
            self.lbl_ping_bg.animate()
            self.lbl_ping_status.animate()
        self.lbl_logo.animate()
        self.lbl_number.animate()
        self.lbl_time.animate()
        self.lbl_time_txt.animate()
        self.lbl_name.animate()
        self.lbl_name_txt.animate()
