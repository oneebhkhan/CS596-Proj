import psychopy.visual
import psychopy.event

win = psychopy.visual.Window(
    size=[400, 400],
    units="pix",
    fullscr=False
)

frames = []

# store each frame as a separate 'ImageStim'
for frame_num in xrange(1, 50):

    frame = psychopy.visual.ImageStim(
        win=win,
        units="pix",
        size=[400, 400],
        image="field_python_{n:02d}.png".format(n=frame_num)
    )

    frames.append(frame)

i_frame_to_draw = 0

keep_going = True

while keep_going:

    # because we rendered as 15fps, draw each frame x4 (assuming 60Hz
    # refresh)
    for _ in xrange(4):
        frames[i_frame_to_draw].draw()
        win.flip()

    keys = psychopy.event.getKeys()

    keep_going = (len(keys) == 0)

    # increment the frame to draw, wrapping around when necessary
    i_frame_to_draw = (i_frame_to_draw + 1) % len(frames)

win.close()