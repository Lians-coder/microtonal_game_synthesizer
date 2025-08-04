import arcade as a
from arcade.gui.widgets.buttons import UIFlatButtonStyle
from arcade.gui import (
    UIAnchorLayout,
    UIBoxLayout,
    UIDropdown,
    UIFlatButton,
    UILabel,
    UISlider,
    UITextureToggle,
    UIView,
    UIGridLayout,
    UIManager,
)
from random import choice
from collections import defaultdict
import webbrowser
import wave

PITCH = 440

SCREEN_WIDTH  = 1220
SCREEN_HEIGHT = 800
TITLE         = "Microtonal Guessing Game"

DIATONIC   = ["C", "D", "E", "F", "G", "A", "B"]
CHROMATIC  = ["C♯|D♭", "D♯|E♭", None, "F♯|G♭", "G♯|A♭", "A♯|B♭", None]
MICROTONAL = ["C𝄲", "D𝄳", "D𝄲", "E𝄳", "E𝄲|F𝄳", None, "F𝄲", "G𝄳", "G𝄲", "A𝄳", "A𝄲", "B𝄳", "B𝄲|C𝄳", None]
micro = list(filter(lambda m: m, MICROTONAL))
SCALE_CHROMATIC  = [note for pair in zip(DIATONIC, CHROMATIC) for note in pair if note]
SCALE_MICROTONAL = [note for pair in zip(SCALE_CHROMATIC, micro) for note in pair if note]

TEX_TOGGLE_RED          = a.load_texture(":resources:gui_basic_assets/toggle/red.png")
TEX_TOGGLE_GREEN        = a.load_texture(":resources:gui_basic_assets/toggle/green.png")
TEX_CHECKBOX_CHECKED    = a.load_texture(":resources:gui_basic_assets/checkbox/blue_check.png")
TEX_CHECKBOX_UNCHECKED  = a.load_texture(":resources:gui_basic_assets/checkbox/empty.png")
# TEXT_WIDGET_EXPLANATION = textwrap.dedent("""
# ...
# """).strip()

SPRITE_SCALE = 0.8
SPRITE_POS_X = 112
SPRITE_POS_Y = 180
SPRITE_STEP  = 160
SPRITE_ANGLE = 5

FONT      = "Castellar"
FONT_MENU = "Agency FB"

GAME_VARIANT     = "Challenge"
SELECTED         = "All notes"
OCTAVE_MODIFIERS = [1,]
QUESTIONS        = 30

ANSWERS = []



class SliderDisable(UISlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enabled = True         
    def on_event(self, event):
        if not self.enabled:
            return
        return super().on_event(event)


class SideButton(UIFlatButton):
    def __init__(self, text, font=FONT_MENU, 
                 font_size=18, size_hint=(0.08, 0.05)):
        super().__init__()
        self.text = f"{text}"
        self.style = {
        "press": UIFlatButtonStyle(
            font_name=font,
            font_color=a.color.LEMON_CURRY,
            bg=a.color.JASMINE,
            font_size=font_size),
        "normal": UIFlatButtonStyle(            
            font_name=font,
            font_color=a.color.LEMON_CURRY,
            bg=a.color.FLORAL_WHITE,
            font_size=font_size),
        "hover": UIFlatButtonStyle(
            font_name=font,
            font_color=a.color.FLORAL_WHITE,
            bg=a.color.LEMON_CURRY,                        
            font_size=font_size)}
        self.size_hint = size_hint
   
   
class MenuView(UIView):
    def __init__(self):        
        super().__init__()
        self.ui.enable()
        self.background_color = a.color.FLORAL_WHITE       
        
        self.grid = UIGridLayout(
            horizontal_spacing=150, 
            vertical_spacing=80, 
            column_count=2, 
            row_count=4)
        self.anchor = UIAnchorLayout(children=[self.grid])
        self.ui.add(self.anchor)     
        
        self.open_github_button()
        self.open_about_button()  
        self.title()
        self.add_pitch_things()
        self.set_notes_selected()
        self.set_octave_checkboxes()
        self.set_game_variant()
        self.set_questions()
        self.start()
    
    def open_github_button(self):     
        button = self.anchor.add(
            SideButton(text="Author"),
            anchor_y="top",
            align_y=-128,
            anchor_x="left",
            align_x=250)
        @button.event("on_click")
        def on_click(_):
            webbrowser.open("https://github.com/Lians-coder")

    def open_about_button(self):
        button = self.anchor.add(
            SideButton(text="About"),
            anchor_y="top",
            align_y=-128,
            anchor_x="right",
            align_x=-250)
        @button.event("on_click")
        def on_click(_):
            webbrowser.open("https://github.com/Lians-coder/microtonal_game_synthesizer/readme.md")        
                
    def title(self):    
        title = UILabel(
            text="Menu Screen",
            font_name=FONT,
            font_size=32,
            text_color=a.color.GRAY)
        self.grid.add(title, column=0, column_span=2, row=0)
        
    def set_game_variant(self):          
        self.variant = UIDropdown(
            default="Challenge",
            options=["Challenge", "Training", "Synthesizer"])
        self.variant_warning = UILabel(
                    text="\n",
                    font_name=FONT_MENU,
                    font_size=19,
                    text_color=a.color.LEMON_CURRY)
        self.sync_game_variant()  
              
        self.grid.add(UIBoxLayout(
            align="center",
            space_between=20,
            children=[
                UILabel(
                    text="Game Variant",
                    font_name=FONT_MENU,
                    font_size=26,
                    text_color=a.color.GRAY),
                self.variant,
                self.variant_warning]),
            column=1, row=1)        
        
        @self.variant.event("on_change")
        def on_game_variant_change(event):  
            global GAME_VARIANT
            var = self.variant.value 
            GAME_VARIANT = var    
            if var == "Synthesizer":
                self.question_slider.enabled = False
                self.variant_warning.text = "All notes will be playable"
            else:
                self.question_slider.enabled = True
                if GAME_VARIANT == "Training":
                    self.variant_warning.text = "This mode will give you feedback"
                else:
                    self.variant_warning.text = "No feedback during the game"
        
    def set_notes_selected(self):
        self.notes = UITextureToggle(            
                on_texture=TEX_TOGGLE_GREEN,
                off_texture=TEX_TOGGLE_RED,
                value=True)                      
        self.sync_selected()        
        self.grid.add(UIBoxLayout(
            vertical=False,
            align="left",
            space_between=20,
            children=[
                UILabel(
                    text="Chromatic",
                    font_name=FONT_MENU,
                    font_size=26,
                    text_color=a.color.GRAY),
                self.notes,
                UILabel(
                    text="All notes",
                    font_name=FONT_MENU,
                    font_size=26,
                    text_color=a.color.GRAY)]),            
            column=0, row=3)
        
        @self.notes.event("on_change")
        def on_change_notes(event):
            global SELECTED
            if self.notes.value:
                SELECTED = "All notes"
            else:
                SELECTED = "Chromatic"                

    def set_octave_checkboxes(self):   
        self.oct_4 = UITextureToggle(
            on_texture=TEX_CHECKBOX_CHECKED,
            off_texture=TEX_CHECKBOX_UNCHECKED,
            width=52,
            height=52)
        self.oct_5 = UITextureToggle(
            on_texture=TEX_CHECKBOX_CHECKED,
            off_texture=TEX_CHECKBOX_UNCHECKED,
            width=52,
            height=52)
        self.oct_6 = UITextureToggle(
            on_texture=TEX_CHECKBOX_CHECKED,
            off_texture=TEX_CHECKBOX_UNCHECKED,
            width=52,
            height=52)                    
        self.sync_octave_checkboxes()                   
        self.grid.add(UIBoxLayout(
            vertical=False,
            align="center",
            space_between=20,
            children=[
                UILabel(
                    text="Octaves:",
                    font_name=FONT_MENU,
                    font_size=26,
                    text_color=a.color.GRAY),
                UIBoxLayout(children=[                    
                    UILabel(
                        text="4th",
                        font_name=FONT_MENU,
                        font_size=20,
                        text_color=a.color.GRAY),
                    self.oct_4,]),
                UIBoxLayout(children=[                    
                    UILabel(
                        text="5th",
                        font_name=FONT_MENU,
                        font_size=20,
                        text_color=a.color.GRAY),
                    self.oct_5,]),
                UIBoxLayout(children=[                    
                    UILabel(
                        text="6th",
                        font_name=FONT_MENU,
                        font_size=20,
                        text_color=a.color.GRAY),
                    self.oct_6,])]),
            column=0, row=2)
        
        global OCTAVE_MODIFIERS
        def set_octave_modifiers(state, modifier):
            if state:
                if modifier not in OCTAVE_MODIFIERS:
                    OCTAVE_MODIFIERS.append(modifier)
            else:
                if modifier in OCTAVE_MODIFIERS:
                    OCTAVE_MODIFIERS.remove(modifier)
            if len(OCTAVE_MODIFIERS) == 0:
                ch = choice([4, 5, 6])
                name = f"oct_{ch}"
                getattr(self, name).value = True           
                        
        @self.oct_4.event("on_change")
        def on_check_oct_4(event):
            set_octave_modifiers(self.oct_4.value, 1)                    
            
        @self.oct_5.event("on_change")
        def on_check_oct_5(event):
            set_octave_modifiers(self.oct_5.value, 2)  
            
        @self.oct_6.event("on_change")
        def on_check_oct_6(event):
            set_octave_modifiers(self.oct_6.value, 4)  
            
    def set_questions(self):           
        self.question_slider = SliderDisable(
            value=30,
            min_value=5,
            max_value=100,
            step=5)        
        self.sync_questions()        
        self.question_label = UILabel(
            text=f"Questions: {self.question_slider.value}",
            font_name=FONT_MENU,
            font_size=26,
            text_color=a.color.GRAY)
        self.grid.add(UIBoxLayout(
            align="center",
            space_between=20,
            children=[self.question_label, self.question_slider]),
            column=1, row=2)
        
        @self.question_slider.event("on_change")
        def on_slider_change(event):
            questions = int(self.question_slider.value)
            self.question_label.text = f"Questions: {questions}"
            global QUESTIONS
            QUESTIONS = questions
            
    def add_pitch_things(self):    
        self.pitch_slider = UISlider(
            value=440,
            min_value=400,
            max_value=480,
            step=1)
        self.sync_pitch()
        self.pitch_label = UILabel(
            text=f"Pitch: A = {PITCH} Hz",
            font_name=FONT_MENU,
            font_size=26,
            text_color=a.color.GRAY)
        self.grid.add(UIBoxLayout(
            align="center",
            space_between=20,
            children=[self.pitch_label, self.pitch_slider]),
            column=0,row=1)
        
        @self.pitch_slider.event("on_change")
        def on_slider_change(event):
            pitch = int(self.pitch_slider.value)
            self.pitch_label.text = f"Pitch: A = {pitch} Hz"
            global PITCH
            PITCH = pitch
            wave.set_frequencies(PITCH)
                    
    def start(self):   
        self.start_button = SideButton(
            text="Start", font=FONT, font_size=28, size_hint=(1, 1))
        self.grid.add(self.start_button, column=1, row=3)
        
        @self.start_button.event("on_click")
        def on_start(event):
            match GAME_VARIANT:
                case "Challenge":
                    game_view = Challenge()
                case "Training":
                    game_view = Training()
                case "Synthesizer":
                    game_view = Synthesizer()
                    
            game_view.setup()
            self.window.show_view(game_view)    

    def sync_pitch(self):
        self.pitch_slider.value = int(PITCH)
               
    def sync_octave_checkboxes(self):
        self.oct_4.value = 1 in OCTAVE_MODIFIERS
        self.oct_5.value = 2 in OCTAVE_MODIFIERS
        self.oct_6.value = 4 in OCTAVE_MODIFIERS   
            
    def sync_game_variant(self):
        self.variant.value = GAME_VARIANT        
    
    def sync_selected(self):
        self.notes.value = "All notes" in SELECTED
        
    def sync_questions(self):
        self.question_slider.value = int(QUESTIONS)         
                     
    def on_show_view(self):
        self.sync_octave_checkboxes()
        self.sync_pitch()
        self.sync_game_variant()
        self.sync_selected()
        self.sync_questions()
    

class Synthesizer(a.View):
    def __init__(self):
        super().__init__()
        self.window.background_color = a.color.OLD_LACE
        self.sprite_list = None
        self.sprite_dict = None
        self.sprite_dict_inverted = None
        self.labels = None
        
        # TODO: set ABOUT button with instructions + LINK to github
        # TODO: add musical output flow to allow several sounds at once + list all presses on top
        # TODO: add options to select octaves in the play process
                
    def setup(self):
        self.init_sprites_storages()
        self.create_diatonic()
        self.create_chromatic()
        self.create_microtonal()
        self.sprites_dict_inversion()
             
    def init_sprites_storages(self):
        self.sprite_list = a.SpriteList()  # <sprite_obj_list>
        self.sprite_dict = {}              # SD  {note : <sprite_obj>}
        self.sprite_dict_inverted = {}     # SDI {<sprite_obj> : note}
        self.labels = {}
       
    def create_diatonic(self, img="./assets/images/diatonic_regular.png", enabled=True):
        self.create_sprites_with_labels(
            notes=DIATONIC, sprite_img=img, font_size=30, enabled=enabled)     
        
    def create_chromatic(self, img="./assets/images/chromatic_regular.png", enabled=True):    
        self.create_sprites_with_labels(
            notes=CHROMATIC, sprite_img=img, x=0.5, y=1, enabled=enabled) 
        
    def create_microtonal(self, img="./assets/images/microtonal_regular.png", enabled=True):   
        self.create_sprites_with_labels(
            notes=MICROTONAL, sprite_img=img, 
            x=0.25, y=0.5, x_offset=0.5, rotation=True, off=[4, 12], font_size=22,
            enabled=enabled)                    
      
    def select_image_for_sprite(self, note):
        pass
    
    def create_sprites_with_labels(self, notes, **kwargs):
        positions = self.create_sprites(notes, **kwargs)
        for note, (x, y) in positions.items():
            self.create_label(x, y, text=note, note=note, font_size=kwargs.get("font_size", 26)) 
          
    def create_sprites(self, notes, 
                       x=0, y=0, x_offset=1, step=SPRITE_STEP,
                       sprite_img=None, scale=SPRITE_SCALE,
                       rotation=False, off=[],
                       enabled=True, **kwards):
        positions = {}
        
        for i, note in enumerate(notes):
            if not note:
                continue
            note_img = sprite_img or self.select_image_for_sprite(note)
            sprite = a.Sprite(note_img, scale=scale)
            
            sprite.is_enabled = enabled
            sprite.is_clicked = False            
            sprite.timer = 0.0
            
            sprite_x = SPRITE_POS_X + (x + i * x_offset) * step
            sprite_y = SPRITE_POS_Y + y * step
            sprite.position = sprite_x, sprite_y
            
            if rotation:
                angle = SPRITE_ANGLE
                if i % 2 == 1:
                    angle *= -1
                if i in off:
                    sprite_x += 0.25 * SPRITE_STEP
                    sprite_y -= 0.25 * SPRITE_STEP
                    angle = 0
                    sprite.position = sprite_x, sprite_y    
                sprite.angle = angle
   
            # TODO: add shades for each sprite
            
            self.sprite_list.append(sprite)
            self.sprite_dict[note] = sprite
            positions[note] = (sprite_x, sprite_y)
        return positions
        
    def create_label(
        self, sx, sy, text, note, 
        color=a.color.LIGHT_SLATE_GRAY, font_size=26, font=FONT, 
        ax="center", ay="center"):
        label = a.Text(
            text=text,
            x=sx,
            y=sy,
            color=color,
            font_size=font_size,
            font_name=font,
            anchor_x=ax,
            anchor_y=ay)
        self.labels[note] = label
                  
    def sprites_dict_inversion(self):
        self.sprite_dict_inverted = {v: k for k, v in self.sprite_dict.items()} 
             
    def on_draw(self, color=a.color.OLD_LACE):
        self.clear(color)
        self.sprite_list.draw()
        for label in self.labels.values():
            label.draw()
    
    def on_mouse_press(self, x, y, button, _, audio=True):
        if button == a.MOUSE_BUTTON_LEFT:
            colliding_sprites = a.get_sprites_at_point((x, y), self.sprite_list) 
            if colliding_sprites:
                s = colliding_sprites[-1]
                if s.is_enabled:
                    s.is_clicked = True
                    s.timer = 0.0
                    if audio:
                        note=self.sprite_dict_inverted[s]
                        self.play_note(note)                            
                       
    def play_note(self, note):
        wave.play_note(note,
            octave_modifiers=OCTAVE_MODIFIERS)  

    def on_key_press(self, symbol, _):
        if symbol == a.key.ESCAPE:
            game_view = MenuView()
            self.window.show_view(game_view)
        # TODO: add button that represent escape - to menu
        
        # TODO: add key bindings for each note        
        # if symbol == a.key.A:
        #     s = self.sprite_dict["A"]
        #     s.is_clicked = True
        #     self.play_on_sprite(s)
            
    def on_update(self, delta_time):
        for s in self.sprite_list:
            if s.is_clicked:
                self.animate_sprite(delta_time, s)
                
    def animate_sprite(self, dt, s, img=False):
        if img:
            self.sprite_img = self.select_image_for_sprite()
        t_half = 0.2
        sc = SPRITE_SCALE
        sc_change = 0.04
        s.timer += dt
        if s.timer < t_half:
            s.scale = sc + sc_change * (s.timer / t_half)
        elif s.timer < t_half * 2:
            s.scale = sc - sc_change * ((s.timer - t_half) / t_half)
        else:
            s.scale = sc
            s.is_clicked = False
    
                        
class Challenge(Synthesizer):
    def __init__(self):
        super().__init__()
        self.waiting_for_click = False
        self.note = ""  
        self.q = QUESTIONS
    
    def setup(self):
        self.init_sprites_storages()
        self.create_diatonic()
        self.create_chromatic()
        if SELECTED == "Chromatic":
            img = "./assets/images/microtonal_not_used.png"
            self.create_microtonal(img=img, enabled=False)
        else:
            self.create_microtonal()
        self.sprites_dict_inversion()
        
    def on_update(self, delta_time):
        super().on_update(delta_time)     
        while not self.waiting_for_click: 
            print(f"{self.q = }")       
            if self.q > 0:            
                if SELECTED == "All notes":
                    self.note = choice(SCALE_MICROTONAL)
                else:
                    self.note = choice(SCALE_CHROMATIC) 
                self.play_note(self.note)
                print(f"{self.note = }")
                self.waiting_for_click = True
                
    def set_stats(self, s):
        print("run stats")
        guess = self.sprite_dict_inverted[s]
        note_dict = {
            "note": self.note,
            "guess": guess,
            "correct": self.note == guess}
        print(f"{note_dict}")
        ANSWERS.append(note_dict)
             
    def on_mouse_press(self, x, y, button, _, audio=True):
        super().on_mouse_press(x, y, button, _, audio=False)
        if button == a.MOUSE_BUTTON_LEFT: 
            print("get mouse")
            colliding_sprites = a.get_sprites_at_point((x, y), self.sprite_list)
            if colliding_sprites:
                print("colliding sprites")
                s = colliding_sprites[-1]
                if s.is_enabled:
                    self.set_stats(s)
                    self.q -= 1 
                if self.q == 0:
                    game_view = StatisticsViev()
                    self.window.show_view(game_view)
                self.waiting_for_click = False
                
    # TODO: add questions left 
    

class Training(Challenge):
    # def __init__(self):        
    #     super().__init__()
        
    # TODO: addcheckbox to decide if the note selected should be playesd & formula for thereafter calculations of delay between notes
    # TODO set greenish value for bg     
    def animate_sprite(self, *args, **kwargs):
        super().animate_sprite(*args, img=True, **kwargs)
    
    # TODO: add blue for played and outline for checke
    def select_image_for_sprite(self):
        img = ...
        return img
    

class StatisticsViev(Synthesizer):
    def __init__(self):
        super().__init__()
        self.statistics = self.get_statistics()
        
        self.ui_manager = UIManager()
        self.grid = UIGridLayout(
            horizontal_spacing=150, 
            vertical_spacing=80, 
            column_count=1, 
            row_count=7)
        self.anchor = UIAnchorLayout(children=[self.grid])
        self.ui_manager.add(self.anchor)         
        self.title()
        self.overall_stats(stats=None)
        self.open_menu_button()
        self.new_game_button()
        self.setup()

    def title(self):    
        title = UILabel(
            text="Statistics",
            font_name=FONT,
            font_size=32,
            text_color=a.color.GRAY)
        self.grid.add(title, column=0, row=0)
        
    def overall_stats(self, stats):
        label = UILabel(
            text=f"Overall statistics: {stats}",
            font_name=FONT_MENU,
            font_size=28,
            text_color=a.color.GRAY)
        self.grid.add(label, column=0, row=1)
     
    def open_menu_button(self):
        self.open_menu_button = self.anchor.add(
            SideButton(text="Menu"),
            anchor_y="top",
            align_y=-128,
            anchor_x="left",
            align_x=250)        
        @self.open_menu_button.event("on_click")
        def on_start(event):
            game_view = MenuView()
            self.window.show_view(game_view)

    def new_game_button(self):
        self.new_game_button = self.anchor.add(
            SideButton(text="New Game"),
            anchor_y="top",
            align_y=-128,
            anchor_x="right",
            align_x=-250)
        @self.new_game_button.event("on_click")
        def on_start(event):
            match GAME_VARIANT:
                case "Challenge":
                    game_view = Challenge()
                case "Training":
                    game_view = Training()                 
            game_view.setup()
            self.window.show_view(game_view)    

    def create_sprites_with_labels(self, notes, **kwargs):
        positions = self.create_sprites(notes, **kwargs)
        for note, (x, y) in positions.items():
            if note not in self.statistics:
                text = ""
            else:
                acc = round(self.statistics[note]["accuracy"])
                text = f"{acc}%"
            self.create_label(x, y, text=text, note=note, font=FONT_MENU, font_size=kwargs.get("font_size", 26)) 
            
    def create_diatonic(self, img=None, enabled=False):
        super().create_diatonic(img=None, enabled=False)
        
    def create_chromatic(self, img=None, enabled=False):
        super().create_chromatic(img=None, enabled=False)
        
    def create_microtonal(self, img=None, enabled=False):
        super().create_microtonal(img=None, enabled=False)
        
    def select_image_for_sprite(self, note):
        print(f"{note = }")
        if note in DIATONIC:
            word = "diatonic"
        elif note in CHROMATIC:
            word = "chromatic"
        else:
            word = "microtonal"  
        print(f"{word = }") 
        if note not in self.statistics:
            img = f"./assets/images/{word}_not_used.png"
        else:
            stats = self.statistics[note]
            print(f"stats for {note} = {stats["accuracy"]}")
            if stats["accuracy"] >= 90:
                img = f"./assets/images/{word}_right.png"
            elif stats["accuracy"] <= 10:
                img = f"./assets/images/{word}_wrong.png"
            else:
                img = f"./assets/images/{word}_regular.png"
        print(f"{img = }")
        return img
    
    def on_draw(self):
        super().on_draw()
        self.ui_manager.draw()
                       
    @staticmethod          
    def get_statistics():
        statistics = defaultdict(lambda: {"played": 0, "correct": 0})    
        for entry in ANSWERS:
            note = entry["note"]
            statistics[note]["played"] += 1
            if entry["correct"]:
                statistics[note]["correct"] += 1                
        for note, stats in statistics.items():
            stats["accuracy"] = stats["correct"] / stats["played"] * 100
        return dict(statistics)
    # TODO: calculate overall statistics
    
    
    # TODO: make them functional - return to menu option + new game option

       
def main():
    window = a.Window(
        title=TITLE,
        width=SCREEN_WIDTH,
        height=SCREEN_HEIGHT)
    window.center_window()
    game = MenuView()
    window.show_view(game)
    a.run()
    
    
if __name__ == "__main__":
    main()