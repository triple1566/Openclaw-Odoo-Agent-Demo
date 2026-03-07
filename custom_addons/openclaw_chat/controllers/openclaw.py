from odoo import http
from odoo.http import request
import requests


class OpenClawController(http.Controller):
    #Adds a route handler function to a specific address
    @http.route(
        "/openclaw/chat",
        type="json",
        methods=["POST"],
        auth="user"
    )

    def openclaw_chat(self,message):
        print(message)
        claw_record = request.env['claw.chat'].search([('creator','=','admin')],limit=1)
        #curl addr: - meshed to openclaw server using tailscale
        response = requests.post(f"{claw_record.tailnet_addr}", 
                             headers={"Authorization": f"Bearer {claw_record.hook_token}"},
                             json={
                                "message": f"For this request, use the ODOO tool under your TOOLS.md file, your job is to follow the request exactly once, and once only. DO NOT REPEAT IF IT FAILS. if it fails, report immediately by stating the json data you sent, and the json data returned to you, and the status code. The said request is: {message}",
                                "name": "Odoo",
                                "agentId": "main",
                                "sessionKey": "main",
                                "wakeMode": "now",
                                "deliver": True,
                                "channel": "last",
                                "model": f"{claw_record.llm_model}",
                                "thinking": "low",
                                "timeoutSeconds": 120
                            })
        reply = "Done" if response.status_code == 202 else "Null"
        return {"reply": f"{reply}! \n =====> \n status_code: {response.status_code}, header: {response.headers} body: {response.content}"}

    @http.route(
        "/openclaw/call_receiver",
        type="json",
        methods=["POST"],
        auth="user"
    )
    def openclaw_receiver(self,log):
        claw_receiver = request.env['claw.receiver']

        record = claw_receiver.create({
            "log": log
        })

        return {
            "status":"ok",
            "log": f"log written to {record.id}"
        }