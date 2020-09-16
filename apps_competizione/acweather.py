import ac
import acsys
import ctypes
import math
import os
from .util.func import rgb
from .util.classes import Window, Label, Value, POINT, Font, Colors
from .configuration import Configuration


class ACWeather:

    # INITIALIZATION

    def __init__(self):
        self.session=Value()
        self.session.setValue(-1)
        self.cursor=Value()
        self.cursor.setValue(False)
        self.ui_row_height = Value(-1)
        self.font = Value(0)
        self.window = Window(name="ACTV Weather", icon=False, width=325, height=42, texture="")

        ###################### Track condition ######################
        self.lbl_track_bg = Label(self.window.app, "")\
            .set(w=75, h=18, x=0, y=-80,
                 background=rgb([202, 202, 200],bg=True),
                 opacity=1,visible=1)
        self.lbl_track_txt = Label(self.window.app, "TRACK")\
            .set(w=75, h=0, x=0, y=-81,
                 font_size=13, align="center",
                 color=rgb([0, 0, 0]),
                 opacity=0,visible=1)
        self.lbl_track_condition_bg = Label(self.window.app, "")\
            .set(w=75, h=24, x=0, y=18,
                 background=rgb([22, 22, 20],bg=True),
                 opacity=1,visible=1)
        self.lbl_track_condition_txt = Label(self.window.app, "FLOODED")\
            .set(w=75, h=0, x=0, y=-60,
                 font_size=13, align="center",
                 color=rgb([255, 255, 255]),
                 opacity=0,visible=1)

        ###################### Temperature ######################
        self.lbl_temperature_bg = Label(self.window.app, "")\
            .set(w=125, h=18, x=80, y=-80,
                 background=rgb([202, 202, 200],bg=True),
                 opacity=1,visible=1)
        self.lbl_temperature_txt = Label(self.window.app, "TEMPERATURE")\
            .set(w=125, h=0, x=80, y=-81,
                 font_size=13, align="center",
                 color=rgb([0, 0, 0]),
                 opacity=0,visible=1)
        self.lbl_temperature_data_bg = Label(self.window.app, "")\
            .set(w=125, h=24, x=80, y=18,
                 background=rgb([22, 22, 20],bg=True),
                 opacity=1,visible=1)
        self.lbl_temperature_data_txt = Label(self.window.app, "19c Track 20c")\
            .set(w=125, h=0, x=80, y=-60,
                 font_size=13, align="center",
                 color=rgb([255, 255, 255]),
                 opacity=0,visible=1)

        ###################### Wind ######################
        self.lbl_wind_bg = Label(self.window.app, "")\
            .set(w=115, h=18, x=210, y=-80,
                 background=rgb([202, 202, 200],bg=True),
                 opacity=1,visible=1)
        self.lbl_wind_txt = Label(self.window.app, "WIND")\
            .set(w=115, h=0, x=210, y=-81,
                 font_size=13, align="center",
                 color=rgb([0, 0, 0]),
                 opacity=0,visible=1)
        self.lbl_wind_data_bg = Label(self.window.app, "")\
            .set(w=115, h=24, x=210, y=18,
                 background=rgb([22, 22, 20],bg=True),
                 opacity=1,visible=1)
        self.lbl_wind_data_txt = Label(self.window.app, "9 KM/H")\
            .set(w=115, h=0, x=210, y=-60,
                 font_size=13, align="center",
                 color=rgb([255, 255, 255]),
                 opacity=0,visible=1)
        '''
        ac.initFont(0, "ACTVCPBOLD", 0, 0)
        self.lbl_track_txt.setFont("ACTVCPBOLD", 0, 0)
        self.lbl_track_condition_txt.setFont("ACTVCPBOLD", 0, 0)
        self.lbl_temperature_txt.setFont("ACTVCPBOLD", 0, 0)
        self.lbl_temperature_data_txt.setFont("ACTVCPBOLD", 0, 0)
        self.lbl_wind_txt.setFont("ACTVCPBOLD", 0, 0)
        self.lbl_wind_data_txt.setFont("ACTVCPBOLD", 0, 0)
        '''
        self.load_cfg()



    
    # PUBLIC METHODS
    
    #---------------------------------------------------------------------------------------------------------------------------------------------
    def load_cfg(self):
        self.ui_row_height.setValue(Configuration.ui_row_height)
        self.font.setValue(Font.current)
        self.redraw_size()

    def redraw_size(self):
        if self.ui_row_height.hasChanged() or self.font.hasChanged():
            # Fonts
            self.lbl_track_txt.update_font()
            self.lbl_track_condition_txt.update_font()
            self.lbl_temperature_txt.update_font()
            self.lbl_temperature_data_txt.update_font()
            self.lbl_wind_txt.update_font()
            self.lbl_wind_data_txt.update_font()

            # UI
            font_size = Font.get_font_size(self.ui_row_height.value+Font.get_font_offset()) - self.ui_row_height.value * 6/38
            ac.console("font:" + str(font_size))
            row1_height = self.ui_row_height.value * 18/38
            row1_y_offset = -80
            row1_font_offset = -77 - self.ui_row_height.value*4/38
            row1_background=rgb([202, 202, 200], bg=True)
            row1_color=rgb([0, 0, 0])
            row2_height = self.ui_row_height.value * 24/38
            row2_y_offset = -80 + row1_height
            row2_font_offset = -78 + self.ui_row_height.value*18/38
            row2_background=rgb([22, 22, 20], bg=True)
            row2_color=rgb([255, 255, 255])
            ###################### Track condition ######################
            width = self.ui_row_height.value * 75/38
            x_offset=0
            self.lbl_track_bg.set(w=width, h=row1_height, x=x_offset, y=row1_y_offset,
                     background=row1_background, opacity=1)
            self.lbl_track_txt.set(w=width, x=x_offset, y=row1_font_offset,
                     font_size=font_size,
                     color=row1_color)
            self.lbl_track_condition_bg.set(w=width, h=row2_height, x=x_offset, y=row2_y_offset,
                     background=row2_background, opacity=1)
            self.lbl_track_condition_txt.set(w=width, x=x_offset, y=row2_font_offset,
                     font_size=font_size,
                     color=row2_color)

            ###################### Temperature ######################
            width = self.ui_row_height.value * 125/38
            x_offset=self.ui_row_height.value * 80/38
            self.lbl_temperature_bg.set(w=width, h=row1_height, x=x_offset, y=row1_y_offset,
                     background=row1_background, opacity=1)
            self.lbl_temperature_txt.set(w=width, x=x_offset, y=row1_font_offset,
                     font_size=font_size,
                     color=row1_color)
            self.lbl_temperature_data_bg.set(w=width, h=row2_height, x=x_offset, y=row2_y_offset,
                     background=row2_background, opacity=1)
            self.lbl_temperature_data_txt.set(w=width, x=x_offset, y=row2_font_offset,
                     font_size=font_size,
                     color=row2_color)

            ###################### Wind ######################
            width = self.ui_row_height.value * 115/38
            x_offset=self.ui_row_height.value * 210/38
            self.lbl_wind_bg.set(w=width, h=row1_height, x=x_offset, y=row1_y_offset,
                     background=row1_background, opacity=1)
            self.lbl_wind_txt.set(w=width, x=x_offset, y=row1_font_offset,
                     font_size=font_size,
                     color=row1_color)
            self.lbl_wind_data_bg.set(w=width, h=row2_height, x=x_offset, y=row2_y_offset,
                     background=row2_background, opacity=1)
            self.lbl_wind_data_txt.set(w=width, x=x_offset, y=row2_font_offset,
                     font_size=font_size,
                     color=row2_color)

    def manageWindow(self):
        pt=POINT()
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
        if result and pt.x > win_x and pt.x < win_x + self.window.width and pt.y > win_y and pt.y < win_y + self.window.height:   
            self.cursor.setValue(True)
        else:
            self.cursor.setValue(False)

        session_changed=self.session.hasChanged()
        #if session_changed:
        #    self.last_lap_in_pit=0
        
        if self.cursor.hasChanged() or session_changed:
            if self.cursor.value:
                self.window.setBgOpacity(0.4).border(0)
                self.window.showTitle(True)
            else:
                self.window.setBgOpacity(0).border(0)
                self.window.showTitle(False)
                    
    def on_update(self, sim_info):
        self.session.setValue(sim_info.graphics.session)
        self.manageWindow()
        surface_grip = sim_info.graphics.surfaceGrip
        if surface_grip > 0.98:
            self.lbl_track_condition_txt.setText("OPTIMUM")
        elif surface_grip > 0.96:
            self.lbl_track_condition_txt.setText("FAST")
        elif surface_grip > 0.95:
            self.lbl_track_condition_txt.setText("SLOW")#97
        elif surface_grip > 0.92:
            self.lbl_track_condition_txt.setText("GREEN")
        elif surface_grip > 0.87:
            self.lbl_track_condition_txt.setText("OLD")
        else:
            self.lbl_track_condition_txt.setText("DUSTY")

        air_temp = sim_info.physics.airTemp
        road_temp = sim_info.physics.roadTemp

        self.lbl_temperature_data_txt.setText(str(air_temp) + "c Track " + str(road_temp) + "c")

        wind_speed = ac.getWindSpeed()
        wind_direction = ac.getWindDirection()
        self.lbl_wind_data_txt.setText(str(wind_speed) + " KM/H")
