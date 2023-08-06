import argparse
from fibonacci_cisco.printFibonacci import getFibonacciCisco
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='example')

    parser.add_argument('-n', '--index_of_fib', type=int, help='exporter ips list: "index_of_fib',
                        required=True)

    args= parser.parse_args()
    n = args.index_of_fib
    getFibonacciCisco(n)