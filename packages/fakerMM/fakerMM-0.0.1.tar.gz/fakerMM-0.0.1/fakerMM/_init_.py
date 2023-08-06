import numpy as np
from faker import Faker
fake = Faker('es-ES')

def spanish_name(row):

    name = ''
    sex = np.random.randint(0, 2, 1) 
    if sex==1: # female
        name = fake.last_name_female() + ' ' + fake.last_name_female() + '; ' + fake.first_name_female()
    if sex!=1: # male
        name = fake.last_name_male() + ' ' + fake.last_name_male() + '; ' + fake.first_name_male()
    
    # randomly determine if two first name should be used:
    if np.random.randint(0, 2, 1) == 1:
        name = name + ' ' + fake.first_name_nonbinary()
        
    return(name)

def safe_email(row):
    return(fake.ascii_safe_email())

def clean_phone_num(row):
    
    phone=fake.phone_number().replace(' ', '')
    
    return(phone)

def fake_address(row):
      address = fake.street_address() + ', ' + fake.city()
    
      return(address) 