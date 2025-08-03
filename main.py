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
)
from random import randint, choice
# import textwrap
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

# TEX_SLIDER_THUMB_BLUE   = a.load_texture(":resources:gui_basic_assets/slider/thumb_blue.png")
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
SPRITE_ANGLE = 4

FONT      = "Castellar"
FONT_MENU = "Agency FB"

GAME_VARIANT     = "Challenge"
SELECTED         = ""
OCTAVE_MODIFIERS = [1,]
QUESTIONS        = 30

STATISTICS = []


class SliderDisable(UISlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enabled = True         
    def on_event(self, event):
        if not self.enabled:
            return
        return super().on_event(event)
    
    
class MenuView(UIView):
    def __init__(self):        
        super().__init__()
        self.ui.enable()
        self.background_color = a.color.LAVENDER_BLUSH
        
        # TODO: Add ABOUT button
        # TODO Add Statistics view - disabled if not played
        
        grid = UIGridLayout(
            horizontal_spacing=150, 
            vertical_spacing=80, 
            column_count=2, 
            row_count=4)         
        self.ui.add(UIAnchorLayout(children=[grid]))
            
        title = UILabel(
            text="Menu Screen",
            font_name=FONT,
            font_size=32,
            text_color=a.color.GRAY)
        grid.add(title, column=0, column_span=2, row=0)

        self.pitch_slider = UISlider(
            value=440,
            min_value=400,
            max_value=480,
            step=1)
        self.pitch_label = UILabel(
            text=f"Pitch: A = {PITCH} Hz",
            font_name=FONT_MENU,
            font_size=26,
            text_color=a.color.GRAY)
        grid.add(UIBoxLayout(
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

        self.variant = UIDropdown(
            default="Challenge",
            options=["Challenge", "Training", "Synthesizer"])
        self.sync_game_variant() 
        
        grid.add(UIBoxLayout(
            align="center",
            space_between=20,
            children=[
                UILabel(
                    text="Game Variant",
                    font_name=FONT_MENU,
                    font_size=26,
                    text_color=a.color.GRAY),
                self.variant]),
            column=1, row=1)        
        
        @self.variant.event("on_change")
        def on_game_variant_change(event):  
            var = self.variant.value     
            if var == "Synthesizer":
                self.question_slider.enabled = False
            else:
                self.question_slider.enabled = True
            global GAME_VARIANT
            GAME_VARIANT = var

        self.notes = UITextureToggle(            
                on_texture=TEX_TOGGLE_GREEN,
                off_texture=TEX_TOGGLE_RED,
                value=True)
        grid.add(UIBoxLayout(
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
                SELECTED = "all"
            else:
                SELECTED = "chromatic"
  
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
                
        grid.add(UIBoxLayout(
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
                    self.oct_6,])
                ]),
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
        
        self.question_slider = SliderDisable(
            value=30,
            min_value=5,
            max_value=100,
            step=5)
        self.question_label = UILabel(
            text="Questions: 30",
            font_name=FONT_MENU,
            font_size=26,
            text_color=a.color.GRAY)
        grid.add(UIBoxLayout(
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
            
        self.start_button = UIFlatButton(
            text="Start",
            style={
                "normal": UIFlatButtonStyle(
                    font_name=FONT,
                    font_size=22),
                "hover": UIFlatButtonStyle(
                    font_name=FONT,
                    font_color=a.color.LAVENDER_BLUSH,
                    bg=a.color.CANDY_PINK,
                    font_size=22),
                "press": UIFlatButtonStyle(
                    font_name=FONT,
                    font_color=a.color.GRAY,
                    bg=a.color.BUBBLE_GUM,                        
                    font_size=22),
                "disabled": UIFlatButtonStyle(
                    font_name=FONT,
                    font_size=22)},
            size_hint=(1, 1))
        grid.add(self.start_button, column=1, row=3)
        
        @self.start_button.event("on_click")
        def on_start(event):
            match GAME_VARIANT:
                case "Challenge":
                    game_view = Challenge()
                case "Training":
                    game_view = Training()
                case "Synthesizer":
                    game_view = Synthesizer()
            
            self.window.show_view(game_view)    
            
    def sync_octave_checkboxes(self):
            self.oct_4.value = 1 in OCTAVE_MODIFIERS
            self.oct_5.value = 2 in OCTAVE_MODIFIERS
            self.oct_6.value = 4 in OCTAVE_MODIFIERS   
            
    def sync_game_variant(self):
        self.variant.value = GAME_VARIANT
                 
    def on_show_view(self):
        self.sync_octave_checkboxes()
        self.sync_game_variant()


class Synthesizer(a.View):
    def __init__(self):
        super().__init__()
        self.window.background_color = a.color.LAVENDER_BLUSH
        
        # TODO: set ABOUT button with instructions + LINK to github
        # TODO: add musical output flow to allow several sounds at once + list all presses on top
        
        self.sprite_list = a.SpriteList()  # <sprite_obj_list>
        self.sprite_dict = {}              # {note : <sprite_obj>}
        self.sprite_dict_inverted = {}     # {<sprite_obj> : note}
        self.labels = {}
        
        self.create_sprites(notes=DIATONIC,
                            sprite_img="./assets/images/diatonic_regular.png", 
                            x=0, y=0, font_size=30)
        self.create_sprites(notes=CHROMATIC,
                            sprite_img="./assets/images/chromatic_regular.png", 
                            x=0.5, y=1)
        self.create_sprites(notes=MICROTONAL,
                            sprite_img="./assets/images/microtonal_regular.png", 
                            x=0.25, y=0.5, x_offset=0.5,
                            rotation=True, off=[4, 12],
                            font_size=22)
        
        self.sprites_dict_inversion()
    
    def select_image_for_sprite(self):
        pass
       
    def create_sprites(self, notes, sprite_img, # sprite_img=None
                       x=0, y=0, x_offset=1, step=SPRITE_STEP, scale=SPRITE_SCALE,
                       rotation=False, off=[],
                       font_size=26):
        """Create sprite and add corresponding label"""
        
        for i, note in enumerate(notes):
            if not note:
                continue
            # if not sprite_img:
            #     sprite_img = self.select_image_for_sprite()
            sprite = a.Sprite(sprite_img, scale=scale)
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
                
            sprite.is_clicked = False
            # TODO: add shades for each sprite
            
            self.sprite_list.append(sprite)
            self.sprite_dict[note] = sprite

            label_text = note
            label = a.Text(text=label_text,
                                x=sprite_x,
                                y=sprite_y,
                                color=a.color.LIGHT_SLATE_GRAY,
                                font_size=font_size,
                                font_name=FONT,
                                anchor_x="center",
                                anchor_y="center")
            self.labels[note] = label
               
    def sprites_dict_inversion(self):
        self.sprite_dict_inverted = {v: k for k, v in self.sprite_dict.items()} 
             
    def on_draw(self):
        self.clear(a.color.LAVENDER_BLUSH)
        self.sprite_list.draw()
        for label in self.labels.values():
            label.draw()
    
    def on_mouse_press(self, x, y, button, _, audio=True):
        if button == a.MOUSE_BUTTON_LEFT:
            colliding_sprites = a.get_sprites_at_point((x, y), self.sprite_list) 
            if colliding_sprites:
                s = colliding_sprites[-1]
                s.is_clicked = True
                s.timer = 0.0
            if audio:
                note=self.sprite_dict_inverted[s]
                self.play_note(note)                            
                       
    def play_note(self, note):
        wave.play_note(
            note,
            octave_modifiers=OCTAVE_MODIFIERS)  

    def on_key_press(self, symbol, _):
        if symbol == a.key.ESCAPE:
            game_view = MenuView()
            self.window.show_view(game_view)
        
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
    def on_mouse_press(self, x, y, button, _, audio=True):
        super().on_mouse_press(x, y, button, _, audio=False)
    
    for _ in QUESTIONS:
        if SELECTED == "all":
            note = SCALE_MICROTONAL[randint(0,23)]
        else:
            note = SCALE_CHROMATIC[randint(0,11)]
        ...
            
    
    
    

class Training(Challenge): 
    # TODO: addcheckbox to decide if the note selected should be playesd & formula for thereafter calculations of delay between notes
         
    def animate_sprite(self, *args, **kwargs):
        super().animate_sprite(*args, img=True, **kwargs)
    
    # TODO: add blue for played and outline for checke
    def select_image_for_sprite(self):
        img = ...
        return img           
    


class StatisticsViev(Synthesizer):
    # TODO statistics calculations + draw on sprites
    # def select_image_for_sprite(self):
    #     pass 
    # TODO: add ABOUT button
    # TODO: return to menu option
    # TODO: new game option
    pass

       
def main():
    window = a.Window(title=TITLE,
                           width=SCREEN_WIDTH,
                           height=SCREEN_HEIGHT)
    window.center_window()
    game = MenuView()
    window.show_view(game)
    a.run()
    
    
if __name__ == "__main__":
    main()