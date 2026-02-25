{
    'name':'Claw Chat',
    'version':'1.0',
    'author':'Leo Jeong',
    'summary':'Openclaw Automation Module',
    'category':'tools',
    'depends':['base', 'web'],
    'data':[
        'security/ir.model.access.csv',
        'views/chat_view.xml',
        'views/chat_menu.xml',
    ],
    'assets':{
        "web.assets_backend": [
            "openclaw_chat/static/src/js/chat_systray.js",
            "openclaw_chat/static/src/js/chat_panel.js",
            "openclaw_chat/static/src/xml/chat_systray.xml",
            "openclaw_chat/static/src/xml/chat_panel.xml",
            "openclaw_chat/static/src/css/chat_panel.css",
        ],
    },
    'application':True
}