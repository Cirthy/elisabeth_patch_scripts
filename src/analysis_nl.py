from sage.crypto.boolean_function import BooleanFunction
import gc
import pickle


def one_depth_sub_tts(tt, current_index = 0):
    n = log(len(tt), 2)
    for i in range(current_index, n):
        stt1 = []
        stt2 = []
        for j in range(1<<i):
            stt1 += tt[(2 * j) * 1<<(n - i - 1) : (2 * j + 1) * 1<<(n - i - 1)]
            stt2 += tt[(2 * j + 1) * 1<<(n - i - 1) : 2 * (j + 1) * 1<<(n - i - 1)]
        yield stt1
        yield stt2
    gc.collect()
        

def sub_tts_generator(tt, depth, current_index = 0):
    assert(depth > 0)
    if current_index > log(len(tt), 2) - depth:
        pass
    elif depth == 1:
        for stts in one_depth_sub_tts(tt, current_index):
            yield stts
    else:
        index_tracker = 2 * current_index
        for stts in one_depth_sub_tts(tt, current_index):
            for sstts in sub_tts_generator(stts, depth - 1, index_tracker // 2):
                yield sstts
            index_tracker += 1


def nl_subfonctions(tt):
	nl_subfonctions = [[] for _ in range(3)]
	f = BooleanFunction(tt)
	nl_subfonctions[0].append(f.nonlinearity())
	for stt in sub_tts_generator(tt, 1):
		sub_f = BooleanFunction(stt)
		nl_subfonctions[1].append(sub_f.nonlinearity())
	for stt in sub_tts_generator(tt, 2):
		sub_f = BooleanFunction(stt)
		nl_subfonctions[2].append(sub_f.nonlinearity())
	print(min(nl_subfonctions[0]), min(nl_subfonctions[1]), min(nl_subfonctions[2]))
	return nl_subfonctions


def analysis_nl(path_tt="../data/tts", path_results='../data/results_nl'):
	results = []
	with open(path_tt, 'r') as fd:
		line = fd.readline()
		cnt = 1
		while(line):
			tt = [int(c) for c in line[:-1]]
			print(cnt)
			cnt += 1
			results.append(nl_subfonctions(tt))
			line = fd.readline()
	with open(path_results, 'wb') as fd:
		pickle.dump(results, fd)


# analysis_nl(path_tt="../data/margrethe/tts", path_results='../data/margrethe/results_nl')
