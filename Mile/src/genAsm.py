import pickle
import os
import sys
with open('scopeTabDump', 'rb') as handle:
    scopeTab  = pickle.load(handle)
basicTypes=["int","float","rune","string","bool"]

with open("code.txt") as f:
    content = f.readlines()
content = [x.strip() for x in content]

## To Remove Concurrent Returns ##
index=1
while(index<len(content)):
    if(content[index]=="return" and content[index-1]=="return"):
        del(content[index])
    else:
        index=index+1

j=0
codeLines=[]
for i in content:
    codeLines.append([])
    for x in i.split():
        codeLines[j].append(x)
    j+=1

regToVar=[]
for i in range(0,28):
    regToVar.append("free")
regToVarFloat=[]
for i in range(0,32):
    regToVarFloat.append("free")

varToReg={}
varToRegFloat={}

regReplace=1
regReplaceFloat=0

currentFunc=""
currentLabel=""

def getOffset(name):
    for x in scopeTab:
        if (scopeTab[x].table.get(name)==None):
            continue
        return scopeTab[x].table[name]["offset"]

def getVarOffset(vartemp):
    for x in scopeTab:
        if (scopeTab[x].table.get(vartemp)==None):
            continue
        return scopeTab[x].table[scopeTab[x].table[vartemp]["type"]]["offset"], x

def getType(vartemp):
    for x in scopeTab:
        if (scopeTab[x].table.get(vartemp)==None):
            continue
        if(scopeTab[x].table[scopeTab[x].table[vartemp]["type"]]["type"][0] not in basicTypes):
            return 1
        else:
            return 0


def getReg(a=None):
    if (a==None):
        for i in range(2, 26):
            if (regToVar[i]=="free"):
                return i
        if(regToVar[regReplace][0]=='t'):
            off=getOffset(regToVar[regReplace])
            f.write("sw " + "$"+ str(regReplace) + "," + str(-off)+"($fp)\n")
        elif(not getType(varToReg[regReplace]):
            off, control=getVarOffset(regToVar[regReplace])
            if(not control):
                f.write("sw " + "$"+ str(regReplace) + "," + str(-off)+"($gp)\n")
            else:
                f.write("sw " + "$"+ str(regReplace) + "," + str(-off)+"($fp)\n")
        del varToReg[regToVar[regReplace]]
        org=regReplace
        regReplace=(regReplace%24) + 2
        return org
    else:
        for i in range(0, 32):
            if (regToVarFloat[i]=="free"):
                return i
        off=getOffset(regToVarFloat[regReplaceFloat])
        if(varToRegFloat[regReplaceFloat][0]=='t' or not getType(varToRegFloat[regReplaceFloat]) ):
            f.write("swc1 " + "$f"+ str(regReplaceFloat) + "," + str(-off)+"($fp)\n")
        del varToRegFloat[regToVarFloat[regReplaceFloat]]
        org=regReplaceFloat
        regReplaceFloat=(regReplaceFloat+1)%32
        return org

def writeInstrBin(reg1, reg2, reg3, op):
    if(op=="||" or op=="|"):
        f.write("or "+"$"+str(reg1)+",$" +str(reg2)+",$" +str(reg3)+"\n")
    elif(op=="&&" or op=="&"):
        f.write("and "+"$"+str(reg1)+",$" +str(reg2)+",$" +str(reg3)+"\n")
    elif(op=="+"):
        f.write("add "+"$"+str(reg1)+",$" +str(reg2)+",$" +str(reg3)+"\n")
    elif(op=="-"):
        f.write("sub "+"$"+str(reg1)+",$" +str(reg2)+",$" +str(reg3)+"\n")
    elif(op=="*"):
        f.write("mult "+"$" +str(reg2)+",$" +str(reg3)+"\n"+ "mflo " +"$"+str(reg1)+"\n")
    elif(op=="/"):
        f.write("div "+"$"+str(reg2)+",$" +str(reg3)+"\n"+"mflo "+"$" + str(reg1)+"\n")
    elif(op=="%"):
        f.write("div "+"$"+str(reg2)+",$" +str(reg3)+"\n"+"mfhi "+"$" + str(reg1)+"\n")
    elif(op==">>"):
        f.write("srav "+"$"+str(reg1)+",$" +str(reg2)+",$" +str(reg3)+"\n")
    elif(op=="<<"):
        f.write("sllv "+"$"+str(reg1)+",$" +str(reg2)+",$" +str(reg3)+"\n")
    elif(op=="^"):
        f.write("xor "+"$"+str(reg1)+",$" +str(reg2)+",$" +str(reg3)+"\n")
    elif(op=="<"):
        f.write("slt "+"$"+str(reg1)+",$" +str(reg2)+",$" +str(reg3)+"\n")
    elif(op==">"):
        f.write("slt "+"$"+str(reg1)+",$" +str(reg3)+",$" +str(reg2)+"\n")
    elif(op=="<="):
        f.write("slt "+"$"+str(reg1)+",$" +str(reg3)+",$" +str(reg2)+"\n"+"xori " +"$" + str(reg1)+",$"+ str(reg1)+ "1"+ "\n")
    elif(op==">="):
        f.write("slt "+"$"+str(reg1)+",$" +str(reg2)+",$" +str(reg3)+"\n"+"xori " +"$" + str(reg1)+",$"+ str(reg1)+ "1"+ "\n")
    elif(op=="=="):
        reg4=getReg()
        regToVar[reg4]="free"
        f.write("slt "+"$"+str(reg1)+",$" +str(reg2)+",$" +str(reg3)+"\n"+"slt " +"$" + str(reg4)+",$"+ str(reg3)+ ",$"+str(reg2)+ "\n")
        f.write("xori " +"$" + str(reg1)+",$"+ str(reg1)+ "1"+ "\n" + "xori " +"$" + str(reg4)+",$"+ str(reg4)+ "1"+ "\n")
        f.write("and "+"$"+str(reg1)+",$" +str(reg4)+",$" +str(reg1)+"\n")
    elif(op=="!="):
        reg4=getReg()
        regToVar[reg4]="free"
        f.write("slt "+"$"+str(reg1)+",$" +str(reg2)+",$" +str(reg3)+"\n"+"slt " +"$" + str(reg4)+",$"+ str(reg3)+ ",$"+str(reg2)+ "\n")
        f.write("or "+"$"+str(reg1)+",$" +str(reg4)+",$" +str(reg1)+"\n")


f=open('mips.txt', 'wr')

f.write(".text\n.globl main\n")
for code in codeLines:
    if (len(code) == 2 and code[1]==":"):
	if(code[0]=="main"):
            currentLabel="main"
        f.write(code[0]+code[1]+"\n")
        f.write("addi "+ "$fp,$sp,0\n")
        if (scopeTab[0].table.get(code[0])!= None):
            scope=scopeTab[0].table[code[0]]["Scope"]
            f.write("addi "+"$sp,"+"$sp,"+"-"+str(scopeTab[scope].table["#total_size"]["type"])+"\n")

    if (len(code) == 5):
        if(code[2][0]!='t' and code[2][0]!='v' and code[4][0]!='t' and code[4][0]!='v'):   #constant, constant
            if (code[3][-3]=="i" or code[3][-3]=='u' or code[3][-3]=='o'):  #integer op
                op=code[3][:-3] if code[3][-3]=="i" else code[3][:-4]
                val=eval(code[2]+op+code[4])
                if (val==True):
                    val=1
                elif(val==False):
                    val=0
                reg=getReg()
                f.write("addi "+"$"+str(reg)+",$0," + str(val)+"\n")
                regToVar[reg]=code[0]
                varToReg[code[0]]=reg


            else:   #float operation
                op=code[3][:-5]
                val=eval(code[2]+op+code[4])
                if (val=="True"):
                    val=1
                elif(val=="False"):
                    val=0
                reg=getReg(f)
                f.write("addi "+"$"+str(reg)+",$0," + str(val)+"\n")
                regToVarFloat[reg]=code[0]
                varToRegFloat[code[0]]=reg
        elif(code[2][0]!='t' and code[2][0]!='v' and (code[4][0]=='t' or code[4][0]=='v')):   # constant, temp or constant, vartemp
                if (code[3][-3]=="i" or code[3][-3]=='u' or code[3][-3]=='o'):  #integer op or rune op
                    op=code[3][:-3] if code[3][-3]=="i" else code[3][:-4]
                    if(varToReg.get(code[4])==None):
                        reg3=getReg()
                        if(code[4][0]=='t'):
                            off=getOffset(code[4])
                            f.write("lw " + "$"+ str(reg3) + "," + str(-off)+"($fp)\n")
                        else:
                            off, control=getVarOffset(code[4])
                            if(not getType(code[4])):
                                if(control==0):
                                    f.write("lw " + "$"+ str(reg3) + "," +str(-off)+"($gp)\n")
                                else:
                                    f.write("lw " + "$"+ str(reg3) + ","+str(-off)+"($fp)\n")

                            else:
                                if(control==0):
                                    f.write("subi " + "$"+ str(reg3) + "," + "$gp," + str(off)+"\n")
                                else:
                                    f.write("subi " + "$"+ str(reg3) + "," + "$fp," + str(off)+"\n")
                        regToVar[reg3]=code[4]
                        varToReg[code[4]]=reg3
                    else:
                        reg3=varToReg[code[4]]

                    reg2=getReg()
                    f.write("addi " + "$"+ str(reg2) + ",$0," +code[2]+"\n")
                    regToVar[reg2]="free"
                    reg1=getReg()
                    regToVar[reg1]=code[0]
                    varToReg[code[0]]=reg1
                    writeInstrBin(reg1, reg2, reg3, op)
                else:
                    xxxyyy=0

        elif(code[4][0]!='t' and code[4][0]!='v' and (code[2][0]=='t' or code[2][0]=='v')):   # temp, constant or vartemp, constant
                if (code[3][-3]=="i" or code[3][-3]=='u' or code[3][-3]=='o'):  #integer op or rune op
                    op=code[3][:-3] if code[3][-3]=="i" else code[3][:-4]
                    if(varToReg.get(code[2])==None):
                        reg2=getReg()
                        if(code[2][0]=='t'):
                            off=getOffset(code[2])
                            f.write("lw " + "$"+ str(reg2) + "," +str(-off)+"($fp)\n")
                        else:
                            off, control=getVarOffset(code[2])
                            if(not getType(code[2])):
                                if(control==0):
                                    f.write("lw " + "$"+ str(reg2) + "," +str(-off)+"($gp)\n")
                                else:
                                    f.write("lw " + "$"+ str(reg2) + ","+str(-off)+"($fp)\n")
                            else:
                                if(control==0):
                                    f.write("subi " + "$"+ str(reg2) + "," + "$gp," + str(off)+"\n")
                                else:
                                    f.write("subi " + "$"+ str(reg2) + "," + "$fp," + str(off)+"\n")
                        regToVar[reg2]=code[2]
                        varToReg[code[2]]=reg2
                    else:
                        reg2=varToReg[code[2]]

                    reg3=getReg()
                    f.write("addi " + "$"+ str(reg3) + ",$0," +code[4]+"\n")
                    regToVar[reg3]="free"
                    reg1=getReg()
                    regToVar[reg1]=code[0]
                    varToReg[code[0]]=reg1
                    writeInstrBin(reg1, reg2, reg3, op)
                else:
                    xxxyyy=0
        else:  # t,t or t,v, or v,t, or v,v
            if (code[3][-3]=="i" or code[3][-3]=='u' or code[3][-3]=='o'):  #integer or rune  op
                op=code[3][:-3] if code[3][-3]=="i" else code[3][:-4]
                if(varToReg.get(code[2])==None):
                    reg2=getReg()
                    if(code[2][0]=='t'):
                        off=getOffset(code[2])
                        f.write("lw " + "$"+ str(reg2) + "," + str(-off)+"($fp)\n")
                    else:
                        off, control=getVarOffset(code[2])
                        if(not getType(code[2])):
                            if(control==0):
                                f.write("lw " + "$"+ str(reg2) + "," + str(-off)+"($gp)\n")
                            else:
                                f.write("lw " + "$"+ str(reg2) + ","+str(-off)+"($fp)\n")
                        else:
                            if(control==0):
                                f.write("subi " + "$"+ str(reg2) + "," + "$gp," + str(off)+"\n")
                            else:
                                f.write("subi " + "$"+ str(reg2) + "," + "$fp," + str(off)+"\n")
                    regToVar[reg2]=code[2]
                    varToReg[code[2]]=reg2
                else:
                    reg2=varToReg[code[2]]
                if(varToReg.get(code[4])==None):
                    reg3=getReg()
                    if(code[4][0]=='t'):
                        off=getOffset(code[4])
                        f.write("lw " + "$"+ str(reg3) + "," + str(-off)+"($fp)\n")
                    else:
                        off, control=getVarOffset(code[4])
                        if(not getType(code[4])):
                            if(control==0):
                                f.write("lw " + "$"+ str(reg3) + "," + str(-off)+"($gp)\n")
                            else:
                                f.write("lw " + "$"+ str(reg3) + ","+str(-off)+"($fp)\n")

                        else:
                            if(control==0):
                                f.write("subi " + "$"+ str(reg3) + "," + "$gp," + str(off)+"\n")
                            else:
                                f.write("subi " + "$"+ str(reg3) + "," + "$fp," + str(off)+"\n")
                    regToVar[reg3]=code[4]
                    varToReg[code[4]]=reg3
                else:
                    reg3=varToReg[code[4]]
                reg1=getReg()
                regToVar[reg1]=code[0]
                varToReg[code[0]]=reg1
                writeInstrBin(reg1, reg2, reg3, op)
            else:
                xxxyyy=0

    if (len(code)==3 and (code[0][0]=='t' or code[0][0]=='v') and code[2][0]!="*" and code[2][0]!="r"):
        reg1=getReg()
        regToVar[reg1]=code[0]
        varToReg[code[0]]=reg1
        if(code[2][0]!='t' and code[2][0]!='v'): #constant
            reg2=getReg()
            f.write("addi "+ "$" +str(reg2)+",$0," + code[2] +"\n")
            regToVar[reg2]="free"
        else:
            if(varToReg.get(code[2])==None):
                reg2=getReg()
                if(code[2][0]=='t'):
                    off=getOffset(code[2])
                    f.write("lw " + "$"+ str(reg2) + "," + str(-off)+"($fp)\n")
                else:
                    off, control=getVarOffset(code[2])
                    if(not getType(code[2])):
                        if(control==0):
                            f.write("lw " + "$"+ str(reg2) + "," + str(-off)+"($gp)\n")
                        else:
                            f.write("lw " + "$"+ str(reg2) + ","+str(-off)+"($fp)\n")
                    else:
                        if(control==0):
                            f.write("subi " + "$"+ str(reg2) + "," + "$gp," + str(off)+"\n")
                        else:
                            f.write("subi " + "$"+ str(reg2) + "," + "$fp," + str(off)+"\n")
                regToVar[reg2]=code[2]
                varToReg[code[2]]=reg2
            else:
                reg2=varToReg[code[2]]
            f.write("addi "+"$"+str(reg1)+ ",$" + str(reg2) + ","+ "0\n")

    if(len(code)==4 and code[0]=="*"):
        if(code[3][0]!='t' and code[3][0]!='v'): #constant
            reg2=getReg()
            f.write("addi "+ "$" +str(reg2)+",$0," + code[3] +"\n")
            regToVar[reg2]="free"
        else:
            if(varToReg.get(code[3])==None):
                reg2=getReg()
                if(code[3][0]=='t'):
                    off=getOffset(code[3])
                    f.write("lw " + "$"+ str(reg2) + "," + str(-off)+"($fp)\n")
                else:
                    off, control=getVarOffset(code[3])
                    if(not getType(code[3])):
                        if(control==0):
                            f.write("lw " + "$"+ str(reg2) + "," + str(-off)+"($gp)\n")
                        else:
                            f.write("lw " + "$"+ str(reg2) + ","+str(-off)+"($fp)\n")
                    else:
                        if(control==0):
                            f.write("subi " + "$"+ str(reg2) + "," + "$gp," + str(off)+"\n")
                        else:
                            f.write("subi " + "$"+ str(reg2) + "," + "$fp," + str(off)+"\n")
                regToVar[reg2]=code[3]
                varToReg[code[3]]=reg2
            else:
                reg2=varToReg[code[3]]
        if(varToReg.get(code[1])==None):
            reg1=getReg()
            if(code[1][0]=='t'):
                off=getOffset(code[1])
                f.write("lw " + "$"+ str(reg1) + "," + str(-off)+"($fp)\n")
            regToVar[reg1]=code[1]
            varToReg[code[1]]=reg1
        else:
            reg1=varToReg[code[1]]
        f.write("sw $"+str(reg2)+",0($"+str(reg1)+")\n")

    if(len(code)==4 and code[2]=="*"):
        reg1=getReg()
        regToVar[reg1]=code[0]
        varToReg[code[0]]=reg1
        if(varToReg.get(code[3])==None):
            reg2=getReg()
            if(code[3][0]=='t'):
                off=getOffset(code[3])
                f.write("lw " + "$"+ str(reg2) + "," + str(-off)+"($fp)\n")
            else:
                off, control=getVarOffset(code[3])
                if(not getType(code[3])):
                    if(control==0):
                        f.write("lw " + "$"+ str(reg2) + "," + str(-off)+"($gp)\n")
                    else:
                        f.write("lw " + "$"+ str(reg2) + ","+str(-off)+"($fp)\n")
                else:
                    if(control==0):
                        f.write("subi " + "$"+ str(reg2) + "," + "$gp," + str(off)+"\n")
                    else:
                        f.write("subi " + "$"+ str(reg2) + "," + "$fp," + str(off)+"\n")
            regToVar[reg2]=code[3]
            varToReg[code[3]]=reg2
        else:
            reg2=varToReg[code[3]]
        f.write("lw "+"$"+str(reg1)+ ",0"+"($" + str(reg2) + ")"+ "\n")

    if (code[0]=="ifnot"):

        if(code[1][0]!='t'):
            reg1=getReg()
            regToVar[reg1]=code[0]
            varToReg[code[0]]=reg1
            f.write("addi " + "$"+str(reg1)+ ",$0,"+ code[1]+"\n")
        else:
            if(varToReg.get(code[1])!=None):
                reg1=varToReg[code[1]]
            else:
                reg1=getReg()
                regToVar[reg1]=code[0]
                varToReg[code[0]]=reg1
                off=getOffset(code[1])
                f.write("lw " + "$"+ str(reg1) + "," + str(-off)+"($fp)\n")
        f.write("blez " + "$"+str(reg1)+"," + code[3] +"\n" )

    if (code[0]=="goto"):
        f.write("j " + code[1]+"\n")

    if(len(code)==4 and code[2]=="&"):
        reg1=getReg()
        regToVar[reg1]=code[0]
        varToReg[code[0]]=reg1
        if(varToReg.get(code[3])==None):
            reg2=getReg()
            if(code[3][0]=='t'):
                off=getOffset(code[3])
                f.write("lw " + "$"+ str(reg2) + "," + str(-off)+"($fp)\n")
            else:
                off, control=getVarOffset(code[3])
                if(control==0):
                    f.write("subi " + "$"+ str(reg2) + "," + "$gp," + str(off)+"\n")
                else:
                    f.write("subi " + "$"+ str(reg2) + "," + "$fp," + str(off)+"\n")
            regToVar[reg2]=code[3]
            varToReg[code[3]]=reg2
        else:
            reg2=varToReg[code[3]]
        f.write("addi $"+str(reg1)+",$"+str(reg2)+",0\n")

    if(code[0]=="startf"):
        currentFunc=code[1]
        retSize=scopeTab[0].table[currentFunc]["#total_retSize"]
        f.write("addi $sp,$sp,"+str(-retSize)+"\n")

    if(code[0]=="param" and len(code)==2): # param reg
        if(code[1][0]!='t' and code[1][0]!='v'): #constant
            reg=getReg()
            f.write("addi "+ "$" +str(reg2)+",$0," + code[1] +"\n")
            regToVar[reg]="free"
        else:
            if(varToReg.get(code[1])==None):
                reg=getReg()
                if(code[1][0]=='t'):
                    off=getOffset(code[1])
                    f.write("lw " + "$"+ str(reg) + ","+str(-off)+"($fp)\n")
                else:
                    off, control=getVarOffset(code[1])
                    if(not getType(code[1])):
                        if(control==0):
                            f.write("lw " + "$"+ str(reg) + ","+str(-off)+"($gp)\n")
                        else:
                            f.write("lw " + "$"+ str(reg) + ","+str(-off)+"($fp)\n")
                    else:
                        if(control==0):
                            f.write("subi " + "$"+ str(reg) + "," + "$gp," + str(off)+"\n")
                        else:
                            f.write("subi " + "$"+ str(reg) + "," + "$fp," + str(off)+"\n")
                regToVar[reg]=code[1]
                varToReg[code[1]]=reg
            else:
                reg=varToReg[code[1]]
        f.write("addi $sp,$sp,-4\nsw $"+str(reg)+",0($sp)\n")

    if(code[0]=="param" and len(code)==3): # param reg size
        size=int(code[2])
        if(code[1][0]!='t' and code[1][0]!='v'): #constant
            reg=getReg()
            f.write("addi "+ "$" +str(reg2)+",$0," + code[1] +"\n")
            regToVar[reg]="free"
        else:
            if(varToReg.get(code[1])==None):
                reg=getReg()
                if(code[1][0]=='t'):
                    off=getOffset(code[1])
                    f.write("lw " + "$"+ str(reg) + ","+str(-off)+"($fp)\n")
                else:
                    off, control=getVarOffset(code[1])
                    if(not getType(code[1])):
                        if(control==0):
                            f.write("lw " + "$"+ str(reg) + ","+str(-off)+"($gp)\n")
                        else:
                            f.write("lw " + "$"+ str(reg) + ","+str(-off)+"($fp)\n")
                    else:
                        if(control==0):
                            f.write("subi " + "$"+ str(reg) + "," + "$gp," + str(off)+"\n")
                        else:
                            f.write("subi " + "$"+ str(reg) + "," + "$fp," + str(off)+"\n")
                regToVar[reg]=code[1]
                varToReg[code[1]]=reg
            else:
                reg=varToReg[code[1]]
        regToCopy=getReg()
        off=0
        while size>0:
            f.write("addi $sp,$sp,-4\n")
            f.write("lw $"+str(regToCopy)+","+str(off)+"($"+str(reg)+")\n")
            f.write("sw $"+str(regToCopy)+",0($sp)\n")
            size=size-4
            off=off+4

    if(code[0]=="call"):
        ## Reset the reg-var maps
        for index in range(2, 26):
            if (regToVar[index]=="free"):
                continue
            if(regToVar[index][0]=='t'):
                off=getOffset(regToVar[index])
                f.write("sw " + "$"+ str(index) + "," + str(-off)+"($fp)\n")
            elif(not getType(regToVar[index])):
                off,control=getVarOffset(regToVar[index])
                if (not control):
                    f.write("sw " + "$"+ str(index) + "," + str(-off)+"($gp)\n")
                else:
                    f.write("sw " + "$"+ str(index) + "," + str(-off)+"($fp)\n")
            if(varToReg.get(regToVar[index])!=None):
                del varToReg[regToVar[index]]
            regToVar[index]="free"

        f.write("addi $sp,$sp,-4\n")
        f.write("sw $ra,0($sp)\n")
        f.write("addi $sp,$sp,-4\n")
        f.write("sw $fp,0($sp)\n")
        f.write("add $fp,$0,$sp\n")
        f.write("jal "+currentFunc+"\n")

    if(code[0]=="endf"):
        size=4+scopeTab[0].table[currentFunc]["#total_retSize"]+scopeTab[0].table[currentFunc]["#total_parSize"]
        f.write("lw $ra,0($sp)\n")
        f.write("addi $sp,$sp,"+str(size)+"\n")

    if(len(code)==3 and code[2][0:3]=="ret"):
        reg=getReg()
        regToVar[reg]=code[0]
        varToReg[code[0]]=reg
        retNumber=int(code[2][7:])
        off=4*retNumber
        if(varToReg.get(code[0])==None):
            reg=getReg()
            off=getOffset(code[0])
            f.write("lw " + "$"+ str(reg) + ","+str(-off)+"($fp)\n")
            regToVar[reg]=code[0]
            varToReg[code[0]]=reg
        else:
            reg=varToReg[code[0]]
        f.write("lw $"+str(reg)+","+str(-off)+"($sp)\n")

    if(len(code)==1 and code[0]=="return"):
        ## Reset reg-var maps
        for index in range(2, 26):
            if (regToVar[index]=="free"):
                continue
            if(varToReg.get(regToVar[index])!=None):
                del varToReg[regToVar[index]]
            regToVar[index]="free"

        if(currentLabel=="main"):
            f.write("jr $ra\n")
            currentLabel=""
        else:
            f.write("add $sp,$fp,$0\n")
            f.write("lw $fp,0($sp)\n")
            f.write("addi $sp,$sp,4\n")
            f.write("jr $ra\n")

    if(len(code)==4 and code[1]=="return"):
        retNumber=int(code[3])
        func=code[0]
        off=scopeTab[0].table[func]["retSizeList"][retNumber]

        if(code[2][0]!='t' and code[2][0]!='v'): #constant
            reg=getReg()
            f.write("addi "+ "$" +str(reg2)+",$0," + code[1] +"\n")
            regToVar[reg]="free"
        else:
            if(varToReg.get(code[2])==None):
                reg=getReg()
                if(code[2][0]=='t'):
                    off=getOffset(code[2])
                    f.write("lw " + "$"+ str(reg) + ","+str(-off)+"($fp)\n")
                else:
                    off, control=getVarOffset(code[2])
                    if(not getType(code[2])):
                        if(control==0):
                            f.write("lw " + "$"+ str(reg) + ","+str(-off)+"($gp)\n")
                        else:
                            f.write("lw " + "$"+ str(reg) + ","+str(-off)+"($fp)\n")
                    else:
                        if(control==0):
                            f.write("subi " + "$"+ str(reg) + "," + "$gp," + str(off)+"\n")
                        else:
                            f.write("subi " + "$"+ str(reg) + "," + "$fp," + str(off)+"\n")
                regToVar[reg]=code[2]
                varToReg[code[2]]=reg
            else:
                reg=varToReg[code[2]]
                f.write("sw $"+str(reg)+","+str(-off)+"($fp)\n")


f.close()
