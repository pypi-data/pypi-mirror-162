class PersonForBMI:
    def __init__(self, age, height, weight, gender=None):
        self.age = age
        self.height = height
        self.weight = weight
        self.gender = gender
        self.__bmi = 0.0

    def calculate_bmi(self):
        if self.gender.upper() == "male".upper() or self.gender.upper() == "m".upper():
            self.__bmi = self.weight / (self.height / 100 * self.height / 100) * 0.98
        elif (
            self.gender.upper() == "female".upper()
            or self.gender.upper() == "f".upper()
        ):
            self.__bmi = self.weight / (self.height / 100 * self.height / 100) * 0.94
        elif self.gender not in ["female", "male", "f", "m"]:
            print("Gender must be either: female/male/f/m ...")
            return
        return round(self.__bmi, 2)

    def conclusions(self):
        if self.__bmi < 18.5:
            print("Your weight is too low")
        elif self.__bmi < 24.9:
            print("Your weight is normal")
        elif self.__bmi < 29.9:
            print("You have an overweight")
        elif self.__bmi < 34.9:
            print("1st level overweight")
        elif self.__bmi < 39.9:
            print("2nd level overweight")
        else:
            print("3rd level overweight")

    def __call__(self):
        return f"(age:{self.age}, height:{self.height}, weight:{self.weight}, gender:{self.gender}, bmi:{self.__bmi})"
