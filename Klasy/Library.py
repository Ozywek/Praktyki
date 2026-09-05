from LibraryBook import LibraryBook
class Library:
    def __init__(self):
        self.books = []

    def add_book(self, book):
        self.books.append(book)

    def get_books(self):
        return self.books

    def available_books(self):
        borrowed = []
        for i in self.books:
            if i.is_borrowed == False:
                borrowed.append(i)
        return borrowed
    def find_by_author(self, author):
        lista = []
        for i in self.books:
            if i.author == author:
                lista.append(i)
        return lista

    def borrow_by_title(self, title):
        lista = []
        for i in self.books:
            if i.title == title:
                if i.borrow() == True:
                    return True
        return False

    def oldest_book(self):
        if not self.books:
            return None

        year = self.books[0].year
        name = self.books[0].title

        for i in self.books:
            if i.year < year:
                year = i.year
                name = i.title
        return i

    def count_by_author(self):
        dict = {}
        for i in self.books:
            if i.author in dict:
                dict[i.author] += 1
            else: dict[i.author] = 1
        return dict


library = Library()
library.add_book(LibraryBook("Wied?min", "Andrzej Sapkowski", 1993))
library.add_book(LibraryBook("Narrenturm", "Andrzej Sapkowski", 2002))
library.add_book(LibraryBook("Solaris", "Stanis?aw Lem", 1961))

print(len(library.get_books()))              # 3
print(library.oldest_book().title)           # Solaris
# {"Andrzej Sapkowski": 2, "Stanis?aw Lem": 1}

print(library.borrow_by_title("Solaris"))    # True
print(library.borrow_by_title("Solaris"))    # False
print(len(library.available_books()))        # 2"Solaris", "Stanis?aw Lem", 1961))

for book in library.find_by_author("Andrzej Sapkowski"):
    print(book.describe())

print(library.count_by_author())