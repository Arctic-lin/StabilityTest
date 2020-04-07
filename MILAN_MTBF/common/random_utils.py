import random

from common import logger


def random_name(index_num):
    numseed = "0123456789"
    sa = []
    for i in range(5):
        sa.append(random.choice(numseed))
    stamp = ''.join(sa)
    strname = 'Auto%02d_' % (index_num + 1) + stamp
    logger.debug('Create a random name %s.' % strname)
    return strname