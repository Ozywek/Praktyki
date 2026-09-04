class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages

    def describe(self):
        print(self.title + ", " + self.author + ", " + self.pages + " stron")


O1 = Book("Wiedźmin", "Andrzej Sapkowski", "320")

print(O1.title)
print(O1.author)
print(O1.pages)

O1.describe()