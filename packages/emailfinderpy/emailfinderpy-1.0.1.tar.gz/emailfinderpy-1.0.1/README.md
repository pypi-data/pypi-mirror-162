# emailfinderpy
## What is it?
This package can be use to verify emails. On top of that, it can also help you find email address. It might take a while to run the code since this code use brute force and try every single possible email combinations.

If you are interested to contribute, feel free to create a pull requests.

## How to use
Install this package using pip
`pip install emailfinderpy` or `pip3 install emailfinderpy`

```python
import emailfinderpy as em

print(em.verify_email('ssuntoso@gmail.com'))
# True

print(em.verify_multiple_email(['s.suntoso@gmail.com', 'ssuntoso@gmail.com'], 'Sean'))
#   Name                Email   Status
#0  Sean  s.suntoso@gmail.com  Veified
#1  Sean   ssuntoso@gmail.com  Veified

# email_finder(first_name, middle_name, last_name, domain)
print(em.email_finder('Sean', '', 'Suntoso', 'gmail.com'))
#            Name                Email   Status
#0  sean  suntoso   ssuntoso@gmail.com  Veified
#1  sean  suntoso  s.suntoso@gmail.com  Veified
```
