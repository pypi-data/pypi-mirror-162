import json
#SwitchTools by Отчим Анала#6840

class Case:
    def __init__(self,Value,LambdaFunc,LambdaArgs=None):
        if not LambdaArgs:
            LambdaArgs = []
        self.Value = Value
        self.LambdaFunc = LambdaFunc
        self.LambdaArgs = LambdaArgs
class Switch:
    def __init__(self,Value,Cases : list) -> Case:
        DefaultCase = None
        SkipVars = ['int','str','float','bool','long']
        self.Cases = Cases
        val = Value
        if not type(val).__name__ in SkipVars:
            val = json.dumps(val.__dict__)
        self.Value = val
        for i in Cases:
            
            CaseValue = i.Value
            if not type(i.Value).__name__ in SkipVars:
                CaseValue = json.dumps(i.Value.__dict__)
            else:
                if i.Value == "default":
                    DefaultCase = i
            if CaseValue == self.Value:
                if not i.LambdaArgs:
                    i.LambdaFunc()
                if i.LambdaArgs:
                    i.LambdaFunc(*i.LambdaArgs)
                return
        if DefaultCase.LambdaArgs:
            DefaultCase.LambdaFunc(*i.LambdaArgs)
        else:
            DefaultCase.LambdaFunc()