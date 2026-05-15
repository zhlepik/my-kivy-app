from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import Clock
from kivy.animation import Animation
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.core.window import Window

if platform != 'android':
    Window.size = (400, 720)

LANG_DATA = {
    "ru": {
        "uptime": "ВРЕМЯ РАБОТЫ",
        "energy": "ЗАРЯД",
        "diff": "Сессия",
        "warn_title": "Запуск",
        "warn_text": "Оптимизировано для Pixel. На других устройствах вид может отличаться.",
        "btn_ok": "ОК"
    },
    "en": {
        "uptime": "UPTIME",
        "energy": "BATTERY",
        "diff": "Session",
        "warn_title": "Launch",
        "warn_text": "Optimized for Pixel. UI may vary on other devices.",
        "btn_ok": "OK"
    }
}

KV = '''
<PixelCard@MDCard>:
    padding: "24dp"
    radius: [32, ]
    orientation: 'vertical'
    elevation: 0
    md_bg_color: 
        (0.12, 0.12, 0.14, 1) if app.theme_cls.theme_style == "Dark" \
        else (0.94, 0.94, 0.96, 1)

MDScreen:
    md_bg_color: 
        (0.05, 0.05, 0.05, 1) if self.theme_cls.theme_style == "Dark" \
        else (1, 1, 1, 1)

    MDBoxLayout:
        orientation: 'vertical'
        padding: ["24dp", "50dp", "24dp", "30dp"]
        spacing: "20dp"

        # Заголовок
        MDBoxLayout:
            adaptive_height: True
            MDLabel:
                text: "TimePix"
                font_style: "H4"
                bold: True
                theme_text_color: "Primary"
            
            MDBoxLayout:
                adaptive_width: True
                MDIconButton:
                    icon: "translate"
                    on_release: app.switch_lang()
                MDIconButton:
                    icon: "theme-light-dark"
                    on_release: app.switch_theme()

        # Карточка Времени
        PixelCard:
            size_hint_y: None
            height: "140dp"
            MDLabel:
                text: app.tr['uptime']
                font_style: "Overline"
                theme_text_color: "Secondary"
            MDLabel:
                id: uptime_label
                text: "00:00:00"
                font_style: "H3"
                theme_text_color: "Primary"

        # Карточка Батареи
        PixelCard:
            size_hint_y: None
            height: "220dp"
            spacing: "15dp"
            
            MDBoxLayout:
                adaptive_height: True
                MDLabel:
                    text: app.tr['energy']
                    font_style: "Overline"
                    theme_text_color: "Secondary"
                MDLabel:
                    id: battery_diff_label
                    text: "0%"
                    halign: "right"
                    font_style: "Caption"
                    theme_text_color: "Secondary"

            AnchorLayout:
                MDCard:
                    size_hint: (1, None)
                    height: "70dp"
                    radius: [20, ]
                    md_bg_color: (0.5, 0.5, 0.5, 0.1)
                    clip_children: True
                    
                    RelativeLayout:
                        MDCard:
                            id: battery_fill
                            size_hint: (0.1, 1)
                            radius: [18, ]
                            md_bg_color: app.battery_color
                        MDLabel:
                            id: battery_percent
                            text: "0%"
                            halign: "center"
                            bold: True
                            font_style: "H5"
                            theme_text_color: "Primary"

        MDWidget: # Пустое место

        # Инфо об устройстве
        MDLabel:
            id: device_info
            text: "Detecting..."
            halign: "center"
            font_style: "Caption"
            theme_text_color: "Secondary"
'''

class TimePixApp(MDApp):
    from kivy.properties import ColorProperty, DictProperty
    battery_color = ColorProperty([0.2, 0.8, 0.4, 1])
    tr = DictProperty({})

    def build(self):
        self.lang = "ru"
        self.tr = LANG_DATA[self.lang]
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        self.start_level = None
        return Builder.load_string(KV)

    def switch_theme(self):
        self.theme_cls.theme_style = "Light" if self.theme_cls.theme_style == "Dark" else "Dark"

    def switch_lang(self):
        self.lang = "en" if self.lang == "ru" else "ru"
        self.tr = LANG_DATA[self.lang]

    def on_start(self):
        self.get_device_details()
        Clock.schedule_interval(self.update_stats, 1)
        self.update_stats(0)

    def get_device_details(self):
        info = "PC / Windows"
        is_pixel = False
        
        if platform == 'android':
            try:
                from jnius import autoclass
                Build = autoclass('android.os.Build')
                Version = autoclass('android.os.Build$VERSION')
                model = Build.MODEL
                brand = Build.MANUFACTURER
                release = Version.RELEASE
                info = f"{brand} {model} | Android {release}"
                if "google" in brand.lower():
                    is_pixel = True
            except:
                info = "Android Device"

        self.root.ids.device_info.text = info
        if platform == 'android' and not is_pixel:
            Clock.schedule_once(self.show_simple_warn, 1)

    def show_simple_warn(self, dt):
        MDDialog(
            title=self.tr['warn_title'],
            text=self.tr['warn_text'],
            buttons=[MDFlatButton(text=self.tr['btn_ok'], on_release=lambda x: x.parent.parent.parent.parent.dismiss())]
        ).open()

    def update_stats(self, dt):
        level, uptime = 100, "00:00:00"
        
        if platform == 'android':
            try:
                from jnius import autoclass
                PA = autoclass('org.kivy.android.PythonActivity').mActivity
                BM = PA.getSystemService(autoclass('android.content.Context').BATTERY_SERVICE)
                level = BM.getIntProperty(autoclass('android.os.BatteryManager').BATTERY_PROPERTY_CAPACITY)
                ms = autoclass('android.os.SystemClock').elapsedRealtime()
                s = int(ms/1000)%60; m = int(ms/60000)%60; h = int(ms/3600000)
                uptime = f"{h:02d}:{m:02d}:{s:02d}"
            except: pass

        if self.start_level is None: self.start_level = level
        diff = level - self.start_level

        self.root.ids.uptime_label.text = uptime
        self.root.ids.battery_percent.text = f"{level}%"
        self.root.ids.battery_diff_label.text = f"{self.tr['diff']}: {'+' if diff>=0 else ''}{diff}%"

        # Цвета
        if level > 70: self.battery_color = [0.2, 0.7, 0.3, 1]
        elif level > 25: self.battery_color = [1, 0.7, 0.1, 1]
        else: self.battery_color = [0.9, 0.2, 0.2, 1]

        Animation(size_hint=(max(level/100, 0.1), 1), d=0.5, t='out_quad').start(self.root.ids.battery_fill)

if __name__ == '__main__':
    TimePixApp().run()