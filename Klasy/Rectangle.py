class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2*self.height+2*self.width
    def is_square(self):
        if self.width == self.height:
            return True
        else:
            return False