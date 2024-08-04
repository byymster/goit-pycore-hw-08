from collections import UserDict
from datetime import datetime, timedelta
import pickle

DUMP_FILE = "address_book.dat"


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me correct values.\nType 'help' to see available commands."
        except IndexError:
            return "Invalid number of arguments.\nType 'help' to see available commands."

    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    # реалізація класу
    pass


class Birthday(Field):
    def __init__(self, value):
        try:
            date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Phone(Field):
    def __init__(self, value):
        if not self._validate(value):
            raise ValueError("Phone number must contain 10 digits")
        super().__init__(value)

    @staticmethod
    def _validate(phone_number):
        return phone_number.isdigit() and len(phone_number) == 10


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p.value

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

    def __str__(self):
        birthday_data = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_data}"


class AddressBook(UserDict):

    @input_error
    def add_record(self, args):
        record = Record(args[0])
        record.add_phone(args[1])
        self.data[record.name.value] = record
        return f"Contact {record.name.value} was added."

    def find(self, name):
        return self.data.get(name, "Contact not found")

    def delete(self, name):
        del self.data[name]

    def get_upcoming_birthdays(self) -> list[dict[str, str]]:
        upcoming_birthdays = []
        today = datetime.now()
        for user in self.data.values():
            birthday_this_year = datetime.strptime(
                f'{today.year}.{user.birthday.value.month}.{user.birthday.value.day}', "%Y.%m.%d")
            difference = (birthday_this_year - today).days

            if 0 <= difference <= 7:
                # If the birthday falls on a weekend, shift it to the next Monday
                if birthday_this_year.weekday() >= 5:
                    birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()))
                upcoming_birthdays.append({
                    'name': user.name.value,
                    'congratulation_date': birthday_this_year.strftime('%Y.%m.%d')
                })

        return upcoming_birthdays

    @input_error
    def change_record(self, args):
        name, old_phone, new_phone = args
        record = self.find(name)
        if isinstance(record, Record):
            record.edit_phone(old_phone, new_phone)
            return f"Phone number {old_phone} was changed to {new_phone} for contact {name}."
        else:
            return record

    def all(self):
        return "\n".join([str(data) for data in self.data.values()])

    @input_error
    def add_birthday(self, args):
        name, birthday = args
        record = self.find(name)
        if not isinstance(record, Record):
            return record
        record.add_birthday(birthday)
        return f"Birthday {birthday} was added to contact {name}."

    @input_error
    def show_birthday(self, args):
        name = args[0]
        record = self.find(name)
        return record.birthday

    @input_error
    def birthdays(self):
        upcoming_birthdays = self.get_upcoming_birthdays()
        if not upcoming_birthdays:
            return "No upcoming birthdays."
        return "\n".join([f"{data['name']} - {data['congratulation_date']}" for data in upcoming_birthdays])

    def load(self):
        try:
            with open(DUMP_FILE, "rb") as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            print("No data file found. Creating a new data structure.")

    def save(self):
        with open(DUMP_FILE, "wb") as file:
            pickle.dump(self.data, file)


def main():
    contacts = AddressBook()
    contacts.load()
    print("Welcome to the assistant bot!")
    while True:
        try:
            user_input = input("Enter a command: ")
            command, *args = parse_input(user_input)
            match command:
                case "close" | "exit":
                    print("Good bye!")
                    break
                case "hello":
                    print("How can I help you?")
                case "add":
                    print(contacts.add_record(args))
                case "change":
                    print(contacts.change_record(*args))
                case 'phone':
                    print(contacts.find(args[0]))
                case 'all':
                    print(contacts.all())
                case 'add-birthday':
                    print(contacts.add_birthday(args))
                case 'show-birthday':
                    print(contacts.show_birthday(args))
                case 'birthdays':
                    print(contacts.birthdays())
                case 'help':
                    print("""
                    Available commands:
                        hello - Greet the bot.
                        add <username> <phone> - Add a new contact.
                        change <username> <phone> - Change an existing contact.
                        phone <username> - Get phone number of a contact.
                        all - List all contacts.
                        add-birthday <username> <birthday> - Add birthday to a contact.
                        show-birthday <username> - Show birthday of a contact.
                        birthdays - Show upcoming birthdays.
                    """)
                case _:
                    print("Invalid command.")
        except ValueError as e:
            print(e)
    contacts.save()


if __name__ == "__main__":
    main()
