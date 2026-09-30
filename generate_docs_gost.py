"""Генерация PDF документа со схемой алгоритма по ГОСТ 19.701-90."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def register_cyrillic_font():
    """Поиск и регистрация системного TrueType шрифта с поддержкой кириллицы."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("CustomFont", path))
                return "CustomFont"
            except Exception:
                pass
    return "Helvetica"


def draw_arrow(c, x1, y1, x2, y2):
    """Рисование соединительной линии со стрелкой по ГОСТ 19.701-90."""
    c.line(x1, y1, x2, y2)
    # Наконечник стрелки через path
    p = c.beginPath()
    if x1 == x2:  # Вертикальная линия вниз
        p.moveTo(x2, y2)
        p.lineTo(x2 - 4, y2 + 8)
        p.lineTo(x2 + 4, y2 + 8)
    elif y1 == y2:  # Горизонтальная линия вправо
        p.moveTo(x2, y2)
        p.lineTo(x2 - 8, y2 - 4)
        p.lineTo(x2 - 8, y2 + 4)
    p.close()
    c.drawPath(p, stroke=1, fill=1)


def draw_flowchart_pdf(filename="ГОСТ_19.701_90_Алгоритм.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    font_name = register_cyrillic_font()

    is_cyrillic = font_name != "Helvetica"

    # Заголовок документа
    c.setFont(font_name, 14)
    title = (
        "Схема алгоритма работы системы (ГОСТ 19.701-90)"
        if is_cyrillic
        else "Algoritm raboty sistemy (GOST 19.701-90)"
    )
    c.drawCentredString(width / 2, height - 50, title)

    c.setFont(font_name, 10)
    sub = (
        "Процесс авторизации и разграничения прав доступа"
        if is_cyrillic
        else "Protsess avtorizatsii i razgranicheniya prav dostupa"
    )
    c.drawCentredString(width / 2, height - 68, sub)

    c.setLineWidth(1.2)

    # 1. Символ «Пуск / Останов» (Терминатор) - скругленный прямоугольник
    c.roundRect(220, height - 130, 160, 36, 12, stroke=1, fill=0)
    t1 = "Начало работы" if is_cyrillic else "Nachalo raboty"
    c.drawCentredString(300, height - 110, t1)

    # Линия к вводу данных
    draw_arrow(c, 300, height - 130, 300, height - 165)

    # 2. Символ «Данные» (Параллелограмм) - Ввод учетных данных
    p_data = c.beginPath()
    p_data.moveTo(225, height - 200)
    p_data.lineTo(395, height - 200)
    p_data.lineTo(375, height - 165)
    p_data.lineTo(205, height - 165)
    p_data.close()
    c.drawPath(p_data, stroke=1, fill=0)
    t2 = (
        "Ввод логина и пароля" if is_cyrillic else "Vvod logina i parolya"
    )
    c.drawCentredString(300, height - 186, t2)

    # Линия к первому условию
    draw_arrow(c, 300, height - 200, 300, height - 235)

    # 3. Символ «Решение» (Ромб) - Проверка валидности
    p_dec1 = c.beginPath()
    p_dec1.moveTo(300, height - 235)
    p_dec1.lineTo(385, height - 265)
    p_dec1.lineTo(300, height - 295)
    p_dec1.lineTo(215, height - 265)
    p_dec1.close()
    c.drawPath(p_dec1, stroke=1, fill=0)
    t3 = (
        "Успешный вход?" if is_cyrillic else "Uspeshny vhod?"
    )
    c.drawCentredString(300, height - 269, t3)

    # Ветка НЕТ (Ошибка -> возвращение к вводу данных)
    c.drawString(392, height - 260, "Нет" if is_cyrillic else "Net")
    c.line(385, height - 265, 450, height - 265)
    c.line(450, height - 265, 450, height - 182)
    draw_arrow(c, 450, height - 182, 385, height - 182)

    # Ветка ДА (переход к проверке роли)
    c.drawString(306, height - 308, "Да" if is_cyrillic else "Da")
    draw_arrow(c, 300, height - 295, 300, height - 335)

    # 4. Символ «Решение» (Ромб) - Проверка роли (Администратор?)
    p_dec2 = c.beginPath()
    p_dec2.moveTo(300, height - 335)
    p_dec2.lineTo(395, height - 365)
    p_dec2.lineTo(300, height - 395)
    p_dec2.lineTo(205, height - 365)
    p_dec2.close()
    c.drawPath(p_dec2, stroke=1, fill=0)
    t4 = "Роль = Администратор?" if is_cyrillic else "Rol = Administrator?"
    c.drawCentredString(300, height - 369, t4)

    # Ветка ДА (Администратор) -> вправо
    c.drawString(402, height - 360, "Да" if is_cyrillic else "Da")
    c.line(395, height - 365, 470, height - 365)
    draw_arrow(c, 470, height - 365, 470, height - 430)

    # Символ «Процесс» (Прямоугольник) - Полный доступ
    c.rect(395, height - 475, 150, 45, stroke=1, fill=0)
    t_adm1 = "Доступ к CRUD товаров" if is_cyrillic else "Dostup k CRUD tovarov"
    t_adm2 = "и управлению заказами" if is_cyrillic else "i zakazam (polny)"
    c.drawCentredString(470, height - 452, t_adm1)
    c.drawCentredString(470, height - 466, t_adm2)

    # Ветка НЕТ (Клиент / Гость) -> прямо вниз
    c.drawString(306, height - 408, "Нет" if is_cyrillic else "Net")
    draw_arrow(c, 300, height - 395, 300, height - 430)

    # Символ «Процесс» (Прямоугольник) - Ограниченный доступ
    c.rect(220, height - 475, 160, 45, stroke=1, fill=0)
    t_usr1 = "Просмотр каталога," if is_cyrillic else "Prosmotr kataloga,"
    t_usr2 = "поиск и фильтрация" if is_cyrillic else "poisk i filtratsiya"
    c.drawCentredString(300, height - 452, t_usr1)
    c.drawCentredString(300, height - 466, t_usr2)

    # Слияние потоков к концу
    c.line(470, height - 475, 470, height - 515)
    c.line(470, height - 515, 300, height - 515)
    c.line(300, height - 475, 300, height - 515)
    draw_arrow(c, 300, height - 515, 300, height - 545)

    # 5. Символ «Пуск / Останов» (Терминатор) - Завершение работы
    c.roundRect(220, height - 580, 160, 35, 12, stroke=1, fill=0)
    t_end = "Конец работы" if is_cyrillic else "Konets raboty"
    c.drawCentredString(300, height - 560, t_end)

    c.showPage()
    c.save()
    print(f"Документ {filename} успешно сгенерирован!")


if __name__ == "__main__":
    draw_flowchart_pdf()