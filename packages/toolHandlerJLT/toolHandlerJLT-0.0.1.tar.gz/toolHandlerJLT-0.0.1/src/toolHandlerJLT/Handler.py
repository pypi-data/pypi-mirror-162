# -*- coding: utf-8 -*-


def _def_shan():
    try:
        with open('./xx/_def_1.txt', 'r', encoding='utf-8') as f:
            a = f.readlines()
        return a
    except Exception as e:
        print(e)
    finally:
        return

def _def_gai():
    try:
        with open('./xx/_def_2.txt', 'r', encoding='utf-8') as f:
            a = f.readlines()
    except Exception as e:
        print(e)
    finally:
        return

def _def_huan():
    try:
        with open('./xx/_def_2.txt', 'r', encoding='utf-8') as f:
            temp = f.readlines()
            a = [temp]
        return a
    except Exception as e:
        print(e)
    finally:
        return

def read_result(ori_=''):
    try:
        with open(ori_, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return lines
    except Exception as e:
        print(e)
    finally:
        return

def rule_(aaa=[]):
    try:
        a = _def_shan()
        b = _def_gai()
        c = _def_huan()

        lines_new = aaa

        for i in range(len(lines_new)):
            line = lines_new[i]
            for it_b in b:
                son = '\t'.join(it_b.split('\t')[0:5])
                if son in line:
                    line_split = line.split('\t')
                    line_split[5] = "-1"
                    lines_new[i] = '\t'.join(line_split)


        for i in range(len(lines_new)):
            line = lines_new[i]
            for it_c in c:
                son_0 = '\t'.join(it_c[0].split('\t')[0:5])
                son_1 = '\t'.join(it_c[1].split('\t')[0:5])

                if son_0 in line:
                    line_split = line.split('\t')
                    line_split[4] = it_c[1].split('\t')[4]
                    lines_new[i] = '\t'.join(line_split)

                if son_1 in line:
                    line_split = line.split('\t')
                    line_split[4] = it_c[0].split('\t')[4]
                    lines_new[i] = '\t'.join(line_split)
                    break

        for i in range(len(lines_new)):
            line = lines_new[i]
            for it_a in a:
                son = '\t'.join(it_a.split('\t')[0:5])
                if son in line:
                    lines_new[i] = '0'
        lines_shan = [it for it in lines_new if it != "0"]
        return lines_shan
    except Exception as e:
        print(e)
    finally:
        return


def echo_(bbb=[]):
    lines = bbb
    try:

        with open('./xx/_def_0.txt', 'r', encoding='utf-8') as f:
            line = f.readline()
            if line:
                eeeid = [int(it.strip()) for it in line.split(',')]
            else:
                eeeid = []

        no_eee_result = []
        eee_result = []
        for line in lines:
            temp = line.split('\t')
            need_line = temp[:6]
            if int(need_line[0]) in eeeid:
                eee_result.append('\t'.join(need_line) + '\n')
            else:
                no_eee_result.append('\t'.join(need_line) + '\n')

        if eee_result:
            no_eee_result.extend(eee_result)
            no_eee_result.extend(eee_result)
            no_eee_result.extend(eee_result)
            return no_eee_result
        else:
            new_result = []
            re_res = []
            for i in no_eee_result:
                if i not in new_result:
                    new_result.append(i)
                else:
                    re_res.append(i)
            new_result.extend(re_res)
            #
            new_result.extend(re_res)
            new_result.extend(re_res)
            new_result.extend(re_res)

            return new_result
    except Exception as e:
        print(e)
    finally:
        return

def sort_(ccc=[]):
    if ccc:
        ccc.sort()
        return ccc
    else:
        return

def _r_start(input=[]):
    if input:
        output = sort_(echo_(rule_(input)))
        return output
    else:
        return


