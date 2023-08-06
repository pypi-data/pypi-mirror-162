def AnalyzeNamingForm(Form):
    SavedBracketIndex = {}
    FrontIndex = -1
    EndIndex = -1
    Counter = -1
    FileNameStruct = []
    VariableNameStorage = {}

    # Find bracket and save index
    for Index, AtoZ in enumerate(Form):
        if AtoZ == "{":
            FrontIndex = Index
        elif AtoZ == "}":
            if FrontIndex != -1:
                EndIndex = Index
                SavedBracketIndex[len(SavedBracketIndex)] = [FrontIndex, EndIndex]

    # Split words by bracket location and make bracket word specifize
    for Index, Pair in enumerate(SavedBracketIndex):
        FrontIndex = SavedBracketIndex[Pair][0]
        EndIndex = SavedBracketIndex[Pair][1]

        # if frontest words are exist
        if Index <= 0:
            Counter += 1
            FileNameStruct.append(Form[0: SavedBracketIndex[Pair][0]])

        # this pairs word
        Counter += 1
        FileNameStruct.append(Form[SavedBracketIndex[Pair][0]: SavedBracketIndex[Pair][1] + 1])
        VariableNameStorage[Counter] = Form[FrontIndex + 1: EndIndex]

        # words between current and next
        if Pair + 1 < len(SavedBracketIndex):
            Counter += 1
            FileNameStruct.append(Form[SavedBracketIndex[Pair][1] + 1:SavedBracketIndex[Pair + 1][0]])

        # end of words
        if Pair + 1 >= len(SavedBracketIndex):
            if SavedBracketIndex[Pair][1] < len(Form):
                FileNameStruct.append(Form[SavedBracketIndex[Pair][1] + 1:len(Form)])

    return VariableNameStorage, FileNameStruct


def GetFileNameByForm(GlobalVariables, VariableNameList, FileNameStructure):
    Temp = FileNameStructure
    for Var in VariableNameList.keys():
        try:
            CurrentValue = str(GlobalVariables[VariableNameList[Var]])
            Temp[Var] = str(CurrentValue)
        except KeyError:
            print("Can't Find [%s] variable on global variable list" % VariableNameList[Var])
    return "".join(Temp)