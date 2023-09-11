import hashlib
import random

Z16 = Integers(16)

def generate_nluts(str_seed, nb_nluts, path="../data/nluts"):
    h = hashlib.new('sha256')
    h.update(str_seed.encode('UTF-8'))
    strex = h.hexdigest()
    random.seed(strex)
    with open(path, 'w') as fd:
        for _ in range(nb_nluts):
            nlut = []
            for i in range(8):
                nlut.append(random.randrange(16))
                fd.write(hex(nlut[i])[2:])
            fd.write('\n')


def load_nluts(path="../data/nluts"):
    nluts = []
    with open(path, 'r') as fd:
        line = fd.readline()
        while (line):
            nlut = []
            for c in line[:-1]:
                nlut.append(Z16(int(c, 16)))
            for i in range(len(line) - 1):
                nlut.append(Z16(-nlut[i]))
            nluts.append(nlut)
            line = fd.readline()
    return nluts


def gabriel(x, nluts):
    for i in range(3):
        x[2*i+1] += x[2*i]
    y = []
    for i in range(6):
        y.append(nluts[i][x[i]])
    z = []
    for i in range(3):
        z.append(y[(2*i-1) % 6] + y[2*i])
        z.append(y[(2*i+5) % 6] + y[2*i+1])
    for i in range(6):
        z[i] += x[(i+2) % 6]
        z[i] = nluts[i+6][z[i]]
    t = []
    for i in range(2):
        t.append(z[3*i] + z[3*i+1] + z[3*i+2])
        t.append(z[3*i+1] + z[(3*i+4) % 6])
        t.append(z[3*i+2] + z[(3*i+4) % 6] + y[3*i])
    for i in range(6):
        t[i] += x[5-i]
    z = x[6]
    for i in range(6):
        z += nluts[i+12][t[i]]
    return z


def sum_tt(tt1, tt2):
	assert(len(tt1) == len(tt2))
	tt_sum = []
	for (i,j) in zip(tt1, tt2):
		tt_sum.append(i ^^ j)
	return tt_sum


def gabriel_tts(nluts, path="../data/tts"):
    tts = [[] for _ in range(4)]
    for x0 in Z16:
        for x1 in Z16:
            for x2 in Z16:
                for x3 in Z16:
                    for x4 in Z16:
                        for x5 in Z16:
                            v = gabriel([x0, x1, x2, x3, x4, x5, 0], nluts)
                            for i in range(4):
                                tts[i].append(int(v)>>i & 0x1)
    # Lazy and dirty
    for i in range(3):
    	for j in range(i + 1, 4):
    		tts.append(sum_tt(tts[i], tts[j]))
    for i in range(2, 4):
    	tts.append(sum_tt(tts[4], tts[i]))
    for i in range(2):
    	tts.append(sum_tt(tts[9], tts[i]))
    tts.append(sum_tt(tts[10], tts[3]))

    with open(path, 'w') as fd:
        for tt in tts:
            for b in tt:
                fd.write(str(b))
            fd.write('\n')


str_seed = "Welcome to Gabriel"
nb_nluts = 18
generate_nluts(str_seed, nb_nluts)
nluts = load_nluts()
gabriel_tts(nluts)
