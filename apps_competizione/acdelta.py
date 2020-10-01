import ac
import acsys
import ctypes
import os, threading, json, math
import gzip
import time
from .util.func import rgb
from .util.classes import Window, Label, Value, POINT, Colors, Font, Config, Log, Button, raceGaps
from .configuration import Configuration

        
class ACDelta:
    resetPressed = False
    importPressed = False

    # INITIALIZATION
    def __init__(self): 
        self.window = Window(name="ACTV CP Delta", width=180, height=300)
        self.cursor = Value(False)
        self.session = Value(-1)
        self.performance = Value(0)
        self.spline = Value(0)
        self.currentVehicle = Value(-1)
        self.laptime = Value(0)
        self.TimeLeftUpdate = Value(0)
        self.referenceLap = []
        self.referenceLapTime = Value(0)
        self.lastLapTime = Value(0)
        self.lapCount = 0
        self.performance_display = 0
        self.current_car_class=Value("")
        self.lastLapIsValid = True
        self.best_lap_time=0
        self.visual_timeout = -1
        self.currentLap = []
        self.drivers_info = []
        self.deltaLoaded = False
        self.thread_save = False
        self.last_yellow_flag_end = False
        self.standings = None
        self.rowHeight = Value(-1)
        self.is_multiplayer = ac.getServerIP() != ''
        self.numCars=self.cars_count=ac.getCarsCount()
        self.font_size=16
        self.is_touristenfahrten = False
        track = ac.getTrackName(0)
        config = ac.getTrackConfiguration(0)
        if track.find("ks_nordschleife") >= 0 and config.find("touristenfahrten") >= 0:
            self.is_touristenfahrten = True
        self.current_lap_others = []
        self.spline_others = []
        self.drivers_lap_count = []
        self.reference_lap_time_others = []
        for i in range(self.cars_count):
            self.drivers_lap_count.append(Value(0))
            self.spline_others.append(Value(0))
            self.current_lap_others.append([])
            self.reference_lap_time_others.append([])
        self.last_lap_start = [-1] * self.cars_count

        self.lbl_flag = Label(self.window.app)\
            .set(w=77, h=50,
                 x=1, y=-80,
                 background=Colors.white(bg=True),
                 opacity=1)
        self.lbl_number_bg = Label(self.window.app)\
            .set(w=77, h=0,
                 x=0, y=0,
                 background=Colors.white(bg=True),
                 opacity=1,
                 visible=1)
        self.lbl_number_text = Label(self.window.app, "000")\
            .set(w=77, h=0,
                 x=0, y=0,
                 opacity=0,
                 color=Colors.black_txt(),
                 font_size=26,
                 align="center",
                 visible=1)
        self.lbl_name_bg = Label(self.window.app)\
            .set(w=77, h=0,
                 x=0, y=0,
                 opacity=1,
                 visible=1)
        self.lbl_name_text = Label(self.window.app, "PLY")\
            .set(w=77, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="center",
                 visible=1)
        self.lbl_position_text_shadow = Label(self.window.app, "0")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="right",
                 visible=1)
        self.lbl_position_text = Label(self.window.app, "0")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="right",
                 visible=1)
        self.lbl_position_text_multi_shadow = Label(self.window.app, "0")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="right",
                 visible=1)
        self.lbl_position_text_multi = Label(self.window.app, "0")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="right",
                 visible=1)
        self.lbl_position_total_text_shadow = Label(self.window.app, "/0")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="left",
                 visible=1)
        self.lbl_position_total_text = Label(self.window.app, "/0")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="left",
                 visible=1)
        self.lbl_position_total_text_multi_shadow = Label(self.window.app, "/0")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="left",
                 visible=1)
        self.lbl_position_total_text_multi = Label(self.window.app, "/0")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="left",
                 visible=1)
        self.lbl_delta_bg = Label(self.window.app)\
            .set(w=77, h=0,
                 x=0, y=0,
                 opacity=0,
                 background=Colors.delta_neutral(),
                 visible=1)
        self.lbl_current_time_bg = Label(self.window.app)\
            .set(w=77, h=0,
                 x=0, y=0,
                 opacity=1,
                 visible=1)
        self.lbl_current_time_text = Label(self.window.app, "--:--.---")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="left",
                 visible=1)
        self.lbl_best_time_title_bg = Label(self.window.app)\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=1,
                 visible=1)
        self.lbl_best_title_text = Label(self.window.app, "BEST")\
            .set(w=77, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="left",
                 visible=1)
        self.lbl_best_time_text = Label(self.window.app, "--:--.---")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="right",
                 visible=1)
        self.lbl_last_title_bg = Label(self.window.app)\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=1,
                 visible=1)
        self.lbl_last_title_text = Label(self.window.app, "LAST")\
            .set(w=77, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="left",
                 visible=1)
        self.lbl_last_time_text = Label(self.window.app, "--:--.---")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="right",
                 visible=1)
        self.lbl_prediction_title_bg = Label(self.window.app)\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=1,
                 visible=1)
        self.lbl_prediction_title_text = Label(self.window.app, "PRED")\
            .set(w=77, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="left",
                 visible=1)
        self.lbl_prediction_time_text = Label(self.window.app, "--:--.---")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="right",
                 visible=1)
        self.lbl_delta_text = Label(self.window.app, "+0.00")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 color=Colors.black_txt(),
                 align="center",
                 visible=1)
        self.lbl_laps_completed_text_shadow = Label(self.window.app, "0")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="right",
                 visible=1)
        self.lbl_laps_completed_text = Label(self.window.app, "0")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="right",
                 visible=1)
        self.lbl_laps_text_shadow = Label(self.window.app, "LAPS")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="left",
                 visible=1)
        self.lbl_laps_text = Label(self.window.app, "LAPS")\
            .set(w=0, h=0,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="left",
                 visible=1)

        self.btn_reset = Button(self.window.app, self.on_reset_press)\
            .setPos(90, 68).setSize(120, 20)\
            .setText("Reset saved lap")\
            .setAlign("center")\
            .setBgColor(rgb([255, 12, 12], bg=True))\
            .setVisible(0)

        self.btn_import_from = Button(self.window.app, self.on_import_from_press)\
            .setPos(90, 68).setSize(120, 20)\
            .setText("Import Delta")\
            .setAlign("center")\
            .setBgColor(rgb([255, 12, 12], bg=True))\
            .setVisible(0)
        self.load_cfg()
        
    @staticmethod
    def on_reset_press(a, b):
        ACDelta.resetPressed = True

    @staticmethod
    def on_import_from_press(a, b):
        ACDelta.importPressed = True
                
    # PUBLIC METHODS
    def load_cfg(self):
        self.rowHeight.setValue(Configuration.ui_row_height)
        self.redraw_size()
            
    def redraw_size(self):
        self.lbl_number_text.update_font()
        self.lbl_name_text.update_font()
        self.lbl_position_text.update_font()
        self.lbl_position_text_shadow.update_font()
        self.lbl_position_text_multi.update_font()
        self.lbl_position_text_multi_shadow.update_font()
        self.lbl_position_total_text.update_font()
        self.lbl_position_total_text_shadow.update_font()
        self.lbl_position_total_text_multi.update_font()
        self.lbl_position_total_text_multi_shadow.update_font()
        self.lbl_laps_completed_text.update_font()
        self.lbl_laps_completed_text_shadow.update_font()
        self.lbl_name_bg.set(background=Colors.info_timing_bg(), animated=True,init=True).show()
        self.lbl_current_time_bg.set(background=Colors.delta_time(), animated=True,init=True).show()
        self.lbl_best_time_title_bg.set(background=Colors.delta_laps(), animated=True,init=True).show()
        self.lbl_last_title_bg.set(background=Colors.delta_laps(), animated=True,init=True).show()
        self.lbl_prediction_title_bg.set(background=Colors.delta_laps(), animated=True,init=True).show()
        self.lbl_name_text.set(color=Colors.delta_name_txt(), animated=True,init=True)
        self.lbl_delta_bg.show()
        self.lbl_delta_text.show()
        self.lbl_number_bg.show()
        if self.rowHeight.hasChanged():
            self.font_size = font_size = Font.get_font_size(self.rowHeight.value + Font.get_font_offset())
            self.window.setSize(self.rowHeight.value*392/38,self.rowHeight.value*208/38)
            self.btn_reset.setSize(self.rowHeight.value*160/38, self.rowHeight.value*32/38)\
                .setPos(10, self.rowHeight.value*170/38)\
                .setFontSize(font_size)
            self.btn_import_from.setSize(self.rowHeight.value*160/38, self.rowHeight.value*32/38)\
                .setPos(10, self.rowHeight.value*170/38)\
                .setFontSize(font_size)
            self.lbl_flag.set(w=self.rowHeight.value*392/38,h=self.rowHeight.value*16/38, y=-self.rowHeight.value*22/38)
            #col 1
            self.lbl_number_bg.set(w=self.rowHeight.value * 77/38,
                                   h=self.rowHeight.value,
                                   animated=True)
            self.lbl_number_text.set(w=self.rowHeight.value * 77/38,
                                     y=Font.get_font_x_offset()-3,
                                     font_size=Font.get_font_size(self.rowHeight.value*44/38+Font.get_font_offset()),
                                     animated=True)
            self.lbl_name_bg.set(w=self.rowHeight.value * 77/38,h=self.rowHeight.value * 21/38,y=self.rowHeight.value * 40/38, animated=True)
            self.lbl_name_text.set(w=self.rowHeight.value * 77/38,
                                   y=self.rowHeight.value * 33/38 + Font.get_font_x_offset(),
                                   font_size=font_size,
                                   animated=True)
            self.lbl_position_text.set(x=self.rowHeight.value * 38/38,
                                       y=self.rowHeight.value * 54/38,
                                       font_size=font_size+self.rowHeight.value * 21/38,
                                       animated=True)
            self.lbl_position_text_shadow.set(
                                       x=self.rowHeight.value * 38/38 - 1,
                                       y=self.rowHeight.value * 54/38,
                                       font_size=font_size+self.rowHeight.value * 21/38 + 1,
                                       color=Colors.black_shadow(),
                                       animated=True)
            self.lbl_position_text_multi.set(x=self.rowHeight.value * 38/38,
                                       y=self.rowHeight.value * 107/38,
                                       font_size=font_size+self.rowHeight.value * 3/38,
                                       color=Colors.position_multiclass(),
                                       animated=True)
            self.lbl_position_text_multi_shadow.set(
                                       x=self.rowHeight.value * 38/38 - 1,
                                       y=self.rowHeight.value * 107/38,
                                       font_size=font_size+self.rowHeight.value * 3/38 + 1,
                                       color=Colors.black_shadow(),
                                       animated=True)
            self.lbl_position_total_text.set(x=self.rowHeight.value * 38/38,
                                       y=self.rowHeight.value * 73/38,
                                       font_size=font_size+self.rowHeight.value * 3/38,
                                       animated=True)
            self.lbl_position_total_text_shadow.set(x=self.rowHeight.value * 38/38 - 1,
                                       y=self.rowHeight.value * 73/38,
                                       font_size=font_size+self.rowHeight.value * 3/38 + 1,
                                       color=Colors.black_shadow(),
                                       animated=True)
            self.lbl_position_total_text_multi.set(x=self.rowHeight.value * 38/38,
                                       y=self.rowHeight.value * 116/38,
                                       font_size=font_size-self.rowHeight.value * 5/38,
                                       color=Colors.position_multiclass(),
                                       animated=True)
            self.lbl_position_total_text_multi_shadow.set(x=self.rowHeight.value * 38/38 - 1,
                                       y=self.rowHeight.value * 116/38,
                                       font_size=font_size-self.rowHeight.value * 5/38 + 1,
                                       color=Colors.black_shadow(),
                                       animated=True)
            #col 2
            self.lbl_current_time_bg.set(w=self.rowHeight.value * 240/38,h=self.rowHeight.value * 50/38,x=self.rowHeight.value * 89/38, animated=True)
            self.lbl_best_time_title_bg.set(w=self.rowHeight.value * 194/38,
                                      h=self.rowHeight.value * 25/38,
                                      x=self.rowHeight.value * 87/38,
                                      y=self.rowHeight.value * 53/38,
                                      animated=True)
            self.lbl_last_title_bg.set(w=self.rowHeight.value * 194/38,
                                      h=self.rowHeight.value * 25/38,
                                      x=self.rowHeight.value * 87/38,
                                      y=self.rowHeight.value * 80/38,
                                      animated=True)
            self.lbl_prediction_title_bg.set(w=self.rowHeight.value * 194/38,
                                      h=self.rowHeight.value * 25/38,
                                      x=self.rowHeight.value * 87/38,
                                      y=self.rowHeight.value * 107/38,
                                      animated=True)
            self.lbl_current_time_text.set(x=self.rowHeight.value * 115/38,y=self.rowHeight.value * -12/38 + Font.get_font_x_offset(),
                                           font_size=font_size+self.rowHeight.value * 25/38,
                                           animated=True)#Font.get_font_size(self.rowHeight.value*76/38+Font.get_font_offset())
            self.lbl_best_title_text.set(x=self.rowHeight.value * 99/38,
                                         y=self.rowHeight.value * 50/38 + Font.get_font_x_offset(),
                                         font_size=font_size-self.rowHeight.value * 6/38, animated=True)
            self.lbl_last_title_text.set(x=self.rowHeight.value * 99/38,
                                         y=self.rowHeight.value * 77/38 + Font.get_font_x_offset(),
                                         font_size=font_size-self.rowHeight.value * 6/38, animated=True)
            self.lbl_prediction_title_text.set(x=self.rowHeight.value * 99/38,
                                               y=self.rowHeight.value * 104/38 + Font.get_font_x_offset(),
                                               font_size=font_size-self.rowHeight.value * 6/38, animated=True)
            self.lbl_best_time_text.set(x=self.rowHeight.value * 245/38,
                                        y=self.rowHeight.value * 44/38 + Font.get_font_x_offset(),
                                        font_size=font_size+self.rowHeight.value * 3/38,
                                        animated=True)
            self.lbl_last_time_text.set(x=self.rowHeight.value * 245/38,
                                        y=self.rowHeight.value * 73/38 + Font.get_font_x_offset(),
                                        font_size=font_size+self.rowHeight.value * 3/38,
                                        animated=True)
            self.lbl_prediction_time_text.set(x=self.rowHeight.value * 245/38,
                                              y=self.rowHeight.value * 100/38 + Font.get_font_x_offset(),
                                              font_size=font_size+self.rowHeight.value * 3/38,
                                              animated=True)
            #col 3
            self.lbl_delta_bg.set(x=self.rowHeight.value * 306/38,w=self.rowHeight.value * 86/38,h=self.rowHeight.value * 50/38, animated=True)
            self.lbl_delta_text.set(x=self.rowHeight.value * 306/38,
                                    w=self.rowHeight.value * 86/38,
                                    y=0 + Font.get_font_x_offset(),
                                    font_size=font_size + self.rowHeight.value * 4/38,
                                    animated=True)
            self.lbl_laps_completed_text.set(x=self.rowHeight.value * 375/38,y=self.rowHeight.value * 45/38,
                                             font_size=font_size+self.rowHeight.value * 31/38,
                                             animated=True)
            self.lbl_laps_completed_text_shadow.set(x=self.rowHeight.value * 375/38,y=self.rowHeight.value * 45/38 - 1,
                                             font_size=font_size+self.rowHeight.value * 31/38 + 1,
                                             color=Colors.black_shadow(),
                                             animated=True)
            self.lbl_laps_text.set(x=self.rowHeight.value * 380/38,y=self.rowHeight.value * 82/38,
                                   font_size=font_size - self.rowHeight.value * 6/38,
                                   animated=True)
            self.lbl_laps_text_shadow.set(x=self.rowHeight.value * 380/38 + 1,y=self.rowHeight.value * 82/38,
                                   font_size=font_size - self.rowHeight.value * 6/38 + 1,
                                   color=Colors.black_shadow(),
                                   animated=True)

    def get_delta_file_path(self):
        track_file_path = os.path.join(os.path.expanduser("~"), "Documents", "Assetto Corsa", "plugins", "actv_deltas", "default")
        if not os.path.exists(track_file_path):
            os.makedirs(track_file_path)
        track_file_path += "/" + ac.getTrackName(0)
        if ac.getTrackConfiguration(0) != "":
            track_file_path += "_" + ac.getTrackConfiguration(0)
        track_file_path += "_" + ac.getCarName(0) + ".delta"
        return track_file_path
    
    def save_delta(self):
        reference_lap = list(self.referenceLap)
        reference_lap_time = self.referenceLapTime.value
        if len(reference_lap) > 0:
            try:
                times = []
                for l in reference_lap:
                    times.append((l.sector, l.time))
                data_file = {
                            'lap': reference_lap_time,
                            'times': times, 
                            'track': ac.getTrackName(0), 
                            'config': ac.getTrackConfiguration(0), 
                            'car': ac.getCarName(0), 
                            'user': ac.getDriverName(0)
                            }                  
                file = self.get_delta_file_path()
                with gzip.open(file, 'wt') as outfile:
                    json.dump(data_file, outfile)
            except:
                Log.w("Error tower")
        
    def load_delta(self):
        self.deltaLoaded = True
        file = self.get_delta_file_path()
        if os.path.exists(file):
            try:
                with gzip.open(file, 'rt') as data_file:   
                    data = json.load(data_file)
                    self.referenceLapTime.setValue(data["lap"])                    
                    times = data["times"]
                    self.referenceLap = []
                    for t in times:
                        self.referenceLap.append(raceGaps(t[0], t[1]))
                    ac.console("AC Delta: File loaded:" + str(self.referenceLapTime.value))
            except:
                Log.w("Error tower")  
     
    def get_performance_gap(self, sector, time):
        if self.currentVehicle.value > 0:
            if len(self.reference_lap_time_others[self.currentVehicle.value]) < 10:
                return round(ac.getCarState(self.currentVehicle.value, acsys.CS.PerformanceMeter) * 1000)
            if sector > 0.5:
                reference_lap = reversed(self.reference_lap_time_others[self.currentVehicle.value])
            else:
                reference_lap = self.reference_lap_time_others[self.currentVehicle.value]
            for l in reference_lap:
                if l.sector == sector:
                    return time - l.time
            return False  # do not update
        
        # Car user
        if len(self.referenceLap) < 10:
            return round(ac.getCarState(0, acsys.CS.PerformanceMeter)*1000)
        if sector > 0.5:
            reference_lap = reversed(self.referenceLap)
        else:
            reference_lap = self.referenceLap
        for l in reference_lap:
            if l.sector == sector:
                return time - l.time
        return False  # do not update


    def set_drivers_info(self, info):
        self.drivers_info = info

    def get_driver_number(self):
        if self.currentVehicle.value >= 0:
            for driver in self.drivers_info:
                if driver['id'] == self.currentVehicle.value:  # or fastest...
                    if driver['number'] != "" and driver['number'] != "0":
                        return str(driver['number'])
                    return str(self.currentVehicle.value)
        return str(self.currentVehicle.value)
    
    def time_splitting(self, ms, full="no"):
        s = ms/1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        # d, h = divmod(h,24)
        if full == "yes":
            d = ms % 1000
            if h > 0:
                return "{0}:{1}:{2}.{3}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2), str(int(d)).zfill(3))
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

    def time_splitting_delta(self, ms):
        s = ms/1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        # d, h = divmod(h,24)
        d = ms % 1000 / 10
        if h > 0:
            return "{0}:{1}:{2}.{3}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2), str(int(d)).zfill(2))
        elif m > 0:
            return "{0}:{1}.{2}".format(int(m), str(int(s)).zfill(2), str(int(d)).zfill(2))
        else:
            return "{0}.{1}".format(int(s), str(int(d)).zfill(2))

    def time_splitting_full(self, ms):
        s = ms/1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        # d, h = divmod(h,24)
        d = ms % 1000
        if h > 0:
            return "{0}:{1}:{2}.{3}".format(str(int(h)).zfill(2), str(int(m)).zfill(2), str(int(s)).zfill(2), str(int(d)).zfill(3))
        elif m > 0:
            return "{0}:{1}.{2}".format(str(int(m)).zfill(2), str(int(s)).zfill(2), str(int(d)).zfill(3))
        else:
            return "00:{0}.{1}".format(str(int(s)).zfill(2), str(int(d)).zfill(3))

        
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
        if result and pt.x > win_x and pt.x < win_x + self.window.width and pt.y > win_y and pt.y < win_y + self.window.height:   
            self.cursor.setValue(True)
        else:
            self.cursor.setValue(False)
        session_changed = self.session.hasChanged()
        if session_changed:
            self.visual_timeout = -1
            self.reset_data()
            self.reset_others()
            if not Configuration.save_delta:
                self.referenceLapTime.setValue(0)
                self.referenceLap = []
                self.lastLapTime.setValue(0)
                self.spline.setValue(0)
        if self.cursor.hasChanged() or session_changed:
            if self.cursor.value:
                if self.visual_timeout < 0:
                    self.visual_timeout = time.time() + 6
            self.window.showTitle(False)
        if self.cursor.value and 0 < self.visual_timeout > time.time():
            self.window.setBgOpacity(0.1).border(0)
            if self.currentVehicle.value == 0:
                self.btn_reset.setVisible(1)
                self.btn_import_from.setVisible(0)
            else:
                self.btn_reset.setVisible(0)
                if len(self.reference_lap_time_others[self.currentVehicle.value]) > 800:
                    self.btn_import_from.setVisible(1)
        else:
            self.window.setBgOpacity(0).border(0)
            self.btn_reset.setVisible(0)
            self.btn_import_from.setVisible(0)
            self.visual_timeout = -1

                
    def reset_data(self):
        self.currentLap = []
        self.lastLapIsValid = True
        self.last_yellow_flag_end = False
        self.lapCount = 0

    def reset_others(self):
        for i in range(self.cars_count):
            self.drivers_lap_count[i].setValue(0)
            self.spline_others[i].setValue(0)
            self.current_lap_others[i]=[]
            self.reference_lap_time_others[i]=[]
            self.last_lap_start[i] = -1

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

    def get_race_standings_position(self, identifier):
        if len(self.standings):
            p = [i for i, v in enumerate(self.standings) if v[0] == identifier]
            if len(p) > 0:
                return p[0] + 1
        return ac.getCarRealTimeLeaderboardPosition(identifier) + 1

    def get_race_standings_position_in_class(self, identifier):
        if len(self.standings):
            #filter
            standings = []
            for s in self.standings:
                if s[2]==self.current_car_class.value and ac.isConnected(s[0]) > 0:
                    standings.append((s[0], s[1]))
            p = [i for i, v in enumerate(standings) if v[0] == identifier]
            if len(p) > 0:
                if p[0] + 1 > len(standings):
                    return (len(standings), len(standings))
                return (p[0] + 1, len(standings))
        if self.session.value != 2:
            return (ac.getCarLeaderboardPosition(identifier), self.numCars)
        return (ac.getCarRealTimeLeaderboardPosition(identifier) + 1, self.numCars)

    def get_standings_position(self, identifier):
        if len(self.standings):
            p = [i for i, v in enumerate(self.standings) if v[0] == identifier]
            if len(p) > 0:
                return p[0] + 1
        return ac.getCarLeaderboardPosition(identifier)# + 1

    def get_class_id(self, identifier):
        if len(self.standings):
            for s in self.standings:
                if s[0] == identifier:
                    return s[2]
        return Colors.getClassForCar(ac.getCarName(identifier))

    def animate(self):
        self.lbl_delta_bg.animate()
        self.lbl_number_bg.animate()
        self.lbl_number_text.animate()
        self.lbl_name_bg.animate()
        self.lbl_current_time_bg.animate()
        self.lbl_best_time_title_bg.animate()
        self.lbl_last_title_bg.animate()
        self.lbl_prediction_title_bg.animate()
        self.lbl_name_text.animate()
        self.lbl_flag.animate()
        self.lbl_position_text.animate()
        self.lbl_position_text_shadow.animate()
        self.lbl_position_text_multi.animate()
        self.lbl_position_text_multi_shadow.animate()
        self.lbl_position_total_text.animate()
        self.lbl_position_total_text_shadow.animate()
        self.lbl_position_total_text_multi.animate()
        self.lbl_position_total_text_multi_shadow.animate()
        self.lbl_current_time_text.animate()
        self.lbl_best_title_text.animate()
        self.lbl_last_title_text.animate()
        self.lbl_prediction_title_text.animate()
        self.lbl_best_time_text.animate()
        self.lbl_last_time_text.animate()
        self.lbl_prediction_time_text.animate()
        self.lbl_delta_text.animate()
        self.lbl_laps_completed_text.animate()
        self.lbl_laps_completed_text_shadow.animate()
        self.lbl_laps_text.animate()
        self.lbl_laps_text_shadow.animate()

    def on_update(self, sim_info, standings):
        session_time_left = sim_info.graphics.sessionTimeLeft
        sim_info_status = sim_info.graphics.status
        self.standings = standings
        if self.is_multiplayer:
            self.numCars=0
        for i in range(self.cars_count):
            if ac.isConnected(i) > 0:
                if self.is_multiplayer:
                    self.numCars+=1
                self.drivers_lap_count[i].setValue(ac.getCarState(i, acsys.CS.LapCount))
                if self.last_lap_start[i] == -1 and not math.isinf(session_time_left) and session_time_left != 0:
                    self.last_lap_start[i] = session_time_left
                if self.drivers_lap_count[i].hasChanged() and not math.isinf(session_time_left):
                    self.last_lap_start[i] = session_time_left
                    # if PB save delta
                    if ac.getCarState(i, acsys.CS.LastLap) <= ac.getCarState(i, acsys.CS.BestLap):
                        self.reference_lap_time_others[i]=list(self.current_lap_others[i])
                        if len(self.reference_lap_time_others[i]) > 2000:  # 2laps in
                            how_much = math.floor(len(self.reference_lap_time_others[i]) / 1000)
                            del self.reference_lap_time_others[i][0:math.floor(len(self.reference_lap_time_others[i]) / how_much)]
                    # reset
                    self.current_lap_others[i]=[]
                # Deltas
                self.spline_others[i].setValue(round(ac.getCarState(i, acsys.CS.NormalizedSplinePosition),3))
                if self.is_touristenfahrten and self.spline_others[i].value == 0.953:
                    self.last_lap_start[i] = session_time_left
                    self.current_lap_others[i] = []
                if ac.isCarInPit(i) or ac.isCarInPitline(i):
                    self.current_lap_others[i] = []
                if self.spline_others[i].hasChanged() and not math.isinf(session_time_left):
                    self.current_lap_others[i].append(raceGaps(self.spline_others[i].value, self.last_lap_start[i] - session_time_left))


        if not self.deltaLoaded and Configuration.save_delta:
            thread_load = threading.Thread(target=self.load_delta)
            thread_load.daemon = True      
            thread_load.start() 
        if self.__class__.resetPressed:
            self.referenceLapTime.setValue(0)
            self.referenceLap = []
            self.lastLapTime.setValue(0)
            self.spline.setValue(0)
            self.__class__.resetPressed = False
        if self.__class__.importPressed:
            self.referenceLap = self.reference_lap_time_others[self.currentVehicle.value]
            self.referenceLapTime.setValue(ac.getCarState(self.currentVehicle.value, acsys.CS.BestLap))
            '''
            self.lastLapTime.setValue(0)
            self.spline.setValue(0)
            '''
            self.__class__.importPressed = False
        self.session.setValue(sim_info.graphics.session)
        self.manage_window()
        self.animate()
        self.currentVehicle.setValue(ac.getFocusedCar())
        self.current_car_class.setValue(self.get_class_id(self.currentVehicle.value))
        if self.currentVehicle.hasChanged() or self.current_car_class.hasChanged():
            # number, curtime...
            if Configuration.names == 1:
                self.lbl_name_text.setText(self.format_name_tlc2(ac.getDriverName(self.currentVehicle.value)))
            else:
                self.lbl_name_text.setText(self.format_name_tlc(ac.getDriverName(self.currentVehicle.value)))
            self.lbl_number_text.setText(self.get_driver_number())
            #car_name=ac.getCarName(self.currentVehicle.value)
            self.lbl_number_bg.set(background=Colors.color_for_car_class(self.current_car_class.value),init=True)
            self.lbl_number_text.set(color=Colors.txt_color_for_car_class(self.current_car_class.value),init=True)
            self.performance_display=0
        completed_laps = ac.getCarState(self.currentVehicle.value, acsys.CS.LapCount)
        self.lbl_laps_completed_text.setText(str(completed_laps))
        self.lbl_laps_completed_text_shadow.setText(str(completed_laps))
        if completed_laps > 1:
            self.lbl_laps_text.setText("LAPS")
            self.lbl_laps_text_shadow.setText("LAPS")
        else:
            self.lbl_laps_text.setText("LAP")
            self.lbl_laps_text_shadow.setText("LAP")

        if sim_info_status == 2:  # LIVE
            if math.isinf(session_time_left) or (self.session.value == 2 and sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0):
                self.reset_data()
                self.reset_others()
                if not Configuration.save_delta:
                    self.referenceLapTime.setValue(0)
                    self.referenceLap = []
                    self.lastLapTime.setValue(0)
                    self.spline.setValue(0)
            elif self.currentVehicle.value == 0 and bool(ac.isCarInPitline(0)) or bool(ac.isCarInPit(0)):
                self.reset_data()
            self.spline.setValue(round(ac.getCarState(self.currentVehicle.value, acsys.CS.NormalizedSplinePosition), 3))
            #Current lap time
            if self.currentVehicle.value != 0 and self.last_lap_start[self.currentVehicle.value] != -1 and not math.isinf(session_time_left):
                self.lbl_current_time_text.setText(self.time_splitting_full(self.last_lap_start[self.currentVehicle.value] - session_time_left))
            else:
                self.lbl_current_time_text.setText(self.time_splitting_full(ac.getCarState(self.currentVehicle.value,acsys.CS.LapTime)))
            if self.currentVehicle.value == 0 and not self.lastLapIsValid:
                self.lbl_current_time_text.set(color=Colors.red(), animated=True)
            else:
                self.lbl_current_time_text.set(color=Colors.white(), animated=True)


            if self.currentVehicle.value == 0 and self.lastLapIsValid and sim_info.physics.numberOfTyresOut >= 4:
                self.lastLapIsValid = False
            
            if self.spline.hasChanged():
                if self.currentVehicle.value == 0:
                    self.laptime.setValue(round(ac.getCarState(self.currentVehicle.value, acsys.CS.LapTime), 3))
                    self.lastLapTime.setValue(ac.getCarState(self.currentVehicle.value, acsys.CS.LastLap))
                    gap = self.get_performance_gap(self.spline.value, self.laptime.value)
                    if gap != False:
                        self.performance.setValue(gap)
                    if self.lastLapTime.value > 0:
                        self.lbl_last_time_text.setText(self.time_splitting(self.lastLapTime.value, "yes"))
                    else:
                        self.lbl_last_time_text.setText("--:--.---")
                    # new lap
                    if self.lastLapTime.hasChanged():
                        if (self.referenceLapTime.value == 0 or self.lastLapTime.value < self.referenceLapTime.value) and self.lastLapIsValid and self.lastLapTime.value > 0 and self.lapCount < ac.getCarState(0, acsys.CS.LapCount):
                            #if self.lastLapTime.value > 0:
                            #    self.lbl_last_time_text.setText(self.time_splitting(self.lastLapTime.value, "yes"))
                            #else:
                            #    self.lbl_last_time_text.setText("--:--.---")
                            self.referenceLapTime.setValue(self.lastLapTime.value)
                            self.referenceLap = list(self.currentLap)
                            if len(self.referenceLap) > 2000:  # 2laps in
                                ac.console("too many laps in reference----")
                                ac.log("too many laps in reference----")
                                how_much = math.floor(len(self.referenceLap)/1000)
                                del self.referenceLap[0:math.floor(len(self.referenceLap)/how_much)]
                            if self.currentVehicle.value == 0 and Configuration.save_delta and len(self.referenceLap) > 20:
                                thread_save = threading.Thread(target=self.save_delta)
                                thread_save.daemon = True
                                thread_save.start()

                        self.currentLap = []
                        self.lapCount = ac.getCarState(self.currentVehicle.value, acsys.CS.LapCount)
                        self.lastLapIsValid = True
                    
                    self.currentLap.append(raceGaps(self.spline.value, self.laptime.value))

                    self.best_lap_time = self.referenceLapTime.value
                    self.performance_display = self.performance.value
                else:
                    gap = self.get_performance_gap(self.spline.value, self.last_lap_start[self.currentVehicle.value] - session_time_left)
                    if gap != False:
                        self.performance_display = gap
                    #else:
                    #    self.performance_display = ac.getCarState(self.currentVehicle.value, acsys.CS.PerformanceMeter)
                    self.best_lap_time = ac.getCarState(self.currentVehicle.value, acsys.CS.BestLap)
                    last_lap = ac.getCarState(self.currentVehicle.value, acsys.CS.LastLap)
                    if last_lap > 0:
                        self.lbl_last_time_text.setText(self.time_splitting(last_lap, "yes"))
                    else:
                        self.lbl_last_time_text.setText("--:--.---")

            #update rate
            if not math.isinf(session_time_left):
                self.TimeLeftUpdate.setValue(int(session_time_left / 500))
            if self.TimeLeftUpdate.hasChanged():
                # update graphics

                # position
                if self.session.value != 2:
                    pos = self.get_standings_position(self.currentVehicle.value)
                else:
                    pos = self.get_race_standings_position(self.currentVehicle.value)
                if pos > self.numCars:
                    pos = self.numCars

                if Colors.multiCarsClasses:
                    # Position in class
                    pos_class = self.get_race_standings_position_in_class(self.currentVehicle.value)
                    self.lbl_position_text.setText(str(pos_class[0]))
                    self.lbl_position_text_shadow.setText(str(pos_class[0]))
                    self.lbl_position_total_text.setText("/{0}".format(pos_class[1]))
                    self.lbl_position_total_text_shadow.setText("/{0}".format(pos_class[1]))
                    # Position in overall
                    self.lbl_position_text_multi.setText(str(pos)).show()
                    self.lbl_position_text_multi_shadow.setText(str(pos)).show()
                    self.lbl_position_total_text_multi.setText("/{0}".format(self.numCars)).show()
                    self.lbl_position_total_text_multi_shadow.setText("/{0}".format(self.numCars)).show()
                else:
                    # Position in overall
                    self.lbl_position_text.setText(str(pos))
                    self.lbl_position_text_shadow.setText(str(pos))
                    self.lbl_position_total_text.setText("/{0}".format(self.numCars))
                    self.lbl_position_total_text_shadow.setText("/{0}".format(self.numCars))
                    self.lbl_position_text_multi.hide()
                    self.lbl_position_text_multi_shadow.hide()
                    self.lbl_position_total_text_multi.hide()
                    self.lbl_position_total_text_multi_shadow.hide()

                # flags
                flag = sim_info.graphics.flag
                if flag == 1:
                    # AC_BLUE_FLAG Flag
                    self.lbl_flag.set(background=Colors.blue_flag()).show()
                elif flag == 2:
                    # AC_YELLOW_FLAG Flag
                    self.lbl_flag.set(background=Colors.timer_border_yellow_flag_bg()).show()
                    self.last_yellow_flag_end = session_time_left
                elif flag == 3 or flag == 6:
                    # AC_BLACK_FLAG,AC_PENALTY_FLAG
                    self.lbl_flag.set(background=Colors.black()).show()
                elif flag == 4:
                    # AC_WHITE_FLAG
                    self.lbl_flag.set(background=Colors.white(bg=True)).show()
                elif ac.getCarState(self.currentVehicle.value, acsys.CS.RaceFinished) == 1:#flag == 5
                    # AC_CHECKERED_FLAG
                    self.lbl_flag.set(background=Colors.flag_finish()).show()
                elif self.last_yellow_flag_end != False and self.last_yellow_flag_end - 4000 <= session_time_left:
                    # Green flag
                    self.lbl_flag.set(background=Colors.timer_border_bg()).show()
                else:
                    self.lbl_flag.hide()


                if self.best_lap_time > 0:
                    self.lbl_best_time_text.setText(self.time_splitting(self.best_lap_time, "yes"))
                else:
                    self.lbl_best_time_text.setText("--:--.---")
                if self.best_lap_time > 0:# and self.currentVehicle.value == 0
                    time_prefix = "+"
                    color = Colors.delta_neutral()
                    if self.performance_display >= 10:
                        time_prefix = "+"
                        color = Colors.delta_positive()
                    elif self.performance_display <= -10:
                        time_prefix = "-"
                        color = Colors.delta_negative()
                    self.lbl_delta_bg.set(background=color,animated=True)
                    txt_delta = time_prefix + self.time_splitting_delta(abs(self.performance_display))
                    self.lbl_delta_text.set(font_size=self.font_size + self.rowHeight.value * 3/38 - ((len(txt_delta) - 5) * self.rowHeight.value * 4/38),animated=True).setText(txt_delta)
                    if self.performance_display < self.best_lap_time:
                        self.lbl_prediction_time_text.setText(self.time_splitting(self.best_lap_time + self.performance_display,"yes"))
                    else:
                        self.lbl_prediction_time_text.setText("--:--.---")
                else:
                    self.lbl_delta_bg.set(background=Colors.delta_neutral(),animated=True)
                    self.lbl_delta_text.set(font_size=self.font_size + self.rowHeight.value * 4/38,animated=True).setText("-.--")
                    self.lbl_prediction_time_text.setText("--:--.---")

