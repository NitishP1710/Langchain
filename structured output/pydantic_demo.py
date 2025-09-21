from pydantic import BaseModel

class Student(BaseModel):
    name:str

new_student={"name":"nitish"}
student=Student(**new_student)
print(student) #give pydantic object dictionary

student2={"name":32}
student2=Student(**student2)
print(student2) # give message that name should be valid string

