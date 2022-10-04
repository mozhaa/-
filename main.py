from Detail import Detail
from PIL import Image, ImageDraw
from window import Window
import threading
import numpy as np
import pickle
import sys
import cv2


def main(args):
    '''
    Commands:
        help
        add {name:str} {mass:float} {length:float}
        move {name:str} {delta:float}
        move_to {name:str} {pos:float}
        rename {oldname:str} {newname:str}
        print {name:str}
        list
        save {filename}

    '''
    print(main.__doc__)
    window = Window()


def query_handler(window):
    details = list()
    while True:
        query = input().split(" ")
        run_query(query, details)
        window.show_details(details)


def run_query(query, details):
    match query[0]:
        case "help":
            print(main.__doc__)
        case "add":
            try:
                details.append(Detail(name=query[1], mass=float(query[2]), length=float(query[3])))
            except ValueError:
                print("Invalid mass or length (not integers)")
        case "move":
            for obj in details:
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
            for obj in details:
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
            for obj in details:
                if obj.name == query[1]:
                    if not obj.rename(query[2], details):
                        print("This name is already in use")
                    break
            else:
                print("No detail with this name")
        case "print":
            for obj in details:
                if obj.name == query[1]:
                    print("Detail", repr(obj), sep="\n\t")
                    break
            else:
                print("No detail with this name")
        case "list":
            if len(details) == 0:
                print("No details")
                return
            print("Details:")
            for obj in details:
                print('\t' + repr(obj))
        case "save":
            with open(query[1], "wb") as file:
                pickle.dump(details, file)


if __name__ == "__main__":
    main(sys.argv)
