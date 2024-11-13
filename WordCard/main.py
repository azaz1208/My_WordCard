from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.core.text import LabelBase
import uuid
import json


Window.size = (400, 600)

class WordCard_layout(MDBoxLayout):
    text = StringProperty("")
    card_uuid = StringProperty("")
    
class Plus_WordCard_layout(MDBoxLayout):
    text = StringProperty("")
    card_id = StringProperty("")
    
class AddCardDialog_Content(MDBoxLayout):
    pass

class WordCard_Dialog_Content(MDBoxLayout):
    word = StringProperty("")
    meaning = StringProperty("")
    sentence = StringProperty("")

class MainApp(MDApp):
    filename = "wordcard_data.json"
    # sum_dict = {}
    
    def build(self):
        LabelBase.register(name="kose", fn_regular="./fonts/Kosefont-JP.ttf")

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        return Builder.load_file('my_layout.kv')
    
    def on_start(self):
        # get sum_dict from json
        try:
            sum_dict = self.read_file(self.filename)
            card_uuids = list(sum_dict.keys())

            for i in range(len(card_uuids)):
                card_uuid = card_uuids[i]
                word = sum_dict[card_uuid][0]
                self.root.ids.wordCard_area.add_widget(WordCard_layout(text=word, card_uuid = card_uuid))
        except:
            with open(self.filename, "w") as file:
                json.dump({}, file)
    
    def read_file(self, filename):
        with open(filename, 'r') as f:
            rea = json.load(f)
        return rea
        
    def write_file(self, filename, data):
        with open(filename, 'w') as f:
            json.dump(data,f, indent=4)

    def update_file(self, filename, data):
        rea = self.read_file(filename)
        rea.update(data)
        self.write_file(filename, rea)

    def show_add_card_dialog(self):
        print("az")
        self.root.ids.wordCard_area.add_widget(WordCard_layout(text="Word Card"))

    # 彈出新增字卡的視窗
    def show_add_card_dialog(self):
        self.dialog = MDDialog(
            title = "Add new word",
            content_cls = AddCardDialog_Content(),
            type = "custom",

            buttons = [
                MDFlatButton(
                    text = "CANCEL",
                    on_release = self.close_dialog
                ),
                MDFlatButton(
                    text = "ADD",
                    on_release = self.add_card
                )
            ]
        )
        self.dialog.open()

    def save_card_data(self):
        # save the word, meaning, sentence to a dict
        word = self.dialog.content_cls.ids.word_input.text
        meaning = self.dialog.content_cls.ids.meaning_input.text
        sentence = self.dialog.content_cls.ids.sentence_input.text
        
        wordCard_uuid = str(uuid.uuid4())

        self.update_file(self.filename, {wordCard_uuid: (word, meaning, sentence)})

        return wordCard_uuid

    def add_card(self, *obj):
        # save card
        card_uuid = self.save_card_data()

        # add a new word card to the screen
        word = self.dialog.content_cls.ids.word_input.text
        self.root.ids.wordCard_area.add_widget(WordCard_layout(text=word, card_uuid = card_uuid))
        print(f"Card Added! UUID: {card_uuid}")
        self.close_dialog()
        
    def close_dialog(self, *obj):
        self.dialog.dismiss()
        self.dialog = None

    def last_dialog(self, card_uuid):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None

        # get sum_dict from .json
        sum_dict = self.read_file(self.filename)
        
        total_key_list = list(sum_dict.keys())

        # 檢查保護機制，如果uuid不在total_key_list裡，避免引發error直接後面掛掉
        if card_uuid not in total_key_list:
            return
        
        card_index = total_key_list.index(card_uuid)
        last_card_index = card_index - 1
        last_card_uuid = total_key_list[last_card_index]
        # print(last_card_uuid)

        self.on_wordCard_label_press(last_card_uuid)

    def next_dialog(self, card_uuid):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None

        # get sum_dict from .json
        sum_dict = self.read_file(self.filename)

        total_key_list = list(sum_dict.keys())

        # 檢查保護機制，如果uuid不在total_key_list裡，避免引發error直接後面掛掉
        if card_uuid not in total_key_list:
            return
        
        card_index = total_key_list.index(card_uuid)
        if card_index == len(total_key_list)-1:
            next_card_index = 0
        else : 
            next_card_index = card_index + 1

        next_card_uuid = total_key_list[next_card_index]
        # print(last_card_uuid)

        self.on_wordCard_label_press(next_card_uuid)

    def edit_dialog(self, card_uuid):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None

        # get sum_dict from .json
        sum_dict = self.read_file(self.filename)

        word = sum_dict[card_uuid][0]
        meaning = sum_dict[card_uuid][1]
        sentence = sum_dict[card_uuid][2]

        d_content = AddCardDialog_Content()
        d_content.ids.word_input.text = word
        d_content.ids.meaning_input.text = meaning
        d_content.ids.sentence_input.text = sentence

        self.dialog = MDDialog(
            title = "Edit word",
            content_cls = d_content,
            type = "custom",

            buttons = [
                MDFlatButton(
                    text = "CANCEL",
                    on_release = self.close_dialog
                ),
                MDFlatButton(
                    text = "SAVE",
                    on_release = lambda az : self.save_edit_card(card_uuid)
                )
            ]
        )
        self.dialog.open()

    def save_edit_card(self, card_uuid):
        word = self.dialog.content_cls.ids.word_input.text
        meaning = self.dialog.content_cls.ids.meaning_input.text
        sentence = self.dialog.content_cls.ids.sentence_input.text

        # 存取編輯後的資料到.json
        self.update_file(self.filename, {card_uuid: (word, meaning, sentence)})
        self.close_dialog()

        # 更新 wordcard label
        for card in self.root.ids.wordCard_area.children:
            if card.card_uuid == card_uuid:
                card.text = word
                break

        # print(f"card Data updated: {self.sum_dict}")

        self.on_wordCard_label_press(card_uuid)
        
    

    def on_wordCard_label_press(self, card_uuid):
        # get sum_dict from json
        sum_dict = self.read_file(self.filename)

        word = sum_dict[card_uuid][0]
        meaning = f"meaning : \n {sum_dict[card_uuid][1]}"
        sentence = f"sentence : \n {sum_dict[card_uuid][2]}"

        self.dialog = MDDialog(
            # title = word,
            content_cls = WordCard_Dialog_Content(word = word, meaning = meaning, sentence = sentence),
            type = "custom",

            buttons = [
                # 要用到lambda （匿名函式）再隨便打個東西，函式名稱裡面就可以給值進去，在目前此情境的on_release需要傳參數進去，所以需要用到匿名函式
                MDFlatButton(
                    text = "LAST",
                    on_release = lambda az : self.last_dialog(card_uuid)
                ),
                MDFlatButton(
                    text = "NEXT",
                    on_release = lambda az : self.next_dialog(card_uuid)
                ),
                MDFlatButton(
                    text = "EDIT",
                    on_release = lambda az : self.edit_dialog(card_uuid)
                ),
                MDFlatButton(
                    text = "CANCEL",
                    on_release = self.close_dialog
                )
            ]
        )
        self.dialog.open()

    def close_app(self):
        MDApp.get_running_app().stop()


        
        


if __name__ == '__main__':
    MainApp().run() 