import re

class juliaModel():
    '''Converts an .net file into a string in julia ODE function format'''
    def __init__(self, netFile, modelName, model, obj, config):
        ## Load in the model
        self.config = config
        self.model = netFile
        # I don't think I ended up using this but it may be helpful
        self.modelText = model
        self.modelN = modelName
        self.objFunc = obj
        self.keywords = {'parameters':0, 'species':1, 'groups':2, 'reactions':3, 'functions':4}
        self.begin = 'begin '
        self.end = 'end '
    def extract(self, keyword):
        '''A function to seperate parameters from values where a parameter is a reaction or a variable'''
        block = (self.begin + keyword, self.end + keyword) 
        begin = self.model.find(block[0])
        end = self.model.find(block[1])
        if begin == -1:
            return {}
        else:
            begin = self.model.find(block[0]) + len(block[0])
            values = self.model[begin:end].strip().splitlines()
            dictValues = {}
            for v in values:
                v = v.strip().split()
                if len(v) > 2:
                    if keyword == 'parameters':
                        if v[2][-6:] == '__FREE':
                            dictValues[v[2]] = [v[2], 'p["' + v[2] + '"]']
                        elif v[1][-6:] == '__FREE':
                            dictValues[v[1]] = [v[1], 'p["' + v[1] + '"]']
                        if v[1][-6:] != '__FREE': 
                            dictValues[v[0]] = v[1:]
                    elif keyword == 'groups':
                        gList = []
                        for i in v[-1].split(','):
                            gList.append('u['+i+']')
                        newV = '+'.join(gList)
                        v.append(newV)
                        dictValues[v[0]] = [v[1],v[3]] 
                    else:
                        dictValues[v[0]] = v[1:]
                else:
                    dictValues[v[0]] = [v[1],'0']
            return dictValues
    def parseReactions(self):
        '''A function to parse the reactions block of the .net file to create the ODEs contained in the reaction block'''
        dictSpecies = self.extract('species')
        for k,v in dictSpecies.items():
            v.append('u['+k+']')     
        dictReactions = self.extract('reactions')
        tempListEq = []
        listEq = []
        finalEq = []
        listEq1 = []
        listEqNames = []
        listODEs = []
        ## extract the ODEs from the reactions and represent in a list
        for groupKeys, groupVals in dictSpecies.items():
            for reaction in dictReactions.values():
                reactants = reaction[0].split(',')
                products = reaction[1].split(',')
                rateLaw = reaction[2]
                for reactant in reactants:
                    if reactant == '0' and groupKeys == reactant:
                        tempListEq.append('\bdu[' + groupKeys + '] = ')
                        tempListEq.append('(0*')            
                        tempListEq.append('(' + rateLaw + '))')
                        tempListEq.append('\n')
                        listEq.append(tempListEq)
                        break
                    else:
                        if groupKeys == reactant:
                            tempListEq.append('du[' + groupKeys + '] = ')
                            tempListEq.append('(-1 *')            
                            tempListEq.append(reactants)
                            tempListEq.append('(' + rateLaw + '))')
                            tempListEq.append('\n')
                            listEq.append(tempListEq)
                            break
                for product in products:
                    if reactant == '0' and groupKeys == product:
                        tempListEq.append('du[' + groupKeys + ']=')
                        tempListEq.append('(')            
                        tempListEq.append('(' + rateLaw + '))')
                        tempListEq.append('\n')
                        listEq.append(tempListEq)
                        break  
                    elif product == '0' and groupKeys == product:
                        tempListEq.append('du[' + groupKeys + '] = ')
                        tempListEq.append('(')            
                        tempListEq.append('(' + 0 + '))')
                        tempListEq.append('\n')
                        listEq.append(tempListEq)
                        break  
                    else:
                        if groupKeys == product:
                            tempListEq.append('du[' + groupKeys + '] = ')
                            tempListEq.append('(')
                            tempListEq.append(reactants)
                            tempListEq.append('(' + rateLaw + '))')
                            listEq.append(tempListEq)
                            tempListEq.append('\n')
                            break
                tempListEq = []
        finalEq = []
        ## Convert any numbers to their species
        for outterList in listEq:
            for keyNames in outterList:
                if type(keyNames) == list:
                    for names in keyNames:
                        finalEq.append(dictSpecies[names][2] + ' * ')
                else:
                    finalEq.append(keyNames)
        stringOfEq = ' '.join(finalEq)
        newStringEq = stringOfEq.strip().split('\n')
        listEq1 = []
        listEqNames = []
        ## create the equations
        for i in newStringEq:
            i = i.strip()
            i = i.split('=')
            listEq1.append(i)
            listEqNames.append(i[0])
        listODEs = []
        for u in listEq1:
            if u[0] in listEqNames:
                if u[0] in listODEs:
                    listODEs.append('+' + u[1])
                else:
                    listODEs.append('\n')
                    listODEs.append(u[0])
                    listODEs.append('=')
                    listODEs.append(u[1])
        stringODEs = ''.join(listODEs)
        return stringODEs
    def compileModel(self):
        '''A function to assemble the various strings into a julia ODE model/function format'''
        species = self.extract('species')
        functions = '\n'.join([v[0]+'='+v[1] for k,v in self.extract('functions').items()]).replace('()','').replace('if(', 'ifelse(')
        groups = '\n'.join([v[0]+'='+v[1] for k,v in self.extract('groups').items()])
        params = '\n'.join([v[0]+'='+v[1] for k,v in self.extract('parameters').items()])
        ODE = self.parseReactions()
        start = f'function {self.modelN}!(du,u,p,t)'
        output = 'return ' + ','.join(['du['+str(i+1)+']' for i in range(len(species))])
        end = 'end'
        model = '\n'.join([start, groups, params, functions, ODE, output])
        model = model.split("\n")
        model = '\n'.join([line for line in model if line.strip() != ""])
        indentModel = model.replace('\n', '\n\t')
        finalModel = '\n'.join([indentModel, end])
        return finalModel
    def compileCallBack(self):
        '''A function to assemble the various strings into a julia ODE model/function format'''
        functions = '\n'.join([v[0]+'='+v[1] for k,v in self.extract('functions').items()]).replace('()','').replace('if(', 'ifelse(')
        groups = '\n'.join([v[0]+'='+v[1] for k,v in self.extract('groups').items()])
        params = '\n'.join([v[0]+'=integrator.'+v[1] if v[1][-8:] == '__FREE"]' else v[0]+'='+v[1]\
                            for k,v in self.extract('parameters').items()])
        start = f'function call{self.modelN}(u,t,integrator)'
        output = 'return [' + ','.join([v[0] for v in self.extract('groups').values()])+ ', ' + ','.join([v[0] for k,v in self.extract('functions').items()]).replace('()','')+']'
        end = 'end'
        model = '\n'.join([start, groups, params, functions,output])
        model = model.split("\n")
        model = '\n'.join([line for line in model if line.strip() != ""])
        indentModel = model.replace('\n', '\n\t')
        callModel = '\n'.join([indentModel, end])   
        return callModel
    
    def state(self):
        species = '\n'.join(['species__'+k +'='+v[1] for k,v in self.extract('species').items()]).replace('()','')
        params = '\n'.join([v[0]+'=pset'+v[1][1:] if v[1][-8:] == '__FREE"]' else v[0]+'='+v[1]\
                            for k,v in self.extract('parameters').items()])
        start = f'function state{self.modelN}(pset)'
        end = 'end'
        output = 'return float([' + ','.join(['species__'+k for k,v in self.extract('species').items()]).replace('()','')+'])'
        strState = '\n'.join([start, params, species, output])
        indentModel = strState.replace('\n', '\n\t')
        state = '\n'.join([indentModel, end])
        return state
    def strOutput(self):
        model = self.compileModel()
        cb = self.compileCallBack()
        inital= self.state()
        out = '\n'.join([inital,model,cb])
        return out
    def speciesCols(self):
        groups = ','.join(['"' + v[0]+'"=>'+str(i+2) for i,v in enumerate(self.extract('groups').values())])
        numGroups = len(self.extract('groups').values())
        functions = ','.join(['"' + v[0] +'"'+'=>'+str(numGroups + i + 2) for i,v in enumerate(self.extract('functions').values())]).replace('()','').replace('if(', 'ifelse(')
        speciesDict = f'Dict("time"=>1,{groups},{functions})'
        return speciesDict
    def paramCols(self):
        params = {v[0].replace('()', ''):i+1  for i,v in enumerate(self.extract('parameters').values())}
        return params
    def juliaODE(self):
        start = re.search('begin actions', self.modelText)
        end = re.search('end actions', self.modelText)
        if start == None and end == None:
            endStr = len('end')
            start = self.modelText.rfind('end ')
            newStr = self.modelText[start:]
            newStrNewLine = newStr.find('\n')
            modelText = newStr[newStrNewLine:]
            s = 0
            e = -1
        else:
            s = start.span()[1]
            e = end.span()[0]
        actList = self.modelText[s:e].strip().split('\n')
        strActions = []
        strSolve = []
        strCommands = []
        newActList = []
        newActListCommands = []
        concList = []
        speciesDict = {}
        pCols = self.paramCols()
        prevMatch = ''
        for i,v in enumerate(self.extract('species').values()):
            speciesDict[v[0]] = str(i+1) 
        numGroups = len(self.extract('species').values())
        # I don't think you can set a concentration of a function but this will require futher testing
        #for i,v in enumerate(self.extract('functions').values()):
        #    speciesDict[v[0]] = str(numGroups + i + 2) 
        for i in range(len(actList)):
            try:
                if actList[i].strip()[-1] == "\\":
                    actList[i] = actList[i] + actList[i+1]
                    actList.pop(i+1)
            except IndexError:
                continue
        for i in range(len(actList)):
            if actList[i].startswith('generate'):
                continue
            if actList[i].startswith('#'):
                continue
            if bool(actList[i]) == True:
                newActList.append(actList[i].strip().split('('))
                newActListCommands.append(actList[i].strip().split('(')[0])
                concList.append(actList[i].strip())
        lengthNewActList = len(newActList)
        firstSim = False
        resetConc = False
        setNewConc = False
        for i in range(lengthNewActList):
            if newActListCommands[i] == 'simulate':
                nSteps = re.search("n_steps\s*=>\s*(.*?)\s*[,}]", newActList[i][1])
                if isinstance(nSteps, type(None)):
                    nSteps = '0'
                else:
                    nSteps = nSteps.groups()[0]
                tStart = re.search("t_start\s*=>\s*(.*?)\s*[,}]", newActList[i][1])
                if isinstance(tStart, type(None)):
                    tStart = '0'
                else:
                    tStart = tStart.groups()[0]
                tEnd = re.search("t_end\s*=>\s*(.*?)\s*[,}]", newActList[i][1]).groups()[0]
                diffT = (float(eval(tEnd)) - float(eval(tStart)))/float(eval(nSteps))
                savet = str(float(eval(tStart))) + ':' + str(diffT) + ':' + str(float(eval(tEnd)))
                t = float(eval(tStart)), float(eval(tEnd))
                strSimulate = f'ODEProblem({self.modelN}!, u, {t}, pars, saveat = {savet}'
                match = re.search("suffix\s*=>\s*['\"](.*?)['\"]\s*[,}]", newActList[i][1]).group(1)
                aTol = re.search("atol\s*=>\s*(.*?)\s*[,}]", newActList[i][1]) 
                rTol = re.search("rtol\s*=>\s*(.*?)\s*[,}]", newActList[i][1])
                if isinstance(aTol, type(None)):
                    aTol = 'abstol=1e-8'
                else:
                    aTol =  'abstol=' + aTol.groups()[0]
                if isinstance(rTol, type(None)):
                    rTol = 'reltol=1e-8'
                else:
                    rTol = 'reltol=' + rTol.groups()[0]
                for num in reversed(range(0, i+1)):
                    if newActListCommands[num] == 'simulate':
                        if firstSim == False:
                            strActions.append('outCb["' + match + '"]=SavedValues(Float64, Vector)')
                            strActions.append(match + f'= SavingCallback(call{self.modelN}, outCb["{match}"], saveat = {savet})')    
                            strActions.append('model["'+ match + '"]=' + strSimulate + ', callback =' + match + ')')
                            strSolve.append(f'prob{match},outCb{match} = fileIn[1]["{match}"],fileIn[2]["{match}"]')
                            strSolve.append(f'initConc = deepcopy(prob{match}.u0[:])')
                            if setNewConc == True:
                                newSpecies = speciesDict[specie]
                                strSolve.append(f'prob{match}.u0[{newSpecies}] = {number}')
                            strSolve.append(f'sol{match} = solve(prob{match}, {aTol}, {rTol})')    
                            strSolve.append(f'y{match} = mapreduce(transpose,vcat,outCb{match}.saveval)')
                            strSolve.append(f'res["{match}"] = hcat(sol{match}.t,y{match})')   
                        elif newActList[num] == newActList[num - 1]:
                            strActions.append('outCb["' + match + '"]=SavedValues(Float64, Vector)')
                            strActions.append(match + f'= SavingCallback(call{self.modelN}, outCb["{match}"], saveat = {savet})')    
                            strActions.append('model["'+ match + '"]=' + strSimulate + ', callback =' + match + ')')
                            strSolve.append(f'prob{match}.u0 = last(sol{match})')
                            if setNewConc == True:
                                newSpecies = speciesDict[specie]
                                strSolve.append(f'prob{match}.u0[{newSpecies}] = {number}')
                            strSolve.append(f'sol{match} = solve(prob{match}, {aTol}, {rTol})')
                            strSolve.append(f'y{match} = mapreduce(transpose,vcat,outCb{match}.saveval)')
                            strSolve.append(f'res["{match}"] = hcat(sol{match}.t,y{match})')
                        elif newActListCommands[num] == newActListCommands[num - 1]:
                            strActions.append('outCb["' + match + '"]=SavedValues(Float64, Vector)')
                            strActions.append(match + f'= SavingCallback(call{self.modelN}, outCb["{match}"], saveat = {savet})')    
                            strActions.append('model["'+ match + '"]=' + strSimulate + ', callback =' + match + ')')
                            strSolve.append(f'prob{match},outCb{match} = fileIn[1]["{match}"],fileIn[2]["{match}"]')
                            strSolve.append(f'prob{match}.u0 = last(sol{prevMatch})')
                            strSolve.append(f'sol{match} = solve(prob{match}, {aTol}, {rTol})')    
                            strSolve.append(f'y{match} = mapreduce(transpose,vcat,outCb{match}.saveval)')
                            strSolve.append(f'res["{match}"] = hcat(sol{match}.t,y{match})')    
                        else:
                            strActions.append('outCb["' + match + '"]=SavedValues(Float64, Vector)')
                            strActions.append(match + f'= SavingCallback(call{self.modelN}, outCb["{match}"], saveat = {savet})')    
                            strActions.append('model["'+ match + '"]=' + strSimulate + ', callback =' + match + ')')
                            strSolve.append(f'prob{match},outCb{match} = fileIn[1]["{match}"],fileIn[2]["{match}"]')
                            strSolve.append(f'prob{match}.u0[:] = last(sol{prevMatch})')
                            if setNewConc == True:
                                newSpecies = speciesDict[specie]
                                strSolve.append(f'prob{match}.u0[{newSpecies}] = {number}')
                            if resetConc == True:
                                strSolve.append(f'prob{match}.u0[:] = initConc')
                            strSolve.append(f'sol{match} = solve(prob{match}, {aTol}, {rTol})')    
                            strSolve.append(f'y{match} = mapreduce(transpose,vcat,outCb{match}.saveval)')
                            strSolve.append(f'res["{match}"] = hcat(sol{match}.t,y{match})')         
                        prevMatch = match
                        resetConc = False
                        setNewConc = False
                        firstSim = True
                        break
            elif newActListCommands[i] == 'setConcentration':
                for num in range(i, lengthNewActList):
                    if newActListCommands[num] == 'simulate':
                        setNewConc = True
                        firstParan = concList[i].find('(')
                        lastParan = concList[i].rfind(')')
                        vals = concList[i][firstParan + 1:lastParan].replace('"', '').split(',')
                        try:
                            specie, number = vals
                            number = eval(number)
                        except NameError:
                            specie, number = vals
                            number = pCols[number]
                        break
            if firstSim == True:
                if newActListCommands[i] == 'resetConcentrations':
                    for num in range(i, lengthNewActList):
                        if newActListCommands[num] == 'simulate':
                            resetConc = True
                            break
                elif newActListCommands[i] == 'saveConcentrations':
                    for num in reversed(range(0, i)):
                        if newActListCommands[num] == 'simulate':
                            match = re.search("suffix\s*=>\s*['\"](.*?)['\"]\s*[,}]", newActList[num][1]).group(1)
                            strSolve.append(f'initConc = deepcopy(last(sol{match}.u))')
                            break
        strActions = '\n\t'.join(strActions)
        strSolve = '\n\t'.join(strSolve)
        juliaFile = f'simDataCols{self.modelN} = {self.speciesCols()}\n' + self.strOutput() + f'\nfunction solveOdeProb{self.modelN}(pars)\n\toutCb = Dict()\n\tmodel = Dict()\
        \n\tu = float(state{self.modelN}(pars))\n\t{strActions}\n\treturn [model,outCb]\nend\nfunction solveOdeSol{self.modelN}(fileIn)\n\tres = Dict()\n\
        {strSolve}\n\treturn res\nend'
        return juliaFile

    def juliaObjFunction(self):
        if self.objFunc == 'neg_bin':
            objFuncHeader  = 'neg_bin(simData, expData, simRow, i, colName, simDataDict)'
            objFunc  = f'function neg_bin(simData, expData, simRow, expRow, colName, simDataCols)\
            \n\trVal = {self.config.config["neg_bin_r"]}\
            \n\tsimVal = simData[simRow, simDataCols[colName]]\n\texpVal = expData.data[expRow, expData.cols[colName]] \
            \n\tif expVal >= 0\n\t\tprob = clamp(rVal / (rVal + simVal), 1e-10, 1 - 1e-10) \
            \n\t\tval = loggamma(expVal + rVal) - loggamma(expVal + 1) - loggamma(rVal) + rVal * log(prob) + expVal * log(1 - prob) \
            \n\telse\n\t\tval = 0\n\tend\n\treturn abs(val)\nend;'
        
        elif self.objFunc == 'neg_bin_dynamic':
            objFuncHeader = 'neg_bin_dynamic(simData, expData, simRow, i, colName, simDataDict, pset)'
            objFunc = 'function neg_bin_dynamic(simData, expData, simRow, expRow, colName, simDataCols, pSET) \
            \n\trVal=pSET.get_param("r__FREE").value\
            \n\tsimVal = simData[ simRow, simDataCols[ colName ]]\
            \n\texpVal = expData.data[ expRow, expData.cols[ colName ]]\
            \n\tif expVal >= 0\
            \n\t\tprob = clamp(rVal / (rVal + simVal), 1e-10, 1 - 1e-10)\
            \n\t\tval = loggamma(expVal + rVal)- loggamma(expVal + 1) - loggamma(rVal) + rVal * log(prob) + expVal * log(1 - prob)\
            \n\telse\
            \n\t\tval =0\
            \n\tend\
            \n\treturn abs(val)\
            \nend;'

        elif self.objFunc == 'sos':
            objFuncHeader = 'sos(simData, expData, simRow, i, colName, simDataDict)'
            objFunc = 'function sos(simData, expData, simRow, expRow, colName, simDataCols)\
            \n\tsimVal =simData[ simRow, simDataCols[ colName ] ]\
            \n\texpVal = expData.data[ expRow, expData.cols[ colName ]]\
            \n\treturn (simVal - expVal ) ^ 2\
            \nend;'
        ## The remainder of the functions needs to be imported
        elif self.objFunc == 'sod':
            objFuncHeader  = 'sod(simData, expData, simRow, i, colName, simDataDict)'
            objFunc = 'function sod(simData, expData, simRow, expRow, colName, simDataCols)\
            \n\tsimVal = simData[ simRow, simDataCols[ colName ] ]\
            \n\texpVal = expData.data[ expRow, expData.cols[ colName ] ]\
            \n\treturn abs(simVal - expVal)\
            \nend;'
        ## sod ran successfully  
    
        elif self.objFunc == 'norm_sos':
            objFuncHeader = 'norm_sos(simData, expData, simRow, i, colName, simDataDict)' 
            objFunc = 'function norm_sos(simData, expData, simRow, expRow, colName, simDataCols)\
            \n\tsimVal = simData[simRow, simDataCols[ colName ] ]\
            \n\texpVal = expData.data[ expRow, expData.cols[ colName ] ]\
            \n\treturn (simVal - expVal) ^2\
            \n\end;' 
        ##reexamined for correctness 

        elif self.objFunc == 'chi_sq':
            objFuncHeader = 'chi_sq(simData, expData, simRow, i, colName, simDataDict)'
            objFunc = 'function chi_sq(simData, expData, simRow, expRow, colName, simDataCols)\
            \n\tsimVal = simData[simRow, simDataCols[ colName ] ]\
            \n\texpVal = expData.data[expRow, expData.cols[ colName ] ]\
            \n\tsdCol = expData.cols[colName * "_SD"]\
            \n\texpSigma = expData.data[expRow, sdCol]\
            \n\tval = 1. / (2. * expSigma ^2.) * (simVal - expVal) ^2.\
            \n\treturn val\
            \nend;'

        elif self.objFunc == 'chi_sq_dynamic':
            objFuncHeader = 'chi_sq_dynamic(simData, expData, simRow, i, colName, simDataDict, pset)'
            objFunc = 'function chi_sq_dynamic(simData, expData, simRow, expRow, colName, simDataCols, pSET)\
            \n\tsimVal = simData[simRow, simDataCols[ colName ] ]\
            \n\texpVal = expData.data[expRow, expData.cols[ colName ] ]\
            \n\texpSigma = pSET.get_param("sigma__FREE").value \
            \n\tval = 1. / (2. * expSigma ^2.) * (simVal - expVal) ^2. + log(expSigma)\
            \n\treturn val\
            \nend;'
        
        return objFunc,objFuncHeader  

    def juliaFunctions(self, modelNameList):
        self.modelList = modelNameList
        runFunction = self.juliaRunFunction(self.modelList)
        probFunction = self.juliaProbFunction(self.modelList)
        colFunction = self.juliaColsFunction(self.modelList)
        objFunction = self.juliaObjFunction()
        updateParams = 'function solveOdeNewPars(probCb, pars)\n\tprobs = probCb\n\tfor i in keys(probs)\n\t\tfor k in keys(probs[i][1])\
        \n\t\t\tfor j in keys(pars)\n\t\t\t\tprobs[i][1][k].p[j] = pars[j]\n\t\t\tend\n\t\tend\n\tend\nend'
        structure = 'struct results\n\tpset\n\tout\n\tscore\n\tname\nend\nstruct resData\n\tcols\n\tdata\nend'
        sortFunction = 'm2(d) = collect(keys(d))[argmin(collect(values(d)))];'
        fitFunction = f'function objCalc(finalRes, expDataRes, simDataDict, pset)\n\tsimData = finalRes\n\texpData = expDataRes\
        \n\tindVar = m2(expData.cols);\n\tcompareColsSet = intersect(keys(expData.cols), keys(simDataDict));\n\tdelete!(compareColsSet,indVar);\
        \n\tcompareCols = collect(compareColsSet)\
        \n\tfuncVal = 0.0\n\tfor i = 1:size(expData.data)[1]\n\t\tsimRow = searchsortednearest(finalRes[:,simDataDict[indVar]], expData.data[i, 1])\
        \n\t\tfor colName in compareCols\
        \n\t\t\tif occursin("_Cum", colName)\
        \n\t\t\t\ttemp = diff(finalRes, dims = 1)\
        \n\t\t\t\tsimData = vcat(simData[1,:]\', temp)\
        \n\t\t\tend\
        \n\t\t\tfuncVal += {objFunction[1]}\n\t\tend\n\tend\n\treturn funcVal \
        \nend;'
        compareFunction = 'function searchsortednearest(a,x)\n\tidx = searchsortedfirst(a,x)\n\tif (idx==1); return idx; end\
        \n\tif (idx>length(a)); return length(a); end\n\tif (a[idx]==x); return idx; end\n\tif (abs(a[idx]-x) < abs(a[idx-1]-x))\
        \n\t\treturn idx\n\telse\n\t\treturn idx-1\n\tend\nend;'
        functionString = '\n'.join([colFunction, objFunction[0],sortFunction, compareFunction, fitFunction, probFunction, updateParams, runFunction, structure])
        return functionString
    def juliaProbFunction(self, listModelNames):
        self.allProbs = []
        self.modelList = listModelNames
        for i in self.modelList:
            self.allProbs.append('probs["'+ i +'"] = solveOdeProb' + i + '(params)')
        modelListStr = '\n\t'.join(self.allProbs)
        probFunction = f'function allProbs(params)\n\tprobs = Dict()\n\t{modelListStr}\n\treturn probs\nend'
        return probFunction
    def juliaRunFunction(self, listModelNames):
        self.allFuncs = []
        self.modelList = listModelNames
        for i in self.modelList:
            self.allFuncs.append('res["'+ i +'"] = solveOdeSol' + i + '(probs["' + i + '"])')
        functionListStr = '\n\t'.join(self.allFuncs)
        runFunction = f'function runAll(probs, pSet, exp)\n\tres = Dict()\n\texpData = exp\n\tpset=pSet\
        \n\t{functionListStr}\n\tnum = 0\
        \n\tfor i in keys(res)\n\t\tfor j in keys(expData)\n\t\t\tif i == j\n\t\t\t\tfor k in keys(res[i])\
        \n\t\t\t\t\tfor l in keys(expData[i])\n\t\t\t\t\t\tif k == l\n\t\t\t\t\t\t\tnum += objCalc(res[i][k], expData[i][k], simDataCols[i], pset)\
        \n\t\t\t\t\t\tres[i][k] = resData(simDataCols[i], res[i][k])\
        \n\t\t\t\t\t\tend\n\t\t\t\t\tend\n\t\t\t\tend\n\t\t\tend\n\t\tend\n\tend\n\treturn results(pSet,res,num,pSet.name)\nend'
        return runFunction
    def juliaColsFunction(self, listModelNames):
        self.modelList = listModelNames
        self.colsList = []
        for i in self.modelList:
            self.colsList.append(f'cols["{i}"] = simDataCols{i}')
        colStr = '\n\t'.join(self.colsList)
        colFunction = f'function modelCols()\n\tcols = Dict()\n\t{colStr}\n\treturn cols\nend\nsimDataCols = modelCols()'
        return colFunction
    def saveJuliaFile(self, fileIn, dir):
        file = fileIn
        filenameWpath = dir + '\juliaBNF.jl'
        with open(dir + '\juliaBNF.jl', 'w') as f:
            f.write(file)
        return filenameWpath
    def juliaDependancies(self):
        jlDstr = 'using Distributed\nusing SpecialFunctions\nusing DifferentialEquations\n'
        return jlDstr
