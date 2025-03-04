from astrbot.api.all import *
from astrbot.api.event.filter import command, event_message_type, EventMessageType
import json
import os
import datetime
import logging
from typing import Dict, Any

logger = logging.getLogger("CheckInPlugin")

# 数据存储路径
DATA_DIR = os.path.join("data", "plugins", "checkin")
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "checkin_data.json")

# 初始化数据结构
CheckinData = Dict[str, Dict[str, Any]]

def _load_data() -> CheckinData:
    """加载签到数据"""
    try:
        if not os.path.exists(DATA_FILE):
            return {}
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"数据加载失败: {str(e)}")
        return {}

def _save_data(data: CheckinData):
    """保存签到数据"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"数据保存失败: {str(e)}")

def _get_today() -> str:
    """获取当前日期字符串 (格式: YYYY-MM-DD)"""
    return datetime.datetime.now().strftime("%Y-%m-%d")

def _get_month() -> str:
    """获取当前月份字符串 (格式: YYYY-MM)"""
    return datetime.datetime.now().strftime("%Y-%m")

def _calculate_rewards(continuous_days: int) -> int:
    """计算签到奖励 (示例: 基础10分 + 连续签到额外奖励)"""
    return 10 + continuous_days * 2

@register(
    "签到插件",
    "腾讯元宝",
    "多维度排行榜签到系统",
    "1.0.0"
)
class CheckInPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.data = _load_data()

    @command("签到", alias=["打卡"])
    async def check_in(self, event: AstrMessageEvent):
        """每日签到获取奖励"""
        user_id = event.get_sender_id()
        today = _get_today()
        month = _get_month()

        # 初始化用户数据
        if user_id not in self.data:
            self.data[user_id] = {
                "total_days": 0,
                "month_days": 0,
                "continuous_days": 0,
                "total_rewards": 0,
                "month_rewards": 0,
                "last_checkin": None
            }

        user_data = self.data[user_id]

        # 检查今日是否已签到
        if user_data["last_checkin"] == today:
            yield event.plain_result("⚠️ 今日已签到，请勿重复操作")
            return

        # 计算连续签到
        last_date = user_data["last_checkin"]
        if last_date and (datetime.datetime.strptime(today, "%Y-%m-%d") - datetime.datetime.strptime(last_date, "%Y-%m-%d")).days == 1:
            user_data["continuous_days"] += 1
        else:
            user_data["continuous_days"] = 1

        # 更新数据
        rewards = _calculate_rewards(user_data["continuous_days"])
        user_data.update({
            "total_days": user_data["total_days"] + 1,
            "month_days": user_data["month_days"] + 1 if month == _get_month() else 1,
            "total_rewards": user_data["total_rewards"] + rewards,
            "month_rewards": user_data["month_rewards"] + rewards if month == _get_month() else rewards,
            "last_checkin": today
        })

        _save_data(self.data)
        yield event.plain_result(
            f"🎉 签到成功！\n"
            f"连续签到: {user_data['continuous_days']} 天\n"
            f"今日奖励: {rewards} 积分"
        )

    def _generate_rank(self, key: str, title: str) -> str:
        """生成排行榜"""
        sorted_users = sorted(
            self.data.items(),
            key=lambda x: x[1][key],
            reverse=True
        )[:10]  # 取前10名

        if not sorted_users:
            return f"暂无{title}数据"

        msg = [f"🏆 {title} TOP {len(sorted_users)}"]
        for i, (user_id, data) in enumerate(sorted_users):
            msg.append(f"{i+1}. 用户 {user_id[-4:]} - {data[key]}")
        return "\n".join(msg)

    @command("签到排行榜", alias=["签到排行"])
    async def show_rank(self, event: AstrMessageEvent):
        """查看所有排行榜"""
        yield event.plain_result(
            "请选择具体排行榜类型：\n"
            "/签到总奖励排行榜\n"
            "/签到月奖励排行榜\n"
            "/签到总天数排行榜\n"
            "/签到月天数排行榜\n"
            "/签到今日排行榜"
        )

    @command("签到总奖励排行榜", alias=["签到总排行"])
    async def total_rewards_rank(self, event: AstrMessageEvent):
        """总奖励排行榜"""
        yield event.plain_result(self._generate_rank("total_rewards", "累计奖励积分"))

    @command("签到月奖励排行榜", alias=["签到月排行"])
    async def month_rewards_rank(self, event: AstrMessageEvent):
        """本月奖励排行榜"""
        yield event.plain_result(self._generate_rank("month_rewards", "本月奖励积分"))

    @command("签到总天数排行榜", alias=["签到总天数排行"])
    async def total_days_rank(self, event: AstrMessageEvent):
        """总签到天数排行榜"""
        yield event.plain_result(self._generate_rank("total_days", "累计签到天数"))

    @command("签到月天数排行榜", alias=["签到月天数排行"])
    async def month_days_rank(self, event: AstrMessageEvent):
        """本月签到天数排行榜"""
        yield event.plain_result(self._generate_rank("month_days", "本月签到天数"))

    @command("签到今日排行榜", alias=["签到今日排行", "签到日排行"])
    async def today_rank(self, event: AstrMessageEvent):
        """今日签到排行榜"""
        today_users = [
            (user_id, data) 
            for user_id, data in self.data.items() 
            if data["last_checkin"] == _get_today()
        ]
        sorted_users = sorted(today_users, key=lambda x: x[1]["continuous_days"], reverse=True)[:10]

        if not sorted_users:
            yield event.plain_result("今日暂无签到数据")
            return

        msg = ["🏆 今日签到榜 TOP 10"]
        for i, (user_id, data) in enumerate(sorted_users):
            msg.append(f"{i+1}. 用户 {user_id[-4:]} - 连续 {data['continuous_days']} 天")
        yield event.plain_result("\n".join(msg))