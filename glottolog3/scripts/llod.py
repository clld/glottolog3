from clld.scripts.util import parsed_args
from clld.scripts.llod import llod_func, register


if __name__ == '__main__':
    args = parsed_args(bootstrap=True)
    llod_func(args)
    register(args)

