import tkinter as tk
from calculate import get_center_of_gravity
from PIL import Image, ImageDraw
import random
import pickle
from Detail import Detail


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("model")
        self.details = list()
        self.doc =     '''
            Commands:
                help
                add {name:str} {mass:float} {length:float}
                move {name:str} {delta:float}
                move_to {name:str} {pos:float}
                rename {oldname:str} {newname:str}
                edit {name:str} {property:str} {newvalue:float}
                remove {name:str}
                print {name:str}
                list
                save {filename}
                load {filename}

            '''

        self.entry_text = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.entry_text, width=100)
        self.entry.grid(row=0, column=0)

        self.button = tk.Button(self, text="O", command=self.button_click)
        self.button.grid(row=0, column=1)

        self.canvas = tk.Canvas(self, width=600, height=400)
        self.canvas.grid(row=1, column=0, columnspan=2)

        self.mainloop()

    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill = self.winfo_rgb(fill) + (alpha,)
            image = Image.new('RGBA', (x2-x1, y2-y1), fill)
            self.canvas.create_image(x1, y1, image=image, anchor='nw')
        self.canvas.create_rectangle(x1, y1, x2, y2, **kwargs)

    def show_details(self):
        self.canvas.delete("all")
        self.canvas.create_line(0, 200, 600, 200, fill="black", width=1)
        self.canvas.create_line(300, 198, 300, 202, fill='red', width=2)
        if len(self.details) == 0: return
        left_edge = min([det.pos for det in self.details])
        right_edge = max([(det.pos + det.length) for det in self.details])
        scale = max(abs(left_edge), abs(right_edge))
        center = get_center_of_gravity(self.details)
        for det in self.details:
            x1 = int(300 * (det.pos) / scale + 300)
            y1 = int(200 - 50 * (det.mass / det.length) / 2)
            x2 = int(300 * (det.pos + det.length) / scale + 300)
            y2 = int(200 + 50 * (det.mass / det.length) / 2)
            print(x1, y1, x2, y2)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=("#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])))
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
                except ValueError:
                    print("Invalid mass or length (not integers)")
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
