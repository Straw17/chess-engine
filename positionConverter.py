while True:
    newTable = []

    toReformat = ""
    print("Enter list: ")
    while True:
        nextLine = input()
        if nextLine == "":
            break
        else:
            toReformat += nextLine
    toReformat = toReformat.split(",")
    
    for a in range(8):
        newRow = []
        for b in range(8):
            newItem = toReformat[a*8 + b]
            newRow.append(int(newItem))
        newTable += newRow

    print("[")
    for a in range(8):
        for b in range(8):
            itemStr = str(newTable[a*8+b])
            for i in range(4-len(itemStr)):
                itemStr = " " + itemStr
            print(itemStr, end=",")
        print("")
    print("]")
    print("")
            
