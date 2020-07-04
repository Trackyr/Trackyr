#!/bin/usr/env python3
import discord

class DiscordClient():
    def get_properties(self):
        return ["webhook", "botname", "avatar"]

    def is_property_valid(self, key, value):
        if key == "webhook":
            try:
                discord.Webhook.from_url(value, adapter=discord.RequestsWebhookAdapter())
                return True, None
            except:
                return False, "Webhook is invalid"
        elif key == "botname":
            if value == "" or value is None:
                return False, "Botname cannot be empty"
            else:
                return True, None
        else:
            raise ValueError(f"Invalid property: {key}")

        return False

    def send(self, title, message, **kwargs):
        global webhook_cache

        if not "webhook_cache" in globals():
            webhook_cache = {}

        webhook_url = kwargs["webhook"]
        self.bot_name = kwargs["botname"]
        self.avatar = kwargs["avatar"]

        if not webhook_url in webhook_cache:
            webhook_cache[webhook_url] = discord.Webhook.from_url(webhook_url, adapter=discord.RequestsWebhookAdapter())

        self.webhook = webhook_cache[webhook_url]

        self.webhook.send(content=f"**{title}**", username=self.bot_name, avatar_url=self.avatar)
        self.webhook.send(content=message, username=self.bot_name, avatar_url=self.avatar)

    # Sends a Discord message with links and info of new ads
    def send_ads(self, ad_dict, discord_title, colour_flag, **kwargs):
        global webhook_cache

        if not "webhook_cache" in globals():
            webhook_cache = {}

        webhook_url = kwargs["webhook"]
        self.bot_name = kwargs["botname"]
        self.avatar = kwargs["avatar"]


        if not webhook_url in webhook_cache:
            webhook_cache[webhook_url] = discord.Webhook.from_url(webhook_url, adapter=discord.RequestsWebhookAdapter())

        self.webhook = webhook_cache[webhook_url]

        title = self.__create_discord_title(discord_title, len(ad_dict))

        self.webhook.send(content=f"**{title}**", username=self.bot_name, avatar_url=self.avatar)

        for ad_id in ad_dict:
            embed = self.__create_discord_embed(ad_dict, ad_id, colour_flag)

            self.webhook.send(embed=embed, username=self.bot_name, avatar_url=self.avatar)

    def __create_discord_title(self, discord_title, ad_count):
        if ad_count > 1:
            return str(ad_count) + ' New ' + discord_title + ' Ads Found!'

        return 'One New ' + discord_title + ' Ad Found!'

    def __create_discord_embed(self, ad_dict, ad_id, colour_flag):
        embed = discord.Embed()

        colour_flag = colour_flag.lstrip("#")
        if colour_flag == "":
            colour_flag="ff8c00"
        embed.colour = int(colour_flag, base=16)

        embed.url=ad_dict[ad_id]['Url']

        try:
            embed.title = f"{ad_dict[ad_id]['Title']}"

            if ad_dict[ad_id]['Location'] != "":
                location=ad_dict[ad_id]['Location']
                location_trunct=(location[:100] + '..') if len(location) > 100 else location
                embed.add_field(name="Location", value=location_trunct)

            if ad_dict[ad_id]['Date'] != "":
                date=ad_dict[ad_id]['Date']
                date_trunct=(date[:75] + '..') if len(date) > 75 else date
                embed.add_field(name="Date", value=date_trunct)

            if ad_dict[ad_id]['Price'] != "":
                price=ad_dict[ad_id]['Price']
                price_trunct=(price[:25] + '..') if len(price) > 25 else price
                embed.add_field(name="Price", value=price_trunct)

            if ad_dict[ad_id]['Description'] != "":
                description=ad_dict[ad_id]['Description']
                description_trunct=(description[:500] + '..') if len(description) > 500 else description
                embed.add_field(name="Description", value=description_trunct, inline=False)

            if ad_dict[ad_id]['Details'] != "":
                details=ad_dict[ad_id]['Details']
                details_trunct=(details[:100] + '..') if len(details) > 100 else details
                embed.add_field(name="Details", value=details_trunct, inline=False)

        except KeyError:
            embed.title = f"{ad_dict[ad_id]['Title']}"

        return embed
