import utils
import settings
import IPython
import sys


def main(fname):
    data, md = utils.load(settings.DATA_DIR / fname)
    print("Current settings: {}".format(md))
    print("Opened file. Edit parameter 'x' by doing md['x'] = y.")
    print("^D when finished")
    print("Starting console...\n")
    IPython.embed()

    utils.save(settings.DATA_DIR / fname, data, md)
    print("Saved changes. Exiting...")

if __name__ == "__main__":
    main(sys.argv[1])