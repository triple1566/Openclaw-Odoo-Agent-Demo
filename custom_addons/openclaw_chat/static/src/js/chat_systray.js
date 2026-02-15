import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { ChatPanel } from "./chat_panel";

export class ChatSystray extends Component{
    setup() {
        this.dialog = useService("dialog");
    }

    openChat() {
        this.dialog.add(ChatPanel, {}, {
            backdrop: false,
            size: "medium",
        });
    }
}

ChatSystray.template = "openclaw_chat.ChatSystray";

registry.category("systray").add(
    "openclaw_chat.systray",
    { Component: ChatSystray }
);
