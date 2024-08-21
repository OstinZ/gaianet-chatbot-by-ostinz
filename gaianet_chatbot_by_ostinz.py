import os
import sys
import asyncio
import requests
import random
import logging
import subprocess
from requests.exceptions import ConnectionError, Timeout, RequestException

# ตั้งค่าระดับการบันทึกเหตุการณ์
logging.basicConfig(level=logging.INFO)

# ตั้งชื่อหน้าต่าง Command Prompt ตามชื่อบอท
os.system("title Gaianet Chatbot by Ostinz")

# ฟังก์ชันแสดงโลโก้
def print_logo():
    logo = r"""
 _____   ___  _____  ___   _   _  _____ _____   _____  _   _   ___ ___________  _____ _____ 
|  __ \ / _ \|_   _|/ _ \ | \ | ||  ___|_   _| /  __ \| | | | / _ \_   _| ___ \|  _  |_   _|
| |  \// /_\ \ | | / /_\ \|  \| || |__   | |   | /  \/| |_| |/ /_\ \| | | |_/ /| | | | | |  
| | __ |  _  | | | |  _  || . ` ||  __|  | |   | |    |  _  ||  _  || | | ___ \| | | | | |  
| |_\ \| | | |_| |_| | | || |\  || |___  | |   | \__/\| | | || | | || | | |_/ /\ \_/ / | |  
 \____/\_| |_/\___/\_| |_/\_| \_/\____/  \_/    \____/\_| |_/\_| |_/\_/ \____/  \___/  \_/  
                 ________   __  _____ _____ _____ _____ _   _  ______                       
                 | ___ \ \ / / |  _  /  ___|_   _|_   _| \ | ||___  /                       
                 | |_/ /\ V /  | | | \ `--.  | |   | | |  \| |   / /                        
                 | ___ \ \ /   | | | |`--. \ | |   | | | . ` |  / /                         
                 | |_/ / | |   \ \_/ /\__/ / | |  _| |_| |\  |./ /___                       
                 \____/  \_/    \___/\____/  \_/  \___/\_| \_/\_____/                       
    """
    print(logo)

# ฟังก์ชันแสดงโลโก้เมื่อเริ่มโปรแกรม
print_logo()

# กำหนดตัวแปรที่จำเป็น
questions = [
    "What is 10 plus 5?", "What is 12 divided by 4?", "What is 7 times 3?"
]

restart_count = 0  # ตัวนับการรีสตาร์ทโปรแกรม
question_count = 0
error_count = 0

def get_api_url(sub_domain):
    example_sub_domain = "0xk8j2k3nd8dljf35gjk7gk5f0e1h2h3jkf8c29"
    
    # ตรวจสอบว่า sub-domain มีรูปแบบที่ถูกต้องหรือไม่ (ตัวอย่างง่ายๆ)
    if not sub_domain.startswith("0x") or len(sub_domain) < 10:
        logging.warning("Invalid sub-domain provided. Using example sub-domain.")
        sub_domain = example_sub_domain
    
    return f"https://{sub_domain}.us.gaianet.network/v1/chat/completions"

async def main():
    sub_domain = input("Please enter your sub-domain: ")
    api_url = get_api_url(sub_domain)
    logging.info(f"API URL set to: {api_url}")
    logging.info("Starting to ask questions...")
    await ask_question(api_url)

async def ask_question(api_url):
    global question_count, restart_count, error_count
    timeout = 60  # ตั้งค่า timeout สำหรับคำขอ

    while True:
        try:
            question = random.choice(questions)
            logging.info(f"Asking: {question}")

            response = await asyncio.to_thread(requests.post,
                api_url,
                headers={
                    'accept': 'application/json',
                    'content-type': 'text/event-stream'
                },
                json={"model": "Qwen2-0.5B-Instruct-Q5_K_M", "messages": [{"role": "user", "content": question}]},
                timeout=timeout
            )

            if not check_response_status(response):
                logging.warning(f"Restart Count: {restart_count}. Restarting program...")
                restart_program()

            question_count += 1
            logging.info(f"Sent {question_count} questions. Status Code: {response.status_code}")
            logging.info(f"Response: {response.json()}")

        except (ConnectionError, Timeout) as e:
            error_count += 1
            logging.error(f"Connection or Timeout error detected: {str(e)}")
            restart_program()
        except RequestException as e:
            error_count += 1
            logging.error(f"Request error detected: {str(e)}")
            await asyncio.sleep(5)  # รอ 5 วินาทีก่อนลองใหม่
        except Exception as e:
            error_count += 1
            logging.error(f"Unknown error detected: {str(e)}")
            restart_program()

def check_response_status(response):
    return response.status_code not in [500, 504]

def restart_program():
    global restart_count
    restart_count += 1
    logging.info(f"Restarting the program... Total restarts: {restart_count}")
    python = sys.executable
    subprocess.Popen([python] + sys.argv)  # ใช้ subprocess เพื่อรีสตาร์ทโปรแกรมใหม่
    sys.exit()  # ออกจากโปรแกรมเดิม

# รันโปรแกรมหลัก
if __name__ == "__main__":
    asyncio.run(main())
