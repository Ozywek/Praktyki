class LibraryBook:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year
        self.is_borrowed = False

    def borrow(self):
        if self.is_borrowed == False:
            self.is_borrowed = True
            return True
        else: return False

    def give_back(self):
        if self.is_borrowed:
            self.is_borrowed = False
            return True
        else: return False

    def describe(self):
        print(self.title + " (" + str(self.year) + "), " + self.author )
