def flatten(l):
    result = []
    for i in l:
        if type(i) == list:
            result += flatten(i)
        else:
            result += [i]
    return result