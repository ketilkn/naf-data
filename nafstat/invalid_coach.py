import logging.config

from pathlib import PosixPath
import nafparser.coach

logging.config.fileConfig('pylogging.conf', disable_existing_loggers=True)
LOG = logging.getLogger(__name__)
logging.getLogger("nafstat.file_loader").setLevel(logging.INFO)


def find_empty(source, parser=nafparser.coach.fromfile):
    LOG.debug("find invalid coaches in %s", source)
    path = PosixPath(source)
    if not path.is_dir():
        LOG.error("No such path %s", path)
        return []
    for f in path.glob("*.html"):
        parse_result = parser(f.as_posix())
        if not parse_result:
            yield(f)


def main():
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument("source", default="data/coach")
    argparser.add_argument("--move",  type=str)
    argparser.add_argument("--print", action="store_true")
    argparser.add_argument("--filename", action="store_true")
    argparser.add_argument("--coach", action="store_true")
    argparser.add_argument("--matches", action="store_true")

    arguments = argparser.parse_args()

    for c in find_empty(arguments.source):
        if arguments.print:
            print(c.as_posix())
        elif arguments.move:
            print("Moving {} to {}".format(c.as_posix(), arguments.target))
            c.rename(arguments.target + "/" + c.name)


if __name__ == "__main__":
    main()
