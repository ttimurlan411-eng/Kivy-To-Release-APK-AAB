from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
import random

class Cell(Button):
    def __init__(self, row, col, **kwargs):
        super().__init__(**kwargs)
        self.row = row
        self.col = col
        self.is_mine = False
        self.adjacent = 0
        self.revealed = False
        self.flagged = False
        self.background_normal = 'atlas://data/images/defaulttheme/button'
        self.background_down = 'atlas://data/images/defaulttheme/button_pressed'

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.button == 'right':
            return True
        return super().on_touch_down(touch)

class MinesweeperGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.rows = 9
        self.cols = 9
        self.total_mines = 10
        self.first_click = True
        self.game_over = False
        self.flags_count = 0
        self.revealed_count = 0
        self.cells = []
        self.mine_positions = set()
        self.timer = 0
        self.timer_event = None

        # Үстүнкү панель
        top = BoxLayout(size_hint=(1, 0.1), spacing=10, padding=10)
        self.mine_display = Label(text=f"Mines: {self.total_mines}", font_size=20)
        self.face_btn = Button(text="😊", font_size=20, size_hint=(0.2, 1))
        self.face_btn.bind(on_press=self.reset_game)
        self.time_display = Label(text="Time: 0", font_size=20)
        top.add_widget(self.mine_display)
        top.add_widget(self.face_btn)
        top.add_widget(self.time_display)
        self.add_widget(top)

        # Оюн тактасы
        self.board = GridLayout(cols=self.cols, spacing=1, size_hint=(1, 0.9))
        self.add_widget(self.board)

        self.reset_game()

    def reset_game(self, *args):
        self.game_over = False
        self.first_click = True
        self.flags_count = 0
        self.revealed_count = 0
        self.mine_positions.clear()
        self.timer = 0
        if self.timer_event:
            self.timer_event.cancel()
        self.time_display.text = "Time: 0"
        self.mine_display.text = f"Mines: {self.total_mines}"
        self.face_btn.text = "😊"

        self.board.clear_widgets()
        self.cells = []
        for row in range(self.rows):
            for col in range(self.cols):
                cell = Cell(row, col)
                cell.bind(on_press=self.on_left_click)
                cell.bind(on_touch_down=self.on_right_click)
                self.board.add_widget(cell)
                self.cells.append(cell)

    def on_right_click(self, cell, touch):
        if touch.button == 'right' and not self.game_over and not cell.revealed:
            if not cell.flagged:
                cell.flagged = True
                cell.text = "🚩"
                self.flags_count += 1
            else:
                cell.flagged = False
                cell.text = ""
                self.flags_count -= 1
            self.mine_display.text = f"Mines: {self.total_mines - self.flags_count}"
            return True
        return False

    def on_left_click(self, cell):
        if self.game_over or cell.revealed or cell.flagged:
            return

        if self.first_click:
            self.first_click = False
            self._place_mines(cell.row, cell.col)
            self._calc_adjacent()
            self.timer_event = Clock.schedule_interval(self.update_timer, 1)

        if cell.is_mine:
            self._reveal_mines(cell)
            self.game_over = True
            self.face_btn.text = "💀"
            if self.timer_event:
                self.timer_event.cancel()
            return

        self._reveal_cell(cell.row, cell.col)

        if self.revealed_count == self.rows * self.cols - self.total_mines:
            self._win_game()

    def update_timer(self, dt):
        if not self.game_over:
            self.timer += 1
            self.time_display.text = f"Time: {self.timer}"

    def _place_mines(self, first_row, first_col):
        safe = {(first_row, first_col)}
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                r, c = first_row+dr, first_col+dc
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    safe.add((r,c))
        all_pos = [(r,c) for r in range(self.rows) for c in range(self.cols) if (r,c) not in safe]
        self.mine_positions = set(random.sample(all_pos, self.total_mines))
        for cell in self.cells:
            if (cell.row, cell.col) in self.mine_positions:
                cell.is_mine = True

    def _calc_adjacent(self):
        for cell in self.cells:
            if cell.is_mine:
                continue
            cnt = 0
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr == 0 and dc == 0: continue
                    r, c = cell.row+dr, cell.col+dc
                    if 0 <= r < self.rows and 0 <= c < self.cols:
                        neighbor = self.cells[r*self.cols + c]
                        if neighbor.is_mine:
                            cnt += 1
            cell.adjacent = cnt

    def _reveal_cell(self, row, col):
        cell = self.cells[row*self.cols + col]
        if cell.revealed or cell.flagged or cell.is_mine:
            return
        cell.revealed = True
        self.revealed_count += 1
        cell.background_normal = ''
        if cell.adjacent > 0:
            cell.text = str(cell.adjacent)
            colors = {1: (0,0,1,1), 2: (0,0.5,0,1), 3: (1,0,0,1),
                      4: (0,0,0.5,1), 5: (0.5,0,0,1), 6: (0,0.5,0.5,1),
                      7: (0,0,0,1), 8: (0.5,0.5,0.5,1)}
            cell.color = colors.get(cell.adjacent, (0,0,0,1))
        else:
            cell.text = ""
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr == 0 and dc == 0: continue
                    r, c = row+dr, col+dc
                    if 0 <= r < self.rows and 0 <= c < self.cols:
                        self._reveal_cell(r, c)

    def _reveal_mines(self, clicked_cell):
        for cell in self.cells:
            if cell.is_mine:
                cell.revealed = True
                cell.background_normal = ''
                cell.text = "💣"
                if (cell.row, cell.col) == (clicked_cell.row, clicked_cell.col):
                    cell.background_color = (1, 0, 0, 1)
            elif cell.flagged and not cell.is_mine:
                cell.text = "❌"
                cell.background_normal = ''

    def _win_game(self):
        self.game_over = True
        self.face_btn.text = "😎"
        if self.timer_event:
            self.timer_event.cancel()
        for cell in self.cells:
            if cell.is_mine and not cell.flagged:
                cell.text = "🚩"
                cell.flagged = True
        self.mine_display.text = "Mines: 0"

class MinesweeperApp(App):
    def build(self):
        return MinesweeperGame()

if __name__ == '__main__':
    MinesweeperApp().run()