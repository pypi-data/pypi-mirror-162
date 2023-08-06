import os

from b_cfn_opensearch_index_tests.integration.manager import MANAGER

DO_NOT_DESTROY_INFRASTRUCTURE = int(os.environ.get('DO_NOT_DESTROY_INFRASTRUCTURE', 0))


def inf_destroy():
    if DO_NOT_DESTROY_INFRASTRUCTURE == 1:
        return

    MANAGER.destroy_infrastructure()


if __name__ == '__main__':
    inf_destroy()
