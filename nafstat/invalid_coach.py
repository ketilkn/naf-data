import logging.config

logging.config.fileConfig('pylogging.conf', disable_existing_loggers=True)
LOG = logging.getLogger(__name__)
logging.getLogger("nafstat.file_loader").setLevel(logging.INFO)

from pathlib import PosixPath

from nafstat.tournament import parse_coach

def find_empty(source):
    LOG.debug("find invalid coaches in %s", source)
    path = PosixPath(source)
    if not path.is_dir():
        LOG.error("No such path %s", path)
        return []
    for f in path.glob("*.html"):
        parse_result = parse_coach.fromfile(f.as_posix())
        if not parse_result:
            yield(f)




def main():
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument("source", default="data/")
    argparser.add_argument("target", default="data/")
    argparser.add_argument("--filename", action="store_true")
 
    arguments = argparser.parse_args()

    for c in find_empty(arguments.source):
        print("Moving {} to {}".format(c.as_posix(), arguments.target))
        c.rename(arguments.target + "/" + c.name)



if __name__ == "__main__":
    main()
