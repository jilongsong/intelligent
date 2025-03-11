"""
测试服务器，用于验证API响应
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests
from urllib.parse import urlparse, parse_qs

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # 显示测试页面
        html = """
        <html>
        <head>
            <title>DSL API 测试</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                pre { background: #f5f5f5; padding: 10px; }
                .response { margin-top: 20px; }
            </style>
        </head>
        <body>
            <h1>DSL API 测试</h1>
            
            <h2>1. 测试聊天接口</h2>
            <button onclick="testChat()">运行测试</button>
            <div id="chatResponse" class="response"></div>
            
            <h2>2. 测试加载DSL</h2>
            <button onclick="testLoadDsl()">运行测试</button>
            <div id="dslResponse" class="response"></div>
            
            <script>
                async function testChat() {
                    const response = document.getElementById('chatResponse');
                    response.innerHTML = '正在测试...';
                    
                    try {
                        const result = await fetch('http://localhost:8000/api/v1/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                message: '你好，请介绍一下你自己',
                                version: 'api'
                            })
                        });
                        
                        const data = await result.json();
                        response.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    } catch (error) {
                        response.innerHTML = '<pre>错误: ' + error.message + '</pre>';
                    }
                }
                
                async function testLoadDsl() {
                    const response = document.getElementById('dslResponse');
                    response.innerHTML = '正在测试...';
                    
                    const complexDsl = {
                        type: 'container',
                        children: [
                            {
                                type: 'list',
                                items: [
                                    {type: 'text', content: 'Item 1'},
                                    {type: 'text', content: 'Item 2'},
                                    {type: 'text', content: 'Item 3'}
                                ]
                            },
                            {
                                type: 'tabs',
                                children: [
                                    {
                                        type: 'tab',
                                        items: [
                                            {type: 'button', label: 'Button 1'},
                                            {type: 'button', label: 'Button 2'}
                                        ]
                                    }
                                ]
                            }
                        ]
                    };
                    
                    try {
                        // 加载DSL
                        let result = await fetch('http://localhost:8000/api/v1/load_dsl', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                dsl_content: JSON.stringify(complexDsl),
                                version: 'api'
                            })
                        });
                        
                        let data = await result.json();
                        response.innerHTML = '<h3>加载DSL响应:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                        
                        // 分析DSL
                        result = await fetch('http://localhost:8000/api/v1/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                message: '请分析当前DSL的结构',
                                version: 'api'
                            })
                        });
                        
                        data = await result.json();
                        response.innerHTML += '<h3>分析DSL响应:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    } catch (error) {
                        response.innerHTML = '<pre>错误: ' + error.message + '</pre>';
                    }
                }
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

def run(port=8001):
    """启动测试服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, TestHandler)
    print(f'启动测试服务器在端口 {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
