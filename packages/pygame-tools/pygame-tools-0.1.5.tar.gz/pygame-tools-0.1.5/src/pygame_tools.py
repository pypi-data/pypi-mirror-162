'''Basic classes for creating a pygame application'''

import pygame, math, sys
from string import printable as _printable
from typing import Type, TypeVar, Optional
from glob import glob
from pygame.locals import *
from recordclass import RecordClass

printable = _printable.strip() + ' '

T = TypeVar('T', bound='ManyOf')

class ManyOf:
    '''
    A class that can be used to group objects and call them at the same time
    reads methods from a given class and creates those methods in this class
    by looping over each provided object and calling that method on it
    '''
    def __init__(self, cls: Type[T], *obj_list: tuple[T]):
        '''
        initialize the ManyOf class
        :cls: the type or class of the objects in obj_list
        :obj_list: the list of objects that the methods will be called on
        '''
        if len(obj_list) < 1:
            raise ValueError('Must pass at least one object in obj_list')
        self.obj_list = obj_list
        for method in filter(lambda x: x != '__class__', dir(cls)):
            if not callable(getattr(cls, method)): # if the method is not a function
                continue # move on to the next method
            def func(*args, __method_name__=method, **kwargs): # create new function
                results = [getattr(obj, __method_name__)(*args, **kwargs) for obj in obj_list]
                return ManyOf(type(results[0]), *results)
            func.__name__ = method # rename function
            setattr(self, method, func) # save function as method

class TrueEvery:
    '''This is a functor that creates a function that returns true once every {self.count} calls'''

    def __init__(self, count: int, initial_count: int = None, once: bool = False, start_value: int = 0):
        '''
        :count: the number of times {self.__call__} must be called to return true once
        :initial_count: Optional. defaults to {self.count}. the number of times {self._call__} must be called to return True after the first call
        :once: Optional. defaults to False. the value
        :start_value: Optional. defaults to 0. the value that the offset starts at before the current call
        '''
        self.count = count
        self.initial_count = initial_count if initial_count != None else count
        self.once = once
        self.calls = self.start_value = start_value
        self.first_call = True

    def __call__(self) -> bool:
        '''
        Override () operator
        :returns: true once every {self.count} calls
            always returns true first time run unless start_value is set to something different
        '''
        # TODO: refactor this
        if not self.first_call and self.once:
            return False
        self.calls -= 1
        if self.calls <= 0:
            self.calls = self.initial_count if self.first_call else self.count
            self.first_call = False
            return True

    def reset(self, override_start_value: int = None):
        '''
        reset {self.calls}, and {self.first_call}
        :override_start_value: Optional. Defaults to self.start_value. set a new start value instead of the one in the constructor
        '''
        self.calls = override_start_value if override_start_value != None else self.start_value
        self.first_call = True

    def run_or_reset(self, boolean: bool) -> bool:
        '''
        :boolean: the boolean to be evaluated. If this boolean is True the {self.__call__} is called.
            If the boolean is False it calls {self.reset}
        :returns: a bool. It returns the result of call if {boolean} is True. or it returns False if {boolean} is False
        '''
        if boolean:
            return self()
        self.reset()
        return False

class Point: #forward declaration
    pass

class Point(RecordClass):
    x: int | float
    y: int | float

    def __neg__(self) -> Point:
        '''
        take the negative of a Point
        '''
        return Point(-self.x, -self.y)

    def __add__(self, other: int | float | Point) -> Point:
        '''add two points'''
        if isinstance(other, int | float):
            return Point(self.x + other, self.y + other)
        if not isinstance(other, Point):
            try:
                other = Point._make(other)
            except TypeError:
                return NotImplemented
        return Point(self.x + other.x, self.y + other.y)

    def __radd__(self, other: int | float | Point) -> Point:
        '''add two points'''
        return self + other

    def __sub__(self, other: int | float | Point) -> Point:
        '''subtract self from other'''
        if not isinstance(other, int | float) and not isinstance(other, Point):
            other = Point._make(other)
        return self + (-other)

    def __rsub__(self, other: int | float | Point) -> Point:
        '''subtract self from other'''
        return -self + other

    def __mul__(self, other: int | float | Point) -> Point:
        '''Multiply x and y by other'''
        if isinstance(other, int | float):
            return Point(self.x * other, self.y * other)
        if not isinstance(other, Point):
            try:
                other = Point._make(other)
            except TypeError:
                return NotImplemented
        return Point(self.x * other.x, self.y * other.y)

    def __rmul__(self, other: int | float | Point) -> Point:
        '''Multiply x and y by other'''
        return self * other

    def __truediv__(self, other: int | float | Point) -> Point:
        '''Divide x and y by other'''
        if isinstance(other, int | float):
            return Point(self.x / other, self.y / other)
        if not isinstance(other, Point):
            try:
                other = Point._make(other)
            except TypeError:
                return NotImplemented
        return Point(self.x / other.x, self.y / other.y)

    def __rtruediv__(self, other: int | float | Point) -> Point:
        '''Divide other by x and y'''
        if isinstance(other, int | float):
            return Point(other / self.x , other / self.y)
        if not isinstance(other, Point):
            try:
                other = Point._make(other)
            except TypeError:
                return NotImplemented
        return Point(other.x / self.x, other.y / self.y)

    def __floordiv__(self, other: int | float | Point) -> Point:
        '''Divide x and y by other and round down'''
        if isinstance(other, int | float):
            return Point(self.x // other, self.y // other)
        if not isinstance(other, Point):
            try:
                other = Point._make(other)
            except TypeError:
                return NotImplemented
        return Point(self.x // other.x, self.y // other.y)

    def __rfloordiv__(self, other: int | float | Point) -> Point:
        '''Divide other by x and y and round down'''
        if isinstance(other, int | float):
            return Point(other // self.x , other // self.y)
        if not isinstance(other, Point):
            try:
                other = Point._make(other)
            except TypeError:
                return NotImplemented
        return Point(other.x // self.x, other.y // self.y)

    def __floor__(self) -> Point:
        '''round down on x and y'''
        return Point(math.floor(self.x), math.floor(self.y))

    def __ceil__(self) -> Point:
        '''round up on x and y'''
        return Point(math.ceil(self.x), math.ceil(self.y))

    def __eq__(self, pos: Point) -> bool:
        '''check if two poits are equal'''
        if not isinstance(pos, Point):
            try:
                pos = Point._make(pos)
            except TypeError:
                return NotImplemented
        return self.x == pos.x and self.y == pos.y

    def __abs__(self) -> Point:
        '''Returns the a Point with absolute value on x and y'''
        return Point(abs(self.x), abs(self.y))

    def rotate(self, angle: float, center: Optional[Point] = None) -> Point:
        '''
        rotates a point clockwise around center
        :angle: angle which to rotate, radians
        :center: the point to rotate around
        '''
        if center is None:
            center = Point(0, 0)
        elif not isinstance(center, Point):
            center = Point._make(center)
        pos = self - center
        return center + Point(
            pos.x * math.cos(angle) - pos.y * math.sin(angle),
            pos.y * math.cos(angle) + pos.x * math.sin(angle)
        )
    rotate_cw = rotate

    def rotate_ccw(self, angle: float, center: Optional[Point] = None) -> Point:
        '''
        rotates a point counter-clockwise around center
        :angle: angle which to rotate, radians
        :center: the point to rotate around
        '''
        return self.rotate(-angle, center)

    def dist(self, pos: Point) -> float:
        '''
        calculate distance between self and pos
        :pos: position to calculate distance from
        '''
        return Point.distance(self, pos)

    def dist_from_line(self, start: Point, end: Point) -> float:
        '''
        returns distance between self and line
        :start: the start of the line
        :end: the end of the line
        :returns: the distance between the line and self
        '''
        return Point.distance_from_line(start, end, self)

    @staticmethod
    def distance(pos1: Point, pos2: Point) -> float:
        '''
        takes two points and returns the distance between then
        static method
        :pos1: first point
        :pos2: second point
        :returns: distance between pos1 and pos2
        '''
        if not isinstance(pos1, Point):
            pos1 = Point._make(pos1)
        if not isinstance(pos2, Point):
            pos2 = Point._make(pos2)
        return math.sqrt((pos2.x - pos1.x) ** 2 + (pos2.y - pos1.y) ** 2)

    @staticmethod
    def distance_from_line(start: Point, end: Point, point: Point) -> float:
        '''
        measure the distance between a point and a line
        used https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line as a reference
        static method
        :start: the start of the line
        :end: the end of the line
        :point: the point to measure
        :returns: the distance between the line and the point
        '''
        if not isinstance(start, Point):
            start = Point._make(start)
        if not isinstance(end, Point):
            end = Point._make(end)
        if not isinstance(point, Point):
            point = Point._make(point)
        try:
            return abs((end.x - start.x) * (start.y - point.y) - (start.x - point.x) * (end.y - start.y)) / math.sqrt((end.x - start.x) ** 2 + (end.y - start.y) ** 2)
        except ZeroDivisionError:
            return Point.distance(start, point)

def clip_surface(surface: pygame.Surface, rect: Rect) -> pygame.Surface:
    '''Copy part of a pygame.Surface'''
    cropped = pygame.Surface(rect.size)
    cropped.blit(surface, (0, 0), rect)
    return cropped

def get_bezier_curve_points(p0: Point, p1: Point, p2: Point, density: int) -> list[Point]:
    '''
    calculates the points for a quadratic bezier curve
    :p0: the first point in the bezier curve
    :p1: the point in the curves direction
    :p2: the last point in the bezier curve
    :density: number of Points in the returned list
    :returns: a list of points for the bezier curve
    '''
    if not isinstance(p0, Point):
        p0 = Point._make(p0)
    if not isinstance(p1, Point):
        p1 = Point._make(p1)
    if not isinstance(p2, Point):
        p2 = Point._make(p2)
    result = []
    for i in range(density+1):
        t = i / density
        result.append(Point(
            (1 - t) ** 2 * p0.x + 2 * (1 - t) * t * p1.x + t ** 2 * p2.x,
            (1 - t) ** 2 * p0.y + 2 * (1 - t) * t * p1.y + t ** 2 * p2.y
            ))
    return result

class Animation:
    '''
    Represents a object that has multiple frames each with diffrent length
    :example:

        # assets/animations has files 0.png, 1.png, 2.png, and 3.png
        a = Animation('assets/animations/*', [30, 7, 7, 7]) # create animation
        class Example(GameScreen):
            def __init__(self):
                pygame.init()
                size = Point(300, 300)
                real_size = size * 2
                screen = pygame.display.set_mode(real_size)
                super().__init__(screen, real_size, size)

            def update(self):
                super().update()
                self.screen.blit(a.get_surface(), (self.window_size.x / 2, self.window_size.y / 2))
                a.update()

        Example().run()
    '''
    def __init__(self, glob_path: str, frame_data: [int], repititions: int = None):
        '''
        :glob_path: the path that glob is called on.
            e.g.: 'assets/animations/*' to get every file in assets/animations
        :frame_data: how long a frame of the animation should be displayed in game frames
            e.g.: [7, 8, 9] first image found in glob_path lasts 7, the next lasts 8, and the third lasts 9
            this must be the same length as the number of items from glob_path
        :repititions: Optional. defaults to None. if repititions is none, it repeats forever.
            if this number is an int, it decrements every time update is called until it is zero
        '''
        self.glob_path = glob_path
        self.frame_data = frame_data
        self.repititions = repititions
        self.finished = True if self.repititions == 0 else False
        self.load(glob_path, frame_data)

    def update(self):
        '''
        Indicate a frame has passed
        '''
        if not self.finished:
            self.frames_until_next -= 1
            if self.frames_until_next == 0:
                self.frame_index = (self.frame_index + 1) % self.frame_count
                self.frames_until_next += self.frames[self.frame_index][1]
                if self.frame_index == 0 and self.repititions != None:
                    self.repititions -= 1
                    if self.repititions == 0:
                        self.finished = True

    def get_surface(self) -> pygame.Surface:
        '''return the frame of the current index'''
        return self.frames[self.frame_index][0]

    def reset(self):
        '''Restart the animation to the start of the loop'''
        self.frame_index = 0
        self.frames_until_next = self.frames[0][1]

    def load(self, glob_path: str, frame_data):
        '''
        Load animations from a glob path
        :glob_path: the path that glob is called on.
            e.g.: 'assets/animations/*' to get every file in assets/animations
        :frame_data: how long a frame of the animation should be displayed in game frames
            e.g.: [7, 8, 9] first image found in glob_path lasts 7, the next lasts 8, and the third lasts 9
            this must be the same length as the number of items from glob_path
        '''
        file_names = glob(glob_path)
        if len(file_names) != len(frame_data):
            raise ValueError('Length of frame_data and the number of files must be the same')
        self.frames = [(pygame.image.load(file_name), frame_data[i]) for i, file_name in enumerate(file_names)]
        self.frame_count = len(self.frames)
        self.frame_index = 0
        self.frames_until_next = self.frames[0][1]

class Circle:

    def __init__(self, center: Point, radius: int, color: Color, width: int = 0):
        self._center = Point._make(center)
        self._radius = radius
        self.diameter = radius * 2
        self.color = color
        self.width = width
        self.rect = Rect(0, 0, self.diameter, self.diameter)
        self.rect.center = self.center

    @property
    def radius(self) -> int:
        return self._radius

    @radius.setter
    def radius(self, radius: int):
        self._radius = radius
        self.diameter = radius * 2
        self.rect.w = self.diameter
        self.rect.h = self.diameter
        self.rect.center = self.center

    @property
    def center(self) -> Point:
        return self._center

    @center.setter
    def center(self, center: Point):
        self._center = center
        if not isinstance(self._center, Point):
            self._center = Point._make(self._center)
        self.rect.center = self.center

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.color, self.rect, self.width, self.radius)

    def collide_point(self, point: Point, only_border: bool = False) -> bool:
        if not isinstance(point, Point):
            point = Point._make(point)
        dist = int(Point.distance(self.center, point))
        return only_border and dist <= self.radius and dist >= self.radius - self.width + 1 or (not only_border and dist <= self.radius)

class Particle(Circle):

    def __init__(self, center: Point, radius: int, color: Color, velocity: Point, lifetime: int = None, radius_decrement: int = None, frames_between_decrement: int = 1):
        super().__init__(center, radius, color)
        self.velocity = velocity
        if not isinstance(self.velocity, Point):
            self.velocity = Point._make(self.velocity)
        self.lifetime = lifetime
        self.radius_decrement = radius_decrement
        self.radius_decrement_timer = TrueEvery(frames_between_decrement)
        self.alive = True

    def update(self):
        if self.alive:
            self.center = self.center.x + self.velocity.x, self.center.y + self.velocity.y
            if self.lifetime != None:
                self.lifetime -= 1
                if self.lifetime <= 0:
                    self.alive = False
            if self.radius_decrement != None and self.radius_decrement_timer():
                self.radius -= self.radius_decrement
                if self.radius <= 0:
                    self.alive = False

class Button:
    '''A button in a pygame application'''

    def __init__(
            self,
            action: callable,
            text: str,
            rect: Rect,
            font: pygame.font.Font,
            rect_color: Color = (255, 255, 255),
            highlight_color: Color = (150, 150, 150),
            font_color: Color = (0, 0, 0),
            rect_line_width: int = 0,
            border_radius: int = 0,
            border_size: int = 0,
            border_color: Color = (0, 0, 0),
            clicked_color: Color = (100, 100, 100)
            ):
        self.action = action
        self.text = text
        self.rect = rect if isinstance(rect, Rect) else Rect(rect)
        self.font = font
        self.rect_color = rect_color
        self.font_color = font_color
        self.highlight_color = highlight_color if highlight_color else rect_color
        self.rect_line_width = rect_line_width
        self.border_radius = border_radius
        self.border_size = border_size
        self.border_color = border_color
        self.clicked_color = clicked_color
        self.clicked = False
        self.highlight = False

    def draw(self, screen: pygame.Surface, override_highlight: bool = None):
        pygame.draw.rect(screen, self.clicked_color if self.clicked else self.highlight_color if (override_highlight == None and self.highlight) or override_highlight else self.rect_color, self.rect, self.rect_line_width, self.border_radius)
        self.clicked = False
        if self.border_size > 0:
            pygame.draw.rect(screen, self.border_color, self.rect, self.border_size, self.border_radius)
        text_obj = self.font.render(self.text, True, self.font_color)
        text_size = text_obj.get_size()
        screen.blit(text_obj, (self.rect.centerx - text_size[0] / 2, self.rect.centery - text_size[1] / 2))

    def __call__(self):
        '''Overwrite the () operator on the button object'''
        if self.action:
            self.action()
        self.clicked = True

class ToggleButton:
    '''When clickd this button will change its color, text, and also call target'''

    def __init__(
            self,
            action: callable,
            on_text: str,
            off_text: str,
            rect: Rect,
            font: pygame.font.Font,
            on_rect_color: Color = (255, 255, 255),
            off_rect_color: Color = None,
            on_highlight_color: Color = (150, 150, 150),
            off_highlight_color: Color = (150, 150, 150),
            on_font_color: Color = (0, 0, 0),
            off_font_color: Color = (0, 0, 0),
            rect_line_width: int = 0,
            border_radius: int = 0,
            border_size: int = 0,
            on_border_color: Color = (0, 0, 0),
            off_border_color: Color = None,
            toggled: bool = False,
            ):
        self.action = action
        self.on_text = on_text
        self.off_text = off_text
        self.rect = rect
        self.font = font
        self.on_rect_color = on_rect_color
        self.off_rect_color = off_rect_color if off_rect_color else on_rect_color
        self.on_highlight_color = on_highlight_color
        self.off_highlight_color = off_highlight_color
        self.on_font_color = on_font_color
        self.off_font_color = off_font_color
        self.rect_line_width = rect_line_width
        self.border_radius = border_radius
        self.border_size = border_size
        self.on_border_color = on_border_color
        self.off_border_color = off_border_color if off_border_color else on_border_color
        self.highlight = False
        self.toggled = toggled

    def draw(self, screen: pygame.Surface, override_highlight: bool = None):
        if self.toggled:
            pygame.draw.rect(screen, self.on_highlight_color if (override_highlight == None and self.highlight) or override_highlight else self.on_rect_color, self.rect, self.rect_line_width, self.border_radius)
            if self.border_size > 0:
                pygame.draw.rect(screen, self.on_border_color, self.rect, self.border_size, self.border_radius)
            text_obj = self.font.render(self.on_text, True, self.on_font_color)
            text_size = text_obj.get_size()
            screen.blit(text_obj, (self.rect.centerx - text_size[0] / 2, self.rect.centery - text_size[1] / 2))
        else:
            pygame.draw.rect(screen, self.off_highlight_color if (override_highlight == None and self.highlight) or override_highlight else self.off_rect_color, self.rect, self.rect_line_width, self.border_radius)
            if self.border_size > 0:
                pygame.draw.rect(screen, self.off_border_color, self.rect, self.border_size, self.border_radius)
            text_obj = self.font.render(self.off_text, True, self.off_font_color)
            text_size = text_obj.get_size()
            screen.blit(text_obj, (self.rect.centerx - text_size[0] / 2, self.rect.centery - text_size[1] / 2))

    def __call__(self):
        '''override the ()'''
        if self.action:
            self.action()
        self.toggled = not self.toggled

class GameScreen:
    '''
    A class to reperesent a screen inside a pygame application
    e.g.: menu, pause screen, or main screen
    to use this class, inherit it and overwrite some/all of its functions
    :example:

        class Example(GameScreen):
            def __init__(self):
                pygame.init()
                real_size = Point(600, 600) # size of window itself
                size = real_size / 40 # 1 pixel for every 40
                super().__init__(pygame.display.set_mode(real_size), real_size, size)

            def update(self):
                pygame.draw.line(self.screen, (255, 255, 255), (0, self.window_size.y / 2), (self.window_size.x, self.window_size.y / 2))

        example = Example()
        example.run()
    '''

    def __init__(self, screen: pygame.Surface, real_window_size: Point, window_size: Point = None, frame_rate: int = 30):
        '''
        :screen: The pygame surface that will be drawn onto
        :real_window_size: The height and width of the screen in real computer pixels
        :window_size: The height and width of the screen in game pixels pixels
            if this is smaller than real_window_size the pixels become larger
            if this is larger than real_window_size the pixels become smaller
        :frame_rate: The desired frame rate of the current screen
        '''
        self.window_scaled = bool(window_size) and window_size != real_window_size
        self.real_screen = screen
        self.screen = screen if not self.window_scaled else pygame.Surface(window_size)
        self.real_window_size = Point._make(real_window_size)
        self.window_size = Point._make(window_size if self.window_scaled else real_window_size)
        self.window_scale = self.real_window_size // self.window_size
        self.frame_rate = frame_rate
        self.running = False
        self.rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.game_ticks = 0

    def get_scaled_mouse_pos(self) -> Point:
        pos = pygame.mouse.get_pos()
        return pos // self.window_scale

    def tick(self):
        self.clock.tick(self.frame_rate)
        self.game_ticks += 1
        if self.game_ticks > 999999999999999999999:
            self.game_ticks = 0

    def key_down(self, event: pygame.event.Event):
        '''Function called when a pygame KEYDOWN event is triggered'''

    def key_up(self, event: pygame.event.Event):
        '''Function called when a pygame KEYUP event is triggered'''

    def mouse_button_down(self, event: pygame.event.Event):
        '''Function called when a pygame MOUSEBUTTONDOWN event is triggered'''

    def mouse_button_up(self, event: pygame.event.Event):
        '''Function called when a pygame key_down MOUSEBUTTONDOWN is triggered'''

    def handle_event(self, event: pygame.event.Event):
        '''Handle a pygame events'''
        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            self.key_down(event)
        elif event.type == KEYUP:
            self.key_up(event)
        elif event.type == MOUSEBUTTONDOWN:
            self.mouse_button_down(event)
        elif event.type == MOUSEBUTTONUP:
            self.mouse_button_up(event)

    def update(self):
        '''Run every frame, meant for drawing and update logic'''
        self.screen.fill((0, 0, 100))

    def run(self):
        '''Run the main loop'''
        self.running = True
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            if self.window_scaled:
                self.real_screen.blit(pygame.transform.scale(self.screen, self.real_window_size), (0, 0))
            pygame.display.update()
            self.tick()

class MenuScreen(GameScreen):
    '''
    A class to represent a menu screen inside a pygame application
    e.g.: Main menu, Pause menu, Options
    '''

    def __init__(self, screen: pygame.Surface, real_window_size: Point, window_size: Point = None, frame_rate: int = 30):
        super().__init__(screen, real_window_size, window_size, frame_rate)
        self.buttons = []
        self.button_index = 0

    def key_down(self, event: pygame.event.Event):
        if len(self.buttons) < 1:
            return
        if event.key == K_UP or event.key == K_RIGHT or event.key == K_DOWN or event.key == K_LEFT:
            if event.key == K_DOWN or event.key == K_RIGHT:
                self.button_index += 1
                buttons_length = len(self.buttons)
                if self.button_index >= buttons_length:
                    self.button_index %= buttons_length
            else:
                self.button_index -= 1
                if self.button_index < 0:
                    self.button_index = len(self.buttons) - 1
        elif event.key == K_RETURN or event.key == K_SPACE:
            self.buttons[self.button_index]()

    def draw_buttons(self, screen: pygame.Surface = None, highlight: bool = True):
        '''Draw the buttons'''
        if not screen:
            screen = self.screen
        for i, button in enumerate(self.buttons):
            button.draw(screen, True if i == self.button_index and highlight else None)

    def update(self):
        self.draw_buttons()

    def mouse_button_down(self, event: pygame.event.Event):
        if event.button == 1:
            if self.window_scaled:
                mouse_pos = self.get_scaled_mouse_pos()
            else:
                mouse_pos = Point._make(pygame.mouse.get_pos())
            for i, button in enumerate(self.buttons):
                if button.rect.collidepoint(mouse_pos):
                    self.button_index = i
                    button()

class TextBox:
    '''
    A text box that displays text for the user
    ... in a box
    '''
    def __init__(
            self,
            text: list[str],
            rect: pygame.Rect,
            bg_color: pygame.Color = 'grey',
            text_color: pygame.Color = 'black',
            border_radius: int = 10,
            padding: Point = None,
            font: pygame.font.Font = None,
            center_text: bool = False
        ):
        self.text = text
        self.rect = rect
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.padding = padding if padding is not None else Point(10, 10)
        self.font = font if font is not None else pygame.font.SysFont(pygame.font.get_default_font(), 20)
        self.center_text = center_text
        self.text_arr_size = len(self.text)
        self.text_index = 0
        self.done = False
        self.font_height = self.font.size('Tg')[1]
        self.center = Point(
            self.rect.x + self.padding.x + (self.rect.w - self.padding.x * 2) / 2,
            self.rect.y + self.padding.y + (self.rect.h - self.padding.y * 2) / 2
        )

    def draw(self, screen: pygame.Surface):
        '''
        draw the text box to the screen
        :screen: the screen to draw to
        '''
        if self.done:
            return
        pygame.draw.rect(screen, self.bg_color, self.rect, 0, self.border_radius)
        self.draw_text(screen)

    def draw_text(self, screen: pygame.Surface):
        '''
        draw text with wrapping
        https://www.pygame.org/wiki/TextWrap
        above link heavily referenced
        :screen: the screen to draw to
        '''
        y = 0
        text = self.text[self.text_index]
        while text:
            text_len = len(text)
            i = 1
            while self.font.size(text[:i])[0] < self.rect.w - self.padding.x * 2 and i < text_len and text[i] != '\n':
                i += 1
            if i < text_len and text[i] != '\n':
                new_i = text.rfind(' ', 0, i) + 1 # attempt to find the farthest space
                if new_i: # space is found
                    i = new_i # use found index for word wrapping
            elif i < text_len and text[i] == '\n':
                text = text.replace('\n', '', 1)
            size = Point(*self.font.size(text[:i]))
            screen.blit(
                self.font.render(text[:i], True, self.text_color),
                (
                    self.center.x - size.x // 2 if self.center_text else self.rect.x + self.padding.x,
                    self.rect.y + self.padding.y + y
                )
            )
            text = text[i:]
            y += self.font_height

    def update(self):
        '''
        increment the text index to move to the second slide
        '''
        self.text_index += 1
        if self.text_index >= self.text_arr_size:
            self.done = True

class InputBox(TextBox):
    '''
    A TextBox that updates with input taken
    '''
    def __init__(
            self,
            rect: pygame.Rect,
            bg_color: pygame.Color = 'grey',
            text_color: pygame.Color = 'black',
            border_radius: int = 10,
            padding: Point = None,
            font: pygame.font.Font = None,
            center_text: bool = False,
        ):
        super().__init__(
            [''],
            rect,
            bg_color,
            text_color,
            border_radius,
            padding,
            font,
            center_text,
        )

    def update(self, event: pygame.event.Event):
        '''
        this will update the text with an appropriately depending on the key pressed
        :event: the KEYDOWN event to be evaluated
        '''
        if event.type != KEYDOWN:
            return
        match event.unicode.lower():
            case '\x1b': # escape
                self.reset()
            case '\r': # enter
                self.done = True
            case '\x08': # backspace
                self.text[0] = self.text[0][:-1]
            case key if key in printable:
                self.text[0] += event.unicode

    def reset(self):
        '''
        reset the text to be blank again
        '''
        self.done = False
        self.text[0] = ''
        self.text_index = 0

    def get_value(self) -> str:
        '''
        get the value of the text entered
        :returns: the text entered
        '''
        return self.text[0]
