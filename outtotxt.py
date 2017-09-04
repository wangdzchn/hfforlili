#! /usr/bin/env python
#  _*_ coding: utf-8 _*_
# __author__ = 'wangdz'
# Data: 2017/9/4

import os
import re
from scipy.optimize import leastsq
import numpy as np
import matplotlib.pyplot as plt

file_obj = [name for name in os.listdir('./') if re.findall(r'.out', name)]
for fn in file_obj:
    fn_exdir = os.path.splitext(fn)[0]
    fgin = open(fn, 'r')
    fgout = open(fn_exdir+'.txt', 'w')
    title_hprc = []
    title_tsrt = []
    tbl_hprc = []
    tbl_tsrt = []
    lst_hprc = []
    lst_tsrt = []
    lst_A = ['A:']
    lst_N = ['N:']
    lst_E = ['E:']
    idx_lst = 0
    x_axis = []
    y_axis = []
    flag = False
    while True:
        line = fgin.readline()
        if re.match(r'High Pressure Rate Coefficients \(Temperature-Species Rate Tables\)', line.strip()):
            while True:
                line = fgin.readline()
                if line != '\n':
                    if re.match(r'[T]', line.strip()):
                        title_hprc.append(re.split(r'  +|\n+', line.strip()))
                        if lst_hprc:
                            tbl_hprc.append(lst_hprc)
                            lst_hprc = []
                        continue
                    elif re.match(r'Capture/Escape Rate Coefficients:', line.strip()):
                        if lst_hprc:
                            tbl_hprc.append(lst_hprc)
                            lst_hprc = []
                        break
                    else:
                        lst_hprc.append(re.split(r' +|\n+', re.sub(r'\*+', '-1', line.strip())))

        elif re.match(r'Temperature-Species Rate Tables:', line.strip()):
            while True:
                line = fgin.readline()
                if line != '\n':
                    if re.match(r'[TP]', line.strip()):
                        title_tsrt.append(re.split(r'  +|\n+', line.strip()))
                        if lst_tsrt:
                            tbl_tsrt.append(lst_tsrt)
                            lst_tsrt = []
                        continue
                    elif re.match(r'_+', line.strip()):
                        if lst_tsrt:
                            tbl_tsrt.append(lst_tsrt)
                            lst_tsrt = []
                        break
                    else:
                        lst_tsrt.append(re.split(r' +|\n+', re.sub(r'\*+', '-1', line.strip())))
        if not line:
            break


    # 拟合用函数
    def func(p, t):
        a, e, n = p
        return a*np.power(t, n)*np.exp(-e/t)


    def error(p, t, y):
        return func(p, t) - y


    #  输出函数
    def write_op(title1, content_lst, title2=[]):
        for l in lst_A:
            fgout.write(str(l).ljust(20))
        fgout.write('\n')
        for l in lst_N:
            fgout.write(str(l).ljust(20))
        fgout.write('\n')
        for l in lst_E:
            fgout.write(str(l).ljust(20))
        fgout.write('\n')
        #  判断两类数据决定表头书写的内容
        if not title2:
            for l in title1:
                fgout.write(str(l).ljust(20))
            fgout.write('\n')
        else:
            fgout.write(str(title1[0]) + '\n')
            for l in title2:
                fgout.write(str(l).ljust(20))
            fgout.write('\n')
        for lst1 in content_lst:
            for itm in lst1:
                fgout.write(re.sub('^-1', '***', str(itm)).ljust(20))
            fgout.write('\n')


    def draw_pic():
        plt.scatter(x_axis, y_axis)
        nod = np.linspace(400, 1500)
        plt.plot(nod, func((a, e, n), nod))
        plt.show()


    for lst in tbl_hprc:
        array = np.array(lst, dtype=float)
        for col_idx in range(1, len(lst[0])):
            x_axis = []
            y_axis = []
            for idx in range(len(array)):
                if array[:, col_idx][idx] != -1:
                    x_axis.append(array[:, 0][idx])
                    y_axis.append(array[:, col_idx][idx])
            if len(x_axis) >= 2 and len(y_axis) >= 2:
                p0 = (1, 1, 1)
                para = leastsq(error, p0, args=(x_axis, y_axis))
                a, e, n = para[0]
                # draw_pic()
                # xx = input()
                lst_A.append(a)
                lst_N.append(n)
                lst_E.append(e)
            else:
                lst_A.append('None')
                lst_N.append('None')
                lst_E.append('None')
            x_axis = []
            y_axis = []
        write_op(title_hprc[idx_lst], lst)
        fgout.write('-' * 300 + '\n')
        lst_A = ['A:']
        lst_E = ['E:']
        lst_N = ['N:']
        idx_lst += 1

    idx_lst = 0
    for lst in tbl_tsrt:
        array = np.array(lst, dtype=float)
        for col_idx in range(1, len(lst[0])):
            x_axis = []
            y_axis = []
            for idx in range(len(array)):
                if array[:, col_idx][idx] != -1:
                    x_axis.append(array[:, 0][idx])
                    y_axis.append(array[:, col_idx][idx])
            if len(x_axis) >= 3 and len(y_axis) >= 3:
                try:
                    p0 = (1, 1, 1)
                    para = leastsq(error, p0, args=(x_axis, y_axis))
                    a, e, n = para[0]
                    # draw_pic()
                    lst_A.append(a)
                    lst_N.append(n)
                    lst_E.append(e)
                except BaseException as e:
                    print(e)
                    lst_A.append('wrong')
                    lst_N.append('wrong')
                    lst_E.append('wrong')
                finally:
                    pass
            else:
                lst_A.append('None')
                lst_N.append('None')
                lst_E.append('None')
        write_op(title_tsrt[idx_lst], lst, title_tsrt[idx_lst+1])
        fgout.write('-'*300+'\n')
        lst_A = ['A:']
        lst_E = ['E:']
        lst_N = ['N:']
        idx_lst += 2
    fgin.close()
    fgout.close()
