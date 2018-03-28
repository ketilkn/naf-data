#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import requests
import time
import logging
import humanfriendly

LOG = logging.getLogger(__package__)


def throttle_by_request_time(fun, *args):
    def throttle_decorator(*args):
        do_throttle = "--throttle" in sys.argv or "--no-throttle" not in sys.argv
        start_time = time.time()
        result = fun(*args)
        request_time = time.time()-start_time

        if do_throttle:
            LOG.debug("Waiting %s after %s", humanfriendly.format_timespan(request_time), fun.__name__)
            time.sleep(request_time)
        else:
            LOG.debug("Throttle is False")
        return result

    return throttle_decorator


def download_to(session, url, target):
    response = session.get(url)
    if not response.history and response.status_code == 200:
        html = response.text
        try:
            open(target, "w").write(html)
            LOG.debug(" Wrote {} to {}".format(url, target))
            return True
        except OSError:
            LOG.error(" Failed writing {} to {}".format(url, target))
    else:
        LOG.warning(" Server error {} to {}".format(url, response.status_code))
    return False


def verify_session(session, response = None):
    #TODO check if session is logged in
    return response.status_code == 200


def login(url, username, password):
    s = requests.session()
    r = s.post(url, data={"user":username, "pass":password})

    if verify_session(s,r):
        return s
    #FIXME Throw exception ? / return None?
    print("Could not verify session")
    sys.exit("Could not verify session")


def new_session():
    return requests.session()


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)


if __name__ == "__main__":
    main()