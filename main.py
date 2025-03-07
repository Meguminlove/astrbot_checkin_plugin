from astrbot.api.all import *
from astrbot.api.event.filter import command, event_message_type, EventMessageType
import json
import os
import datetime
import logging
import random
import hashlib
from typing import Dict, Any

logger = logging.getLogger("CheckInPlugin")

DATA_DIR = os.path.join("data", "plugins", "astrbot_checkin_plugin")
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "checkin_data.json")

MOTIVATIONAL_MESSAGES = [
    "不相信自己的人，连努力的价值都没有 💪",
    # ... 保持原有语录不变 ...
]

def _load_data() -> dict:
    try:
        if not os.path.exists(DATA_FILE):
            return {}
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"数据加载失败: {str(e)}")
        return {}

def _save_data(data: dict):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"数据保存失败: {str(e)}")

def _get_context_id(event: AstrMessageEvent) -> str:
    try:
        if hasattr(event, 'message') and hasattr(event.message, 'source'):
            source = event.message.source
            if hasattr(source, 'group_id') and source.group_id:
                return f"group_{source.group_id}"
            if hasattr(source, 'user_id') and source.user_id:
                return f"private_{source.user_id}"
        
        if hasattr(event, 'group_id') and event.group_id:
            return f"group_{event.group_id}"
        if hasattr(event, 'user_id') and event.user_id:
            return f"private_{event.user_id}"
        
        event_str = f"{event.get_message_id()}-{event.get_time()}"
        return f"ctx_{hashlib.md5(event_str.encode()).hexdigest()[:6]}"
        
    except Exception as e:
        logger.error(f"上下文ID生成异常: {str(e)}")
        return "default_ctx"

def _generate_rewards() -> int:
    return random.randint(1, 30)

@register("签到插件", "Kimi&Meguminlove", "多维度排行榜签到系统", "1.0.4", "https://github.com/Meguminlove/astrbot_checkin_plugin")
class CheckInPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.data = _load_data()

    @command("签到", alias=["打卡"])
    async def check_in(self, event: AstrMessageEvent):
        try:
            ctx_id = _get_context_id(event)
            user_id = event.get_sender_id()
            today = datetime.date.today().isoformat()
            
            # 获取带保底的用户名
            current_username = event.get_sender_name() or f"用户{user_id[-4:]}"

            ctx_data = self.data.setdefault(ctx_id, {})
            user_data = ctx_data.setdefault(user_id, {
                "username": current_username,  # 初始化时确保有值
                "total_days": 0,
                "continuous_days": 0,
                "month_days": 0,
                "total_rewards": 0,
                "month_rewards": 0,
                "last_checkin": None
            })
            
            # 强制更新用户名（即使存在）
            user_data["username"] = current_username

            if user_data["last_checkin"] == today:
                yield event.plain_result("⚠️ 今日已签订契约，请勿重复操作")
                return

            last_date = user_data["last_checkin"]
            current_month = today[:7]
            
            if last_date:
                last_day = datetime.date.fromisoformat(last_date)
                if (datetime.date.today() - last_day).days == 1:
                    user_data["continuous_days"] += 1
                else:
                    user_data["continuous_days"] = 1
                
                if last_date[:7] != current_month:
                    user_data["month_days"] = 0
                    user_data["month_rewards"] = 0
            else:
                user_data["continuous_days"] = 1

            rewards = _generate_rewards()
            user_data.update({
                "total_days": user_data["total_days"] + 1,
                "month_days": user_data["month_days"] + 1,
                "total_rewards": user_data["total_rewards"] + rewards,
                "month_rewards": user_data["month_rewards"] + rewards,
                "last_checkin": today
            })

            _save_data(self.data)
            
            selected_msg = random.choice(MOTIVATIONAL_MESSAGES)
            yield event.plain_result(
                f"✨【契约成立】\n"
                f"📅 连续签订契约: {user_data['continuous_days']}天\n"
                f"🎁 获得星之碎片: {rewards}个\n"
                f"💬 契约签订寄语: {selected_msg}"
            )

        except Exception as e:
            logger.error(f"签到处理异常: {str(e)}", exc_info=True)
            yield event.plain_result("🔧 契约服务暂时不可用，请联系管理员")

    def _get_rank(self, event: AstrMessageEvent, key: str) -> list:
        ctx_id = _get_context_id(event)
        ctx_data = self.data.get(ctx_id, {})
        return sorted(ctx_data.items(), key=lambda x: x[1][key], reverse=True)[:10]

    def _generate_rank_msg(self, title: str, ranked: list, value_key: str, unit: str) -> str:
        msg = [f"🏆 {title}"]
        for i, (uid, data) in enumerate(ranked):
            # 用户名三重保障机制
            username = data.get('username') or f"用户{uid[-4:]}"
            if not username.strip():
                username = f"用户{uid[-4:]}"
            msg.append(f"{i+1}. 契约者 {username} - {data[value_key]}{unit}")
        return "\n".join(msg)

    @command("签到排行榜", alias=["签到排行"])
    async def show_rank_menu(self, event: AstrMessageEvent):
        yield event.plain_result(
            "📊 排行榜类型：\n"
            "/签到总奖励排行榜 - 累计获得星之碎片\n"
            "/签到月奖励排行榜 - 本月获得星之碎片\n"
            "/签到总天数排行榜 - 历史签到总天数\n"
            "/签到月天数排行榜 - 本月签到天数\n"
            "/签到今日排行榜 - 今日签到用户榜"
        )

    @command("签到总奖励排行榜", alias=["签到总排行"])
    async def total_rewards_rank(self, event: AstrMessageEvent):
        ranked = self._get_rank(event, "total_rewards")
        yield event.plain_result(self._generate_rank_msg("累计星之碎片排行榜", ranked, "total_rewards", "个"))

    @command("签到月奖励排行榜", alias=["签到月排行"])
    async def month_rewards_rank(self, event: AstrMessageEvent):
        ranked = self._get_rank(event, "month_rewards")
        yield event.plain_result(self._generate_rank_msg("本月星之碎片排行榜", ranked, "month_rewards", "个"))

    @command("签到总天数排行榜", alias=["签到总天数排行"])
    async def total_days_rank(self, event: AstrMessageEvent):
        ranked = self._get_rank(event, "total_days")
        yield event.plain_result(self._generate_rank_msg("累计契约天数榜", ranked, "total_days", "天"))

    @command("签到月天数排行榜", alias=["签到月天数排行"])
    async def month_days_rank(self, event: AstrMessageEvent):
        ranked = self._get_rank(event, "month_days")
        yield event.plain_result(self._generate_rank_msg("本月契约天数榜", ranked, "month_days", "天"))

    @command("签到今日排行榜", alias=["签到今日排行", "签到日排行"])
    async def today_rank(self, event: AstrMessageEvent):
        ctx_id = _get_context_id(event)
        today = datetime.date.today().isoformat()
        ranked = sorted(
            [(uid, data) for uid, data in self.data.get(ctx_id, {}).items() 
             if data["last_checkin"] == today],
            key=lambda x: x[1]["continuous_days"],
            reverse=True
        )[:10]
        yield event.plain_result(self._generate_rank_msg("今日契约榜", ranked, "continuous_days", "天"))