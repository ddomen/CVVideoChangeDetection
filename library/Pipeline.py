import inspect

class Pipeline:
    def __init__(self, *functions):
        self.functions = []
        if len(functions) > 0: self.add(*functions)

    def __getitem__(self, index): return Pipeline(self.functions[index])
    
    def __call__(self, image, *args, **kwargs): return self.apply(image, *args, **kwargs)

    def __applyFunction(self, function, original, progress, *args, **kwargs):
        params = inspect.signature(function).parameters
        accVarPos = False
        accVarKW = False
        nParams = 0
        for p in params.values():
            if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD: nParams += 1
            else:
                accVarPos = accVarPos or p.kind == inspect.Parameter.VAR_POSITIONAL
                accVarKW = accVarKW or p.kind == inspect.Parameter.VAR_KEYWORD
        if nParams == 0:
            if accVarPos and accVarKW: return function(progress, original, *args, **kwargs)
            elif accVarPos: return function(progress, original, *args)
            elif accVarKW: return function({ 'original':original, 'progress':progress, **kwargs })
            return function()
        elif nParams == 1:
            if accVarPos and accVarKW: return function(progress, original, *args, **kwargs)
            elif accVarPos: return function(progress, original, *args)
            elif accVarKW: return function(progress, { 'original':original, **kwargs })
            return function(progress)
        else:
            if accVarPos and accVarKW: return function(progress, original, *args, **kwargs)
            elif accVarPos: return function(progress, orignal, *args)
            elif accVarKW: return function(progress, orignal, **kwargs)
            return function(progress, original, *[*args[:nParams-2]])
        return progress


    def add(self, *functions):
        for function in functions:
            if isinstance(function, list) or isinstance(function, tuple): self.add(*function)
            elif callable(function):self.functions.append(function)
        return self

    def apply(self, image, *args, **kwargs):
        progress = image.copy()
        for function in self.functions:
            progress = self.__applyFunction(function, image, progress, *args, **kwargs)
        return progress