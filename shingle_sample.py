# -*- coding: UTF-8 -*-
if __name__ == '__build__':
    raise Exception

def canonize(source):
        stop_symbols = '.,!?:;-\n\r()'

        stop_words = (u'это', u'как', u'так',
        u'и', u'в', u'над',
        u'к', u'до', u'не',
        u'на', u'но', u'за',
        u'то', u'с', u'ли',
        u'а', u'во', u'от',
        u'со', u'для', u'о',
        u'же', u'ну', u'вы',
        u'бы', u'что', u'кто',
        u'он', u'она')

        return ( [x for x in [y.strip(stop_symbols) for y in source.lower().split()] if x and (x not in stop_words)] )

def genshingle(source):
    import binascii
    shingleLen = 6 #длина шингла
    out = [] 
    for i in range(len(source) - (shingleLen - 1)):
        out.append (binascii.crc32(' '.join( [x for x in source[i:i + shingleLen]] ).encode('utf-8')))

    return out

def compaire (source1, source2):
    same = 0
    for i in range(len(source1)):
        if source1[i] in source2:
            same = same + 1

    return same * 2 / float(len(source1) + len(source2)) * 100

def main():
    text1 = u'Разум дан человеку для того, чтобы он разумно жил, а не для того только, чтобы он понимал, что он неразумно живет.' 
    text2 = u'Человек обладает разумом, чтобы жить разумно, а не только для того, чтобы понимать, что он неразумно живет.' 
    text3 = u'Разум дан человеку для того, чтобы он разумно жил, а не для того только, чтобы он понимал, что он неразумно живет.'
    text4 = u'Разум дан человеку не для того, чтобы он понимал, что он неразумно живет.'

    sh1 = genshingle(canonize(text1))
    sh2 = genshingle(canonize(text2))
    sh3 = genshingle(canonize(text3))
    sh4 = genshingle(canonize(text4))


    print compaire(sh1, sh2)
    print compaire(sh1, sh3)
    print compaire(sh1, sh4)


# Start program
main()