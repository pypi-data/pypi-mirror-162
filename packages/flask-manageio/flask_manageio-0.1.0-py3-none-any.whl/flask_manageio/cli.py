import os
import sys
import site


def starting_point():
    if len(sys.argv) > 3:
        print('You have specified too many arguments')
        sys.exit()

    if 0 <= 1 < len(sys.argv):
        _command = sys.argv[1]
        if 0 <= 2 < len(sys.argv):
            _project_name = sys.argv[2]
            if _command == 'generate':
                pwd = os.curdir
                path = os.path.join(pwd, _project_name)
                sitePackages = site.getusersitepackages()
                os.mkdir(path)
                os.popen('cp -r ' + sitePackages + '/flask_manageio/project_bed' + '/* ' + path)
                print("Congrats project is done")
                print("cd /" + _project_name)
                sys.exit()
            print("Not known command")
            sys.exit()
        print("Second argument is missing i.e project name")
        sys.exit()
    print("First argument is missing i.e generate")
    sys.exit()


starting_point()
