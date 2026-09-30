"""Генерация файла Отчет_отладка.docx без внешних зависимостей (чистый Python: zipfile + XML)."""

import zipfile
import os

def create_docx(filename="Отчет_отладка.docx"):
    # Минимальная структура XML документа Word (.docx)
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    # Таблица и текст отчета
    test_rows = [
        ("1", "Авторизация администратора (admin@shop.ru)", "Выдача токена сессии, появление функционала добавления и редактирования", "Успешно"),
        ("2", "Вход в роли Гостя (без пароля)", "Открытие каталога без кнопок редактирования и без доступа к заказам", "Успешно"),
        ("3", "Подсветка товара со скидкой > 15%", "Применение фона #2E8B57, текст белый, перечеркнутая базовая цена", "Успешно"),
        ("4", "Подсветка отсутствующего товара (остаток = 0)", "Выделение строки голубым цветом #E0F7FA", "Успешно"),
        ("5", "Попытка удаления товара, входящего в заказ", "Отказ сервера HTTP 400 с информативным сообщением об ошибке", "Успешно"),
        ("6", "Загрузка изображения товара и ресайз", "Ограничение до 5 МБ и автоматическое сжатие ровно до 300х200 пикселей", "Успешно"),
        ("7", "Сортировка по остатку и фильтрация по поставщику", "Корректная совместная фильтрация в реальном времени", "Успешно"),
    ]

    xml_rows = ""
    # Заголовок таблицы
    xml_rows += """
    <w:tr>
      <w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>№</w:t></w:r></w:p></w:tc>
      <w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Тестируемый сценарий</w:t></w:r></w:p></w:tc>
      <w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Ожидаемый результат</w:t></w:r></w:p></w:tc>
      <w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Статус</w:t></w:r></w:p></w:tc>
    </w:tr>"""

    for num, name, exp, status in test_rows:
        xml_rows += f"""
        <w:tr>
          <w:tc><w:p><w:r><w:t>{num}</w:t></w:r></w:p></w:tc>
          <w:tc><w:p><w:r><w:t>{name}</w:t></w:r></w:p></w:tc>
          <w:tc><w:p><w:r><w:t>{exp}</w:t></w:r></w:p></w:tc>
          <w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>{status}</w:t></w:r></w:p></w:tc>
        </w:tr>"""

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:jc w:val="center"/></w:pPr>
      <w:r><w:rPr><w:b/><w:sz w:val="32"/></w:rPr><w:t>Отчет о результатах тестирования и отладки</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Специальность: 09.02.07 Информационные системы и программирование</w:t></w:r></w:p>
    <w:p><w:r><w:t>Программный модуль: Управление складом и заказами</w:t></w:r></w:p>
    <w:p/>
    <w:p><w:r><w:rPr><w:b/><w:sz w:val="24"/></w:rPr><w:t>1. Протокол выполнения тест-кейсов</w:t></w:r></w:p>
    
    <w:tbl>
      <w:tblPr>
        <w:tblBorders>
          <w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/>
          <w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/>
          <w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>
          <w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/>
          <w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/>
          <w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/>
        </w:tblBorders>
      </w:tblPr>
      {xml_rows}
    </w:tbl>
    
    <w:p/>
    <w:p><w:r><w:rPr><w:b/><w:sz w:val="24"/></w:rPr><w:t>2. Заключение</w:t></w:r></w:p>
    <w:p>
      <w:r><w:t>В ходе функционального тестирования нештатных и аварийных ситуаций не зафиксировано. Все модули (авторизация, каталог с подсветкой, поиск/фильтрация, CRUD товаров, модуль заказов) работают штатно и соответствуют техническому заданию.</w:t></w:r>
    </w:p>
    <w:sectPr/>
  </w:body>
</w:document>"""

    # Упаковываем всё в zip с расширением .docx
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as docx:
        docx.writestr('[Content_Types].xml', content_types)
        docx.writestr('_rels/.rels', rels)
        docx.writestr('word/document.xml', document_xml)

    print(f"Документ {filename} успешно создан (без сторонних зависимостей)!")

if __name__ == "__main__":
    create_docx()