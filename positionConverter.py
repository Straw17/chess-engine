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
            newItem = newItem.strip()
            newRow.append(int(newItem))
        newTable.append(newRow)

    print("[", end="")
    for row in newTable:
        print(str(row) + ",")
    print("]")
    print("")
            
