from pyteal import compileTeal, Mode
import base64
from algosdk import encoding
from algosdk.future.transaction import PaymentTxn, AssetTransferTxn, calculate_group_id, LogicSigTransaction
from algosdk.future.transaction import ApplicationCallTxn, ApplicationOptInTxn, ApplicationClearStateTxn, LogicSig
from time import time
from gardsdk.helpers import __get, __get_cdp_debt, __cdp

def open_cdp(address, client, total_malgs, GARD, account_id):
    
    # V1 values
    curr_price = __get("current_price")
    validator_id = __get("validator_id")
    gard_id = __get("gard_id")
    fee_id = __get("open_fee_id")
    devfee_address = __get("devfee_address")
    reserve_addr = __get("reserve_address")

    return_txns = []

    # Transaction parameters   ,
    params = client.suggested_params()
    params.flat_fee = True
    params.fee = 1000
            
    # Check if account holds GARD
    account_info = client.account_info(address)
    flag = False
    for scrutinized_asset in account_info['assets']:
        scrutinized_id = scrutinized_asset['asset-id']
        if (scrutinized_id == gard_id):
            flag = True
            break

    # Calculate contract address
    program = __cdp(address, account_id)
    compiled = compileTeal(program, Mode.Signature, version=6)
    response = client.compile(compiled)
    program, contract_addr = response['result'], response['hash']

    # Construct LogicSig
    prog = base64.decodebytes(program.encode())
    arg = (4).to_bytes(8, 'big')
    lsig = LogicSig(prog, args=[arg])

    params.fee = 2000
    txn1 = PaymentTxn(address, params, contract_addr, 300000)
    params.fee = 0
    txn2 = ApplicationOptInTxn(contract_addr, params, validator_id)
    if not flag:
        params.fee = 1000
        txn3 = AssetTransferTxn(address, params, address, 0, gard_id)
        note = "I'm opting in!".encode()
        g_id = calculate_group_id([txn1, txn2, txn3])
        txn1.group = g_id
        txn2.group = g_id
        txn3.group = g_id
        #stx1 = txn1.sign(key)
        stx2 = LogicSigTransaction(txn2, lsig)
        #stx3 = txn3.sign(key)
        return_txns.append([txn1, stx2, txn3])
        print("Contract opted into App + User opted into Stable")
    else:
        g_id = calculate_group_id([txn1, txn2])
        txn1.group = g_id
        txn2.group = g_id
        #stxn1 = txn1.sign(key)
        stxn2 = LogicSigTransaction(txn2, lsig)
        return_txns.append([txn1, stxn2])
        print("Contract opted into App")

    program = __get("reserve_logic_signature")
    logic = base64.decodebytes(program.encode())
    arg = (1).to_bytes(8, 'big')
    lsig = LogicSig(logic, [arg])
    
    devfees = int(GARD/(50*curr_price)) 
    devfees += 10000

    # Construct Txns
    params.fee = 0
    validator_args = ["NewPosition".encode(), (int(time())).to_bytes(8, 'big')]
    tx1 = ApplicationCallTxn(address, params, validator_id, 0, app_args=validator_args, accounts=[contract_addr], foreign_apps=[53083112, fee_id], foreign_assets=[gard_id, account_id])
    params.fee = 4000
    tx2 = PaymentTxn(address, params, contract_addr, total_malgs)
    params.fee = 0
    tx3 = PaymentTxn(address, params, devfee_address, devfees)
    tx4 = AssetTransferTxn(reserve_addr, params, address, GARD, gard_id)

    # Assign group id
    grp_id = calculate_group_id([tx1, tx2, tx3, tx4])
    tx1.group = grp_id
    tx2.group = grp_id
    tx3.group = grp_id
    tx4.group = grp_id

    # Sign 
    #stx1 = tx1.sign(key)
    #stx2 = tx2.sign(key)
    #stx3 = tx3.sign(key)
    stx4 = LogicSigTransaction(tx4, lsig)

    return_txns.append([tx1, tx2, tx3, stx4])

    return return_txns

def close_cdp_fee(usr_addr, client, account_id):

    # V1 values
    validator_id = __get("validator_id")
    gard_id = __get("gard_id")
    fee_id = __get("close_fee_id")
    devfee_addr = __get("devfee_address")
    reserve_addr = __get("reserve_address")
        
    # Transaction parameters
    params = client.suggested_params()
    params.flat_fee = True
    params.fee = 0

    # Calculate logic, address of CDP
    program = __cdp(usr_addr, account_id)
    compiled = compileTeal(program, Mode.Signature, version=6)
    response = client.compile(compiled)
    program, contract_addr = response['result'], response['hash']

    # Confirm opted into validator
    try:
        assert(client.account_application_info(contract_addr, validator_id))
    except:
        print("Contract not opted in to validator")

    # Get current values
    debt = __get_cdp_debt(client, contract_addr)    
    curr_price = __get("current_price")

    # Create LogicSig
    prog = base64.decodebytes(program.encode())
    arg = (2).to_bytes(8, 'big')
    lsig = LogicSig(prog, args=[arg])

    # Calculate fee
    fee = int(debt/(50*curr_price)) 
    fee += 10000

    validator_args = ["CloseFee".encode()]

    # Construct Txns
    tx1 = ApplicationCallTxn(contract_addr, params, validator_id, 0, app_args=validator_args, accounts=[contract_addr], foreign_apps=[53083112, fee_id], foreign_assets=[gard_id])
    params.fee = 5000
    tx2 = AssetTransferTxn(usr_addr, params, reserve_addr, debt, gard_id)
    params.fee = 0
    tx3 = ApplicationClearStateTxn(contract_addr, params, validator_id)
    tx4 = PaymentTxn(contract_addr, params, devfee_addr, fee, close_remainder_to=usr_addr)

    # Assign group id
    grp_id = calculate_group_id([tx1, tx2, tx3, tx4])
    tx1.group = grp_id
    tx2.group = grp_id
    tx3.group = grp_id
    tx4.group = grp_id

    # Sign
    stx1 = LogicSigTransaction(tx1, lsig)
    #stx2 = tx2.sign(key)
    stx3 = LogicSigTransaction(tx3, lsig)
    stx4 = LogicSigTransaction(tx4, lsig)

    return [stx1, tx2, stx3, stx4]