from odoo import http
import requests


class OpenClawController(http.Controller):
    #Adds a route handler function to a specific address
    @http.route(
        "/openclaw/chat",
        type="json",
        methods=["POST"],
        auth="user"
    )
    def openclaw_chat(messages):
        response = requests.post("https://openclaw.tail7c1161.ts.net/hooks/agent", 
                             headers={"Authorization": "Bearer leohooks"},
                             json={
                                "message": "Run this",
                                "name": "Email",
                                "agentId": "hooks",
                                "sessionKey": "hook:email:msg-123",
                                "wakeMode": "now",
                                "deliver": True,
                                "channel": "last",
                                "to": "+15551234567",
                                "model": "openai/gpt-5.2-mini",
                                "thinking": "low",
                                "timeoutSeconds": 120
                            })
        reply = "Done" if response.status_code == 202 else "Null"
        return {"reply": f"{reply}! \n =====> \n status_code: {response.status_code}, header: {response.headers} body: {response.content}"}