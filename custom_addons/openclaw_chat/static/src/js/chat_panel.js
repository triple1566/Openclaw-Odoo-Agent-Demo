import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
//import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc"

export class ChatPanel extends Component {
    //initial construction
    setup() {
        //define the state
        //NOTE: state changes trigger a re-render of the component
        this.state = useState(
            {
                //messages will store chat history in the form of list-of-dicts
                messages: [],
                input: "",
                nextId: 1,
            }
        );
    }

    async send() {
        //if the message is empty or just whitespaces, we ignore
        if (!this.state.input.trim()) return;
        
        //this.orm.call returns a promise
        const reply = await rpc(
            "/openclaw/chat",
            {
                message: this.state.input,
            }
        );

        //stores the message history (both request and reply) in the messages list under state
        this.state.messages.push(
            { id: this.state.nextId++, role: "user", text: this.state.input },
            { id: this.state.nextId++, role: "bot", text: reply.reply }
        );

        this.state.input = "";
    }

    //triggers the logic on any keydown event
    onKeydown(ev) {
        //On keydown event, see if the pressed key is the "Enter" key
        if (ev.key === "Enter") {
            //This is a saftey check to disable default browser behaviour we don't want
            //Without this, we may encounter erratic edge cases
            ev.preventDefault();
            //calls the async send function we defined above
            this.send();
        }
    }
}

ChatPanel.template = "openclaw_chat.ChatPanel"
ChatPanel.components = { Dialog };