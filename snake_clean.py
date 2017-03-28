import curses
import time
from collections import deque
from random import randint

def main(stdscr):
            lastTime = time.time()

        curses.curs_set(0)
        stdscr.scrollok(1)
            stdscr.keypad(1)
        stdscr.nodelay(1)
        curses.raw()
        key = 0
                    direction = -1
            tempDirection = -1
        windowCols = curses.COLS
    windowRows = curses.LINES
        locationX = windowCols / 2 - 1
    locationY = windowRows / 2 - 1
            segments = [(locationX, locationY), (locationX - 1, locationY),
                (locationX - 2, locationY)]

            foodX = randint(1, windowCols - 2)
    foodY = randint(1, windowRows - 2)

    updateTime = 0.08
    framesSinceLast = 0
                            frameLimit = 60

                        inputQueue = deque([])

        stop = 0

        pause = 0

        wrapKey = "w"
    lastWrap = 0
        wrap = 0

                stdscr.border()

        while 1:
                        time.sleep(1.0 / (frameLimit))
                framesSinceLast += 1

                stdscr.clear()
                stdscr.addstr(1, 2, str(len(segments) / 3 - 1))
        if wrap:
            stdscr.addstr(1, windowCols - 22, "WRAP")
        else:
            stdscr.addstr(1, windowCols - 22, "BOUND")
        stdscr.addstr(1, windowCols - 15, "fps: " +
            str(int(framesSinceLast / (time.time() - lastTime))))

                if key == ord("q"):
                        break

                if key == ord(wrapKey) and direction == -1:
            if not lastWrap:
                if wrap:
                    wrap = 0
                else:
                    wrap = 1
                lastWrap = 1
        else:
            lastWrap = 0


                if key == ord("p"):
                                    inputQueue.clear()
                        if pause:
                pause = 0
            else:
                pause = 1

                                                elif key == curses.KEY_RIGHT:
            inputQueue.append(3)
        elif key == curses.KEY_LEFT:
            inputQueue.append(2)
        elif key == curses.KEY_UP:
            inputQueue.append(0)
        elif key == curses.KEY_DOWN:
            inputQueue.append(1)

                if direction == -1:
            stdscr.addstr(windowRows / 2 - 1, windowCols / 2 - 4, "Snake!")

                        if time.time() - lastTime > updateTime and not pause:
                                    if stop:
                break

                                    if (foodX, foodY) in segments:
                                                                for repeat in xrange(0, 9):
                    segments.append(segments[len(segments) - 1])
                                foodX = randint(1, windowCols - 2)
                foodY = randint(1, windowRows - 2)

                                                lastTime = time.time()

                        if len(inputQueue) > 0:
                tempDirection = inputQueue.popleft()

                                                                                if tempDirection == 3 and direction != 2:
                    direction = 3
                elif tempDirection == 2 and direction != 3:
                    direction = 2
                elif tempDirection == 0 and direction != 1:
                    direction = 0
                elif tempDirection == 1 and direction != 0:
                    direction = 1

                                                if direction == 0:
                locationY -= 1
            elif direction == 1:
                locationY += 1
            elif direction == 2:
                locationX -= 1
            elif direction == 3:
                locationX += 1

                                                                                    for i in xrange(len(segments) - 1, 0, -1):
                if segments[i] == segments[0] and segments[i] != segments[i - 1]:
                    stop = 1
                segments[i] = segments[i - 1]

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

                                                segments[0] = (locationX, locationY)

            framesSinceLast = 0

                if direction != -1:
            stdscr.addstr(foodY, foodX, "!")
            for segment in segments:
                stdscr.addstr(segment[1], segment[0], "
                key = stdscr.getch()

            stdscr.clear()
        stdscr.addstr(windowRows / 2 - 2, windowCols / 2 - 6, "Game Over!")
    score = str(len(segments) / 3)
    stdscr.addstr(windowRows / 2, windowCols / 2 - ((len(score) + 7) / 2 + 1), "Score: " + score)
    stdscr.addstr(windowRows / 2 + 2, windowCols / 2 - 10, "Press R to Restart")
            stdscr.nodelay(0)
            if stdscr.getch() == ord("r"):
        main(stdscr)

curses.wrapper(main)
