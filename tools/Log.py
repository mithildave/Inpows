def log(text1, text2 = '', text3 = '', text4 = '', text5 = ''):
    print("-- Log:", text1, text2, text3, text4, text5, '\n')
    pass


def err(text1, text2 = '', text3 = '', text4 = '', text5 = ''):
    print("** Error:", text1, text2, text3, text4, text5, '\n')
    pass


def test(text1, text2 = '', text3 = '', text4 = '', text5 = ''):
    print("## Test massage: ", text1, text2, text3, text4, text5, '\n')
    pass


def lprint(text1, text2 = '', text3 = '', text4 = '', text5 = '', text6 = '', text7 = '', text8 = '', text9 = '', text10 = '', text11 = '', text12 = '', text13 = '', text14 = ''):
    print(text1, text2, text3, text4, text5, text6, text7, text8, text9, text10, text11, text12, text13, text14)
    pass

def record(text1, text2 = '', text3 = '', text4 = '', text5 = ''):
    l = str(text1) + str(text2) + str(text3) + str(text4) + str(text5) + '\n'
    print(l)
    file = open('./exe-time/result-flight.txt', 'a+', encoding='utf-8')
    file.write(l)

def test_print(*arg):
    l = []
    for i in arg:
        l.append(i)
    print(l)


if __name__ == '__main__':
    test_print(1,2,3,4,5,6,7,8,9,0, "2", "5,", 'test')