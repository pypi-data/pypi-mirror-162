from pyteal import *
import json
import urllib
from algosdk.v2client import algod

# Takes uint64 and returns it as uvarint array
@Subroutine(TealType.bytes)
def __Itovi(num):
    output = ScratchVar(TealType.bytes)
    temp = ScratchVar(TealType.uint64)
    main = Seq([
        output.store(Substring(Itob(num), Int(7), Int(8))),
        If(num >= Int(128)).Then(
            Seq([
                temp.store(num / Int(128)),
                While(temp.load() >= Int(128)).Do(
                Seq([
                    output.store(Concat(output.load(), Substring(Itob(temp.load()), Int(7), Int(8)))),
                    temp.store(temp.load() >> Int(7))
                    ])),
                output.store(Concat(output.load(), Substring(Itob(temp.load()), Int(7), Int(8))))
            ]))
    ])
    return Seq([main, Return(output.load())])

def __get(lookup):
    # V1 values
    dict = {}
    dict["validator_id"] = 684650147
    dict["gard_id"] = 684649988
    dict["close_fee_id"] = 684649986
    dict["open_fee_id"] = 684649985
    dict["devfee_address"] = "MTMJ5ADRK3CFG3HGUI7FS4Y55WGCUO5CRUMVNBZ7FW5IIG6T3IU2VJHUMM"
    dict["reserve_address"] = "J2E2XXS4FTW3POVNZIHRIHTFRGOWEWX65NFYIVYIA27HUK63NWT65OLB2Y"
    dict["reserve_logic_signature"] = "BiAGAITcu8YCBAGAAaPdu8YCJgIHUHJvZ3JhbaoEBiAJAKPdu8YCAwIBBITcu8YCBQYmAiC+6esZvMn5n50shvOEPMSEkq1eFvRvDfUchJXaZw3aYiBk2J6AcVbEU2zmoj5Zcx3tjCo7oo0ZVoc/LbqEG9PaKS0XIhJAAV0tFyEEEkABLS0XJRJAAOItFyQSQAChLRchBRJAAIEtFyEHEkAASi0XIQgSQAABADEYIxIxGSISEDYaAIAHQXVjdGlvbhIQMgQkEjMAGCMSEDMAGSISEDcAGgCACENsZWFyQXBwEhAzARkkEhARQgFaMgQkEjMAGSISEDMAGCMSEDcAGgCACE1vcmVHQVJEEhAzAQAoEhAzAQcpEhBCASsxGSEEEjEYIxIQMSAyAxIQMQEiEhBCARMyBCEFEjMAGSISEDMAGCMSEDcAGgCACkNsb3NlTm9GZWUSEDcAMAAhBhIQMwEAKBIQMwIZJBIQQgDZMgQhBRIzABkiEhAzABgjEhA3ABoAgAhDbG9zZUZlZRIQNwAwACEGEhAzAQAoEhAzAhkkEhAzAwcpEhAzAwkoEhBCAJUyBCEHEjMAGSUSEDMAGCMSEDcAMAAhBhIQMwMUKRIQMwQUKBIQQgBtMwAIgXQSMwAAKBIQMwEgMgMSEDMBASISEDIEJRJAADEyBCQSMwEQIQgSEDMBGCMTEDMCGCMSEDMCGSISEDcCGgCACEFwcENoZWNrEhAQQgAcMwEQIQQSMwEIIhIQMwEJMgMSEDMBECUSEUL/4EMtFyISQAEcLRclEkAATy0XgQISQAABADIEgQMSMwAZIhIQMwAYIQUSEDcAGgCACE1vcmVHQVJEEhA3ADAAIxIQMwIQJBIQMwIBIhIQMwIVMgMSEDMCIDIDEhBCAOUyBCQSMwAZIhIQMwAYIQUSEDcAGgCAC05ld1Bvc2l0aW9uEhA3ABwBMwEHEhA3ADAAIxIQMwEQJRIQMwEAMwAAEhAzAQcoKVBXAB4zAABQKClQgT6BiQNYUDcAMAGIAIZQKClQgcgDgWlYUAMSEDMCECUSEDMCADMBABIQMwIHgCBk2J6AcVbEU2zmoj5Zcx3tjCo7oo0ZVoc/LbqEG9PaKRIQMwMQJBIQMwMRIxIQMwMBIhIQMwMVMgMSEDMDIDIDEhBCAB8xECQSMREjEhAxEiISEDEgMgMSEDEVMgMSEDEBIhIQQzUANAAWVwcBNQE0ACEED0EAMjQAIQQKNQI0AiEED0AADjQBNAIWVwcBUDUBQgAVNAE0AhZXBwFQNQE0AoEHkTUCQv/VNAGJ"
    with urllib.request.urlopen(
        "https://storage.googleapis.com/algo-pricing-data-2022/latest_pricing.json"
    ) as url:
        data = json.loads(url.read().decode())
        dict["current_price"] = data["float_price"]
    return dict[lookup]

def __get_cdp_debt(client, cdp_address):
    
    validator_id = __get("validator_id")

    result = client.account_application_info(cdp_address, validator_id)
    if 'message' in result.keys(): return 0
    try:
        for localval in result['app-local-state']["key-value"]:
            if localval['key'] == 'R0FSRF9ERUJU':
                return localval['value']['uint']
    except:
        return 0

def __cdp(user, cdp_id):

    # V1 values
    valid_id = __get("validator_id")
    stab_id = __get("gard_id")
    devfee_add = __get("devfee_address")

    user_address = Addr(user)

    stable_id = Int(stab_id)
    validator_id = Int(valid_id)
 
    devfee_address = Addr(devfee_add)

    # arg_id = 0
    # txn 0 -> self vote account
    # txn 1 -> payment txn of 0 
    Vote = And(
        Gtxn[0].amount() == Int(cdp_id),
        Gtxn[0].sender() == user_address,
        Gtxn[1].rekey_to() == Global.zero_address(),
        Gtxn[1].fee() == Int(0),
        If(Global.group_size() == Int(2)).Then(
            Or(
                And(
                Gtxn[1].type_enum() == TxnType.Payment,
                Gtxn[1].amount() == Int(0),
                Gtxn[1].close_remainder_to() == Global.zero_address()
            ),
                Gtxn[1].type_enum() == TxnType.KeyRegistration,
            )
        ).Else(
            And(
                Global.group_size() == Int(3),
                Gtxn[1].type_enum() == TxnType.ApplicationCall,
                Gtxn[1].application_id() != validator_id,
                Gtxn[2].application_id() == validator_id,
                Gtxn[2].on_completion() == OnComplete.NoOp,
                Gtxn[2].application_args[0] == Bytes("AppCheck"),
            )
        )
    )
    
    # To liquidate accounts with insufficient collateral
    # arg_id = 1
    # txn 0 -> Application call to price validator (application args["liquidate"])
    # txn 1 -> payment to buyer
    # txn 2 -> payment to reserve (in GARD)
    # txn 3 -> payment to devfee address (in GARD)
    # txn 4 -> payment to user address (in GARD)
    Liquidate = And(
        Global.group_size() == Int(5),
        Gtxn[0].on_completion() == OnComplete.CloseOut,
        Gtxn[0].application_id() == validator_id,
        Gtxn[0].assets[0] == stable_id,
        Gtxn[3].asset_receiver() == devfee_address,
        Gtxn[4].asset_receiver() == user_address
    )

    # For user to redeem outstanding stable tokens for collateral w/ fee
    # arg_id = 2
    # txn 0 -> Application call (application args[Bytes("CloseFee")])
    #                           (asset array args[stable_id])
    # txn 1 -> stable to reserve (from holder)
    # txn 2 -> Close out validator local state
    # txn 3 -> payment to fee account and the rest to user
    RedeemStableFee = And(
        Global.group_size() == Int(4),
        Gtxn[0].on_completion() == OnComplete.NoOp,
        Gtxn[0].application_id() == validator_id,
        Gtxn[0].application_args[0] == Bytes("CloseFee"),
        Gtxn[0].assets[0] == stable_id,
        Gtxn[1].sender() == user_address,
        Gtxn[2].on_completion() == OnComplete.ClearState,
        Gtxn[3].receiver() == devfee_address,
        Gtxn[3].close_remainder_to() == user_address,
    )

    # For user to redeem outstanding stable tokens for collateral w/out fee
    # arg_id = 3
    # txn 0 -> Application call (to obtain reserve address) (application args[Bytes("CloseNoFee")])
    #                           (asset array args[stable_id])
    # txn 1 -> stable to reserve (from holder)
    # txn 2 -> Close out validator local state
    # Txn 3 -> payment to holder
    RedeemStableNoFee = And(
        Global.group_size() == Int(4),
        Gtxn[0].on_completion() == OnComplete.NoOp,
        Gtxn[0].application_id() == validator_id, 
        Gtxn[0].application_args[0] == Bytes("CloseNoFee"),
        Gtxn[0].assets[0] == stable_id,
        Gtxn[1].sender() == user_address,
        Gtxn[2].on_completion() == OnComplete.ClearState,
    )

    # arg_id = 4
    Validator_OptIn = And(
        Txn.on_completion() == OnComplete.OptIn,
        Txn.application_id() == validator_id,
        Txn.rekey_to() == Global.zero_address(),
        Txn.fee() == Int(0)
    )

    # For user to mint more GARD leveraging the algo balance of the position
    # arg_id = 5
    # txn 0 -> Application call (application args[Bytes("MoreGARD)])
    #                           (asset array args[stable_id])
    # txn 1 -> devfee payment 
    # txn 2 -> GARD transfer to user
    More_gard = And(
        Global.group_size() == Int(3),
        Gtxn[0].on_completion() == OnComplete.NoOp,
        Gtxn[0].application_id() == validator_id, 
        Gtxn[0].application_args[0] == Bytes("MoreGARD"),
        Gtxn[1].sender() == user_address,
        Gtxn[1].receiver() == devfee_address
    )

    # arg_id = 6
    StartAuction = Or(
        And(
            Txn.application_id() == validator_id,
            Txn.on_completion() == OnComplete.NoOp,
            Txn.application_args[0] == Bytes("Auction"),
        ), 
        And(
            Global.group_size() == Int(3),
            Gtxn[0].application_id() == validator_id,
            Gtxn[0].on_completion() == OnComplete.NoOp,
            Gtxn[0].application_args[0] == Bytes("ClearApp"),
            Gtxn[1].on_completion() == OnComplete.ClearState
        )
    )

    # Only txns of one of the 7 types will be approved
    program = Cond(
        [Btoi(Arg(0)) == Int(0), Vote],
        [Btoi(Arg(0)) == Int(1), Liquidate],
        [Btoi(Arg(0)) == Int(2), RedeemStableFee],
        [Btoi(Arg(0)) == Int(3), RedeemStableNoFee],
        [Btoi(Arg(0)) == Int(4), Validator_OptIn],
        [Btoi(Arg(0)) == Int(5), More_gard],
        [Btoi(Arg(0)) == Int(6), StartAuction]
    )

    return program

"""
def __reserve():

    cl = __algod_client()

    # V1 values
    valid_id = __get("validator_id")
    stable_id = __get("gard_id")
    devfee_add = __get("devfee_address")

    # Create template
    program = __cdp("RHN53AKL3IJGOIF5BJTIUFDOH4KMPR45XS4JM63W46PWMFFR3PPZXF5DOQ", 12)
    compiled = compileTeal(program, Mode.Signature, version=6)
    response = cl.compile(compiled)
    template = response["result"]
    template = 'BiAGAITcu8YCBAGAAaPdu8YCJgIHUHJvZ3JhbaoEBiAJAKPdu8YCAwIBBITcu8YCBQYmAiC+6esZvMn5n50shvOEPMSEkq1eFvRvDfUchJXaZw3aYiBk2J6AcVbEU2zmoj5Zcx3tjCo7oo0ZVoc/LbqEG9PaKS0XIhJAAV0tFyEEEkABLS0XJRJAAOItFyQSQAChLRchBRJAAIEtFyEHEkAASi0XIQgSQAABADEYIxIxGSISEDYaAIAHQXVjdGlvbhIQMgQkEjMAGCMSEDMAGSISEDcAGgCACENsZWFyQXBwEhAzARkkEhARQgFaMgQkEjMAGSISEDMAGCMSEDcAGgCACE1vcmVHQVJEEhAzAQAoEhAzAQcpEhBCASsxGSEEEjEYIxIQMSAyAxIQMQEiEhBCARMyBCEFEjMAGSISEDMAGCMSEDcAGgCACkNsb3NlTm9GZWUSEDcAMAAhBhIQMwEAKBIQMwIZJBIQQgDZMgQhBRIzABkiEhAzABgjEhA3ABoAgAhDbG9zZUZlZRIQNwAwACEGEhAzAQAoEhAzAhkkEhAzAwcpEhAzAwkoEhBCAJUyBCEHEjMAGSUSEDMAGCMSEDcAMAAhBhIQMwMUKRIQMwQUKBIQQgBtMwAIgXQSMwAAKBIQMwEgMgMSEDMBASISEDIEJRJAADEyBCQSMwEQIQgSEDMBGCMTEDMCGCMSEDMCGSISEDcCGgCACEFwcENoZWNrEhAQQgAcMwEQIQQSMwEIIhIQMwEJMgMSEDMBECUSEUL/4EMtFyISQAEcLRclEkAATy0XgQISQAABADIEgQMSMwAZIhIQMwAYIQUSEDcAGgCACE1vcmVHQVJEEhA3ADAAIxIQMwIQJBIQMwIBIhIQMwIVMgMSEDMCIDIDEhBCAOUyBCQSMwAZIhIQMwAYIQUSEDcAGgCAC05ld1Bvc2l0aW9uEhA3ABwBMwEHEhA3ADAAIxIQMwEQJRIQMwEAMwAAEhAzAQcoKVBXAB4zAABQKClQgT6BiQNYUDcAMAGIAIZQKClQgcgDgWlYUAMSEDMCECUSEDMCADMBABIQMwIHgCBk2J6AcVbEU2zmoj5Zcx3tjCo7oo0ZVoc/LbqEG9PaKRIQMwMQJBIQMwMRIxIQMwMBIhIQMwMVMgMSEDMDIDIDEhBCAB8xECQSMREjEhAxEiISEDEgMgMSEDEVMgMSEDEBIhIQQzUANAAWVwcBNQE0ACEED0EAMjQAIQQKNQI0AiEED0AADjQBNAIWVwcBUDUBQgAVNAE0AhZXBwFQNQE0AoEHkTUCQv/VNAGJ'

    print("THIS IS THE TEMPLATE:")
    print(template)

    # public key of DAO Devfee address
    devfee_address = Addr(devfee_add)

    validator_id = Int(valid_id)

    # template base64 encoding from compiling cdp("RHN53AKL3IJGOIF5BJTIUFDOH4KMPR45XS4JM63W46PWMFFR3PPZXF5DOQ", 12)
    # from cdp_escrow.py
    # address will be replaced with user address
    contract_logic = template
    
    print(contract_logic)
    y = Concat(Bytes("Program"), Bytes("base64", contract_logic))

    x1 = Substring(y, Int(0), Int(30))
    x2 = Substring(y, Int(62), Int(455)) 
    x3 = Substring(y, Int(456), Int(561))

    contract_addr = Sha512_256(Concat(x1, Gtxn[0].sender(), x2, __Itovi(Gtxn[0].assets[1]), x3))

    # For Opt-in to GARD 
    # arg_id = 0
    optInStable = And(
        Txn.type_enum() == TxnType.AssetTransfer,
        Txn.xfer_asset() == Int(stable_id),
        Txn.asset_amount() == Int(0),
        Txn.rekey_to() == Global.zero_address(),
        Txn.asset_close_to() == Global.zero_address(),
        Txn.fee() == Int(0)
    )

    # For opening new position 
    # arg_id = 1
    # txn 0 -> Call to price validator (application args["NewPosition", Int(unix_start)]) all as bytes
    # account array [sender, contract_address] 
    # txn 1 -> proper algos to contract address (pays fee)
    # txn 2 -> Algo transfer to Tapera Fee account
    # txn 3 -> GARD transfer to User
    Core = And(
        Global.group_size() == Int(4),
        Gtxn[0].on_completion() == OnComplete.NoOp,
        Gtxn[0].application_id() == validator_id, 
        Gtxn[0].application_args[0] == Bytes("NewPosition"),
        Gtxn[0].accounts[1] == Gtxn[1].receiver(),
        Gtxn[0].assets[0] == Int(stable_id),
        Gtxn[1].type_enum() == TxnType.Payment,
        Gtxn[1].sender() == Gtxn[0].sender(),
        # contract address computed by filling in template
        Gtxn[1].receiver() == contract_addr,
        Gtxn[2].type_enum() == TxnType.Payment,
        # Gtxn[2].amount() is Checked by ApplicationCall
        Gtxn[2].sender() == Gtxn[1].sender(),
        Gtxn[2].receiver() == devfee_address,
        Gtxn[3].type_enum() == TxnType.AssetTransfer,
        Gtxn[3].xfer_asset() == Int(stable_id),
        Gtxn[3].fee() == Int(0),
        # Amount of GARD to be minted
        Gtxn[3].asset_close_to() == Global.zero_address(),
        Gtxn[3].rekey_to() == Global.zero_address(),

    )

    # For minting more from an open position
    more_gard = And(
        Global.group_size() == Int(3),
        Gtxn[0].on_completion() == OnComplete.NoOp,
        Gtxn[0].application_id() == validator_id, 
        Gtxn[0].application_args[0] == Bytes("MoreGARD"),
        Gtxn[0].assets[0] == Int(stable_id),
        Gtxn[2].type_enum() == TxnType.AssetTransfer,
        Gtxn[2].fee() == Int(0),
        Gtxn[2].asset_close_to() == Global.zero_address(),
        Gtxn[2].rekey_to() == Global.zero_address(),
    )

    # Approved Txns must be one of the 3 types
    program = Cond(
        [Btoi(Arg(0)) == Int(0), optInStable],
        [Btoi(Arg(0)) == Int(1), Core],
        [Btoi(Arg(0)) == Int(2), more_gard]
        )

    return program
"""