import argparse, badsql

def main():
    parser = argparse.ArgumentParser(prog ='gfg',
                                     description ='GfG article demo package.')
  
    parser.add_argument('headers', metavar ='headers', type=list, nargs='*', help ='headers')

    args = parser.parse_args()

    badsql.db(args.headers).display()
