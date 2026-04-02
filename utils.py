def is_number(x):
    try:
        float(x)
        return True
    except:
        return False

def check_even_odd(n):
    if int(n)%2 == 0:
        return "Even"
    else:
        return "Odd"