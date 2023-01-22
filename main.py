def znovu():
    import sys
    import pygame
    import time
    from dokusan import generators
    import numpy
    pygame.font.init()

    try:
        class Grid:
            numbers = numpy.int_(list(str(generators.random_sudoku(avg_rank=160))))
            board = numbers.reshape(9, 9)
            
            def __init__(self, rows, cols, width, height):
                self.rows = rows
                self.cols = cols
                self.cubes = [[Cube(self.board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
                self.width = width
                self.height = height
                self.model = None
                self.selected = None

            def update_model(self):
                self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

            def place(self, val):
                row, col = self.selected
                if self.cubes[row][col].value == 0:
                    self.cubes[row][col].set(val)
                    self.update_model()

                    if valid(self.model, val, (row, col)) and solve(self.model):
                        return True
                    else:
                        self.cubes[row][col].set(0)
                        self.cubes[row][col].set_temp(0)
                        self.update_model()
                        return False

            def sketch(self, val):
                row, col = self.selected
                self.cubes[row][col].set_temp(val)

            def draw(self, win):
                gap = self.width / 9
                for i in range(self.rows + 1):
                    if i % 3 == 0 and i != 0:
                        thick = 4
                    else:
                        thick = 1
                    pygame.draw.line(win, (0, 0, 0), (0, i * gap), (self.width, i * gap), thick)
                    pygame.draw.line(win, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)

                for i in range(self.rows):
                    for j in range(self.cols):
                        self.cubes[i][j].draw(win)

            def select(self, row, col):
                for i in range(self.rows):
                    for j in range(self.cols):
                        self.cubes[i][j].selected = False

                self.cubes[row][col].selected = True
                self.selected = (row, col)

            def clear(self):
                row, col = self.selected
                if self.cubes[row][col].value == 0:
                    self.cubes[row][col].set_temp(0)

            def click(self, pos):
                if pos[0] < self.width and pos[1] < self.height:
                    gap = self.width / 9
                    x = pos[0] // gap
                    y = pos[1] // gap
                    return int(y), int(x)
                else:
                    return None

            def is_finished(self):
                for i in range(self.rows):
                    for j in range(self.cols):
                        if self.cubes[i][j].value == 0:
                            return False
                return True
        
        class Cube:
            rows = 9
            cols = 9

            def __init__(self, value, row, col, width, height):
                self.value = value
                self.temp = 0
                self.row = row
                self.col = col
                self.width = width
                self.height = height
                self.selected = False

            def draw(self, win):
                fnt = pygame.font.SysFont("comicsans", 40)

                gap = self.width / 9
                x = self.col * gap
                y = self.row * gap

                if self.temp != 0 and self.value == 0:
                    text = fnt.render(str(self.temp), True, (128, 128, 128))
                    win.blit(text, (x + 5, y + 5))
                elif not (self.value == 0):
                    text = fnt.render(str(self.value), True, (0, 0, 0))
                    win.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))

                if self.selected:
                    pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

            def set(self, val):
                self.value = val

            def set_temp(self, val):
                self.temp = val

        class Button:
            def __init__(self, x, y, image, scale):
                width = image.get_width()
                height = image.get_height()
                self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
                self.rect = self.image.get_rect()
                self.rect.topleft = (x, y)
                self.clicked = False

            def draw(self, surface):
                action = False
                pos = pygame.mouse.get_pos()

                if self.rect.collidepoint(pos):
                    if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                        self.clicked = True
                        action = True

                if pygame.mouse.get_pressed()[0] == 0:
                    self.clicked = False

                surface.blit(self.image, (self.rect.x, self.rect.y))

                return action
                
        def solve(bo):
            find = find_empty(bo)
            if not find:
                return True
            else:
                row, col = find

            for i in range(1, 10):
                if valid(bo, i, (row, col)):
                    bo[row][col] = i

                    if solve(bo):
                        return True

                    bo[row][col] = 0
                
            return False
                    
        def valid(bo, num, pos):
            # Check row
            for i in range(len(bo[0])):
                if bo[pos[0]][i] == num and pos[1] != i:
                    return False

            # Check column
            for i in range(len(bo)):
                if bo[i][pos[1]] == num and pos[0] != i:
                    return False

            # Check box
            box_x = pos[1] // 3
            box_y = pos[0] // 3

            for i in range(box_y * 3, box_y * 3 + 3):
                for j in range(box_x * 3, box_x * 3 + 3):
                    if bo[i][j] == num and (i, j) != pos:
                        return False

            return True

        def find_empty(bo):
            for i in range(len(bo)):
                for j in range(len(bo[0])):
                    if bo[i][j] == 0:
                        return i, j  # row, col

            return None
            
        def redraw_window(win, board, cas, strikes, vyhra, vysvetleni, prohra, strikez, final, final_render, bila):
            win.fill((255, 255, 255))
            # Draw time
            fnt = pygame.font.SysFont("comicsans", 30)
            text = fnt.render("Čas: " + format_time(cas), True, (0, 0, 0))
            win.blit(text, (368, 550))
            # Draw Srdicka
            srdce_img = pygame.image.load('resources/srdce.png')
            srdce_scale = pygame.transform.scale(srdce_img, (120, 40))
            win.blit(srdce_scale, (20, 550))
            # Draw Strikes
            text = fnt.render("X  " * strikes, True, (0, 0, 0))
            win.blit(text, (29, 546))
            # Draw Strikez
            text = fnt.render("X  X  X" * strikez, True, (0, 0, 0))
            win.blit(text, (29, 546))
            # Draw Board
            board.draw(win)
            # Draw Vyhra
            vyhra_img = pygame.image.load('resources/vyhra.png')
            vyhra_scale = pygame.transform.scale(vyhra_img, (476 * vyhra, 291 * vyhra))
            win.blit(vyhra_scale, (32, 150))
            # Draw Pravidla
            pravidla_img = pygame.image.load('resources/pravidla_vysvetleni.png')
            pravidla_scale = pygame.transform.scale(pravidla_img, (400 * vysvetleni, 489 * vysvetleni))
            win.blit(pravidla_scale, (70, 28))
            # Draw Prohra
            prohra_img = pygame.image.load('resources/prohra.png')
            prohra_scale = pygame.transform.scale(prohra_img, (476 * prohra, 311 * prohra))
            win.blit(prohra_scale, (32, 150))
            # Draw Bila
            bila_img = pygame.image.load('resources/bila.png')
            bila_scale = pygame.transform.scale(bila_img, (150 * bila, 50 * bila))
            win.blit(bila_scale, (368, 550))
            # Draw time
            fnt = pygame.font.SysFont("comicsans", 25)
            text = fnt.render(("Dohráno v čase: " + format_time(final)) * final_render, True, (255, 255, 255))
            win.blit(text, (150, 360))
            
        def format_time(secs):
            sec = secs % 60
            minute = secs // 60

            if minute in range(0, 10):
                minuty = "0" + str(minute)
            else:
                minuty = str(minute)

            if sec in range(0, 10):
                sekundy = "0" + str(sec)
            else:
                sekundy = str(sec)

            mat = minuty + ":" + sekundy
            return mat

        def main():
            win = pygame.display.set_mode((540, 680))
            pygame.display.set_caption("Sudoku")
            board = Grid(9, 9, 540, 540)
            key = None
            run = True
            start = time.time()
            
            strikes = 0
            vyhra = 0
            vysvetleni = 0
            prohra = 0
            strikez = 0
            final = 0
            final_render = 0
            bila = 0

            nova_hra = pygame.image.load('resources/nova_hra.png').convert_alpha()
            pravidla = pygame.image.load('resources/pravidla.png').convert_alpha()
            ukoncit = pygame.image.load('resources/ukoncit.png').convert_alpha()
            reset = pygame.image.load('resources/reset.png').convert_alpha()
            nova_hra_button = Button(20, 600, nova_hra, 1)
            pravidla_button = Button(208, 600, pravidla, 1)
            ukoncit_button = Button(380, 600, ukoncit, 1)
            reset_button = Button(246, 546, reset, 1)

            while run:
                
                play_time = round(time.time() - start)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1:
                            key = 1
                        if event.key == pygame.K_2:
                            key = 2
                        if event.key == pygame.K_3:
                            key = 3
                        if event.key == pygame.K_4:
                            key = 4
                        if event.key == pygame.K_5:
                            key = 5
                        if event.key == pygame.K_6:
                            key = 6
                        if event.key == pygame.K_7:
                            key = 7
                        if event.key == pygame.K_8:
                            key = 8
                        if event.key == pygame.K_9:
                            key = 9
                        if event.key == pygame.K_KP1:
                            key = 1
                        if event.key == pygame.K_KP2:
                            key = 2
                        if event.key == pygame.K_KP3:
                            key = 3
                        if event.key == pygame.K_KP4:
                            key = 4
                        if event.key == pygame.K_KP5:
                            key = 5
                        if event.key == pygame.K_KP6:
                            key = 6
                        if event.key == pygame.K_KP7:
                            key = 7
                        if event.key == pygame.K_KP8:
                            key = 8
                        if event.key == pygame.K_KP9:
                            key = 9
                        if event.key == pygame.K_DELETE:
                            board.clear()
                            key = None
                        if event.key == pygame.K_BACKSPACE:
                            board.clear()
                            key = None
                        if event.key == pygame.K_RETURN:
                            i, j = board.selected
                            if board.cubes[i][j].temp != 0:
                                if board.place(board.cubes[i][j].temp):
                                    print("Spravne")
                                else:
                                    strikes += 1
                                key = None

                                if board.is_finished():
                                    vyhra = 1
                                    bila = 1
                                    final = round(time.time() - start)
                                    final_render = 1
                                    run = True
                        if event.key == pygame.K_KP_ENTER:
                            i, j = board.selected
                            if board.cubes[i][j].temp != 0:
                                if board.place(board.cubes[i][j].temp):
                                    print("Spravne")
                                else:
                                    strikes += 1
                                key = None

                                if board.is_finished():
                                    vyhra = 1
                                    bila = 1
                                    final = round(time.time() - start)
                                    final_render = 1
                                    run = True

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        clicked = board.click(pos)
                        if clicked:
                            board.select(clicked[0], clicked[1])
                            key = None

                if board.selected and key is not None:
                    board.sketch(key)

                redraw_window(win, board, play_time, strikes, vyhra, vysvetleni, prohra, strikez, final, final_render,
                              bila)

                if nova_hra_button.draw(win):
                    pygame.quit()
                    time.sleep(0.4)
                    znovu()

                if strikes == 3:
                    strikes = 0
                    strikez = 1
                    prohra = 1
                    bila = 1
                    final_render = 0

                if pravidla_button.draw(win):
                    vysvetleni = 1

                if ukoncit_button.draw(win):
                    pygame.quit()

                if reset_button.draw(win):
                    vyhra = 0
                    vysvetleni = 0
                    prohra = 0
                    final_render = 0

                pygame.display.update()

        main()
        pygame.quit()
    except Exception:
        sys.exit(1)
    # hi 


znovu()
