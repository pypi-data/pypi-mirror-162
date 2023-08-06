from pyteal import compileTeal, Mode
import base64
from algosdk.future.transaction import PaymentTxn, AssetTransferTxn, calculate_group_id
from algosdk.future.transaction import ApplicationCallTxn, LogicSig, LogicSigTransaction
from gardsdk.helpers import __get, __get_cdp_debt, __cdp

def add_collateral(client, addr, cdp_addr, amount):
    print(client.suggested_params())
    return(PaymentTxn(addr, client.suggested_params(), cdp_addr, amount))

def cdp_vote(usr_addr, client, account_id):

    # V1 values
    validator_id = __get("validator_id")

    # Transaction parameters   
    params = client.suggested_params()
    params.flat_fee = True
    params.fee = 2000

    # Get Logic for CDP
    program = __cdp(usr_addr, account_id)
    compiled = compileTeal(program, Mode.Signature, version=6)
    response = client.compile(compiled)
    program, contract_addr = response['result'], response['hash']

    # Confirm opted into validator
    try:
        assert(client.account_application_info(contract_addr, validator_id))
    except:
        print("Contract not opted in to validator")

    # Construct LogicSig
    prog = base64.decodebytes(program.encode())
    arg = (0).to_bytes(8, 'big')
    lsig = LogicSig(prog, args=[arg])

    # Construct Txns
    tx1 = PaymentTxn(usr_addr, params, usr_addr, account_id)
    params.fee = 0
    note = "Heyo World!".encode()
    tx2 = PaymentTxn(contract_addr, params, usr_addr, 0, note=note)

    # Assign group id
    grp_id = calculate_group_id([tx1, tx2])
    tx1.group = grp_id
    tx2.group = grp_id

    # Sign
    #stx1 = tx1.sign(key)
    stx2 = LogicSigTransaction(tx2, lsig)

    return [tx1, stx2]

def mint_from_existing(address, client, account_id, to_mint):

    # V1 values
    curr_price = __get("current_price")
    validator_id = __get("validator_id")
    gard_id = __get("gard_id")
    fee_id = __get("open_fee_id")
    devfee_address = __get("devfee_address")
    reserve_addr = __get("reserve_address")

    # Transaction parameters   ,
    params = client.suggested_params()
    params.flat_fee = True
    params.fee = 1000
 
    devfees = int(to_mint/(50*curr_price)) 
    devfees += 10000

    # Calculate contract address
    program = __cdp(address, account_id)
    compiled = compileTeal(program, Mode.Signature, version=6)
    response = client.compile(compiled)
    program, contract_addr = response['result'], response['hash']

    # Confirm opted into validator
    try:
        assert(client.account_application_info(contract_addr, validator_id))
    except:
        print("Contract not opted in to validator")

    # Construct LogicSig
    prog = base64.decodebytes(program.encode())
    arg = (5).to_bytes(8, 'big')
    lsig = LogicSig(prog, args=[arg])

    program = __get("reserve_logic_signature")
    logic = base64.decodebytes(program.encode())
    arg = (2).to_bytes(8, 'big')
    lsig2 = LogicSig(logic, [arg])
       
    # Construct Txns
    params.fee = 0
    validator_args = ["MoreGARD".encode()]
    tx1 = ApplicationCallTxn(contract_addr, params, validator_id, 0, app_args=validator_args, accounts=[contract_addr], foreign_apps=[53083112, fee_id], foreign_assets=[gard_id])
    params.fee = 3000
    tx2 = PaymentTxn(address, params, devfee_address, devfees)
    params.fee = 0
    tx3 = AssetTransferTxn(reserve_addr, params, address, to_mint, gard_id)

    # Assign group id
    grp_id = calculate_group_id([tx1, tx2, tx3])
    tx1.group = grp_id
    tx2.group = grp_id
    tx3.group = grp_id

    # Sign 
    stx1 = LogicSigTransaction(tx1, lsig)
    #stx2 = tx2.sign(key)
    stx3 = LogicSigTransaction(tx3, lsig2)

    return [stx1, tx2, stx3]

def liquidate(address, client, owner_address, account_id):
    
    # V1 values
    validator_id = __get("validator_id")
    gard_id = __get("gard_id")
    devfee_address = __get("devfee_address")
    reserve_addr = __get("reserve_address")

    # Transaction parameters
    params = client.suggested_params()
    params.flat_fee = True
    params.fee = 0

    # Calculate logic, address of CDP
    program = __cdp(owner_address, account_id)
    compiled = compileTeal(program, Mode.Signature, version=5)
    response = client.compile(compiled)
    contract_addr = response['hash']

    logic = base64.decodebytes(program.encode())
    arg = (1).to_bytes(8, 'big')
    lsig2 = LogicSig(logic, [arg])

    # Confirm opted into validator
    try:
        assert(client.account_application_info(contract_addr, validator_id))
    except:
        print("Contract not opted in to validator")

    # Get current values
    debt = __get_cdp_debt(client, contract_addr)    

    print("Auction Started!")
    # Construct Txns
    params.fee = 0
    tx1 = ApplicationCallTxn(contract_addr, params, validator_id, 2, accounts=[contract_addr], foreign_assets=[gard_id])
    tx2 = PaymentTxn(contract_addr, params, address, 0, close_remainder_to=address)
    params.fee = 5000
    tx3 = AssetTransferTxn(address, params, reserve_addr, debt, gard_id)
    params.fee = 0
    tx4 = AssetTransferTxn(address, params, devfee_address, debt//25, gard_id)
    tx5 = AssetTransferTxn(address, params, owner_address, 4*debt//25, gard_id)

     # Assign group id
    grp_id = calculate_group_id([tx1, tx2, tx3, tx4, tx5])
    tx1.group = grp_id
    tx2.group = grp_id
    tx3.group = grp_id
    tx4.group = grp_id
    tx5.group = grp_id 

    stx1 = LogicSigTransaction(tx1, lsig2)
    stx2 = LogicSigTransaction(tx2, lsig2)

    return [stx1, stx2, tx3, tx4, tx5]