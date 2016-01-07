import discord
import urllib
import random
import os
import chanrestrict
import json
import shutil

HELP_MESSAGE = r"""
Hello! I'm the *LaTeX* math bot!

You can type mathematical *LaTeX* into the chat and I'll automatically render it!

Be aware that using `\begin{align}` will break me, so please don't use it.

Simply use the `!tex` command.

**Examples**

`!tex x = 7`

`!tex \sqrt{a^2 + b^2} = c`

`!tex \int_0^{2\pi} \sin{(4\theta)} \mathrm{d}\theta`
"""

LATEX_FRAMEWORK = r"""
\documentclass[varwidth=true]{standalone}
\usepackage{amsmath}
\begin{document}
\begin{align*}
__DATA__
\end{align*}
\end{document}
"""

if not os.path.isfile('settings.json'):

	shutil.copyfile('settings_default.json', 'settings.json')
	print('Now you can go and edit `settings.json`.')
	print('See README.md for more information on these settings.')

else:

	settings = json.loads(open('settings.json').read())

	chanrestrict.setup(settings['channels']['whitelist'],
					   settings['channels']['blacklist'])

	client = discord.Client()
	client.login(settings['login']['email'], settings['login']['password'])

	# Generate LaTeX locally. Is there such things as rogue LaTeX code?
	def generate_image(latex):
		num = str(random.randint(0, 2 ** 31))
		latex_file = num + '.tex'
		dvi_file = num + '.dvi'
		with open(latex_file, 'w') as tex:
			latex = LATEX_FRAMEWORK.replace('__DATA__', latex)
			tex.write(latex)
			tex.flush()
			tex.close()
		os.system('latex -quiet ' + latex_file)
		os.system('dvipng -q* -D 300 -T tight ' + dvi_file)
		png_file = num + '1.png'
		return png_file

	# More unpredictable, but probably safer for my computer.
	def generate_image_online(latex):
		url = 'http://frog.isima.fr/cgi-bin/bruno/tex2png--10.cgi?'
		url += urllib.parse.quote(latex, safe='')
		fn = str(random.randint(0, 2 ** 31)) + '.png'
		urllib.request.urlretrieve(url, fn)
		return fn

	@client.event
	@chanrestrict.apply
	def on_message(message):
		# print('Author:', message.author)
		# print('Content:', message.content)
		# print('Channel:', message.channel.name)
		# print('Server:', message.server.name)
		# print()

		msg = message.content
		
		for c in settings['commands']['render']:

			if msg.startswith(c) and (str(message.author) == client.user.name or settings['mode'] == 'reply'):
				
				latex = msg[len(c):].strip()
				print('Latex:', latex)

				if settings['renderer'] == 'external':
					fn = generate_image_online(latex)
				if settings['renderer'] == 'local':
					fn = generate_image(latex)

				if settings['mode'] == 'reply':
					if os.path.getsize(fn) > 0:
						client.send_file(message.channel, fn)
						print('Success!')
					else:
						client.send_message(message.channel, 'Something broke. :frowning:')
						print('Failure.')

				if settings['mode'] == 'edit':
					if os.path.getsize(fn) > 0:
						client.delete_message(message)
						client.send_file(message.channel, fn)
						print('Success!')
					else:
						client.send_message(message.channel, 'LaTeX failed. :frowning:')
						print('Failure.')

				break

		if msg in settings['commands']['help']:
			client.send_message(message.author, HELP_MESSAGE)

	@client.event
	def on_ready():
		print('LaTeX Math Bot!')
		print('Running as', client.user.name)

		# print(client.user.name, '|', client.user.id, '\n')
		# for i in client.servers:
		# 	print('===', i.name, '===')
		# 	print('  Channels')
		# 	for j in i.channels:
		# 		print('   ', j.type, ':', j.name)
		# 	print('  Members')
		# 	for j in i.members:
		# 		print('   ', j.name)
		# print()

	client.run()