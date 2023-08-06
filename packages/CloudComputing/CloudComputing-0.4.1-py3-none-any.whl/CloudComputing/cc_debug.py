COLOR_CODE = {
    'INFO': "\033[1;32m",
    'WARNING': "\033[1;35m",
    'ERROR': "\033[1;31m"
}
NORMAL = "\033[0m"

def cc_print(msg, level=0):
    # level = 0  > normal print
    # level = 1  > info
    # level = 2  > warning
    # level = 3  > error
    # level = -1 > do not print
    if level < 0:
        return
    if level == 0:
        print(msg)
    elif level == 1:
        print(" {}[INFO]{}    {}".format(COLOR_CODE['INFO'], NORMAL, msg))
    elif level == 2:
        print(" {}[WARNING]{} {}".format(COLOR_CODE['WARNING'], NORMAL, msg))
    elif level == 3:
        print(" {}[ERROR]{}   {}".format(COLOR_CODE['ERROR'], NORMAL, msg))