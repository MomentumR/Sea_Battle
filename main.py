from random import randint

class Cell:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __eq__(self, another):
		return self.x == another.x and self.y == another.y

	def __repr__(self):
		return f'({self.x}, {self.y})'


class BoardException(Exception):
	pass

class BoardOutException(BoardException):
	def __str__(self):
		return 'Вы выстрелили за пределв доски!'

class BoardUsedException(BoardException):
	def __str__(self):
		return 'Вы уже стреляли в эту клетку'

class BoardWrongShipException(BoardException):
	pass


class Warship:
	def __init__(self, bow, l, o):
		self.bow = bow
		self.l = l
		self.o = o
		self.conditions = l

	@property
	def cells(self):
		ship_cells = []
		for i in range(self.l):
			cur_x = self.bow.x
			cur_y = self.bow.y

			if self.o == 0:
				cur_x += i

			elif self.o == 1:
				cur_y += i
			ship_cells.append(Cell(cur_x, cur_y))
		return ship_cells

	def fire(self, shot):
		return shot in self.cells


class Place:
	def __init__(self, hid = False, size = 6):
		self.size = size
		self.hid = hid

		self.count = 0

		self.field = [ ["O"]*size for _ in range(size) ]

		self.busy = []
		self.ships = []

	def circuit(self, ship, verb = False):
		near = [
			(-1, -1), (-1, 0), (-1, 1),
			(0, -1), (0, 0), (0, 1),
			(1, -1), (1, 0), (1, 1)
		]
		for d in ship.cells:
			for dx, dy in near:
				cur = Cell(d.x + dx, d.y + dy)
				if not(self.overboard(cur)) and cur not in self.busy:
					if verb:
						self.field[cur.x][cur.y] = "."
					self.busy.append(cur)

	def add_warship(self, ship):
		for d in ship.cells:
			if self.overboard(d) or d in self.busy:
				raise BoardWrongShipException()
		for d in ship.cells:
			self.field[d.x][d.y] = "■"
			self.busy.append(d)

		self.ships.append(ship)
		self.circuit(ship)


	def __str__(self):
		res = ''
		res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
		for i, row in enumerate(self.field):
			res += f"\n{i+1} | " + " | ".join(row) + " |"

		if self.hid:
			res = res.replace("■", "O")
		return res

	def overboard(self, d):
		return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

	def shot(self, d):
		if self.overboard(d):
			raise BoardOutException()

		if d in self.busy:
			raise BoardUsedException()

		self.busy.append(d)

		for ship in self.ships:
			if d in ship.cells:
				ship.conditions -= 1
				self.field[d.x][d.y] = "X"
				if ship.conditions == 0:
					self.count += 1
					self.circuit(ship, verb=True)
					print("Корабль подбит!")
					return False
				else:
					print("Корабль поврежден!")
					return True
		self.field[d.x][d.y] = "."
		print("Не попал!")
		return False

	def initially(self):
		self.busy = []

class Player:
	def __init__(self, board, enemy):
		self.board = board
		self.enemy = enemy

	def ask(self):
		raise NotImplementedError()

	def move(self):
		while True:
			try:
				target = self.ask()
				repeat = self.enemy.shot(target)
				return repeat
			except BoardException as e:
				print(e)

class Comp(Player):
	def ask(self):
		d = Cell(randint(0, 5), randint(0, 5))
		print(f"Ход компьютера: {d.x+1} {d.y+1}")
		return d

class Human(Player):
	def ask(self):
		while True:
			cords = input("Ваш ход: ").split()
			if len(cords) != 2:
				print("Введите 2 координаты!")
				continue

			x, y = cords

			if not(x.isdigit()) or not(y.isdigit()):
				print("Введите числа!")
				continue

			x, y = int(x), int(y)

			return Cell(x - 1, y - 1)

class Game:
	def __init__(self, size = 6):
		self.size = size
		pl = self.random_locate()
		co = self.random_locate()
		co.hid = True

		self.ai = Comp(co, pl)
		self.us = Human(pl, co)

	def locate_warship(self):
		lens = [3, 2, 2, 1, 1, 1, 1]
		board = Place(size = self.size)
		attempts = 0
		for l in lens:
			while True:
				attempts += 1
				if attempts > 2000:
					return None
				ship = Warship(Cell(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
				try:
					board.add_warship(ship)
					break
				except BoardWrongShipException:
					pass
		board.initially()
		return board

	def random_locate(self):
		board = None
		while board is None:
			board = self.locate_warship()
		return board

	def welcome(self):
		print("-------------------")
		print("  Привествуем Вас  ")
		print("      в игре       ")
		print("    морской бой    ")
		print("-------------------")
		print(" формат вводаЖ x y ")
		print(" x - номер строки  ")
		print(" y - номер столбца ")

	def play_moves(self):
		num = 0
		while True:
			print("-"*20)
			print("Доска пользователя:")
			print(self.us.board)
			print("-" * 20)
			print("Доска компьютера:")
			print(self.ai.board)
			print("-" * 20)
			if num % 2 == 0:
				print("Ходит пользователь!")
				repeat = self.us.move()
			else:
				print("Ходит компьютер!")
				repeat = self.ai.move()
			if repeat:
				num -= 1

			if self.ai.board.count == 7:
				print("-" * 20)
				print("Пользователь выиграл!")
				break

			if self.us.board.count == 7:
				print("-" * 20)
				print("Компьютер выиграл!")
				break
			num += 1

	def start(self):
		self.welcome()
		self.play_moves()

g = Game()
g.start()
