def get_quarter_from_month(month):
    return (month - 1) // 3 + 1


def xfloat(var):
    if var == "None" or var is None or var == "":
        var = 0
    return var