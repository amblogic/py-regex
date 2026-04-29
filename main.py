import re
import csv

with open("phonebook_raw.csv", encoding="utf-8") as f:
    all_csv = list(csv.reader(f, delimiter=","))

headers = all_csv[0]
all_contacts = all_csv[1:]

# приведем ФИО к стандарту lastname,firstname,surname
for contact in all_contacts:
    fio = " ".join(contact[:3]).split()
    contact[0] = fio[0] if len(fio) > 0 else ""
    contact[1] = fio[1] if len(fio) > 1 else ""
    contact[2] = fio[2] if len(fio) > 2 else ""

phone_pattern = re.compile(
    r"(\+7|8)?\s*\(?(\d{3})\)?[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})\s*(\(?(доб\.)\s*(\d+)\)?)?"
)


# Нормализуем телефон
for contact in all_contacts:
    # телефон в 6 столбце
    dirty_phone = contact[5]
    match = phone_pattern.search(dirty_phone)
    if match:
        formatted_phone = (
            f"+7({match.group(2)}){match.group(3)}-{match.group(4)}-{match.group(5)}"
        )
        if match.group(7):  # если есть "доб."
            formatted_phone += f" доб.{match.group(8)}"
        contact[5] = formatted_phone

# Сделаем 2 прогона. Сначала сгруппируем тех у кого совпадение по ФИО
# Затем объединим всех с полным ФИО и тех у кого отсутствует отчество
new_list = {}
merged = 0

#1й  проход
for contact in all_contacts:
    # ключ для объединения
    key_double = (contact[0].lower(), contact[1].lower(), contact[2].lower())

    if key_double not in new_list:
        new_list[key_double] = contact
    else:
        # посчитаем сколько дублей нашлось.
        merged += 1
        temp = new_list[key_double]
        # не удаляем содержимое уже сохраненного.
        # Просто добавляем из нового.
        for i in range(len(contact)):
            if temp[i] == "" and contact[i] != "":
                temp[i] = contact[i]


# создаем отдельный список контактов с полными ФИО
fio_list = [contact for key, contact in new_list.items() if contact[2]]

for key, contact in new_list.items():
    # отфильтруем только контакты без отчества
    if contact[2]:
        continue
    else:
        for fio_contact in fio_list:
            if fio_contact[0] == contact[0] and fio_contact[1] == contact[1]:
                # посчитаем сколько дублей нашлось по ФИ.
                merged += 1
                # не удаляем содержимое уже сохраненного.
                # Просто добавляем из нового.
                for i in range(len(fio_contact)):
                    if fio_contact[i] == "" and contact[i] != "":
                        fio_contact[i] = contact[i]
                #если нашлось совпадение - останавливаем
                break

        else:
            #т.к. не нашлось совпадений по ФИО добавим в результирующий список
            fio_list.append(contact)


# Итоговый список
result_list = [headers] + fio_list

print(
    f"Всего обработано контактов: {len(all_contacts)}. Объединено: {merged} дублей по Фамилии Имени Отчеству"
)
# Сохраняем
with open("phonebook_clean.csv", "w", encoding="utf-8", newline="") as f:
    datawriter = csv.writer(f, delimiter=",")
    datawriter.writerows(result_list)
