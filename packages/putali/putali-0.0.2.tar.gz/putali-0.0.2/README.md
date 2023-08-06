# putali

Under construction! Give a try at it!

Developed by Ujjawal Shah (c) 2022

## Examples of How To Use Package

Get contact email from the website homepage

```python
import putali

homepage = putali.Scrollhomepage('https://www.bok.com.np/')
email_adresses = homepage.emails()
print(f'emails: {email_adresses}')
```

Get phonenumbers from the homepage

```python
import putali

homepage = putali.Scrollhomepage('https://www.bok.com.np/')

#phonenumber is only for Nepal right now
phone_numbers = homepage.phonenumber()
print(f'phone numbers: {phone_numbers}')
```
