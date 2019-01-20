# TODO: refactor for Python3
from LitterBug import LitterBug

if __name__ == '__main__':
    while True:
        try:
            lb = LitterBug()
            lb.generate_clip()
            lb.upload_clip()

        except Exception as e:
            print e
            lb.exception_handler()

        lb.clean_up()
        del lb
