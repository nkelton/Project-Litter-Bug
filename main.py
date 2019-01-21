# TODO: refactor for Python3
from LitterBug import LitterBug

if __name__ == '__main__':
    while True:
        try:
            print('attempting to initalize lb')
            lb = LitterBug()
            print('attempting to generate clip')
            lb.generate_clip()
            print('attempting to upload clip')
            lb.upload_clip()

        except Exception as e:
            print(e)
            print('attempting to handle exception')
            lb.exception_handler()

        lb.clean_up()
        del lb
