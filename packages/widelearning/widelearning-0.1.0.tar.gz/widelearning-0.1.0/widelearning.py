
def own_kernel(file_path):	
    f = open(file_path, 'r')
	
    weights = []

    for i in f:
        weights.append(i.strip().split(','))

    for j in weights:
        j.pop()

    for ii in weights:
        for i1, elem in enumerate(ii):
            ii[i1] = [[int(elem)]]

    return weights 

