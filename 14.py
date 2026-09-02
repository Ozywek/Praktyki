def common_elements(list1, list2):
    lista = []
    for i in list1:
        for j in list2:
            if i == j:
                lista.append(i)
    return lista
