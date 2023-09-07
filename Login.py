import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

#加密函数
def Cypher(original: bytes, salt: bytes):
    #使用PBKDF2HMAC函数生成密钥推导kdf
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
    #将原始信息original用kdf推导产生密钥basic
    basic = kdf.derive(original)
    #返回的是推导后的密钥basic和盐值salt的bytes类型连接
    return  basic + salt

#哈希计算函数
def SHA(data: bytes) -> bytes:
    hash = hashes.Hash(algorithm=hashes.SHA256())
    hash.update(data)
    return hash.finalize()

#主要的登录函数，需要的登录信息存储文件名称datafile作为参数
def login(datafile: str) -> tuple[bool, bytes]:
    #读取存储信息，每一行为一个用户的信息，传入saved_data列表储存
    try:
        with open(datafile, 'rb') as saved:
            saved_data = saved.read().split(b'\n')
    
    #没找到文件就建一个
    except:
        print('未发现所需文件。将创建。')
        with open(datafile, 'wb') as saved:
            saved.write(b'')
            saved_data = []


#判断用户输入的用户名是否存在，存在即已注册则登录，不存在则注册
    while(True):
        username = str.encode(input('请输入用户名：'))
        
        #遍历saved_data，每条信息base64解码后截取数据，前32位为加密的用户名，32~64位为加密密码，后32位为盐值
        for i in range(len(saved_data)):
            savedCypher = base64.urlsafe_b64decode(saved_data[i])
            sha_username = savedCypher[:32]
            
            #计算输入的用户名的哈希，若结果和存储的哈希值一致则判断用户名已存在，读取此用户的密码+盐值和单独盐值
            if sha_username == SHA(username):
                savedSalt = savedCypher[-32:]
                savedCypherPwdsalt = savedCypher[32:]
                password = str.encode(input('请输入密码：'))
                
                #使用用户输入的密码和储存的盐值进行加密，若结果和存储的加密密码一致则判断登录成功
                if savedCypherPwdsalt == Cypher(password, savedSalt):
                    print('登录成功。')
                    #返回新注册为False以及盐值
                    return(False, savedSalt)
                else:
                    print('密码错误。请重新登录。')
                    break
        
        reg = input('未发现用户。是否进行注册？(Y/N):').upper()
        
        #输入的不是Y或N提示输入错误，重新输入
        while(reg != 'Y' and reg != 'N'):
            reg = input('输入错误，请输入(Y/N):').upper()
            
        if reg == 'Y':
            password = str.encode(input('请输入密码：'))
            salt = os.urandom(32)
            sha_usr = SHA(username)
            CypherPwd = Cypher(password, salt)
            data = base64.urlsafe_b64encode(sha_usr + CypherPwd)
            #将已加密的且base64编码的新用户注册信息添加为saved_data的新元素并整个覆写回datafile
            saved_data.append(data)
            print('已成功注册。')    
            with open(datafile, 'wb') as writer:
                writer.write(b'\n'.join(saved_data).lstrip(b'\n'))
                
            #返回新注册为True以及盐值
            return(True, salt)

        #输入N不注册，此时pass回到最外层while(True)，重新开始输入用户名
        elif reg == 'N':
            pass

#测试用
if __name__ == '__main__':
    isLogin, key = login('users.txt')
    key = base64.urlsafe_b64encode(key)
    print(isLogin, key)