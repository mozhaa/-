import tkinter as tk
from calculate import get_center_of_gravity, random_color, calculate
from PIL import Image, ImageTk
import json
import random
import pickle
from Detail import Detail
import bisect


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("model")
        self.details = list()
        self.doc =     '''
            Commands:
                help
                add {name} {mass} {length}
                move {name} {delta}
                move_to {name} {pos}
                rename {oldname} {newname}
                edit {name} {property} {newvalue}
                remove {name}
                print {name}
                list
                save {filename}
                load {filename}

            '''

        self.colors = dict()
        self.selected = None
        self.images = list()

        self.entry_text = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.entry_text, width=100)
        self.entry.bind("<Return>", lambda *args: self.button_click())
        self.entry.grid(row=0, column=0)

        self.button = tk.Button(self, text="O", command=self.button_click)
        self.button.grid(row=0, column=1)

        self.canvas = tk.Canvas(self, width=600, height=400)
        self.button.bind("<Left>", self.move_left)
        self.button.bind("<Right>", self.move_right)
        self.canvas.grid(row=1, column=0, columnspan=2)

        self.mainloop()


    def move_left(self, *args):
        if self.selected == None:
            return
        edges = list()
        for det in self.details:
            if det.name != self.selected.name:
                edges.extend([det.pos, det.pos + det.length, det.pos - self.selected.length, det.pos + det.length - self.selected.length])
        edges = sorted(list(set(edges)))
        index = bisect.bisect_left(edges, self.selected.pos) - 1
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
        index = bisect.bisect_right(edges, self.selected.pos + self.selected.length)
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
                color = "#F07777"
                textcolor = "#FF0000"
            else:
                color = self.colors[det.name]
                textcolor = 'black'
            self.create_rectangle(x1, y1, x2, y2, fill=color, alpha=.3)
            self.canvas.create_text((x1 + x2) / 2, y1 - 6, text=det.name, fill=textcolor, font=('Helvetica 12'))
            # self.create_rectangle(
            #     x1, y1,
            #     x2, y2,
            #     fill=("#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])), alpha=.3)

    def button_click(self):
        self.run_query(self.entry_text.get().split(" "))
        self.entry_text.set("")
        self.show_details()

    def run_query(self, query):
        match query[0]:
            case "help":
                print(self.doc)
            case "add":
                try:
                    self.details.append(Detail(name=query[1], mass=float(query[2]), length=float(query[3])))
                    print("Added new detail: ", repr(self.details[-1]))
                except ValueError:
                    print("Invalid mass or length (not integers)")
                except IndexError:
                    print("Not enough arguments")
            case "move":
                for obj in self.details:
                    if obj.name == query[1]:
                        try:
                            obj.move(float(query[2]))
                            break
                        except ValueError:
                            print("Invalid delta (not an integer)")
                            return
                else:
                    print("No detail with this name")
            case "move_to":
                for obj in self.details:
                    if obj.name == query[1]:
                        try:
                            obj.move_to(float(query[2]))
                            break
                        except ValueError:
                            print("Invalid position (not an integer)")
                            return
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
                with open(query[1], "wb") as file:
                    pickle.dump(self.details, file)
            case "load":
                with open(query[1], "rb") as file:
                    self.details = pickle.load(file)
            case "remove":
                for i, obj in enumerate(self.details):
                    if obj.name == query[1]:
                        print("Removed", self.details.pop(i).name)
                        break
                else:
                    print("No detail with this name")
            case "edit":
                for obj in self.details:
                    if obj.name == query[1]:
                        if query[2] == "mass":
                            try:
                                obj.mass = float(query[3])
                            except ValueError:
                                print("Not float value")
                        if query[2] == "length":
                            try:
                                obj.length = float(query[3])
                            except ValueError:
                                print("Not float value")
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
                        self.run_query(("add", name1, det.mass*ratioa, det.length*ratioa))
                        self.run_query(("add", name2, det.mass*ratiob, det.length*ratiob))
                        self.run_query(("move_to", name1, det.pos))
                        self.run_query(("move_to", name2, det.pos + det.length*ratioa))
                        self.run_query(("remove", det.name))
                        break
                else:
                    print("No detail with such name")
            case "copy":
                for det in self.details:
                    if det.name == query[1]:
                        self.run_query(("add", query[2], det.mass, det.length))
                        self.run_query(("move_to", query[2], det.pos))
                        break
                else:
                    print("No detail with this name")
            case "calculate":
                calculate(self.details)
