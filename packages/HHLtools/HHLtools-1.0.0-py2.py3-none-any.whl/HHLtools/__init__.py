import string

def output(content):
    print('success!your content:\n{}'.format(content))


def countWordNum(content):
    wordList = [word.lower().strip(string.punctuation) for word in content.split()]
    words = {word:wordList.count(word) for word in list(set(wordList))}
    del words['']
    words = {key:words[key] for key in sorted(words.keys(),key=lambda x:wordList.index(x))}
    return words

