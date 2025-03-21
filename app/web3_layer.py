import base64
import hashlib
from datetime import datetime
import jwt
from fastapi import HTTPException
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from starlette import status
from config import SECRET_KEY, ALGORITHM
from schemas import TonProofItem, TonPayload


def verify_signature(key, message, signature):
    verify_key = VerifyKey(key)
    try:
        verify_key.verify(message, signature)
        return True
    except (BadSignatureError, TypeError, ValueError):
        return False


def generate_ton_payload(ttl: int = 600) -> TonPayload:
    payload = {
        "data": "Auth on NFT lootboxes",
        "exp": int(datetime.now().timestamp()) + ttl
    }
    return TonPayload(payload=jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM))


def verify_ton_proof(proof: TonProofItem) -> str:
    """
    Проверяет подпись TON Proof.

    :param proof: Объект с данными подписи (payload, signature, domain, timestamp и т.д.)
    :return address
    """

    # TODO check proof.proof.domain
    try:
        jwt.decode(proof.proof.payload, SECRET_KEY, algorithms=[ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid payload: {e}")

    if proof.proof.timestamp < datetime.now().timestamp() / 1000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Proof expired")

    pubkey_bytes = bytes(bytearray.fromhex(proof.public_key))

    # Извлекаем workchain и хэш адреса
    workchain, address = proof.address.split(':')
    address_hash = bytes.fromhex(address)

    # Подготавливаем данные для подписи
    ton_proof_prefix = b"ton-proof-item-v2/"
    wc = int(workchain).to_bytes(4, byteorder='big')
    ts = int(proof.proof.timestamp).to_bytes(8, byteorder='little')
    dl = proof.proof.domain.lengthBytes.to_bytes(4, byteorder='little')

    # Собираем сообщение для хэширования
    msg = (
        ton_proof_prefix +
        wc +
        address_hash +
        dl +
        proof.proof.domain.value.encode('utf-8') +
        ts +
        proof.proof.payload.encode('utf-8')
    )

    # Хэшируем сообщение с помощью SHA-256
    msg_hash = hashlib.sha256(msg).digest()

    # Добавляем префикс для TON Connect
    ton_connect_prefix = b"ton-connect"
    full_msg = b'\xff\xff' + ton_connect_prefix + msg_hash

    # Хэшируем финальное сообщение
    full_msg_hash = hashlib.sha256(full_msg).digest()

    # Декодируем подпись из base64
    proof_signature_bytes = base64.b64decode(proof.proof.signature)

    # Проверяем подпись с использованием публичного ключа
    if not verify_signature(pubkey_bytes, full_msg_hash, proof_signature_bytes):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    return proof.address