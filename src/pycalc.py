class NotANumberError(ValueError):
    """Input that isn't an int or float"""

def check_types(value):
    c = 0
    for check in (int, float):
        try:
            value = check(value)
            if type(value) == check:
                return value
        except:
            continue
    
    if type(value) == str:
        raise NotANumberError("The input entered was neither int or float compatible," \
                                " therefore this error has been encountered") from None
    else:
        return value

def calc():
    x = input("First number please: ")
    y = input("Second number please: ")

    first_number = check_types(x)
    second_number = check_types(y)

    print("Confirming either int or float")
    print("First number Type", type(first_number))
    print("Second number Type", type(second_number))

    final_number = first_number+second_number
    print(f"Adding: {first_number} and {second_number} to get {final_number}")
    return final_number

if __name__ == "__main__":
    number = calc()
