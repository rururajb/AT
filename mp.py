def f(x):
    return x**2

import multiprocessing

if __name__ == "__main__":
    with multiprocessing.Pool() as pool:
        print(pool.map(f, range(10)))