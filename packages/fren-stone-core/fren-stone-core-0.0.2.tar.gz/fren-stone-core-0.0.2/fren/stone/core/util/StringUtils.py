def isNoneOrEmpty(data):
    '''
    判断对象是否为空
    :param data 数据
    '''
    if data is None:
        return True
    #空数组，空对象也认为是空
    elif str(data) == "[]" or str(data) == "{}":
        return True
    #去除空格，换行符，制表符后为空也为空
    elif isinstance(data,str) and data.replace(" ","").replace("\n","").replace("\t","") == "":
        return True
    else:
        return False


