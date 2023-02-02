# Telegram Bot for Picture Send

## Overview

This is a telegram bot for send pictures with different frequency and scheduling in advance. The bot is designed to be used only by administrators, who can add or remove other administrators.

## Features

- Share pictures every 15 minutes
- Schedule pictures to be sent in advance
- Delete pictures
- Limited to administrator access only
- Ability to add/remove administrators

## Usage

1. Add the bot to your telegram channel as an administrator
2. Use the following commands to manage the bot:
- `/start` - start the bot 
- `/admin_new` - add new admin
- `/admin_delete` - delete admin
- `/admin_list` - list of admins
- `/edit_time` - also the same
- `/edit_total_time` - total time
- `/info_schedule` - information about scheduled pictures
- `/info_time` - information about unscheduled pictures, those that come every 15 minutes
- `/delete_time` - deletes everything
