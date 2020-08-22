import ac
import acsys
import ctypes
from .util.classes import Window, Label, Value, POINT, Colors, Font, lapTimeStart
from .configuration import Configuration


class ACInfo:
    # INITIALIZATION
    def __init__(self):
        self.rowHeight = 38
        self.lastLapInPit = 0
        self.lastLapInvalidated = 0
        self.isLapVisuallyEnded = True
        self.raceStarted = False
        self.carsCount = 0
        self.pos = 0
        self.driver_old_best_lap = 0
        self.driver_name_width = 0
        self.lbl_position_text = Value("")
        self.currentVehicle = Value(-1)
        self.row_height = Value(-1)
        self.cursor = Value(False)
        self.fastestLap = Value(0)
        self.fastestLap2 = Value(0)
        self.fastestLapLastSector = Value(0)
        self.font = Value(0)
        self.theme = Value(-1)
        self.fastestPos = 1
        self.lastLap = 0
        self.lastLapStart = 10000
        self.sector_delay = 5000
        self.lastTimeInPit = 0
        self.visible_end = 0
        self.lastLapTime = 0
        self.lapCanBeInvalidated = True
        self.fastestLapBorderActive = False
        self.firstLapStarted = False
        self.forceViewAlways = False
        self.minLapCount = 1
        self.sectorCount = -1
        self.lapTimesArray = []
        self.driversLap = []
        self.drivers_info = []
        self.drivers_best_sectors = []
        self.standings = None
        track = ac.getTrackName(0)
        config = ac.getTrackConfiguration(0)
        if track.find("ks_nordschleife") >= 0 and config.find("touristenfahrten") >= 0:
            self.minLapCount = 0
            self.lastLapInvalidated = -1
        elif track.find("drag1000") >= 0 or track.find("drag400") >= 0:
            self.minLapCount = 0
            self.lastLapInvalidated = -1
        self.fastestLapSectors = [0, 0, 0, 0, 0, 0]
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
        self.load_cfg()
        self.info_position.setAnimationSpeed("o", 0.1)
        self.info_number.setAnimationSpeed("o", 0.1)
        self.lbl_car_class_bg.setAnimationSpeed("o", 0.1)
        self.lbl_split.setAnimationSpeed("a", 0.1)
        self.lbl_fastest_split.setAnimationSpeed("a", 0.1)

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
            self.info_number.set(background=Colors.color_for_car_class(car_name), animated=True, init=True)
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

    def get_sector(self):
        splits = ac.getCurrentSplits(self.currentVehicle.value)
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
        for i in range(self.carsCount):
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
        for i in range(self.carsCount):
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
                self.lbl_split.show()
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


    def get_best_lap(self):
        # old bestLap
        return self.fastestLap2.old

    def set_drivers_sectors(self, sectors):
        self.drivers_best_sectors = sectors

    def get_driver_best_sector(self, identifier, sector):
        for driver in self.drivers_best_sectors:
            if driver['id'] == identifier:
                if len(driver['sectors']) > sector:
                    return driver['sectors'][sector]
                break
        return 0

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
            self.fastestLapSectors = [0, 0, 0, 0, 0, 0]
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
        if self.carsCount == 0:
            self.carsCount = ac.getCarsCount()
        self.currentVehicle.setValue(ac.getFocusedCar())
        backup_laptime = 0
        backup_last_lap_in_pits = 0
        if len(self.lapTimesArray) < self.carsCount:
            for x in range(self.carsCount):
                c = ac.getCarState(x, acsys.CS.LapCount)
                self.driversLap.append(Value(c))
                self.lapTimesArray.append(lapTimeStart(c, session_time_left, 0))
        else:
            for x in range(self.carsCount):
                c = ac.getCarState(x, acsys.CS.LapCount)
                self.driversLap[x].setValue(c)
                if self.driversLap[x].hasChanged():
                    self.lapTimesArray[x].lap = self.driversLap[x].value
                    self.lapTimesArray[x].time = session_time_left
                if bool(ac.isCarInPitline(x)) or bool(ac.isCarInPit(x)):
                    self.lapTimesArray[x].lastpit = c
                if x == self.currentVehicle.value:
                    backup_laptime = self.lapTimesArray[x].time - session_time_left
                    self.lastLapStart = self.lapTimesArray[x].time
                    backup_last_lap_in_pits = self.lapTimesArray[x].lastpit

        current_vehicle_changed = self.currentVehicle.hasChanged()

        if current_vehicle_changed or (self.fastestLapBorderActive and session_time_left < self.visible_end - 2000):
            self.fastestLapBorderActive = False
            if self.currentVehicle.value >= 0:
                car_name = ac.getCarName(self.currentVehicle.value)
            else:
                car_name = ac.getCarName(0)
            self.lbl_logo.setBgColor(Colors.logo_for_car(car_name,self.get_driver_skin(self.currentVehicle.value)))
            self.info_number.set(background=Colors.color_for_car_class(car_name), animated=True)
            self.info_number_txt.setText(self.get_driver_number(self.currentVehicle.value))
            self.info_number_txt.set(color=Colors.txt_color_for_car_class(car_name), animated=True)
            self.lbl_car_class_txt.setText(Colors.car_class_name(car_name))

        if sim_info_status == 2:
            # LIVE
            if self.session.value != 2:
                # NOT RACE
                # qtime
                self.fastestLap.setValue(fl)
                bestlap = ac.getCarState(self.currentVehicle.value, acsys.CS.BestLap)
                is_in_pit = bool(ac.isCarInPitline(self.currentVehicle.value)) or \
                            bool(ac.isCarInPit(self.currentVehicle.value))
                lap_count = ac.getCarState(self.currentVehicle.value, acsys.CS.LapCount)
                if self.lastLap != lap_count:
                    self.lastLap = lap_count
                    self.firstLapStarted = False
                    if self.currentVehicle.value == 0:
                        self.lastLapStart = session_time_left
                cur_lap_time = ac.getCarState(self.currentVehicle.value, acsys.CS.LapTime)
                if cur_lap_time == 0 and backup_laptime > 0 and self.minLapCount > 0:
                    cur_lap_time = backup_laptime
                if cur_lap_time > 0:
                    self.firstLapStarted = True
                self.lastLapTime = cur_lap_time

                if is_in_pit:
                    self.lastLapInPit = lap_count
                    self.lastTimeInPit = session_time_left
                if self.currentVehicle.value == 0 and sim_info.physics.numberOfTyresOut >= 4 and self.lapCanBeInvalidated:
                    self.lastLapInvalidated = lap_count
                if is_in_pit and self.minLapCount == 0:
                    self.lastLapInvalidated = -1
                if self.sectorCount < 0:
                    self.sectorCount = sim_info.static.sectorCount
                    if not self.lbl_sectors_init:
                        self.ini_sector_labels(self.sectorCount)

                if self.fastestLap.value > 0:
                    for x in range(self.carsCount):
                        c = ac.getCarState(x, acsys.CS.BestLap)
                        if self.fastestLap2.value == 0 or (c > 0 and c < self.fastestLap2.value):
                            self.fastestLap2.setValue(c)
                            self.fastestLapSectors = ac.getLastSplits(x)
                            if len(self.fastestLapSectors):
                                self.fastestLapLastSector.setValue(self.fastestLapSectors[-1])
                else:
                    self.fastestLapSectors = [0, 0, 0, 0, 0, 0]

                lap_invalidated = bool(self.lastLapInvalidated == lap_count)
                if current_vehicle_changed or self.driver_name_text.value == "":
                    self.driver_name_text.setValue(ac.getDriverName(self.currentVehicle.value))
                # sector_delay = 5000
                # live or info
                if ((self.lastLapStart < 0 and self.minLapCount > 0 and self.isLapVisuallyEnded) or(self.minLapCount == 0 and lap_invalidated)) and self.session.value != 0:
                    self.driver_name_visible.setValue(0)
                    self.timing_visible.setValue(0)
                    self.info_position.hide()
                    self.info_position_txt.hide()
                elif (self.lastLapInPit < lap_count or self.minLapCount == 0) and not lap_invalidated and (self.lastTimeInPit == 0 or self.lastTimeInPit > self.lastLapStart or self.minLapCount == 0):
                    if self.currentVehicle.value == 0:
                        sector = sim_info.graphics.currentSectorIndex
                    else:
                        sector = self.get_sector()

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

                    traite = False
                    self.isLapVisuallyEnded = True
                    cur_splits = ac.getCurrentSplits(self.currentVehicle.value)
                    time_split = 0
                    fastest_split = 0
                    i = 0
                    for c in cur_splits:
                        if c > 0:
                            time_split += c
                            fastest_split += self.fastestLapSectors[i]
                            i += 1
                    fastest_split_fin = fastest_split
                    if i < self.sectorCount:
                        fastest_split_fin += self.fastestLapSectors[i]

                    # Situation
                    for s in range(0, self.sectorCount):
                        if sector == s + 1 and s + 1 <= self.sectorCount and cur_lap_time - time_split <= self.sector_delay and fastest_split > 0:
                            # SECTOR_X_FINISHED_BEGIN_SECTOR_Y
                            self.isLapVisuallyEnded = False

                            driver_best_sector = self.get_driver_best_sector(self.currentVehicle.value, s)
                            if self.fastestLapSectors[s] >= cur_splits[s]:
                                self.lbl_sectors_bg[s].set(background=Colors.info_split_best_bg(), animated=True)
                                self.lbl_sectors_text[s].setText("-" + self.time_splitting(self.fastestLapSectors[s] - cur_splits[s], "yes"))
                            elif driver_best_sector > 0 and driver_best_sector >= cur_splits[s]:
                                self.lbl_sectors_bg[s].set(background=Colors.info_split_personal_bg(), animated=True)
                                self.lbl_sectors_text[s].setText("+" + self.time_splitting(cur_splits[s] - self.fastestLapSectors[s], "yes"))
                            else:
                                self.lbl_sectors_bg[s].set(background=Colors.info_split_slow_bg(), animated=True)
                                self.lbl_sectors_text[s].setText("+" + self.time_splitting(cur_splits[s] - self.fastestLapSectors[s], "yes"))

                            self.timing_text.setValue(self.time_splitting(time_split, "yes"))
                            self.info_position.hide()
                            self.info_position_txt.hide()
                            i = 0
                            for l in self.lbl_sectors_bg:
                                if i < sector:
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
                            traite = True
                            break

                    if not traite:
                        if self.sectorCount - 1 == sector and self.fastestLap.value > 0 and cur_lap_time > self.fastestLap.value - self.sector_delay:
                            # LAST_SECONDS_OF_SECTOR_LAP,
                            self.isLapVisuallyEnded = False
                            self.timing_text.setValue(self.time_splitting(cur_lap_time))
                            self.info_position.hide()
                            self.info_position_txt.hide()
                        elif self.lastLapInvalidated != lap_count - 1 and ((self.lastLapInPit != lap_count - 1 and sector == 0) or (self.minLapCount == 0)) and cur_lap_time <= self.sector_delay and last_lap > 0:
                            # LAP_FINISHED_BEGIN_NEW_LAP,
                            self.isLapVisuallyEnded = False
                            pos = ac.getCarLeaderboardPosition(self.currentVehicle.value)
                            if pos == -1:
                                pos = self.get_standings_position(self.currentVehicle.value)
                            self.pos = pos
                            self.info_position.set(background=Colors.info_position_bg(), animated=True, init=True)
                            self.info_position_txt.set(color=Colors.info_position_txt(), animated=True, init=True)

                            self.info_position_txt.setText(str(pos)).show()
                            self.info_position.show()
                            self.timing_text.setValue(self.time_splitting(last_lap, "yes"))

                            #self.lbl_sectors_text[self.sectorCount - 1].set(color=Colors.info_position_txt(),animated=True)
                            last_splits = ac.getLastSplits(self.currentVehicle.value)
                            #get old last 3rd sector to compare -0000 self.fastestLapSectors[-1]
                            if len(self.fastestLapSectors) and len(last_splits):
                                if self.fastestLapSectors[-1] >= last_splits[-1]:
                                    self.lbl_sectors_bg[-1].set(background=Colors.info_split_best_bg(), animated=True)
                                    self.lbl_sectors_text[-1].setText("-" + self.time_splitting(self.fastestLapLastSector.old - last_splits[-1], "yes"))
                                elif self.driver_old_best_lap > 0 and self.driver_old_best_lap >= last_splits[-1]:
                                    self.lbl_sectors_bg[-1].set(background=Colors.info_split_personal_bg(), animated=True)
                                    self.lbl_sectors_text[-1].setText("+" + self.time_splitting(last_splits[-1] - self.fastestLapSectors[-1], "yes"))
                                else:
                                    self.lbl_sectors_bg[-1].set(background=Colors.info_split_slow_bg(), animated=True)
                                    self.lbl_sectors_text[-1].setText("+" + self.time_splitting(last_splits[-1] - self.fastestLapSectors[-1], "yes"))

                                for l in self.lbl_sectors_text:
                                    l.show()
                                for l in self.lbl_sectors_bg:
                                    l.show()
                                for l in self.lbl_sectors_title_bg:
                                    l.show()
                                for l in self.lbl_sectors_title_txt:
                                    l.show()
                        else:
                            # OTHER
                            self.isLapVisuallyEnded = True
                            self.timing_text.setValue(self.time_splitting(cur_lap_time))
                            self.info_position.hide()
                            self.info_position_txt.hide()
                            i = 0
                            for l in self.lbl_sectors_bg:
                                if i < sector:
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
                            if fastest_split_fin > 0:
                                self.driver_old_best_lap = self.get_driver_best_sector(self.currentVehicle.value,
                                                                                       sector)
                    self.fastestLap.changed = False
                else:
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
                    elif lap_invalidated and self.lastLapInPit < lap_count and self.minLapCount > 0:
                        self.driver_name_visible.setValue(0)
                        self.timing_visible.setValue(0)
                        self.info_position.hide()
                        self.info_position_txt.hide()
                    elif bestlap > 0:
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
                    elif is_in_pit:
                        self.driver_name_visible.setValue(0)
                        self.timing_visible.setValue(0)
                        self.info_position.hide()
                        self.info_position_txt.hide()
                    else:
                        self.driver_name_visible.setValue(1)
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
                for x in range(self.carsCount):
                    c = ac.getCarState(x, acsys.CS.LapCount)
                    if c > completed:
                        completed = c
                if completed <= 1:
                    self.race_fastest_lap.setValue(0)
                else:
                    for i in range(self.carsCount):
                        bl = ac.getCarState(i, acsys.CS.BestLap)
                        l = ac.getCarState(i, acsys.CS.LapCount)
                        if bl > 0 and l > self.minLapCount and (self.race_fastest_lap.value == 0 or bl < self.race_fastest_lap.value):
                            self.race_fastest_lap.setValue(bl)
                            self.race_fastest_lap_driver.setValue(i)

                if self.race_fastest_lap.hasChanged() and self.race_fastest_lap.value > 0:
                    self.fastestLapBorderActive = True
                    car_name = ac.getCarName(self.race_fastest_lap_driver.value)
                    self.lbl_logo.setBgColor(Colors.logo_for_car(car_name,self.get_driver_skin(self.race_fastest_lap_driver.value)))
                    self.visible_end = session_time_left - 10000
                    self.driver_name_visible.setValue(1)
                    self.driver_name_text.setValue(ac.getDriverName(self.race_fastest_lap_driver.value))
                    self.info_position.hide()
                    self.info_position_txt.hide()
                    self.lbl_fastest_split.setText(self.time_splitting(self.race_fastest_lap.value, "yes")).show()
                    self.info_number.set(background=Colors.color_for_car_class(car_name))
                    self.info_number_txt.setText(self.get_driver_number(self.race_fastest_lap_driver.value))
                    self.info_number_txt.set(color=Colors.txt_color_for_car_class(car_name), animated=True)
                    self.lbl_car_class_txt.setText(Colors.car_class_name(car_name))

                elif current_vehicle_changed or (self.forceViewAlways and not self.fastestLapBorderActive):
                    # driver info
                    if not self.forceViewAlways:
                        self.visible_end = session_time_left - 8000
                    self.driver_name_visible.setValue(1)
                    self.driver_name_text.setValue(ac.getDriverName(self.currentVehicle.value))

                    if not self.raceStarted:
                        if sim_info.graphics.completedLaps > 0 or sim_info.graphics.iCurrentTime > 20000:
                            self.raceStarted = True
                        # Generate standings from -0.5 to 0.5 for the start of race
                        standings = []
                        for i in range(self.carsCount):
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
                    self.lbl_fastest_split.hide()
                elif self.visible_end == 0 or session_time_left < self.visible_end or (sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0):
                    self.driver_name_visible.setValue(0)
                    self.info_position.hide()
                    self.info_position_txt.hide()
                    self.timing_visible.setValue(0)
                    self.lbl_fastest_split.hide()
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
