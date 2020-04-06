#!/bin/usr/env python3
import discord
import logger_lib as log

class DiscordClient():

    def get_properties(self):
        return ["webhook", "botname"]

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

    # Sends a Discord message with links and info of new ads
    def send_ads(self, ad_dict, discord_title, **kwargs):
        global webhook_cache

        if not "webhook_cache" in globals():
            webhook_cache = {}

        webhook_url = kwargs["webhook"]
        self.bot_name = kwargs["botname"]

        if not webhook_url in webhook_cache:
            webhook_cache[webhook_url] = discord.Webhook.from_url(webhook_url, adapter=discord.RequestsWebhookAdapter())

        self.webhook = webhook_cache[webhook_url]

        title = self.__create_discord_title(discord_title, len(ad_dict))

        result = self.webhook.send(content=f"**{title}**", username=self.bot_name)

        for ad_id in ad_dict:
            embed = self.__create_discord_embed(ad_dict, ad_id)

            self.webhook.send(embed=embed, username=self.bot_name)

    def __create_discord_title(self, discord_title, ad_count):
        if ad_count > 1:
            return str(ad_count) + ' New ' + discord_title + ' Ads Found!'

        return 'One New ' + discord_title + ' Ad Found!'

    def __create_discord_embed(self, ad_dict, ad_id):

        embed = discord.Embed()
        embed.colour = discord.Colour.green()
        embed.url=ad_dict[ad_id]['Url']

        try:
            embed.title = f"{ad_dict[ad_id]['Title']}"

            if ad_dict[ad_id]['Location'] != "":
                embed.add_field(name="Location", value=ad_dict[ad_id]['Location'])

            if ad_dict[ad_id]['Date'] != "":
                embed.add_field(name="Date", value=ad_dict[ad_id]['Date'])
            
            if ad_dict[ad_id]['Price'] != "":
                embed.add_field(name="Price", value=ad_dict[ad_id]['Price'])

            if ad_dict[ad_id]['Description'] != "":
                embed.add_field(name="Description", value=ad_dict[ad_id]['Description'], inline=False)

            if ad_dict[ad_id]['Details'] != "":
                embed.add_field(name="Details", value=ad_dict[ad_id]['Details'], inline=False)
            
        except KeyError:
            embed.title = f"{ad_dict[ad_id]['Title']}"

        return embed

