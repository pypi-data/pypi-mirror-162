import re
import smtplib
import dns.resolver
import pandas as pd
import numpy as np

def verify_email(inputAddress):
  # Address used for SMTP MAIL FROM command  
  fromAddress = 'corn@bt.com'

  # Simple Regex for syntax checking
  regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'

  # Email address to verify
  #inputAddress = input('Please enter the emailAddress to verify:')
  addressToVerify = str(inputAddress)

  # Syntax check
  match = re.match(regex, addressToVerify)
  if match == None:
    return False
    
  # Get domain for DNS lookup
  splitAddress = addressToVerify.split('@')
  domain = str(splitAddress[1])
  # print('Domain:', domain)

  try:
    # MX record lookup
    records = dns.resolver.resolve(domain, 'MX')
    mxRecord = records[0].exchange
    mxRecord = str(mxRecord)

    # SMTP lib setup (use debug level for full output)
    server = smtplib.SMTP()
    server.set_debuglevel(0)

    # SMTP Conversation
    server.connect(mxRecord)
    server.helo(server.local_hostname) ### server.local_hostname(Get local server hostname)
    server.mail(fromAddress)
    code, message = server.rcpt(str(addressToVerify))
    server.quit()
  except:
    return False

  # Assume SMTP response 250 is success
  if code == 250:
    return True
  else:
    return False

def verify_multiple_email(emailAddress, name):  
  test_result = []
  for email in emailAddress:
    if (verify_email(email)):
      result = {'Name': name, 'Email': email, 'Status': 'Veified'}
      test_result.append(result)
  test_result_df = pd.DataFrame(test_result)
  return test_result_df

def generate_two_name(first_name, last_name, domain):
  patterns = []
  patterns.append(first_name + last_name + domain)
  patterns.append(last_name + first_name + domain)
  patterns.append(first_name + '.' + last_name + domain)
  patterns.append(last_name + '.' + first_name + domain)
  patterns.append(first_name + '_' + last_name + domain)
  patterns.append(last_name + '_' + first_name + domain)
  patterns.append(first_name + '-' + last_name + domain)
  patterns.append(last_name + '-' + first_name + domain)
  return patterns

def generate_three_name(first, last, middle, domain):
  patterns = []
  patterns.append(first + middle + last + domain)
  patterns.append(first + last + middle + domain)
  patterns.append(middle + first + last + domain)
  patterns.append(middle + last + first + domain)
  patterns.append(last + first + middle + domain)
  patterns.append(last + middle + first + domain)
  
  patterns.append(first + '.' + middle + '.' + last + domain)
  patterns.append(first + '.' + last + '.' + middle + domain)
  patterns.append(middle + '.' + first + '.' + last + domain)
  patterns.append(middle + '.' + last + '.' + first + domain)
  patterns.append(last + '.' + first + '.' + middle + domain)
  patterns.append(last + '.' + middle + '.' + first + domain)

  patterns.append(first + '_' + middle + '_' + last + domain)
  patterns.append(first + '_' + last + '_' + middle + domain)
  patterns.append(middle + '_' + first + '_' + last + domain)
  patterns.append(middle + '_' + last + '_' + first + domain)
  patterns.append(last + '_' + first + '_' + middle + domain)
  patterns.append(last + '_' + middle + '_' + first + domain)

  patterns.append(first + '-' + middle + '-' + last + domain)
  patterns.append(first + '-' + last + '-' + middle + domain)
  patterns.append(middle + '-' + first + '-' + last + domain)
  patterns.append(middle + '-' + last + '-' + first + domain)
  patterns.append(last + '-' + first + '-' + middle + domain)
  patterns.append(last + '-' + middle + '-' + first + domain)
  return patterns

def generate_pattern(first_name='', last_name='', middle_name='', domain=''):
  first_initial = ''
  last_initial = ''
  middle_initial = ''
  if len(first_name) > 0:
  	first_initial = first_name[0]
  if len(last_name) > 0:
    last_initial = last_name[0]
  if len(middle_name) > 0:
  	middle_initial = middle_name[0]

  domain = '@' + domain
  patterns = []
  patterns.append(last_name + domain)
  patterns.append(last_initial + domain)

  if (first_name != '' and middle_name == ''):
    patterns.append(first_initial + domain)
    patterns.append(first_name + domain)

    patterns += generate_two_name(first_name, last_name, domain)
    patterns += generate_two_name(first_name, last_initial, domain)
    patterns += generate_two_name(first_initial, last_name, domain)
    patterns += generate_two_name(first_initial, last_initial, domain)

  if (first_name == '' and middle_name != ''):
    patterns.append(middle_initial + domain)
    patterns.append(middle_name + domain)
    
    patterns += generate_two_name(middle_name, last_name, domain)
    patterns += generate_two_name(middle_name, last_initial, domain)
    patterns += generate_two_name(middle_initial, last_name, domain)
    patterns += generate_two_name(middle_initial, last_initial, domain)

  if(middle_name != '' and first_name != ''):
    patterns.append(last_initial + domain)
    patterns.append(last_name + domain)

    patterns += generate_two_name(first_name, middle_name, domain)
    patterns += generate_two_name(first_name, middle_initial, domain)
    patterns += generate_two_name(first_initial, middle_name, domain)
    patterns += generate_two_name(first_initial, middle_initial, domain)
    patterns += generate_two_name(last_name, middle_name, domain)
    patterns += generate_two_name(last_name, middle_initial, domain)
    patterns += generate_two_name(last_initial, middle_name, domain)
    patterns += generate_two_name(last_initial, middle_initial, domain)

    patterns += generate_three_name(first_name, last_name, middle_name, domain)
    patterns += generate_three_name(first_name, last_name, middle_initial, domain)
    patterns += generate_three_name(first_name, last_initial, middle_name, domain)
    patterns += generate_three_name(first_name, last_initial, middle_initial, domain)
    patterns += generate_three_name(first_initial, last_name, middle_name, domain)
    patterns += generate_three_name(first_initial, last_name, middle_initial, domain)
    patterns += generate_three_name(first_initial, last_initial, middle_name, domain)
    patterns += generate_three_name(first_initial, last_initial, middle_initial, domain)

  return patterns

def email_finder(first_name, middle_name, last_name, domain):
  first_name = first_name.lower()
  middle_name = middle_name.lower()
  last_name = last_name.lower()
  domain = domain.lower()

  name = first_name + ' ' + middle_name + ' ' + last_name
  emails = generate_pattern(first_name, last_name, middle_name, domain)
  test_result = verify_multiple_email(emails, name)
  
  if('Status' in test_result):
    return (test_result)
  else:
    return ('NOT FOUND')