from algosdk import account, mnemonic

# create an account
private_key, address = account.generate_account()

# get the mnemonic associated with the account
mnemonic = mnemonic.from_private_key(private_key)

# write the credentials to a file
with open('user3.txt', 'w') as file:
    file.write(f'user public key: {address}\n')
    file.write(f'user private key: {private_key}\n')
    file.write(f'user mnemonic: {mnemonic}\n')
    print("user Credentials Saved in 'create2.txt' File")
