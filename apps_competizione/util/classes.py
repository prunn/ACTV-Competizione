import sys, traceback
import ac
import math
import configparser
import ctypes
import os.path
import json
import functools
from apps_competizione.util.func import rgb
from html.parser import HTMLParser
import winreg


class Window:
    # INITIALIZATION

    def __init__(self, name="defaultAppWindow", title="", icon=False, width=100, height=100, scale=1, texture=""):
        # local variables
        self.name = name
        self.title = title
        self.width = width
        self.height = height
        self.scale = scale
        self.x = 0
        self.y = 0
        self.last_x = 0
        self.last_y = 0
        self.is_attached = False
        self.attached_l = -1
        self.attached_r = -1

        # creating the app window
        self.app = ac.newApp(self.name)

        # default settings
        ac.drawBorder(self.app, 0)
        ac.setBackgroundOpacity(self.app, 0)
        if icon is False:
            ac.setIconPosition(self.app, 0, -10000)

        # applying settings
        ac.setTitle(self.app, "")
        if texture != "":
            ac.setBackgroundTexture(self.app, texture)
        ac.setSize(self.app, math.floor(self.width * scale), math.floor(self.height * scale))

    # PUBLIC METHODS

    def onRenderCallback(self, func):
        ac.addRenderCallback(self.app, func)
        return self

    def setSize(self, width, height):
        self.width = width
        self.height = height
        ac.setSize(self.app, math.floor(self.width), math.floor(self.height))

    def setBgOpacity(self, alpha):
        ac.setBackgroundOpacity(self.app, alpha)
        return self

    def showTitle(self, show):
        if show:
            ac.setTitle(self.app, self.name)
        else:
            ac.setTitle(self.app, "")
        return self

    def border(self, value):
        ac.drawBorder(self.app, value)
        return self

    def setBgTexture(self, texture):
        ac.setBackgroundTexture(self.app, texture)
        return self

    def setPos(self, x, y):
        self.x = x
        self.y = y
        ac.setPosition(self.app, self.x, self.y)
        return self

    def setLastPos(self):
        self.x = self.last_x
        self.y = self.last_y
        ac.setPosition(self.app, self.last_x, self.last_y)
        return self

    def getPos(self):
        self.x, self.y = ac.getPosition(self.app)
        return self


# -#####################################################################################################################################-#
class Value:
    def __init__(self, value=0):
        self.value = value
        self.old = value
        self.changed = False

    def setValue(self, value):
        if self.value != value:
            self.old = self.value
            self.value = value
            self.changed = True

    def hasChanged(self):
        if self.changed:
            self.changed = False
            return True
        return False


class raceGaps:
    def __init__(self, sector, time):
        self.sector = sector
        self.time = time


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_ulong), ("y", ctypes.c_ulong)]


class Colors:
    app_path = 'apps/python/actv_competizione/'
    general_theme = 1  # 0 : Dark
    theme_red = -1
    theme_green = -1
    theme_blue = -1
    theme_highlight = -1
    cars_classes_current = -1
    dataCarsClasses = []
    car_classes_list = []
    carsClassesLoaded = False
    multiCarsClasses = False
    is_addon_flag = False
    theme_files = []
    car_classes = {
        'default_bg': rgb([255, 255, 255]), # White
        'default_txt': rgb([0, 0, 0]),

        'lmp1_title': 'LMP1',
        'lmp1_bg': rgb([220, 0, 0]), # Red
        'lmp1_txt': rgb([255, 255, 255]),

        'lmp2_title': 'LMP2',
        'lmp2_bg': rgb([0, 80, 150]), # Blue
        'lmp2_txt': rgb([255, 255, 255]),

        'lmp3_title': 'LMP3',
        'lmp3_bg': rgb([102, 51, 102]), # Purple
        'lmp3_txt': rgb([255, 255, 255]),

        'proto c_title': 'PROTO C',
        'proto c_bg': rgb([238, 234, 51]), # Yellow
        'proto c_txt': rgb([0, 0, 0]),

        'gte-gt3_title': 'GT3-GTE',
        'gte-gt3_bg': rgb([0, 150, 54]), # Green
        'gte-gt3_txt': rgb([0, 0, 0]),

        'gt4_title': 'GT4',
        'gt4_bg': rgb([252, 139, 1]), # Orange
        'gt4_txt': rgb([255, 255, 255]),

        'suv_title': 'SUV',
        'suv_bg': rgb([242, 65, 225]), # Bad Pink
        'suv_txt': rgb([0, 0, 0]),

        'hypercars_title': 'HYP',
        'hypercars_bg': rgb([227, 90, 90]), # Light red
        'hypercars_txt': rgb([0, 0, 0]),

        'hypercars r_title': 'HYP R',
        'hypercars r_bg': rgb([127, 215, 127]), # Light green
        'hypercars r_txt': rgb([0, 0, 0]),

        'supercars_title': 'SUPER',
        'supercars_bg': rgb([21, 141, 255]), # Dark blue
        'supercars_txt': rgb([0, 0, 0]),

        'sportscars_title': 'SPORTS',
        'sportscars_bg': rgb([101, 101, 101]), # Grey
        'sportscars_txt': rgb([255, 255, 255]),

        'vintage supercars_title': 'V SUPER',
        'vintage supercars_bg': rgb([65, 200, 220]), # Light blue
        'vintage supercars_txt': rgb([0, 0, 0]),

        'vintage gt_title': 'V GT',
        'vintage gt_bg': rgb([212, 167, 206]), # Pink
        'vintage gt_txt': rgb([0, 0, 0]),

        'vintage touring_title': 'V TOURING',
        'vintage touring_bg': rgb([236, 205, 96]), # Dark yellow
        'vintage touring_txt': rgb([0, 0, 0]),

        'small sports_title': 'SMALL',
        'small sports_bg': rgb([0, 0, 0]), # Black
        'small sports_txt': rgb([255, 255, 255]),

        '90s touring_title': '90S T',
        '90s touring_bg': rgb([96, 169, 184]), # Blue-Green
        '90s touring_txt': rgb([0, 0, 0]),

    }
    current_theme = {
        'tower_time_odd_txt': rgb([0, 0, 0]),
        'tower_time_highlight_txt': rgb([0, 0, 0]),
        'tower_time_qualification_highlight_txt': rgb([0, 0, 0]),
        'tower_time_retired_txt': rgb([0, 0, 0]),
        'tower_time_best_lap_txt': rgb([0, 0, 0]),
        'tower_time_last_lap_txt': rgb([0, 0, 0]),
        'tower_time_place_gain_txt': rgb([0, 0, 0]),
        'tower_time_place_lost_txt': rgb([0, 0, 0]),
        'tower_time_pit_txt': rgb([0, 0, 0]),
        'tower_time_highlight_odd_bg': rgb([0, 0, 0]),
        'tower_time_odd_bg': rgb([0, 0, 0]),
        'weather_header_bg': rgb([0, 0, 0]),
        'weather_header_txt': rgb([0, 0, 0]),
        'weather_data_bg': rgb([0, 0, 0]),
        'weather_data_txt': rgb([0, 0, 0]),
        'tower_time_retired_bg': rgb([0, 0, 0]),
        'tower_time_green_txt': rgb([0, 0, 0]),
        'tower_driver_odd_bg': rgb([0, 0, 0]),
        'tower_driver_odd_txt': rgb([0, 0, 0]),
        'tower_driver_highlight_odd_bg': rgb([0, 0, 0]),
        'tower_driver_highlight_odd_txt': rgb([0, 0, 0]),
        'tower_driver_stopped_txt': rgb([0, 0, 0]),
        'tower_driver_retired_bg': rgb([0, 0, 0]),
        'tower_driver_retired_txt': rgb([0, 0, 0]),
        'tower_position_odd_bg': rgb([0, 0, 0]),
        'tower_position_fastest_bg': rgb([0, 0, 0]),
        'tower_position_odd_txt': rgb([0, 0, 0]),
        'tower_position_highlight_odd_bg': rgb([0, 0, 0]),
        'tower_position_highlight_odd_txt': rgb([0, 0, 0]),
        'tower_position_retired_txt': rgb([0, 0, 0]),
        'tower_position_retired_bg': rgb([0, 0, 0]),
        'tower_pit_txt': rgb([0, 0, 0]),
        'tower_tires_txt': rgb([0, 0, 0]),
        'tower_tires_bg': rgb([0, 0, 0]),
        'tower_pit_highlight_txt': rgb([0, 0, 0]),
        'tower_stint_lap_invalid_txt': rgb([0, 0, 0]),
        'tower_p2p_txt': rgb([0, 0, 0]),
        'tower_p2p_cooling': rgb([0, 0, 0]),
        'tower_p2p_active': rgb([0, 0, 0]),
        'tower_border_default_bg': rgb([0, 0, 0]),
        'tower_border_retired_bg': rgb([0, 0, 0]),
        'tower_mode_title_bg': rgb([0, 0, 0]),
        'tower_mode_title_txt': rgb([0, 0, 0]),
        'tower_stint_title_bg': rgb([0, 0, 0]),
        'tower_stint_title_txt': rgb([0, 0, 0]),
        'tower_stint_tire_bg': rgb([0, 0, 0]),
        'tower_stint_tire_txt': rgb([0, 0, 0]),
        'tower_class_bg': rgb([0, 0, 0]),
        'tower_class_txt': rgb([0, 0, 0]),
        'info_driver_bg': rgb([0, 0, 0]),
        'info_driver_txt': rgb([0, 0, 0]),
        'info_driver_single_bg': rgb([0, 0, 0]),
        'info_driver_single_txt': rgb([0, 0, 0]),
        'info_split_txt': rgb([255, 255, 255]),
        'info_split_positive_txt': rgb([255, 255, 255]),
        'info_split_negative_txt': rgb([255, 255, 255]),
        'delta_name_bg': rgb([0, 0, 0]),
        'delta_name_txt': rgb([0, 0, 0]),
        'info_timing_bg': rgb([0, 0, 0]),
        'info_timing_txt': rgb([0, 0, 0]),
        'info_position_bg': rgb([0, 0, 0]),
        'info_position_txt': rgb([0, 0, 0]),
        'info_fastest_time_txt': rgb([0, 0, 0]),
        'info_border_default_bg': rgb([0, 0, 0]),
        'info_car_class_bg': rgb([0, 0, 0]),
        'info_car_class_txt': rgb([0, 0, 0]),
        'info_sector_title_bg': rgb([0, 0, 0]),
        'info_sector_title_txt': rgb([0, 0, 0]),
        'timer_title_bg': rgb([0, 0, 0]),
        'timer_title_txt': rgb([0, 0, 0]),
        'timer_title_yellow_flag_bg': rgb([0, 0, 0]),
        'timer_title_yellow_flag_txt': rgb([0, 0, 0]),
        'timer_time_bg': rgb([0, 0, 0]),
        'timer_time_txt': rgb([0, 0, 0]),
        'timer_time_yellow_flag_bg': rgb([0, 0, 0]),
        'timer_time_yellow_flag_txt': rgb([0, 0, 0]),
        'tower_driver_blue_txt': rgb([2, 188, 255]),
        'tower_driver_lap_up_txt': rgb([252, 139, 7]),
        'timer_pit_window_bg': rgb([0, 0, 0]),
        'timer_pit_window_txt': rgb([0, 0, 0]),
        'timer_pit_window_open_txt': rgb([0, 0, 0]),
        'timer_pit_window_done_txt': rgb([0, 0, 0]),
        'timer_pit_window_close_txt': rgb([0, 0, 0]),
        'timer_border_bg': rgb([0, 0, 0]),
        'timer_border_yellow_flag_bg': rgb([0, 0, 0]),
        'speedtrap_title_bg': rgb([0, 0, 0]),
        'speedtrap_title_txt': rgb([0, 0, 0]),
        'speedtrap_speed_bg': rgb([0, 0, 0]),
        'speedtrap_speed_txt': rgb([0, 0, 0]),
        'speedtrap_border_bg': rgb([0, 0, 0]),
        'logo_bg': rgb([0, 0, 0]),
        'info_split_best_bg': rgb([126, 32, 164], a=1),
        'info_split_personal_bg': rgb([42, 142, 42], a=1),
        'info_split_slow_bg': rgb([223, 142, 36], a=1),
    }

    @staticmethod
    def theme(bg=False, reload=False, a=1):
        #if reload and Colors.general_theme == 0:
        #    Colors.export_theme_values()
        # get theme color
        if reload or Colors.theme_red < 0 or Colors.theme_green < 0 or Colors.theme_blue < 0:
            if reload and Colors.general_theme > 0:
                Colors.load_theme_values()

            cfg = Config(Colors.app_path, "config.ini")
            Colors.theme_red = cfg.get("SETTINGS", "red", "int")
            if Colors.theme_red < 0 or Colors.theme_red > 255:
                Colors.theme_red = 224
            Colors.theme_green = cfg.get("SETTINGS", "green", "int")
            if Colors.theme_green < 0 or Colors.theme_green > 255:
                Colors.theme_green = 0
            Colors.theme_blue = cfg.get("SETTINGS", "blue", "int")
            if Colors.theme_blue < 0 or Colors.theme_blue > 255:
                Colors.theme_blue = 0
        # return rgb([40, 152, 211], bg = bg)
        return rgb([Colors.theme_red, Colors.theme_green, Colors.theme_blue], bg=bg, a=a)

    @staticmethod
    def highlight(bg=False, reload=False):
        # get theme color
        if reload or Colors.theme_highlight < 0:
            cfg = Config(Colors.app_path, "config.ini")
            Colors.theme_highlight = cfg.get("SETTINGS", "tower_highlight", "int")
            if Colors.theme_highlight != 1:
                Colors.theme_highlight = 0
        if Colors.theme_highlight == 1:
            return Colors.green(bg=bg)
        return Colors.red(bg=bg)

    @staticmethod
    def loadCarClasses():
        Colors.dataCarsClasses = []
        Colors.car_classes_list = []
        Colors.multiCarsClasses = False
        loaded_cars = []
        last_class=-1
        for i in range(ac.getCarsCount()):
            car_name = ac.getCarName(i)
            if car_name not in loaded_cars:
                loaded_cars.append(car_name)
                class_found=False
                #check car_classes first
                for index, c in Colors.car_classes.items():
                    if index.find("_cars") >= 0:
                        if car_name in c:
                            cur_class = index.replace("_cars","")
                            driver_index = index.replace("_cars", "_drivers")
                            if not driver_index in Colors.car_classes.keys():
                                Colors.dataCarsClasses.append({"c": car_name, "t": cur_class})
                                if last_class != -1 and last_class != cur_class:
                                    Colors.multiCarsClasses = True
                                last_class = cur_class
                                if not last_class in Colors.car_classes_list:
                                    Colors.car_classes_list.append(last_class)
                                class_found = True
                                break
                if not class_found:
                    file_path = "content/cars/" + car_name + "/ui/ui_car.json"
                    try:
                        if os.path.exists(file_path):
                            with open(file_path) as data_file:
                                d = data_file.read().replace('\r', '').replace('\n', '').replace('\t', '')
                                data = json.loads(d)
                                for t in data["tags"]:
                                    if t[0] == "#":
                                        Colors.dataCarsClasses.append({"c": car_name, "t": t[1:].lower()})
                                        if last_class != -1 and last_class != t[1:].lower():
                                            Colors.multiCarsClasses = True
                                        last_class = t[1:].lower()
                                        if not last_class in Colors.car_classes_list:
                                            Colors.car_classes_list.append(last_class)
                    except:
                        Log.w("Error color:" + file_path)
        Colors.carsClassesLoaded = True

    @staticmethod
    def getClassForCar(car,steam_id=None):
        if not Colors.carsClassesLoaded:
            Colors.loadCarClasses()
        #Driver class
        if steam_id is not None:
            for index, c in Colors.car_classes.items():
                if index.find("_drivers") >= 0 and steam_id in c:
                    # drivers + cars
                    car_index = index.replace("_drivers", "_cars")
                    if (not car_index in Colors.car_classes.keys()) or (car_index in Colors.car_classes.keys() and car in Colors.car_classes[car_index]):
                        Colors.multiCarsClasses=True #?? how to know for sure?
                        cur_class = index.replace("_drivers", "")
                        if not cur_class in Colors.car_classes_list:
                            Colors.car_classes_list.append(cur_class)
                        return cur_class

        for c in Colors.dataCarsClasses:
            if c["c"] == car:
                return c["t"]
        return ""

    # ------------Theme engine -----------
    @staticmethod
    def load_themes():
        Colors.theme_files = []
        theme_files = [os.path.join(root, name)
                       for root, dirs, files in os.walk(Colors.app_path + "themes/")
                       for name in files
                       if name.endswith(".ini")]
        if len(theme_files):
            for t in theme_files:
                cfg = Config(t, "")
                name = cfg.get('MAIN', 'title', 'string')
                if name == -1:
                    name = ""
                Colors.theme_files.append({"file": t, "name": name})

    @staticmethod
    def load_theme_values():
        if Colors.general_theme > 0 and len(Colors.theme_files):
            cfg = Config(Colors.theme_files[Colors.general_theme - 1]['file'], "")
            for key in Colors.current_theme:
                value = cfg.get('THEME', key, 'string')
                if value != -1:
                    # Translate value to rgba
                    Colors.current_theme[key] = Colors.txt_to_rgba(value)

            # Fallback for older themes - new, old
            fallbacks = [["tower_time_highlight_odd_bg", "tower_driver_highlight_odd_bg"],
                         ["tower_time_odd_bg", "tower_driver_odd_bg"],
                         ["tower_border_retired_bg", "tower_border_default_bg"],
                         ["tower_time_retired_bg", "tower_driver_retired_bg"]]
            for f in fallbacks:
                value = cfg.get('THEME', f[0], 'string')
                if value == -1:
                    Colors.current_theme[f[0]] = Colors.current_theme[f[1]]

        # Car classes
        if os.path.exists(Colors.app_path + 'car_classes.ini'):
            cfg = Config(Colors.app_path,'car_classes.ini')
            cfg_sections = cfg.sections()
            for s in cfg_sections:
                index=s.lower()
                value = cfg.get(s,'bg','string')
                if value != -1 and value != "":
                    Colors.car_classes[index+'_bg'] = Colors.txt_to_rgba(value) # Translate value to rgba
                value = cfg.get(s,'txt','string')
                if value != -1 and value != "":
                    Colors.car_classes[index+'_txt'] = Colors.txt_to_rgba(value) # Translate value to rgba
                value = cfg.get(s,'title','string')
                if value != -1 and value != "":
                    Colors.car_classes[index+'_title'] = value
                value = cfg.get(s,'cars','string')
                if value != -1 and value != "":
                    if value.find(",") > 0:
                        array_values = value.split(',')
                    else:
                        array_values = [value]
                    Colors.car_classes[index+'_cars'] = array_values
                value = cfg.get(s,'drivers','string')
                if value != -1 and value != "":
                    if value.find(",") > 0:
                        array_values = value.split(',')
                    else:
                        array_values = [value]
                    Colors.car_classes[index+'_drivers'] = array_values

    @staticmethod
    def export_theme_values():
        ac.log('----------Start export theme------------')
        ac.log('[THEME]')
        for key in Colors.current_theme:
            try:
                val = getattr(Colors, key)()
                if len(val) == 4:
                    ac.log(str(key) + "=" + str(round(val[0]*255)) + "," + str(round(val[1]*255)) + "," + str(round(val[2]*255)) + "," + str(val[3]))
                else:
                    ac.log(str(key) + "=" + str(round(val[0]*255)) + "," + str(round(val[1]*255)) + "," + str(round(val[2]*255)) + ",1")
            except:
                ac.log(str(key) + "=")


    @staticmethod
    def get_color_for_key(key):
        if key in Colors.current_theme:
            if Colors.current_theme[key][0] == "t":
                return Colors.theme()
            return Colors.current_theme[key]
        return rgb([0, 0, 0])

    @staticmethod
    def txt_to_rgba(value):
        value_type = value.find(",")
        if value_type > 0:
            array_values = value.split(',')
            # RGB or RGBA split
            if len(array_values) == 3:
                #Theme
                if array_values[0] == "t" and array_values[1] == "t" and array_values[2] == "t":
                    return "t", "t", "t"
                #RGB
                return rgb([int(array_values[0]),
                            int(array_values[1]),
                            int(array_values[2])])
            if len(array_values) == 4:
                #Theme
                if array_values[0] == "t" and array_values[1] == "t" and array_values[2] == "t":
                    return "t", "t", "t", array_values[3]
                #RGBA
                return rgb([int(array_values[0]),
                            int(array_values[1]),
                            int(array_values[2])],
                           a=float(array_values[3]))
            if len(array_values) == 5:
                # Background image
                if array_values[4].find(".jpg") > 0 or array_values[4].find(".png") > 0 or array_values[4].find(".tga") > 0:
                    val = rgb([int(array_values[0]),
                               int(array_values[1]),
                               int(array_values[2])],
                              a=float(array_values[3]))
                    return val[0], val[1], val[2], val[3], array_values[4]

            ac.console('Error loading color :' + str(value))
            ac.log('Error loading color :' + str(value))
        value = value.lstrip('#')
        if len(value) == 6:
            # HEX RGB
            lv = len(value)
            array_values = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
            return rgb([int(array_values[0]),
                        int(array_values[1]),
                        int(array_values[2])])
        if len(value) == 8:
            # HEX ARGB
            lv = len(value)
            array_values = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
            #ac.log("HEX=" + str(array_values[1]) + "," + str(array_values[2]) + "," + str(array_values[3]) + "," + str(array_values[0]/255))
            #ac.console("HEX=" + str(array_values[1]) + "," + str(array_values[2]) + "," + str(array_values[3]) + "," + str(array_values[0]/255))
            return rgb([int(array_values[1]),
                        int(array_values[2]),
                        int(array_values[3])],
                       a=float(array_values[0]/255))

        ac.console('Error loading color :' + str(value))
        ac.log('Error loading color :' + str(value))
        return rgb([0, 0, 0])

    # --------------- Driver -------------
    @staticmethod
    def tower_time_odd_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_odd_bg')
        return rgb([32, 32, 32], a=0.72)

    @staticmethod
    def tower_time_retired_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_retired_bg')
        return rgb([32, 32, 32], a=0.72)

    @staticmethod
    def tower_time_odd_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_odd_txt')
        return Colors.white()

    @staticmethod
    def tower_time_green_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_green_txt')
        return rgb([95, 180, 157], a=1)

    @staticmethod
    def tower_time_highlight_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_highlight_txt')
        return Colors.white()

    @staticmethod
    def tower_time_highlight_odd_bg():
        #return rgb([0, 0, 0], a=1)
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_highlight_odd_bg')
        return rgb([32, 32, 32], a=0.72)

    @staticmethod
    def tower_time_qualification_highlight_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_qualification_highlight_txt')
        if Colors.theme_highlight == 1:
            return Colors.green()
        return Colors.red()

    @staticmethod
    def tower_time_retired_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_retired_txt')
        return rgb([168, 48, 48])

    @staticmethod
    def tower_time_best_lap_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_best_lap_txt')
        # return rgb([135, 31, 144])
        return rgb([255, 26, 133])
        # TODO white, use when background is purple
        # return rgb([250, 250, 250])

    @staticmethod
    def tower_time_best_lap_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_best_lap_bg')
        # return rgb([135, 31, 144])
        # return rgb([255, 26, 133])
        # TODO purple label bg, use when white text
        return rgb([111, 66, 193])

    @staticmethod
    def tower_time_last_lap_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_last_lap_txt')
        return rgb([191, 0, 0])

    @staticmethod
    def tower_time_place_gain_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_place_gain_txt')
        return rgb([32, 192, 31])

    @staticmethod
    def tower_time_place_lost_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_place_lost_txt')
        return rgb([191, 0, 0])

    @staticmethod
    def tower_time_pit_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_pit_txt')
        return Colors.yellow()

    @staticmethod
    def tower_driver_odd_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_odd_bg')
        return rgb([32, 32, 32], a=0.72)

    @staticmethod
    def tower_driver_odd_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_odd_txt')
        return Colors.white()

    @staticmethod
    def tower_driver_highlight_odd_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_highlight_odd_bg')
        return rgb([32, 32, 32], a=0.72)

    @staticmethod
    def tower_driver_highlight_odd_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_highlight_odd_txt')
        return Colors.white()

    @staticmethod
    def tower_driver_stopped_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_stopped_txt')
        return Colors.yellow()

    @staticmethod
    def tower_driver_blue_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_blue_txt')
        return Colors.blue_flag()

    @staticmethod
    def tower_driver_lap_up_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_lap_up_txt')
        return Colors.blue_flag()

    @staticmethod
    def tower_driver_retired_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_retired_bg')
        return rgb([32, 32, 32], a=0.72)

    @staticmethod
    def tower_driver_retired_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_retired_txt')
        return rgb([112, 112, 112])

    @staticmethod
    def tower_position_odd_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_odd_bg')
        return rgb([12, 12, 12], a=0.62)

    @staticmethod
    def tower_position_fastest_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_fastest_bg')
        return rgb([12, 12, 12], a=0.62)

    @staticmethod
    def tower_position_odd_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_odd_txt')
        return Colors.white()

    @staticmethod
    def tower_position_highlight_odd_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_highlight_odd_bg')
        return rgb([255, 255, 255], a=0.96)

    @staticmethod
    def tower_position_highlight_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_highlight_txt')
        return Colors.red()

    @staticmethod
    def tower_position_highlight_odd_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_highlight_odd_txt')
        return Colors.red()

    @staticmethod
    def tower_position_retired_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_retired_txt')
        return rgb([112, 112, 112])

    @staticmethod
    def tower_position_retired_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_retired_bg')
        return rgb([0, 0, 0], a=0.58)

    @staticmethod
    def tower_pit_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_pit_txt')
        return rgb([225, 225, 225])

    @staticmethod
    def tower_tires_txt():
        return Colors.get_color_for_key('tower_tires_txt')

    @staticmethod
    def tower_tires_bg():
        return Colors.get_color_for_key('tower_tires_bg')

    @staticmethod
    def tower_pit_highlight_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_pit_highlight_txt')
        return rgb([191, 0, 0])

    @staticmethod
    def tower_stint_lap_invalid_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_stint_lap_invalid_txt')
        return rgb([191, 0, 0])

    @staticmethod
    def tower_p2p_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_p2p_txt')
        return rgb([225, 225, 225])

    @staticmethod
    def tower_p2p_cooling():
        return rgb([0,80,150], bg=1, t=Colors.app_path + 'img/tower_status.png')

    @staticmethod
    def tower_p2p_active():
        return rgb([252,139,1], bg=1, t=Colors.app_path + 'img/tower_status.png')

    @staticmethod
    def tower_border_default_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_border_default_bg')
        return Colors.theme(a=Colors.border_opacity())

    @staticmethod
    def tower_border_default_bg_opacity():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_border_default_bg')[3]
        return Colors.border_opacity()

    @staticmethod
    def tower_border_default_bg_opacity_retired():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_border_retired_bg')[3]
        return Colors.border_opacity()

    # --------------- Tower --------------
    @staticmethod
    def tower_mode_title_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_mode_title_bg')
        return Colors.theme()

    @staticmethod
    def tower_mode_title_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_mode_title_txt')
        return Colors.white()

    @staticmethod
    def tower_stint_title_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_stint_title_bg')
        return rgb([20, 20, 20], a=0.8)

    @staticmethod
    def tower_stint_title_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_stint_title_txt')
        return Colors.white()

    @staticmethod
    def tower_stint_tire_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_stint_tire_bg')
        return rgb([32, 32, 32], a=0.58)

    @staticmethod
    def tower_stint_tire_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_stint_tire_txt')
        return Colors.white()

    @staticmethod
    def tower_class_bg():
        return Colors.get_color_for_key('tower_class_bg')

    @staticmethod
    def tower_class_txt():
        return Colors.get_color_for_key('tower_class_txt')

    # --------------- Info ---------------
    @staticmethod
    def info_driver_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_driver_bg')
        #return Colors.theme()
        return rgb([20, 20, 20], a=0.8)

    @staticmethod
    def info_driver_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_driver_txt')
        return Colors.white()

    @staticmethod
    def info_driver_single_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_driver_single_bg')
        return rgb([20, 20, 20], a=0.8)

    @staticmethod
    def info_driver_single_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_driver_single_txt')
        return Colors.white()

    @staticmethod
    def info_split_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_split_txt')
        return Colors.white()

    @staticmethod
    def info_split_positive_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_split_positive_txt')
        return Colors.yellow()

    @staticmethod
    def info_split_negative_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_split_negative_txt')
        return Colors.green()

    @staticmethod
    def info_timing_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_timing_bg')
        return rgb([55, 55, 55], a=0.64)

    @staticmethod
    def delta_name_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('delta_name_bg')
        return rgb([55, 55, 55], a=0.64)

    @staticmethod
    def delta_name_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('delta_name_txt')
        return rgb([255, 255, 255], a=1)

    @staticmethod
    def info_timing_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_timing_txt')
        return Colors.white()

    @staticmethod
    def info_position_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_position_bg')
        return rgb([112, 112, 112])

    @staticmethod
    def info_position_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_position_txt')
        return Colors.white()

    @staticmethod
    def info_fastest_time_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_fastest_time_txt')
        return Colors.white()

    @staticmethod
    def info_border_default_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_border_default_bg')
        return Colors.theme(a=0.64)

    # --------------- Timer ---------------
    @staticmethod
    def timer_title_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_title_bg')
        return Colors.theme(a=0.64)

    @staticmethod
    def timer_title_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_title_txt')
        return Colors.white()

    @staticmethod
    def timer_title_yellow_flag_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_title_yellow_flag_bg')
        return Colors.black()

    @staticmethod
    def timer_title_yellow_flag_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_title_yellow_flag_txt')
        return Colors.white()

    @staticmethod
    def timer_time_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_time_bg')
        return rgb([55, 55, 55], a=0.64)

    @staticmethod
    def timer_time_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_time_txt')
        return Colors.white()

    @staticmethod
    def timer_time_yellow_flag_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_time_yellow_flag_bg')
        return Colors.yellow(True)

    @staticmethod
    def timer_time_yellow_flag_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_time_yellow_flag_txt')
        return Colors.black_txt()

    @staticmethod
    def timer_pit_window_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_pit_window_bg')
        return rgb([55, 55, 55], a=0.64)

    @staticmethod
    def timer_pit_window_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_pit_window_txt')
        return Colors.white()

    @staticmethod
    def timer_pit_window_open_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_pit_window_open_txt')
        return Colors.green()

    @staticmethod
    def timer_pit_window_done_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_pit_window_done_txt')
        return rgb([172, 172, 172])

    @staticmethod
    def timer_pit_window_close_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_pit_window_close_txt')
        return Colors.red()

    @staticmethod
    def timer_border_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_border_bg')
        return Colors.theme(a=Colors.border_opacity())

    @staticmethod
    def timer_border_yellow_flag_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_border_yellow_flag_bg')
        return Colors.black()

    @staticmethod
    def border_opacity():
        return 0.7

    @staticmethod
    def white(bg=False, a=1):
        return rgb([255, 255, 255], bg=bg, a=a)

    @staticmethod
    def delta_laps():
        return rgb([0, 0, 0], a=0, t=Colors.app_path + 'img/delta_laps.png')

    @staticmethod
    def delta_time():
        return rgb([0, 0, 0], a=0, t=Colors.app_path + 'img/delta_time.png')

    @staticmethod
    def delta_neutral():
        return rgb([0, 0, 0], a=0, t=Colors.app_path + 'img/delta_neutral.png')

    @staticmethod
    def info_lap_neutral():
        return rgb([140, 151, 157], bg=True, a=1)

    @staticmethod
    def delta_negative():
        return rgb([0, 0, 0], a=0, t=Colors.app_path + 'img/delta_negative.png')

    @staticmethod
    def delta_positive():
        return rgb([0, 0, 0], a=0, t=Colors.app_path + 'img/delta_positive.png')

    @staticmethod
    def logo_bg(bg=True, a=1):
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('logo_bg')
        return rgb([187, 187, 187], bg=bg, a=a)

    @staticmethod
    def black():
        return rgb([0, 0, 0], a=1)

    @staticmethod
    def blue_flag():
        return rgb([0, 0, 200], a=1)

    @staticmethod
    def flag_finish():
        return rgb([255, 255, 255], a=1, t=Colors.app_path + 'img/flag_finish.png')

    @staticmethod
    def tower_finish():
        return rgb([255, 255, 255], a=1, t=Colors.app_path + 'img/tower_finish.png')

    @staticmethod
    def timer_finish():
        return rgb([255, 255, 255], a=0, t=Colors.app_path + 'img/timer_finish.png')

    @staticmethod
    def timer_left_corner():
        return rgb([0, 0, 0], a=0, t=Colors.app_path + 'img/timer_left.png')

    @staticmethod
    def timer_right_corner():
        return rgb([0, 0, 0], a=0, t=Colors.app_path + 'img/timer_right.png')

    @staticmethod
    def info_split_txt():
        return Colors.get_color_for_key('info_split_txt')

    @staticmethod
    def info_split_positive_txt():
        return Colors.get_color_for_key('info_split_positive_txt')

    @staticmethod
    def info_split_negative_txt():
        return Colors.get_color_for_key('info_split_negative_txt')

    @staticmethod
    def info_split_personal_txt():
        return Colors.get_color_for_key('info_split_personal_txt')

    @staticmethod
    def info_split_best_bg():
        return Colors.get_color_for_key('info_split_best_bg')

    @staticmethod
    def info_split_slow_bg():
        return Colors.get_color_for_key('info_split_slow_bg')

    @staticmethod
    def info_split_personal_bg():
        return Colors.get_color_for_key('info_split_personal_bg')

    @staticmethod
    def info_car_class_bg():
        return Colors.get_color_for_key('info_car_class_bg')

    @staticmethod
    def info_car_class_txt():
        return Colors.get_color_for_key('info_car_class_txt')

    @staticmethod
    def info_sector_title_bg():
        return Colors.get_color_for_key('info_sector_title_bg')

    @staticmethod
    def info_sector_title_txt():
        return Colors.get_color_for_key('info_sector_title_txt')

    @staticmethod
    def weather_header_bg():
        return Colors.get_color_for_key('weather_header_bg')

    @staticmethod
    def weather_header_txt():
        return Colors.get_color_for_key('weather_header_txt')

    @staticmethod
    def weather_data_bg():
        return Colors.get_color_for_key('weather_data_bg')

    @staticmethod
    def weather_data_txt():
        return Colors.get_color_for_key('weather_data_txt')

    @staticmethod
    def weather_wind_direction_img():
        return rgb([0, 0, 0], a=0, t=Colors.app_path + 'img/winddir.png')

    @staticmethod
    def black_txt():
        return rgb([0, 0, 0])

    @staticmethod
    def black_shadow():
        return rgb([77, 77, 77])

    @staticmethod
    def position_multiclass():
        return rgb([255, 255, 255], a=0.76)

    @staticmethod
    def red(bg=False):
        return rgb([224, 0, 0], bg=bg)

    @staticmethod
    def status_pitstop():
        return rgb([229, 138, 0], bg=1, t=Colors.app_path + 'img/tower_status.png')

    @staticmethod
    def status_stopped_ontrack():
        return rgb([224, 0, 0], bg=1, t=Colors.app_path + 'img/tower_status.png')

    @staticmethod
    def ping_bg():
        return rgb([63, 63, 63], bg=1)

    @staticmethod
    def green(bg=False):
        return rgb([32, 192, 31], bg=bg)

    @staticmethod
    def green_bg():
        return rgb([1, 170, 89], bg=1)

    @staticmethod
    def status_green():
        return rgb([1, 170, 89], bg=1, t=Colors.app_path + 'img/tower_status.png')

    @staticmethod
    def yellow(bg=False):
        return rgb([240, 171, 1], bg=bg)

    @staticmethod
    def logo_for_car(car,skin):
        #Skin team logo
        if skin != '' and os.path.exists(Colors.app_path + 'logos/' + car + '_' + skin + '.png'):
            return rgb([0, 0, 0], a=0, t=Colors.app_path + 'logos/' + car + '_' + skin + '.png')
        if skin != '' and os.path.exists('content/cars/' + car + '/skins/' + skin + '/logo.png'):
            return rgb([0, 0, 0], a=0, t='content/cars/' + car + '/skins/' + skin + '/logo.png')
        # Car brand
        if os.path.exists(Colors.app_path + 'logos/' + car + '.png'):
            return rgb([0, 0, 0], a=0, t=Colors.app_path + 'logos/' + car + '.png')
        if car.find("mclaren") >= 0:
            return rgb([0, 0, 0], a=0, t=Colors.app_path + 'logos/mclaren.png')
        if car.find("audi") >= 0:
            return rgb([0, 0, 0], a=0, t=Colors.app_path + 'logos/audi.png')
        if car.find("porsche") >= 0:
            return rgb([0, 0, 0], a=0, t=Colors.app_path + 'logos/porsche.png')
        if os.path.exists('content/cars/' + car + '/logo.png'):
            return rgb([0, 0, 0], a=0, t='content/cars/' + car + '/logo.png')
        if os.path.exists('content/cars/' + car + '/ui/badge.png'):
            return rgb([0, 0, 0], a=0, t='content/cars/' + car + '/ui/badge.png')
        return rgb([0, 0, 0], a=0, t='content/gui/default_icon.png')#512,NationFlags/AC.png(48)

    @staticmethod
    def color_for_car_class(car_class):
        if Colors.multiCarsClasses:
            if car_class != "" and car_class+'_bg' in Colors.car_classes:
                return Colors.car_classes[car_class+'_bg']
        return Colors.car_classes['default_bg']

    @staticmethod
    def car_class_name(car_class):
        if car_class != "" and car_class + '_title' in Colors.car_classes:
            return Colors.car_classes[car_class + '_title']
        if len(car_class) > 8:
            return car_class[:9].upper()
        return car_class.upper()

    @staticmethod
    def txt_color_for_car_class(car_class):
        if Colors.multiCarsClasses:
            if car_class != "" and car_class+'_txt' in Colors.car_classes:
                return Colors.car_classes[car_class+'_txt']
        return Colors.car_classes['default_txt']

    @staticmethod
    def get_drivers_picture(steam_id):
        if steam_id is not None and os.path.exists(Colors.app_path + 'img/drivers/' + steam_id + '.png'):
            return rgb([0, 0, 0], a=0, t=Colors.app_path + 'img/drivers/' + steam_id + '.png')
        if steam_id is not None and os.path.exists(Colors.app_path + 'img/drivers/' + steam_id + '.jpg'):
            return rgb([0, 0, 0], a=0, t=Colors.app_path + 'img/drivers/' + steam_id + '.jpg')
        return rgb([0,0,0],a=0)

    @staticmethod
    def get_drivers_country(country):
        Colors.is_addon_flag=False
        if country is not None and country != '' and os.path.exists(Colors.app_path + 'img/flags/' + country + '.png'):
            Colors.is_addon_flag=True
            return rgb([0, 0, 0], a=0, t=Colors.app_path + 'img/flags/' + country + '.png')
        if country is not None and country != '' and os.path.exists(Colors.app_path + 'img/flags/' + country + '.jpg'):
            Colors.is_addon_flag=True
            return rgb([0, 0, 0], a=0, t=Colors.app_path + 'img/flags/' + country + '.jpg')
        if country is not None and country != '' and os.path.exists('content/gui/NationFlags/' + country + '.png'):
            return rgb([0, 0, 0], a=0, t='content/gui/NationFlags/' + country + '.png')
        return rgb([0,0,0],a=0)


class Label:
    refresh_rate = 50
    # INITIALIZATION

    def __init__(self, window, text=""):
        self.text = text
        #self.window = window
        self.debug = False
        self.is_hiding = True
        self.label = ac.addLabel(window, self.text)
        self.params = {"x": Value(0), "y": Value(0), "w": Value(0), "h": Value(0), "br": Value(0), "bg": Value(0),
                       "bb": Value(0), "o": Value(0), "r": Value(1), "g": Value(1), "b": Value(1), "a": Value(0)}
        self.f_params = {"x": Value(0), "y": Value(0), "w": Value(0), "h": Value(0), "br": Value(0), "bg": Value(0),
                         "bb": Value(0), "o": Value(0), "r": Value(1), "g": Value(1), "b": Value(1), "a": Value(0)}
        self.o_params = {"x": Value(0), "y": Value(0), "w": Value(0), "h": Value(0), "br": Value(0), "bg": Value(0),
                         "bb": Value(0), "o": Value(0), "r": Value(1), "g": Value(1), "b": Value(1), "a": Value(1)}
        self.multiplier = {"x": Value(3), "y": Value(3), "w": Value(1), "h": Value(1), "br": Value(0.06),
                           "bg": Value(0.06), "bb": Value(0.06), "o": Value(0.02), "r": Value(0.06), "g": Value(0.06),
                           "b": Value(0.06), "a": Value(0.02)}
        self.multiplier_mode = {"x": "", "y": "", "w": "", "h": "", "br": "", "bg": "", "bb": "", "o": "", "r": "",
                                "g": "", "b": "", "a": ""}
        self.fontSize = 12
        self.spring_multiplier = 36
        self.align = "left"
        self.bgTexture = Value('')
        self.fontName = ""
        self.cur_fontName = ""
        self.visible = 0
        self.isVisible = Value(False)
        self.isTextVisible = Value(False)
        self.setVisible(0)
        self.params_adjust_needed=False

    # PUBLIC METHODS
    def set(self, text=None, align=None, color=None, font_size=None, font=None, w=None, h=None, x=None, y=None, texture=None, background=None, opacity=None, visible=None, animated=False, text_hidden=False, init=False):
        # Text
        if text is not None:
            self.setText(text, text_hidden)
        # Text alignment
        if align is not None:
            self.setAlign(align)
        # Size
        if w is not None and h is not None:
            self.setSize(w, h, animated)
        elif w is not None:
            self.setSize(w, self.params["h"].value, animated)
        elif h is not None:
            self.setSize(self.params["w"].value, h, animated)
        # Position
        if x is not None and y is not None:
            self.setPos(x, y, animated)
        elif x is not None:
            self.setX(x, animated)
        elif y is not None:
            self.setY(y, animated)
        # Font color
        if color is not None:
            self.setColor(color, animated, init)
        # Font
        if font is not None:
            self.setFont(font, 0, 0)
        # Font size
        if font_size is not None:
            self.setFontSize(font_size)
        # Background texture
        if texture is not None:
            self.setBgTexture(texture)
        # Background color
        if background is not None:
            self.setBgColor(background, animated, init)
        # Background opacity
        if opacity is not None:
            self.setBgOpacity(opacity, animated, init)
        # Visibility
        if visible is not None:
            self.setVisible(visible)
        return self

    def setText(self, text, hidden=False):
        self.text = text
        if hidden:
            ac.setText(self.label, "")
            self.isTextVisible.setValue(False)
        else:
            ac.setText(self.label, self.text)
            self.isTextVisible.setValue(True)
        return self

    def setSize(self, w, h, animated=False):
        self.f_params["w"].setValue(w)
        self.f_params["h"].setValue(h)
        if not animated:
            self.o_params["w"].setValue(w)
            self.o_params["h"].setValue(h)
            self.params["w"].setValue(w)
            self.params["h"].setValue(h)
            if self.params["w"].hasChanged() or self.params["h"].hasChanged():
                ac.setSize(self.label, self.params["w"].value, self.params["h"].value)
        return self

    def setPos(self, x, y, animated=False):
        self.f_params["x"].setValue(x)
        self.f_params["y"].setValue(y)
        if not animated:
            self.o_params["x"].setValue(x)
            self.o_params["y"].setValue(y)
            self.params["x"].setValue(x)
            self.params["y"].setValue(y)
            if self.params["x"].hasChanged() or self.params["y"].hasChanged():
                ac.setPosition(self.label, self.params["x"].value, self.params["y"].value)
        return self

    def setY(self, y, animated=False):
        self.f_params["y"].setValue(y)
        if not animated:
            self.o_params["y"].setValue(y)
            self.params["y"].setValue(y)
            if self.params["y"].hasChanged():
                ac.setPosition(self.label, self.params["x"].value, self.params["y"].value)
        return self

    def setX(self, x, animated=False):
        self.f_params["x"].setValue(x)
        if not animated:
            self.o_params["x"].setValue(x)
            self.params["x"].setValue(x)
            if self.params["x"].hasChanged():
                ac.setPosition(self.label, self.params["x"].value, self.params["y"].value)
        return self

    def setColor(self, color, animated=False, init=False):
        self.f_params["r"].setValue(color[0])
        self.f_params["g"].setValue(color[1])
        self.f_params["b"].setValue(color[2])
        if init or not animated:
            self.o_params["r"].setValue(color[0])
            self.o_params["g"].setValue(color[1])
            self.o_params["b"].setValue(color[2])
            self.o_params["a"].setValue(color[3])
        if self.isVisible.value:
            self.f_params["a"].setValue(color[3])
        if not animated:
            self.params["r"].setValue(color[0])
            self.params["g"].setValue(color[1])
            self.params["b"].setValue(color[2])
            if self.isVisible.value:
                self.params["a"].setValue(color[3])
                ac.setFontColor(self.label, *color)
        return self

    def setFont(self, fontName, italic, bold):
        self.fontName = fontName
        self.cur_fontName = fontName
        ac.setCustomFont(self.label, self.fontName, italic, bold)
        return self

    def update_font(self):
        self.setFont(Font.get_font(), 0, 0)
        return self

    def change_font_if_needed(self, support=None):
        '''

        if support is not None:
            self.cur_fontName = Font.get_support_font()
            ac.setCustomFont(self.label, self.cur_fontName, 0, 0)
        elif self.fontName != self.cur_fontName:
            self.setFont(Font.get_font(), 0, 0)
        '''
        return self

    def setFontSize(self, fontSize):
        self.fontSize = fontSize
        ac.setFontSize(self.label, self.fontSize)
        return self

    def setAlign(self, align="left"):
        self.align = align
        ac.setFontAlignment(self.label, self.align)
        return self

    def setBgTexture(self, texture):
        self.bgTexture.setValue(texture)
        if self.bgTexture.hasChanged():
            if self.bgTexture.value == '':
                ac.setBackgroundTexture(self.label, Colors.app_path + 'img/reset_bg.png')
                #ac.setBackgroundTexture(self.label, 'content/gui/actv/reset_bg.png')
            else:
                ac.setBackgroundTexture(self.label, self.bgTexture.value)
        return self

    def setBgColor(self, color, animated=False, init=False):
        # background image [0]
        if len(color) > 4 and color[4] is not None:
            self.setBgTexture(color[4])
        else:
            self.setBgTexture('')
        self.f_params["br"].setValue(color[0])
        self.f_params["bg"].setValue(color[1])
        self.f_params["bb"].setValue(color[2])
        if init or not animated:
            self.o_params["br"].setValue(color[0])
            self.o_params["bg"].setValue(color[1])
            self.o_params["bb"].setValue(color[2])
        if not animated:
            self.params["br"].setValue(color[0])
            self.params["bg"].setValue(color[1])
            self.params["bb"].setValue(color[2])
            ac.setBackgroundColor(self.label, color[0], color[1], color[2])
            if self.isVisible.value:
                ac.setBackgroundOpacity(self.label, self.params["o"].value)
            else:
                ac.setBackgroundOpacity(self.label, 0)
        if len(color) > 3:
            self.setBgOpacity(color[3], animated, init)
        return self

    def setBgOpacity(self, opacity, animated=False, init=False):
        if init or not animated:
            self.o_params["o"].setValue(opacity)
        if self.isVisible.value:
            self.f_params["o"].setValue(opacity)
        if not animated:
            if self.isVisible.value:
                self.params["o"].setValue(opacity)
                ac.setBackgroundOpacity(self.label, self.params["o"].value)
        return self

    ############################## Animations ##############################

    def debug_param(self, title="", param="o"):
        ac.console(title + ": current:" + str(self.params[param].value) + " final:" + str(self.f_params[param].value) + " origin:" + str(
            self.o_params[param].value))
        ac.log(title + ": current:" + str(self.params[param].value) + " final:" + str(self.f_params[param].value) + " origin:" + str(
            self.o_params[param].value))
        return self

    def setVisible(self, value):
        self.visible = value
        self.isVisible.setValue(bool(value))
        ac.setVisible(self.label, value)
        if self.isVisible.value:
            self.is_hiding = False
        else:
            self.is_hiding = True
        return self

    def setAnimationSpeed(self, param, value):
        for p in param:
            self.multiplier[p].setValue(value)
        return self

    def setAnimationMode(self, param, value):
        for p in param:
            self.multiplier_mode[p] = value
        return self

    def hide(self):
        self.is_hiding = True
        if self.o_params["o"].value == 0:
            self.hideText()
        else:
            #self.setBgOpacity(0, True)
            self.f_params["o"].setValue(0)
        return self

    def slide_up(self):
        self.f_params["h"].setValue(0)
        return self

    def show(self):
        self.is_hiding = False
        if self.o_params["o"].value == 0:
            self.showText()
        else:
            self.f_params["o"].setValue(self.o_params["o"].value)
            self.f_params["a"].setValue(self.o_params["a"].value)
        return self

    def slide_down(self):
        self.f_params["h"].setValue(self.o_params["h"].value)
        return self

    def showText(self):
        self.is_hiding = False
        self.f_params["a"].setValue(self.o_params["a"].value)
        return self

    def hideText(self):
        self.is_hiding = True
        self.f_params["a"].setValue(0)
        return self

    def adjustParam(self, p):
        if self.params[p].value != self.f_params[p].value:
            self.params_adjust_needed = True
            if self.multiplier_mode[p] == "spring":
                multiplier = self.multiplier[p].value
                spring_multi = self.spring_multiplier
                if p == "y":
                    spring_multi = self.f_params["h"].value - 1
                    if not spring_multi > 0:
                        spring_multi = 36
                if abs(self.f_params[p].value - self.params[p].value) > spring_multi * self.multiplier[p].value:
                    multiplier = round(abs(self.f_params[p].value - self.params[p].value) / spring_multi)
            else:
                multiplier = self.multiplier[p].value
            if self.__class__.refresh_rate < 32:
                multiplier=multiplier*3
            elif self.__class__.refresh_rate < 40:
                multiplier=multiplier*2
            if abs(self.f_params[p].value - self.params[p].value) < multiplier:
                multiplier = abs(self.f_params[p].value - self.params[p].value)
            if self.params[p].value < self.f_params[p].value:
                self.params[p].setValue(self.params[p].value + multiplier)
            else:
                self.params[p].setValue(self.params[p].value - multiplier)
        return self

    def animate(self):
        if self.debug:
            #self.debug_param("A", "a")
            #self.debug_param("O", "o")
            self.debug_param("br", "br")
            #self.debug_param("g", "g")
            #self.debug_param("b", "b")
        # adjust size +1
        self.params_adjust_needed = False
        self.adjustParam("w").adjustParam("h")
        # adjust position +3
        self.adjustParam("x").adjustParam("y")
        # adjust background
        self.adjustParam("br").adjustParam("bg").adjustParam("bb").adjustParam("o")
        # adjust colors + 0.02
        self.adjustParam("r").adjustParam("g").adjustParam("b").adjustParam("a")
        if self.params_adjust_needed:
            # commit changes
            if self.params["x"].hasChanged() or self.params["y"].hasChanged():
                ac.setPosition(self.label, self.params["x"].value, self.params["y"].value)
            param_h_changed = self.params["h"].hasChanged()
            if self.params["w"].hasChanged() or param_h_changed:
                ac.setSize(self.label, self.params["w"].value, self.params["h"].value)
                #if param_h_changed:
                #    if self.params["h"].value == 0:
                #        self.isVisible.setValue(False)
                #    else:
                #        self.isVisible.setValue(True)
            if self.params["br"].hasChanged() or self.params["bg"].hasChanged() or self.params["bb"].hasChanged():
                ac.setBackgroundColor(self.label, self.params["br"].value, self.params["bg"].value, self.params["bb"].value)
                ac.setBackgroundOpacity(self.label, self.params["o"].value)

            opacity_changed = self.params["o"].hasChanged()
            if opacity_changed:
                # fg opacity
                ac.setBackgroundOpacity(self.label, self.params["o"].value)
                # TODO : hide by alpha
                if not self.is_hiding and (self.params["o"].value >= 0.4 or self.f_params["o"].value < 0.4):
                    self.isTextVisible.setValue(True)
                elif self.is_hiding:
                    self.isTextVisible.setValue(False)
                if self.isTextVisible.hasChanged():
                    if self.isTextVisible.value:
                        ac.setText(self.label, self.text)
                        ac.setFontColor(self.label, self.params["r"].value,
                                        self.params["g"].value,
                                        self.params["b"].value,
                                        self.params["a"].value)
                    else:
                        ac.setText(self.label, "")
                        if self.debug:
                            self.debug_param("setText", "a")
                            self.debug_param("setText", "o")

            alpha_changed = self.params["a"].hasChanged()
            if self.params["r"].hasChanged() or self.params["g"].hasChanged() \
                    or self.params["b"].hasChanged() or alpha_changed:
                ac.setFontColor(self.label,
                                self.params["r"].value,
                                self.params["g"].value,
                                self.params["b"].value,
                                self.params["a"].value)

            if opacity_changed or alpha_changed:
                if self.is_hiding and ((opacity_changed and self.params["o"].value == 0)
                                       or (alpha_changed and self.params["a"].value == 0)):
                    self.setVisible(0)
                elif not self.is_hiding:
                    self.setVisible(1)

# -#####################################################################################################################################-#


class Button:
    # INITIALIZATION

    def __init__(self, window, clickFunc, width=60, height=20, x=0, y=0, text="", texture=""):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.button = ac.addButton(window, text)

        # adding default settings
        self.setSize(width, height)
        self.setPos(x, y)
        if texture != "":
            self.setBgTexture(texture)

        # default settings
        ac.drawBorder(self.button, 0)
        ac.setBackgroundOpacity(self.button, 0)

        # adding a click event
        ac.addOnClickedListener(self.button, clickFunc)

    # PUBLIC METHODS

    def setSize(self, width, height):
        self.width = width
        self.height = height
        ac.setSize(self.button, self.width, self.height)
        return self

    def setFontSize(self, fontSize):
        self.fontSize = fontSize
        ac.setFontSize(self.button, self.fontSize)
        return self

    def setPos(self, x, y):
        self.x = x
        self.y = y
        ac.setPosition(self.button, self.x, self.y)
        return self

    def setBgTexture(self, texture):
        ac.setBackgroundTexture(self.button, texture)
        return self

    def setText(self, text, hidden=False):
        ac.setText(self.button, text)
        return self

    def setAlign(self, align="left"):
        ac.setFontAlignment(self.button, align)
        return self

    def setBgColor(self, color, animated=False):
        ac.setBackgroundColor(self.button, *color)
        # ac.setBackgroundOpacity(self.label, self.params["o"].value)
        return self

    def setBgOpacity(self, opacity, animated=False):
        ac.setBackgroundOpacity(self.button, opacity)
        return self

    def setVisible(self, value):
        ac.setVisible(self.button, value)
        return self


# -#####################################################################################################################################-#

class Log:
    @staticmethod
    def w(message):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        ac.console(message + ":")
        for line in lines:
            ac.log(line)
        for line in lines:
            if line.find("Traceback") >= 0:
                continue
            s = line.replace("\n", " -> ")
            s = s.replace("  ", "")
            if s[-4:] == " -> ":
                s = s[:-4]
            ac.console(s)


class Config:
    user_documents_path=None
    # INITIALIZATION

    def __init__(self, path, filename):
        self.file = path + filename
        self.parser = 0

        try:
            self.parser = configparser.RawConfigParser()
        except:
            ac.console("Prunn: Config -- Failed to initialize ConfigParser.")

        # read the file
        self._read()

    # LOCAL METHODS

    @staticmethod
    def get_user_documents_path():
        if Config.user_documents_path is None:
            '''
            # Solution 1
            file_path = os.path.join(os.path.expanduser("~"), "Documents", "Assetto Corsa", "cfg") + "/"
            if not os.path.exists(file_path + 'race.ini'):
                file_path = os.path.join(os.path.expandvars("%OneDrive%"), "Documents", "Assetto Corsa", "cfg") + "/"
            if not os.path.exists(file_path + 'race.ini'):
                file_path = 'cfg/'
                
            # Solution 2
            dll = ctypes.windll.shell32
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH + 1)
            if dll.SHGetSpecialFolderPathW(None, buf, 0x0005, False):
                Config.user_documents_path = buf.value
            else:
                ac.log("Failure!")
            '''
            # Solution 3
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            v = winreg.QueryValueEx(k, "Personal")
            Config.user_documents_path = os.path.join(v[0], "Assetto Corsa") + "/"

        return Config.user_documents_path

    def _read(self):
        self.parser.read(self.file, encoding='utf-8')

    def _write(self):
        with open(self.file, "w") as cfgFile:
            self.parser.write(cfgFile)

    # PUBLIC METHODS

    def sections(self):
        return self.parser.sections()

    def has(self, section=None, option=None):
        if section is not None:
            # if option is not specified, search only for the section
            if option is None:
                return self.parser.has_section(section)
            # else, search for the option within the specified section
            else:
                return self.parser.has_option(section, option)
        # if section is not specified
        else:
            ac.console("Prunn: Config.has -- section must be specified.")

    def set(self, section=None, option=None, value=None):
        if section is not None:
            # if option is not specified, add the specified section
            if option is None:
                self.parser.add_section(section)
                self._write()
            # else, add the option within the specified section
            else:
                if not self.has(section, option) and value is None:
                    ac.console("Prunn: Config.set -- a value must be passed.")
                else:
                    if not self.has(section):
                        self.parser.add_section(section)
                    self.parser.set(section, option, value)
                    self._write()
        # if sections is not specified
        else:
            ac.console("Prunn: Config.set -- section must be specified.")

    def get(self, section, option, type=""):
        if self.has(section) and self.has(section, option):
            # if option request is an integer
            if type == "int":
                return self.parser.getint(section, option)
            # if option request is a float
            elif type == "float":
                return self.parser.getfloat(section, option)
            # if option request is boolean
            elif type == "bool":
                return self.parser.getboolean(section, option)
            # it must be a string then!
            else:
                return self.parser.get(section, option)
        else:
            return -1

    def remSection(self, section):
        if self.has(section):
            self.parser.remove_section(section)
            self._write()
        else:
            ac.console("Prunn: Config.remSection -- section not found.")

    def remOption(self, section, option):
        if self.has(section) and self.has(section, option):
            self.parser.remove_option(section, option)
            self._write()
        else:
            ac.console("Prunn: Config.remOption -- option not found.")


class Font:
    # Name, size offset, support, width, font x offset
    '''
    fonts = [["Segoe UI", 0, None, 1.2, 0],
             ["Noto Sans", 0, None, 1.26, 0],
             ["Open Sans", 0, 0, 1.5, 0],
             ["Yantramanav", 5, 0, 1.18, 0],
             ["Signika Negative", 3, 0, 1.2, 0],
             ["Strait", 7, 0, 1.1, 0],
             ["Overlock", 4, 1, 1.1, 0]]
     '''
    init = []
    font_ini = ''
    font_files = []
    current = 0
    current_font = {
        'font_name': "Segoe UI",
        'size_offset': -7,
        'support_utf8': 1,
        'width': 1.2,
        'x_offset': 4
    }

    # ------------Theme engine -----------
    @staticmethod
    def load_fonts():
        Font.font_files = []
        theme_files = [os.path.join(root, name)
                       for root, dirs, files in os.walk(Colors.app_path + "fonts/")
                       for name in files
                       if name.endswith(".ini")]
        if len(theme_files):
            for t in theme_files:
                cfg = Config(t, "")
                name = cfg.get('MAIN', 'title', 'string')
                if name == -1:
                    name = ""
                Font.font_files.append({"file": t, "name": name})

    @staticmethod
    def set_font(font):
        Font.current = font
        if Font.current > 0:
            Font.font_ini = Font.font_files[Font.current - 1]['file']
        else:
            Font.font_ini = ''
        if Font.current > 0 and len(Font.font_files):
            cfg = Config(Font.font_files[Font.current - 1]['file'], "")
            for key in Font.current_font:
                value = cfg.get('CONFIG', key, 'string')
                if value != -1:
                    Font.current_font[key] = value
        else:
            Font.current_font = {
                'font_name': "Segoe UI",
                'size_offset': -7,
                'support_utf8': 1,
                'width': 1.2,
                'x_offset': 4
            }

        if not len(Font.init):
            i = 0
            Font.init.append(False)
            for _ in Font.font_files:
                Font.init.append(False)
                i += 1
        if not Font.init[Font.current]:
            if ac.initFont(0, Font.current_font['font_name'], 0, 0) > 0:
                Font.init[Font.current] = True

    @staticmethod
    def get_font():
        return Font.current_font['font_name']

    @staticmethod
    def get_font_file_name():
        if Font.current > 0:
            return Font.font_files[Font.current - 1]['name']
        return 'Segoe UI'

    @staticmethod
    def get_font_width_adjust():
        return float(Font.current_font['width'])

    @staticmethod
    def get_support_font():
        if bool(int(Font.current_font['support_utf8'])):
            return Font.current_font['font_name']
        return "Segoe UI"

    @staticmethod
    def get_font_offset():
        return int(Font.current_font['size_offset'])

    @staticmethod
    def get_font_x_offset():
        return int(Font.current_font['x_offset'])

    @staticmethod
    def get_text_dimensions(text, height):
        class SIZE(ctypes.Structure):
            _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]
        points = Font.get_font_size(height+Font.get_font_offset())

        hdc = ctypes.windll.user32.GetDC(0)
        hfont = ctypes.windll.gdi32.CreateFontA(-32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Arial")
        #hfont = ctypes.windll.gdi32.CreateFontA(-points, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, Font.get_font())
        hfont_old = ctypes.windll.gdi32.SelectObject(hdc, hfont)
        size = SIZE(0, 0)
        ctypes.windll.gdi32.GetTextExtentPoint32A(hdc, text, len(text), ctypes.byref(size))
        ctypes.windll.gdi32.SelectObject(hdc, hfont_old)
        ctypes.windll.gdi32.DeleteObject(hfont)
        #ac.console("Name :" + str(points) + " : " + str(Font.get_font()) + " : " + str(size.cx) + " = " + str(size.cx / 32 * points * Font.get_font_width_adjust()))
        #ac.console("Name :" + str(points) + " : " + str(Font.get_font()) + " : " + str(size.cx) + " = " + str(size.cx / 32 * points * Font.get_font_width_adjust()))
        #ac.log("Name :" + str(points) + " : " + str(Font.get_font()) + " : " + str(size.cx) + " = " + str(size.cx / 32 * points * Font.get_font_width_adjust()))
        #return size.cx
        #return size.cx * Font.get_font_width_adjust()
        return size.cx / 32 * points * Font.get_font_width_adjust()

    @staticmethod
    def get_font_size(row_height):
        if row_height >= 60:
            return int(row_height * 2 / 3)
        if row_height == 59 or row_height == 58:
            return 39
        if row_height == 57 or row_height == 56:
            return 38
        if row_height == 55 or row_height == 54:
            return 37
        if row_height == 53 or row_height == 52:
            return 36
        if row_height == 52 or row_height == 51:
            return 35
        if row_height == 50 or row_height == 49:
            return 34
        if row_height == 48 or row_height == 47:
            return 33
        if row_height == 46 or row_height == 45:
            return 32
        if row_height == 44 or row_height == 43:
            return 31
        if row_height == 42:
            return 30
        if row_height == 41:
            return 29
        if row_height == 40:
            return 28
        if row_height == 39:
            return 27
        if row_height == 38 or row_height == 37:
            return 26
        if row_height == 36 or row_height == 35:
            return 25
        if row_height == 34:
            return 24
        if row_height == 33:
            return 23
        if row_height == 32 or row_height == 31:
            return 22
        if row_height == 30 or row_height == 29:
            return 21
        if row_height == 28:
            return 19
        if row_height == 27:
            return 19
        if row_height == 26:
            return 19
        if row_height == 25:
            return 18
        if row_height == 24 or row_height == 23:
            return 17
        if row_height == 22:
            return 16
        if row_height == 21:
            return 15
        if row_height == 20:
            return 14
        if row_height < 30:
            return row_height - 6
        return 26


class Laps:
    def __init__(self, lap, valid, time):
        self.lap = lap
        self.valid = valid
        self.time = time


class lapTimeStart:
    def __init__(self, lap, time, lastpit):
        self.lap = lap
        self.time = time
        self.lastpit = lastpit

class CarClass:
    def __init__(self, app, identifier, title, ui_row_height, offset, color):
        self.identifier=identifier
        self.title=title
        self.active=True
        self.w = 0
        self.h = 0
        self.lbl_title_bg = Label(app) \
            .set(w=35, h=20,
                 x=0, y=-ui_row_height,
                 opacity=1)
        self.lbl_title_txt = Label(app, title) \
            .set(w=35, h=0,
                 x=0, y=-ui_row_height + Font.get_font_x_offset(),
                 font_size=12,
                 align="center",
                 opacity=0)
        self.lbl_title_border = Label(app) \
            .set(w=35, h=2,
                 x=0, y=-2,
                 background=color, opacity=Colors.tower_border_default_bg_opacity())
        self.lbl_title_bg.setAnimationMode("x", "spring")
        self.lbl_title_txt.setAnimationMode("x", "spring")
        self.lbl_title_border.setAnimationMode("x", "spring")
        self.redraw_size(ui_row_height, offset)
        self.partial_func = functools.partial(self.on_click_func, identifier=self.identifier)
        ac.addOnClickedListener(self.lbl_title_bg.label, self.partial_func)

    @classmethod
    def on_click_func(*args, identifier=0):
        Colors.cars_classes_current = identifier

    def redraw_size(self,ui_row_height, offset):
        # set y axis, colors
        font_size = Font.get_font_size(ui_row_height + Font.get_font_offset())
        self.lbl_title_txt.update_font()
        self.w=len(self.title)*ui_row_height*18/36
        self.h = ui_row_height
        #self.w=ui_row_height * 49 / 36 + Font.get_text_dimensions(self.title, ui_row_height)
        self.lbl_title_bg.set(w=self.w, h=ui_row_height,
                 x=offset,
                 background=Colors.tower_class_bg(), animated=True, init=True)
        self.lbl_title_txt.set(w=self.w,
                 x=offset,
                 font_size=font_size,
                 color=Colors.tower_class_txt(),animated=True, init=True)
        self.lbl_title_border.set(w=self.w,
                 x=offset, opacity=Colors.tower_border_default_bg_opacity(),
                 animated=True)

    def animate(self):
        self.lbl_title_bg.animate()
        self.lbl_title_txt.animate()
        self.lbl_title_border.animate()

    def show(self):
        self.lbl_title_bg.show()
        self.lbl_title_txt.show()
        self.lbl_title_border.show()

    def hide(self):
        self.lbl_title_bg.hide()
        self.lbl_title_txt.hide()
        self.lbl_title_border.hide()

    def setX(self, x):
        self.lbl_title_bg.setX(x, animated=True)
        self.lbl_title_txt.setX(x, animated=True)
        self.lbl_title_border.setX(x, animated=True)

    def setY(self,y):
        self.lbl_title_bg.setY(y, animated=True)
        self.lbl_title_txt.setY(y + Font.get_font_x_offset(), animated=True)
        self.lbl_title_border.setY(y + self.h - 2, animated=True)

class MyHTMLParser(HTMLParser):
    html_table = 0
    logging_html = False
    line = []
    data = []
    tmp_data = ""
    b = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.__class__.html_table += 1
            if self.__class__.html_table > 1:
                self.__class__.logging_html = True

    def handle_endtag(self, tag):
        if tag == "table":
            self.__class__.logging_html = False
        elif self.__class__.logging_html and tag == "tr" and len(self.__class__.line) > 0:
            self.__class__.data.append(self.__class__.line)
            self.__class__.line = []
            self.__class__.tmp_data = ""
        elif self.__class__.logging_html and tag == "td":
            self.__class__.line.append(self.__class__.tmp_data)
            self.__class__.tmp_data = ""

    def handle_data(self, data):
        if self.__class__.logging_html:
            self.__class__.tmp_data = data

class HTMLParserPing(HTMLParser):
    html_table = 0
    logging_html = False
    line = []
    data = []
    tmp_data = ""
    b = 0

    def reset_data(self):
        HTMLParserPing.html_table = 0
        HTMLParserPing.logging_html = False
        HTMLParserPing.line = []
        HTMLParserPing.data = []
        HTMLParserPing.tmp_data = ""
        HTMLParserPing.b = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.__class__.html_table += 1
            if self.__class__.html_table > 1:
                self.__class__.logging_html = False
            else:
                self.__class__.logging_html = True

    def handle_endtag(self, tag):
        if tag == "table":
            self.__class__.logging_html = False
        elif self.__class__.logging_html and tag == "tr" and len(self.__class__.line) > 0:
            self.__class__.data.append(self.__class__.line)
            self.__class__.line = []
            self.__class__.tmp_data = ""
        elif self.__class__.logging_html and tag == "td":
            self.__class__.line.append(self.__class__.tmp_data)
            self.__class__.tmp_data = ""

    def handle_data(self, data):
        if self.__class__.logging_html:
            self.__class__.tmp_data = data

class GameData:
    def __init__(self):
        self.status=-1
        self.session=-1
        self.sessionTimeLeft=0
        self.flag=-1
        self.beforeRaceStart=False
        self.focusedCar=0
        self.cursor_x=0
        self.cursor_y=0

    def update(self, sim_info):
        self.session = sim_info.graphics.session
        self.sessionTimeLeft = sim_info.graphics.sessionTimeLeft
        if math.isinf(self.sessionTimeLeft):
            self.sessionTimeLeft=0
        self.status=sim_info.graphics.status
        self.flag=sim_info.graphics.flag
        self.focusedCar=ac.getFocusedCar()
        self.beforeRaceStart = self.status == 2 and sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0
        pt = POINT()
        if ctypes.windll.user32.GetCursorPos(ctypes.byref(pt)):
            self.cursor_x=pt.x
            self.cursor_y=pt.y

class Translate:
    def drivername(name):
        # ac.console("acc driver:translating name: %s " % name)
        dicNames = {}
        file_path = os.path.join(os.path.dirname(__file__), 'names.txt')
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split(':')
                dicNames[key.lower()] = value

        lower_name = name.lower()
        # ac.log("ACC Driver:translating name: %s " % dicNames.get(lower_name, name))
        # return dicNames.get(lower_name, name).upper()
        return dicNames.get(lower_name, name)