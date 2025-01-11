from eth_account.messages import encode_defunct
from fastapi import HTTPException
from web3 import Web3


def verify_metamask_message_signature(signature: str) -> str:
    message = f"Authenticate on NFT lootboxes"
    encoded_message = encode_defunct(text=message)

    try:
        recovered_address = Web3().eth.account.recover_message(encoded_message, signature=signature)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return Web3.to_checksum_address(recovered_address)
