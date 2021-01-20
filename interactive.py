from tkinter import *
from dotsandboxes import Game

import sys
import importlib

assert len(sys.argv) is 3
_, red_module, blue_module = sys.argv


bots = {
  'red': importlib.import_module(red_module),
  'blue': importlib.import_module(blue_module),
}

game = Game()

def display(state):

	canvas.delete(ALL)

	square_width = min(int(canvas['width']),int(canvas['height']))

	step = square_width/state.game.width
	r = int(step/10.0)
	w = int(step/15.0)

	def make_callback(move):
		def callback(event):
			if state.whose_turn == 'red' and RED_AI.get():
				print("Give the red guy a chance to think!")
				return
			if state.whose_turn == 'blue' and BLUE_AI.get():
				print("The blue lady needs more time to think!")
				return
			make_move(state, move)
		return callback


	for i,j in state.game.h_lines:
		x = (i+0.5)*step
		y = (j+0.5)*step
		if (i,j) in state.h_line_owners:
			owner = state.h_line_owners[(i,j)]
			canvas.create_line(x,y,x+step,y,width=w,fill=owner)
		else:
			line = canvas.create_line(x,y,x+step,y,width=w/2,dash=(w,w),fill=state.whose_turn)
			canvas.tag_bind(line,"<Button-1>",make_callback(('h',(i,j))))
			
	for i,j in state.game.v_lines:
		x = (i+0.5)*step
		y = (j+0.5)*step
		if (i,j) in state.v_line_owners:
			owner = state.v_line_owners[(i,j)]
			canvas.create_line(x,y,x,y+step,width=w,fill=owner)
		else:
			line = canvas.create_line(x,y,x,y+step,width=w/2,dash=(w,w),fill=state.whose_turn)
			canvas.tag_bind(line,"<Button-1>",make_callback(('v',(i,j))))
			
	for i,j in state.game.boxes:
		x = (i+0.5)*step
		y = (j+0.5)*step
		if (i,j) in state.box_owners:
			owner = state.box_owners[(i,j)]
			canvas.create_rectangle(x+r,y+r,x+step-r,y+step-r,fill=owner)

	for i,j in state.game.dots:
		x = (i+0.5)*step
		y = (j+0.5)*step
		canvas.create_oval(x-r,y-r,x+r,y+r,fill='black')

	if not state.is_terminal():
		if state.whose_turn == 'red' and RED_AI.get():
			think(state)
		elif state.whose_turn == 'blue' and BLUE_AI.get():
			think(state)

	canvas.pack(side=RIGHT)
	master.update()

def make_move(state, move):
	moves = state.get_moves()
	if move in moves:
		UNDO_STACK.append(state)
		next_state = state.copy()
		next_state.apply_move(move)
		display(next_state)
	else:
		print(move, "not in legal moves!")

def think(state):
	import threading
	class ThinkingThread(threading.Thread):
		def run(self):
			move = bots[state.whose_turn].think(state.copy())
			make_move(state, move)

	ThinkingThread().start()


def restart():
	initial_state = game.make_initial_state()
	UNDO_STACK[:] = [initial_state]
	display(initial_state)

def undo():
	if len(UNDO_STACK) > 1:
		UNDO_STACK.pop()
		display(UNDO_STACK[-1])

master = Tk()

UNDO_STACK = []
RED_AI = IntVar(master)
BLUE_AI = IntVar(master)

master.title("Dots and Boxes")

w = 600
h = 600

toolbar = Frame(master, width=w, height=h+20)
toolbar.pack(side=BOTTOM)

undo_btn = Button(toolbar, text="Undo", command=undo)
undo_btn.pack(side=LEFT)

restart_btn = Button(toolbar, text="Restart", command=restart)
restart_btn.pack(side=LEFT)

red_ai_btn = Checkbutton(toolbar, text="Red AI", variable=RED_AI)
red_ai_btn.pack(side=LEFT)
blue_ai_btn = Checkbutton(toolbar, text="Blue AI", variable=BLUE_AI)
blue_ai_btn.pack(side=LEFT)

canvas = Canvas(master, width=w, height=h)
canvas.pack(side=RIGHT)

restart()

mainloop()
