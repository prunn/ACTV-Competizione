import ac
import acsys
import ctypes
import math
from .util.classes import Window, Label, Value, POINT, Colors, Font, lapTimeStart, Config
from .configuration import Configuration


class ACInfo:
    # INITIALIZATION
    def __init__(self):
        self.rowHeight = 38
        self.lastLapInvalidated = 0
        self.isLapVisuallyEnded = True
        self.raceStarted = False
        self.cars_count = ac.getCarsCount()
        self.pos = 0
        self.driver_name_width = 0
        self.lbl_position_text = Value("")
        self.currentVehicle = Value(-1)
        self.row_height = Value(-1)
        self.cursor = Value(False)
        self.fastestLap = Value(0)
        self.current_car_class=Value("")
        self.font = Value(0)
        self.theme = Value(-1)
        self.sector_delay = 5000
        self.visible_end = 0
        self.lapCanBeInvalidated = True
        self.fastestLapBorderActive = False
        self.driver_in_pit_active = False
        self.forceViewAlways = False
        self.minLapCount = 1
        self.sectorCount = -1
        self.lapTimesArray = []
        self.driversLap = []
        for i in range(self.cars_count):
            self.lapTimesArray.append(lapTimeStart(0, 0, 0))
            self.driversLap.append(Value(0))
        self.drivers_info = []
        self.drivers_best_sectors = []
        self.standings = None
        self.track_name = ac.getTrackName(0)
        self.track_config = ac.getTrackConfiguration(0)
        if self.track_config == "":
            self.track_config= "main"
        if self.track_name.find("ks_nordschleife") >= 0 and self.track_config.find("touristenfahrten") >= 0:
            self.minLapCount = 0
            self.lastLapInvalidated = -1
        elif self.track_name.find("drag1000") >= 0 or self.track_name.find("drag400") >= 0:
            self.minLapCount = 0
            self.lastLapInvalidated = -1
        self.session = Value(-1)
        self.window = Window(name="ACTV CP Info", width=332, height=self.rowHeight * 2)

        self.lbl_driver_name = Label(self.window.app, "")\
            .set(w=284, h=self.rowHeight,
                 x=0, y=0,
                 opacity=1)
        self.lbl_fastest_lap_bg = Label(self.window.app, "")\
            .set(w=284, h=self.rowHeight,
                 x=0, y=0,
                 opacity=1)
        self.lbl_driver_name_text = Label(self.window.app, "Loading")\
            .set(w=0, h=0,
                 x=0, y=0,
                 font_size=26,
                 align="left",
                 opacity=0)
        self.driver_name_visible = Value()
        self.driver_name_visible_fin = Value(0)
        self.driver_name_text = Value("")
        self.position_visible = Value(0)
        self.timing_text = Value()
        self.race_fastest_lap = Value(0)
        self.race_fastest_lap_driver = Value()
        self.sector_mapping = True
        self.sector_map = []
        self.sector_map_current = Value()

        self.driver_old_fastest_sectors = []
        self.drivers_lap_count = []
        self.drivers_sector = []
        self.drivers_sector_times = []
        self.drivers_sector_times_last_lap = []
        self.drivers_best_lap_sector_times = []
        self.drivers_is_in_pit = []
        for _ in range(self.cars_count):
            self.drivers_lap_count.append(Value(0))
            self.drivers_sector.append(Value(0))
            self.drivers_sector_times.append([])
            self.drivers_sector_times_last_lap.append([])
            self.drivers_best_lap_sector_times.append([])
            self.drivers_is_in_pit.append(Value(0))
        self.last_lap_start = [-1] * self.cars_count
        self.last_sector_start = [-1] * self.cars_count
        self.drivers_last_lap_pit = [0] * self.cars_count
        self.drivers_pit_lane_start_time = [0] * self.cars_count
        self.drivers_pit_stop_start_time = [0] * self.cars_count

        self.timing_visible = Value(0)
        self.lbl_timing = Label(self.window.app)\
            .set(w=284, h=self.rowHeight,
                 x=0, y=0)
        self.lbl_timing_text = Label(self.window.app, "Loading")\
            .set(w=0, h=self.rowHeight,
                 x=0, y=self.rowHeight,
                 opacity=0,
                 font_size=26,
                 align="right")
        self.lbl_team_txt = Label(self.window.app, "Loading")\
            .set(w=284, h=self.rowHeight,
                 x=0, y=self.rowHeight,
                 opacity=0,
                 font_size=26,
                 align="left")
        self.lbl_split = Label(self.window.app, "Fastest Lap")\
            .set(w=0, h=self.rowHeight,
                 x=10, y=self.rowHeight,
                 opacity=0,
                 font_size=26,
                 align="left")
        self.lbl_fastest_split = Label(self.window.app, "Loading")\
            .set(w=0, h=self.rowHeight,
                 x=48, y=self.rowHeight,
                 opacity=0,
                 font_size=26,
                 align="right")
        self.info_position = Label(self.window.app)\
            .set(w=self.rowHeight, h=self.rowHeight,
                 x=0, y=0)
        self.info_position_txt = Label(self.window.app, "0")\
            .set(w=self.rowHeight, h=self.rowHeight,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="center")
        self.info_number = Label(self.window.app)\
            .set(w=0, h=0,
                 x=246, y=0,
                 opacity=1)
        self.lbl_car_class_bg = Label(self.window.app)\
            .set(w=0, h=0,
                 x=246, y=0,
                 opacity=1)
        self.info_number_txt = Label(self.window.app, "1")\
            .set(w=0, h=0,
                 x=0, y=0,
                 font_size=26,
                 opacity=0,
                 align="center")
        self.lbl_car_class_txt = Label(self.window.app, "")\
            .set(w=0, h=0,
                 x=0, y=0,
                 font_size=26,
                 opacity=0,
                 align="center")
        self.lbl_border = Label(self.window.app)\
            .set(w=284, h=2,
                 x=0, y=0, opacity=1)
        self.lbl_logo = Label(self.window.app)\
            .set(w=284, h=2,
                 x=0, y=0, opacity=1)
        self.lbl_sectors_bg = []
        self.lbl_sectors_text = []
        self.lbl_sectors_title_bg = []
        self.lbl_sectors_title_txt = []
        self.lbl_sectors_init = False
        cfg_sectors_map = Config("apps/python/actv_competizione/", "actv_data.ini")
        sectors_map = cfg_sectors_map.get("sectors_map", self.track_name + "_" + self.track_config, "string")
        if sectors_map != -1:
            self.sector_map = list(map(float, sectors_map.split(";")))

        self.load_cfg()
        self.info_position.setAnimationSpeed("o", 0.1)
        self.info_number.setAnimationSpeed("o", 0.1)
        self.lbl_car_class_bg.setAnimationSpeed("o", 0.1)
        self.lbl_split.setAnimationSpeed("a", 0.1)
        self.lbl_fastest_split.setAnimationSpeed("a", 0.1)

    def on_shutdown(self):
        # saving sector map
        section = "sectors_map"
        if len(self.sector_map) > 0:
            cfg = Config("apps/python/actv_competizione/", "actv_data.ini")
            if not cfg.has(section):
                cfg.set(section)
            cfg.set(section, self.track_name + "_" + self.track_config, ';'.join(map(str, self.sector_map)))

    # PUBLIC METHODS
    # ---------------------------------------------------------------------------------------------------------------------------------------------
    def load_cfg(self):
        if Configuration.lapCanBeInvalidated == 1:
            self.lapCanBeInvalidated = True
        else:
            self.lapCanBeInvalidated = False
        if Configuration.forceInfoVisible == 1:
            self.forceViewAlways = True
        else:
            self.forceViewAlways = False
        self.row_height.setValue(Configuration.ui_row_height)
        self.font.setValue(Font.current)
        self.theme.setValue(Colors.general_theme + Colors.theme_red + Colors.theme_green + Colors.theme_blue)
        self.redraw_size()

    def redraw_size(self):
        # Colors
        if self.theme.hasChanged():
            if self.currentVehicle.value >= 0:
                car_name = ac.getCarName(self.currentVehicle.value)
            else:
                car_name = ac.getCarName(0)
            self.lbl_timing.set(background=Colors.info_timing_bg(),animated=True, init=True)
            self.lbl_car_class_bg.set(background=Colors.black(), animated=True, init=True)
            self.info_number_txt.set(color=Colors.info_position_txt(), animated=True, init=True)
            self.lbl_car_class_txt.set(color=Colors.info_position_txt(), animated=True, init=True)
            self.lbl_driver_name.set(background=Colors.info_driver_bg(), animated=True, init=True)
            self.lbl_driver_name_text.set(color=Colors.info_driver_txt(), animated=True, init=True)
            self.lbl_fastest_split.set(color=Colors.info_fastest_time_txt(), animated=True, init=True)
            self.lbl_timing_text.set(color=Colors.info_timing_txt(), animated=True, init=True)
            self.lbl_team_txt.set(color=Colors.info_timing_txt(), animated=True, init=True)
            self.lbl_fastest_lap_bg.set(background=Colors.info_driver_bg(), animated=True, init=True)

            self.lbl_border.set(background=Colors.logo_bg(), animated=True, init=True)
            self.lbl_logo.set(background=Colors.logo_for_car(car_name,self.get_driver_skin(self.currentVehicle.value)), animated=True, init=True)
            self.info_position.set(background=Colors.info_position_bg(), animated=True, init=True)
            self.info_position_txt.set(color=Colors.info_position_txt(), animated=True, init=True)

        if self.row_height.hasChanged() or self.font.hasChanged():
            # Fonts
            font_offset = Font.get_font_offset()
            self.lbl_driver_name_text.update_font()
            self.lbl_split.update_font()
            self.info_position_txt.update_font()
            self.info_number_txt.update_font()
            self.lbl_car_class_txt.update_font()
            # UI
            font_size = Font.get_font_size(self.row_height.value+font_offset)
            self.lbl_driver_name.set(x=self.row_height.value * 140 / 38, h=self.row_height.value * 60 / 38)  #,w=width, animated=True ,
            self.lbl_fastest_lap_bg.set(y=self.row_height.value * 60 / 38,x=self.row_height.value * 60 / 38,h=self.row_height.value)  # w=width,, animated=True
            self.lbl_driver_name_text.set(x=self.row_height.value * 150 / 38,
                                          h=self.row_height.value,
                                          y=Font.get_font_x_offset() + self.row_height.value * 4 / 38,
                                          font_size=font_size - self.row_height.value * 1 / 38, animated=True)
            self.lbl_timing.set(h=self.row_height.value * 60 / 38,y=0, w=self.row_height.value * 166 / 38, animated=True)#w=width,
            self.lbl_timing_text.set(x=self.row_height.value * 150 / 38,
                                     w=self.row_height.value * 130 / 38,
                                     y=Font.get_font_x_offset()  + self.row_height.value * 6 / 38,
                                     font_size=font_size + self.row_height.value * 7 / 38, animated=True)
            self.lbl_team_txt.set(w=0, h=self.row_height.value,
                                     x=self.row_height.value * 150 / 38, y=self.row_height.value * 26/38 + Font.get_font_x_offset(),
                                     font_size=font_size - self.row_height.value * 4 / 38, animated=True)
            self.lbl_split.set(x=self.row_height.value * 70 / 38, y=self.row_height.value * 60 / 38 + Font.get_font_x_offset(),
                               font_size=font_size, animated=True)
            self.lbl_fastest_split.set(x=self.row_height.value * 190 / 38, y=self.row_height.value * 60 / 38 + Font.get_font_x_offset(),
                                       font_size=font_size, animated=True)
            self.info_position.set(w=self.row_height.value * 60 / 38, h=self.row_height.value * 60 / 38, animated=True)
            self.info_position_txt.set(w=self.row_height.value * 60 / 38, h=self.row_height.value * 60 / 38,
                                       font_size=font_size + self.row_height.value * 14 / 38, y=Font.get_font_x_offset() + 2, animated=True)
            self.info_number.set(x=self.row_height.value * 432 / 38,
                                 w=self.row_height.value * 60 / 38,
                                 h=self.row_height.value * 42 / 38, animated=True)
            self.lbl_car_class_bg.set(x=self.row_height.value * 432 / 38, y=self.row_height.value * 42 / 38,
                                 w=self.row_height.value * 60 / 38,
                                 h=self.row_height.value * 18 / 38, animated=True)
            self.info_number_txt.set(x=self.row_height.value * 432 / 38,
                                     w=self.row_height.value * 60 / 38, h=self.row_height.value * 42 / 38,
                                     font_size=font_size + self.row_height.value * 10 / 38, y=Font.get_font_x_offset() - 4, animated=True)
            self.lbl_car_class_txt.set(x=self.row_height.value * 432 / 38,
                                     w=self.row_height.value * 60 / 38, h=self.row_height.value * 60 / 38,
                                     font_size=font_size - self.row_height.value * 7 / 38, y=self.row_height.value * 37 / 38 + Font.get_font_x_offset(), animated=True)

            self.lbl_border.set(w=self.row_height.value * 80 / 38, h=self.row_height.value * 60 / 38, x=self.row_height.value * 60 / 38, animated=True)
            self.lbl_logo.set(w=self.row_height.value * 40 / 38, h=self.row_height.value * 40 / 38, x=self.row_height.value * 80 / 38,
                              y=self.row_height.value * 10 / 38, animated=True)
            self.set_width_and_name()
        self.resize_sector_labels()

    def ini_sector_labels(self, sector_count):
        for i in range(sector_count):
            self.lbl_sectors_bg.append(Label(self.window.app))
            self.lbl_sectors_text.append(Label(self.window.app, "--.-"))
            self.lbl_sectors_title_bg.append(Label(self.window.app))
            self.lbl_sectors_title_txt.append(Label(self.window.app, "S"+str(i+1)))
        self.lbl_sectors_init = True
        self.resize_sector_labels()

    def resize_sector_labels(self):
        if self.lbl_sectors_init:
            for l in self.lbl_sectors_bg:
                l.set(opacity=1)\
                    .set(background=Colors.info_lap_neutral(),
                         animated=True, init=True)\
                    .set(h=self.row_height.value * 48 / 38,
                         y=self.row_height.value * 80 / 38)#60
            for l in self.lbl_sectors_title_bg:
                l.set(opacity=1)\
                    .set(background=Colors.white(),
                         animated=True, init=True)\
                    .set(h=self.row_height.value * 20 / 38,
                         y=self.row_height.value * 60 / 38)
            font_offset = Font.get_font_offset()
            for l in self.lbl_sectors_text:
                l.set(h=self.row_height.value,
                      y=self.row_height.value * 80 / 38 + Font.get_font_x_offset(),
                      font_size=Font.get_font_size(self.row_height.value + font_offset) + 9,
                      color=Colors.white(),
                      opacity=0,
                      align="center",
                      animated=True, init=True)#87
            for l in self.lbl_sectors_title_txt:
                l.set(h=self.row_height.value,
                      y=self.row_height.value * 51 / 38 + Font.get_font_x_offset(),
                      font_size=Font.get_font_size(self.row_height.value + font_offset) + 2,
                      color=Colors.black_txt(),
                      opacity=0,
                      align="center",
                      animated=True, init=True).update_font()

    def set_drivers_info(self, info):
        self.drivers_info = info

    def get_driver_number(self, currentVehicle):
        if currentVehicle >= 0:
            for driver in self.drivers_info:
                if driver['id'] == currentVehicle:  # or fastest...
                    if driver['number'] != "" and driver['number'] != "0":
                        return str(driver['number'])
                    return str(currentVehicle)
        return str(currentVehicle)

    def get_driver_skin(self, currentVehicle):
        if currentVehicle >= 0:
            for driver in self.drivers_info:
                if driver['id'] == currentVehicle:  # or fastest...
                    return str(driver['skin'])
        return ""

    def get_team(self, currentVehicle):
        if currentVehicle >= 0:
            for driver in self.drivers_info:
                if driver['id'] == currentVehicle:  # or fastest...
                    return str(driver['team'])
        return currentVehicle

    def format_name(self, name, max_name_length):
        space = name.find(" ")
        if space > 0:
            if len(name) > max_name_length and space + 1 < len(name):
                first = ""
                if len(name) > 0:
                    first = name[0] + "."
                name = first + name[space + 1:].lstrip()
                if len(name) > max_name_length:
                    return name[:max_name_length + 1]
                return name
            return name[:space].capitalize().lstrip() + name[space:]
        if len(name) > max_name_length:
            return name[:max_name_length+1].lstrip()
        return name.lstrip()

    def format_tire(self, name):
        space = name.find("(")
        if space > 0:
            name = name[:space]
        name = name.strip()
        if len(name) > 16:
            return name[:17]
        return name

    def time_splitting(self, ms, full="no"):
        ms=abs(ms)
        s = ms / 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        # d,h=divmod(h,24)
        if full == "yes":
            d = ms % 1000
            if h > 0:
                return "{0}:{1}:{2}.{3}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2),
                                                str(int(d)).zfill(3))
            elif m > 0:
                return "{0}:{1}.{2}".format(int(m), str(int(s)).zfill(2), str(int(d)).zfill(3))
            else:
                return "{0}.{1}".format(int(s), str(int(d)).zfill(3))
        else:
            d = ms / 100 % 10
            if h > 0:
                return "{0}:{1}:{2}.{3}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2), int(d))
            elif m > 0:
                return "{0}:{1}.{2}".format(int(m), str(int(s)).zfill(2), int(d))
            else:
                return "{0}.{1}".format(int(s), int(d))

    def get_sector(self,sim_info,vehicle):
        if len(self.sector_map):
            i=len(self.sector_map)
            spline=ac.getCarState(vehicle, acsys.CS.NormalizedSplinePosition)
            for s in reversed(self.sector_map):
                i-=1
                if 0 < s < spline:
                    return i
            return 0
        if vehicle == 0:
            return sim_info.graphics.currentSectorIndex

        splits = ac.getCurrentSplits(vehicle)
        i = 0
        sector = 0
        for c in splits:
            i += 1
            if c > 0:
                sector = i
        return sector

    def get_standings_position(self, vehicle):
        # mainly for replay
        standings = []
        for i in range(self.cars_count):
            bl = ac.getCarState(i, acsys.CS.BestLap)
            if bl > 0 and bool(ac.isConnected(vehicle)):
                standings.append((i, bl))
        standings = sorted(standings, key=lambda student: student[1])
        p = [i for i, v in enumerate(standings) if v[0] == vehicle]
        if len(p) > 0:
            return p[0] + 1
        return 0

    def get_race_standings_position(self, identifier):
        if len(self.standings):
            p = [i for i, v in enumerate(self.standings) if v[0] == identifier]
            if len(p) > 0:
                return p[0] + 1
        return ac.getCarRealTimeLeaderboardPosition(identifier) + 1

    def get_race_standings_position_replay(self, vehicle):
        standings = []
        for i in range(self.cars_count):
            bl = ac.getCarState(i, acsys.CS.LapCount) + ac.getCarState(i, acsys.CS.NormalizedSplinePosition)
            if bl > 0:
                standings.append((i, bl))
        standings = sorted(standings, key=lambda student: student[1], reverse=True)
        p = [i for i, v in enumerate(standings) if v[0] == vehicle]
        if len(p) > 0:
            return p[0] + 1
        return 0

    def animate(self):
        self.lbl_driver_name.animate()
        self.lbl_fastest_lap_bg.animate()
        self.lbl_driver_name_text.animate()
        self.lbl_timing.animate()
        self.lbl_timing_text.animate()
        self.lbl_team_txt.animate()
        self.info_position.animate()
        self.info_position_txt.animate()
        self.info_number.animate()
        self.lbl_car_class_bg.animate()
        self.info_number_txt.animate()
        self.lbl_car_class_txt.animate()
        self.lbl_split.animate()
        self.lbl_fastest_split.animate()
        self.lbl_border.animate()
        self.lbl_logo.animate()
        if self.lbl_sectors_init:
            for l in self.lbl_sectors_bg:
                l.animate()
            for l in self.lbl_sectors_text:
                l.animate()
            for l in self.lbl_sectors_title_bg:
                l.animate()
            for l in self.lbl_sectors_title_txt:
                l.animate()

    def reset_visibility(self):
        self.driver_name_visible.setValue(0)
        self.lbl_driver_name.hide()
        self.lbl_fastest_lap_bg.hide()
        self.lbl_driver_name_text.hide()
        self.lbl_border.hide()
        self.driver_name_visible_fin.setValue(0)
        self.lbl_timing.hide()
        self.lbl_timing_text.hide()
        self.lbl_team_txt.hide()
        self.timing_visible.setValue(0)
        self.lbl_fastest_split.hide()
        self.lbl_split.hide()
        self.info_number.hide()
        self.lbl_car_class_bg.hide()
        self.info_number_txt.hide()
        self.lbl_car_class_txt.hide()
        self.info_position.hide()
        self.info_position_txt.hide()
        self.lbl_logo.hide()
        self.visible_end = 0
        self.driver_name_text.setValue("")

    def set_width_and_name(self):
        name = self.format_name(self.driver_name_text.value, 17)
        width = (self.row_height.value * 49 / 36) + Font.get_text_dimensions(name, self.row_height.value)
        if width < self.row_height.value * 7.2:
            width = self.row_height.value * 7.2

        self.driver_name_width = width
        self.lbl_fastest_lap_bg.set(w=width + self.row_height.value * 140 / 38, animated=True)

        self.lbl_timing.set(x=self.driver_name_width + self.row_height.value * 200 / 38, animated=True)
        self.lbl_timing_text.set(x=self.driver_name_width + self.row_height.value * 200 / 38, animated=True)
        self.lbl_fastest_split.set(w=width, animated=True)
        self.lbl_driver_name_text.setText(name)
        self.lbl_driver_name.set(w=self.driver_name_width, animated=True)
        self.info_number.set(x=self.driver_name_width + self.row_height.value * 140 / 38, animated=True)
        self.lbl_car_class_bg.set(x=self.driver_name_width + self.row_height.value * 140 / 38, animated=True)
        self.info_number_txt.set(x=self.driver_name_width + self.row_height.value * 140 / 38, animated=True)
        self.lbl_car_class_txt.set(x=self.driver_name_width + self.row_height.value * 140 / 38, animated=True)
        if self.session.value != 2:
            full_width=width + self.row_height.value * 306 / 38
            if self.lbl_sectors_init and len(self.lbl_sectors_bg):
                width = full_width / len(self.lbl_sectors_bg)
                i = 0
                x = self.row_height.value * 60 / 38
                for l in self.lbl_sectors_bg:
                    l.set(w=width, x=x + width * i, animated=True)
                    i += 1
                i = 0
                for l in self.lbl_sectors_title_bg:
                    l.set(w=width, x=x + width * i, animated=True)
                    i += 1
                i = 0
                for l in self.lbl_sectors_text:
                    l.set(w=width, x=x + width * i, animated=True)
                    i += 1
                i = 0
                for l in self.lbl_sectors_title_txt:
                    l.set(w=width, x=x + width * i, animated=True)
                    i += 1

    def visibility_qualif(self):
        self.lbl_split.hide()
        self.lbl_fastest_split.hide()
        self.lbl_fastest_lap_bg.hide()
        self.driver_name_visible_fin.setValue(self.driver_name_visible.value)
        # if driver name is shown
        if self.driver_name_visible.value == 1:
            self.lbl_driver_name.show()
            self.info_number.show()
            self.lbl_car_class_bg.show()
            self.info_number_txt.show()
            self.lbl_car_class_txt.show()
            self.lbl_border.show()
            self.lbl_logo.show()
            self.lbl_driver_name_text.show()

            if self.driver_name_text.hasChanged():
                self.set_width_and_name()
            font_offset = Font.get_font_offset()
            font_size = Font.get_font_size(self.row_height.value + font_offset)
            # if timing is shown
            if self.timing_visible.value == 1:
                self.lbl_timing.show()
                self.lbl_timing_text.show()
                self.lbl_team_txt.hide()
                self.lbl_driver_name_text.set(y=Font.get_font_x_offset() + self.row_height.value * 2 / 38, font_size=font_size + self.row_height.value * 14 / 38, animated=True)
                if self.timing_text.hasChanged():
                    self.lbl_timing_text.setText(self.timing_text.value)
            else:
                self.lbl_timing.hide()
                self.lbl_timing_text.hide()
                team = self.get_team(self.currentVehicle.value)
                if team != '':
                    self.lbl_team_txt.setText(str(team)).show()
                    self.lbl_driver_name_text.set(y=Font.get_font_x_offset() + self.row_height.value * 4 / 38, font_size=font_size - self.row_height.value * 1 / 38, animated=True)
                else:
                    self.lbl_team_txt.hide()
                    self.lbl_driver_name_text.set(y=Font.get_font_x_offset() + self.row_height.value * 2 / 38, font_size=font_size + self.row_height.value * 14 / 38, animated=True)
        else:
            self.lbl_driver_name.hide()
            self.lbl_driver_name_text.hide()
            self.lbl_border.hide()
            self.lbl_logo.hide()
            self.lbl_team_txt.hide()
            self.lbl_timing.hide()
            self.lbl_timing_text.hide()
            self.info_number.hide()
            self.lbl_car_class_bg.hide()
            self.info_number_txt.hide()
            self.lbl_car_class_txt.hide()
            for l in self.lbl_sectors_bg:
                l.hide()
            for l in self.lbl_sectors_text:
                l.hide()
            for l in self.lbl_sectors_title_bg:
                l.hide()
            for l in self.lbl_sectors_title_txt:
                l.hide()


    def visibility_race(self):
        if self.lbl_sectors_init:
            for l in self.lbl_sectors_bg:
                l.hide()
            for l in self.lbl_sectors_text:
                l.hide()
            for l in self.lbl_sectors_title_bg:
                l.hide()
            for l in self.lbl_sectors_title_txt:
                l.hide()
        self.lbl_timing.hide()
        self.lbl_timing_text.hide()
        font_offset = Font.get_font_offset()
        font_size = Font.get_font_size(self.row_height.value+font_offset)
        self.lbl_driver_name_text.set(y=Font.get_font_x_offset() + self.row_height.value * 4 / 38, font_size=font_size - 1, animated=True)

        if self.driver_name_visible.value == 1:
            # 2 lines, name team
            self.lbl_border.show()
            self.lbl_logo.show()
            if self.fastestLapBorderActive:
                self.lbl_fastest_lap_bg.show()
                self.lbl_split.setText("Fastest Lap").show()
                team = self.get_team(self.race_fastest_lap_driver.value)
                if team != '':
                    self.lbl_driver_name_text.set(y=Font.get_font_x_offset() + self.row_height.value * 4 / 38,
                                                  font_size=font_size - 1, animated=True)
                    self.lbl_team_txt.setText(str(team)).show()
                else:
                    self.lbl_driver_name_text.set(y=Font.get_font_x_offset() + self.row_height.value * 2 / 38,
                                                  font_size=font_size + self.row_height.value * 14 / 38, animated=True)
                    self.lbl_team_txt.hide()
            else:
                if self.driver_in_pit_active:
                    self.lbl_fastest_lap_bg.show()
                    self.lbl_split.setText("Pit Lane").show()
                else:
                    self.lbl_split.hide()
                    self.lbl_fastest_lap_bg.hide()
                team = self.get_team(self.currentVehicle.value)
                if team != '':
                    self.lbl_team_txt.setText(str(team)).show()
                    self.lbl_driver_name_text.set(y=Font.get_font_x_offset() + self.row_height.value * 4 / 38,
                                                  font_size=font_size - 1, animated=True)
                else:
                    self.lbl_driver_name_text.set(y=Font.get_font_x_offset() + self.row_height.value * 2 / 38,
                                                  font_size=font_size + self.row_height.value * 14 / 38, animated=True)
                    self.lbl_team_txt.hide()
            self.lbl_driver_name.show()
            self.lbl_driver_name_text.show()
            self.info_number.show()
            self.lbl_car_class_bg.show()
            self.info_number_txt.show()
            self.lbl_car_class_txt.show()
            self.lbl_border.show()
            self.lbl_logo.show()
            if self.driver_name_text.hasChanged():
                self.set_width_and_name()
        else:
            self.lbl_split.hide()
            self.lbl_driver_name.hide()
            self.lbl_fastest_lap_bg.hide()
            self.lbl_driver_name_text.hide()
            self.lbl_border.hide()
            self.lbl_logo.hide()
            self.info_number.hide()
            self.lbl_car_class_bg.hide()
            self.info_number_txt.hide()
            self.lbl_car_class_txt.hide()
            self.lbl_team_txt.hide()

    def get_driver_best_sector(self, identifier, sector):
        for driver in self.drivers_best_sectors:
            if driver['id'] == identifier:
                if len(driver['sectors']) > sector:
                    return driver['sectors'][sector]
                break
        return 0

    def get_class_id(self, identifier):
        if len(self.standings):
            for s in self.standings:
                if s[0] == identifier:
                    return s[2]
        return Colors.getClassForCar(ac.getCarName(identifier))

    def manage_window(self):
        pt = POINT()
        result = ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        win_x = self.window.getPos().x
        win_y = self.window.getPos().y
        if win_x > 0:
            self.window.last_x = win_x
            self.window.last_y = win_y
        else:
            self.window.setLastPos()
            win_x = self.window.getPos().x
            win_y = self.window.getPos().y
        if result and win_x < pt.x < win_x + self.window.width and win_y < pt.y < win_y + self.window.height:
            self.cursor.setValue(True)
        else:
            self.cursor.setValue(False)

        session_changed = self.session.hasChanged()
        if session_changed:
            self.reset_visibility()
            self.raceStarted = False
            self.driver_old_fastest_sectors = []
            self.drivers_lap_count = []
            self.drivers_sector = []
            self.drivers_sector_times = []
            self.drivers_sector_times_last_lap = []
            self.drivers_best_lap_sector_times = []
            self.drivers_is_in_pit = []
            for _ in range(self.cars_count):
                self.drivers_lap_count.append(Value(0))
                self.drivers_sector.append(Value(0))
                self.drivers_sector_times.append([])
                self.drivers_sector_times_last_lap.append([])
                self.drivers_best_lap_sector_times.append([])
                self.drivers_is_in_pit.append(Value(0))
            self.last_lap_start = [-1] * self.cars_count
            self.last_sector_start = [-1] * self.cars_count
            self.drivers_last_lap_pit = [0] * self.cars_count
            self.drivers_pit_lane_start_time = [0] * self.cars_count
            self.drivers_pit_stop_start_time = [0] * self.cars_count
        if self.cursor.hasChanged() or session_changed:
            if self.cursor.value and self.driver_name_visible.value == 0:
                self.window.setBgOpacity(0.4).border(0)
                self.window.showTitle(True)
            else:
                self.window.setBgOpacity(0).border(0)
                self.window.showTitle(False)

    def on_update(self, sim_info, fl, standings):
        self.standings = standings
        self.session.setValue(sim_info.graphics.session)
        sim_info_status = sim_info.graphics.status
        session_time_left = sim_info.graphics.sessionTimeLeft
        if (sim_info_status != 1 and sim_info_status != 3 and session_time_left != 0 and session_time_left != -1 and session_time_left + 100 < sim_info.graphics.sessionTimeLeft) or sim_info_status == 0:
            self.session.setValue(-1)
            self.session.setValue(sim_info.graphics.session)
        self.manage_window()
        self.animate()
        self.currentVehicle.setValue(ac.getFocusedCar())

        for x in range(self.cars_count):
            c = ac.getCarState(x, acsys.CS.LapCount)
            self.driversLap[x].setValue(c)
            if self.driversLap[x].hasChanged():
                self.lapTimesArray[x].lap = self.driversLap[x].value
                self.lapTimesArray[x].time = session_time_left
            if bool(ac.isCarInPitline(x)) or bool(ac.isCarInPit(x)):
                self.lapTimesArray[x].lastpit = c

        backup_laptime = self.lapTimesArray[self.currentVehicle.value].time - session_time_left
        backup_last_lap_in_pits = self.lapTimesArray[self.currentVehicle.value].lastpit
        current_vehicle_changed = self.currentVehicle.hasChanged()
        self.current_car_class.setValue(self.get_class_id(self.currentVehicle.value))

        if current_vehicle_changed or self.current_car_class.hasChanged() or (self.fastestLapBorderActive and session_time_left < self.visible_end - 2000):
            self.fastestLapBorderActive = False
            if self.currentVehicle.value >= 0:
                car_name = ac.getCarName(self.currentVehicle.value)
            else:
                car_name = ac.getCarName(0)
            self.lbl_logo.setBgColor(Colors.logo_for_car(car_name,self.get_driver_skin(self.currentVehicle.value)))
            self.info_number.set(background=Colors.color_for_car_class(self.current_car_class.value), animated=True)
            self.info_number_txt.setText(self.get_driver_number(self.currentVehicle.value))
            self.info_number_txt.set(color=Colors.txt_color_for_car_class(self.current_car_class.value), animated=True)
            self.lbl_car_class_txt.setText(Colors.car_class_name(self.current_car_class.value))

        if sim_info_status == 2:
            # LIVE
            #mapping sectors
            if self.currentVehicle.value == 0 and self.sector_mapping:
                if len(self.sector_map) < sim_info.static.sectorCount:
                    self.sector_map = []
                    for _ in range(sim_info.static.sectorCount):
                        self.sector_map.append(-1)

                self.sector_map_current.setValue(sim_info.graphics.currentSectorIndex)
                if self.sector_map_current.hasChanged():
                    #ac.console("Sector map:" + str(self.sector_map_current.value) + " - " + str(round(sim_info.graphics.normalizedCarPosition,4)))
                    self.sector_map[self.sector_map_current.value] = round(sim_info.graphics.normalizedCarPosition,3)

                self.sector_mapping=False
                for s in self.sector_map:
                    if s < 0:
                        self.sector_mapping = True

            if self.session.value != 2:
                # NOT RACE
                # qtime
                # check sector/laps changes
                chk_fl=0
                fastest_lap_driver_id=0
                for i in range(self.cars_count):
                    if ac.isConnected(i) > 0:
                        c = ac.getCarState(i, acsys.CS.BestLap)
                        if chk_fl==0 or 0 < c < chk_fl:
                            chk_fl=c
                            fastest_lap_driver_id=i

                        self.drivers_lap_count[i].setValue(ac.getCarState(i, acsys.CS.LapCount))
                        self.drivers_sector[i].setValue(self.get_sector(sim_info,i))
                        if self.drivers_sector[i].hasChanged():
                            #ac.console("sector:" + str(self.drivers_sector[i].value) + " : " + str(self.last_sector_start[i]) + " - " + str(session_time_left) + " = " + str(self.last_sector_start[i] - session_time_left))
                            self.drivers_sector_times[i].append(self.last_sector_start[i] - session_time_left)
                            self.last_sector_start[i] = session_time_left

                        if self.last_lap_start[i] == -1 and not math.isinf(session_time_left) and session_time_left != 0:
                            self.last_lap_start[i] = self.last_sector_start[i] = session_time_left
                        if self.drivers_lap_count[i].hasChanged() and not math.isinf(session_time_left):
                            self.last_lap_start[i] = self.last_sector_start[i] = session_time_left
                            # if PB save delta
                            if ac.getCarState(i, acsys.CS.LastLap) <= ac.getCarState(i, acsys.CS.BestLap):
                                # save fastest lap sectors
                                self.drivers_best_lap_sector_times[i] = self.drivers_sector_times[i]
                            #Reset
                            self.drivers_sector_times_last_lap[i]=self.drivers_sector_times[i]
                            self.drivers_sector_times[i]=[]
                        if ac.isCarInPit(i) or ac.isCarInPitline(i):
                            self.drivers_sector_times_last_lap[i]=self.drivers_sector_times[i]
                            self.drivers_sector_times[i] = []
                            self.drivers_last_lap_pit[i] = self.drivers_lap_count[i].value

                self.fastestLap.setValue(fl)
                is_in_pit = bool(ac.isCarInPitline(self.currentVehicle.value)) or \
                            bool(ac.isCarInPit(self.currentVehicle.value))
                lap_count = ac.getCarState(self.currentVehicle.value, acsys.CS.LapCount)
                cur_lap_time = ac.getCarState(self.currentVehicle.value, acsys.CS.LapTime)
                if cur_lap_time == 0 and backup_laptime > 0 and self.minLapCount > 0:
                    cur_lap_time = backup_laptime

                if self.currentVehicle.value == 0 and sim_info.physics.numberOfTyresOut >= 4 and self.lapCanBeInvalidated:
                    self.lastLapInvalidated = lap_count
                if is_in_pit and self.minLapCount == 0:
                    self.lastLapInvalidated = -1
                if self.sectorCount < 0:
                    self.sectorCount = sim_info.static.sectorCount
                    if not self.lbl_sectors_init:
                        self.ini_sector_labels(self.sectorCount)

                lap_invalidated = bool(self.lastLapInvalidated == lap_count)
                if current_vehicle_changed or self.driver_name_text.value == "":
                    self.driver_name_text.setValue(ac.getDriverName(self.currentVehicle.value))
                # sector_delay = 5000
                # live or info
                #self.last_lap_start[self.currentVehicle.value] - session_time_left < 5000

                if self.drivers_last_lap_pit[self.currentVehicle.value] + self.minLapCount <= self.drivers_lap_count[self.currentVehicle.value].value and (self.currentVehicle.value!=0 or (self.currentVehicle.value==0 and not lap_invalidated)):

                    sector = self.get_sector(sim_info,self.currentVehicle.value)
                    self.driver_name_visible.setValue(1)
                    self.timing_visible.setValue(1)

                    last_lap = ac.getCarState(self.currentVehicle.value, acsys.CS.LastLap)

                    traite = False
                    self.isLapVisuallyEnded = True
                    cur_splits = ac.getCurrentSplits(self.currentVehicle.value)
                    time_split = 0
                    for c in cur_splits:
                        if c > 0:
                            time_split += c

                    # Situation
                    for s in range(0, self.sectorCount):
                        if sector == s + 1 and s + 1 <= self.sectorCount and cur_lap_time - time_split <= self.sector_delay:
                            # SECTOR_X_FINISHED_BEGIN_SECTOR_Y
                            self.isLapVisuallyEnded = False
                            self.timing_text.setValue(self.time_splitting(time_split, "yes"))
                            self.info_position.hide()
                            self.info_position_txt.hide()
                            traite = True
                            break

                    if not traite:
                        if self.lastLapInvalidated != lap_count - 1 and ((self.drivers_last_lap_pit[self.currentVehicle.value] != self.drivers_lap_count[self.currentVehicle.value].value - 1 and sector == 0) or (self.minLapCount == 0)) and cur_lap_time <= self.sector_delay and last_lap > 0:
                            # LAP_FINISHED_BEGIN_NEW_LAP,
                            self.isLapVisuallyEnded = False
                            pos = ac.getCarLeaderboardPosition(self.currentVehicle.value)
                            if pos == -1:
                                pos = self.get_standings_position(self.currentVehicle.value)
                            self.pos = pos
                            self.info_position.set(background=Colors.info_position_bg(), animated=True, init=True)
                            self.info_position_txt.set(color=Colors.info_position_txt(), animated=True, init=True)
                            if pos > 0:
                                self.info_position_txt.setText(str(pos)).show()
                                self.info_position.show()
                            self.timing_text.setValue(self.time_splitting(last_lap, "yes"))

                            # force last sector show
                            sector=self.sectorCount
                        else:
                            # OTHER
                            self.isLapVisuallyEnded = True
                            self.timing_text.setValue(self.time_splitting(cur_lap_time))
                            self.info_position.hide()
                            self.info_position_txt.hide()
                            #keep old best lap sectors for lap en compare
                            if len(self.drivers_best_lap_sector_times[fastest_lap_driver_id]) > 0:
                                self.driver_old_fastest_sectors = self.drivers_best_lap_sector_times[fastest_lap_driver_id]

                    ################################## Sectors ###########################
                    if self.timing_visible.value == 1:
                        i = 0
                        for l in self.lbl_sectors_bg:
                            if i < sector and len(self.drivers_best_lap_sector_times[fastest_lap_driver_id]) > i:
                                driver_best_sector=driver_current_lap_sector=-1
                                best_split = self.drivers_best_lap_sector_times[fastest_lap_driver_id][i]
                                if sector == self.sectorCount:
                                    #ac.console("----------test--- last")
                                    if len(self.drivers_sector_times_last_lap[self.currentVehicle.value]) > i:
                                        driver_current_lap_sector = self.drivers_sector_times_last_lap[self.currentVehicle.value][i]
                                else:
                                    if len(self.drivers_sector_times[self.currentVehicle.value]) > i:
                                        driver_current_lap_sector = self.drivers_sector_times[self.currentVehicle.value][i]
                                #driver_best_sector = self.get_driver_best_sector(self.currentVehicle.value, i) and len(self.drivers_best_lap_sector_times[fastest_lap_driver_id]) > i

                                if len(self.drivers_best_lap_sector_times[self.currentVehicle.value]) > i:
                                    driver_best_sector = self.drivers_best_lap_sector_times[self.currentVehicle.value][i]
                                #ac.console("B:" + str(best_split) + " PB:" + str(driver_best_sector) + " Cur:" + str(driver_current_lap_sector))

                                if best_split >= driver_current_lap_sector:
                                    #old fastest lap
                                    if sector == self.sectorCount and len(self.driver_old_fastest_sectors) > i:
                                        best_split = self.driver_old_fastest_sectors[i]
                                    l.set(background=Colors.info_split_best_bg(), animated=True)
                                    self.lbl_sectors_text[i].setText("-" + self.time_splitting(best_split - driver_current_lap_sector, "yes"))
                                elif driver_best_sector > 0 and driver_best_sector >= driver_current_lap_sector:
                                    l.set(background=Colors.info_split_personal_bg(), animated=True)
                                    self.lbl_sectors_text[i].setText("+" + self.time_splitting(driver_current_lap_sector - best_split, "yes"))
                                else:
                                    l.set(background=Colors.info_split_slow_bg(), animated=True)
                                    self.lbl_sectors_text[i].setText("+" + self.time_splitting(driver_current_lap_sector - best_split, "yes"))

                                l.show()
                                self.lbl_sectors_text[i].show()
                                self.lbl_sectors_title_txt[i].show()
                                self.lbl_sectors_title_bg[i].show()
                            else:
                                l.hide()
                                self.lbl_sectors_text[i].hide()
                                self.lbl_sectors_title_txt[i].hide()
                                self.lbl_sectors_title_bg[i].hide()
                            i += 1



                    self.fastestLap.changed = False
                else:
                    bestlap = ac.getCarState(self.currentVehicle.value, acsys.CS.BestLap)
                    for l in self.lbl_sectors_bg:
                        l.hide()
                    for l in self.lbl_sectors_text:
                        l.hide()
                    for l in self.lbl_sectors_title_bg:
                        l.hide()
                    for l in self.lbl_sectors_title_txt:
                        l.hide()
                    self.isLapVisuallyEnded = True
                    spline_position = ac.getCarState(self.currentVehicle.value, acsys.CS.NormalizedSplinePosition)
                    if spline_position <= 0.001:
                        spline_position = 1
                    if session_time_left > 0 and self.minLapCount == 1 and spline_position > 0.95 and not is_in_pit:
                        self.driver_name_visible.setValue(1)
                        self.timing_visible.setValue(1)
                        self.info_position.hide()
                        self.info_position_txt.hide()
                        self.timing_text.setValue("0.0")
                    elif (self.currentVehicle.value != 0 or (self.currentVehicle.value==0 and not lap_invalidated)) and self.drivers_last_lap_pit[self.currentVehicle.value] < self.drivers_lap_count[self.currentVehicle.value].value and self.minLapCount > 0:
                        self.driver_name_visible.setValue(Configuration.forceInfoVisible)
                        self.timing_visible.setValue(0)
                        self.info_position.hide()
                        self.info_position_txt.hide()
                    elif bestlap > 0:
                        if Configuration.forceInfoVisible == 1:
                            self.driver_name_visible.setValue(1)
                            self.timing_visible.setValue(1)
                            self.timing_text.setValue(self.time_splitting(bestlap, "yes"))
                            pos = ac.getCarLeaderboardPosition(self.currentVehicle.value)
                            if pos == -1:
                                pos = self.get_standings_position(self.currentVehicle.value)
                            self.pos = pos
                            self.info_position.set(background=Colors.info_position_bg(), animated=True, init=True)
                            self.info_position_txt.set(color=Colors.info_position_txt(), animated=True, init=True)

                            self.info_position.show()
                            self.info_position_txt.setText(str(pos)).show()
                            self.lbl_position_text.setValue(str(pos))
                        else:
                            self.driver_name_visible.setValue(0)
                            self.timing_visible.setValue(0)
                            self.info_position.hide()
                            self.info_position_txt.hide()
                    elif is_in_pit:
                        self.driver_name_visible.setValue(Configuration.forceInfoVisible)
                        self.timing_visible.setValue(0)
                        self.info_position.hide()
                        self.info_position_txt.hide()
                    else:
                        self.driver_name_visible.setValue(Configuration.forceInfoVisible)
                        self.timing_visible.setValue(0)
                        self.info_position.hide()
                        self.info_position_txt.hide()
                if cur_lap_time <= self.sector_delay and ac.getCarState(self.currentVehicle.value, acsys.CS.LastLap) > 0 and backup_last_lap_in_pits + 1 < ac.getCarState(self.currentVehicle.value, acsys.CS.LapCount) and session_time_left < 0:
                    self.driver_name_visible.setValue(1)
                    self.timing_visible.setValue(1)
                    #self.lbl_split.show()
                    self.info_position.show()
                    self.info_position_txt.show()
                self.visibility_qualif()

            else:
                # ------------- Race -------------
                # fastest lap
                completed = 0
                for x in range(self.cars_count):
                    pit_lane = bool(ac.isCarInPitline(x))
                    pit_box = bool(ac.isCarInPit(x))
                    self.drivers_is_in_pit[x].setValue(pit_lane or pit_box)
                    if self.drivers_is_in_pit[x].hasChanged():
                        if self.drivers_is_in_pit[x].value:
                            self.drivers_pit_lane_start_time[x] = session_time_left

                    c = ac.getCarState(x, acsys.CS.LapCount)
                    if c > completed:
                        completed = c
                if completed <= 1:
                    self.race_fastest_lap.setValue(0)
                else:
                    for i in range(self.cars_count):
                        bl = ac.getCarState(i, acsys.CS.BestLap)
                        l = ac.getCarState(i, acsys.CS.LapCount)
                        if bl > 0 and l > self.minLapCount and (self.race_fastest_lap.value == 0 or bl < self.race_fastest_lap.value):
                            self.race_fastest_lap.setValue(bl)
                            self.race_fastest_lap_driver.setValue(i)

                is_in_pit = self.drivers_is_in_pit[self.currentVehicle.value].value
                if self.race_fastest_lap.hasChanged() and self.race_fastest_lap.value > 0 and not is_in_pit:
                    self.fastestLapBorderActive = True
                    self.lbl_split.setText("Fastest Lap")
                    car_name = ac.getCarName(self.race_fastest_lap_driver.value)
                    self.lbl_logo.setBgColor(Colors.logo_for_car(car_name,self.get_driver_skin(self.race_fastest_lap_driver.value)))
                    self.visible_end = session_time_left - 10000
                    self.driver_name_visible.setValue(1)
                    self.driver_name_text.setValue(ac.getDriverName(self.race_fastest_lap_driver.value))
                    self.info_position.hide()
                    self.info_position_txt.hide()
                    self.lbl_fastest_split.setText(self.time_splitting(self.race_fastest_lap.value, "yes")).show()
                    class_id = self.get_class_id(self.race_fastest_lap_driver.value)
                    self.info_number.set(background=Colors.color_for_car_class(class_id))
                    self.info_number_txt.setText(self.get_driver_number(self.race_fastest_lap_driver.value))
                    self.info_number_txt.set(color=Colors.txt_color_for_car_class(class_id), animated=True)
                    self.lbl_car_class_txt.setText(Colors.car_class_name(class_id))

                elif current_vehicle_changed or (self.forceViewAlways and not self.fastestLapBorderActive) or is_in_pit:
                    # driver info
                    if is_in_pit:
                        self.driver_in_pit_active = True
                        self.lbl_split.setText("Pit Lane")
                        pit_lane_time = self.drivers_pit_lane_start_time[self.currentVehicle.value] - session_time_left
                        self.lbl_fastest_split.setText(self.time_splitting(pit_lane_time)).show()
                    elif session_time_left < self.visible_end:
                        self.lbl_fastest_split.hide()

                    if not self.forceViewAlways or is_in_pit:
                        self.visible_end = session_time_left - 8000
                    self.driver_name_visible.setValue(1)
                    self.driver_name_text.setValue(ac.getDriverName(self.currentVehicle.value))

                    if not self.raceStarted:
                        if sim_info.graphics.completedLaps > 0 or sim_info.graphics.iCurrentTime > 20000:
                            self.raceStarted = True
                        # Generate standings from -0.5 to 0.5 for the start of race
                        standings = []
                        for i in range(self.cars_count):
                            bl = ac.getCarState(i, acsys.CS.LapCount) + ac.getCarState(i,acsys.CS.NormalizedSplinePosition)
                            if bl < 0.5:
                                bl += 0.5  # 0.1 = 0.6
                            elif 0.5 <= bl < 1:
                                bl -= 0.5  # 0.9 = 0.4
                            standings.append((i, bl))
                        standings = sorted(standings, key=lambda student: student[1], reverse=True)
                        p = [i for i, v in enumerate(standings) if v[0] == self.currentVehicle.value]
                        if len(p) > 0:
                            pos = p[0] + 1
                        else:
                            pos = ac.getCarRealTimeLeaderboardPosition(self.currentVehicle.value) + 1
                    else:
                        if sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0:
                            self.raceStarted = False
                        pos = self.get_race_standings_position(self.currentVehicle.value)
                    self.pos = pos
                    self.info_position.set(background=Colors.info_position_bg(), animated=True, init=True)
                    self.info_position_txt.set(color=Colors.info_position_txt(), animated=True, init=True)
                    self.info_position.show()
                    self.info_position_txt.setText(str(pos)).show()
                    self.timing_visible.setValue(0)
                elif self.visible_end == 0 or session_time_left < self.visible_end or (sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0):
                    self.driver_name_visible.setValue(0)
                    self.info_position.hide()
                    self.info_position_txt.hide()
                    self.timing_visible.setValue(0)
                    self.lbl_fastest_split.hide()
                if session_time_left < self.visible_end:
                    self.driver_in_pit_active = False
                self.visibility_race()
        elif sim_info_status == 1 and self.session.value != 2:
            # Replay Qualif
            lap_count = ac.getCarState(self.currentVehicle.value, acsys.CS.LapCount)
            cur_lap_time = ac.getCarState(self.currentVehicle.value, acsys.CS.LapTime)
            is_in_pit = (bool(ac.isCarInPitline(self.currentVehicle.value)) or bool(ac.isCarInPit(self.currentVehicle.value)))
            if current_vehicle_changed or self.driver_name_text.value == "":
                self.driver_name_text.setValue(ac.getDriverName(self.currentVehicle.value))
            if is_in_pit:
                self.driver_name_visible.setValue(0)
                self.timing_visible.setValue(0)
                self.info_position.hide()
                self.info_position_txt.hide()
            elif cur_lap_time <= self.sector_delay and lap_count > 1:
                # show last lap
                self.driver_name_visible.setValue(1)
                self.timing_visible.setValue(1)
                if self.currentVehicle.value == 0:
                    last_lap = sim_info.graphics.iLastTime
                else:
                    last_lap = 0
                    last_splits = ac.getLastSplits(self.currentVehicle.value)
                    for c in last_splits:
                        last_lap += c
                    if last_lap == 0:
                        last_lap = ac.getCarState(self.currentVehicle.value, acsys.CS.LastLap)
                pos = ac.getCarLeaderboardPosition(self.currentVehicle.value)
                if pos == -1:
                    pos = self.get_standings_position(self.currentVehicle.value)
                self.pos = pos
                self.info_position.set(background=Colors.info_position_bg(), animated=True, init=True)
                self.info_position_txt.set(color=Colors.info_position_txt(), animated=True, init=True)
                self.info_position_txt.setText(str(pos)).show()
                self.info_position.show()
                self.timing_text.setValue(self.time_splitting(last_lap, "yes"))
                self.fastestLap.changed = False
            elif lap_count > self.minLapCount:
                # showTiming
                self.driver_name_visible.setValue(1)
                self.timing_visible.setValue(1)
                self.timing_text.setValue(self.time_splitting(cur_lap_time))
                self.info_position.hide()
                self.info_position_txt.hide()
            else:
                # showTireInfo
                self.driver_name_visible.setValue(1)
                self.timing_visible.setValue(0)
                self.info_position.hide()
                self.info_position_txt.hide()
            self.visibility_qualif()
        elif sim_info_status == 1 and self.session.value == 2:
            # Replay Race
            if current_vehicle_changed or (self.forceViewAlways and not self.fastestLapBorderActive):
                # driver info
                if not self.forceViewAlways:
                    self.visible_end = session_time_left - 8000
                self.driver_name_visible.setValue(1)
                self.driver_name_text.setValue(ac.getDriverName(self.currentVehicle.value))
                pos = self.get_race_standings_position_replay(self.currentVehicle.value)
                self.pos = pos
                self.info_position.set(background=Colors.info_position_bg(), animated=True, init=True)
                self.info_position_txt.set(color=Colors.info_position_txt(), animated=True, init=True)
                self.info_position.show()
                self.info_position_txt.setText(str(pos)).show()
                self.timing_visible.setValue(0)
                self.lbl_fastest_split.hide()
            elif self.visible_end == 0 or session_time_left < self.visible_end or (
                    sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0):
                self.driver_name_visible.setValue(0)
                self.info_position.hide()
                self.info_position_txt.hide()
                self.timing_visible.setValue(0)
                self.lbl_fastest_split.hide()
            self.visibility_race()
        else:
            # REPLAY
            self.reset_visibility()
