from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2",
    base_url="https://4e68-115-241-193-70.ngrok-free.app",
    temperature=0,
)

from langchain_core.messages import AIMessage

messages = [
    (
        "system",
        "You are a helpful assistant that reads through the contents of a PDF file, understands them, restructures them and tells it in a way that students can understand. ",
    ),
    ("assistant", """Python OOPs Concepts
Object Oriented Programming is a fundamental concept in Python, empowering developers to build modular, maintainable, and scalable applications. By understanding the core OOP principles (classes, objects, inheritance, encapsulation, polymorphism, and abstraction), programmers can leverage the full potential of Python OOP capabilities to design elegant and efficient solutions to complex problems.


A class is a collection of objects. Classes are blueprints for creating objects. A class defines a set of attributes and methods that the created objects (instances) can have.

Some points on Python class:  

Classes are created by keyword class.
Attributes are the variables that belong to a class.
Attributes are always public and can be accessed using the dot (.) operator. Example: Myclass.Myattribute
Creating a Class

Here, the class keyword indicates that we are creating a class followed by name of the class (Dog in this case).



Explanation:

class Dog: Defines a class named Dog.
species: A class attribute shared by all instances of the class.
__init__ method: Initializes the name and age attributes when a new object is created.
Note: For more information, refer to python classes.
"""),
]
ai_msg = llm.invoke(messages)
with open("exampleOutputs/output1.txt", "a") as f:
  f.write(ai_msg.content)
print(ai_msg.content)