import argparse, badsql

def mkdb():
    parser = argparse.ArgumentParser(prog ='badsql',
                                     description ='badsql mkdb')
  
    parser.add_argument('headers', metavar ='headers', type=list, nargs='*', help ='headers')

    args = parser.parse_args()

    db = badsql.db([''.join([str(x) for x in y]) for y in args.headers])
    db.display()
    db.save('test')

def insertrow():
    parser = argparse.ArgumentParser(prog ='badsql',
                                     description ='badsql insertrow')

    parser.add_argument('pos', metavar ='pos', type=int, nargs=1, help= 'pos')
  
    parser.add_argument('values', metavar ='values', type=list, nargs='*', help ='values')

    args = parser.parse_args()

    try:
        db = badsql.load('test')
        db.insert(args.pos, [''.join([str(x) for x in y]) for y in args.values])
        db.display()
        db.save('test')
    except:
        print('Error occurred')

