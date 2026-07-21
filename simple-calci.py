num1= float(input("enter number1:"))
operator= input("enter operator(+,-,*,/,):")
num2= float(input("enter number2:"))

if operator== "+":
    print("result=", num1+num2)
elif operator=="-":
    print("result=", num1-num2)
elif operator=="*":
    print("result=", num1*num2)
elif operator=="/":
    if num2!=0:
        print("reslut=",num1/num2)
    else:
        print("result is infinite")
else:
    print("invalid operator try again")
    
