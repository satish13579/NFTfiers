import base64
from algosdk.v2client import algod,indexer
from algosdk import account, mnemonic
from algosdk import util,transaction,error
import json,base64
from beaker import client, sandbox, consts
import contract
API_KEY="LFIoc7BZFY4CAAHfCC2at53vp5ZabBio5gAQ0ntL"

def create_application():
    algod_address = "https://testnet-algorand.api.purestake.io/ps2"
    algod_token = ""
    headers = {
        "X-API-Key": API_KEY,
    }
    sender="CVPT5JBQ7RCXDVSRW7TSFJPBKRTDCOETDZE6GQKPN7NVEKDXIJWN3FKEAM"
    mnemoni="type deer chief harbor palm wagon resist uphold antenna remain sun feel soccer before napkin noodle net punch pistol polar angle daughter paddle about dwarf"
    private_key = mnemonic.to_private_key(mnemoni)

    with open("approval.teal", "r") as f:
        approval_program = f.read()

    with open("clear.teal", "r") as f:
        clear_program = f.read()

    acct=sandbox.SandboxAccount(address=sender,private_key=private_key)
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)
    app_client = client.ApplicationClient(
        algod_client, contract.app, signer=acct.signer
    )

    app_id, app_address, _ = app_client.create()
    print(f"Deployed Application ID: {app_id} Address: {app_address}")

    # approval_result = algod_client.compile(approval_program)
    # approval_binary = base64.b64decode(approval_result["result"])

    # clear_result = algod_client.compile(clear_program)
    # clear_binary = base64.b64decode(clear_result["result"])
    # gstate=transaction.StateSchema(2,2)
    # print(gstate)
    # lstate=transaction.StateSchema(0,0)
    # print(lstate)
    # create_txn=transaction.ApplicationCreateTxn(sender,algod_client.suggested_params(),transaction.OnComplete.NoOpOC,approval_binary,clear_binary,gstate,lstate)
    # screate_txn=create_txn.sign(private_key)
    # txid = algod_client.send_transaction(screate_txn)
    # result = transaction.wait_for_confirmation(algod_client, txid, 4)
    # app_id = result["application-index"]
    # print(f"Created app with id: {app_id}")

create_application()