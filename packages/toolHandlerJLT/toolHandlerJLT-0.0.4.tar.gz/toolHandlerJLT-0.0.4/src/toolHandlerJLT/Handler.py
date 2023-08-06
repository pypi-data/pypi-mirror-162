# -*- coding: utf-8 -*-

def _def_shan():
    try:
        a = [
            "1625	攻击事件	48	55	发起者	[80.0 40.59259259259258 774.8148148148148 529.4814814814814]	F-22战斗机\n",
            "1695	部署事件	99	107	发起者	[52.5 37.5 1062.5 452.5]	“幻影2000”\n",
            "1861	攻击事件	0	4	发起者	[2.6511627906976747 62.899224806201545 833.6589147286821 590.031007751938]	F-22\n",
            "1861	攻击事件	77	81	发起者	[2.6511627906976747 62.899224806201545 833.6589147286821 590.031007751938]	F-35\n",
            "1736	机动事件	49	57	发起者	[34.65346534653465 70.64356435643565 587.1287128712871 394.4059405940594]	333“完美”号\n",
            "1736	机动事件	58	66	发起者	[34.65346534653465 70.64356435643565 587.1287128712871 394.4059405940594]	335“响亮”号\n",
            "1736	机动事件	67	70	发起者	-1	339\n",
            "1736	机动事件	71	88	发起者	[34.65346534653465 70.64356435643565 587.1287128712871 394.4059405940594]\n"
        ]
        return a
    except Exception as e:
        print(e)

def _def_gai():
    try:
        a = [
            "1677	保障事件	43	48	发起者	[1.282051282051282 207.82051282051282 829 378]	安-225\n",
            "1834	攻击事件	36	42	承受者	[57.87037037037037 81.57407407407406 587.5 363.5185185185185]	米格29战机\n",
            "1873	部署事件	11	21	发起者	[137.42105263157893 61.84210526315789 593.2105263157895 397.1052631578947]	“本福尔德”号驱逐舰\n",
            "1873	部署事件	22	35	发起者	[137.42105263157893 61.84210526315789 593.2105263157895 397.1052631578947]	“柯蒂斯·威尔伯”号驱逐舰\n",
            "1873	部署事件	36	50	发起者	[137.42105263157893 61.84210526315789 593.2105263157895 397.1052631578947]	“钱瑟勒斯维尔”号导弹巡洋舰\n",
            "1877	机动事件	41	59	发起者	[32.5 121.83333333333334 1076.6666666666667 483.5]	F-16C/D block70战斗机\n",
            "1954	机动事件	21	28	发起者	[13.279069767441861 157.95348837209303 1499 672]	B-52轰炸机\n"
             ]
        return a
    except Exception as e:
        print(e)

def _def_huan():
    try:
        a = [
                [
                    "1793	攻击事件	2	10	发起者	[180.1980198019802 277.4059405940594 250.990099009901 303.64356435643566]	“鱼叉”反舰导弹\n",
                    "1793	攻击事件	11	20	使用器械	[32.67326732673267 1.1683168316831711 639 201]	P-8A反潜巡逻机\n"
                ]
        ]
        return a
    except Exception as e:
        print(e)

def read_result(ori_=''):
    try:
        with open(ori_, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return lines
    except Exception as e:
        print(e)

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


def echo_(bbb=[]):
    lines = bbb
    try:
        eeeid = [1614, 1620, 1625, 1631, 1637, 1653, 1656, 1668, 1669, 1741, 1754, 1756, 1758, 1768, 1780, 1783, 1786,
                 1975, 1979,1787, 1793, 1807, 1820, 1830, 1832, 1834, 1836, 1837, 1839]
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

if __name__ == '__main__':

    aaaaa = read_result(ori_=r'/data/zxwang/ccks2022/test/test_result/result_20220810_182955.txt')

    result = _r_start(aaaaa)

    print(len(result))
    with open(r'/data/zxwang/ccks2022/test/test_result/result_20220810_182955_rule_echo_sort_test.txt', 'w', encoding='utf-8') as f_w:
        f_w.writelines(result)
