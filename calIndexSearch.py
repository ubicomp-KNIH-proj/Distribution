import datetime

def dateToIndex(reg_year, reg_month, reg_day, target_year, target_month, target_day):
    reg = datetime.datetime.strptime(reg_year + '-' + reg_month + '-' + reg_day, "%Y-%m-%d")
    target = datetime.datetime.strptime(target_year + '-' + target_month + '-' + target_day, "%Y-%m-%d")

    index = target - reg
    return int(index.days)

def listLength(reg_year, reg_month, reg_day, target_year, target_month, target_day):
    reg = datetime.datetime.strptime(reg_year + '-' + reg_month + '-' + reg_day, "%Y-%m-%d")
    target = datetime.datetime.strptime(target_year + '-' + target_month + '-' + target_day, "%Y-%m-%d")

    index = target - reg
    return int(index.days) + 1

def monthToInt(month):
    if "Aug":
        return 8
    elif "Sep":
        return 9
    elif "Oct":
        return 10
    elif "Nov":
        return 11
    elif "Dec":
        return 12
# def main():
#     reg_y, reg_m, reg_d = input("year, month, day: ").split(' ')
#     tar_y, tar_m, tar_d = input("year, month, day: ").split(' ')
#     print(dateToIndex(reg_y, reg_m, reg_d, tar_y, tar_m, tar_d))

# if __name__ == "__main__":
#     main()
