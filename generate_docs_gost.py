"""
Генератор блок-схемы алгоритма по ГОСТ 19.701-90.
Текст и линии строго черного цвета (не сливаются с фоном).
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def get_cyrillic_font():
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\arial.ttf"
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont("GostFont", p))
                return "GostFont"
            except Exception:
                pass
    return "Helvetica"

def draw_arrow(c, x1, y1, x2, y2):
    c.saveState()
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.line(x1, y1, x2, y2)
    
    p = c.beginPath()
    if x1 == x2:  # Линия вертикально вниз
        p.moveTo(x2, y2)
        p.lineTo(x2 - 4, y2 + 8)
        p.lineTo(x2 + 4, y2 + 8)
    elif y1 == y2 and x2 > x1:  # Линия вправо
        p.moveTo(x2, y2)
        p.lineTo(x2 - 8, y2 - 4)
        p.lineTo(x2 - 8, y2 + 4)
    elif y1 == y2 and x2 < x1:  # Линия влево
        p.moveTo(x2, y2)
        p.lineTo(x2 + 8, y2 - 4)
        p.lineTo(x2 + 8, y2 + 4)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.restoreState()

def generate_pdf():
    pdf_path = "ГОСТ_19.701_90_Алгоритм.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    f = get_cyrillic_font()

    # Явно задаем базовые цвета: обводка черная, заливка для текста черная
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineWidth(1.2)

    # Заголовок
    c.setFont(f, 13)
    c.drawCentredString(width / 2, height - 35, "СХЕМА АЛГОРИТМА СИСТЕМЫ (ГОСТ 19.701-90)")
    c.setFont(f, 9)
    c.drawCentredString(width / 2, height - 48, "Процесс разграничения прав (RBAC), каталога и управления заказами")

    cx = width / 2

    # Функция вывода текста с принудительным черным цветом
    def draw_text(x, y, text, size=9, center=True):
        c.saveState()
        c.setFillColorRGB(0, 0, 0)
        c.setFont(f, size)
        if center:
            c.drawCentredString(x, y, text)
        else:
            c.drawString(x, y, text)
        c.restoreState()

    # 1. Пуск (Терминатор)
    c.roundRect(cx - 70, height - 90, 140, 28, 10, stroke=1, fill=0)
    draw_text(cx, height - 78, "Пуск (Старт)", size=10)
    draw_arrow(c, cx, height - 90, cx, height - 115)

    # 2. Ввод учетных данных (Параллелограмм)
    p = c.beginPath()
    p.moveTo(cx - 85, height - 145)
    p.lineTo(cx + 85, height - 145)
    p.lineTo(cx + 65, height - 115)
    p.lineTo(cx - 105, height - 115)
    p.close()
    c.drawPath(p, stroke=1, fill=0)
    draw_text(cx - 10, height - 134, "Ввод логина / пароля или Гость", size=9)
    draw_arrow(c, cx, height - 145, cx, height - 175)

    # 3. Ромб: Проверка входа
    pr1 = c.beginPath()
    pr1.moveTo(cx, height - 175)
    pr1.lineTo(cx + 85, height - 195)
    pr1.lineTo(cx, height - 215)
    pr1.lineTo(cx - 85, height - 195)
    pr1.close()
    c.drawPath(pr1, stroke=1, fill=0)
    draw_text(cx, height - 198, "Успешный вход?", size=9)

    # Ветка Нет (Ошибка входа)
    draw_text(cx + 92, height - 190, "Нет", size=9, center=False)
    c.line(cx + 85, height - 195, cx + 170, height - 195)
    c.line(cx + 170, height - 195, cx + 170, height - 130)
    draw_arrow(c, cx + 170, height - 130, cx + 75, height - 130)

    # Ветка Да
    draw_text(cx + 5, height - 227, "Да", size=9, center=False)
    draw_arrow(c, cx, height - 215, cx, height - 245)

    # 4. Процесс: Каталог товаров
    c.rect(cx - 85, height - 280, 170, 35, stroke=1, fill=0)
    draw_text(cx, height - 263, "Загрузка товаров из БД,", size=9)
    draw_text(cx, height - 275, "подсветка скидок и остатков", size=9)
    draw_arrow(c, cx, height - 280, cx, height - 305)

    # 5. Ромб: Администратор?
    pr2 = c.beginPath()
    pr2.moveTo(cx, height - 305)
    pr2.lineTo(cx + 95, height - 330)
    pr2.lineTo(cx, height - 355)
    pr2.lineTo(cx - 95, height - 330)
    pr2.close()
    c.drawPath(pr2, stroke=1, fill=0)
    draw_text(cx, height - 333, "Администратор?", size=9)

    # Ветка Да -> Админ
    draw_text(cx + 102, height - 325, "Да", size=9, center=False)
    c.line(cx + 95, height - 330, cx + 160, height - 330)
    draw_arrow(c, cx + 160, height - 330, cx + 160, height - 375)

    c.rect(cx + 85, height - 425, 150, 50, stroke=1, fill=0)
    draw_text(cx + 160, height - 398, "CRUD товаров (300х200)", size=8.5)
    draw_text(cx + 160, height - 412, "и полный доступ к Заказам", size=8.5)

    # Ветка Нет -> Менеджер?
    draw_text(cx - 135, height - 325, "Нет", size=9, center=False)
    c.line(cx - 95, height - 330, cx - 160, height - 330)
    draw_arrow(c, cx - 160, height - 330, cx - 160, height - 375)

    # 6. Ромб: Менеджер?
    pr3 = c.beginPath()
    pr3.moveTo(cx - 160, height - 375)
    pr3.lineTo(cx - 85, height - 400)
    pr3.lineTo(cx - 160, height - 425)
    pr3.lineTo(cx - 235, height - 400)
    pr3.close()
    c.drawPath(pr3, stroke=1, fill=0)
    draw_text(cx - 160, height - 403, "Менеджер?", size=9)

    # Ветка Да (Менеджер)
    draw_text(cx - 75, height - 395, "Да", size=9, center=False)
    c.line(cx - 85, height - 400, cx - 30, height - 400)
    draw_arrow(c, cx - 30, height - 400, cx - 30, height - 455)

    c.rect(cx - 100, height - 495, 140, 40, stroke=1, fill=0)
    draw_text(cx - 30, height - 472, "Каталог + Просмотр", size=8.5)
    draw_text(cx - 30, height - 485, "модуля Заказов", size=8.5)

    # Ветка Нет (Клиент / Гость)
    draw_text(cx - 245, height - 395, "Нет", size=9, center=False)
    c.line(cx - 235, height - 400, cx - 270, height - 400)
    draw_arrow(c, cx - 270, height - 400, cx - 270, height - 455)

    c.rect(cx - 340, height - 495, 140, 40, stroke=1, fill=0)
    draw_text(cx - 270, height - 472, "Только просмотр каталога,", size=8.5)
    draw_text(cx - 270, height - 485, "поиск и фильтрация", size=8.5)

    # Слияние
    c.line(cx + 160, height - 425, cx + 160, height - 525)
    c.line(cx - 30, height - 495, cx - 30, height - 525)
    c.line(cx - 270, height - 495, cx - 270, height - 525)
    c.line(cx - 270, height - 525, cx + 160, height - 525)
    draw_arrow(c, cx, height - 525, cx, height - 555)

    # 7. Останов (Терминатор)
    c.roundRect(cx - 70, height - 590, 140, 28, 10, stroke=1, fill=0)
    draw_text(cx, height - 578, "Останов (Выход)", size=10)

    c.showPage()
    c.save()
    print("ГОСТ_19.701_90_Алгоритм.pdf успешно перегенерирован с четким черным шрифтом!")

if __name__ == "__main__":
    generate_pdf()