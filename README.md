# Telegram Mastodon Forward

A simple bot to auto forwarding messages from telegram channel to mastodon.

# Feature

- Support multi message types
    - Text
    - Photo
    - Audio
    - Video
    - Media Group

# Deploy

- Go to `https://<YOUR MASTODON SITE>/settings/applications`, click `New Application`, fill in `Application name` and
  click `Submit` button. Save the `Client key`, `Client secret` and `Your access token` field.

- Go to https://botfather.t.me , create a new bot and save the token.

- ```bash
  git clone https://github.com/WorldObservationLog/Telegram-Mastodon-Forward
  cd Telegram-Mastodon-Forward
  python3 -m venv venv
  # For *nix
  source venv/Scripts/activate
  # For Windows
  venv/Scripts/activate.bat
  pip install -r requirements.txt
  cp config.example.toml
  # Then edit the config.toml
  python main.py
  ```

  