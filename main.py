from tkinter import *
from tkinter import simpledialog, messagebox, ttk
from pandas import *
from random import *
from gtts import gTTS
import pygame.mixer

BACKGROUND_COLOR = "#B1DDC6"
languages = ['French', 'Russian', 'Dutch', 'Japanese', 'Hindi', 'German', 'Spanish']
language = ""
current_card = {}
learn_lang = {}


"""this function is for generating next flashcard"""
def next_card():
    global current_card, flip_timer
    window.after_cancel(flip_timer) # it cancels previous timer
    current_card = choice(learn_lang) # randomly gets a record from the languages
    canvas.itemconfig(card_title, text=language, fill="black")
    canvas.itemconfig(card_text, text=current_card[language], fill="black")
    canvas.itemconfig(white_canvas, image=white_card)
    known_button.grid_remove() # removing cross and wrong buttons in the lang section
    unknown_button.grid_remove()
    flip_timer = window.after(3000, func=flip_card)  # starting the timer only after user spends 3s


"""Gives the meaning for the current word"""
def flip_card():
    canvas.itemconfig(card_title, text="English", fill="#FFFFFF")
    canvas.itemconfig(card_text, text=current_card["English"], fill="#FFFFFF")
    canvas.itemconfig(white_canvas, image=green_card)
    known_button.grid(row=1, column=1)
    unknown_button.grid(row=1, column=0)


def get_user_input():
    global language
    language = simpledialog.askstring("Language", "Enter the language you want to learn:").title()
    if language in languages:
        messagebox.showinfo("Selected Language", f"You chose to learn {language}")
    else:
        messagebox.showinfo("Error", "Sorry , that language isn't available right now")
        get_user_input()


"""if user knows the word , it will not be asked again"""
def known_answer():
    learn_lang.remove(current_card) # remove the current word from the file
    data = DataFrame(learn_lang)  # the dict is converted into dataframe
    data.to_csv(f"Learned-Data/words_to_learn_in_{language}.csv", index=False)
    next_card()  # the data is being converted to csv without index


"""Playing the pronunciation of the word using gTTs"""
def play(pronunciation):
    # if the mp3 exist , it will play else, create and play
    if not pygame.mixer.get_init():
        pygame.mixer.init() # initializing the mixer
    try:
        pygame.mixer.music.load(f"audio/{language}/{pronunciation}.mp3")  # loading the file
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.music.unload()
    except pygame.error:
        lang = "en"
        myobj = gTTS(text=pronunciation, lang=lang, slow=False)
        myobj.save(f"audio/{language}/{pronunciation}.mp3")
        pygame.mixer.music.load(f"audio/{language}/{pronunciation}.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()

"""when the next button is clicked, goes to next flash card """
def next_slide(popup):
    popup.destroy()
    next_card()


"""for showing popup for knowing the pronunciation"""
def show_pronunciation_popup(pronunciation):
    pronunciation_popup = Toplevel()
    pronunciation_popup.title("Pronunciation")
    pronunciation_popup.geometry("300x100")
    Label(pronunciation_popup, text=f"Pronunciation for {pronunciation} :").grid(row=0, column=0, columnspan=2, padx=50)
    play_button = Button(pronunciation_popup, text="Play", command=lambda: play(pronunciation))
    play_button.grid(row=1, column=0, pady=20, padx=50)
    next_button = Button(pronunciation_popup, text="Next", command=lambda: next_slide(pronunciation_popup))
    next_button.grid(row=1, column=1)


def wrong_answer():
    show_pronunciation_popup(current_card[language])


window = Tk()
window.title("Flashy")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)


canvas = Canvas(width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)
white_card = PhotoImage(file="images/card_front.png")
green_card = PhotoImage(file="images/card_back.png")
white_canvas = canvas.create_image(400, 263, image=white_card)
card_title = canvas.create_text(400, 150, text="", font=("Arial", 40, "italic"))
card_text = canvas.create_text(400, 260, text="", font=("Arial", 60, "bold"))
canvas.grid(row=0, column=0, columnspan=2)

button_images = {
    "cross": PhotoImage(file="images/wrong.gif"),
    "check": PhotoImage(file="images/right.gif")
}

"""Gif is used here as the gif will be more compatible when inside a function"""
cross_image = PhotoImage(file="images/wrong.gif")
known_button = Button(image=button_images["check"], highlightthickness=0, borderwidth=0, command=known_answer,
                          bg=BACKGROUND_COLOR)
check_image = PhotoImage(file="images/right.gif")
unknown_button = Button(image=button_images["cross"], borderwidth=0, highlightthickness=0, command=wrong_answer,
                            bg=BACKGROUND_COLOR)

get_user_input()

try:
    lang_data = read_csv(f"Learned-Data/words_to_learn_in_{language}.csv")
except FileNotFoundError:
    original_data = read_csv(f"data/{language}_words.csv")
    learn_lang = original_data.to_dict(orient="records")
else:
    learn_lang = lang_data.to_dict(orient="records")

flip_timer = window.after(3000, func=flip_card)

next_card()

window.mainloop()
