import curses
import time
from collections import deque
from random import randint

def main(stdscr):
    # the location of a lot of these variable updates, including this one, is
    # really arbitrary, but it works.
    lastTime = time.time()

    # make the cursor invisible
    curses.curs_set(0)
    # scrolling is not okay (it often happens anyways)
    stdscr.scrollok(1)
    # we use the cursor keys to control the game, so they can't be used to
    # control the cursor.  this makes curses interpret them as normal keys
    stdscr.keypad(1)
    # getch takes input, but doesn't wait for it (no delay in the program)
    stdscr.nodelay(1)
    # I don't know what this does
    curses.raw()
    # currently pressed key(s?)
    key = 0
    # start screen, up, down, left, right
    # the start screen is defined by a direction because it makes it easy to
    # handle the transition to any other direction at game start
    # also because enumeration support is shit
    direction = -1
    # I created this for the old input system (no queue), and I still use it,
    # but I'm not sure if I really need it
    tempDirection = -1
    # because those environment variables were just too cumbersome.
    windowCols = curses.COLS
    windowRows = curses.LINES
    # the center of the window
    locationX = windowCols / 2 - 1
    locationY = windowRows / 2 - 1
    # a list containing all the segments of the worm!
    # I folded it over to comply with the line length limit
    segments = [(locationX, locationY), (locationX - 1, locationY),
                (locationX - 2, locationY)]

    # the randomly generated food location (for some reason the edges of the
    # window cause the program to crash, so we don't put it there.)
    foodX = randint(1, windowCols - 2)
    foodY = randint(1, windowRows - 2)

    updateTime = 0.08
    framesSinceLast = 0
    # the frame limit simply defines the length of a time.sleep call
    # without it, the terminal is refreshed by curses tens of thousands of times
    # per second, which is ridiculous (even 60 is ridiculous, I'm just doing it
    # because I'm too lazy to handle input better)
    # increase this value if you're some kind of snake god who wants to enter
    # more than 60 commands per game update (which is set to 0.1 seconds)
    frameLimit = 60

    # the inputQueue allows multiple commands to entered within one game update
    # (though only one command may be entered per frame)
    # they are then executed one by one in subsequent game updates
    # possibly the only non-standard part of this program (though certainly a
    # common addition, it is a little bit fancy)
    inputQueue = deque([])

    # stops the loop because I don't know how to break out of a nested loop
    stop = 0

    # pauses the loop
    pause = 0
    
    # I don't know why this one is abstracted, but whatever
    wrapKey = "w"
    lastWrap = 0
    # causes the snake to wrap around instead of hitting the edge
    wrap = 0

    # the border doesn't work, but the program acts as if it exists (hitting the
    # character positions at the edge of the window if a failure state)
    # someone fix this
    stdscr.border()

    # game loop! handles input and stuff
    while 1:
        # sleep to limit update rate (doesn't affect game speed, but gives the
        # CPU a break)
        time.sleep(1.0 / (frameLimit))
        # count frames for a cool fps counter
        framesSinceLast += 1

        # clear everything on stdscr from the last pass
        stdscr.clear()
        # score and fps first so they get overwritten by other objects
        stdscr.addstr(1, 2, str(len(segments) / 3 - 1))
        if wrap:
            stdscr.addstr(1, windowCols - 22, "WRAP")
        else:
            stdscr.addstr(1, windowCols - 22, "BOUND")
        stdscr.addstr(1, windowCols - 15, "fps: " +
            str(int(framesSinceLast / (time.time() - lastTime))))

        # handle input!
        if key == ord("q"):
            # "q" is the only input which gets handled immediately (quit)
            break
            
        # toggle wrap mode
        if key == ord(wrapKey) and direction == -1:
            if not lastWrap:
                if wrap:
                    wrap = 0
                else:
                    wrap = 1
                lastWrap = 1
        else:
            lastWrap = 0
            

        # pause (just stops the game from updating, loop still runs)
        if key == ord("p"):
            # clear the input queue (only matters for unpause)
            # otherwise inputs entered while paused will be executed
            inputQueue.clear()
            # flip flop
            if pause:
                pause = 0
            else:
                pause = 1

        # everything else gets tossed in the queue
        # only one key per frame, otherwise we wouldn't know which one was
        # pressed first (whatever)
        # oh, and only reasonable (though not necessarily valid) inputs are
        # accepted, so you can't spam the queue with random letters
        elif key == curses.KEY_RIGHT:
            inputQueue.append(3)
        elif key == curses.KEY_LEFT:
            inputQueue.append(2)
        elif key == curses.KEY_UP:
            inputQueue.append(0)
        elif key == curses.KEY_DOWN:
            inputQueue.append(1)

        # if we're still on the splash screen, write the title
        if direction == -1:
            stdscr.addstr(windowRows / 2 - 1, windowCols / 2 - 4, "Snake!")

        # the game itself only updates every 0.1 seconds, so if this frame
        # occurs after that much time has passed, we update the game
        if time.time() - lastTime > updateTime and not pause:
            # I'm listening to a song about mopeds right now (Downtown)
            # that nested loop break handling I mentioned (I'm really sorry)
            if stop:
                break

            # check for a food collision (if it's already in the worm, it's free
            # because I'm lazy)
            if (foodX, foodY) in segments:
                # add three segments to the worm (they get thrown on the end of
                # the list in the same position as the end and get sorted out as
                # the whole thing updates)
                for repeat in xrange(0, 9):
                    segments.append(segments[len(segments) - 1])
                # and produce a new random food if we ate it
                foodX = randint(1, windowCols - 2)
                foodY = randint(1, windowRows - 2)

            # arbitrary position for time update (if I didn't talk about it
            # earlier, lastTime just keeps track of how often the game is
            # updated, so it is independant of framerate)
            lastTime = time.time()

            # pop off the inputQueue and handle it, if there is anything there
            if len(inputQueue) > 0:
                tempDirection = inputQueue.popleft()

                # if the input is invalid, it gets popped anyways, but nothing
                # happens (otherwise the game would get stuck)
                # one thing to note, if the input is invalid, it still takes up
                # this entire update cycle, so don't make mistakes
                if tempDirection == 3 and direction != 2:
                    direction = 3
                elif tempDirection == 2 and direction != 3:
                    direction = 2
                elif tempDirection == 0 and direction != 1:
                    direction = 0
                elif tempDirection == 1 and direction != 0:
                    direction = 1

            # move the location depending upon the direction
            # in practice, this moves the front segment of the worm, but that
            # actually is done a bit later on
            if direction == 0:
                locationY -= 1
            elif direction == 1:
                locationY += 1
            elif direction == 2:
                locationX -= 1
            elif direction == 3:
                locationX += 1

            # check for collisions between the front segment and any other
            # it looks weird because it might be possible (when add segments)
            # for some of the segments to be in the same place but not colliding
            # if they are consecutive in the list (consecutive segments can
            # never collide anyways)
            # then, move the segment up to the position of the one previous
            for i in xrange(len(segments) - 1, 0, -1):
                if segments[i] == segments[0] and segments[i] != segments[i - 1]:
                    stop = 1
                segments[i] = segments[i - 1]

            # check for collision with the border of the window
            if not wrap:
                if locationX < 1 or locationX > windowCols - 2 or locationY < 1 or locationY > windowRows - 2:
                    stop = 1
            else:
                if locationX < 1:
                    locationX = windowCols - 2
                if locationX > windowCols - 2:
                    locationX = 1
                if locationY < 1:
                    locationY = windowRows - 2
                if locationY > windowRows - 2:
                    locationY = 1

            # set the front segment to the position that was updated
            # I think this is in the wrong place, and might be the source of some
            # of the problems with edge collision, but whatever, it works
            segments[0] = (locationX, locationY)

            framesSinceLast = 0

        # if not on the splash screen, draw the food and worm segments
        if direction != -1:
            stdscr.addstr(foodY, foodX, "!")
            for segment in segments:
                stdscr.addstr(segment[1], segment[0], "#")

        # update keyboard input
        key = stdscr.getch()

    # !!! game over screen !!!
    # clear the stdscr
    stdscr.clear()
    # write stuff
    stdscr.addstr(windowRows / 2 - 2, windowCols / 2 - 6, "Game Over!")
    score = str(len(segments) / 3)
    stdscr.addstr(windowRows / 2, windowCols / 2 - ((len(score) + 7) / 2 + 1), "Score: " + score)
    stdscr.addstr(windowRows / 2 + 2, windowCols / 2 - 10, "Press R to Restart")
    # aren't looping anymore, and will just wait for the user to tell the
    # program what to do, so getch is set to delay again
    stdscr.nodelay(0)
    # if the next key input is "r," go ahead and call main again (there's
    # probably a more responsible way to do this)
    if stdscr.getch() == ord("r"):
        main(stdscr)
    # if the input is anything else, we just let the function end and curses
    # handles quiting the program

# voodoo!
curses.wrapper(main)
