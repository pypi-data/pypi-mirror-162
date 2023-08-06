class StateMachineIo:
    pass

class Connection:
    def __init__(self, o, t, i):
        self.o = o
        self.t = t
        self.i = i

class StateMachine:
    def __init__(self):
        self.i = StateMachineIo()
        self.n = StateMachineIo()
        self.o = StateMachineIo()
        self.con = []
        def f(_self):
            pass
        self._step = f
    def step(self):
        self._step(self)
    def send(self):
        for con in self.con:
            con.t.i.__dict__[con.i] = self.o.__dict__[con.o]
    def connect(self, _o_name : str, target, _i_name : str):
        self.con.append(Connection(_o_name, target, _i_name))
    def inner(self):
        def deco(f):
            def f2(_self):
                f(_self.i, _self.o)
            self._step = f2
            return f2
        return deco
    def __str__(self):
        return ' '.join([l+':'+(','.join(['{}={}'.format(k,v) for k, v in t.__dict__.items()]) if len(t.__dict__)>0 else 'None')for t,l in [(self.i,'in'),(self.n,'self'),(self.o,'out')]])
            