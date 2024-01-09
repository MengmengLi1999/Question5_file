#!/usr/bin/env python
# coding: utf-8

import datetime
import json
import webbrowser
import time
from flask import Flask, render_template, request
from threading import Thread
from flask_socketio import SocketIO
from flask_cors import CORS


# 创建 Flask 应用
app = Flask(__name__, static_folder='static',template_folder=r'C:\Users\11054\Desktop\hust\templates')
socketio = SocketIO(app)  # 实时通信
CORS(app)  # 允许所有域名跨源访问

# 指定存储数据的文件路径
data_file = 'visitor_data.json'


# 读取数据
def read_data():
    try:
        with open(data_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # 如果文件不存在，返回初始数据
        return {"total_visits": 0, "daily_visits": {}, "last_reset": str(datetime.date.today())}


# 写入更新后数据
def write_data(data):
    with open(data_file, 'w') as file:
        json.dump(data, file)


# 主页的路由处理函数
@app.route('/')
def index():
    data = read_data()
    # 更新总访问量
    data['total_visits'] += 1

    # 更新每日访问量
    today = str(datetime.date.today())
    if today not in data['daily_visits']:
        data['daily_visits'][today] = 0
    data['daily_visits'][today] += 1

    write_data(data)
    return render_template('index.html')


# 重置访问数据
@app.route('/reset')
def reset():
    data = read_data()
    # 重置每日访问量
    data['daily_visits'] = {}
    data['last_reset'] = str(datetime.date.today())
    write_data(data)
    return data


# 提供接口访问当前的访问数据
@app.route('/data')
def data():
    # 提供当前的访问数据
    return read_data()


# 创建字典来存储 IoT 监测点
iot_points = {}

# 创建字典来存储 IoT 监测点的访问次数
iot_visits = {}

@app.route('/iot/<iot_id>', methods=['POST'])
def set_iot(iot_id):
    video_path = request.form.get("video_path")  # 从 POST 请求中获取视频路径
    if video_path:
        iot_points[iot_id] = video_path
        iot_visits[iot_id] = 0  # 记录访问次数，初始值为0
        return f'Created IoT monitoring point {iot_id} with video {video_path}'
    else:
        return "Video path not provided", 400

@app.route('/iot-points')
def get_iot_points():
    return iot_points

@app.route('/visit/<iot_id>', methods=['GET'])
def visit_iot(iot_id):
    if iot_id in iot_visits:
        iot_visits[iot_id] += 1  # 增加访问次数
        return f'IoT monitoring point {iot_id} visited. Total visits: {iot_visits[iot_id]}'
    else:
        return "IoT monitoring point not found", 404


def open_browser():
    # 等待服务器启动
    time.sleep(3)
    webbrowser.open_new('http://127.0.0.1:5000/')


# 在 Flask 应用启动时启动线程
if __name__ == '__main__':
    # 在另一个线程中打开浏览器
    Thread(target=open_browser).start()
    # 启动 Flask 应用
    socketio.run(app, host='127.0.0.1', port=5000, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)

