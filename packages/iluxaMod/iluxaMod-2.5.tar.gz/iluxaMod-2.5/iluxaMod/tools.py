class pickle:
    def __init__(self, filename):
        self.filename = filename


    def pick(self, data):
        import pickle
        '''Save data to pickle-file'''
        with open(self.filename, 'wb') as f:
            pickle.dump(data, f)

    def unpick(self):
        import pickle
        '''Unpack pickle-file'''
        with open(self.filename, 'rb') as f:
            return pickle.load(f)


def str_to_time(string):
    import datetime
    '''
    Convert string to time-type
    '''
    return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')