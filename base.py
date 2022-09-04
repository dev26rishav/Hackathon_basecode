#!/usr/bin/env python
import sys, os
from tkinter import *
from PIL import ImageTk, Image
import cProfile
import pstats


SCALING_FACTOR = 50
OFFSET_FACTOR = 0.5
# Actual value
BOARD_SIZE = None
## Dictionary to store the widget information
widgetInfoDict = {}
# widgetInfoDict {  "root" : <root widget object (main window")>,
#                   "pw"    : <reference to paned window inside the top (horizontal)>,
#                   "lf1"   : <reference to label_frame1 inside the horizontal paned window>
#                   "lf2"   : <reference to label_frame2 inside the horizontal paned window>
#                   "text"  : <reference to text widget inside the label_frame1>,
#                   "canvas"  : <reference to canvas widget inside the label_frame1>,
#               }

## Dictionary to store piece info
pieceInfoDict = {}
# pieceInfoDict {  "<piece_1>" : [<x_cord> , <y_cord>],
#                   "<piece_2>" : [<x_cord> , <y_cord>]
#               }


## Function to create the toplevel window, text and canvas widget
#
def createEditor(fileContents):
    # main tkinter window
    widgetInfoDict["root"] = Tk()
    widgetInfoDict["root"].geometry(str(widgetInfoDict["root"].winfo_screenwidth()) + 'x' + str(
        int(widgetInfoDict["root"].winfo_screenheight() * 0.9)))

    # panedwindow object
    widgetInfoDict["pw"] = PanedWindow(widgetInfoDict["root"], orient='horizontal')

    widgetInfoDict["lf1"] = LabelFrame(widgetInfoDict["root"], text='Editor', width=500)
    widgetInfoDict["lf1"].pack(expand='yes', fill=BOTH)

    widgetInfoDict["lf2"] = LabelFrame(widgetInfoDict["root"], text='Canvas', width=500)
    widgetInfoDict["lf2"].pack(expand='yes', fill=BOTH)

    widgetInfoDict["text"] = Text(widgetInfoDict["lf1"])
    widgetInfoDict["text"].pack(fill=BOTH, expand=True)

    widgetInfoDict["canvas"] = Canvas(widgetInfoDict["lf2"])
    widgetInfoDict["canvas"].pack(fill=BOTH, expand=True)

    widgetInfoDict["canvas"].pack()

    widgetInfoDict["pw"].add(widgetInfoDict["lf1"])
    widgetInfoDict["pw"].add(widgetInfoDict["lf2"])
    widgetInfoDict["pw"].pack(fill=BOTH, expand=True)
    widgetInfoDict["pw"].configure(sashrelief=RAISED)

    renderBoard(BOARD_SIZE)

    btn = Button(widgetInfoDict["lf1"], text='Evaluate', bd='5', command=placeSequenceProfiler)
    btn.pack(side='bottom')
    widgetInfoDict["text"].insert(END, fileContents)
    widgetInfoDict["root"].mainloop()


## Function to read the data from sequence cmds (placeSequence.txt) file and write to the text editor
#
#   @param placementSwqCmdsFile : Reference to the area.txt file path
#
def readData(placmntSeqCmdsFile):
    with open(placmntSeqCmdsFile, 'r') as cmdFileObj:
        fileContents = cmdFileObj.read()
        # widgetInfoDict["text"].insert(END, fileContent)
        return fileContents

img_ref = []


def renderPiece(x, y, shape):
    x, y = x + 0.5, y + 0.5
    shapeImage = shape.split('_')
    img = ImageTk.PhotoImage(Image.open(f"ChessPieces{os.sep}{shapeImage[0]}.png"))
    widgetInfoDict["canvas"].create_image(x * SCALING_FACTOR, y * SCALING_FACTOR, image=img)
    img_ref.append(img)

## Function to draw the board on the canvas
#
#   @param boardSize : integer number.
#
def renderBoard(boardSize):
    renderRectangle([0, 0, boardSize, boardSize], "board")
    for n in range(boardSize):
        renderLine([n, 0, n, boardSize])
        renderLine([0, n, boardSize, n])
    return


## Function to draw the rectangle on the canvas using the coordinates
#
#   @param coord : tuple with lower left and upper right coordinates
#   @param name : Reference to the shape name
#
# Info : In tkinter, rectangle/square can be drawn by passing the lower left and upper right coordinates, ex: to draw a
# 5(l), 7(b) rectangle from origin, coordinates are (0,0) and (5,7)
#
def renderRectangle(coords, name=None):
    coords = [coord * SCALING_FACTOR for coord in coords]
    coordref = widgetInfoDict["canvas"].create_rectangle(coords[0], coords[1], coords[2], coords[3])
    # ref 'coordref' can be used to print the coordinates of the rendered name, i.e.
    # print(widgetInfoDict["canvas"].coords(coordref))
    # Add the shape name to the rendered name
    if name:
        widgetInfoDict["canvas"].create_text((coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2, text=name)


## Function to draw a line on the canvas using the coordinates
#
#   @param coord : [x1, y1, x2, y2]
#   @param color : Color of the line
#   @param name :  Reference to the line name
#
def renderLine(coords, color="black", name=None):
    coords = [coord * SCALING_FACTOR for coord in coords]
    coordref = widgetInfoDict["canvas"].create_line(coords[0], coords[1], coords[2], coords[3], fill=color)
    # ref 'coordref' can be used to print the coordinates of the rendered name, i.e.
    # print(widgetInfoDict["canvas"].coords(coordref))
    # Add the shape name to the rendered name
    if name:
        widgetInfoDict["canvas"].create_text((coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2, text=name)


## Function to read the coordinate information from the file
#
#   @param pieceInfoFile : Reference to the pieceInfoFile path
#
def readPieceInfoFromFile(pieceInfoFile):
    with open(pieceInfoFile, 'r') as pieceFileObj:
        for line in pieceFileObj:
            dataLst = line.split()
            if len(dataLst) != 3:
                print("Couldn't process the line " + line + " in " + str(
                    pieceInfoFile) + "due to missing of information. Format is '<piece_name> <x_cord> <y_cord>', "
                                     "hence skipping this line")
                continue
            pieceInfoDict[dataLst[0]] = [int(dataLst[1]), int(dataLst[2])]

def profile(function,*arguments):
    pr = cProfile.Profile()
    pr.enable()
    function(*arguments)
    pr.disable()
    return pstats.Stats(pr).sort_stats('cumtime')

def placeSequenceProfiler():
    profile(placeSequence).print_stats()
    
## Function which will be executed after the 'Evaluate' button click
#
def placeSequence():
    # clear the canvas
    widgetInfoDict["canvas"].delete("all")
    # Re-render the board
    renderBoard(BOARD_SIZE)
    renderPiece(WHITE_X, WHITE_Y, 'WhiteKing')


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "Please pass the <Black Positions> file path, <White King Coordinates> and <Board Size> as arguments in "
            "the command line")
        sys.exit()

    BOARD_SIZE = int(sys.argv[4])
    WHITE_X, WHITE_Y = int(sys.argv[2]), int(sys.argv[3])
    data = readData(sys.argv[1])
    createEditor(data)
