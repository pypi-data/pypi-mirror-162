from .machine import StateMachine, StateMachineIo

def gen_states(s : StateMachineIo):
    states = []
    keys = list(s.__dict__.keys())
    if len(keys)>0:
        states = [[v] for v in s.__dict__[keys[0]]]
        if len(keys)>1:
            for k in keys[1:]:
                new_states = []
                for i in states:
                    for j in s.__dict__[k]:
                        new_states.append(i+[j])
                states = new_states        
    states = [tuple(item) for item in states]
    back = {}
    for i in range(len(states)):
        back[states[i]]=i
    return states, keys, back

class TestResult:
    def __init__(self,k1,k2,k3,data,states):
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3
        self.data = data
        self.states = states

def test_machine(machine : StateMachine, i : StateMachineIo, s : StateMachineIo):
    inputs, i_keys, i_dict = gen_states(i)
    states, s_keys, s_dict = gen_states(s)
    
    o_keys = machine.o.__dict__.keys()

    data = []
    for i in range(len(states)):
        for j in range(len(inputs)):
            m = StateMachine()
            for k in range(len(s_keys)):
                m.s.__dict__[s_keys[k]] = states[i][k]
            for k in range(len(i_keys)):
                m.i.__dict__[i_keys[k]] = inputs[j][k]
            for k, v in machine.o.__dict__.items():
                m.o.__dict__[k] = v
            machine._step(m)
            res_s = tuple([m.s.__dict__[k] for k in s_keys])
            res_o = tuple([m.o.__dict__[k] for k in o_keys])
            data.append([s_dict[states[i]],inputs[j],s_dict[res_s], res_o])

    return TestResult(i_keys, s_keys, o_keys, data, states)
    