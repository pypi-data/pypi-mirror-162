from my_state_machine import StateMachine

a1 = StateMachine()

a1.i.D1 = 0
a1.o.Q1 = 0

@a1.inner()
def a1_step(i, o):
    o.Q1 = 1 - i.D1

a1.connect('Q1', a1, 'D1')

for i in range(10):
    a1.step()
    a1.send()
    print(a1)