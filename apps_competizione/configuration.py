import ac
import apps_competizione.util.win32con, ctypes, ctypes.wintypes
import threading
import time
from .util.classes import Window, Button, Label, Value, POINT, Config, Log, Font, Colors
from .util.func import rgb


class Configuration:
    configChanged = False
    tabChanged = False
    currentTab = 1
    race_mode = 0
    qual_mode = 0
    names = 3
    lapCanBeInvalidated = 1
    forceInfoVisible = 0
    save_delta = 1
    max_num_cars = 10
    ui_row_height = 36
    theme_red = 224
    theme_green = 0
    theme_blue = 0
    tower_highlight = 0
    theme_ini = 'apps/python/actv_competizione/themes/cp.ini'

    # INITIALIZATION
    def __init__(self):
        self.visual_timeout = -1
        self.session = Value(-1)
        self.listen_active = True
        Colors.load_themes()
        Font.load_fonts()



        self.window = Window(name="ACTV CP Config", icon=False, width=251, height=470, texture="").setBgOpacity(0)

        y = 50
        self.spin_race_mode = ac.addSpinner(self.window.app, "Race tower mode :")
        ac.setRange(self.spin_race_mode, 0, 8)
        ac.setPosition(self.spin_race_mode, 20, y)
        ac.setValue(self.spin_race_mode, self.__class__.race_mode)
        ac.addOnValueChangeListener(self.spin_race_mode, self.on_spin_race_mode_changed)
        self.lbl_race_mode = Label(self.window.app, "Auto")\
            .setSize(120, 26).setPos(186, y - 28)\
            .setFontSize(12).setAlign("left")\
            .setVisible(1)

        y += 70
        self.spin_qual_mode = ac.addSpinner(self.window.app, "Qual tower mode :")
        ac.setRange(self.spin_qual_mode, 0, 4)
        ac.setPosition(self.spin_qual_mode, 20, y)
        ac.setValue(self.spin_qual_mode, self.__class__.qual_mode)
        ac.addOnValueChangeListener(self.spin_qual_mode, self.on_spin_qual_mode_changed)
        self.lbl_qual_mode = Label(self.window.app, "Gaps")\
            .setSize(120, 26).setPos(186, y - 28)\
            .setFontSize(12).setAlign("left")\
            .setVisible(1)

        y += 70
        self.spin_num_cars = ac.addSpinner(self.window.app, "Number cars tower")
        ac.setRange(self.spin_num_cars, 6, 80)
        ac.setPosition(self.spin_num_cars, 20, y)
        ac.setValue(self.spin_num_cars, self.__class__.max_num_cars)
        ac.addOnValueChangeListener(self.spin_num_cars, self.on_spin_num_cars_changed)

        y += 70
        self.spin_row_height = ac.addSpinner(self.window.app, "Row height")
        ac.setRange(self.spin_row_height, 26, 80)
        ac.setPosition(self.spin_row_height, 20, y)
        ac.setValue(self.spin_row_height, self.__class__.ui_row_height)
        ac.addOnValueChangeListener(self.spin_row_height, self.on_spin_row_height_changed)

        # Names mode
        y += 70
        self.spin_names = ac.addSpinner(self.window.app, "Names :")
        ac.setRange(self.spin_names, 0, 4)
        ac.setPosition(self.spin_names, 20, y)
        ac.setValue(self.spin_names, self.__class__.names)
        ac.addOnValueChangeListener(self.spin_names, self.on_spin_names_changed)
        self.lbl_names = Label(self.window.app, "TLC") \
            .setSize(120, 26).setPos(150, y - 28) \
            .setFontSize(12).setAlign("left") \
            .setVisible(1)

        y += 52
        self.chk_force_info = ac.addCheckBox(self.window.app, "")
        ac.setPosition(self.chk_force_info, 20, y)
        ac.addOnCheckBoxChanged(self.chk_force_info, self.on_check_force_info_changed)
        self.lbl_title_force_info = Label(self.window.app, "Info always visible")\
            .setSize(200, 26).setPos(65, y + 1)\
            .setFontSize(16).setAlign("left")\
            .setVisible(1)

        y += 33
        self.chk_save_delta = ac.addCheckBox(self.window.app, "")
        ac.setPosition(self.chk_save_delta, 20, y)
        ac.addOnCheckBoxChanged(self.chk_save_delta, self.on_check_save_delta_changed)
        self.lbl_title_save_delta = Label(self.window.app, "Save delta between sessions")\
            .setSize(200, 26).setPos(65, y + 3)\
            .setFontSize(14).setAlign("left")\
            .setVisible(1)

        self.cfg_loaded = False
        self.cfg = Config("apps/python/actv_competizione/", "config.ini")
        self.load_cfg()

        # thread
        self.key_listener = threading.Thread(target=self.listen_key)
        self.key_listener.daemon = True
        self.key_listener.start()

    def __del__(self):
        self.listen_active = False

    def load_cfg(self):
        self.__class__.forceInfoVisible = self.cfg.get("SETTINGS", "force_info_visible", "int")
        if self.__class__.forceInfoVisible == -1:
            self.__class__.forceInfoVisible = 0
        self.__class__.save_delta = self.cfg.get("SETTINGS", "save_delta", "int")
        if self.__class__.save_delta == -1:
            self.__class__.save_delta = 1
        self.__class__.max_num_cars = self.cfg.get("SETTINGS", "num_cars_tower", "int")
        if self.__class__.max_num_cars == -1:
            self.__class__.max_num_cars = 10
        self.__class__.ui_row_height = self.cfg.get("SETTINGS", "ui_row_height", "int")
        if self.__class__.ui_row_height == -1:
            user32 = ctypes.windll.user32
            window_height = user32.GetSystemMetrics(1)
            if window_height >= 2000:  # 4k
                self.__class__.ui_row_height = 76
            elif window_height >= 1400:  # 2k
                self.__class__.ui_row_height = 57
            else: # 1080p
                self.__class__.ui_row_height = 38
        self.__class__.race_mode = self.cfg.get("SETTINGS", "race_mode", "int")
        if self.__class__.race_mode == -1:
            self.__class__.race_mode = 1
        self.__class__.qual_mode = self.cfg.get("SETTINGS", "qual_mode", "int")
        if self.__class__.qual_mode == -1:
            self.__class__.qual_mode = 0
        self.__class__.names = self.cfg.get("SETTINGS", "names", "int")
        if self.__class__.names == -1:
            self.__class__.names = 3
        #font_ini = self.cfg.get("SETTINGS", "font_ini", "string")
        font_ini = "apps/python/actv_competizione/fonts/actvcpbold.ini"
        if font_ini != -1:
            Font.font_ini = font_ini
        else:
            Font.font_ini = ''

        if Font.font_ini != '' and len(Font.font_files):
            #  font number from ini
            for i in range(0, len(Font.font_files)):
                if Font.font_files[i]['file'] == Font.font_ini:
                    Font.set_font(i + 1)
                    break
        else:
            font = self.cfg.get("SETTINGS", "font", "int")
            if font == -1 or font > len(Font.font_files) - 1:
                font = 2  # Open Sans
            Font.set_font(font)
        Colors.theme_ini = theme_ini = 'apps/python/actv_competizione/themes/cp.ini'
        #theme_ini = self.cfg.get("SETTINGS", "theme_ini", "string")
        if theme_ini != -1:
            Colors.theme_ini = theme_ini
        else:
            Colors.theme_ini = ''

        if Colors.theme_ini != '' and len(Colors.theme_files):
            #  Get_theme number from ini
            for i in range(0, len(Colors.theme_files)):
                if Colors.theme_files[i]['file'] == Colors.theme_ini:
                    Colors.general_theme = i + 1
                    break
        else:
            general_theme = self.cfg.get("SETTINGS", "general_theme", "int")
            if general_theme >= 0:
                Colors.general_theme = general_theme

        ac.setValue(self.spin_race_mode, self.__class__.race_mode)
        ac.setValue(self.spin_qual_mode, self.__class__.qual_mode)
        ac.setValue(self.spin_names, self.__class__.names)
        ac.setValue(self.spin_num_cars, self.__class__.max_num_cars)
        ac.setValue(self.spin_row_height, self.__class__.ui_row_height)
        ac.setValue(self.chk_force_info, self.__class__.forceInfoVisible)
        ac.setValue(self.chk_save_delta, self.__class__.save_delta)
        self.set_labels()
        self.cfg_loaded = True

    def save_cfg(self):
        self.set_labels()
        self.cfg.set("SETTINGS", "race_mode", self.__class__.race_mode)
        self.cfg.set("SETTINGS", "qual_mode", self.__class__.qual_mode)
        self.cfg.set("SETTINGS", "names", self.__class__.names)
        self.cfg.set("SETTINGS", "force_info_visible", self.__class__.forceInfoVisible)
        self.cfg.set("SETTINGS", "save_delta", self.__class__.save_delta)
        self.cfg.set("SETTINGS", "num_cars_tower", self.__class__.max_num_cars)
        self.cfg.set("SETTINGS", "ui_row_height", self.__class__.ui_row_height)
        #self.cfg.set("SETTINGS", "font_ini", Font.font_ini)
        #self.cfg.set("SETTINGS", "general_theme", Colors.general_theme)
        #self.cfg.set("SETTINGS", "theme_ini", Colors.theme_ini)

    def set_labels(self):
        # Qualifying mode
        if self.__class__.qual_mode == 0:
            self.lbl_qual_mode.setText("Gaps")
        elif self.__class__.qual_mode == 1:
            self.lbl_qual_mode.setText("Times")
        elif self.__class__.qual_mode == 2:
            self.lbl_qual_mode.setText("Tires")
        elif self.__class__.qual_mode == 3:
            self.lbl_qual_mode.setText("Compact")
        else:
            self.lbl_qual_mode.setText("Relative")
        # Race mode
        if self.__class__.race_mode == 0:
            self.lbl_race_mode.setText("Auto")
        elif self.__class__.race_mode == 1:
            self.lbl_race_mode.setText("Gaps")
        elif self.__class__.race_mode == 2:
            self.lbl_race_mode.setText("Intervals")
        elif self.__class__.race_mode == 3:
            self.lbl_race_mode.setText("Compact")
        elif self.__class__.race_mode == 4:
            self.lbl_race_mode.setText("Progress")
        elif self.__class__.race_mode == 5:
            self.lbl_race_mode.setText("Pit Stops")
        elif self.__class__.race_mode == 6:
            self.lbl_race_mode.setText("Tires")
        elif self.__class__.race_mode == 7:
            self.lbl_race_mode.setText("Off")
        else:
            self.lbl_race_mode.setText("Relative")

        # Names mode
        if self.__class__.names == 0:
            self.lbl_names.setText("TLC")
        elif self.__class__.names == 1:
            self.lbl_names.setText("TLC2")
        elif self.__class__.names == 2:
            self.lbl_names.setText("Last")
        elif self.__class__.names == 3:
            self.lbl_names.setText("F.Last")
        else:
            self.lbl_names.setText("First")

    def change_tab(self):
        if self.__class__.currentTab == 1:
            self.show_tab1()
        else:
            self.hide_tab1()

    def hide_tab1(self):
        ac.setVisible(self.spin_race_mode, 0)
        ac.setVisible(self.spin_qual_mode, 0)
        ac.setVisible(self.spin_names, 0)
        ac.setVisible(self.spin_num_cars, 0)
        ac.setVisible(self.spin_row_height, 0)
        ac.setVisible(self.chk_force_info, 0)
        ac.setVisible(self.chk_save_delta, 0)
        self.lbl_title_force_info.setVisible(0)
        self.lbl_title_save_delta.setVisible(0)
        self.lbl_race_mode.setVisible(0)
        self.lbl_qual_mode.setVisible(0)
        self.lbl_names.setVisible(0)

    def show_tab1(self):
        ac.setVisible(self.spin_race_mode, 1)
        ac.setVisible(self.spin_qual_mode, 1)
        ac.setVisible(self.spin_names, 1)
        ac.setVisible(self.spin_num_cars, 1)
        ac.setVisible(self.spin_row_height, 1)
        ac.setVisible(self.chk_force_info, 1)
        ac.setVisible(self.chk_save_delta, 1)
        self.lbl_title_force_info.setVisible(1)
        self.lbl_title_save_delta.setVisible(1)
        self.lbl_race_mode.setVisible(1)
        self.lbl_qual_mode.setVisible(1)
        self.lbl_names.setVisible(1)

    def manage_window(self):
        if self.session.hasChanged():
            self.visual_timeout = -1
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
            self.visual_timeout = time.time() + 6
        if self.visual_timeout != 0 and self.visual_timeout > time.time():
            self.window.setBgOpacity(0.6).border(0)
            if self.__class__.currentTab == 1:
                self.show_tab1()
        else:
            self.window.setBgOpacity(0).border(0)
            if self.visual_timeout != 0:
                if self.__class__.currentTab == 1:
                    self.hide_tab1()
            self.visual_timeout = 0

    def on_update(self, sim_info):
        self.session.setValue(sim_info.graphics.session)
        self.manage_window()
        if self.__class__.tabChanged:
            self.change_tab()
            Configuration.tabChanged = False
        if self.__class__.configChanged and self.cfg_loaded:
            self.save_cfg()
            self.__class__.configChanged = False
            return True
        elif self.__class__.configChanged and not self.cfg_loaded:
            self.__class__.configChanged = False
        return False

    def listen_key(self):
        try:
            # ctypes.windll.user32.RegisterHotKey(None, 1, 0, apps_competizione.util.win32con.VK_F7)
            ctypes.windll.user32.RegisterHotKey(None, 1, apps_competizione.util.win32con.MOD_CONTROL, 0x57)  # CTRL+W
            msg = ctypes.wintypes.MSG()
            while self.listen_active:
                if ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                    if msg.message == apps_competizione.util.win32con.WM_HOTKEY:
                        self.hotkey_pressed()
                    ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                    ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
        except:
            Log.w("Error")
        finally:
            ctypes.windll.user32.UnregisterHotKey(None, 1)

    def hotkey_pressed(self):
        if self.session.value == 2:
            if self.__class__.race_mode >= 8:
                self.__class__.race_mode = 0
            else:
                self.__class__.race_mode += 1
            ac.setValue(self.spin_race_mode, self.__class__.race_mode)
        else:
            if self.__class__.qual_mode >= 4:
                self.__class__.qual_mode = 0
            else:
                self.__class__.qual_mode += 1
            ac.setValue(self.spin_qual_mode, self.__class__.qual_mode)
        self.__class__.configChanged = True

    @staticmethod
    def on_check_force_info_changed(name, state):
        Configuration.forceInfoVisible = state
        Configuration.configChanged = True

    @staticmethod
    def on_check_save_delta_changed(name, state):
        Configuration.save_delta = state
        Configuration.configChanged = True

    @staticmethod
    def on_spin_num_cars_changed(value):
        Configuration.max_num_cars = value
        Configuration.configChanged = True

    @staticmethod
    def on_spin_row_height_changed(value):
        Configuration.ui_row_height = value
        Configuration.configChanged = True

    @staticmethod
    def on_spin_race_mode_changed(value):
        Configuration.race_mode = value
        Configuration.configChanged = True

    @staticmethod
    def on_spin_qual_mode_changed(value):
        Configuration.qual_mode = value
        Configuration.configChanged = True

    @staticmethod
    def on_spin_names_changed(value):
        Configuration.names = value
        Configuration.configChanged = True

    @staticmethod
    def on_tab1_press(a, b):
        if Configuration.currentTab != 1:
            Configuration.currentTab = 1
            Configuration.tabChanged = True
