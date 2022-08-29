import re
import pickle
import os.path
from dataclasses import field
from typing import List
from collections import UserDict
from datetime import datetime

import parse


def input_error(func):
    def iner(*args):
        try:
            return func(*args)
        except NoNameError:
            return "Enter user name"
        except NoKeyInformation:
            return f"no key information {args[1]}"
        except ErrorDate:
            return f"incorrect date {args[4]}"
        except ErrorPhone:
            return f"incorrect phone {args[2]}"
        except Exception as ex:
            return ex

    return iner


class ErrorDate(Exception):
    pass


class ErrorPhone(Exception):
    pass


class NoNameError(Exception):
    pass


class NoKeyInformation(Exception):
    pass


class Field:

    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class Name(Field):

    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if value == "":
            raise NoNameError

        self.__value = value


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        try:
            birthday = datetime.strptime(value, '%d-%m-%Y').date()
        except ValueError:
            raise ErrorDate

        self.__value = birthday


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        phone_pattern = r"\+?\d+\(?\d+\)?\d+\-?\d+\-?\d+"
        result = re.search(phone_pattern, value)
        if not result:
            raise ErrorPhone

        self.__value = value


class Email(Field):
    pass


class Record:
    def __init__(self, name: Name, birthday: Birthday = None) -> None:
        self.name = name
        self.birthday = birthday
        self.phones = []
        self.emails = []

    def __str__(self) -> str:
        result = self.name.value
        if self.phones:
            list_phones = []
            for phone in self.phones:
                list_phones.append(phone.value)
            result += ' ' + '; '.join(list_phones)
        if self.emails:
            list_emails = []
            for email in self.emails:
                list_emails.append(email.value)
            result += ' ' + '; '.join(list_emails)

        if self.birthday:
            result += " " + self.birthday.value.strftime('%Y/%m/%d')

        return result

    def add_phone(self, phone):
        self.phones.append(Phone(phone))
        return "phone add"

    def add_email(self, email):
        self.emails.append(Email(email))
        return "email add"

    def delete_phone(self, delete_phone):
        is_in_phones = False
        for phone in self.phones:
            if phone.value == delete_phone:
                self.phones.remove(phone)
                is_in_phones = True
                break

        if is_in_phones:
            return f"phone delete {delete_phone}"
        else:
            return f"{self.name.value} hes no phone {delete_phone}"

    def delete_email(self, delete_email):
        is_in_emails = False
        for email in self.emails:
            if email.value == delete_email:
                self.emails.remove(email)
                is_in_emails = True
                break

        if is_in_emails:
            return f"email delete {delete_email}"
        else:
            return f"{self.name.value} hes no phone {delete_email}"

    def days_to_birthday(self):
        if self.birthday:
            now = datetime.now().date()
            birthday = datetime(
                year=now.year, month=self.birthday.value.month, day=self.birthday.value.day).date()
            if now > birthday:
                birthday = datetime(
                    year=now.year + 1, month=self.birthday.value.month, day=self.birthday.value.day).date()

            delta = birthday - now
            return delta.days


class AddressBook(UserDict):

    def __init__(self, filename=''):
        super().__init__()
        if filename == '':
            filename = 'AddressBook.txt'
            filename_json = 'AddressBook.json'

        self.filename = filename

    def save_to_file(self):
        with open(self.filename, "wb") as fh:
            pickle.dump(self, fh)

    def read_from_file(self):
        addressBook = self
        if os.path.isfile(self.filename):
            with open(self.filename, "rb") as fh:
                unpacked = pickle.load(fh)
            if isinstance(unpacked, AddressBook):
                addressBook = unpacked
        return addressBook

    __items_per_page = 20

    def items_per_page(self, value):
        self.__items_per_page = value

    def __iter__(self):
        self.page = 0
        return self

    items_per_page = property(fget=None, fset=items_per_page)

    def __next__(self):
        records = list(self.data.values())
        start_index = self.page * self.__items_per_page
        end_index = (self.page + 1) * self.__items_per_page
        self.page += 1
        if len(records) > end_index:
            to_return = records[start_index:end_index]
        else:
            if len(records) > start_index:
                to_return = records[start_index: len(records)]
            else:
                raise StopIteration
        return to_return

    @input_error
    def add_record(self, name, phone, email, birthday):
        field_name = Name(name)
        record = Record(field_name)
        if phone:
            record.add_phone(phone)
        if email:
            record.add_email(email)
        if birthday:
            record.birthday = Birthday(birthday)

        self.data[record.name.value] = record
        return "done"

    @input_error
    def get_record(self, name):
        if name == "":
            raise NoNameError
        result = self.data.get(name)
        if not result:
            raise NoKeyInformation
        return result

    def show_all(self):
        result = ""
        for i in self:
            result += "*" * 15 + "\n"
            for record in i:
                result += str(record) + "\n"
            result += "*" * 15
        return result

    def find_records(self, str_find):
        records = []
        for record in self.data.values():
            record_str = str(record)
            if str_find in record_str:
                records.append(record)

        return records


def main():

    addressBook = AddressBook()
    addressBook = addressBook.read_from_file()

    while True:
        user_input = input(">>> ")

        command, args = parse.parse_user_input(user_input)
        phone = parse.get_phone_from_args(args)
        email = parse.get_email_from_args(args)
        birthday = parse.get_birthday_from_args(args)
        name = args.replace(phone, "").replace(
            email, "").replace(birthday, "").strip()

        if command == "hello":
            print("How can I help you?")
        elif command == "exit":
            addressBook.save_to_file()
            print("Good bye!")
            break
        elif command == "add":
            print(addressBook.add_record(name, phone, email, birthday))
        elif command == "change":
            record = addressBook.get_record(name)
            if isinstance(record, Record):
                if phone:
                    print(record.add_phone(phone))
                if email:
                    print(record.add_email(email))
            else:
                print(record)
        elif command == "phone":
            record = addressBook.get_record(name)
            print(record)
        elif command == "birthday":
            record = addressBook.get_record(name)
            print(record.days_to_birthday())
        elif command == "show_all":
            print(addressBook.show_all())
        elif command == "delete":
            record = addressBook.get_record(name)
            if isinstance(record, Record):
                if phone:
                    print(record.delete_phone(phone))
                if email:
                    print(record.delete_email(email))
            else:
                print(record)
        elif command == "find":
            records = addressBook.find_records(args)
            for record in records:
                print(record)
        else:
            print(f"I don't know what means '{user_input}'")


if __name__ == "__main__":
    main()
