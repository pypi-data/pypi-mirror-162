
import os
import argparse
from chariotCore import VERSION
from chariotCore.tasks import *

def cmdline():

    #   创建命令行解析对象
    parser = argparse.ArgumentParser(description=f"千乘系统插件生成器 v{VERSION}")

    #   添加命令
    parser.add_argument("-v", "--version", help="查看版本", action="store_true")
    parser.add_argument("-g", "--generate", help="生成插件，需要yaml文件路径参数，建议每次改动yaml文件时重新生成一次插件。注意，重新生成插件会覆盖不同组件的models.py校验文件。使用示例：chariot-plugin -g .\plugin.spec.yaml", action="append")
    parser.add_argument("-y","--yaml",help="在当前工作目录下生成一个yaml模板文件用于编写插件参数",action="store_true")
    parser.add_argument("-r", "--run", help="运行插件指定功能，需要json格式的数据参数。注意，此命令会尝试运行完成一个功能的完整流程，并且发送真实请求。使用示例：chariot-plugin -r tests\example_action.json", action="append")
    parser.add_argument("-hp", "--http", help="启动api接口，插件以REST服务的形式对外提供服务，用测试接口", action="store_true")
    parser.add_argument("-t", "--test", help="测试插件指定功能的连接器(connection)部分，需要json格式的数据参数。注意，此命令可能会发送真实请求。使用示例：chariot-plugin -t tests\example_action.json", action="append")
    parser.add_argument("-tb", "--tarball", help="插件打包(此命令仅在Linux环境下可用)，生成在线包，用于在线环境的插件安装，打包后的文件较小", action="store_true")
    parser.add_argument("-mki", "--mkimg", help="制作成docker镜像(此命令仅在Linux环境下可用），生成离线包，用于离线环境的插件安装。注意，打包时需要联网，打包后的文件较大", action="store_true")
    parser.add_argument("-ts","--testserver",help="启动API测试服务器，插件将以REST服务的形式对外提供服务，用于测试接口，此功能将在未来某一个版本中完全取代 --http 的功能",action="store_true")

    #   获取add_argument中action的参数
    args = parser.parse_args()

    #   获取版本号
    if args.version:
        print("chariot-plugin: " + VERSION)

    #   生成插件
    elif args.generate:
        #   需要当前工作区的绝对路径和yaml文件的相对路径
        yaml_path = args.generate[0]
        generate(os.getcwd(),yaml_path)

    #   在当前工作目录下生成一个yaml模板文件
    elif args.yaml:
        #   需要当前工作区的绝对路径
        generateYaml(os.getcwd())

    #   根据tests文件下的json文件内填写的参数，以正常流程(包括使用连接器)运行插件内不同的组件
    elif args.run:
        #   需要当前工作区的绝对路径和example_action.json的相对路径
        tests_data = args.run[0]
        run(os.getcwd(),tests_data)

    #   根据tests文件下的json文件内connection的内容参数,仅测试连接器功能
    elif args.test:
        #   需要当前工作区的绝对路径和example_action.json的相对路径
        tests_data = args.test[0]
        test(os.getcwd(),tests_data)

    elif args.http:
        #   需要当前工作区的绝对路径
        http(os.getcwd())

    #   打包在线包
    elif args.tarball:
        tarball(os.getcwd())

    #   打包离线包
    elif args.mkimg:
        mkimg(os.getcwd())

    elif args.testserver:
        testserver(os.getcwd())

    else:
        logging.info("输入 chariot-plugin -h 以获取帮助")


