import os
import argparse
from bot_framework import BaseBot
from customer_service_bot import CustomerServiceBot
from report_bot import ReportBot

# 配置路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# 创建配置和数据目录
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Telegram Bot System')
    parser.add_argument('--bot-type', type=str, required=True, 
                        help='Bot type (base, customer_service, report)')
    parser.add_argument('--token', type=str, required=True, 
                        help='Telegram bot token')
    args = parser.parse_args()
    
    # 根据bot类型创建相应的机器人实例
    if args.bot_type == 'base':
        bot = BaseBot(
            token=args.token,
            bot_type="基础",
            db_path=os.path.join(DATA_DIR, 'base_bot.db'),
            config_path=os.path.join(CONFIG_DIR, 'base_bot.json')
        )
    elif args.bot_type == 'customer_service':
        bot = CustomerServiceBot(
            token=args.token,
            db_path=os.path.join(DATA_DIR, 'customer_service_bot.db'),
            config_path=os.path.join(CONFIG_DIR, 'customer_service_bot.json')
        )
    elif args.bot_type == 'report':
        bot = ReportBot(
            token=args.token,
            db_path=os.path.join(DATA_DIR, 'report_bot.db'),
            config_path=os.path.join(CONFIG_DIR, 'report_bot.json')
        )
    else:
        print(f"未知的机器人类型: {args.bot_type}")
        return
    
    # 启动机器人
    print(f"启动 {args.bot_type} 机器人...")
    bot.run()

if __name__ == '__main__':
    main()    
    
