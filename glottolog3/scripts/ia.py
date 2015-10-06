from clld.scripts.util import parsed_args
from clld.scripts.internetarchive import ia_func


if __name__ == '__main__':
    ia_func('update', parsed_args(bootstrap=True))
