import tkinter as tk
from tkinter import filedialog
import pygame
import os
import subprocess
import sys
import time
import json

from translator import flow_to_code
from translation import TranslationException

os.system('cls' if os.name == 'nt' else 'clear')

root = tk.Tk()
root.geometry("800x600")
root.width = 800
root.height = 600
root.minsize(450, 450)
root.title("Python Flow - Editor flowchart per Python")

canvas = tk.Canvas(root, width=1, height=1)
canvas.configure(bg="gray")
canvas.pack(fill=tk.BOTH, expand=True)
canvas_origin = [0, 0]

node_connections = [] # una lista di coppie di nodi connessi
node_connections_classes = [] # una lista di coppie di classi connesse
nodes = [] # una lista di tutti i nodi (classi)
nodes_parent_classes = {} # un dizionario che associa un nodo (box) alla sua classe parente
if getattr(sys, 'frozen', False):
    sound_path = os.path.join(sys._MEIPASS, "sounds")
    temp_dir = os.path.join(sys._MEIPASS, "temp")
    help_pages_path = os.path.join(sys._MEIPASS, "help_pages.txt")
    icon = tk.PhotoImage(file=os.path.join(sys._MEIPASS, "icons\\icon.png"))
    nodes_path = os.path.join(sys._MEIPASS, "nodes.json")
    new_file_import = os.path.join(sys._MEIPASS, "assets\\model.pyf")
else:
    sound_path = os.path.join(os.path.dirname(__file__), "sounds")
    temp_dir = os.path.join(os.path.dirname(__file__), "temp")
    help_pages_path = os.path.join(os.path.dirname(__file__), "help_pages.txt")
    icon = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__), "icons\\icon.png"))
    nodes_path = os.path.join(os.path.dirname(__file__), "nodes.json")
    new_file_import = os.path.join(os.path.dirname(__file__), "assets\\model.pyf")
root.iconphoto(False, icon)
root.update_idletasks()

current_start_node = None
current_end_node = None

def play_sound(sound: str):
    pygame.mixer.init()
    pygame.mixer.music.load(f"{sound_path}\\{sound}.mp3")
    pygame.mixer.music.play()

declared_variables = []
nodes_scanned_for_declared_variables = []
variable_declared_by_node = {}
declared_functions = []
nodes_scanned_for_declared_functions = []
function_declared_by_node = {}
declared_lists = []
nodes_scanned_for_declared_lists = []
list_declared_by_node = {}

def check_for_declared_variables_or_functions():
    for node in nodes:
        if node.type == "variabledecl":
            if not node in nodes_scanned_for_declared_variables or not node.translate_items[0].get() == variable_declared_by_node[node]:
                try:
                    if not node.translate_items[0].get() == "":
                        try:
                            if not node.translate_items[0].get() == variable_declared_by_node[node]:
                                declared_variables.remove(variable_declared_by_node[node])
                        except:
                            pass
                        declared_variables.append(node.translate_items[0].get())
                        nodes_scanned_for_declared_variables.append(node)
                        variable_declared_by_node[node] = node.translate_items[0].get()
                except:
                    pass
        elif node.type == "defcallvar":
            if not node in nodes_scanned_for_declared_variables or not node.translate_items[2].get() == variable_declared_by_node[node]:
                try:
                    if not node.translate_items[2].get() == "":
                        try:
                            if not node.translate_items[2].get() == variable_declared_by_node[node]:
                                declared_variables.remove(variable_declared_by_node[node])
                        except:
                            pass
                        declared_variables.append(node.translate_items[2].get())
                        nodes_scanned_for_declared_variables.append(node)
                        variable_declared_by_node[node] = node.translate_items[2].get()
                except:
                    pass
        elif node.type == "def":
            if not node in nodes_scanned_for_declared_functions or not node.translate_items[0].get() == function_declared_by_node[node]:
                try:
                    if not node.translate_items[0].get() == "":
                        try:
                            if not node.translate_items[0].get() == function_declared_by_node[node]:
                                declared_functions.remove(function_declared_by_node[node])
                        except:
                            pass
                        declared_functions.append(node.translate_items[0].get())
                        nodes_scanned_for_declared_functions.append(node)
                        function_declared_by_node[node] = node.translate_items[0].get()
                except:
                    pass
        elif node.type == "listdecl":
            if not node in nodes_scanned_for_declared_lists or not node.translate_items[0].get() == list_declared_by_node[node]:
                try:
                    if not node.translate_items[0].get() == "":
                        try:
                            if not node.translate_items[0].get() == list_declared_by_node[node]:
                                declared_lists.remove(list_declared_by_node[node])
                        except:
                            pass
                        declared_lists.append(node.translate_items[0].get())
                        nodes_scanned_for_declared_lists.append(node)
                        list_declared_by_node[node] = node.translate_items[0].get()
                except:
                    pass
            if not node in nodes_scanned_for_declared_variables or not node.translate_items[0].get() == variable_declared_by_node[node]:
                try:
                    if not node.translate_items[0].get() == "":
                        try:
                            if not node.translate_items[0].get() == variable_declared_by_node[node]:
                                declared_variables.remove(variable_declared_by_node[node])
                        except:
                            pass
                        declared_variables.append(node.translate_items[0].get())
                        nodes_scanned_for_declared_variables.append(node)
                        variable_declared_by_node[node] = node.translate_items[0].get()
                except:
                    pass

    root.after(500, check_for_declared_variables_or_functions)

check_for_declared_variables_or_functions()

bigger_input = tk.Entry(canvas.master)
bigger_input.pack(fill=tk.X, side=tk.BOTTOM)

last_focused_widget = None
def update_bigger_input():
    global last_focused_widget
    focused_widget = root.focus_get()
    if isinstance(focused_widget, tk.Entry):
        bigger_input.pack(fill=tk.X, side=tk.BOTTOM)
        if focused_widget == bigger_input:
            if isinstance(last_focused_widget, tk.Entry):
                last_focused_widget.delete(0, tk.END)
                last_focused_widget.insert(0, focused_widget.get())
        else:
            bigger_input.delete(0, tk.END)
            bigger_input.insert(0, focused_widget.get())
    else:
        bigger_input.forget()
    if focused_widget != bigger_input:
        last_focused_widget = focused_widget
    root.after(20, update_bigger_input)

update_bigger_input()

if_condition_options = ["==", "!=", ">", "<", ">=", "<=", "è", "non è", "è in", "non è in"]
class Node:
    def __str__(self, mode):
        global if_condition_options
        if mode == "log":
            return f"Node(\nx: {self.x}\ny: {self.y}\ntype: {self.type}\nbox: {self.box}\nitems: {self.items}\ntranslate_items: {self.translate_items}\ncircles: {self.circles}\ncircle_types: {self.circle_types}\ncircle_io_types: {self.circle_io_types}\ncircles_is_connected: {self.circles_is_connected}\ncircle_connections: {self.circle_connections}\ncircles_line_connections: {self.circles_line_connections}\nlines_circle_connections: {self.lines_circle_connections}\ninput_circles_number: {self.input_circles_number}\noutput_circles_number: {self.output_circles_number}\n{f"condition_operator: {if_condition_options.index(self.if_condition_operator)}" if self.type == "if" or self.type == "while" else ''})"
        elif mode == "export":
            other_nodes = []
            for pair in node_connections_classes:
                if pair[0] == self:
                    other_nodes.append(pair[1])
                elif pair[1] == self:
                    other_nodes.append(pair[0])
            circle_connections_list = []
            for circle in self.circle_connections.keys():
                other_circle_type = None
                for node in other_nodes:
                    for circle2 in node.circles:
                        if circle == node.circle_connections[circle2]:
                            other_circle_type = node.circle_types[circle2]
                            break
                circle_connections_list.append([self.circle_types[circle], other_circle_type])
            input_texts = []
            for item in self.translate_items:
                if isinstance(item, tk.Entry):
                    input_texts.append(item.get())

            return f"{{id:{self.id},,x:{int(canvas.coords(self.box)[0])},,y:{int(canvas.coords(self.box)[1])},,type:{self.type},,circle_connections_list:{circle_connections_list},,input_circles_number:{self.input_circles_number},,output_circles_number:{self.output_circles_number},,input_texts:{input_texts}}}"

    def __init__(self, x: int, y: int, type: str, import_args: list = []):    
        self.x = x
        self.y = y
        self.id = len(nodes) + 1
        self.box = None # il box del nodo
        self.items = [] # gli oggetti della scatola (label, input, ...)
        self.translate_items = [] # una lista di oggetti nella scatola in forma non-id (per la traduzione a codice)
        self.circles = [] # i cerchi che possiede il nodo
        self.circle_types = {} # un dizionario che associa un cerchio al suo tipo
        self.circle_io_types = {} # un dizionario che associa un cerchio al suo tipo (input / output)
        self.circles_is_connected = {} # un dizionario che indica se un cerchio è connesso a un altro
        self.circle_connections = {} # un dizionario che indica l'altro cerchio a cui è connesso un cerchio di questo nodo
        self.circles_line_connections = {} # un dizionario che indica la linea associata ad un cerchio
        self.lines_circle_connections = {} # un dizionario che indica la linea associata alla connessione di un cerchio di questo nodo
        self.input_circles_number = 0 # il numero di cerchi di input del nodo
        self.output_circles_number = 0 # il numero di cerchi di output del nodo

        node_dict = json.load(open(nodes_path, "r"))[type]

        width = node_dict["width"]
        height = node_dict["height"]

        self.box = canvas.create_rectangle(x, y, x+width, y+height, fill=node_dict["fill-color"])

        for circle in node_dict["input-circles"]:
            icircle = canvas.create_oval(x+circle["x1"], y+circle["y1"], x+circle["x2"], y+circle["y2"], fill="red")
            self.circles.append(icircle)
            self.circle_types[icircle] = circle["type"]
            self.circle_io_types[icircle] = "input"
            self.circles_is_connected[icircle] = False

        self.input_circles_number = len(node_dict["input-circles"])

        for circle in node_dict["output-circles"]:
            ocircle = canvas.create_oval(x+circle["x1"], y+circle["y1"], x+circle["x2"], y+circle["y2"], fill="red")
            self.circles.append(ocircle)
            self.circle_types[ocircle] = circle["type"]
            self.circle_io_types[ocircle] = "output"
            self.circles_is_connected[ocircle] = False

        self.output_circles_number = len(node_dict["output-circles"])

        for label in node_dict["labels"]:
            font = ("Arial", 12, "bold")
            if "font-size" in label.keys():
                font = ("Arial", label["font-size"], "bold")
            nlabel = canvas.create_text(x+label["x"], y+label["y"], text=label["text"], font=font, anchor="center")
            self.items.append(nlabel)

        if "entries" in node_dict.keys():
            for entry in node_dict["entries"]:
                ewidth = 10
                if "width" in entry.keys():
                    ewidth = entry["width"]
                nentry = tk.Entry(canvas.master, width=ewidth, font=("Arial", 12))
                if "type" in entry.keys():
                    nentry.type = entry["type"]
                self.translate_items.append(nentry)
    
                entry_window = canvas.create_window(x+entry["x"], y+entry["y"], window=nentry)
                self.items.append(entry_window)

        global if_condition_options
        if type == "if" or type == "while":
            self.if_condition_operator = tk.StringVar(canvas.master)
            if len(import_args) > 0:
                self.if_condition_operator.set(if_condition_options[int(import_args[0])])
            else:
                self.if_condition_operator.set(if_condition_options[0])
            def set_condition_operator(option):
                self.if_condition_operator.set(option)
                button.config(text=option)
            def show_condition_selection_menu():
                dropdown_condition_selection = tk.Menu(canvas.master, tearoff=0)
                for option in if_condition_options:
                    dropdown_condition_selection.add_command(label=option, command=lambda option=option: set_condition_operator(option))
                dropdown_condition_selection.post(root.winfo_pointerx(), root.winfo_pointery())
            button = tk.Button(canvas.master, text=self.if_condition_operator.get(), command=show_condition_selection_menu)
            if type == "if":
                entry_window2 = canvas.create_window(x + width/2 - 20, y + height/2 + 13, window=button)
            else:
                entry_window2 = canvas.create_window(x + width/2 - 10, y + height/2 + 13, window=button)
            self.items.append(entry_window2)

        if type == "listset":
            actions = ["Aggiungi", "Rimuovi"]
            self.list_action = tk.StringVar(value=actions[0])

            def show_action_menu():
                menu = tk.Menu(canvas.master, tearoff=0)
                for action in actions:
                    def set_list_action(action=action):
                        self.list_action.set(action)
                        button.config(text=self.list_action.get())
                    menu.add_command(label=action, command=set_list_action)
                menu.post(root.winfo_pointerx(), root.winfo_pointery())

            button = tk.Button(canvas.master, text=self.list_action.get(), command=show_action_menu)
            entry_window = canvas.create_window(x + width/2, y + height/2 - 40, window=button)
            self.items.append(entry_window)
        
        if type == "start":
            global current_start_node
            current_start_node = self
        elif type == "end":
            global current_end_node
            current_end_node = self

        canvas.tag_bind(self.box, '<Button-1>', self.start_drag)
        canvas.tag_bind(self.box, '<B1-Motion>', self.drag)
        canvas.tag_bind(self.box, '<Button-3>', self.delete_node)
        for circle in self.circles:
            canvas.tag_bind(circle, '<Button-1>', self.start_drag_line)
            canvas.tag_bind(circle, '<B1-Motion>', self.drag_line)
            canvas.tag_bind(circle, '<ButtonRelease-1>', self.check_line)
            canvas.tag_bind(circle, '<Button-3>', self.delete_line)
        for item in self.items:  
            canvas.tag_bind(item, '<Button-1>', self.start_drag)
            canvas.tag_bind(item, '<B1-Motion>', self.drag)
            canvas.tag_bind(item, '<Button-3>', self.delete_node)

        canvas.tag_bind("line", '<Button-3>', self.delete_line_if_overlapping_line_clicked)

        self.type = type # il tipo del nodo
        self.lines = [] # le linee che collegano il nodo con altri nodi

        self.start_drag_circle = None # il cerchio da cui è partito un drag
        self.start_drag_line_item = None # la linea che sta venendo draggata

        nodes.append(self)
        nodes_parent_classes[self.box] = self

        if not self.items:
            self.items = []

        self.update_lines()

    def init_from_import(self, node):
        nodes.remove(self)
        self.id = int(node["id"])
        self.input_circles_number = int(node["input_circles_number"])
        self.output_circles_number = int(node["output_circles_number"])
        input_texts = eval(node["input_texts"])
        fields = []
        for item in self.translate_items:
            if isinstance(item, tk.Entry):
                fields.append(item)
        for i in range(len(fields)):
            text = input_texts[i]
            text_field = fields[i]
            text_field.delete(0, tk.END)
            text_field.insert(0, text)
        
        canvas.tag_bind(self.box, '<Button-1>', self.start_drag)
        canvas.tag_bind(self.box, '<B1-Motion>', self.drag)
        canvas.tag_bind(self.box, '<Button-3>', self.delete_node)
        for circle in self.circles:
            canvas.tag_bind(circle, '<Button-1>', self.start_drag_line)
            canvas.tag_bind(circle, '<B1-Motion>', self.drag_line)
            canvas.tag_bind(circle, '<ButtonRelease-1>', self.check_line)
            canvas.tag_bind(circle, '<Button-3>', self.delete_line)
        for item in self.items:  
            canvas.tag_bind(item, '<Button-1>', self.start_drag)
            canvas.tag_bind(item, '<B1-Motion>', self.drag)
            canvas.tag_bind(item, '<Button-3>', self.delete_node)

        canvas.tag_bind("line", '<Button-3>', self.delete_line_if_overlapping_line_clicked)
        nodes.append(self)

    def start_drag(self, event):
        self.x = event.x
        self.y = event.y
        self.x_before_drag = self.x
        self.y_before_drag = self.y

    def drag(self, event):
        dx = event.x - self.x
        dy = event.y - self.y
        canvas.move(self.box, dx, dy)
        for circle in self.circles:
            canvas.move(circle, dx, dy)
        for item in self.items:
            canvas.move(item, dx, dy)
        self.x = event.x
        self.y = event.y

    def start_drag_line(self, event):
        x = event.x + canvas.canvasx(0)
        y = event.y + canvas.canvasy(0)
        overlapping_items = canvas.find_overlapping(x, y, x, y)
        for item in overlapping_items:
            if item is None:
                continue
            if canvas.type(item) == "oval":
                if not self.circles_is_connected[item]:
                    self.start_drag_circle = item
                    line = canvas.create_line(canvas.coords(item)[0] + 10, canvas.coords(item)[1] + 10, x, y, width=5, tags="line")
                    self.start_drag_line_item = line
                    self.circles_line_connections[item] = line
                    self.lines_circle_connections[line] = item
                    self.lines.append(line)

    def drag_line(self, event):
        x = event.x + canvas.canvasx(0)
        y = event.y + canvas.canvasy(0)
        if not self.start_drag_circle in self.circles_is_connected.keys():
            return
        if not self.circles_is_connected[self.start_drag_circle]:
            canvas.coords(self.start_drag_line_item, canvas.coords(self.start_drag_circle)[0] + 10, canvas.coords(self.start_drag_circle)[1] + 10, x, y)

    def check_line(self, event):
        x = event.x + canvas.canvasx(0)
        y = event.y + canvas.canvasy(0)
        if not self.circles_is_connected[self.start_drag_circle]:
            overlapping_items = canvas.find_overlapping(x, y, x, y)
            for item in overlapping_items:
                if canvas.type(item) == "oval":
                    parent_box = None
                    for instance in nodes:
                        for circle in instance.circles:
                            if circle == item:
                                parent_box = instance.box
                        if instance.box == parent_box:
                            if not parent_box is None:
                                if instance.circle_io_types[item] != self.circle_io_types[self.start_drag_circle]:
                                    if not instance == self:
                                        if not instance.circles_is_connected[item]:
                                            parent_class = instance

                                            self.circles_is_connected[self.start_drag_circle] = True
                                            parent_class.circles_is_connected[item] = True

                                            self.circles_line_connections[self.start_drag_circle] = self.start_drag_line_item
                                            parent_class.circles_line_connections[item] = self.start_drag_line_item

                                            self.lines_circle_connections[self.start_drag_line_item] = self.start_drag_circle
                                            parent_class.lines_circle_connections[self.start_drag_line_item] = item

                                            self.lines.append(self.start_drag_line_item)
                                            parent_class.lines.append(self.start_drag_line_item)

                                            self.circle_connections[self.start_drag_circle] = item
                                            parent_class.circle_connections[item] = self.start_drag_circle

                                            node_connections.append([self.box, parent_box])
                                            node_connections_classes.append([self, parent_class])

                                            return
                                        else:
                                            play_sound("cannot")
                                    else:
                                        play_sound("cannot")
                                else:
                                    play_sound("cannot")
            canvas.delete(self.start_drag_line_item)
            if self.start_drag_line_item in self.lines:
                self.lines.remove(self.start_drag_line_item)
            self.start_drag_line_item = None

    def delete_line(self, event = None):
        if event is None:
            return
        x = event.x + canvas.canvasx(0)
        y = event.y + canvas.canvasy(0)
        overlapping_items = canvas.find_overlapping(x, y, x, y)
        for item in overlapping_items:
            if canvas.type(item) == "oval":
                if self.circles_is_connected[item]:
                    canvas.delete(self.circles_line_connections[item])
                    self.circles_is_connected[item] = False

                    for pair in node_connections:
                        if pair[0] == self.box:
                            other_box_class = nodes_parent_classes[pair[1]]
                            delete_pair = [self.box, other_box_class.box]
                            if delete_pair in node_connections:
                                node_connections.remove(delete_pair)
                            if [self, other_box_class] in node_connections_classes:
                                node_connections_classes.remove([self, other_box_class])
                            other_box_class_circle = other_box_class.lines_circle_connections[self.circles_line_connections[item]]
                            other_box_class.delete_line_from_other_node(other_box_class_circle)
                        elif pair[1] == self.box:
                            other_box_class = nodes_parent_classes[pair[0]]
                            delete_pair = [other_box_class.box, self.box]
                            if delete_pair in node_connections:
                                node_connections.remove(delete_pair)
                            if [other_box_class, self] in node_connections_classes:
                                node_connections_classes.remove([other_box_class, self])
                            other_box_class_circle = other_box_class.lines_circle_connections[self.circles_line_connections[item]]
                            other_box_class.delete_line_from_other_node(other_box_class_circle)
                        self.lines_circle_connections.pop(self.circles_line_connections[item])
                        self.lines.remove(self.circles_line_connections[item])
                        self.circles_line_connections.pop(item)
                        try:
                            self.circle_connections.pop(item)
                        except:
                            try:
                                self.circle_connections.pop(other_box_class_circle)
                            except:
                                pass
                    return
                
    def delete_line_from_other_node(self, connected_circle):
        if self.circles_is_connected[connected_circle]:
            self.circles_is_connected[connected_circle] = False
            self.lines.remove(self.circles_line_connections[connected_circle])
            self.circles_line_connections.pop(connected_circle)
            self.circle_connections.pop(connected_circle)

    def delete_line_if_overlapping_line_clicked(self, event):
        x = event.x + canvas.canvasx(0)
        y = event.y + canvas.canvasy(0)
        overlapping_items = canvas.find_overlapping(x, y, x, y)
        for item in overlapping_items:
            if canvas.type(item) == "oval":
                if item in self.circles_is_connected.keys():
                    if self.circles_is_connected[item]:
                        self.delete_line(event)
                        return
                else:
                    for instance in nodes:
                        for circle in instance.circles:
                            if circle == item:
                                if instance.circles_is_connected[item]:
                                    instance.delete_line(event)
                                    return

    def update_lines(self):
        for line in self.lines:
            circle1 = self.lines_circle_connections[line]
            if self.circles_is_connected[circle1]:
                circle2 = self.circle_connections[circle1]
                if circle2 is not None:
                    canvas.coords(line, canvas.coords(circle1)[0] + 10, canvas.coords(circle1)[1] + 10, canvas.coords(circle2)[0] + 10, canvas.coords(circle2)[1] + 10)
        
        canvas.after(10, self.update_lines)

    def delete_node(self, event, delete_from_nodes: bool = True, check_conns: bool = True):
        if not event == "import":
            if not event.state & 0x0001:
                return
        if check_conns:
            for pair in node_connections_classes:
                if pair[0] == self or pair[1] == self:
                    return
        if self.type == "start" and not event == "import" or self.type == "end" and not event == "import":
            return
        if delete_from_nodes:
            nodes.remove(self)
        if self.box in nodes_parent_classes:
            nodes_parent_classes.pop(self.box)
        canvas.delete(self.box)
        canvas.delete(self.start_drag_line_item)
        for circle in self.circles:
            canvas.delete(circle)
        for item in self.items:
            canvas.delete(item)
        for line in self.lines:
            try:
                canvas.delete(line)
            except:
                pass
        self.lines = []
        self.circles = []
        self.items = []
        self.translate_items = []
        self.circles_is_connected = {}
        self.circle_connections = {}

start_node = Node(100, 100, "start")
end_node = Node(100, 250, "end")

start_canvas_drag_coords = [0, 0]
def start_drag_canvas(event):
    global start_canvas_drag_coords
    canvas.scan_mark(event.x, event.y)
    start_canvas_drag_coords = [event.x, event.y]

canvas.bind("<ButtonPress-3>", start_drag_canvas)

def drag_canvas(event):   
    x = event.x
    y = event.y
    canvas.scan_dragto(x, y, gain=1)

canvas.bind("<B3-Motion>", drag_canvas)

def stop_drag_canvas(event):
    global canvas_origin, start_canvas_drag_coords
    canvas_origin = [canvas_origin[0] + (start_canvas_drag_coords[0] - event.x), canvas_origin[1] + (start_canvas_drag_coords[1] - event.y)]

canvas.bind("<ButtonRelease-3>", stop_drag_canvas)

update_nodes_positions = True
start_node_pos_label = tk.Label(root)
start_node_pos_label.place(x=10, y=10)

def update_start_node_pos():
    global update_nodes_positions
    if not update_nodes_positions:
        return
    if current_start_node is None:
        return
    start_node_x = abs(canvas.canvasx(0) - canvas.coords(current_start_node.box)[0])
    start_node_y = abs(canvas.canvasy(0) - canvas.coords(current_start_node.box)[1])
    start_node_pos_label.configure(text=f"Distanza dal nodo iniziale: {start_node_x}x, {start_node_y}y")
    root.after(10, update_start_node_pos)

update_start_node_pos()

end_node_pos_label = tk.Label(root)
end_node_pos_label.place(x=10, y=30)

def update_end_node_pos():
    global update_nodes_positions
    if not update_nodes_positions:
        return
    if current_end_node is None:
        return
    end_node_x = abs(canvas.canvasx(0) - canvas.coords(current_end_node.box)[0])
    end_node_y = abs(canvas.canvasy(0) - canvas.coords(current_end_node.box)[1])
    end_node_pos_label.configure(text=f"Distanza dal nodo finale: {end_node_x}x, {end_node_y}y")
    root.after(10, update_end_node_pos)

update_end_node_pos()

def show_error():
    global show_error_bool
    show_error_bool = True
    error_label.place(x=(root.winfo_width() - error_label.winfo_reqwidth()) / 2, y=root.winfo_height() - 50)
    close_error_button.place(x=(root.winfo_width() - close_error_button.winfo_reqwidth()) / 100 * 95, y=root.winfo_height() - 50)

def hide_error():
    global show_error_bool
    show_error_bool = False
    error_label.place_forget()
    close_error_button.place_forget()
    if error_node is not None:
        canvas.itemconfig(error_node.box, outline='black', width=1)

error_label = tk.Label(root, font=("Arial", 12, "bold"), fg="red", bg="gray")
close_error_button = tk.Button(root, text="X", font=("Arial", 10), command=hide_error)
show_error_bool = False
error_node = None
def translate_code(option: str):
    global show_error_bool, error_node, code_lang
    error_label.place_forget()
    show_error_bool = False
    for node in nodes:
        canvas.itemconfig(node.box, outline='black', width=1)
    os.system('cls' if os.name == 'nt' else 'clear')
    start_valid = False
    end_valid = False
    for node in nodes:
        if node.type == "start":
            if node.circles_is_connected[node.circles[0]]:
                start_valid = True
        elif node.type == "end":
            if node.circles_is_connected[node.circles[0]]:
                end_valid = True
    if not start_valid:
        error_label.config(text="Nodo d'inizio non connesso.")
        show_error()
        for node in nodes:
            if node.type == "start":
                canvas.itemconfig(node.box, outline='red', width=5)
        print("Invalid flow: start not connected.\n")
        return
    if not end_valid:
        error_label.config(text="Nodo di fine non connesso.")
        show_error()
        for node in nodes:
            if node.type == "end":
                canvas.itemconfig(node.box, outline='red', width=5)
        print("Invalid flow: end not connected.\n")
        return
    code = ""
    try:
        conns = []
        for pair in node_connections_classes:
            conns.append([pair[0], pair[1]])
        code = flow_to_code(conns, nodes, code_lang, True if option == "execute" else False)
    except TranslationException as e:
        error_label.config(text=f"{e.get_error_msg()} al nodo di tipo {e.get_causing_node().type}.")
        show_error()
        show_error_bool = True
        print(f"Invalid flow: translating failed. Caused by: {e.get_error_msg()} (causing node: {e.get_causing_node().type})")
        print("Skipped execution because of invalid flow.")
        error_node = e.get_causing_node()
        for node in nodes:
            if node == e.get_causing_node():
                canvas.itemconfig(node.box, outline="red", width=5)
        return
    match option:
        case "execute":
            with open(f"{temp_dir}\\{'temp.py' if code_lang == 'python' else 'Main.java'}", "w") as file:
                file.write(code)
            if code_lang == "python":
                subprocess.Popen(f"python {temp_dir}\\temp.py")
            else:
                subprocess.Popen(f"java {temp_dir}\\Main.java")
        case "source":
            if code_lang != "python":
                return
            save_path = filedialog.asksaveasfilename(filetypes=[("File di codice sorgente Python", ".py")], defaultextension=".py")
            with open(save_path, "w") as file:
                file.write(code)
        case "app":
            if code_lang != "python":
                return
            save_path = filedialog.asksaveasfilename(filetypes=[("Applicazione eseguibile Python", ".exe")], defaultextension=".exe")
            with open(f"{temp_dir}\\temp.py", "w") as file:
                file.write(f"import os\nimport subprocess\nimport sys\n\n\nsubprocess.Popen(f\"python {{os.path.join(sys._MEIPASS, \"code.py\")}}\")")
            with open(f"{temp_dir}\\code.py", "w") as file:
                file.write(f"{code}\ninput(\"Premi invio per uscire...\")\nquit()")
            os.chdir(temp_dir)
            os.system(f"pyinstaller --onefile --windowed --add-data \"code.py;.\" temp.py")
            time.sleep(1)
            os.system("rmdir /s /q build")
            os.system(f"ren dist\\temp.exe {os.path.basename(save_path)}")
            os.system(f"move dist\\{os.path.basename(save_path)} {os.path.dirname(save_path)}\\{os.path.basename(save_path)}")
            os.system("rmdir /s /q dist")
            os.system("del /s /q temp.spec")
    return

node_options_submenus = ["Generali", "Variabili", "Condizionali", "Funzioni", "Loop"]
node_options_submenus_dict = {"Generali": ["Stampa"],
                              "Variabili": ["Dichiara variabile", "Imposta variabile", "Dichiara lista", "Modifica lista"],
                              "Condizionali": ["Se", "Altrimenti", "Fine se", "Esamina variabile", "Caso variabile", "Fine esamina variabile"],
                              "Funzioni": ["Dichiara funzione", "Chiama funzione (senza ritorno)", "Chiama funzione (variabile)", "Fine funzione", "Ritorna"],
                              "Loop": ["Per ogni oggetto in lista", "Per ogni numero in intervallo", "Fine per (lista)", "Fine per (intervallo)", "Mentre", "Fine mentre"]}
node_options_dict = {"Stampa": "print",
                     "Dichiara variabile": "variabledecl",
                     "Imposta variabile": "variableset",
                     "Dichiara lista": "listdecl",
                     "Modifica lista": "listset",
                     "Se": "if",
                     "Altrimenti": "else",
                     "Fine se": "endif",
                     "Esamina variabile": "match",
                     "Caso variabile": "case",
                     "Fine esamina variabile": "endmatch",
                     "Dichiara funzione": "def",
                     "Chiama funzione (senza ritorno)": "defcall",
                     "Chiama funzione (variabile)": "defcallvar",
                     "Fine funzione": "enddef",
                     "Ritorna": "return",
                     "Per ogni oggetto in lista": "forlist",
                     "Per ogni numero in intervallo": "forrange",
                     "Fine per (lista)": "endforlist",
                     "Fine per (intervallo)": "endforrange",
                     "Mentre": "while",
                     "Fine mentre": "endwhile"}
selected_node = tk.StringVar()
def set_selected_node(option):
    selected_node.set(option)
    add_node_dropdown()
dropdown_node_selection = tk.Menu(root, tearoff=0)
for submenu in node_options_submenus:
    submenu_inst = tk.Menu(dropdown_node_selection, tearoff=0)
    for option in node_options_submenus_dict[submenu]:
        submenu_inst.add_command(label=option, command=lambda option=option: set_selected_node(option))
    dropdown_node_selection.add_cascade(label=submenu, menu=submenu_inst)

node_selection_button = tk.Button(root, text="Aggiungi nodo", command=lambda: dropdown_node_selection.post(root.winfo_pointerx(), root.winfo_pointery()))
node_selection_button.place(x=350, y=10)

dropdown_node_selection.i = 0
def navigate_node_selection_menu(event):
    index = dropdown_node_selection.i
    if event.keysym == "Down":
        dropdown_node_selection.i = (index + 1) % len(node_options_submenus)
        dropdown_node_selection.entryconfig(index, state="active")
    elif event.keysym == "Up":
        dropdown_node_selection.i = (index - 1) % len(node_options_submenus)
        dropdown_node_selection.entryconfig(index, state="active")
    elif event.keysym == "Return":
        dropdown_node_selection.invoke(index)
    
dropdown_node_selection.bind("<Down>", navigate_node_selection_menu)
dropdown_node_selection.bind("<Up>", navigate_node_selection_menu)
dropdown_node_selection.bind("<Return>", navigate_node_selection_menu)

def duplicate_node(event):
    global canvas_origin
    x = canvas_origin[0] - 50 + event.x - root.winfo_x()
    y = canvas_origin[1] - 50 + event.y - root.winfo_y()
    overlapping_items = canvas.find_overlapping(x, y, x, y)
    for item in overlapping_items:
        if canvas.type(item) == "rectangle":
            node = nodes_parent_classes[item]
            if node == current_start_node or node == current_end_node:
                continue
            node_to_create = Node(node.x + 100, node.y, node.type)
            nodes.append(node_to_create)
            nodes_parent_classes[node_to_create.box] = node_to_create
            return

canvas.bind('<Button-2>', duplicate_node)

def add_node_dropdown():
    global canvas_origin
    x = canvas_origin[0] - 50 + root.winfo_pointerx() - root.winfo_x()
    y = canvas_origin[1] - 50 + root.winfo_pointery() - root.winfo_y()
    node_to_create = node_options_dict[selected_node.get()]
    new_node = Node(x, y, node_to_create)
    nodes_parent_classes[new_node.box] = new_node
    match node_to_create:
        case "if":
            end_if_node = Node(x + 300, y - 50, "endif")
            nodes_parent_classes[end_if_node.box] = end_if_node
        case "match":
            end_match_node = Node(x + 300, y - 50, "endmatch")
            nodes_parent_classes[end_match_node.box] = end_match_node
        case "forlist":
            end_forlist_node = Node(x + 300, y - 50, "endforlist")
            nodes_parent_classes[end_forlist_node.box] = end_forlist_node
        case "forrange":
            end_forrange_node = Node(x + 300, y - 50, "endforrange")
            nodes_parent_classes[end_forrange_node.box] = end_forrange_node
        case "while":
            end_while_node = Node(x + 300, y - 50, "endwhile")
            nodes_parent_classes[end_while_node.box] = end_while_node

canvas.bind('n', lambda event: dropdown_node_selection.post(root.winfo_pointerx(), root.winfo_pointery()))

def remove_focus(event):
    canvas.focus_set()

canvas.bind('<Button-1>', remove_focus)

node_to_similar_options_dict = {"print": ["print"],
                                "variabledecl": ["variabledecl", "variableset"],
                                "variableset": ["variabledecl", "variableset"],
                                "listdecl": ["listdecl", "listset"],
                                "listset": ["listdecl", "listset"],
                                "if": ["if", "else", "endif"],
                                "else": ["if", "else", "endif"],
                                "endif": ["if", "else", "endif"],
                                "match": ["match", "case", "endmatch"],
                                "case": ["match", "case", "endmatch"],
                                "endmatch": ["match", "case", "endmatch"],
                                "def": ["def", "defcall", "defcallvar", "enddef", "return"],
                                "defcall": ["def", "defcall", "defcallvar", "enddef", "return"],
                                "defcallvar": ["def", "defcall", "defcallvar", "enddef", "return"],
                                "enddef": ["def", "defcall", "defcallvar", "enddef", "return"],
                                "return": ["def", "defcall", "defcallvar", "enddef", "return"],
                                "forlist": ["forlist", "endforlist"],
                                "forrange": ["forrange", "endforrange"],
                                "endforlist": ["forlist", "endforlist"],
                                "endforrange": ["forrange", "endforrange"],
                                "while": ["while", "endwhile"],
                                "endwhile": ["while", "endwhile"]}

similar_nodes_menu = tk.Menu(root, tearoff=0)
def update_similar_nodes_menu(event):
    global canvas_origin
    similar_nodes_menu.delete(0, tk.END)
    x = canvas_origin[0] + event.x
    y = canvas_origin[1] + event.y
    overlapping_items = canvas.find_overlapping(x, y, x, y)
    for item in overlapping_items:
        if canvas.type(item) == "rectangle":
            if item is None:
                continue
            if nodes_parent_classes[item].type == "start" or nodes_parent_classes[item].type == "end":
                continue
            node = nodes_parent_classes[item]
            for option in node_to_similar_options_dict[node.type]:
                for option2 in node_options_dict.keys():
                    if option == node_options_dict[option2]:
                        option = option2
                similar_nodes_menu.add_command(label=option, command=lambda option=option: set_selected_node(option))
            similar_nodes_menu.post(root.winfo_pointerx(), root.winfo_pointery())
            break

canvas.bind('c', lambda event: update_similar_nodes_menu(event))

similar_nodes_menu.i = 0
def navigate_similar_nodes_selection_menu(event):
    index = similar_nodes_menu.i
    if event.keysym == "Down":
        similar_nodes_menu.i = (index + 1) % len(node_options_submenus)
        similar_nodes_menu.entryconfig(index, state="active")
    elif event.keysym == "Up":
        similar_nodes_menu.i = (index - 1) % len(node_options_submenus)
        similar_nodes_menu.entryconfig(index, state="active")
    elif event.keysym == "Return":
        similar_nodes_menu.invoke(index)
    
similar_nodes_menu.bind("<Down>", navigate_similar_nodes_selection_menu)
similar_nodes_menu.bind("<Up>", navigate_similar_nodes_selection_menu)
similar_nodes_menu.bind("<Return>", navigate_similar_nodes_selection_menu)

current_page = 0
def help_window():
    help_window = tk.Toplevel(root)
    help_window.title("Aiuto")
    help_window.geometry("600x600")
    help_window.update_idletasks()
    help_window.width = 600
    help_window.height = 600

    pages = []
    with open(help_pages_path, "r") as f:
        for page in f.read().split("\n\n"):
            page2 = page.replace(page.split("\n")[0] + "\n", "")
            pages.append([page.split("\n")[0], page2.replace("\n", " ").replace("{n}", "\n")])

    def fix_word_cutting(text, charwidth):
        current_charwidth = 0
        words = text.split(" ")
        new_text = ""
        for word in words:
            if current_charwidth + len(word) < charwidth:
                new_text += word + " "
                current_charwidth += len(word) + 1
            else:
                new_text += "\n" + word + " "
                current_charwidth = len(word) + 1 - (charwidth - current_charwidth)
            if word.endswith("\n"):
                current_charwidth = 0
        new_text.replace("\n\n", "\n")
        return new_text

    page_title = tk.Label(help_window, text=pages[current_page][0], font=("Arial", 13, "bold"))
    page_title.place(x=10, y=10)
    page_content = tk.Text(help_window, height=round(help_window.winfo_height() / 22) + 1, width=round(help_window.winfo_width() / 8.5) - 1, wrap=tk.NONE)
    page_content.charwidth = round((help_window.winfo_width() - 20) / 8.5)
    page_content.place(x=10, y=40)
    page_content.insert(tk.INSERT, fix_word_cutting(pages[current_page][1].encode("utf-8").decode("latin-1"), page_content.charwidth))
    page_content.config(state=tk.DISABLED)
    page_content_scrollbar = tk.Scrollbar(help_window, orient=tk.VERTICAL, command=page_content.yview)
    page_content_scrollbar.place(x=help_window.winfo_width() - 20, y=40, height=round(help_window.winfo_height() - 80))
    page_content.config(yscrollcommand=page_content_scrollbar.set)
    page_count = tk.Label(help_window, text=f"{current_page + 1}/{len(pages)}")
    page_count.place(x=help_window.winfo_width() - 65, y=help_window.winfo_height() - 30)

    def change_page(action: str):
        global current_page
        if action == "previous":
            if current_page > 0:
                current_page -= 1
        elif action == "next":
            if current_page < len(pages) - 1:
                current_page += 1
        
        page_title.config(text=pages[current_page][0])
        page_content.config(state=tk.NORMAL)
        page_content.delete("1.0", tk.END)
        page_content.insert(tk.INSERT, fix_word_cutting(pages[current_page][1], page_content.charwidth))
        page_content.config(state=tk.DISABLED)
        page_count.config(text=f"{current_page + 1}/{len(pages)}")

    previous_page_button = tk.Button(help_window, text="<", command=lambda: change_page("previous"))
    previous_page_button.place(x=10, y=help_window.winfo_height() - 30)

    next_page_button = tk.Button(help_window, text=">", command=lambda: change_page("next"))
    next_page_button.place(x=help_window.winfo_width() - 30, y=help_window.winfo_height() - 30)


    def resize_window():
        current_width = help_window.winfo_width()
        current_height = help_window.winfo_height()
        if current_width != help_window.width:
            page_content.config(width=round(help_window.winfo_width() / 8.5) - 1)
            new_charwidth = round((help_window.winfo_width() - 20) / 8.5)
            page_content.charwidth = new_charwidth
            page_content.config(state=tk.NORMAL)
            page_content.delete("1.0", tk.END)
            page_content.insert(tk.INSERT, fix_word_cutting(pages[current_page][1], page_content.charwidth))
            page_content.config(state=tk.DISABLED)
            next_page_button.place(x=help_window.winfo_width() - 30)
            page_content_scrollbar.place(x=help_window.winfo_width() - 20)
            page_count.place(x=help_window.winfo_width() - 65)
        if current_height != help_window.height:
            page_content.config(height=round(help_window.winfo_height() / 22) + 1)
            previous_page_button.place(y=help_window.winfo_height() - 30)
            next_page_button.place(y=help_window.winfo_height() - 30)
            page_content_scrollbar.place(y=40, height=round(help_window.winfo_height() - 80))
            page_count.place(y=help_window.winfo_height() - 30)
        help_window.width = current_width
        help_window.height = current_height
        help_window.after(10, resize_window)
    resize_window()

    help_window.mainloop()

def export_workflow(override_path: str = "", is_save: bool = True):
    global current_file_label, current_file, open_files
    if override_path == "":
        export_file = filedialog.asksaveasfilename(filetypes=[("File di salvataggio Python Flow", ".pyf")], defaultextension=".pyf")
    else:
        export_file = override_path
    if not os.path.exists(os.path.dirname(export_file)):
        return
    current_file_label.config(text=os.path.basename(export_file))
    current_file = export_file
    if is_save and not export_file in open_files:
        open_files.append(export_file)
    content = ""

    node_connections_classes_id_list = []
    for pair in node_connections_classes:
        node_connections_classes_id_list.append([pair[0].id, pair[1].id])
    content += f"{{node_connections_classes:{node_connections_classes_id_list}}}\n"
    circles = []
    added_circles = []
    for node in nodes:
        for circle in node.circles:
            if circle in node.circle_connections:
                if not circle in added_circles:
                    other_circle = node.circle_connections[circle]
                    other_node = None
                    for node2 in nodes:
                        for circle2 in node2.circles:
                            if circle2 == other_circle:
                                other_node = node2
                                break
                    if other_node is not None:
                        circles.append([[node.id, node.circle_types[circle]], [other_node.id, other_node.circle_types[other_circle]]])
                        added_circles.append(circle)
                        added_circles.append(other_circle)
    content += f"{{circles:{circles}}}\n"
    content += "["
    for node in nodes:
        content += node.__str__("export").replace(" ", "")
        if not node == nodes[-1]:
            content += ",,,"
    content += "]"
    
    if is_save:
        with open(export_file, "w") as f:
            f.write(content)
        global last_save_content
        last_save_content = content
    return content

def instantiate_app_from_import(override_path: str = "", is_switch: bool = False):
    global nodes, node_connections, node_connections_classes, nodes_parent_classes, update_nodes_positions, current_file, current_file_label, open_files
    update_nodes_positions = False
    if override_path == "":
        import_file = filedialog.askopenfilename(filetypes=[("File di salvataggio Python Flow", ".pyf")], defaultextension=".pyf")
    else:
        import_file = override_path
    if not os.path.exists(os.path.dirname(import_file)):
        return
    current_file_label.config(text=os.path.basename(import_file))
    current_file = import_file
    if not is_switch:
        open_files.append(import_file)
    for node in nodes[:]:
        node.delete_node("import", check_conns=False)
    contents = ""
    node_connections = []
    nodes_parent_classes = {}
    with open(import_file, "r") as f:
        contents = f.read()
    flow_globals_text = contents.split("\n")[0].removeprefix("{").removesuffix("}").replace(" ", "")
    flow_globals = {}
    for pair in flow_globals_text.split(",,"):
        flow_globals[pair.split(":")[0]] = pair.split(":")[1]
    circles_text = contents.split("\n")[1].split(":")[1].removeprefix("{").removesuffix("}").replace(" ", "")
    circles = eval(circles_text)
    flow_text = contents.split("\n")[2].removeprefix("[").removesuffix("]")
    flow = []
    for node in flow_text.split("},,,{"):
        node = node.removeprefix("{").removesuffix("}")
        new_node_dict = {}
        for pair in node.split(",,"):
            if "{" in pair and "}" in pair and not "{}" in pair:
                new_node_dict[pair.split(":")[0]] = pair.split(":")[1] + ":" + pair.split(":")[2]
                continue
            new_node_dict[pair.split(":")[0]] = pair.split(":")[1]
        flow.append(new_node_dict)

    node_connections_classes = eval(flow_globals["node_connections_classes"].replace(" ", ""))
    start_node_pos = [0, 0]
    for node in flow:
        added_node = Node(int(node["x"]), int(node["y"]), node["type"], [node["condition_operator"]] if node["type"] == "if" or node["type"] == "while" else [])
        added_node.init_from_import(node)
        if node["type"] == "start":
            start_node_pos = [int(node["x"]), int(node["y"])]
    for node in nodes:
        if not node_connections_classes is None and not node_connections_classes == []:
            for pair in node_connections_classes:
                if node.id == pair[0]:
                    value = pair[1]
                    node_connections_classes.remove(pair)
                    value_node = None
                    for node2 in nodes:
                        if node2.id == value:
                            value_node = node2
                    node_connections_classes.append([node, value_node])
                elif node.id == pair[1]:
                    value = pair[0]
                    node_connections_classes.remove(pair)
                    value_node = None
                    for node2 in nodes:
                        if node2.id == value:
                            value_node = node2
                            break
                    node_connections_classes.append([value_node, node])
    for pair in node_connections_classes:
        node_connections.append([pair[0].box, pair[1].box])
    for association in circles:
        node_id = association[0][0]
        node = None
        for node2 in nodes:
            if node2.id == node_id:
                node = node2
                break
        node_circle = None
        for circle in node.circles:
            if node.circle_types[circle] == association[0][1]:
                node_circle = circle
                break
        other_node_id = association[1][0]
        other_node = None
        for node2 in nodes:
            if node2.id == other_node_id:
                other_node = node2
                break
        other_node_circle = None
        for circle in other_node.circles:
            if other_node.circle_types[circle] == association[1][1]:
                other_node_circle = circle
                break
        node.circles_is_connected[node_circle] = True
        other_node.circles_is_connected[other_node_circle] = True
        node.circle_connections[node_circle] = other_node_circle
        other_node.circle_connections[other_node_circle] = node_circle
        line = canvas.create_line(canvas.coords(node_circle)[0] + 10, canvas.coords(node_circle)[1] + 10, canvas.coords(other_node_circle)[0] + 10, canvas.coords(other_node_circle)[1] + 10, width=5, tags="line")
        node.circles_line_connections[node_circle] = line
        other_node.circles_line_connections[other_node_circle] = line
        node.lines_circle_connections[line] = node_circle
        other_node.lines_circle_connections[line] = other_node_circle
        node.lines.append(line)
        other_node.lines.append(line)
    update_nodes_positions = True
    update_start_node_pos()
    update_end_node_pos()
    canvas.xview_moveto(start_node_pos[0])
    canvas.yview_moveto(start_node_pos[1])

def resize_root():
    global current_file_label
    current_width = root.winfo_width()
    current_height = root.winfo_height()
    if current_width != root.width:
        if show_error_bool:
            error_label.place(x=(root.winfo_width() - error_label.winfo_reqwidth()) / 2)
            close_error_button.place(x=(root.winfo_width() - close_error_button.winfo_reqwidth()) / 100 * 95)
        current_file_label.place(x=root.winfo_width() - current_file_label.winfo_reqwidth() - 10, y=10)
    if current_height != root.height:
        if show_error_bool:
            error_label.place(y=root.winfo_height() - 50)
            close_error_button.place(y=root.winfo_height() - 50)
    root.width = current_width
    root.height = current_height
    root.after(10, resize_root)
resize_root()

def add_suggestion(suggestion, entry, part):
    last_char = entry.get()[entry.index(tk.INSERT) - 1]
    while last_char in suggestion:
        entry.delete(f"{tk.INSERT}-1c")
        last_char = entry.get()[entry.index(tk.INSERT) - 1]
    entry.insert(tk.INSERT, suggestion)
    global suggestion_buttons
    for button in suggestion_buttons:
        button.destroy()
    suggestion_buttons = []

suggestion_buttons = []
def autocomplete():
    global declared_variables, declared_lists, declared_functions, suggestion_buttons, bigger_input, canvas_origin
    for button in suggestion_buttons:
        button.destroy()
    suggestion_buttons = []
    complete_entry = root.focus_get()
    if isinstance(complete_entry, tk.Entry):
        content = complete_entry.get()
        x = complete_entry.winfo_rootx() - root.winfo_x()
        y = complete_entry.winfo_rooty() - root.winfo_y()

        suggestions = []
        for variable in declared_variables:
            suggestions.append(f"Variabile: {variable}")
        for list in declared_lists:
            suggestions.append(f"Lista: {list}")
        for function in declared_functions:
            suggestions.append(f"Funzione: {function}")

        parts = content.split(" ")
        new_parts = []
        for part in parts:
            subparts = part.split(".")
            for subpart in subparts:
                new_parts.append(subpart)

        splitted_parts = []
        for part in new_parts:
            subparts = part.split("(")
            for subpart in subparts:
                splitted_parts.append(subpart)

        i = 0
        search = complete_entry.index(tk.INSERT) - 1
        complete_piece = ""
        for part in splitted_parts:
            indexes = []
            for item in range(i, i + len(part)):
                indexes.append(item)
            if search in indexes:
                complete_piece = part
                break
            else:
                i += len(part) + 1

        suggestions_added = 0
        for suggestion in suggestions:
            if suggestions_added >= 5:
                break
            if suggestion.split(": ")[1].lower().startswith(complete_piece.lower()) and not content == "" and not len(complete_piece) >= len(suggestion.split(": ")[1]):
                button = tk.Button(root, text=suggestion, command=lambda sugg=suggestion, e=complete_entry, cont=content: add_suggestion(sugg.split(": ")[1], e, cont))
                suggestion_buttons.append(button)
                button.place(x=x, y=y - 15 + suggestions_added * (30 if complete_entry != bigger_input else -30))
                suggestions_added += 1

root.bind("<KeyRelease>", lambda event: autocomplete())

def destroy_autocomplete():
    global suggestion_buttons
    for button in suggestion_buttons:
        button.destroy()
    suggestion_buttons = []

root.bind("<Button-3>", lambda event: destroy_autocomplete(), "+")

code_lang = "python"
using_python = tk.BooleanVar(value=True)
using_java = tk.BooleanVar(value=False)

def change_code_lang(lang):
    global code_lang, execute_menu
    code_lang = lang

    match code_lang:
        case "python":
            using_python.set(True)
            using_java.set(False)
            execute_menu.entryconfig("Traduci in applicazione eseguibile (.exe)", state="normal")
        case "java":
            using_python.set(False)
            using_java.set(True)
            execute_menu.entryconfig("Traduci in applicazione eseguibile (.exe)", state="disabled")

def new_file():
    global new_file_import
    file_path = filedialog.asksaveasfilename(defaultextension=".pyf", filetypes=[("File di salvataggio Python Flow", ".pyf")], initialfile="Nuovo file")
    if not os.path.exists(os.path.dirname(file_path)):
        return
    open(file_path, "w").write(open(new_file_import, "r").read())
    instantiate_app_from_import(file_path)

def close_current_file():
    global current_file, open_files, are_unsaved_changes_present
    close_file_bool = True
    def confirm_close():
        window = tk.Toplevel(root)
        window.title("Conferma chiusura file")
        window.resizable(False, False)
        window.geometry(f"300x300+{root.winfo_width() // 2 - 150}+{root.winfo_height() // 2 - 150}")

        title = tk.Label(window, text="Sei sicuro di voler chiudere il file?", anchor="center", font=("Arial", 13, "bold"))
        title.place(x=window.winfo_width() // 2, y=75)

        subtitle = tk.Label(window, text="Ci sono modifiche non salvate.", anchor="center", font=("Arial", 14))
        subtitle.place(x=window.winfo_width() // 2, y=150)

        def set_close(value):
            nonlocal close_file_bool
            close_file_bool = value
            window.destroy()

        confirm_button = tk.Button(window, text="Chiudi", command=lambda: set_close(True))
        confirm_button.place(x=100 - confirm_button.winfo_reqwidth(), y=200)

        cancel_button = tk.Button(window, text="Annulla", command=lambda: set_close(False))
        cancel_button.place(x=200, y=200)

        window.wait_window(window)
        return

    if are_unsaved_changes_present:
        confirm_close()
    if close_file_bool:
        if len(open_files) <= 1:
            quit()
        open_files.remove(current_file)
        current_file = open_files[0]
        instantiate_app_from_import(current_file, True)

root_menu = tk.Menu(root, tearoff=0)
root.config(menu=root_menu)

file_menu = tk.Menu(root_menu, tearoff=0)
file_menu.add_command(label="Nuovo file", command=new_file)
file_menu.add_separator()
file_menu.add_command(label="Apri", command=instantiate_app_from_import)
file_menu.add_separator()
file_menu.add_command(label="Salva", command=lambda: export_workflow(current_file))
file_menu.add_command(label="Salva con nome", command=export_workflow)
file_menu.add_separator()
file_menu.add_command(label="Chiudi file", command=close_current_file)

execute_menu = tk.Menu(root_menu, tearoff=0)
execute_menu.add_command(label="Esegui nel terminale", command=lambda: translate_code("execute"))
execute_menu.add_command(label="Traduci in codice sorgente", command=lambda: translate_code("source"))
execute_menu.add_command(label="Traduci in applicazione eseguibile (.exe)", command=lambda: translate_code("app"))
execute_menu.add_separator()
execute_menu.add_checkbutton(label="Linguaggio: Python", command=lambda: change_code_lang("python"), onvalue=True, offvalue=False, variable=using_python)
execute_menu.add_checkbutton(label="Linguaggio: Java", command=lambda: change_code_lang("java"), onvalue=True, offvalue=False, variable=using_java)

help_menu = tk.Menu(root_menu, tearoff=0)
help_menu.add_command(label="Aiuto", command=help_window)

root_menu.add_cascade(label="File", menu=file_menu)
root_menu.add_cascade(label="Esegui", menu=execute_menu)
root_menu.add_cascade(label="Aiuto", menu=help_menu)


open_files_menu = tk.Menu(root_menu, tearoff=0)
def update_open_files():
    global open_files, open_files_menu
    open_files_menu = tk.Menu(root_menu, tearoff=0)
    for file in open_files:
        open_files_menu.add_command(label=os.path.basename(file), command=lambda file=file: instantiate_app_from_import(file, True))
    root.after(500, update_open_files)
root.after(1, update_open_files)

current_file_label = tk.Button(root, text="File non salvato", font=("Arial", 10), command=lambda: open_files_menu.post(root.winfo_pointerx(), root.winfo_pointery()))
current_file_label.place(x=root.winfo_width() - current_file_label.winfo_reqwidth() - 10, y=10)
current_file = ""

open_files = []

last_save_content = ""
are_unsaved_changes_present = False
def check_unsaved_changes():
    global last_save_content, node_connections_classes, nodes, code_lang, current_file, current_file_label, are_unsaved_changes_present
    try:
        if not current_file == "":
            if export_workflow(current_file, False) != last_save_content:
                current_file_label.config(text="*" + os.path.basename(current_file))
                are_unsaved_changes_present = True
            else:
                current_file_label.config(text=os.path.basename(current_file))
                are_unsaved_changes_present = False
    except:
        pass
    root.after(1000, check_unsaved_changes)
check_unsaved_changes()

root.mainloop()