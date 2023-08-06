Tamil to Thanglish converter in python 
=======================================
Installing :)
============
- Make sure you have Python installed in your system.

- Run Following the command in the CMD




    pip install Py_Thanglish

Example :)
============
Code 1 :)
============


    import PyThanglish as py
    input = """அகர முதல எழுத்தெல்லாம் ஆதி
    பகவன் முதற்றே உலகு"""
    output = py.tamil_to_thanglish(input)
    print(input,output ,sep="\n")

Output :)


    அகர முதல எழுத்தெல்லாம் ஆதி
    பகவன் முதற்றே உலகு
    akara muthala yezhuththellaam aathi
    pakavan muthatrrae ulaku

Code 2 :)
============


    import PyThanglish as p
    import pyttsx3 as py
    input = "என்ன செய்துகொண்டி இருக்கிறீர் ?"
    output = p.tamil_to_thanglish(input)
    py.speak(output)
    print(output)

Output :)

- The following output are print and voice


    
        yenna seythukonti irukkireer ?

 Note:)
============
- This is starting leval package 
- This package is useful for tamil to thanglish converte
- The pyttsx3 is not read tamil language.
- But this package is very useful to pyttsx3 read to Tamil in the way of Thanglish 


        THANK YOU FOR VISIT :)
