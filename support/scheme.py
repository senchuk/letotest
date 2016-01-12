# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Скрипт подмены схемы запуска автотестов
#--------------------------------------------------------------------
import sys
import re

priority_list = [
    'must',
    'high',
    'medium',
    'low',
    'none'
]

browser_list = [
    'chrome',
    'firefox',
]

__author__ = 'senchuk'

if __name__ == '__main__':
    name_main_cfg = "main.cfg"
    name_env_cfg = "env.cfg"
    print "\n<<---== Start installation scheme. ==--->>\n"
    if len(sys.argv) > 1:
        print "  Name scheme for start autotests: %s" % str(sys.argv[1])
        f_env = open(name_env_cfg, 'r')
        p = f_env.read()
        match = re.findall("\[" + str(sys.argv[1]) + "\]", p)
        f_env.close()
        if len(match) != 0:
            if len(match) > 2:
                print "  Warning: Find several scheme with this name for start autotest! Installed last found scheme."
            elif len(match) == 1:
                print "  Scheme [%s] found! Success." % str(sys.argv[1])
            f_main = open(name_main_cfg, 'r')
            pp = f_main.readlines()
            num_env = 0
            num_pr = 0
            num_br = 0
            # ищем нужную строку и заменяем её
            for num, index in enumerate(pp):
                m = re.match("^env=", index)
                n = re.match("^priority=", index)
                k = re.match("^browser=", index)
                if m is not None:
                    num_env = num
                elif n is not None:
                    num_pr = num
                elif k is not None:
                    num_br = num
                if (num_env != 0) and (num_pr != 0) and (num_br != 0):
                    break
            f_main.close()
            pp[num_env] = ("env=%s\n" % str(sys.argv[1]))
            if len(sys.argv) > 2:
                if sys.argv[2].lower() in priority_list:
                    print "  Priority for start auto-tests: [%s]" % str(sys.argv[2]).upper()
                    pp[num_pr] = ("priority=%s\n" % str(sys.argv[2]))
                    if len(sys.argv) > 3:
                        if sys.argv[3].lower() in browser_list:
                            print "  Browser for start auto-tests: [%s]" % str(sys.argv[3]).upper()
                            pp[num_br] = ("browser=%s\n" % str(sys.argv[3]))
                elif sys.argv[2].lower() in browser_list:
                    print "  Browser for start auto-tests: [%s]" % str(sys.argv[2]).upper()
                    pp[num_br] = ("browser=%s\n" % str(sys.argv[2]))
                    if len(sys.argv) > 3:
                        if sys.argv[3].lower() in priority_list:
                            print "  Priority for start auto-tests: [%s]" % str(sys.argv[3]).upper()
                            pp[num_pr] = ("priority=%s\n" % str(sys.argv[3]))
            # открываем файл для записи данных с измененной схемой запуска автотестов
            f_main_w = open(name_main_cfg, 'w')
            f_main_w.writelines(pp)
            f_main_w.close()
            print "  Scheme run tests changed! Success."
        else:
            print "  Warning: Not found scheme [%s]. Installed default settings." % str(sys.argv[1])
    else:
        print "  A schema is not specified. To ignore change settings."
    print "\n<<---== Installation of completed schemes. ==--->>\n"
