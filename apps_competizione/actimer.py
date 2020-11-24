import ac
import acsys
import os.path
import json, math
import ctypes
import encodings.idna
import threading
import http.client
from decimal import Decimal, ROUND_HALF_UP
from .util.func import rgb
from .util.classes import Window, Label, Value, Colors, Font, Log, Config
from .configuration import Configuration


class ACTimer:
    # INITIALIZATION

    def __init__(self, sim_info):
        self.replay_initialised = False
        self.replay_asc = False
        self.replay_rgb = 255
        self.session = Value(-1)
        self.theme = Value(-1)
        self.cursor = Value(False)
        self.row_height = Value(-1)
        self.font = Value(0)
        self.numberOfLaps = -1
        self.corner_width=0
        self.hasExtraLap = sim_info.static.hasExtraLap
        self.numberOfLapsTimedRace = -1
        self.sessionMaxTime = -1
        self.pitWindowVisibleEnd = 0
        self.pitWindowStart = sim_info.static.PitWindowStart
        self.pitWindowEnd = sim_info.static.PitWindowEnd
        self.pitWindowActive = False
        self.numberOfLapsCompleted = Value(0)
        self.window = Window(name="ACTV CP Timer", width=228, height=42)

        # background corners
        self.lbl_left_corner = Label(self.window.app)\
            .set(w=27, h=42,
                 x=0, y=-80,
                 opacity=0,
                 background=Colors.timer_left_corner())
        self.lbl_right_corner = Label(self.window.app)\
            .set(w=27, h=42,
                 x=0, y=-80,
                 opacity=0,
                 background=Colors.timer_right_corner())
        # background
        self.lbl_session_info = Label(self.window.app)\
            .set(w=331, h=36,
                 x=self.row_height.value, y=-80)
        # Timer / lap
        self.lbl_session_info_txt = Label(self.window.app, "00:00")\
            .set(w=0, h=36,
                 x=self.row_height.value, y=-76,
                 opacity=0,
                 font_size=26,
                 align="right")
        # Time
        self.lbl_time_of_day_txt = Label(self.window.app, "12:00")\
            .set(w=0, h=36,
                 x=self.row_height.value, y=-76,
                 opacity=0,
                 font_size=26,
                 align="left")
        self.lbl_am_pm_txt = Label(self.window.app, "PM")\
            .set(w=0, h=36,
                 x=self.row_height.value, y=-76,
                 opacity=0,
                 font_size=26,
                 align="left")
        self.lbl_extra_lap_txt = Label(self.window.app, "+1 LAP")\
            .set(w=0, h=36,
                 x=self.row_height.value, y=-76,
                 opacity=0,
                 font_size=26,
                 align="right")
        # background pit window
        self.lbl_session_title = Label(self.window.app)\
            .set(w=36, h=36,
                 x=0, y=-74, opacity=1)
        # Race, Qual, Practice
        self.lbl_session_title_txt = Label(self.window.app, "FREE PRACTICE")\
            .set(w=0, h=36,
                 x=114, y=-76,
                 opacity=0,
                 font_size=26,
                 align="center")
        # Status
        self.lbl_session_border = Label(self.window.app)\
            .set(w=154 + 36, h=2,
                 x=0, y=-74)
        self.lbl_session_border_2 = Label(self.window.app)\
            .set(w=154 + 36, h=2,
                 x=200, y=-74)

        # Open race.ini
        file_path = os.path.join(os.path.expanduser("~"), "Documents", "Assetto Corsa", "cfg") + "/"
        conf = Config(file_path, "race.ini")
        start = conf.get("LIGHTING", "SUN_ANGLE")
        self.time_multiplier = float(conf.get("LIGHTING", "TIME_MULT"))

        session_0=session_1=session_2=session_3=session_4=session_5=session_6=0
        for i in range(6):
            session_name = conf.get("SESSION_" + str(i), "NAME")
            if session_name == "Practice":
                session_0 = conf.get("SESSION_" + str(i), "DURATION_MINUTES")
            elif session_name == "Qualifying":
                session_1 = conf.get("SESSION_" + str(i), "DURATION_MINUTES")
            elif session_name == "Race":
                session_2 = conf.get("SESSION_" + str(i), "DURATION_MINUTES")
            elif session_name == "Hotlap":
                session_3 = conf.get("SESSION_" + str(i), "DURATION_MINUTES")
            elif session_name == "Time Attack":
                session_4 = conf.get("SESSION_" + str(i), "DURATION_MINUTES")
            elif session_name == "Drift":
                session_5 = conf.get("SESSION_" + str(i), "DURATION_MINUTES")
            elif session_name == "Drag":
                session_6 = conf.get("SESSION_" + str(i), "DURATION_MINUTES")

        self.sessions_duration = [float(session_0)*60000,
                                  float(session_1)*60000,
                                  float(session_2)*60000,
                                  float(session_3)*60000,
                                  float(session_4)*60000,
                                  float(session_5)*60000,
                                  float(session_6)*60000
                                  ]
        self.start_time_of_day_original = self.start_time_of_day=(780 + 3.75 * float(start)) * 60000 - (4000 * self.time_multiplier)
        #ac.console("ini:" + str(self.start_time_of_day) + " = " + self.time_of_day(self.start_time_of_day))
        self.last_start_time_offset=-1
        self.session_time_left=0
        self.session_info_imported=False
        self.is_multiplayer = ac.getServerIP() != ''
        self.lbl_time_of_day_txt.setText(self.time_of_day(self.start_time_of_day))
        self.load_cfg()

    # PUBLIC METHODS
    # ---------------------------------------------------------------------------------------------------------------------------------------------
    def load_cfg(self):
        self.row_height.setValue(Configuration.ui_row_height)
        Colors.theme(reload=True)
        self.theme.setValue(Colors.general_theme + Colors.theme_red + Colors.theme_green + Colors.theme_blue)
        self.font.setValue(Font.current)
        self.redraw_size()

    def redraw_size(self):
        # Colors
        if self.theme.hasChanged():
            self.lbl_session_info.set(background=Colors.timer_time_bg(), animated=True, init=True)
            self.lbl_session_info_txt.set(color=Colors.timer_time_txt(), animated=True, init=True)
            self.lbl_time_of_day_txt.set(color=Colors.timer_time_txt(), animated=True, init=True)
            self.lbl_am_pm_txt.set(color=Colors.timer_time_txt(), animated=True, init=True)
            self.lbl_extra_lap_txt.set(color=Colors.timer_time_txt(), animated=True, init=True)
            self.lbl_session_title.set(background=Colors.white(bg=True), animated=True, init=True)
            self.lbl_session_title_txt.set(color=Colors.timer_title_txt(), animated=True, init=True)
        if self.row_height.hasChanged() or self.font.hasChanged():
            # Fonts
            self.lbl_session_info_txt.update_font()
            self.lbl_time_of_day_txt.update_font()
            # Size
            font_size = Font.get_font_size(self.row_height.value+Font.get_font_offset())
            self.lbl_session_info_txt.set(h=self.row_height.value,
                                          font_size=font_size + self.row_height.value*9/38,
                                          y=-76 + Font.get_font_x_offset() - self.row_height.value*7/38)
            #todo race qual pract... width
            height = round(self.row_height.value * 42/38)
            #corner_width = int(self.row_height.value * 27/38)
            #self.corner_width = round(height * 27/42) 57x83
            self.corner_width = int(Decimal(height * 29/42).quantize(0, ROUND_HALF_UP))
            #ac.console("corner--:" + str(self.corner_width) + " x " + str(height))
            #self.lbl_left_corner.set(background=Colors.timer_left_corner())
            #self.lbl_right_corner.set(background=Colors.timer_right_corner())
            self.lbl_left_corner.set(w=self.corner_width, h=height)
            self.lbl_right_corner.set(w=self.corner_width, h=height)
            self.lbl_session_info.set(w=self.row_height.value * 4, h=height)
            self.lbl_time_of_day_txt.set(h=self.row_height.value,
                                         font_size=font_size + self.row_height.value*9/38,
                                         y=-76 + Font.get_font_x_offset() - self.row_height.value*7/38)
            self.lbl_am_pm_txt.set(h=self.row_height.value,
                                   font_size=font_size - self.row_height.value*1/38,
                                   y=-76 + Font.get_font_x_offset() + self.row_height.value*1/38)
            self.lbl_extra_lap_txt.set(h=self.row_height.value,
                                   font_size=font_size - self.row_height.value*1/38,
                                   y=-76 + Font.get_font_x_offset() + self.row_height.value*1/38)
            w_offset = (self.row_height.value - 38) * 50 / 38
            self.lbl_session_title.set(w=self.row_height.value * 216 / 38 + w_offset*2,
                                       x=114 - self.row_height.value * 108 / 38 - w_offset,
                                       h=self.row_height.value*32/38)
            self.lbl_session_title_txt.set(h=self.row_height.value,
                                           font_size=font_size - self.row_height.value*1/38,
                                           y=-76 + Font.get_font_x_offset() + self.row_height.value*1/38)

            self.lbl_session_border.set(w=self.row_height.value*8/38,h=self.row_height.value*32/38)
            self.lbl_session_border_2.set(w=self.row_height.value*8/38,h=self.row_height.value*32/38)

            w_offset = (self.row_height.value - 38) * 22 / 38
            if self.session.value == 1:
                # Qualifying
                self.lbl_session_info_txt.set(x=114 - self.row_height.value * 70 / 38 - w_offset, animated=True)
                self.lbl_session_border.set(x=114 - self.row_height.value * 63 / 38 - w_offset, animated=True) # -8/38=self
                self.lbl_session_border_2.set(x=114 + self.row_height.value * 55 / 38 + w_offset, animated=True)
                self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 70 / 38 + w_offset, animated=True)
                self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 125 / 38 + w_offset, animated=True)
                self.lbl_left_corner.set(x=114 - self.row_height.value * 168 / 38 - self.corner_width)
                self.lbl_right_corner.set(x=114 + self.row_height.value * 168 / 38)
                self.lbl_session_info.set(w=self.row_height.value * 336 / 38, x=114 - self.row_height.value * 168 / 38) #336 + 56 28
            elif self.session.value == 0:
                # PRACTICE
                self.lbl_session_info_txt.set(x=114 - self.row_height.value * 81 / 38 - w_offset, animated=True)
                self.lbl_session_border.setX(x=114 - self.row_height.value * 74 / 38 - w_offset, animated=True) # -8/38=self
                self.lbl_session_border_2.setX(x=114 + self.row_height.value * 66 / 38 + w_offset, animated=True) # 16
                self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 81 / 38 + w_offset, animated=True)
                self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 136 / 38 + w_offset, animated=True)
                self.lbl_left_corner.set(x=114 - self.row_height.value * 180 / 38 - self.corner_width) # 213
                self.lbl_right_corner.set(x=114 + self.row_height.value * 180 / 38)
                self.lbl_session_info.set(w=self.row_height.value * 360 / 38, x=114 - self.row_height.value * 180 / 38) #372 + 92
            elif self.session.value == 3:
                #HOTLAP
                w_offset = (self.row_height.value - 38) * 18 / 38
                self.lbl_session_info_txt.set(x=114 - self.row_height.value * 53 / 38 - w_offset, animated=True)
                self.lbl_session_border.set(x=114 - self.row_height.value * 46 / 38 - w_offset, animated=True)
                self.lbl_session_border_2.set(x=114 + self.row_height.value * 38 / 38 + w_offset, animated=True)
                self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 53 / 38 + w_offset, animated=True)
                self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 108 / 38 + w_offset, animated=True)
                self.lbl_left_corner.set(x=114 - self.row_height.value * 150 / 38 - self.corner_width)
                self.lbl_right_corner.set(x=114 + self.row_height.value * 150 / 38)
                self.lbl_session_info.set(w=self.row_height.value * 300 / 38, x=114 - self.row_height.value * 150 / 38)
            elif self.session.value == 4:
                #TIME ATTACK
                w_offset = (self.row_height.value - 38) * 18 / 38
                self.lbl_session_info_txt.set(x=114 - self.row_height.value * 78 / 38 - w_offset, animated=True)
                self.lbl_session_border.setX(x=114 - self.row_height.value * 71 / 38 - w_offset, animated=True)
                self.lbl_session_border_2.setX(x=114 + self.row_height.value * 63 / 38 + w_offset, animated=True)
                self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 78 / 38 + w_offset, animated=True)
                self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 133 / 38 + w_offset, animated=True)
                self.lbl_left_corner.set(x=114 - self.row_height.value * 183 / 38 - self.corner_width)
                self.lbl_right_corner.set(x=114 + self.row_height.value * 183 / 38)
                self.lbl_session_info.set(w=self.row_height.value * 366 / 38, x=114 - self.row_height.value * 183 / 38)
            elif self.session.value == 5:
                #DRIFT
                w_offset = (self.row_height.value - 38) * 8 / 38
                self.lbl_session_info_txt.set(x=114 - self.row_height.value * 46 / 38 - w_offset, animated=True)
                self.lbl_session_border.set(x=114 - self.row_height.value * 39 / 38 - w_offset, animated=True) # -8/38=self
                self.lbl_session_border_2.set(x=114 + self.row_height.value * 31 / 38 + w_offset, animated=True)
                self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 46 / 38 + w_offset, animated=True)
                self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 101 / 38 + w_offset, animated=True)
                self.lbl_left_corner.set(x=114 - self.row_height.value * 144 / 38 - self.corner_width)
                self.lbl_right_corner.set(x=114 + self.row_height.value * 144 / 38)
                self.lbl_session_info.set(w=self.row_height.value * 288 / 38, x=114 - self.row_height.value * 144 / 38) #336 + 56 28
            elif self.session.value == 6:
                #DRAG
                w_offset = (self.row_height.value - 38) * 8 / 38
                self.lbl_session_info_txt.set(x=114 - self.row_height.value * 46 / 38 - w_offset, animated=True)
                self.lbl_session_border.set(x=114 - self.row_height.value * 39 / 38 - w_offset, animated=True)
                self.lbl_session_border_2.set(x=114 + self.row_height.value * 31 / 38 + w_offset, animated=True)
                self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 46 / 38 + w_offset, animated=True)
                self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 101 / 38 + w_offset, animated=True)
                self.lbl_left_corner.set(x=114 - self.row_height.value * 144 / 38 - self.corner_width)
                self.lbl_right_corner.set(x=114 + self.row_height.value * 144 / 38)
                self.lbl_session_info.set(w=self.row_height.value * 288 / 38, x=114 - self.row_height.value * 144 / 38)




    def time_splitting(self, ms):
        s = ms / 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        # d,h=divmod(h,24)
        if h > 0:
            return "{0}:{1}:{2}".format(str(int(h)), str(int(m)).zfill(2), str(int(s)).zfill(2))
        else:
            return "{0}:{1}".format(str(int(m)).zfill(2), str(int(s)).zfill(2))

    def time_of_day(self, ms):
        ms = ms % (24*3600*1000)
        #if ms > 64800000:#18:00
        #    ms = 64800000
        s = ms / 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        # d,h=divmod(h,24)
        # AM PM - 12h
        h = h % 12
        if h==0 and ms % (24*3600*1000)  > 12 * 3600 * 1000:
            h -= 12
        #if h > 12:
        #    h-=12
        return "{0}:{1}".format(str(int(abs(h))), str(int(m)).zfill(2))

    def get_sessions_data_from_server(self):
        try:
            server_ip = ac.getServerIP()
            port = ac.getServerHttpPort()
            if server_ip != '' and port > 0:
                conn = http.client.HTTPConnection(ac.getServerIP(), port=port)
                conn.request("GET", "/INFO")
                response = conn.getresponse()
                data = json.loads(response.read().decode('utf-8', errors='ignore'))
                conn.close()

                '''
                timeofday: -72
                sessiontypes	[ 1, 2, 3 ]
                durations	[ 2, 2, 12 ]
                '''

                i=0
                for t in data["sessiontypes"]:
                    self.sessions_duration[t-1] = float(data["durations"][i])*60000
                    i+=1

                self.time_multiplier = 1 # no way of knowing, game log?
                self.start_time_of_day_original = self.start_time_of_day = (780 + 3.75 * float(data["timeofday"])) * 60000
                self.last_start_time_offset = self.start_time_of_day + (self.sessions_duration[self.session.value] - self.session_time_left)*self.time_multiplier

        except:
            Log.w("Error tower")
        self.session_info_imported = True

    def animate(self):
        self.lbl_left_corner.animate()
        self.lbl_right_corner.animate()
        self.lbl_session_info.animate()
        self.lbl_session_info_txt.animate()
        self.lbl_time_of_day_txt.animate()
        self.lbl_am_pm_txt.animate()
        self.lbl_extra_lap_txt.animate()
        self.lbl_session_title.animate()
        self.lbl_session_title_txt.animate()
        self.lbl_session_border.animate()
        self.lbl_session_border_2.animate()

    def manage_window(self, game_data):
        win_x = self.window.getPos().x
        win_y = self.window.getPos().y
        if win_x > 0:
            self.window.last_x = win_x
            self.window.last_y = win_y
        else:
            self.window.setLastPos()
            win_x = self.window.getPos().x
            win_y = self.window.getPos().y
        if win_x < game_data.cursor_x < win_x + self.window.width and win_y < game_data.cursor_y < win_y + self.window.height:
            self.cursor.setValue(True)
        else:
            self.cursor.setValue(False)

        if self.session.hasChanged():
            self.numberOfLapsTimedRace = -1
            self.hasExtraLap = -1
            self.numberOfLaps = -1
            self.pitWindowStart = -1
            self.pitWindowEnd = -1
            self.sessionMaxTime = -1
            self.pitWindowVisibleEnd = 0
            self.pitWindowActive = False
            #if self.session_time_left < 0:# last session was not manually skipped
            self.start_time_of_day=self.start_time_of_day_original# Reset time + 900 * self.time_multiplier 
            self.last_start_time_offset = self.start_time_of_day * self.time_multiplier
            #else:
            #    self.start_time_of_day = self.last_start_time_offset
            #if self.last_start_time_offset != -1:
            #    self.start_time_of_day=self.last_start_time_offset
            w_offset = (self.row_height.value - 38) * 22 / 38
            if self.session.value == 2:
                self.lbl_session_title_txt.setText("RACE")
                #self.lbl_session_title.set(x=114 - self.row_height.value * 27 / 38, w=self.row_height.value * 54 / 38)
            elif self.session.value == 1:
                self.lbl_session_title_txt.setText("QUALIFYING")
                self.lbl_session_info_txt.set(x=114 - self.row_height.value * 70 / 38 - w_offset, animated=True)
                self.lbl_session_border.set(x=114 - self.row_height.value * 63 / 38 - w_offset, animated=True) # -8/38=self
                self.lbl_session_border_2.set(x=114 + self.row_height.value * 55 / 38 + w_offset, animated=True)
                self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 70 / 38 + w_offset, animated=True)
                self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 125 / 38 + w_offset, animated=True)
                self.lbl_left_corner.set(x=114 - self.row_height.value * 168 / 38 - self.corner_width)
                self.lbl_right_corner.set(x=114 + self.row_height.value * 168 / 38)
                self.lbl_session_info.set(w=self.row_height.value * 336 / 38, x=114 - self.row_height.value * 168 / 38) #336 + 56 28
            elif self.session.value == 0:
                self.lbl_session_title_txt.setText("FREE PRACTICE")
                self.lbl_session_info_txt.set(x=114 - self.row_height.value * 81 / 38 - w_offset, animated=True)
                self.lbl_session_border.setX(x=114 - self.row_height.value * 74 / 38 - w_offset, animated=True) # -8/38=self
                self.lbl_session_border_2.setX(x=114 + self.row_height.value * 66 / 38 + w_offset, animated=True) # 16
                self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 81 / 38 + w_offset, animated=True)
                self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 136 / 38 + w_offset, animated=True)
                self.lbl_left_corner.set(x=114 - self.row_height.value * 180 / 38 - self.corner_width) # 213
                self.lbl_right_corner.set(x=114 + self.row_height.value * 180 / 38)
                self.lbl_session_info.set(w=self.row_height.value * 360 / 38, x=114 - self.row_height.value * 180 / 38) #372 + 92
            elif self.session.value == 3:
                self.lbl_session_title_txt.setText("HOTLAP")
                w_offset = (self.row_height.value - 38) * 18 / 38
                self.lbl_session_info_txt.set(x=114 - self.row_height.value * 53 / 38 - w_offset, animated=True)
                self.lbl_session_border.set(x=114 - self.row_height.value * 46 / 38 - w_offset, animated=True)
                self.lbl_session_border_2.set(x=114 + self.row_height.value * 38 / 38 + w_offset, animated=True)
                self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 53 / 38 + w_offset, animated=True)
                self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 108 / 38 + w_offset, animated=True)
                self.lbl_left_corner.set(x=114 - self.row_height.value * 150 / 38 - self.corner_width)
                self.lbl_right_corner.set(x=114 + self.row_height.value * 150 / 38)
                self.lbl_session_info.set(w=self.row_height.value * 300 / 38, x=114 - self.row_height.value * 150 / 38)
            elif self.session.value == 4:
                self.lbl_session_title_txt.setText("TIME ATTACK")
                w_offset = (self.row_height.value - 38) * 18 / 38
                self.lbl_session_info_txt.set(x=114 - self.row_height.value * 78 / 38 - w_offset, animated=True)
                self.lbl_session_border.setX(x=114 - self.row_height.value * 71 / 38 - w_offset, animated=True)
                self.lbl_session_border_2.setX(x=114 + self.row_height.value * 63 / 38 + w_offset, animated=True)
                self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 78 / 38 + w_offset, animated=True)
                self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 133 / 38 + w_offset, animated=True)
                self.lbl_left_corner.set(x=114 - self.row_height.value * 183 / 38 - self.corner_width)
                self.lbl_right_corner.set(x=114 + self.row_height.value * 183 / 38)
                self.lbl_session_info.set(w=self.row_height.value * 366 / 38, x=114 - self.row_height.value * 183 / 38)
            elif self.session.value == 5:
                self.lbl_session_title_txt.setText("DRIFT")
                w_offset = (self.row_height.value - 38) * 8 / 38
                self.lbl_session_info_txt.set(x=114 - self.row_height.value * 46 / 38 - w_offset, animated=True)
                self.lbl_session_border.set(x=114 - self.row_height.value * 39 / 38 - w_offset, animated=True)
                self.lbl_session_border_2.set(x=114 + self.row_height.value * 31 / 38 + w_offset, animated=True)
                self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 46 / 38 + w_offset, animated=True)
                self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 101 / 38 + w_offset, animated=True)
                self.lbl_left_corner.set(x=114 - self.row_height.value * 144 / 38 - self.corner_width)
                self.lbl_right_corner.set(x=114 + self.row_height.value * 144 / 38)
                self.lbl_session_info.set(w=self.row_height.value * 288 / 38, x=114 - self.row_height.value * 144 / 38)
            elif self.session.value == 6:
                self.lbl_session_title_txt.setText("DRAG")
                w_offset = (self.row_height.value - 38) * 8 / 38
                self.lbl_session_info_txt.set(x=114 - self.row_height.value * 46 / 38 - w_offset, animated=True)
                self.lbl_session_border.set(x=114 - self.row_height.value * 39 / 38 - w_offset, animated=True)
                self.lbl_session_border_2.set(x=114 + self.row_height.value * 31 / 38 + w_offset, animated=True)
                self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 46 / 38 + w_offset, animated=True)
                self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 101 / 38 + w_offset, animated=True)
                self.lbl_left_corner.set(x=114 - self.row_height.value * 144 / 38 - self.corner_width)
                self.lbl_right_corner.set(x=114 + self.row_height.value * 144 / 38)
                self.lbl_session_info.set(w=self.row_height.value * 288 / 38, x=114 - self.row_height.value * 144 / 38)

        if self.cursor.hasChanged():
            self.window.setBgOpacity(0).border(0)

    def on_update(self, sim_info, game_data):
        self.session.setValue(game_data.session)
        self.manage_window(game_data)
        sim_info_status = game_data.status
        self.animate()
        if sim_info_status == 2:  # LIVE
            self.session_time_left = session_time_left = game_data.sessionTimeLeft
            if self.is_multiplayer and not self.session_info_imported:
                thread_standings = threading.Thread(target=self.get_sessions_data_from_server)
                thread_standings.daemon = True
                thread_standings.start()
            if self.session.value < 2:
                self.lbl_extra_lap_txt.hide()
                self.last_start_time_offset = self.start_time_of_day + (self.sessions_duration[self.session.value] - session_time_left)*self.time_multiplier
                time_of_day=self.time_of_day(self.last_start_time_offset)
                self.lbl_time_of_day_txt.setText(time_of_day).show()
                am_pm_offset=""
                if len(time_of_day) > 4:
                    am_pm_offset="  "
                if self.last_start_time_offset % (24*3600*1000)  < 12 * 3600 * 1000:
                    self.lbl_am_pm_txt.setText(am_pm_offset + "AM").show()
                else:
                    self.lbl_am_pm_txt.setText(am_pm_offset + "PM").show()
                if session_time_left < 0:
                    session_time_left = 0
                    self.lbl_session_info_txt.setColor(Colors.red(),True)
                else:
                    self.lbl_session_info_txt.setColor(Colors.timer_time_txt(),True)
                self.lbl_session_title.hide()
                self.lbl_session_title_txt.setColor(Colors.timer_time_txt(), animated=True).show()
                self.lbl_session_border.show()
                self.lbl_session_border_2.show()
                self.lbl_left_corner.show()
                self.lbl_right_corner.show()
                self.lbl_session_info.show()
                self.lbl_session_info_txt.setText(self.time_splitting(session_time_left)).show()

                # Flags
                if session_time_left <= 0:
                    # Finish
                    self.lbl_session_border.set(background=Colors.timer_finish())
                    self.lbl_session_border_2.set(background=Colors.timer_finish())
                elif game_data.flag == 2:
                    # Yellow Flag
                    self.lbl_session_border.set(background=Colors.timer_border_yellow_flag_bg(),
                                                animated=True)
                    self.lbl_session_border_2.set(background=Colors.timer_border_yellow_flag_bg(),
                                                animated=True)
                else:
                    # Green
                    self.lbl_session_border.set(background=Colors.timer_border_bg(),
                                                animated=True)
                    self.lbl_session_border_2.set(background=Colors.timer_border_bg(),
                                                animated=True)
            elif self.session.value == 2:
                # Race
                completed = 0
                race_finished = 0
                for x in range(ac.getCarsCount()):
                    c = ac.getCarState(x, acsys.CS.LapCount)
                    if c > completed:
                        completed = c
                    if ac.getCarState(x, acsys.CS.RaceFinished):
                        race_finished = 1
                completed += 1
                if self.numberOfLaps < 0:
                    self.numberOfLaps = sim_info.graphics.numberOfLaps
                if self.hasExtraLap == 1 and session_time_left < 0 and self.numberOfLapsTimedRace < 0:
                    self.numberOfLapsTimedRace = completed + 1

                # PitWindow
                pit_window_remain = ""
                if not game_data.beforeRaceStart and (self.pitWindowEnd > 0 or self.pitWindowStart > 0):
                    if self.numberOfLaps > 0:
                        # Lap race
                        self.numberOfLapsCompleted.setValue(completed)
                        if self.numberOfLapsCompleted.hasChanged():
                            if self.numberOfLapsCompleted.value == self.pitWindowStart and not game_data.beforeRaceStart:
                                self.pitWindowVisibleEnd = session_time_left - 8000
                                self.pitWindowActive = True
                            elif self.numberOfLapsCompleted.value == self.pitWindowEnd:
                                self.pitWindowVisibleEnd = session_time_left - 8000
                                self.pitWindowActive = False
                        if self.pitWindowActive:
                            if self.pitWindowEnd - completed > 1:
                                pit_window_remain = " {0} Laps".format(self.pitWindowEnd - completed)
                            else:
                                pit_window_remain = " {0} Lap".format(self.pitWindowEnd - completed)
                    else:
                        # Timed race
                        if self.sessionMaxTime < 0:
                            self.sessionMaxTime = round(session_time_left, -3)
                        if not self.pitWindowActive and session_time_left <= self.sessionMaxTime - self.pitWindowStart * 60 * 1000 and session_time_left >= self.sessionMaxTime - self.pitWindowEnd * 60 * 1000 and not game_data.beforeRaceStart:
                            self.pitWindowVisibleEnd = session_time_left - 8000
                            self.pitWindowActive = True
                        elif self.pitWindowActive and session_time_left < self.sessionMaxTime - self.pitWindowEnd * 60 * 1000:
                            self.pitWindowVisibleEnd = session_time_left - 8000
                            self.pitWindowActive = False
                        if self.pitWindowActive:
                            pit_window_remain = " " + self.time_splitting(session_time_left - (self.sessionMaxTime - self.pitWindowEnd * 60 * 1000))
                else:
                    self.pitWindowActive = False

                self.lbl_left_corner.show()
                self.lbl_right_corner.show()
                self.lbl_session_info.show()
                self.lbl_session_info_txt.show()
                self.lbl_session_title_txt.show()
                self.lbl_session_border.show()
                self.lbl_session_border_2.show()
                if self.hasExtraLap > 0:
                    self.lbl_extra_lap_txt.show()
                else:
                    self.lbl_extra_lap_txt.hide()
                is_final_lap = False
                # Time laps left
                time_left_str_len=5
                if race_finished > 0 and self.numberOfLaps == 0:#session_time_left > 0
                    self.lbl_session_info_txt.setText("00:00").setColor(Colors.red(),True)
                elif race_finished > 0:
                    self.lbl_session_info_txt.setText("{0} / {1}".format(self.numberOfLaps, self.numberOfLaps)).setColor(Colors.red(),True)
                    #self.lbl_session_info_txt.setText("FINISH").setColor(Colors.red(),True)completed == self.numberOfLaps or
                elif (
                        self.numberOfLaps == 0 and self.hasExtraLap == 0 and session_time_left < 0) or (
                        self.hasExtraLap == 1 and completed == self.numberOfLapsTimedRace):
                    self.lbl_session_info_txt.setText("00:00").setColor(Colors.timer_time_txt(),True)
                    is_final_lap=True
                elif self.numberOfLaps > 0:
                    self.lbl_session_info_txt.setText("{0} / {1}".format(completed, self.numberOfLaps)).setColor(Colors.timer_time_txt(),True)
                    if completed == self.numberOfLaps:
                        is_final_lap = True
                elif self.numberOfLaps == 0 and game_data.beforeRaceStart:
                    txt_time=self.time_splitting(int(session_time_left/60000)*60000)
                    time_left_str_len = len(txt_time)
                    self.lbl_session_info_txt.setText(txt_time).setColor(Colors.timer_time_txt(),True)
                elif session_time_left > 0:
                    txt_time=self.time_splitting(session_time_left)
                    time_left_str_len = len(txt_time)
                    self.lbl_session_info_txt.setText(txt_time).setColor(Colors.timer_time_txt(),True)
                else:
                    self.lbl_session_info_txt.setText("00:00").setColor(Colors.timer_time_txt(),True)
                txt_extra_offset=0
                if self.hasExtraLap:
                    txt_extra_offset = self.row_height.value * (time_left_str_len - 5) * 10 / 38

                if self.pitWindowActive:
                    self.lbl_session_title.show()
                    self.lbl_session_title_txt.setText("PIT WINDOW OPEN" + pit_window_remain).setColor(Colors.black_txt())
                    w_offset = (self.row_height.value - 38) * 50 / 38
                    self.lbl_session_info_txt.set(x=114 - self.row_height.value * 122 / 38 - w_offset, animated=True)
                    self.lbl_session_border.set(x=114 - self.row_height.value * 117 / 38 - w_offset, animated=True)
                    self.lbl_session_border_2.set(x=114 + self.row_height.value * 109 / 38 + w_offset, animated=True)
                    self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 122 / 38 + w_offset, animated=True)
                    self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 177 / 38 + w_offset, animated=True)
                    self.lbl_extra_lap_txt.set(x=114 - self.row_height.value * 190 / 38 - txt_extra_offset - w_offset, animated=True)
                    if self.hasExtraLap > 0:
                        self.lbl_left_corner.set(x=114 - self.row_height.value * 262 / 38 - self.corner_width - w_offset)
                        self.lbl_right_corner.set(x=114 + self.row_height.value * 262 / 38 + w_offset)
                        self.lbl_session_info.set(w=self.row_height.value * 524 / 38 + w_offset*2, x=114 - self.row_height.value * 262 / 38 - w_offset)
                    else:
                        self.lbl_left_corner.set(x=114 - self.row_height.value * 216 / 38 - self.corner_width - w_offset)
                        self.lbl_right_corner.set(x=114 + self.row_height.value * 216 / 38 + w_offset)
                        self.lbl_session_info.set(w=self.row_height.value * 432 / 38 + w_offset*2, x=114 - self.row_height.value * 216 / 38 - w_offset)
                    '''
                    right font
                    self.lbl_session_info_txt.set(x=114 - self.row_height.value * 114 / 38, animated=True)
                    self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 114 / 38, animated=True)
                    self.lbl_session_border.set(x=114 - self.row_height.value * 109 / 38, animated=True)
                    self.lbl_session_border_2.set(x=114 + self.row_height.value * 101 / 38, animated=True)
                    self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 175 / 38, animated=True)
                    self.lbl_left_corner.set(x=114 - self.row_height.value * 237 / 38)
                    self.lbl_right_corner.set(x=114 + self.row_height.value * 210 / 38)
                    self.lbl_session_info.set(w=self.row_height.value * 420 / 38, x=114 - self.row_height.value * 210 / 38)
                    '''
                elif self.pitWindowVisibleEnd != 0 and self.pitWindowVisibleEnd < session_time_left:
                    self.lbl_session_title.show()
                    self.lbl_session_title_txt.setText("PIT WINDOW CLOSED").setColor(Colors.black_txt())
                    '''
                    self.lbl_session_info_txt.set(x=114 - self.row_height.value * 120 / 38, animated=True)
                    self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 120 / 38, animated=True)
                    self.lbl_session_border.set(x=114 - self.row_height.value * 115 / 38, animated=True)
                    self.lbl_session_border_2.set(x=114 + self.row_height.value * 107 / 38, animated=True)
                    self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 174 / 38, animated=True)
                    self.lbl_extra_lap_txt.set(x=114 - self.row_height.value * 174 / 38, animated=True)
                    if self.hasExtraLap > 0:
                        self.lbl_left_corner.set(x=114 - self.row_height.value * 243 / 38)
                        self.lbl_right_corner.set(x=114 + self.row_height.value * 216 / 38)
                        self.lbl_session_info.set(w=self.row_height.value * 432 / 38, x=114 - self.row_height.value * 216 / 38)
                    '''
                else:
                    #sim_info.static.reversedGridPositions
                    # Normal race
                    self.lbl_session_title.hide()
                    self.lbl_session_title_txt.setText("RACE").setColor(Colors.timer_title_txt())
                    w_offset = (self.row_height.value - 38) * 6 / 38
                    self.lbl_session_info_txt.set(x=114 - self.row_height.value * 42 / 38 - w_offset, animated=True)
                    self.lbl_session_border.set(x=114 - self.row_height.value * 35 / 38 - w_offset, animated=True)
                    self.lbl_session_border_2.set(x=114 + self.row_height.value * 27 / 38 + w_offset, animated=True)
                    self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 42 / 38 + w_offset, animated=True)
                    self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 97 / 38 + w_offset, animated=True)
                    self.lbl_extra_lap_txt.set(x=114 - self.row_height.value * 110 / 38 - txt_extra_offset - w_offset, animated=True)
                    if self.hasExtraLap > 0:
                        self.lbl_left_corner.set(x=114 - self.row_height.value * 180 / 38 - self.corner_width)
                        self.lbl_right_corner.set(x=114 + self.row_height.value * 180 / 38)
                        self.lbl_session_info.set(w=self.row_height.value * 360 / 38, x=114 - self.row_height.value * 180 / 38)
                    else:
                        self.lbl_left_corner.set(x=114 - self.row_height.value * 140 / 38 - self.corner_width)
                        self.lbl_right_corner.set(x=114 + self.row_height.value * 140 / 38)
                        self.lbl_session_info.set(w=self.row_height.value * 280 / 38, x=114 - self.row_height.value * 140 / 38)

                # Flags
                if race_finished > 0:
                    # Finish
                    self.lbl_session_border.set(background=Colors.timer_finish())
                    self.lbl_session_border_2.set(background=Colors.timer_finish())
                elif game_data.beforeRaceStart:
                    # before race start
                    self.pitWindowVisibleEnd = 0
                    self.pitWindowActive = False
                    self.sessionMaxTime = round(session_time_left, -3)
                    self.lbl_session_border.set(background=Colors.red(),
                                                animated=True)
                    self.lbl_session_border_2.set(background=Colors.red(),
                                                animated=True)
                elif game_data.flag == 2:
                    # Yellow flag
                    self.lbl_session_border.set(background=Colors.timer_border_yellow_flag_bg(),
                                                animated=True)
                    self.lbl_session_border_2.set(background=Colors.timer_border_yellow_flag_bg(),
                                                animated=True)
                elif is_final_lap:
                    # White flag
                    self.lbl_session_border.set(background=Colors.white(bg=True),
                                                animated=True)
                    self.lbl_session_border_2.set(background=Colors.white(bg=True),
                                                animated=True)
                else:
                    # Green flag
                    self.lbl_session_border.set(background=Colors.timer_border_bg(),
                                                animated=True)
                    self.lbl_session_border_2.set(background=Colors.timer_border_bg(),
                                                animated=True)
                if session_time_left != 0:
                    if game_data.beforeRaceStart:
                        self.last_start_time_offset = self.start_time_of_day_original #self.start_time_of_day + (1000)*self.time_multiplier
                    else:
                        self.last_start_time_offset = self.start_time_of_day + (self.sessionMaxTime - session_time_left)*self.time_multiplier
                    time_of_day = self.time_of_day(self.last_start_time_offset)
                    #ac.console(str(self.sessionMaxTime))
                    self.lbl_time_of_day_txt.setText(time_of_day).show()
                    am_pm_offset = ""
                    if len(time_of_day) > 4:
                        am_pm_offset = "  "
                    if self.last_start_time_offset % (24*3600*1000) < 12 * 3600 * 1000:
                        self.lbl_am_pm_txt.setText(am_pm_offset + "AM").show()
                    else:
                        self.lbl_am_pm_txt.setText(am_pm_offset + "PM").show()
                else:
                    time_of_day = self.time_of_day(self.last_start_time_offset)
                    self.lbl_time_of_day_txt.setText(time_of_day).show()
                    am_pm_offset = ""
                    if len(time_of_day) > 4:
                        am_pm_offset = "  "
                    if self.last_start_time_offset % (24*3600*1000) < 12 * 3600 * 1000:
                        self.lbl_am_pm_txt.setText(am_pm_offset + "AM").show()
                    else:
                        self.lbl_am_pm_txt.setText(am_pm_offset + "PM").show()
                #elif self.last_start_time_offset != -1: # Race restart
                #    self.start_time_of_day=self.last_start_time_offset
            elif self.session.value >= 3:
                self.lbl_extra_lap_txt.hide()
                '''
                AC_HOTLAP = 3
                AC_TIME_ATTACK = 4
                AC_DRIFT = 5
                AC_DRAG = 6
                '''
                self.last_start_time_offset = self.start_time_of_day + (
                            self.sessions_duration[self.session.value] - session_time_left) * self.time_multiplier
                time_of_day = self.time_of_day(self.last_start_time_offset)
                self.lbl_time_of_day_txt.setText(time_of_day).show()
                am_pm_offset = ""
                if len(time_of_day) > 4:
                    am_pm_offset = "  "
                if self.last_start_time_offset % (24*3600*1000)  < 12 * 3600 * 1000:
                    self.lbl_am_pm_txt.setText(am_pm_offset + "AM").show()
                else:
                    self.lbl_am_pm_txt.setText(am_pm_offset + "PM").show()
                if session_time_left < 0:
                    session_time_left = 0
                    self.lbl_session_info_txt.setColor(Colors.red(), True)
                else:
                    self.lbl_session_info_txt.setColor(Colors.timer_time_txt(), True)
                self.lbl_session_title.hide()
                self.lbl_session_title_txt.setColor(Colors.timer_time_txt(), animated=True).show()
                self.lbl_session_border.show()
                self.lbl_session_border_2.show()
                self.lbl_left_corner.show()
                self.lbl_right_corner.show()
                self.lbl_session_info.show()
                self.lbl_session_info_txt.setText(self.time_splitting(session_time_left)).show()
                # Green flag
                self.lbl_session_border.set(background=Colors.timer_border_bg(),
                                            animated=True)
                self.lbl_session_border_2.set(background=Colors.timer_border_bg(),
                                              animated=True)
            else:
                self.lbl_left_corner.hide()
                self.lbl_right_corner.hide()
                self.lbl_session_info.hide()
                self.lbl_session_info_txt.hide()
                self.lbl_time_of_day_txt.hide()
                self.lbl_am_pm_txt.hide()
                self.lbl_extra_lap_txt.hide()
                self.lbl_session_title.hide()
                self.lbl_session_title_txt.hide()
                self.lbl_session_border.hide()
                self.lbl_session_border_2.hide()

        elif sim_info_status == 1:
            replay_time_multiplier = sim_info.graphics.replayTimeMultiplier
            self.lbl_extra_lap_txt.hide()
            self.lbl_left_corner.show()
            self.lbl_right_corner.show()
            self.lbl_session_info.show()
            self.lbl_session_info_txt.show()
            self.lbl_time_of_day_txt.show()
            self.lbl_am_pm_txt.show()
            self.lbl_session_title.hide()
            self.lbl_session_border.set(background=Colors.timer_border_bg(),
                                        animated=True).show()
            self.lbl_session_border_2.set(background=Colors.timer_border_bg(),
                                          animated=True).show()
            w_offset = (self.row_height.value - 38) * 6 / 38
            self.lbl_session_info_txt.set(x=114 - self.row_height.value * 50 / 38 - w_offset, animated=True)
            self.lbl_session_border.set(x=114 - self.row_height.value * 43 / 38 - w_offset, animated=True)
            self.lbl_session_border_2.set(x=114 + self.row_height.value * 35 / 38 + w_offset, animated=True)
            self.lbl_time_of_day_txt.set(x=114 + self.row_height.value * 50 / 38 + w_offset, animated=True)
            self.lbl_am_pm_txt.set(x=114 + self.row_height.value * 104 / 38 + w_offset, animated=True)

            self.lbl_left_corner.set(x=114 - self.row_height.value * 168 / 38 - self.corner_width)
            self.lbl_right_corner.set(x=114 + self.row_height.value * 168 / 38)
            self.lbl_session_info.set(w=self.row_height.value * 336 / 38, x=114 - self.row_height.value * 168 / 38)

            self.replay_initialised = True
            self.lbl_session_title_txt.setText("REPLAY")\
                .setColor(rgb([self.replay_rgb, self.replay_rgb, self.replay_rgb]))\
                .show()
            if self.replay_asc and replay_time_multiplier > 0:
                self.replay_rgb += 2
            elif replay_time_multiplier > 0:
                self.replay_rgb -= 2
            if Colors.general_theme == 1:
                if self.replay_rgb <= 2:
                    self.replay_asc = True
                elif self.replay_rgb > 168:
                    self.replay_rgb = 168
                    self.replay_asc = False
            else:
                if self.replay_rgb < 100:
                    self.replay_asc = True
                elif self.replay_rgb >= 246:
                    self.replay_rgb = 246
                    self.replay_asc = False
