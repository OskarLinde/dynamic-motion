
def parse(line):
    comment = line.find(';')
    if comment > -1:
        line = line[:comment]
    
    out = {}
    ls = line.split(' ')
    for l in ls:
        l = l.strip()
        if len(l) > 0:
            cmd = l[0]
            if cmd < 'A' or cmd > 'Z':
                raise Exception(f'Parse error: {line}')
            val = float(l[1:])
            out[cmd] = val
    
    return out
