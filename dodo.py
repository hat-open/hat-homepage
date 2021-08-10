from hat.doit import common

DOIT_CONFIG = common.init(default_tasks=['build'])

from src_doit import *  # NOQA
