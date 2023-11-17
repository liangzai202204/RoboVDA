HTML="""
<!DOCTYPE html>
<html>
<head>
    <title>RoboVda数据展示</title>
    <meta charset="utf-8">
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
            background-color: #f7f7f7;
        }

        .header {
            text-align: center;
            padding: 20px;
            background-color: #008cdd;
            box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
            color: white;
        }

        .header h1 {
            font-size: 32px;
            margin-top: 0;
        }

        .container {
            max-width: 960px;
            margin: 0 auto;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
        }

        .button-container {
            float: left;
            width: 30%;
        }

        .button-container h2 {
            color: #008cdd;
        }

        .button-container ul {
            list-style: none;
            margin: 0;
            padding: 0;
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-start;
        }

        .button-container li {
            margin: 10px;
        }

        .button-container button {
            padding: 10px 16px;
            background-color: #008cdd;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s ease-in-out;
            display: block;
            margin-bottom: 10px;
        }

        .button-container button:hover {
            background-color: #006fad;

        }
        .button-container ul {
            list-style: none;
            margin: 0;
            padding: 0;
            display: flex;
        }

        .data-display {
            float: right;
            width: 65%;
            margin-top: 20px;
            padding: 20px;
            background-color: #88D0E454;
            box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
        }

        .data-display h2 {
            color: #008cdd;
        }

        pre {
            margin: 0;
            padding: 0;
            font-size: 15px;
            line-height: 1.5;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            background-color: #f7f7ff;
            border-radius: 4px;
            max-height: 500px;
            font-weight: bold;
            border: 2px solid blue;

        }

        #data-container {
            width: auto;
            height: auto;
        }
        .button-container button.active {
            background-color: #006fad;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>RoboVda数据展示</h1>
    </div>

    <div class="container">
        <div class="button-container">
            <h2>选择数据内容:</h2>
            <ul>
                <li>
                    <button onclick="postData('/cancelOrder')" id="cancelOrderBtn">取消訂單</button>
                    <button onclick="postData('/postEndpoint2')" id="postEndpoint2Btn">发送POST请求2</button>
                    <button onclick="getData('/get_data')" id="getDataBtn">order/state</button>
                    <button onclick="refreshData('/getOrderStatus')" id="refreshOrderBtn">订单状态</button>
                    <button onclick="refreshData('/getState')" id="refreshStateBtn">topic State</button>
                    <button onclick="refreshData('/getPackTask')" id="refreshPackBtn">打包结果</button>
                    <button onclick="refreshData('/getPushData')" id="refreshPushBtn">机器人推送数据</button>
                </li>
            </ul>
        </div>

        <div class="data-display">
            <h2>数据展示:</h2>
            <pre id="data-container"></pre>
        </div>



    </div>

<script>
        function handleClick(btnId) {
        const btn = document.getElementById(btnId);
        btn.classList.add('active'); // 添加 active 类名
    }

    // 获取按钮元素的数组
    const buttons = document.getElementsByClassName('button-container')[0].getElementsByTagName('button');

    // 为每个按钮添加点击事件处理函数
    Array.from(buttons).forEach(button => {
        button.addEventListener('click', () => {
            Array.from(buttons).forEach(btn => {
                btn.classList.remove('active'); // 移除其他按钮的 active 类名
            });
            handleClick(button.id); // 处理点击的当前按钮
        });
    });
    function getData(url) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const dataContainer = document.getElementById('data-container');
                dataContainer.innerHTML = JSON.stringify(data, null, 2);
            });
    }
    function postData(url) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({}) // 根据需要传递的参数进行修改
    })
    .then(response => response.json())
    .then(data => {
        const dataContainer = document.getElementById('data-container');
        dataContainer.innerHTML = JSON.stringify(data, null, 2);
    });
}


    function refreshData(url) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const dataContainer = document.getElementById('data-container');
                dataContainer.innerHTML = JSON.stringify(data, null, 2);
            });
    }
</script>

</body>
</html>
"""