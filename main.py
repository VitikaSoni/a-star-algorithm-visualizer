import pygame
import math
from queue import PriorityQueue

GRID_COLOR = (128, 128, 128) #grey
DEFAULT_NODE_COLOR = (255, 255, 255) #white
BARRIER_COLOR = (0, 0, 0) #black
CLOSED_COLOR = (255, 165, 0) #orange
END_COLOR = (0, 0, 255) #blue
PATH_COLOR = (128, 0, 128) #purple
START_COLOR = (255, 0, 0) #red
OPEN_COLOR = (255, 255, 0) #yellow

WIDTH = 600
ROWCOL = 20

WIN = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("A* algorithm visualizer")

class Node:
    def __init__(self, row, col, width):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.width = width
        self.color = DEFAULT_NODE_COLOR

    def set_color(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def get_pos(self):
        return self.row, self.col

    def draw(self):
        pygame.draw.rect(WIN, self.color, (self.x, self.y, self.width, self.width ))
        
    def update_neighbors(self, grid):
            self.neighbors = []
            if self.row < ROWCOL - 1 and  grid[self.row + 1][self.col].get_color()!=BARRIER_COLOR:#Down
                self.neighbors.append(grid[self.row + 1][self.col])

            if self.row > 0 and grid[self.row - 1][self.col].get_color()!=BARRIER_COLOR:#Up
                self.neighbors.append(grid[self.row - 1][self.col])
                
            if self.col < ROWCOL - 1 and grid[self.row][self.col+1].get_color()!=BARRIER_COLOR: #Right
                self.neighbors.append(grid[self.row][self.col+1])

            if self.col > 0 and grid[self.row][self.col - 1].get_color()!=BARRIER_COLOR: #Left
                self.neighbors.append(grid[self.row][self.col - 1])

def make_grid():
    grid = []
    nodeWidth = WIDTH // ROWCOL
    for row in range(ROWCOL):
        grid.append([])
        for col in range(ROWCOL):
            node = Node(row, col, nodeWidth)
            grid[row].append(node)
    return grid

def draw_grid():
    gap = WIDTH // ROWCOL

    for row in range(ROWCOL):
        pygame.draw.line(WIN, GRID_COLOR, (0, row * gap), (WIDTH, row * gap))
        for col in range(ROWCOL):
            pygame.draw.line(WIN, GRID_COLOR, (col * gap, 0), (col * gap, WIDTH))
            
def draw(grid):
    WIN.fill(DEFAULT_NODE_COLOR)
    for row in grid:
        for node in row:
            node.draw()
    draw_grid()
    pygame.display.update()

def get_clicked_pos(pos):
    gap = WIDTH // ROWCOL
    x,y = pos

    row = x // gap
    col = y // gap

    return row, col
    
def reset(grid):
    for row in grid:
        for node in row:
            color = node.get_color()
            if color == OPEN_COLOR or color == CLOSED_COLOR or color == PATH_COLOR: 
                node.set_color(DEFAULT_NODE_COLOR)

def dist(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return math.sqrt(abs(x1 - x2)**2 + abs(y1 - y2)**2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current =  came_from[current]
        current.set_color(PATH_COLOR)
        draw()

def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0.0, count, start))

    open_set_hash = {start}

    came_from ={}

    g_score = {node : float("inf") for row in grid for node in row}
    g_score[start] = 0

    f_score = {node : float("inf") for row in grid for node in row}
    f_score[start] = dist(start.get_pos(), end.get_pos())

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            start.set_color(START_COLOR)
            end.set_color(END_COLOR)
            return

        for neighbor in current.neighbors:
            temp_g_score = g_score[current]+1

            if temp_g_score < g_score[neighbor]:
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + dist(neighbor.get_pos(), end.get_pos())
                came_from[neighbor] = current
                if neighbor not in open_set_hash:
                    count+=1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.set_color(OPEN_COLOR)

        draw()

        if current != start:
            current.set_color(CLOSED_COLOR)
           
def main():
    running = True
    usedPreviously = False

    start = None
    end = None

    grid = make_grid()
    while(running):
        draw(grid)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                node = grid[row][col]

                if start == None and node != end:
                    node.set_color(START_COLOR)
                    start = node
                elif end == None and node != start:
                    node.set_color(END_COLOR)
                    end = node
                elif node != end and node != start :
                    node.set_color(BARRIER_COLOR)
                
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                node = grid[row][col]

                node.set_color(DEFAULT_NODE_COLOR)

                if node == start:
                    start = None
                elif node == end:
                    end = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    if usedPreviously:
                        reset(grid)

                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    algorithm(lambda : draw(grid), grid, start, end)
                    usedPreviously = True

                elif event.key == pygame.K_c:
                    usedPreviously = False
                    start = None
                    end = None
                    grid = make_grid()

    pygame.quit()          

main()
