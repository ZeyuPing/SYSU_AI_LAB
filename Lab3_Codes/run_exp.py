from PC_resolution import PC_resolution
from FOL_resolution import FOL_resolution
from MGU import MGU

if __name__ == '__main__':
    experiment_id = input("Which experiment do you want to run? \n"
    "Experiment 1: Propositional calculus\n"
    "Experiment 2: First-order logic\n"
    "Experiment 3: Most general unifier\n"
    "Please input the number of the experiment or type \"all\" for all: ")

    if experiment_id == '1' or experiment_id == 'all':
        KB = "{(FirstGrade,),(~FirstGrade,Child),(~Child,)}" # Knowledge base
        print("test1 KB: ", KB, "\n")
        output = PC_resolution(KB) # output is a list[str]

        for step in output:
            print(step)
        print("\n")

    if experiment_id == '2' or experiment_id == 'all':
        KB = "{(GradStudent(sue),),(~GradStudent(x),Student(x)),(~Student(x),HardWorker(x)),(~HardWorker(sue),)}" # Knowledge base
        print("test1 KB: ", KB, "\n")
        output = FOL_resolution(KB)
        
        for step in output:
            print(step)
        print("\n")

        KB = "{(A(tony),),(A(mike),),(A(john),),(L(tony,rain),),(L(tony,snow),),(~A(x),S(x),C(x)),(~C(y),~L(y,rain)),(L(z,snow),~S(z)),(~L(tony,uu),~L(mike,uu)),(L(tony,vv),L(mike,vv)),(~A(ww),~C(ww),S(ww))}"
        print("test2 KB: ", KB, "\n")
        output = FOL_resolution(KB)

        for step in output:
            print(step)
        print("\n")

        KB = "{(On(tony,mike),),(On(mike,john),),(Green(tony),),(~Green(john),),(~On(xx,yy),~Green(xx),Green(yy))}"
        print("test3 KB: ", KB, "\n")
        output = FOL_resolution(KB)

        for step in output:
            print(step)
        print("\n")

    if experiment_id == '3' or experiment_id == 'all':
        literal1 = "P(xx,a)"
        literal2 = "P(b,yy)"
        print("test literals: ", literal1, "and ", literal2)
        output = MGU(literal1, literal2)
        print(output, "\n")

        literal1 = "P(a,xx,f(g(yy)))"
        literal2 = "P(zz,f(zz),f(uu))"
        print("test literals: ", literal1, "and ", literal2)
        output = MGU(literal1, literal2)
        print(output, "\n")

        literal1 = "P(ab,cd)"
        literal2 = "P(ab,cd)"
        print("test literals: ", literal1, "and ", literal2)
        output = MGU(literal1, literal2)
        print(output, "\n")

        literal1 = "P(x,y)"
        literal2 = "P(a,b)"
        print("test literals: ", literal1, "and ", literal2)
        output = MGU(literal1, literal2)
        print(output, "\n")
