import csv
import io
import threading
from urllib.request import Request, urlopen

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex

try:
    from plyer import tts
except ImportError:
    tts = None

# سنضع هنا رابط Google Sheets المنشور بصيغة CSV لاحقًا.
SHEET_CSV_URL = "PASTE_YOUR_GOOGLE_SHEETS_CSV_URL_HERE"


class EnglishApp(App):
    def build(self):
        self.title = "English Vocabulary"
        self.words = []
        self.word_index = 0
        self.loading = False

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12),
        )

        title = Label(
            text="Learn English",
            font_size="28sp",
            size_hint_y=None,
            height=dp(55),
            color=get_color_from_hex("#4B2E83"),
        )
        layout.add_widget(title)

        self.word_label = Label(
            text="اضغط على «تجديد القائمة» لتحميل الكلمات",
            font_size="25sp",
            halign="center",
            valign="middle",
            color=get_color_from_hex("#222222"),
        )
        self.word_label.bind(size=self.fit_text)
        layout.add_widget(self.word_label)

        self.meaning_label = Label(
            text="",
            font_size="24sp",
            halign="center",
            valign="middle",
            color=get_color_from_hex("#287A45"),
        )
        self.meaning_label.bind(size=self.fit_text)
        layout.add_widget(self.meaning_label)

        self.status_label = Label(
            text="جاهز",
            font_size="14sp",
            size_hint_y=None,
            height=dp(30),
        )
        layout.add_widget(self.status_label)

        navigation = BoxLayout(
            spacing=dp(10),
            size_hint_y=None,
            height=dp(54),
        )
        previous_button = Button(text="السابق", font_size="18sp")
        previous_button.bind(on_release=self.show_previous)
        next_button = Button(text="التالي", font_size="18sp")
        next_button.bind(on_release=self.show_next)
        navigation.add_widget(previous_button)
        navigation.add_widget(next_button)
        layout.add_widget(navigation)

        actions = BoxLayout(
            spacing=dp(10),
            size_hint_y=None,
            height=dp(58),
        )
        speak_button = Button(
            text="نطق الكلمة",
            font_size="17sp",
            background_color=get_color_from_hex("#D9C8F2"),
            color=get_color_from_hex("#24123D"),
        )
        speak_button.bind(on_release=self.speak_word)

        refresh_button = Button(
            text="تجديد القائمة",
            font_size="17sp",
            background_color=get_color_from_hex("#CDEED8"),
            color=get_color_from_hex("#173D26"),
        )
        refresh_button.bind(on_release=self.refresh_words)

        actions.add_widget(speak_button)
        actions.add_widget(refresh_button)
        layout.add_widget(actions)
        return layout

    def fit_text(self, label, size):
        label.text_size = size

    def show_message(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, halign="center", valign="middle"),
            size_hint=(0.88, 0.42),
        )
        popup.open()

    def refresh_words(self, *_):
        if self.loading:
            return

        if not SHEET_CSV_URL.startswith("https://docs.google.com/"):
            self.show_message(
                "إعداد رابط الجدول",
                "سنضع رابط Google Sheets المنشور بصيغة CSV في المتغير "
                "SHEET_CSV_URL داخل ملف main.py.",
            )
            return

        self.loading = True
        self.status_label.text = "جارٍ تحميل الكلمات..."
        threading.Thread(target=self.download_words, daemon=True).start()

    def download_words(self):
        try:
            request = Request(
                SHEET_CSV_URL,
                headers={"User-Agent": "EnglishVocabularyApp/1.0"},
            )
            with urlopen(request, timeout=20) as response:
                csv_text = response.read().decode("utf-8-sig")

            rows = list(csv.reader(io.StringIO(csv_text)))
            words = []

            for row_number, row in enumerate(rows):
                if len(row) < 2:
                    continue

                english = row[0].strip()
                arabic = row[1].strip()
                if not english or not arabic:
                    continue

                if row_number == 0 and english.lower() in (
                    "english", "word", "الكلمة", "الكلمة الإنجليزية"
                ):
                    continue

                words.append({"english": english, "arabic": arabic})

            if not words:
                raise ValueError(
                    "لم أجد كلمات. اجعل العمود الأول للكلمات الإنجليزية "
                    "والثاني للمعاني العربية."
                )

            Clock.schedule_once(lambda dt: self.finish_loading(words, None), 0)
        except Exception as error:
            message = str(error)
            Clock.schedule_once(
                lambda dt, msg=message: self.finish_loading(None, msg), 0
            )

    def finish_loading(self, words, error):
        self.loading = False

        if error:
            self.status_label.text = "تعذّر تحميل الكلمات"
            self.show_message(
                "مشكلة في التحميل",
                "تحقق من اتصال الإنترنت ورابط الجدول وإعدادات مشاركته.\n\n"
                + error,
            )
            return

        self.words = words
        self.word_index = 0
        self.status_label.text = f"تم تحميل {len(words)} كلمة"
        self.display_current_word()

    def display_current_word(self):
        if not self.words:
            self.word_label.text = "لا توجد كلمات محمّلة"
            self.meaning_label.text = ""
            return

        word = self.words[self.word_index]
        self.word_label.text = word["english"]
        self.meaning_label.text = word["arabic"]
        self.status_label.text = (
            f"الكلمة {self.word_index + 1} من {len(self.words)}"
        )

    def show_previous(self, *_):
        if self.words:
            self.word_index = (self.word_index - 1) % len(self.words)
            self.display_current_word()

    def show_next(self, *_):
        if self.words:
            self.word_index = (self.word_index + 1) % len(self.words)
            self.display_current_word()

    def speak_word(self, *_):
        if not self.words:
            self.show_message("لا توجد كلمة", "حمّل قائمة الكلمات أولًا.")
            return

        if tts is None:
            self.show_message(
                "النطق غير متاح",
                "خدمة النطق غير متاحة على هذا الجهاز.",
            )
            return

        try:
            tts.speak(self.words[self.word_index]["english"])
        except Exception as error:
            self.show_message("تعذّر النطق", str(error))


if __name__ == "__main__":
    EnglishApp().run()
