import re
def validateEmail(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return 1
    return 0

#inappropriate words
    #1.定义inappropriate words数组
    #2.遍历传进来的字符串
    #3.return value
dirtyword =  {'fuck','shite'}
def inDictElement(term, dirtyword):
    num_texts_with_term = len([True for text in dirtyword.values() if term.lower() in text.lower().split()])
    if num_texts_with_term == len(dirtyword):
        return 1
    else:
        return 0

