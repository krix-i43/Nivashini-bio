from flask import Flask, request, jsonify, make_response  # make_response added here
import requests
import binascii
import jwt
import urllib3
from urllib.parse import urlparse, parse_qs
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

try:
    import my_pb2
    import output_pb2
    import output_pb3
except ImportError:
    pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'

FREEFIRE_UPDATE_URL = "https://client.ind.freefiremobile.com/UpdateSocialBasicInfo"
MAJOR_LOGIN_URL = "https://loginbp.ggblueshark.com/MajorLogin"
OAUTH_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"
FREEFIRE_VERSION = "OB51"

KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

BIO_HEADERS = {
    "Expect": "100-continue",
    "X-Unity-Version": "2018.4.11f1",
    "X-GA": "v1 1",
    "ReleaseVersion": FREEFIRE_VERSION,
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
}

LOGIN_HEADERS = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/octet-stream",
    "Expect": "100-continue",
    "X-Unity-Version": "2018.4.11f1",
    "X-GA": "v1 1",
    "ReleaseVersion": FREEFIRE_VERSION
}

_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\ndata.proto\"\xbb\x01\n\x04\x44\x61ta\x12\x0f\n\x07\x66ield_2\x18\x02 \x01(\x05\x12\x1e\n\x07\x66ield_5\x18\x05 \x01(\x0b\x32\r.EmptyMessage\x12\x1e\n\x07\x66ield_6\x18\x06 \x01(\x0b\x32\r.EmptyMessage\x12\x0f\n\x07\x66ield_8\x18\x08 \x01(\t\x12\x0f\n\x07\x66ield_9\x18\t \x01(\x05\x12\x1f\n\x08\x66ield_11\x18\x0b \x01(\x0b\x32\r.EmptyMessage\x12\x1f\n\x08\x66ield_12\x18\x0c \x01(\x0b\x32\r.EmptyMessage\"\x0e\n\x0c\x45mptyMessageb\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'data1_pb2', _globals)
BioData = _sym_db.GetSymbol('Data')
EmptyMessage = _sym_db.GetSymbol('EmptyMessage')

def encrypt_data(data_bytes):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    padded = pad(data_bytes, AES.block_size)
    return cipher.encrypt(padded)
    
def get_garena_data(eat_token):
    try:
        callback_url = f"https://api-otrss.garena.com/support/callback/?access_token={eat_token}"
        response = requests.get(callback_url, allow_redirects=False, timeout=10)

        if 300 <= response.status_code < 400 and "Location" in response.headers:
            redirect_url = response.headers["Location"]
            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)

            token_value = query_params.get("access_token", [None])[0]
            account_id = query_params.get("account_id", [None])[0]
            account_nickname = query_params.get("nickname", [None])[0]
            region = query_params.get("region", [None])[0]

            if token_value:
                return token_value
        else:
            return {"error": "Invalid access token or session expired"}
    except Exception as e:
        return f"Error occurred: {e}"

def get_name_region_from_reward(access_token):
    try:
        uid_url = "https://prod-api.reward.ff.garena.com/redemption/api/auth/inspect_token/"
        uid_headers ={
            "authority": "prod-api.reward.ff.garena.com",
            "method": "GET",
            "path": "/redemption/api/auth/inspect_token/",
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "access-token": access_token,
            "cookie": "_gid=GA1.2.444482899.1724033242; _ga_XB5PSHEQB4=GS1.1.1724040177.1.1.1724040732.0.0.0; token_session=cb73a97aaef2f1c7fd138757dc28a08f92904b1062e66c; _ga_KE3SY7MRSD=GS1.1.1724041788.0.0.1724041788.0; _ga_RF9R6YT614=GS1.1.1724041788.0.0.1724041788.0; _ga=GA1.1.1843180339.1724033241; apple_state_key=817771465df611ef8ab00ac8aa985783; _ga_G8QGMJPWWV=GS1.1.1724049483.1.1.1724049880.0.0; datadome=HBTqAUPVsbBJaOLirZCUkN3rXjf4gRnrZcNlw2WXTg7bn083SPey8X~ffVwr7qhtg8154634Ee9qq4bCkizBuiMZ3Qtqyf3Isxmsz6GTH_b6LMCKWF4Uea_HSPk;",
            "origin": "https://reward.ff.garena.com",
            "referer": "https://reward.ff.garena.com/",
            "sec-ch-ua": '"Not.A/Brand";v="99", "Chromium";v="124"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        uid_res = requests.get(uid_url, headers=uid_headers, verify=False)
        uid_data = uid_res.json()
        
        return uid_data.get("uid"), uid_data.get("name"), uid_data.get("region")
    except Exception as e:
        return f"Error occurred: {e}"
        


def get_openid_from_shop2game(uid):
    if not uid: return None
    try:
        openid_url = "https://shop2game.com/api/auth/player_id_login"
        openid_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ar-MA,ar;q=0.9,en-US;q=0.8,en;q=0.7,ar-AE;q=0.6,fr-FR;q=0.5,fr;q=0.4",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Cookie": "source=mb; region=MA; mspid2=ca21e6ccc341648eea845c7f94b92a3c; language=ar; _ga=GA1.1.1955196983.1741710601; datadome=WY~zod4Q8I3~v~GnMd68u1t1ralV5xERfftUC78yUftDKZ3jIcyy1dtl6kdWx9QvK9PpeM~A_qxq3LV3zzKNs64F_TgsB5s7CgWuJ98sjdoCqAxZRPWpa8dkyfO~YBgr; session_key=v0tmwcmf1xqkp7697hhsno0di1smy3dm; _ga_0NY2JETSPJ=GS1.1.1741710601.1.1.1741710899.0.0.0",
            "Origin": "https://shop2game.com",
            "Referer": "https://shop2game.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"'
        }
        payload = {"app_id": 100067, "login_id": str(uid)}
        res = requests.post(openid_url, headers=openid_headers, json=payload, verify=False)
        data = res.json()
        return data.get("open_id")
    except Exception as e:
        return None

def decode_jwt_info(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        name = decoded.get("nickname")
        region = decoded.get("lock_region") 
        uid = decoded.get("account_id")
        return str(uid), name, region
    except:
        return None, None, None

def perform_major_login(access_token, open_id):
    platforms = [8, 3, 4, 6]
    for platform_type in platforms:
        try:
            game_data = my_pb2.GameData()
            game_data.timestamp = "2024-12-05 18:15:32"
            game_data.game_name = "free fire"
            game_data.game_version = 1
            game_data.version_code = "1.108.3"
            game_data.os_info = "Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)"
            game_data.device_type = "Handheld"
            game_data.network_provider = "Verizon Wireless"
            game_data.connection_type = "WIFI"
            game_data.screen_width = 1280
            game_data.screen_height = 960
            game_data.dpi = "240"
            game_data.cpu_info = "ARMv7 VFPv3 NEON VMH | 2400 | 4"
            game_data.total_ram = 5951
            game_data.gpu_name = "Adreno (TM) 640"
            game_data.gpu_version = "OpenGL ES 3.0"
            game_data.user_id = "Google|74b585a9-0268-4ad3-8f36-ef41d2e53610"
            game_data.ip_address = "172.190.111.97"
            game_data.language = "en"
            game_data.open_id = open_id
            game_data.access_token = access_token
            game_data.platform_type = platform_type
            game_data.field_99 = str(platform_type)
            game_data.field_100 = str(platform_type)

            serialized_data = game_data.SerializeToString()
            encrypted = encrypt_data(serialized_data)
            hex_encrypted = binascii.hexlify(encrypted).decode('utf-8')
            
            edata = bytes.fromhex(hex_encrypted)
            response = requests.post(MAJOR_LOGIN_URL, data=edata, headers=LOGIN_HEADERS, verify=False, timeout=10)

            if response.status_code == 200:
                data_dict = None
                try:
                    example_msg = output_pb2.Garena_420()
                    example_msg.ParseFromString(response.content)
                    data_dict = {field.name: getattr(example_msg, field.name) 
                                 for field in example_msg.DESCRIPTOR.fields 
                                 if field.name == "token"}
                except Exception:
                    pass
                if data_dict and "token" in data_dict:
                    return data_dict["token"]
        except Exception:
            continue
    return None
    
def get_token_inspect_data(access_token):
    """Inspect access token to get open_id and platform info"""
    try:
        url = f"https://100067.connect.garena.com/oauth/token/inspect?token={access_token}"
        headers = {
            "User-Agent": "GarenaMSDK/4.0.19P4 (Vivo Y15c; Android 12; en;IN;)",
            "Connection": "close"
        }
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'open_id' in data and 'platform' in data and 'uid' in data:
                return data
    except Exception as e:
        print(Fore.RED + f"Error inspecting token: {e}")
    return None
    
def encrypt_message(key, iv, plaintext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(plaintext, AES.block_size)
    encrypted_message = cipher.encrypt(padded_message)
    return encrypted_message
    
def process_access_token(access_token, uid=None, platform_type=4):
    """Process JWT generation using existing access token"""
    # Inspect the access token first
    token_data = get_token_inspect_data(access_token)
    if not token_data:
        return {"error": "INVALID_TOKEN", "message": "AccessToken invalid."}

    open_id = token_data["open_id"]
    platform_type = token_data.get("platform", platform_type)
    uid = uid or str(token_data["uid"])

    # إنشاء GameData Protobuf مع access token المقدم
    game_data = my_pb2.GameData()
    game_data.timestamp = "2025-05-29 13:11:47"
    game_data.game_name = "free fire"
    game_data.game_version = 1
    game_data.version_code = "1.118.1"
    game_data.os_info = "Android OS 11 / API-30 (RKQ1.201112.002/eng.realme.20221110.193122)"
    game_data.device_type = "Handheld"
    game_data.network_provider = "JIO"
    game_data.connection_type = "MOBILE"
    game_data.screen_width = 720
    game_data.screen_height = 1600
    game_data.dpi = "280"
    game_data.cpu_info = "ARM Cortex-A73 | 2200 | 4"
    game_data.total_ram = 4096
    game_data.gpu_name = "Adreno (TM) 610"
    game_data.gpu_version = "OpenGL ES 3.2"
    game_data.user_id = uid
    game_data.ip_address = "182.75.115.22"
    game_data.language = "en"
    game_data.open_id = open_id
    game_data.access_token = access_token
    game_data.platform_type = platform_type
    game_data.device_form_factor = "Handheld"
    game_data.device_model = "realme RMX1825"
    game_data.field_60 = 30000
    game_data.field_61 = 27500
    game_data.field_62 = 1940
    game_data.field_63 = 720
    game_data.field_64 = 28000
    game_data.field_65 = 30000
    game_data.field_66 = 28000
    game_data.field_67 = 30000
    game_data.field_70 = 4
    game_data.field_73 = 2
    game_data.library_path = "/data/app/com.dts.freefireth-XaT5M7jRwEL-nPaKOQvqdg==/lib/arm"
    game_data.field_76 = 1
    game_data.apk_info = "2f4a7f349f3a3ea581fc4d803bc5a977|/data/app/com.dts.freefireth-XaT5M7jRwEL-nPaKOQvqdg==/base.apk"
    game_data.field_78 = 6
    game_data.field_79 = 1
    game_data.os_architecture = "64"
    game_data.build_number = "2022041388"
    game_data.field_85 = 1
    game_data.graphics_backend = "OpenGLES3"
    game_data.max_texture_units = 16383
    game_data.rendering_api = 4
    game_data.encoded_field_89 = "\x10U\x15\x03\x02\t\rPYN\tEX\x03AZO9X\x07\rU\niZPVj\x05\rm\t\x04c"
    game_data.field_92 = 8999
    game_data.marketplace = "3rd_party"
    game_data.encryption_key = "Jp2DT7F3Is55K/92LSJ4PWkJxZnMzSNn+HEBK2AFBDBdrLpWTA3bZjtbU3JbXigkIFFJ5ZJKi0fpnlJCPDD2A7h2aPQ="
    game_data.total_storage = 64000
    game_data.field_97 = 1
    game_data.field_98 = 1
    game_data.field_99 = str(platform_type)
    game_data.field_100 = str(platform_type).encode()

    # تسلسل البيانات
    serialized_data = game_data.SerializeToString()

    # تشفير البيانات
    encrypted_data = encrypt_message(AES_KEY, AES_IV, serialized_data)
    hex_encrypted_data = binascii.hexlify(encrypted_data).decode('utf-8')

    # إرسال البيانات المشفرة إلى الخادم
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/octet-stream",
        'Expect': "100-continue",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB51"
    }
    edata = bytes.fromhex(hex_encrypted_data)

    try:
        response = requests.post(url, data=edata, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            # محاولة فك تشفير الـ Protobuf
            example_msg = output_pb3.Lokesh()
            try:
                example_msg.ParseFromString(response.content)
                response_dict = parse_response(str(example_msg))
                tooooken = response_dict.get("token", "N/A")
                
                return tooooken
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to deserialize the response: {e}"
                }
        else:
            error_text = response.text.strip()
            if error_text == "BR_PLATFORM_INVALID_PLATFORM":
                return {"success": False, "error": "INVALID_PLATFORM", "message": "this account is registered on another platform"}
            elif error_text == "BR_GOP_TOKEN_AUTH_FAILED":
                return {"success": False, "error": "INVALID_TOKEN", "message": "AccessToken invalid."}
            elif error_text == "BR_PLATFORM_INVALID_OPENID":
                return {"success": False, "error": "INVALID_OPENID", "message": "OpenID invalid."}
            else:
                return {
                    "success": False,
                    "error": f"Failed to get response: HTTP {response.status_code}, {response.reason}"
                }
    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"An error occurred while making the request: {e}"
        }
        
def parse_response(response_content):
    # تحليل الـ response لاستخراج الحقول المهمة
    response_dict = {}
    lines = response_content.split("\n")
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            response_dict[key.strip()] = value.strip().strip('"')
    return response_dict

def perform_guest_login(uid, password):
    payload = {
        'uid': uid,
        'password': password,
        'response_type': "token",
        'client_type': "2",
        'client_secret': "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        'client_id': "100067"
    }
    headers = {
        'User-Agent': "GarenaMSDK/4.0.19P9(SM-M526B ;Android 13;pt;BR;)",
        'Connection': "Keep-Alive"
    }
    try:
        resp = requests.post(OAUTH_URL, data=payload, headers=headers, timeout=10, verify=False)
        data = resp.json()
        if 'access_token' in data:
            return data['access_token'], data.get('open_id')
    except Exception as e:
        pass
    return None, None

def upload_bio_request(jwt_token, bio_text):
    try:
        data = BioData()
        data.field_2 = 17
        data.field_5.CopyFrom(EmptyMessage())
        data.field_6.CopyFrom(EmptyMessage())
        data.field_8 = bio_text
        data.field_9 = 1
        data.field_11.CopyFrom(EmptyMessage())
        data.field_12.CopyFrom(EmptyMessage())

        data_bytes = data.SerializeToString()
        encrypted = encrypt_data(data_bytes)

        headers = BIO_HEADERS.copy()
        headers["Authorization"] = f"Bearer {jwt_token}"

        resp = requests.post(FREEFIRE_UPDATE_URL, headers=headers, data=encrypted, timeout=20, verify=False)

        status_text = "Unknown"
        if resp.status_code == 200: status_text = "✅ Success"
        elif resp.status_code == 401: status_text = "❌ Unauthorized (Token Error/Expired)"
        else: status_text = f"⚠️ Status {resp.status_code}"

        raw_hex = binascii.hexlify(resp.content).decode('utf-8')

        return {
            "status": status_text,
            "code": resp.status_code,
            "bio": bio_text,
            "server_response": raw_hex
        }
    except Exception as e:
        return {"status": f"Error: {str(e)}", "code": 500, "bio": bio_text, "server_response": "N/A"}

@app.route("/bio", methods=["GET", "POST"])
def combined_bio_upload():
    bio = request.args.get("bio") or request.form.get("bio")
    eat = request.args.get("eat") or request.form.get("eat")
    jwt_token = request.args.get("jwt") or request.form.get("jwt")
    uid = request.args.get("uid") or request.form.get("uid")
    password = request.args.get("pass") or request.form.get("pass")
    access_token = request.args.get("access") or request.form.get("access") or request.args.get("access_token")

    if not bio:
        return jsonify({"status": "❌ Error", "code": 400, "error": "Missing 'bio' parameter"}), 400

    final_jwt = None
    login_method = "Direct JWT"
    
    final_open_id = None
    final_access_token = None
    final_uid = None
    final_name = None
    final_region = None

    if jwt_token:
        final_jwt = jwt_token
        j_uid, j_name, j_region = decode_jwt_info(jwt_token)
        final_uid = j_uid
        final_name = j_name
        final_region = j_region
        
    elif uid and password:
        login_method = "UID/Pass Login"
        
        acc_token, login_openid = perform_guest_login(uid, password)
        
        if acc_token and login_openid:
            final_access_token = acc_token
            final_open_id = login_openid
            
            final_jwt = perform_major_login(final_access_token, final_open_id)
            
            if final_jwt:
                 j_uid, j_name, j_region = decode_jwt_info(final_jwt)
                 final_uid = j_uid
                 final_name = j_name
                 final_region = j_region
            else:
                 return jsonify({"status": "❌ JWT Generation Failed", "code": 500}), 500

        else:
            return jsonify({"status": "❌ Guest Login Failed (Check UID/Pass)", "code": 401}), 401

    elif access_token:
        login_method = "Access Token Login"
        final_access_token = access_token
        
        f_uid, f_name, f_region = get_name_region_from_reward(access_token)
        final_uid = f_uid
        final_name = f_name
        final_region = f_region
        final_jwt = process_access_token(access_token)

    elif eat:
        login_method = "Eat Token Login"
        final_access_token = get_garena_data(eat)
        f_uid, f_name, f_region = get_name_region_from_reward(final_access_token)
        final_uid = f_uid
        final_name = f_name
        final_region = f_region
        final_jwt = process_access_token(final_access_token)
    else:
        return jsonify({"status": "❌ Error", "code": 400, "error": "Provide JWT, or UID/Pass, or Eat Token, or Access Token"}), 400

    if not final_jwt:
        return jsonify({"status": "❌ JWT Generation Failed", "code": 500}), 500

    result = upload_bio_request(final_jwt, bio)
    
    response_data = {
        "Credit": "Nivashini",
        "Insta": "ft_rosie._",
        "status": result["status"],
        "login method": login_method,
        "status code": result["code"],
        "bio": result["bio"],
        "uid": str(final_uid) if final_uid else None,
        "name": final_name,
        "region": final_region,
        "access_token": final_access_token,
        "generated_jwt": final_jwt
    }

    response = make_response(jsonify(response_data))
    response.headers["Content-Type"] = "application/json"
    return response
    
@app.route("/", methods=["GET"])
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Nivashini’s Bio</title>

<style>
:root {
    --bg-main: #fffafc;
    --accent: #f6c1d1;
    --border-soft: #f1d5df;
    --text-main: #5b5561;
}

html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
}

body {
    font-family: "Segoe UI", system-ui, sans-serif;
    background: var(--bg-main);
    color: var(--text-main);
    font-size: 17px;
}

/* ===== LAYOUT ===== */
.main-wrapper {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.content {
    flex: 1;
    padding: 24px 16px 160px; /* space for sticky bar */
}

/* ===== TITLE ===== */
h1 {
    text-align: center;
    font-size: 26px;
    color: #8b5d6e;
    margin: 10px 0 24px;
}

/* ===== FORM ===== */
form {
    max-width: 520px;
    margin: 0 auto;
}

label {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 18px 0 6px;
    font-weight: 600;
    color: #7a6b73;
}

input, textarea, select {
    width: 100%;
    padding: 16px;
    border-radius: 16px;
    border: 1px solid var(--border-soft);
    background: #fff;
    font-size: 16px;
}

textarea {
    min-height: 120px;
}

.login-section {
    margin-top: 10px;
    display: none;
}

/* ===== BUTTON ===== */
button {
    width: 100%;
    padding: 18px;
    margin-top: 26px;
    border-radius: 999px;
    border: none;
    background: var(--accent);
    color: #6a2c42;
    font-weight: 700;
    font-size: 17px;
    opacity: 0.6;
}

button:enabled {
    opacity: 1;
}

/* ===== TOAST ===== */
.toast {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    padding: 16px 26px;
    border-radius: 999px;
    font-weight: 600;
    display: none;
    z-index: 9999;
    text-align: center;
}

.info { background: #e0f2fe; color: #0369a1; }
.success { background: #dcfce7; color: #166534; }
.warning { background: #fff1f2; color: #9f1239; }

/* ===== FOOTER (FULL WIDTH) ===== */
.site-footer {
    width: 100%;
    background: #fff0f5;
    text-align: center;
    padding: 18px 12px;
    margin-bottom: 90px; /* lifted above Instagram bar */
}

.site-footer a {
    text-decoration: none;
    color: #a78b9a;
    font-size: 14px;
}

.site-footer span {
    font-weight: 700;
    color: #f2a9c3;
}

/* ===== STICKY INSTAGRAM ===== */
.sticky-insta {
    position: fixed;
    bottom: 12px;
    left: 12px;
    right: 12px;
    border-radius: 999px;
    background: linear-gradient(135deg, #f6c1d1, #fbcfe8);
    padding: 14px;
    text-align: center;
    box-shadow: 0 12px 30px rgba(246,193,209,0.45);
}

.sticky-insta a {
    color: #831843;
    font-weight: 700;
    text-decoration: none;
}
</style>

<script>
function selectLoginMethod() {
    const method = document.getElementById("login_method").value;
    document.querySelectorAll(".login-section").forEach(d => d.style.display = "none");
    submitBtn.disabled = true;
    if (method) {
        document.getElementById(method).style.display = "block";
        submitBtn.disabled = false;
    }
}

function showToast(msg, type) {
    const t = document.getElementById("toast");
    t.textContent = msg;
    t.className = "toast " + type;
    t.style.display = "block";
    setTimeout(() => t.style.display = "none", 3000);
}

async function submitForm(e){
    e.preventDefault();
    showToast("🫧 Processing… please wait 🤍","info");

    try{
        const res=await fetch("/bio",{method:"POST",body:new FormData(bioForm)});
        const data=await res.json();
        const ok=(data.status||"").includes("Success");
        showToast(ok ? "🌸 Bio updated successfully!" : data.status, ok ? "success" : "warning");
    }catch{
        showToast("🍑 Something went wrong","warning");
    }
}
</script>
</head>

<body>

<div id="toast" class="toast"></div>

<div class="main-wrapper">

<div class="content">
<h1>🌸 Nivashini’s Bio</h1>

<form id="bioForm" onsubmit="submitForm(event)">

<label>📝 Bio Text</label>
<textarea name="bio" required></textarea>

<label>🔐 Login Method</label>
<select id="login_method" onchange="selectLoginMethod()" required>
<option value="">🌷 Choose login method</option>
<option value="jwt">🧸 JWT Token</option>
<option value="uidpass">🎀 UID & Password</option>
<option value="access">🫧 Access Token</option>
<option value="eat">🍓 EAT Token</option>
</select>

<div id="jwt" class="login-section"><input name="jwt"></div>
<div id="uidpass" class="login-section"><input name="uid"><input type="password" name="pass"></div>
<div id="access" class="login-section"><input name="access"></div>
<div id="eat" class="login-section"><input name="eat"></div>

<button id="submitBtn" disabled>🌸 Save My Bio</button>

</form>
</div>

<footer class="site-footer">
<a href="https://instagram.com/ft_rosie._" target="_blank">
Made with 🤍 by <span>Nivashini</span>
</a>
</footer>

</div>

<div class="sticky-insta">
<a href="https://instagram.com/ft_rosie._" target="_blank">
🫶 Let’s be friends on Instagram<br>@ft_rosie._
</a>
</div>

</body>
</html>
"""
