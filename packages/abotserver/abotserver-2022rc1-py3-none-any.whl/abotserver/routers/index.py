from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
        <head>
            <title>ABOT OpenAPI</title>
            <style type="text/css">
                html,body{font-size: 14px;font-family: "微软雅黑";text-align: center;width: 100%;height: 100%;
                min-height: 100%;border:0;line-height: none;}
                p{border: 0;margin: 0;padding: 0;line-height: none;}
                body{padding:0px; margin:0px ;}
                .container{position:relative;height: auto;min-height: 100%;margin: 0 line-height:18px;}
                .container .header{height: 100px;background: #FFFFFF;}
                .container .push{padding-bottom: 100px;}
                .footer{position:relative;height: 100px;margin-top:-100px;background: #FFFFFF;}
            </style>
        </head>
        <body style="text-align:center;">
            <div class="container">
                <div class="header">
                    <h1>欢迎访问 ABOT</h1>
                </div>
                <div class="content">
                    <strong><h1>Abot是一个智能机器人OpenAPI接口平台！<h1></strong>
                </div>
                <div class="push"></div>
            </div>
                <div class="footer">
                    <a href="http://beian.miit.gov.cn/" target="_blank">粤ICP备20060464号</a>
                </div>
        </body>
    </html>
    """
