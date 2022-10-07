import bisect
import json
import os
import pickle
import random
import sys
import tkinter as tk

from PIL import Image, ImageTk

from calculate import calculate, get_center_of_gravity, random_color
from Detail import Detail


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("model")
        self.details = list()
        self.doc = '''
    Commands:
        - help
        - add <имя> <масса> <длина> [цвет]
        - addlist <название> <имя>
        - move <имя> <изменение>
        - move_to <имя> <позиция>
        - rename <старое имя> <новое имя>
        - copy <имя1> <имя2>
        - edit <имя> <mass или length> <новое значение>
        - cut <имя> <длина или отношение> [имя1] [имя2]
        - select <имя>
        - deselect
        - remove <имя>
        - print <имя>
        - dist <l/r> <имя1> <l/r> <имя2>
        - list
        - calculate
        - save <название файла>
        - load <название файла>
        - listed print
        - listed show <название>
        - listed save <имя> [название]
        - listed remove <название>
        - listed load <название> <имя> [цвет]
'''

        self.colors = dict()
        self.selected = None
        self.images = list()

        self.entry_text = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.entry_text, width=100)
        self.entry.bind("<Return>", lambda *args: self.button_click())
        self.entry.bind("<F1>", lambda *args: self.button.focus_set())
        self.entry.bind("<FocusIn>", lambda *args: self.entry.config(background="white"))
        self.entry.bind("<FocusOut>", lambda *args: self.entry.config(background="#EEEEEE"))
        self.entry.grid(row=0, column=0)

        self.button = tk.Button(self, text="O", command=self.button_click, background='#CCE5FF')
        self.button.bind("<Left>", self.move_left)
        self.button.bind("<a>", self.move_left)
        self.button.bind("<Right>", self.move_right)
        self.button.bind("<d>", self.move_right)
        self.button.bind("<F1>", lambda *args: self.entry.focus_set())
        self.button.bind("<FocusIn>", lambda *args: self.button.config(background='#3399FF'))
        self.button.bind("<FocusOut>", lambda *args: self.button.config(background='#CCE5FF'))
        self.button.grid(row=0, column=1)

        self.canvas = tk.Canvas(self, width=600, height=400)
        self.canvas.grid(row=1, column=0, columnspan=2)

        os.makedirs('files', exist_ok=True)
        self.entry.focus_set()
        self.mainloop()


    def move_left(self, *args):
        if self.selected == None:
            return
        edges = list()
        for det in self.details:
            if det.name != self.selected.name:
                edges.extend([det.pos, det.pos + det.length, det.pos - self.selected.length, det.pos + det.length - self.selected.length])
        edges = sorted(list(set(edges)))
        index = bisect.bisect_left(edges, self.selected.pos - 0.000000000001) - 1
        if index == -1: return
        self.run_query(("move_to", self.selected.name, edges[index]))
        self.show_details()

    def move_right(self, *args):
        if self.selected == None:
            return
        edges = list()
        for det in self.details:
            if det.name != self.selected.name:
                edges.extend([det.pos, det.pos + det.length, det.pos + self.selected.length, det.pos + det.length + self.selected.length])
        edges = sorted(list(set(edges)))
        # print(edges, self.selected.pos + self.selected.length)
        index = bisect.bisect_right(edges, self.selected.pos + self.selected.length + 0.000000000001)
        if index == len(edges): return
        self.run_query(("move_to", self.selected.name, edges[index] - self.selected.length))
        self.show_details()


    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill = self.winfo_rgb(fill) + (alpha,)
            fill = (fill[0]//255, fill[1]//255, fill[2]//255, fill[3])
            image = Image.new('RGBA', (x2-x1, y2-y1), fill)
            self.images.append(ImageTk.PhotoImage(image))
            self.canvas.create_image(x1, y1, image=self.images[-1], anchor='nw')
        self.canvas.create_rectangle(x1, y1, x2, y2, **kwargs)

    def show_details(self):
        self.canvas.delete("all")
        self.canvas.create_line(0, 200, 600, 200, fill="black", width=1)
        self.canvas.create_line(300, 195, 300, 205, fill='red', width=2)
        if len(self.details) == 0: return
        left_edge = min([det.pos for det in self.details])
        right_edge = max([(det.pos + det.length) for det in self.details])
        scale = max(abs(left_edge), abs(right_edge))
        center = get_center_of_gravity(self.details)
        self.canvas.create_line(int(280 * (center) / scale + 300), 195, int(280 * (center) / scale + 300), 205, fill='green', width=3)
        for det in self.details:
            x1 = int(280 * (det.pos) / scale + 300)
            y1 = int(200 - 50 * (det.mass / det.length) / 2)
            x2 = int(280 * (det.pos + det.length) / scale + 300)
            y2 = int(200 + 50 * (det.mass / det.length) / 2)
            if det.name not in self.colors:
                self.colors[det.name] = "#CDCDCD"# random_color()
            if self.selected != None and self.selected.name == det.name:
                # color = "#F07777"
                color = self.colors[det.name]
                textcolor = "#FF0000"
            else:
                color = self.colors[det.name]
                textcolor = 'black'
            self.create_rectangle(x1, y1, x2, y2, fill=color, outline=textcolor, alpha=.3)
            self.canvas.create_text((x1 + x2) / 2, y1 - 6, text=det.name, fill=textcolor, font=('Helvetica 12'))

    def button_click(self):
        self.run_query(self.entry_text.get().split(" "))
        self.entry_text.set("")
        self.show_details()

    def parse_color(string):
        if string[0] == '#' and len(string) == 7:
            return string
        elif string[:3] == 'rgb':
            hx = '#' + ''.join(map(lambda x: hex(int(x))[2:].zfill(2), string[4:-1].split(',')))
            if len(hx) != 7:
                print(hx)
                print("Invalid rgb values")
                return False
            return hx
        else:
            print("Invalid color option")
            return False

    def run_query(self, query):
        try:
            match query[0]:
                case "help":
                    print(self.doc)

                case "add":
                    self.details.append(Detail(name=query[1], mass=float(query[2]), length=float(query[3])))
                    if len(query) > 4:
                        color = Window.parse_color(query[4])
                        if color != False:
                            self.colors[query[1]] = color
                    print("Added new detail: ", repr(self.details[-1]))

                case "move":
                    to_move = query[1:-1]
                    for obj in self.details:
                        if obj.name in to_move:
                            obj.move(float(query[-1]))
                            to_move.remove(obj.name)
                    if len(to_move) != 0:
                        print("Details not found: ", end="")
                        for i in range(len(to_move)):
                            print(to_move[i], end=(i != len(to_move) - 1) * "," + " ")
                        print()

                case "move_to":
                    for obj in self.details:
                        if obj.name == query[1]:
                            obj.move_to(float(query[2]))
                            break
                    else:
                        print("No detail with this name")

                case "rename":
                    for obj in self.details:
                        if obj.name == query[1]:
                            if not obj.rename(query[2], self.details):
                                print("This name is already in use")
                            break
                    else:
                        print("No detail with this name")

                case "print":
                    for obj in self.details:
                        if obj.name == query[1]:
                            print("Detail", repr(obj), sep="\n\t")
                            break
                    else:
                        print("No detail with this name")

                case "list":
                    if len(self.details) == 0:
                        print("No self.details")
                        return
                    print("self.details:")
                    for obj in self.details:
                        print('\t' + repr(obj))

                case "save":
                    loaded = [self.details, self.colors]
                    with open('files/' + query[1], "wb") as file:
                        pickle.dump(loaded, file)

                case "load":
                    with open('files/' + query[1], "rb") as file:
                        loaded = pickle.load(file)
                    self.details = loaded[0]
                    self.colors = loaded[1]

                case "remove":
                    to_remove = query[1:]
                    for i, obj in enumerate(self.details):
                        if obj.name in to_remove:
                            print("Removed", self.details.pop(i).name)
                    if len(to_remove) != 0:
                        print("No details with such names: ", end="")
                        for i in range(len(to_remove)):
                            print(to_remove[i], end=(i != len(to_remove) - 1) * "," + " ")

                case "edit":
                    for obj in self.details:
                        if obj.name == query[1]:
                            if query[2] == "mass":
                                obj.mass = float(query[3])
                            if query[2] == "length":
                                obj.length = float(query[3])
                            if query[2] == "color":
                                color = Window.parse_color(query[3])
                                if color != False:
                                    self.colors[obj.name] = color
                            break
                    else:
                        print("No detail with this name")

                case "select":
                    for obj in self.details:
                        if obj.name == query[1]:
                            self.selected = obj
                            print("Selected", self.selected.name)
                            break
                    else:
                        print("No detail with this name")

                case "deselect":
                    if self.selected != None:
                        print("Deselected", self.selected.name)
                    self.selected = None

                case "addlist":
                    with open("listed.json", "r") as file:
                        listed_details = json.load(file)
                    for det in listed_details:
                        if det["name"].lower() == query[1].lower():
                            if len(query) > 3:
                                color = Window.parse_color(query[3])
                                if color != False:
                                    self.run_query(("add", query[2], det["mass" ], det["length"], color))
                            else:
                                self.run_query(("add", query[2], det["mass"], det["length"]))
                            break
                    else:
                        print("No detail in listed file with this name")

                case "cut":
                    for det in self.details:
                        if det.name == query[1]:
                            ratio_str = query[2]
                            if '/' in ratio_str:
                                a, b = map(float, ratio_str.split('/'))
                                ratioa, ratiob = a/(a + b), b/(a + b)
                            else:
                                if float(ratio_str) > det.length or float(ratio_str) < 0:
                                    print("Too much to cut or less than 0")
                                    return
                                ratioa, ratiob = float(ratio_str) / det.length, (det.length - float(ratio_str)) / det.length
                            if len(query) > 3:
                                name1, name2 = query[3], query[4]
                            else:
                                name1, name2 = det.name + '1', det.name + '2'
                            self.run_query(("add", name1, det.mass*ratioa, det.length*ratioa, self.colors[det.name]))
                            self.run_query(("add", name2, det.mass*ratiob, det.length*ratiob, self.colors[det.name]))
                            self.run_query(("move_to", name1, det.pos))
                            self.run_query(("move_to", name2, det.pos + det.length*ratioa))
                            self.run_query(("remove", det.name))
                            break
                    else:
                        print("No detail with such name")

                case "copy":
                    for det in self.details:
                        if det.name == query[1]:
                            self.run_query(("add", query[2], det.mass, det.length, self.colors[det.name]))
                            self.run_query(("move_to", query[2], det.pos))
                            break
                    else:
                        print("No detail with this name")

                case "calculate":
                    calculate(self.details)

                case "dist":
                    edges = list()
                    for det in self.details:
                        if det.name == query[2]:
                            if query[1] == 'l':
                                edges.append(det.pos)
                            elif query[1] == 'r':
                                edges.append(det.pos + det.length)
                            else:
                                print("Invalid arguments")
                                return
                        if det.name == query[4]:
                            if query[3] == 'l':
                                edges.append(det.pos)
                            elif query[3] == 'r':
                                edges.append(det.pos + det.length)
                            else:
                                print("Invalid arguments")
                                return
                    if len(edges) == 2:
                        print("Distance =", abs(edges[0] - edges[1]))


                case "listed":
                    with open("listed.json", "r") as file:
                        listed_details = json.load(file)
                    if query[1] == "print":
                        print("Details in listed.json:")
                        for det in listed_details:
                            print("\t", det["name"])
                    if query[1] == "save":
                        for det in self.details:
                            if det.name == query[2]:
                                if len(query) < 4:
                                    name = query[2]
                                else:
                                    name = query[3]
                                listed_details.append({
                                    "name": name,
                                    "mass": det.mass,
                                    "length": det.length
                                })
                                with open("listed.json", "w") as file:
                                    json.dump(listed_details, file)
                                print(f'Added {det.name} to listed.json')
                                break
                        else:
                            print("No detail with this name")
                    if query[1] == "remove":
                        for i, det in enumerate(listed_details):
                            if det["name"].lower() == query[2].lower():
                                listed_details.pop(i)
                                with open("listed.json", "w") as file:
                                    json.dump(listed_details, file)
                                print(f'Removed {query[2]} from listed.json')
                                break
                        else:
                            print("No detail with this name")
                    if query[1] == "show":
                        for i, det in enumerate(listed_details):
                            if det["name"].lower() == query[2].lower():
                                print(f'Detail:  Name: {det["name"]}, Mass: {det["mass"]}, Length: {det["length"]}')
                                break
                        else:
                            print("No detail with this name")
                    if query[1] == "load":
                        for det in listed_details:
                            if det["name"].lower() == query[2].lower():
                                if len(query) > 4:
                                    color = Window.parse_color(query[4])
                                    if color != False:
                                        self.run_query(("add", query[3], det["mass" ], det["length"], color))
                                else:
                                    self.run_query(("add", query[3], det["mass"], det["length"]))
                                break
                        else:
                            print("No detail in listed file with this name")

                case "exit":
                    self.destroy()
                    sys.exit(0)

        except IndexError:
            print("Not enough arguments")
        except ValueError:
            print("Invalid inputs (probably not a float-type)")
        except FileNotFoundError:
            print("No such file")
