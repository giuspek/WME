#!/usr/bin/env python3

import argparse
import signal
import sys
from pysat.examples.rc2 import RC2Stratified, RC2
from pysat.formula import WCNF

TIMED_OUT = False

def _handle_timeout(signum, frame):
    global TIMED_OUT
    TIMED_OUT = True
    raise TimeoutError("global timeout reached")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_wcnf", help="Input WCNF file")
    parser.add_argument("--k", type=int, default=50, help="Maximum number of models")
    parser.add_argument("--timeout", type=int, default=600, help="Global timeout in seconds")
    parser.add_argument("--blo", default="div", choices=["basic", "div", "cluster", "full"],
                        help="BLO/stratification mode for RC2Stratified")
    args = parser.parse_args()

    try:
        wcnf = WCNF(from_file=args.input_wcnf)
    except Exception as e:
        print(f"Error while reading WCNF file '{args.input_wcnf}': {e}", flush=True)
        sys.exit(1)

    signal.signal(signal.SIGALRM, _handle_timeout)
    signal.alarm(args.timeout)

    count = 0
    seen = set()

    try:
        with RC2(
            wcnf,
            process=0,
            adapt=True,
            exhaust=True,
            incr=True,
            minz=True,
            trim=0
        ) as rc2:
            for i, model in enumerate(rc2.enumerate(), 1):
                filtered = [lit for lit in model if abs(lit) <= wcnf.nv]
                filtered.sort(key=lambda x: abs(x))
                print(f"{i}: cost={rc2.cost} model={filtered}")
                if i >= args.k:
                    break

        print(f"c MODEL_COUNT {count}", flush=True)
        print("c TIMEOUT 0", flush=True)

    except TimeoutError:
        print(f"c MODEL_COUNT {count}", flush=True)
        print("c TIMEOUT 1", flush=True)
        sys.exit(124)

    except KeyboardInterrupt:
        print(f"c MODEL_COUNT {count}", flush=True)
        print("c TIMEOUT 1", flush=True)
        sys.exit(124)

    except Exception as e:
        print(f"Error while solving '{args.input_wcnf}': {e}", flush=True)
        print(f"c MODEL_COUNT {count}", flush=True)
        print(f"c TIMEOUT {1 if TIMED_OUT else 0}", flush=True)
        sys.exit(1)

    finally:
        signal.alarm(0)

if __name__ == "__main__":
    main()