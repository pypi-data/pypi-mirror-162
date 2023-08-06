# samparka

A package that allows to get contact-info (emails & phonenumbers) from the website homepage
Phone number is available for Nepal & USA as of now

Developed by Ujjawal Shah (c) 2022

## Examples of How To Use Package

### Get contact email from the website homepage

```python
import samparka

homepage = samparka.Scrollhomepage('https://www.setopati.com/')
email_adresses = homepage.emails()
print(f'emails: {email_adresses}')
```
**Output**:

***emails: ['ketaketi.setopati@gmail.com', 'info@setopati.com', 'setopati@gmail.com']***

### Get phonenumbers from the homepage

```python
import samparka

#to see which countries are available for the phone numbers
print(samparka.__availablecountries__)
```
**Output**:

***['Nepal', 'USA']***


```python
import samparka

homepage = samparka.Scrollhomepage('https://www.setopati.com/')
phone_numbers = homepage.phonenumbers('Nepal')
print(f'phone_numbers: {phone_numbers}')
```
**Output**:

***['+977-1-5429319', '9741857838', '9772067662', '9771494820', '9703857991', '9823847051', '9839993648', '9644041575', '9801123339', '9872264189', '9873538472', '9860830966', '9830826490', '+977-1-5428194', '9731283648', '9652935037', '9702006458', '9851123339']***
