import datetime
import main1

USER_INFO = {
    '李傲': {'password': '2314353', 'login_count': 0, 'last_login': None},
    '常文艺': {'password': '2314317', 'login_count': 0, 'last_login': None},
    '侯俊丽': {'password': '2314333', 'login_count': 0, 'last_login': None},
    '邢广威': {'password': '2314345', 'login_count': 0, 'last_login': None},
    '张泽轩': {'password': '2314341', 'login_count': 0, 'last_login': None}
}

def login():
    while True:
        username = input("用户名: ")
        password = input("密码: ")

        if username in USER_INFO and USER_INFO[username]['password'] == password:
            USER_INFO[username]['login_count'] += 1
            USER_INFO[username]['last_login'] = datetime.datetime.now()
            print("登录成功！")
            return username
        else:
            print("用户名或密码错误，请重新输入。")


def open_dumbbell_section(username):

    print(f"尊敬的用户{username}，您的哑铃管家已准备就绪，请开始训练。")
    start_time = datetime.datetime.now()
    print(f"开始时间：{start_time}")
    main1.main1()
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time
    print(f"结束时间：{end_time}")
    print(f"训练时长：{elapsed_time}")


def open_pending_section(username):

    print(f"尊敬的用户{username}，您的……管家已准备就绪，请开始训练。")

    start_time = datetime.datetime.now()
    print(f"开始时间：{start_time}")
    # 待定部分
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time
    print(f"结束时间：{end_time}")
    print(f"训练时长：{elapsed_time}")


def main():
    print("欢迎使用24h健身管家程序。")
    print("请输入您的用户名和密码进行登录。")

    username = login()
    if username:
        info = USER_INFO[username]
        print(f"用户{username}您好，"
              f"您目前的登录次数是 {info['login_count']}次。")
        if info['last_login']:
            elapsed_time = datetime.datetime.now() - info['last_login']
            print(f"您上次登录的时间为{info['last_login']}，已经过去了{elapsed_time}。")
        else:
            print("上次登录时间: 无")

        while True:
            choice = input("请输入选项 (1-哑铃部分, 2-待定部分, q-退出): ")
            if choice == '1':
                open_dumbbell_section(username)
            elif choice == '2':
                open_pending_section(username)
            elif choice.lower() == 'q':
                print("再见，期待您的再次使用。")
                return
            else:
                print("输入无效，请重新输入。")


if __name__ == "__main__":
    main()
