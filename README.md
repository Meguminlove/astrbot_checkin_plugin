达莉娅AstrBot 简单文字签到插件
# 签到插件(此插件是AI编写)

## 插件说明
- **插件名称**：签到插件
- **作者**：Kimi AI
- **版本**：1.0.0
- **描述**：含多维排行榜的异世界签到系统
- **注意**QQ官方机器人无法正常获取群友ID因为加密

## 功能说明

### 签到功能
- 用户可以通过发送 `/签到` 或 `/打卡` 指令进行签到。
- 插件会记录用户的签到天数、连续签到天数以及累计奖励。
- 每次签到会根据连续签到天数计算奖励（星之碎片），奖励公式为：10 + (连续天数 ** 2)。
- 签到成功后，用户会收到一条包含签到信息和随机励志寄语的消息。

### 排行榜功能
- 插件提供三种排行榜，分别是：
  - 签到总奖励排行榜：显示累计获得星之碎片最多的前10名用户。
  - 签到月奖励排行榜：显示本月累计获得星之碎片最多的前10名用户。
  - 签到今日排行榜：显示今日签到的前10名用户，按连续签到天数排序。
- 用户可以通过发送 `/签到总奖励排行榜`、`/签到月奖励排行榜` 或 `/签到今日排行榜` 指令查看对应的排行榜。

### 数据管理
- 插件会自动保存用户的签到数据到本地文件 `checkin_data.json`。
- 数据包括用户的总签到天数、本月签到天数、连续签到天数、累计奖励、本月奖励以及签到历史记录。
- 数据会定期保存，确保用户数据不会丢失。

### 励志寄语
- 插件包含一个励志寄语库，每次用户签到时会随机选择一条寄语作为签到反馈的一部分。
- 寄语库中包含50条励志语录，涵盖各种风格和主题。

### 跨月处理
- 插件会自动处理跨月签到，每月的签到数据会独立统计。
- 每月的签到天数和奖励会重置，确保数据的准确性。

### 连续签到计算
- 插件会根据用户的签到记录计算连续签到天数。
- 如果用户在连续两天内签到，连续签到天数会增加；如果中断，则重新计算。

## 使用方法

### 签到
- 用户发送 `/签到` 或 `/打卡` 指令进行签到。
- 示例：
  ```
  /签到
  ```
- 回复示例：
  ```
  ✨【契约成立】
  📅 连续签到: 5天
  🎁 获得星之碎片: 25个
  💬 契约寄语: 每天进步一点点！🚀 不相信自己的人，连努力的价值都没有
  ```

### 查看排行榜
- 用户发送 `/签到总奖励排行榜`、`/签到月奖励排行榜` 或 `/签到今日排行榜` 指令查看对应的排行榜。
- 示例：
  ```
  /签到总奖励排行榜
  ```
- 回复示例：
  ```
  🏆【永恒星辉榜】
  1. 旅人1234 ➤ 1000
  2. 旅人5678 ➤ 800
  3. 旅人9012 ➤ 600
  4. 旅人3456 ➤ 400
  5. 旅人7890 ➤ 300
  6. 旅人2345 ➤ 200
  7. 旅人6789 ➤ 150
  8. 旅人1357 ➤ 100
  9. 旅人2468 ➤ 80
  10. 旅人5678 ➤ 50
  ```

## 配置文件
插件会自动创建一个配置文件 `checkin_data.json`，用于保存用户的签到数据。配置文件的结构如下：
```json
{
  "user_id_1": {
    "total_days": 10,
    "month_days": 5,
    "continuous_days": 5,
    "total_rewards": 100,
    "month_rewards": 50,
    "history": {
      "2024-10": [1, 2, 3, 4, 5],
      "2024-11": [1, 2, 3]
    }
  },
  "user_id_2": {
    "total_days": 5,
    "month_days": 5,
    "continuous_days": 5,
    "total_rewards": 50,
    "month_rewards": 50,
    "history": {
      "2024-10": [1, 2, 3, 4, 5],
      "2024-11": [1, 2, 3]
    }
  }
}
```

## 示例

### 签到示例
用户发送 `/签到` 指令，插件会回复：
```
✨【契约成立】
📅 连续签到: 5天
🎁 获得星之碎片: 25个
💬 契约寄语: 每天进步一点点！🚀 不相信自己的人，连努力的价值都没有
```

### 查看总奖励排行榜示例
用户发送 `/签到总奖励排行榜` 指令，插件会回复：
```
🏆【永恒星辉榜】
1. 旅人1234 ➤ 1000
2. 旅人5678 ➤ 800
3. 旅人9012 ➤ 600
4. 旅人3456 ➤ 400
5. 旅人7890 ➤ 300
6. 旅人2345 ➤ 200
7. 旅人6789 ➤ 150
8. 旅人1357 ➤ 100
9. 旅人2468 ➤ 80
10. 旅人5678 ➤ 50
```

---
