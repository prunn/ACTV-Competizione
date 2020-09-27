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
        self.window = Window(name="ACTV Weather", icon=False, width=345, height=42, texture="")

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
                 background=rgb([32, 32, 32], a=0.72),
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
                 background=rgb([0, 0, 0],a=0.8,bg=True),
                 opacity=1,visible=1)
        self.lbl_temperature_track_txt = Label(self.window.app, "Track")\
            .set(w=0, h=0, x=80, y=-60,
                 font_size=13, align="right",
                 color=rgb([255, 255, 255]),
                 opacity=0,visible=1)
        self.lbl_temperature_ambient_txt = Label(self.window.app, "19c")\
            .set(w=0, h=0, x=80, y=-60,
                 font_size=13, align="right",
                 color=rgb([255, 255, 255]),
                 opacity=0,visible=1)
        self.lbl_temperature_ambient_unit_txt = Label(self.window.app, u"\u2103")\
            .set(w=0, h=0, x=80, y=-60,
                 font_size=13, align="left",
                 color=rgb([255, 255, 255]),
                 opacity=0,visible=1)
        self.lbl_temperature_road_txt = Label(self.window.app, "19")\
            .set(w=0, h=0, x=80, y=-60,
                 font_size=13, align="right",
                 color=rgb([255, 255, 255]),
                 opacity=0,visible=1)
        self.lbl_temperature_road_unit_txt = Label(self.window.app, u"\u2103")\
            .set(w=0, h=0, x=80, y=-60,
                 font_size=13, align="left",
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
        self.lbl_wind_data_txt = Label(self.window.app, "9")\
            .set(w=0, h=0, x=210, y=-60,
                 font_size=13, align="right",
                 color=rgb([255, 255, 255]),
                 opacity=0,visible=1)
        self.lbl_wind_unit_txt = Label(self.window.app, "KM/H")\
            .set(w=0, h=0, x=210, y=-60,
                 font_size=13, align="left",
                 color=rgb([255, 255, 255]),
                 opacity=0,visible=1)
        self.lbl_wind_direction_img = Label(self.window.app, "") \
            .set(w=26, h=13, x=86, y=-60,
                 background=rgb([0, 0, 0], a=0, bg=True, t='apps/python/actv_competizione/img/winddir.png'),
                 opacity=0, visible=1)
        self.lbl_wind_direction_txt = Label(self.window.app, u"\u2193")\
            .set(w=0, h=0, x=210, y=-60,
                 font_size=13, align="left",
                 color=rgb([255, 255, 255]),
                 opacity=0,visible=1)
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
            self.lbl_temperature_road_txt.update_font()
            self.lbl_temperature_ambient_txt.update_font()
            self.lbl_wind_txt.update_font()
            self.lbl_wind_data_txt.update_font()
            #self.lbl_wind_direction_txt.setFont('Segoe UI',0,1)

            # UI
            font_size = Font.get_font_size(self.ui_row_height.value+Font.get_font_offset()) - self.ui_row_height.value * 6/38
            row2_font_size = Font.get_font_size(self.ui_row_height.value+Font.get_font_offset()) - self.ui_row_height.value * 3/38

            row1_height = self.ui_row_height.value * 18/38
            row1_y_offset = -80
            row1_font_offset = -76 - self.ui_row_height.value*4/38
            row1_background=rgb([202, 202, 200], bg=True)
            row1_color=rgb([0, 0, 0])
            row2_height = self.ui_row_height.value * 24/38
            row2_y_offset = -80 + row1_height
            row2_font_offset = -78 + self.ui_row_height.value*17/38
            row2_color=rgb([255, 255, 255])
            ###################### Track condition ######################
            width = self.ui_row_height.value * 135/38
            x_offset=0
            self.lbl_track_bg.set(w=width, h=row1_height, x=x_offset, y=row1_y_offset,
                     background=row1_background, opacity=1)
            self.lbl_track_txt.set(w=width, x=x_offset, y=row1_font_offset,
                     font_size=font_size,
                     color=row1_color)
            self.lbl_track_condition_bg.set(w=width, h=row2_height, x=x_offset, y=row2_y_offset,
                     background=Colors.weather_data_bg())
            self.lbl_track_condition_txt.set(w=width, x=x_offset, y=row2_font_offset,
                     font_size=row2_font_size,
                     color=row2_color)

            ###################### Temperature ######################
            width = self.ui_row_height.value * 125/38
            x_offset=self.ui_row_height.value * 140/38
            self.lbl_temperature_bg.set(w=width, h=row1_height, x=x_offset, y=row1_y_offset,
                     background=row1_background, opacity=1)
            self.lbl_temperature_txt.set(w=width, x=x_offset, y=row1_font_offset,
                     font_size=font_size,
                     color=row1_color)
            self.lbl_temperature_data_bg.set(w=width, h=row2_height, x=x_offset, y=row2_y_offset,
                     background=Colors.weather_data_bg())
            x_offset = self.ui_row_height.value * 166 / 38
            self.lbl_temperature_ambient_txt.set(x=x_offset, y=row2_font_offset, font_size=row2_font_size, color=row2_color)
            x_offset = self.ui_row_height.value * 167 / 38
            self.lbl_temperature_ambient_unit_txt.set(x=x_offset, y=row2_font_offset + self.ui_row_height.value * 2/38, font_size=row2_font_size - self.ui_row_height.value * 3/38, color=row2_color)

            x_offset = self.ui_row_height.value * 220 / 38
            self.lbl_temperature_track_txt.set(x=x_offset, y=row2_font_offset + self.ui_row_height.value * 2 / 38,
                                              font_size=row2_font_size - self.ui_row_height.value * 3 / 38,
                                              color=row2_color)
            x_offset = self.ui_row_height.value * 239 / 38
            self.lbl_temperature_road_txt.set(x=x_offset, y=row2_font_offset,
                                              font_size=row2_font_size,
                                              color=row2_color)
            x_offset = self.ui_row_height.value * 240 / 38
            self.lbl_temperature_road_unit_txt.set(x=x_offset, y=row2_font_offset + self.ui_row_height.value * 2/38,
                                                   font_size=row2_font_size - self.ui_row_height.value * 3/38,
                                                   color=row2_color)

            ###################### Wind ######################
            width = self.ui_row_height.value * 115/38
            x_offset=self.ui_row_height.value * 270/38
            self.lbl_wind_bg.set(w=width, h=row1_height, x=x_offset, y=row1_y_offset,
                     background=row1_background, opacity=1)
            self.lbl_wind_txt.set(w=width, x=x_offset, y=row1_font_offset,
                     font_size=font_size,
                     color=row1_color)
            self.lbl_wind_data_bg.set(w=width, h=row2_height, x=x_offset, y=row2_y_offset,
                     background=Colors.weather_data_bg())

            x_offset=self.ui_row_height.value * 343/38
            self.lbl_wind_data_txt.set(x=x_offset, y=row2_font_offset,
                     font_size=row2_font_size,
                     color=row2_color)#w=width,
            x_offset=self.ui_row_height.value * 344/38
            self.lbl_wind_unit_txt.set(x=x_offset, y=row2_font_offset + self.ui_row_height.value * 2/38,
                     font_size=row2_font_size - self.ui_row_height.value * 3/38,
                     color=row2_color)#w=width,
            self.lbl_wind_direction_img.set(w=self.ui_row_height.value * 26/38 , h=self.ui_row_height.value * 13/38,
                                            x=self.ui_row_height.value * 275/38, y=row2_font_offset + self.ui_row_height.value*5/38)
            self.lbl_wind_direction_txt.set(x=self.ui_row_height.value * 307/38, y=row2_font_offset,
                                            font_size=row2_font_size,
                                            color=row2_color)# - self.ui_row_height.value * 1/38

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
            self.lbl_track_condition_txt.setText("OPTIMUM (" + str(round(surface_grip*100))+"%)")
        elif surface_grip > 0.96:
            self.lbl_track_condition_txt.setText("FAST (" + str(round(surface_grip*100))+"%)")
        elif surface_grip > 0.95:
            self.lbl_track_condition_txt.setText("SLOW (" + str(round(surface_grip*100))+"%)")#97
        elif surface_grip > 0.92:
            self.lbl_track_condition_txt.setText("GREEN (" + str(round(surface_grip*100))+"%)")
        elif surface_grip > 0.87:
            self.lbl_track_condition_txt.setText("OLD (" + str(round(surface_grip*100))+"%)")
        else:
            self.lbl_track_condition_txt.setText("DUSTY (" + str(round(surface_grip*100))+"%)")

        air_temp = sim_info.physics.airTemp
        road_temp = str(round(sim_info.physics.roadTemp))

        self.lbl_temperature_ambient_txt.setText(str(round(air_temp)))
        self.lbl_temperature_road_txt.setText(road_temp)
        x_offset = self.ui_row_height.value * (222 - len(road_temp)) / 38
        self.lbl_temperature_track_txt.set(x=x_offset)

        wind_speed = ac.getWindSpeed()
        wind_direction = ac.getWindDirection()
        self.lbl_wind_data_txt.setText(str(wind_speed))

        if 22 < wind_direction <= 68:
            self.lbl_wind_direction_txt.setText(u"\u2197") # North East 'NORTH EAST ARROW' (U+2197)
        elif 68 < wind_direction <= 112:
            self.lbl_wind_direction_txt.setText(u"\u2192") # East 'RIGHTWARDS ARROW' (U+2192)
        elif 112 < wind_direction <= 158:
            self.lbl_wind_direction_txt.setText(u"\u2198") # South East 'SOUTH EAST ARROW' (U+2198)
        elif 158 < wind_direction <= 202:
            self.lbl_wind_direction_txt.setText(u"\u2193") # South 'DOWNWARDS ARROW' (U+2193)
        elif 202 < wind_direction <= 248:
            self.lbl_wind_direction_txt.setText(u"\u2199") # South West 'SOUTH WEST ARROW' (U+2199)
        elif 248 < wind_direction <= 293:
            self.lbl_wind_direction_txt.setText(u"\u2190") # West 'LEFTWARDS ARROW' (U+2190)
        elif 293 < wind_direction <= 338:
            self.lbl_wind_direction_txt.setText(u"\u2196") # North West 'NORTH WEST ARROW' (U+2196)
        else:
            self.lbl_wind_direction_txt.setText(u"\u2191") # North 'UPWARDS ARROW' (U+2191)