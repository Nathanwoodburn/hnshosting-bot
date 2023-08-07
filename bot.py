import subprocess
import os
from dotenv import load_dotenv
import discord
from discord import app_commands
import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

icann_regex = r'^https://[a-z0-9]+(\.[a-z0-9]+)+(/[a-zA-Z0-9-.]*)*$'
handshake_regex = r'^[a-z0-9]+(\.[a-z0-9]+)*$'

@tree.command(name = "mirror", description = "Create a mirror of an ICANN site on a Handshake domain")
async def mirror(interaction, handshakedomain: str, icannurl: str):
    print("Creating mirror to " + icannurl + " from " + handshakedomain + "...")
    if not icannurl.startswith("https://"):
        await interaction.response.send_message("Please use https:// for the ICANN URL", ephemeral=True)
        return
    
    if not re.match(icann_regex, icannurl):
        await interaction.response.send_message("Please use a valid ICANN URL", ephemeral=True)
        return
    if not re.match(handshake_regex, handshakedomain):
        await interaction.response.send_message("Please use a valid Handshake domain", ephemeral=True)
        return


    await interaction.response.send_message("Creating mirror to " + icannurl + " from " + handshakedomain + "..." + "\nCheck your DM for the status of your mirror.", ephemeral=True)

    # Get user from interaction
    user = interaction.user
    handshakedomain_str = str(handshakedomain)
    icannurl_str = str(icannurl)
    user_str = str(user.id)
    command = ['./proxy.sh', handshakedomain_str, icannurl_str, user_str]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
        print("TLSA output:")
        tlsa = get_tlsa(output)
        if tlsa is not None:
            print(tlsa)
            message = "Mirror setup! Add this TLSA record\n`_443._tcp." + handshakedomain_str + "` : `" + tlsa + "`\nAdd this A\n`" + handshakedomain_str + "` : `152.69.188.246`"
            await user.send(message)
        else:
            error = get_error(output)
            await user.send(error)
        
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed with exit code {e.returncode}.")
        await user.send(f"Command execution failed.")
    updateStatus()

@tree.command(name = "delete", description = "Delete a Handshake domain from the system")
async def delete(interaction, handshakedomain: str):
    print("Deleting " + handshakedomain + "...")

    if not re.match(handshake_regex, handshakedomain):
        await interaction.response.send_message("Please use a valid Handshake domain", ephemeral=True)
        return
    await interaction.response.send_message("Deleting " + handshakedomain + "..." + "\nCheck your DM for status.", ephemeral=True)
    # Get user from interaction
    user = interaction.user
    handshakedomain_str = str(handshakedomain)
    user_str = str(user.id)

    # Construct the command
    command = ['./delete.sh', handshakedomain_str, user_str]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
        print("Delete output:")
        out=output.split("\n")[0]
        print(out)
        await user.send(out)
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed with exit code {e.returncode}.")
        await user.send(f"Command execution failed.")
    updateStatus()

@tree.command(name = "list", description = "List all Handshake mirrors")
async def list(interaction):
    print("Listing mirrors...")
    # Verify user is bot owner
    user = interaction.user
    if user != interaction.client.application.owner:
        await interaction.response.send_message("You don't have permission to do that.", ephemeral=True)
        print(user + " tried to list mirrors.")
        return
    
    # List all files in the directory using os
    files = os.listdir("/etc/nginx/sites-available")
    # Remove default
    files.remove("default")
    await interaction.response.send_message("Here are all the mirrors:\n" + "\n".join(files), ephemeral=True)
    
@tree.command(name = "tlsa", description = "Get the TLSA record for an existing Handshake domain")
async def tlsa(interaction, handshakedomain: str):
    if not re.match(handshake_regex, handshakedomain):
        await interaction.response.send_message("Please use a valid Handshake domain", ephemeral=True)
        return

    print("Getting TLSA record for " + handshakedomain + "...")
    # Get user from interaction
    output = subprocess.check_output(['./tlsa.sh', handshakedomain], stderr=subprocess.STDOUT, text=True)
    await interaction.response.send_message(output, ephemeral=True)

@tree.command(name = "git", description = "Create a website from a git repo of html files")
async def git(interaction, handshakedomain: str, giturl: str):
    if not re.match(handshake_regex, handshakedomain):
        await interaction.response.send_message("Please use a valid Handshake domain", ephemeral=True)
        return
    
    if not re.match(icann_regex, giturl):
        await interaction.response.send_message("Please use a valid git URL\nThis should be a https url", ephemeral=True)
        return

    print("Creating website from " + giturl + " on " + handshakedomain + "...")
    await interaction.response.send_message("Creating website from " + giturl + " on " + handshakedomain + "..." + "\nCheck your DM for the status of your website.", ephemeral=True)
    user = interaction.user
    handshakedomain_str = str(handshakedomain)
    user_str = str(user.id)
    giturl_str = str(giturl)
    output = subprocess.check_output(['./git.sh', handshakedomain_str, giturl_str, user_str], stderr=subprocess.STDOUT, text=True)
    # Check if output contains any errors
    lowercase_string = output.lower()
    # Check if the lowercase string contains the word "error"
    if "error" in lowercase_string:
        await user.send("Failed with error:\n" + output)
        return

    output = subprocess.check_output(['./tlsa.sh', handshakedomain_str], stderr=subprocess.STDOUT, text=True)
    # Get only second line
    output = output.split("\n")[1]
    await user.send("Website created! Add this TLSA record\n`_443._tcp." + handshakedomain_str + "` : `" + output + "`\nAdd this A\n`" + handshakedomain_str + "` : `152.69.188.246`")

@tree.command(name = "gitpull", description = "Get the latest changes from a git repo of html files")
async def gitpull(interaction, handshakedomain: str):
    if not re.match(handshake_regex, handshakedomain):
        await interaction.response.send_message("Please use a valid Handshake domain", ephemeral=True)
        return
    print("Pulling latest changes from " + handshakedomain + "...")
    await interaction.response.send_message("Pulling changes for " + handshakedomain + "...", ephemeral=True)
    user = interaction.user
    handshakedomain_str = str(handshakedomain)
    user_str = str(user.id)
    output = subprocess.check_output(['./gitpull.sh', handshakedomain_str, user_str], stderr=subprocess.STDOUT, text=True)
    # Check if output contains any errors
    lowercase_string = output.lower()
    # Check if the lowercase string contains the word "error"
    if "error" in lowercase_string:
        await user.send("Failed with error:\n" + output)
        return

    await user.send("Changes pulled for " + handshakedomain + "!")
    

def get_tlsa(input_string):
    lines = input_string.split("\n")
    for line in lines:
        if line.strip().startswith("TLSA:"):
            return line[6:]
    return None

def get_error(input_string):
    lines = input_string.split("\n")
    for line in lines:
        if line.strip().startswith("ERROR:"):
            return line
    return None

def updateStatus():
    # List all files in the directory using os
    files = os.listdir("/etc/nginx/sites-available")
    # Count the number of files - 1 (default)
    count = len(files) - 1
    # Set the status
    activity = discord.Activity(name=str(count) + " mirrors", type=discord.ActivityType.watching)
    # Update the status
    client.loop.create_task(client.change_presence(activity=activity))

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")
    updateStatus()

client.run(TOKEN)