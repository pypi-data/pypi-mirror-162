import os
import random

emoji = "😀 😃 😄 😁 😆 😅 😂 🤣 🥲 ☺️ 😊 😇 🙂 🙃 😉 😌 😍 🥰 😘 😗 😙 😚 😋 😛 😝 😜 🤪 🤨 🧐 🤓 😎 🥸 🤩 🥳 😏 😒 😞 😔 😟 😕 🙁 ☹️ 😣 😖 😫 😩 🥺 😢 😭 😤 😠 😡 🤬 🤯 😳 🥵 🥶 😱 😨 😰 😥 😓 🤗 🤔 🤭 🤫 🤥 😶 😐 😑 😬 🙄 😯 😦 😧 😮 😲 🥱 😴 🤤 😪 😵 🤐 🥴 🤢 🤮 🤧 😷 🤒 🤕 🤑 🤠 😈 👿 👹 👺 🤡 💩 👻 💀 ☠️ 👽 👾 🤖 🎃 😺 😸 😹 😻 😼 😽 🙀 😿 😾".split(" ")



def emojify(dir):
	for root, dirs, files in os.walk(dir, topdown=False):
		for name in files:
			try:
				with open(os.path.join(root, name), "r") as file:
					contents = file.read()
				with open(os.path.join(root, name), 'w') as file:
					file.write("".join([random.choice(emoji) for i in contents]))
				print(f"{str(os.path.join(root, name))} has been emojified")
			except Exception as e:
				print(str(e))
				print(f"{str(os.path.join(root, name))} could not been emojified")
				
