"""
Run file for PyHive
"""
import sys
import pygame
import math
import operator

# Constants
LEFT = 1
RIGHT = 3

WHITE = (255,255,255)
LIGHT_GREY = (200, 200, 200)
LIGHT_GREY_2 = (220, 220, 220)
YELLOW = (200, 200, 0)
PINK = (255, 150, 150)
BLACK = (0, 0, 0)

SCREEN_SIZE = (800, 600)
ORIGIN = (0, 0)
RADIUS = 50
GUI_CHIP_POS = (50, 50)
INVERSE_COORD = (-1, -1)
CHIP_DRAW_OFFSET = (-49, -55)
STACK_OFFSET = (0, -12)

class Hexagon(object):
    """Class for drawing a hollow hexagon"""

    # This is a list of keys marking coordinates of spaces in all directions
    adjoin_directions = [(0,-1),(1,-1),(1,0),(0,1),(-1,1),(-1,0)]

    # This is a list of keys marking relationships between the adjoining spaces 
    adjoin_loop = [(1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1)]

    def __init__(self, position, radius, color, line = 2, col = None, row = None):
        self.center = position
        self.radius = radius
        self.color = color
        self.line = line
        self.col = col
        self.row = row
        self.init_adjoins()

    def init_adjoins(self):
        """Setup a table of adjoining spaces"""
        self.adjoins = {}
        for key in Hexagon.adjoin_directions:
            self.adjoins[key] = None

    def hex_corner(self, i):
        """Get corner"""
        angle_deg = 60.0 * i
        angle_rad = math.pi / 180 * angle_deg
        return (self.center[0] + self.radius * math.cos(angle_rad),
                self.center[1] + self.radius * math.sin(angle_rad))

    def draw(self, surface, color = None, line = None):
        """Draw a hexagon"""
        if not color:
            color = self.color
        if not line:
            line = self.line
        points = [self.hex_corner(x) for x in range(6)]
        pygame.draw.polygon(surface, color, points, self.line)
        
    def __str__(self):
        return "Grid: ({col}, {row}), Pos: {pos}".format(col=self.col, row=self.row, pos=self.center)

class Chip(object):
    """Base class for drawing a chip on the board"""
    id = 0

    def __init__(self):
        self.offset = CHIP_DRAW_OFFSET
        self.stacked_chip = None
        self.covered_chip = None
        self.hexagon = None
        self.selection_hexagon = None
        self.id = Chip.id
        Chip.id += 1

    def draw(self, surface):
        """Draw the chip on top of the hexagon"""
        if self.hexagon:
            pos = tuple(map(operator.add, self.hexagon.center, self.offset))
            surface.blit(self.image, pos)

    def draw_outline(self, surface, color = YELLOW, line = 10):
        """Draw the outline of the chip if it's placed"""
        if self.selection_hexagon:
            self.selection_hexagon.draw(surface, color, line)

    def is_mouse_on(self, mouse_pos):
        if self.hexagon:
            vector = tuple(map(operator.sub, self.hexagon.center, mouse_pos))
            magnatude = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
            return magnatude < self.hexagon.radius

    def unstack_chip(self):
        # Don't unstack a chip with another on top
        if self.stacked_chip:
            raise ValueError("Can't unstack a covered chip")
        if self.covered_chip:
            # Disassociate chips
            self.covered_chip.stacked_chip = None
            self.covered_chip = None
        self.stacked_chip = None
        self.selection_hexagon = None

    def top_of_stack(self):
        if self.stacked_chip:
            return self.stacked_chip.top_of_stack()
        else:
            return self

    def __str__(self):
        on = "{type} {id}".format(type=type(self.covered_chip).__name__, id=self.covered_chip.id) if self.covered_chip else None
        return "{type} {id} - {pos}, on: {on}".format(type=type(self).__name__, id = self.id, pos=self.hexagon, on=on)

class PlusChip(Chip):
    """Class for drawing a chip with a plus on it"""

    def __init__(self):
        super(PlusChip, self).__init__()
        icon = pygame.image.load("images/Plus.png").convert_alpha()
        self.image = pygame.image.load("images/BlankChip.png").convert_alpha()
        self.image.blit(icon, (0,0))

class BeeChip(Chip):
    """Class for drawing a chip with a bee on it"""
    
    def __init__(self):
        super(BeeChip, self).__init__()
        icon = pygame.image.load("images/Bee.png").convert_alpha()
        self.image = pygame.image.load("images/BlankChip.png").convert_alpha()
        self.image.blit(icon, (0,0))

class AntChip(Chip):
    """Class for drawing a chip with a ant on it"""
    
    def __init__(self):
        super(AntChip, self).__init__()
        icon = pygame.image.load("images/Ant.png").convert_alpha()
        self.image = pygame.image.load("images/BlankChip.png").convert_alpha()
        self.image.blit(icon, (0,0))

class BeetleChip(Chip):
    """Class for drawing a chip with a beetle on it"""
    
    def __init__(self):
        super(BeetleChip, self).__init__()
        icon = pygame.image.load("images/Beetle.png").convert_alpha()
        self.image = pygame.image.load("images/BlankChip.png").convert_alpha()
        self.image.blit(icon, (0,0))

class GrasshopperChip(Chip):
    """Class for drawing a chip with a grasshopper on it"""
    
    def __init__(self):
        super(GrasshopperChip, self).__init__()
        icon = pygame.image.load("images/Grasshopper.png").convert_alpha()
        self.image = pygame.image.load("images/BlankChip.png").convert_alpha()
        self.image.blit(icon, (0,0))

class SpiderChip(Chip):
    """Class for drawing a chip with a spider on it"""
    
    def __init__(self):
        super(SpiderChip, self).__init__()
        icon = pygame.image.load("images/Spider.png").convert_alpha()
        self.image = pygame.image.load("images/BlankChip.png").convert_alpha()
        self.image.blit(icon, (0,0))

class ChipPool(object):
    """
    This class should act as a pool for a full set of basic chips
    When a peice gets played it should be removed from the pool
    and placed on the grid
    """

    def __init__(self):
        self.chip_set = [
            [BeeChip()],
            [SpiderChip() for i in range(2)],
            [BeetleChip() for i in range(2)],
            [GrasshopperChip() for i in range(3)],
            [AntChip() for i in range(3)]
        ]
        self._next = 0

    def peek(self):
        if not self.chip_set or not self.chip_set[self._next]:
            return None
        return self.chip_set[self._next][0]

    def pop(self):
        if not self.chip_set or not self.chip_set[self._next]:
            return None
        popped = self.chip_set[self._next][0]
        self.chip_set[self._next].remove(popped)
        # Remove list if it's now empty
        if not self.chip_set[self._next]:
            del self.chip_set[self._next]
            self._next = self._next % len(self.chip_set) if self.chip_set else 0
        return popped

    def next(self):
        self._next += 1
        self._next %= len(self.chip_set) if self.chip_set else 1
        return self.peek()

class PyHiveGame(object):
    """Class that draws a hive game when run"""

    def __init__(self, screen_size, hex_size):
        # Bring up
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        self.done = False
        # create grid
        self.init_hexagons(screen_size, hex_size)
        self.font = pygame.font.Font(None, 20)
        # setup draw_gui
        self.init_gui()
        # Setup screen coords and draw values
        self.spacing = (hex_size * 2 * 3 / 4, math.sqrt(3) / 2 * hex_size * 2)
        self.orig = tuple(map(operator.div, screen_size, (2, 2)))
        # Create chips
        self.init_chips()
        self.cursor = None

    def init_hexagons(self, screen_size, radius):
        color = LIGHT_GREY
        self.hexagons = {}
        self.screen_center = tuple(map(operator.div, screen_size, (2,2)))
        self.hexagons[ORIGIN] = Hexagon(position = self.screen_center, radius = radius, color = color, line = 1, col = 0, row = 0)

    def init_chips(self):
        self.chips = []
        self.chip_pool = ChipPool()
        self.selected_chip = None
        # put chip in the players "hand"
        start_chip = self.get_new_chip()

    def get_new_chip(self):
        new_chip = None
        if self.selected_chip == self.chip_pool.peek():
            new_chip = self.chip_pool.next()
        else:
            new_chip = self.chip_pool.peek()
        if not new_chip:
            return None
        self.set_grid_pos(new_chip, self.add_chip.hexagon)
        self.chips.append(new_chip)
        self.selected_chip = new_chip
        return new_chip

    def release_selected_chip(self):
        if self.selected_chip == self.chip_pool.peek():
            self.chip_pool.pop()
        self.selected_chip = None

    def init_gui(self):
        self.add_chip = (PlusChip())
        self.set_grid_pos(self.add_chip, Hexagon(GUI_CHIP_POS, RADIUS, BLACK))

    def set_grid_pos(self, chip, hexagon):
        if not chip:
            return
        chip.unstack_chip()
        chip.hexagon = hexagon
        if not chip.selection_hexagon:
            chip.selection_hexagon = Hexagon(hexagon.center, hexagon.radius, hexagon.color)
        chip.selection_hexagon.center = tuple(map(operator.add, chip.hexagon.center, STACK_OFFSET))
        # For hexagons in the grid, make sure there is space to expand_grid
        if hexagon.col != None and hexagon.row != None:
            self.expand_grid(hexagon)

    def expand_grid(self, hexagon):
        """Expand the space, where appropriate, around the newly occupied hexagon"""
        # Ensure adjoining space exist
        for key_index in range(6):
            key = Hexagon.adjoin_directions[key_index]
            inverse_key = tuple(map(operator.mul, key, INVERSE_COORD))
            if not hexagon.adjoins[key]:
                # Get coords
                axial_coords = tuple(map(operator.add, (hexagon.col, hexagon.row), key))
                screen_coords = self.axial_to_screen(axial_coords)
                # Create the new space in the draw table
                new_hexagon = Hexagon(screen_coords, hexagon.radius, hexagon.color, col=axial_coords[0], row=axial_coords[1])
                self.hexagons[axial_coords] = new_hexagon
                # Create the linked space and link it back
                hexagon.adjoins[key] = new_hexagon
                new_hexagon.adjoins[inverse_key] = hexagon

        # Ensure adjoining spaces are linked to each other as well
        for key_index in range(6):
            # Get 2 hexagons in sequence, circling the current hexagon
            first_key = Hexagon.adjoin_directions[key_index]
            second_key = Hexagon.adjoin_directions[(key_index + 1) % 6]
            first = hexagon.adjoins[first_key]
            second = hexagon.adjoins[second_key]
            # Get key modifiers in both circular directions
            cw_key = Hexagon.adjoin_loop[key_index]
            acw_key = tuple(map(operator.mul, cw_key, INVERSE_COORD))
            # Update the chips to link to each other
            first.adjoins[cw_key] = second
            second.adjoins[acw_key] = first

    def stack_on_chip(self, stacked_chip, covered_chip):
        if stacked_chip != covered_chip:
            # Set the grid position of the chip being stacked
            self.set_grid_pos(stacked_chip, covered_chip.selection_hexagon)
            # Not trying to stack a chip on itself
            covered_chip.stacked_chip = stacked_chip
            stacked_chip.covered_chip = covered_chip

    def axial_to_screen(self, (col, row)):
        """Return the center of the axial position as a screen position"""
        x = col * self.spacing[0] + self.orig[0]
        y = (row * self.spacing[1] + self.orig[1]) + (col * self.spacing[1] / 2)
        return (x, y)

    def screen_to_axial(self, (x, y)):
        """Find the nearest axial center (roughly) for the given screen position""" 
        col_f = (x - (self.orig[0] - self.spacing[0] / 2)) / self.spacing[0]
        row = round ( (y - (col_f * self.spacing[1] / 2) - self.orig[1]) / self.spacing[1] )
        col = round (col_f)
        return (int(col), int(row))

    def clicked_chip(self, mouse_pos):
        for chip in self.chips:
            if chip.is_mouse_on(mouse_pos):
                return chip.top_of_stack()

    def chip_at_hexagon(self, pos):
        hexagon = self.hexagons[pos]
        if not hexagon:
            return None
        for chip in self.chips:
            if chip.hexagon == hexagon:
                return chip
        return None

    @staticmethod
    def coords_in_surface((x, y), (width, height)):
        return x >= 0 and x <= width and y >= 0 and y <= height 

    def draw_hexagons(self):
        for hex in self.hexagons.keys():
            self.hexagons[hex].draw(self.screen)
            coord_str = "{}".format(hex)
            coord_text = self.font.render(coord_str, 0, LIGHT_GREY_2)
            font_mid = map(operator.div, self.font.size(coord_str), (2, 2))
            text_pos = tuple(map(operator.sub, self.hexagons[hex].center, font_mid))
            self.screen.blit(coord_text, text_pos)

    def draw_chips(self):
        # Sort chips from top of screen down before drawing
        draw_chips = {}
        for chip in self.chips:
            z_pos = 0
            while chip and chip.hexagon:
                # Sort by z, y then x
                draw_chips["{},{},{}".format(z_pos, chip.hexagon.center[1], chip.hexagon.center[0])] = chip
                # Move up a layer
                chip = chip.stacked_chip
                z_pos += 1
            
        # Draw chips in sorted order
        for chip_key in sorted(draw_chips.keys()):
            draw_chips[chip_key].draw(self.screen)

    def print_grid_debug(self):
        print "----------\nGrid debug\n=========="
        for hex in self.hexagons.keys():
            print str(self.hexagons[hex])

    def print_chip_debug(self):
        print "----------\nChip debug\n=========="
        for chip in self.chips:
            print str(chip)

    def draw_gui(self, mouse_hex):
        # Draw the "Add Chip" Icon
        self.add_chip.draw(self.screen)

        # Draw the selected chip, if one is selected
        if self.selected_chip:
            self.selected_chip.draw_outline(self.screen)

        # Draw hexagon outlines for mouse overs
        if self.hexagons.has_key(mouse_hex):
            chip = self.chip_at_hexagon(mouse_hex)
            if chip:
                chip.top_of_stack().draw_outline(self.screen, PINK, 10)
            else:
                self.hexagons[mouse_hex].draw(self.screen, PINK)

    def run(self):
        """Draw the screen with a hexagon grid"""

        # Create a mouse over event
        mouse_hex = None

        # Loop
        while not self.done:
            # Clear Events
            click = None
            selected = None

            # Events
            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == LEFT:
                        # Check if we're on the gui first
                        if self.add_chip.is_mouse_on(pos):
                            selected = self.add_chip
                        # Then check if we're on an existing chip
                        if not selected:
                            selected = self.clicked_chip(pos)
                        # Otherwise check the grid pos
                        if not selected:
                            click = self.screen_to_axial(pos)
                    if event.button == RIGHT:
                        if self.add_chip.is_mouse_on(pos):
                            self.print_grid_debug()
                            self.print_chip_debug()
                if event.type == pygame.MOUSEMOTION:
                    mouse_hex = self.screen_to_axial(pos)

            # Update
            if selected:
                # A chip has been click with the mouse
                if selected == self.add_chip:
                    # It was the "Add a chip" chip
                    self.get_new_chip()
                else:
                    # It was a game chip, check if we're selecting or moving
                    if self.selected_chip:
                        # Stack the selected chip onto this on
                        self.stack_on_chip(self.selected_chip, selected)
                        # Unselect the selected chip now
                        self.release_selected_chip()
                    else:
                        # Set the chip at the top of the selected stack to be the currently selected
                        self.selected_chip = selected.top_of_stack()
            if self.selected_chip and click and self.hexagons.has_key(click):
                self.set_grid_pos(self.selected_chip, self.hexagons[click])
                self.release_selected_chip()

            # Draw
            self.screen.fill(WHITE)
            self.draw_hexagons()
            self.draw_chips()
            self.draw_gui(mouse_hex)

            pygame.display.update()

        # Tear down
        pygame.quit()
        sys.exit()

drawer = PyHiveGame(SCREEN_SIZE, RADIUS)
drawer.run()