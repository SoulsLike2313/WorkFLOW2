import turtle

# Настройка экрана
screen = turtle.Screen()
screen.setup(width=800, height=600)
screen.bgcolor("#FFF0F5")  # Нежно-розовый фон (LavenderBlush)
screen.title("С 8 Марта!")

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)  # Максимальная скорость отрисовки (0)

def draw_petal(t, radius, angle):
    """Рисует один лепесток"""
    for _ in range(2):
        t.circle(radius, angle)
        t.left(180 - angle)

def draw_flower(x, y, petal_color, center_color):
    """Рисует цветок из 8 лепестков с центром"""
    pen.penup()
    pen.goto(x, y)
    pen.setheading(0)
    pen.pendown()

    # Рисуем лепестки
    pen.color(petal_color)
    for _ in range(8):
        pen.begin_fill()
        draw_petal(pen, 30, 60)
        pen.end_fill()
        pen.left(45)

    # Рисуем желтый центр цветка
    pen.penup()
    pen.goto(x, y - 8)
    pen.pendown()
    pen.color(center_color)
    pen.begin_fill()
    pen.circle(8)
    pen.end_fill()

# 1. Рисуем красивую цифру 8
pen.penup()
pen.goto(0, -30)
pen.pendown()
pen.color("#FF1493")  # Ярко-розовый цвет (DeepPink)
pen.pensize(12)

# Нижний круг восьмерки
pen.circle(70)

# Верхний круг восьмерки
pen.penup()
pen.goto(0, 110)
pen.pendown()
pen.circle(50)

# 2. Добавляем цветы вокруг восьмерки
flowers_data = [
    (-70, 40, "#FF69B4", "#FFD700"),   # Слева по центру
    (70, 40, "#FF69B4", "#FFD700"),    # Справа по центру
    (-45, 150, "#DA70D6", "#FFD700"),  # Слева сверху
    (45, 150, "#DA70D6", "#FFD700"),   # Справа сверху
    (0, 210, "#FF1493", "#FFD700"),    # На самой верхушке
    (0, -30, "#FF1493", "#FFD700")     # В самом низу
]

pen.pensize(2)
for fx, fy, p_color, c_color in flowers_data:
    draw_flower(fx, fy, p_color, c_color)

# 3. Добавляем пару зеленых листиков для живости
pen.color("#32CD32")  # Зеленый (LimeGreen)
pen.penup()
pen.goto(-80, 0)
pen.setheading(200)
pen.pendown()
pen.begin_fill()
draw_petal(pen, 40, 60)
pen.end_fill()

pen.penup()
pen.goto(80, 0)
pen.setheading(-20)
pen.pendown()
pen.begin_fill()
draw_petal(pen, 40, 60)
pen.end_fill()

# 4. Пишем поздравительный текст
pen.penup()
pen.goto(0, -140)
pen.color("#C71585")  # Темно-розовый
pen.write("С 8 Марта!", align="center", font=("Arial", 46, "bold"))

pen.goto(0, -180)
pen.color("#FF69B4")
pen.write("Пусть в душе всегда цветет весна!", align="center", font=("Arial", 22, "italic"))

# Оставляем окно открытым после завершения рисования
turtle.done()
