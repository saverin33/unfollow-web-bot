
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bot para Instagram que deixa de seguir quem não te segue de volta.
Versão simplificada com delay e controle de limite diário.
"""

import os
import time
import json
import random
from datetime import datetime
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, PleaseWaitFewMinutes

class InstagramUnfollowBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = Client()
        self.client.delay_range = [1, 3]
        self.client.user_agent = "Instagram 219.0.0.12.117 Android"
        self.log_dir = "instagram_logs"
        os.makedirs(self.log_dir, exist_ok=True)

    def _log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] [{level}] {message}"
        print(msg)

    def login(self):
        try:
            self.client.login(self.username, self.password)
            self._log("Login realizado com sucesso!")
            return True
        except Exception as e:
            self._log(f"Erro ao fazer login: {e}", "ERROR")
            return False

    def get_users_to_unfollow(self):
        self._log("Coletando seguidores...")
        followers = self.client.user_followers(self.client.user_id)
        self._log(f"Seguidores: {len(followers)}")

        self._log("Coletando seguidos...")
        following = self.client.user_following(self.client.user_id)
        self._log(f"Seguindo: {len(following)}")

        to_unfollow = set(following.keys()) - set(followers.keys())
        self._log(f"Encontrados {len(to_unfollow)} que não te seguem.")
        return list(to_unfollow)

    def unfollow_users(self, users, delay_seconds=120, max_unfollows=50):
        self._log(f"Iniciando unfollow em até {max_unfollows} usuários")
        count = 0
        for user_id in users[:max_unfollows]:
            try:
                user = self.client.user_info(user_id)
                username = user.username
                self.client.user_unfollow(user_id)
                self._log(f"Deixou de seguir: {username}")
                count += 1
                time.sleep(random.randint(1, delay_seconds))
            except PleaseWaitFewMinutes as e:
                self._log(f"Pausado pelo Instagram: {e}", "WARNING")
                break
            except Exception as e:
                self._log(f"Erro ao deixar de seguir {user_id}: {e}", "ERROR")
        self._log(f"Unfollows finalizados: {count}")

    def run(self, delay_seconds=120, max_unfollows=50):
        if not self.login():
            return
        users = self.get_users_to_unfollow()
        if users:
            self.unfollow_users(users, delay_seconds, max_unfollows)
        else:
            self._log("Sem usuários para deixar de seguir.")
