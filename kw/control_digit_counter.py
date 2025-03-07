# Press the green button in the gutter to run the script.
def count_control_digit(code, number):
    codes = {
        "0": 0,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "X": 10,
        "A": 11,
        "B": 12,
        "C": 13,
        "D": 14,
        "E": 15,
        "F": 16,
        "G": 17,
        "H": 18,
        "I": 19,
        "J": 20,
        "K": 21,
        "L": 22,
        "M": 23,
        "N": 24,
        "O": 25,
        "P": 26,
        "R": 27,
        "S": 28,
        "T": 29,
        "U": 30,
        "W": 31,
        "Y": 32,
        "Z": 33
    }
    assert len(code) == 4
    cod1 = codes[code[0]]
    cod2 = codes[code[1]]
    cod3 = codes[code[2]]
    cod4 = codes[code[3]]
    assert len(number) == 8
    par1 = int(number[0])
    par2 = int(number[1])
    par3 = int(number[2])
    par4 = int(number[3])
    par5 = int(number[4])
    par6 = int(number[5])
    par7 = int(number[6])
    par8 = int(number[7])
    sum = 1 * cod1 + 3 * cod2 + 7 * cod3 + 1 * cod4 + 3 * par1 + 7 * par2 + 1 * par3 + 3 * par4 + 7 * par5 + 1 * par6 + 3 * par7 + 7 * par8
#    print(code + "/" + number + ": " + str(sum % 10))
    return sum % 10