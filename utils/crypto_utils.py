import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import os
from dotenv import load_dotenv
from utils.log_utils import logger

load_dotenv()

class CryptoUtils:
    @staticmethod
    def md5_encrypt(text):
        """MD5加密"""
        if not isinstance(text, str):
            text = str(text)
        md5 = hashlib.md5()
        md5.update(text.encode('utf-8'))
        return md5.hexdigest()

    @staticmethod
    def aes_encrypt(text, key=None):
        """AES加密（CBC模式）"""
        key = key or os.getenv("AES_SECRET_KEY")
        if not key:
            raise ValueError("AES密钥未配置")
            
        key = key.encode('utf-8')
        if len(key) not in [16, 24, 32]:
            raise ValueError("AES密钥长度必须为16、24或32字节")
            
        if not isinstance(text, str):
            text = str(text)
        text = text.encode('utf-8')
        
        # 生成随机IV
        iv = os.urandom(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # 填充并加密
        encrypted = cipher.encrypt(pad(text, AES.block_size))
        
        # 返回IV+密文的Base64编码
        return base64.b64encode(iv + encrypted).decode('utf-8')

    @staticmethod
    def aes_decrypt(encrypted_text, key=None):
        """AES解密（CBC模式）"""
        key = key or os.getenv("AES_SECRET_KEY")
        if not key:
            raise ValueError("AES密钥未配置")
            
        key = key.encode('utf-8')
        try:
            # 解码Base64
            data = base64.b64decode(encrypted_text)
            
            # 分离IV和密文
            iv = data[:16]
            encrypted = data[16:]
            
            # 解密
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"AES解密失败: {str(e)}")
            raise

    @staticmethod
    def rsa_encrypt(text, public_key=None):
        """RSA加密"""
        public_key = public_key or os.getenv("RSA_PUBLIC_KEY")
        if not public_key:
            raise ValueError("RSA公钥未配置")
            
        if not isinstance(text, str):
            text = str(text)
        text = text.encode('utf-8')
        
        key = RSA.import_key(public_key)
        cipher = PKCS1_OAEP.new(key)
        encrypted = cipher.encrypt(text)
        return base64.b64encode(encrypted).decode('utf-8')

    @staticmethod
    def rsa_decrypt(encrypted_text, private_key=None):
        """RSA解密"""
        private_key = private_key or os.getenv("RSA_PRIVATE_KEY")
        if not private_key:
            raise ValueError("RSA私钥未配置")
            
        try:
            encrypted = base64.b64decode(encrypted_text)
            key = RSA.import_key(private_key)
            cipher = PKCS1_OAEP.new(key)
            return cipher.decrypt(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"RSA解密失败: {str(e)}")
            raise

    @staticmethod
    def sign(text, private_key=None):
        """生成RSA签名（SHA256）"""
        private_key = private_key or os.getenv("RSA_PRIVATE_KEY")
        if not private_key:
            raise ValueError("RSA私钥未配置")
            
        if not isinstance(text, str):
            text = str(text)
            
        key = RSA.import_key(private_key)
        hash_obj = SHA256.new(text.encode('utf-8'))
        signer = pkcs1_15.new(key)
        signature = signer.sign(hash_obj)
        return base64.b64encode(signature).decode('utf-8')

    @staticmethod
    def verify_sign(text, signature, public_key=None):
        """验证RSA签名"""
        public_key = public_key or os.getenv("RSA_PUBLIC_KEY")
        if not public_key or not signature:
            return False
            
        if not isinstance(text, str):
            text = str(text)
            
        try:
            key = RSA.import_key(public_key)
            hash_obj = SHA256.new(text.encode('utf-8'))
            verifier = pkcs1_15.new(key)
            verifier.verify(hash_obj, base64.b64decode(signature))
            return True
        except (ValueError, TypeError, Exception) as e:
            logger.warning(f"签名验证失败: {str(e)}")
            return False
