class Person():
    """ Создание красиво отформатированного резюме """
    def __init__(self, first_name, last_name, age, patronymic="", **description):
        """ Инициализация данных о пользователе """
        self.first_name = first_name
        self.last_name = last_name
        self.patronymic = patronymic
        self.age = age
        self.description = description

    def person_info(self):
        """ Составление резюме """
        print("---Резюме---")
        if self.patronymic == "":
            full_name = f"Имя: {self.first_name}\nФамилия: {self.last_name}"
        else:
            full_name = f"Имя: {self.first_name}\nФамилия: {self.last_name}\nОтчество: {self.patronymic}"
        print(full_name)
        print("Описание:")
        person_description = self.description
        for k, v in person_description.items():
            print(f"{k}: {v}")
        