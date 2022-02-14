import tkinter as tk

from tkinter import *
from tkinter import filedialog

from translator_app_service import Translator

class TranslatorApp(tk.Tk):
    
    def __init__(self):
        super().__init__()

        self.open_status = False
        self.translator = Translator()

        w = 1000 # width for the Tk self
        h = 700 # height for the Tk self

        # Get screen width and height
        ws = self.winfo_screenwidth() # width of the screen
        hs = self.winfo_screenheight() # height of the screen

        # Calculate x and y coordinates for the Tk self window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)

        self.title('CTranslator')
        self.resizable(0,0)
        self.configure(bg='#949494')

        self.geometry(f'{w}x{h}+{int(x)}+{int(y)}')

        # Bind shortcuts
        self.bind_all('<Control-s>', self.save_file)
        self.bind_all('<F5>', self.run)

        # Create main frame
        self.main_frame = Frame(self)
        self.main_frame.pack(side=TOP, padx=2, pady=2)

        # Subsidiary frames
        self.text_input_frame = Frame(self.main_frame)
        self.text_input_frame.pack(side=LEFT)

        self.output_frame = Frame(self.main_frame)
        self.output_frame.pack(side=RIGHT)

        # Error output frame
        self.error_frame = Frame(self)
        self.error_frame.pack(side=BOTTOM, padx=2, pady=2)

        # Create scrollbars
        self.text_scroll = Scrollbar(self.text_input_frame)
        self.text_scroll.pack(side=RIGHT, fill=Y)

        self.output_scroll = Scrollbar(self.output_frame)
        self.output_scroll.pack(side=RIGHT, fill=Y)

        self.error_scroll = Scrollbar(self.error_frame)
        self.error_scroll.pack(side=RIGHT, fill=Y)

        # Create text box
        self.text_box = Text(self.text_input_frame, 
                        width=97, 
                        height=35,
                        font=('Courier', 10),
                        undo=True, 
                        yscrollcommand=self.text_scroll.set)

        self.text_box.pack()
        self.text_scroll.config(command=self.text_box.yview)

        # Create output
        self.output_box = Text(self.output_frame, 
                        width=25, 
                        height=35,
                        font=('Courier', 10), 
                        yscrollcommand=self.output_scroll.set)

        self.output_box.pack()
        self.output_scroll.config(command=self.output_box.yview)

        # Create error output
        self.error_box = Text(self.error_frame, 
                        width=122, 
                        height=10,
                        font=('Courier', 10), 
                        yscrollcommand=self.error_scroll.set)

        self.error_box.pack()
        self.error_scroll.config(command=self.error_box.yview)

        # Create menu
        self.top_bar = Menu(self)
        self.config(menu=self.top_bar)

        # Add file menu
        self.file_menu = Menu(self.top_bar, tearoff=False)
        self.top_bar.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='New', command=self.new_file)
        self.file_menu.add_command(label='Open', command=self.open_file)
        self.file_menu.add_command(label='Save', command=self.save_file)
        self.file_menu.add_command(label='Save As', command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Save Translation As')

        # Add run menu
        self.run_menu = Menu(self.top_bar, tearoff=False)
        self.top_bar.add_cascade(label='Run', menu=self.run_menu)
        self.run_menu.add_command(label='Run', command=self.run)


    # New file function
    def new_file(self):
        self.text_box.delete('1.0', END)
        self.output_box.delete('1.0', END)

        self.title('New File - CTranslator')

        self.open_status_name = False

    # Open file function
    def open_file(self):
        self.text_box.delete('1.0', END)
        self.output_box.delete('1.0', END)

        text_file = filedialog.askopenfilename(title='Open File', filetypes=[('C Files', '*.c')])

        if text_file:
            # Save the status
            self.open_status_name = text_file

        file_name = text_file.split('/')[-1]

        self.title(f'{file_name} - CTranslator')

        # Read file contents and show them
        file_contents = ''
        with open(text_file, 'r') as f:
            file_contents = f.read()
        
        self.text_box.insert(END, file_contents)


    # Save As file function
    def save_as_file(self):
        text_file = filedialog.asksaveasfilename(title='Save As', defaultextension='.*', filetypes=[('C Files', '*.c')])
        if text_file:
            self.open_status_name = text_file

            file_name = text_file.split('/')[-1]

            self.title(f'{file_name} - CTranslator')

            # Write text box contents to file
            with open(text_file, 'w') as f:
                f.write(self.text_box.get(1.0, END))


    # Save file function
    def save_file(self, event):
        if self.open_status_name:
            # Write text box contents to file
            with open(self.open_status_name, 'w') as f:
                f.write(self.text_box.get(1.0, END))
        else:
            self.save_as_file()
    

    # Run translator
    def run(self, event):
        code = self.text_box.get(1.0, END)

        if code != '\n':
            translation = self.translator.translate_code(code)

            self.output_box.delete('1.0', END)
            self.output_box.insert(END, translation)