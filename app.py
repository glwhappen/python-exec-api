from flask import Flask, request, jsonify
import traceback
import io
import threading
import time
import builtins
import resource
import sys
# import numpy

app = Flask(__name__)

# 创建安全的执行环境，排除特定模块
# def create_safe_globals():
#     # 复制内置函数和变量，但排除不安全的模块
#     safe_builtins = dict(builtins.__dict__)
    
#     # 删除不安全的模块
#     unsafe_modules = ['os', 'sys', 'subprocess', 'shutil', 'resource']
#     for mod in unsafe_modules:
#         if mod in safe_builtins:
#             del safe_builtins[mod]
    
#     safe_globals = {
#         "__builtins__": safe_builtins
#     }
    
#     return safe_globals

def create_safe_globals(additional_globals=None):
    safe_builtins = dict(builtins.__dict__)

    # 定义黑名单模块，主要是直接操作系统相关的
    blacklisted_modules = ['os', 'sys', 'subprocess', 'shutil', 'socket', 'fcntl']

    # 修改 __import__ 函数以实现黑名单功能
    original_import = builtins.__import__
    def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in blacklisted_modules:
            raise ImportError(f"禁止导入{name}模块")
        return original_import(name, globals, locals, fromlist, level)

    safe_builtins['__import__'] = safe_import

    safe_globals = {
        "__builtins__": safe_builtins
    }
    if additional_globals:
        safe_globals.update(additional_globals)  # 将额外的全局变量添加到环境中

    return safe_globals

# 执行代码的线程函数
def execute_code(code, output, safe_globals):
    sys_stdout_backup = sys.stdout
    sys.stdout = output
    try:
        exec(code, safe_globals)
    except Exception as e:
        output.write(f"Error: {str(e)}") # \n{traceback.format_exc()}
    finally:
        sys.stdout = sys_stdout_backup

# 清理输入代码，移除不可打印字符，并确保每条语句独立存在
def clean_code(code):
    # 替换所有非断开空格 (U+00A0) 为标准空格 (U+0020)
    cleaned_code = code.replace('\u00A0', ' ')
    
    # 保留正常的换行符和缩进空格
    return ''.join(c if c.isprintable() or c in ('\n', '\t', ' ') else ' ' for c in cleaned_code)


@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code', '')
    params = data.get('params', {})  # 假设从 JSON 数据中获取参数

    print(code)
    # 捕获 print 输出
    output = io.StringIO()

    # 清理代码
    code = clean_code(code)

    # 设置内存限制为 200MB
    resource.setrlimit(resource.RLIMIT_AS, (10 * 1024 * 1024 * 1024, 20 * 1024 * 1024 * 1024))

    # 创建安全的执行环境
    safe_globals = create_safe_globals(additional_globals=params)
    
    # 构造一个字符串，用于定义代码中的参数
    params_code = '\n'.join(f"{key} = {repr(value)}" for key, value in params.items())
    full_code = f"{params_code}\n{code}"  # 将参数定义添加到代码的开头


    # 创建并启动线程执行代码
    exec_thread = threading.Thread(target=execute_code, args=(full_code, output, safe_globals))
    exec_thread.start()
    
    # 等待线程完成或超时
    exec_thread.join(timeout=60)  # 设置 1 分钟的超时时间
    
    if exec_thread.is_alive():
        return jsonify({'status': 'error', 'error': 'Execution timed out', 'code': code, 'full_code': full_code}), 200

    # 获取 print 的输出内容
    result = output.getvalue()

    if result.startswith('Error: '):
        return jsonify({'status': 'error', 'result': result, 'code': code, 'full_code': full_code}), 200
    else:

        return jsonify({'status': 'success', 'result': result, 'code': code, 'full_code': full_code}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
