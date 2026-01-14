from odoo import models, fields, api,_
import requests

import os
import base64

import pytz
import subprocess
import sys
from odoo import models,fields,api,_

# # Specify the package name and version you want to install
# try:
#     import filetype
# except:    
package_name = "filetype"
package_version = ""  # You can specify a specific version here if needed
#subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

import filetype

from werkzeug.datastructures import FileStorage


class SaleAssortmentLine(models.TransientModel):
    _name = "student.whatsapp.massage"

    payload = fields.Char(string='Message')
    img = fields.Binary(string='Attachment')

    def action_share(self):
        active_ids = self.env["op.student"].browse(self._context.get("active_ids"))
        print('-----------------',active_ids)
        for rec in active_ids:
            # print(self.img) 

            # WhatsApp API URL
            url = "https://7700.media.greenapi.com/waInstance7700158158/sendFileByUpload/baed87786a5747bc8a6b9a4f4c4b37ed2b4433a370e645829f"
            
            if rec.company_id.id in [6,7,8]:
                url = "https://7700.media.greenapi.com/waInstance7700183902/sendFileByUpload/d9fadc38435d4538bbc71008bf8760c5c9875203af21407797"

            # Clean and format the recipient's number
            number_n = rec.mobile.replace("+", "").replace(" ", "")
            if number_n:
                if number_n[0] == '0':
                    number_n = '92' + number_n[1:]

            # Payload for the WhatsApp message
            payload = {
                "chatId": f'{number_n}@c.us',
                # "message": f"{self.payload}"
            }

            # Decode the image from base64
            # image_decoded = base64.b64decode(self.img)
            #
            # # Create a BytesIO stream for the decoded image
            # image_stream = io.BytesIO(image_decoded)

            if self.img:
                print(type(self.img))  # Confirm the type is bytes
                upload_dir = '/tmp'
                file_content = base64.b64decode(self.img)
                kind = filetype.guess(file_content)
                file_extension = f".{kind.extension}"
                print(kind.mime)

                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                # Decode the binary content
                if self.img:
                    file_path = os.path.join(upload_dir, f'CitySchool{file_extension}')

                    # Write the file to the filesystem
                    with open(file_path, 'wb') as f:
                        f.write(file_content)

                print("File saved successfully. Check its content and format.")
                files = [
                    ('file', (f'CitySchool{file_extension}', open(f'/tmp/CitySchool{file_extension}', 'rb'), f"{kind.mime}"))
                ]

                response = requests.post(url, data=payload, files=files)
                os.remove(f'/tmp/CitySchool{file_extension}')
                #
                print(response.text.encode('utf8'),number_n)

            if self.payload:
                url = "https://7700.api.greenapi.com/waInstance7700158158/sendMessage/baed87786a5747bc8a6b9a4f4c4b37ed2b4433a370e645829f"

                payload = {
                    "chatId": f'{number_n}@c.us',
                    "message": f"{self.payload}"
                }
                headers = {
                    'Content-Type': 'application/json'
                }

                response = requests.post(url, json=payload, headers=headers)

                print(response.text.encode('utf8'))
