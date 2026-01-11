import json
import os
from datetime import datetime


class UserStats:
    def __init__(self):
        self.stats_file = 'user_stats.json'
        self.stats = self.load_stats()

    def load_stats(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_stats(self):
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

    def add_request(self, user_id, sign):
        today = datetime.now().strftime("%Y-%m-%d")

        if str(user_id) not in self.stats:
            self.stats[str(user_id)] = {
                'first_seen': today,
                'total_requests': 0,
                'daily_requests': {},
                'signs': {}
            }

        user_data = self.stats[str(user_id)]
        user_data['total_requests'] = user_data.get('total_requests', 0) + 1

        # Ежедневная статистика
        if today not in user_data['daily_requests']:
            user_data['daily_requests'][today] = 0
        user_data['daily_requests'][today] += 1

        # Статистика по знакам
        if sign not in user_data['signs']:
            user_data['signs'][sign] = 0
        user_data['signs'][sign] += 1

        self.save_stats()
        return user_data

    def get_stats(self, user_id):
        return self.stats.get(str(user_id), {})

    def get_total_stats(self):
        total_users = len(self.stats)
        total_requests = sum(user['total_requests'] for user in self.stats.values() if 'total_requests' in user)

        # Самый популярный знак
        sign_counts = {}
        for user_data in self.stats.values():
            for sign, count in user_data.get('signs', {}).items():
                sign_counts[sign] = sign_counts.get(sign, 0) + count

        most_popular = max(sign_counts.items(), key=lambda x: x[1]) if sign_counts else ("нет данных", 0)

        return {
            'total_users': total_users,
            'total_requests': total_requests,
            'most_popular_sign': most_popular[0],
            'most_popular_count': most_popular[1]
        }