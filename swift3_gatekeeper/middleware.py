import re

from swift.common.utils import get_logger
from swift.common.swob import Request
from swift.common.request_helpers import remove_items

inbound_exclusions = ['x-object-meta-s3-', 'x-amz-meta-s3-']
outbound_exclusions = ['x-amz-meta-s3-', 'x-amz-meta-glacier',
                       'x-lifecycle-response']
outbound_replaces = ['x-amz-meta-s3-restore']


def make_exclusion_test(exclusions):
    expr = '|'.join(exclusions)
    test = re.compile(expr, re.IGNORECASE)
    return test.match


def replace_items(headers):
    replaced = {}
    keys = {}
    for h in headers:
        key = h[0]
        if key.lower() not in outbound_replaces:
            continue
        keys[key] = headers.index(h)

    for key, i in keys.iteritems():
        item = headers[i]
        new_key = 'x-amz-%s' % key.split('-')[-1]
        headers[i] = (new_key, item[1])
        replaced[key] = item[0]
    return replaced


class Swift3GateKeeperMiddleware(object):
    def __init__(self, app, conf, *args, **kwargs):
        self.app = app
        self.conf = conf
        self.logger = get_logger(self.conf, log_route='swift3-gatekeeper')
        self.inbound_condition = make_exclusion_test(inbound_exclusions)
        self.outbound_condition = make_exclusion_test(outbound_exclusions)

    def __call__(self, env, start_response):
        req = Request(env)
        removed = remove_items(req.headers, self.inbound_condition)
        if removed:
            self.logger.debug('removed request s3 headers: %s' % removed)

        def gatekeeper_response(status, response_headers, exc_info=None):
            replaced = replace_items(response_headers)
            if replaced:
                self.logger.debug('replaced response s3 headers: %s' %
                                  replaced)
            removed = filter(
                lambda h: self.outbound_condition(h[0]),
                response_headers)
            if removed:
                self.logger.debug('removed response s3 headers: %s' % removed)
                new_headers = filter(
                    lambda h: not self.outbound_condition(h[0]),
                    response_headers)
                return start_response(status, new_headers, exc_info)
            return start_response(status, response_headers, exc_info)
        return self.app(env, gatekeeper_response)


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def swift3_gatekeeper_filter(app):
        return Swift3GateKeeperMiddleware(app, conf)

    return swift3_gatekeeper_filter