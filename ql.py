#!/usr/bin/env python3
"""
=-=-=- ql -=-=-=
| Quick Ledger |
|    v.0.5     |
=-=-=-=-=-=-=-=-
*
* Brian Carter
* robotmachine@gmail.com
* https://github.com/robotmachine/ql
*
* This program is free software. It comes without any warranty, to
* the extent permitted by applicable law. You can redistribute it
* and/or modify it under the terms of the Do What The Fuck You Want
* To Public License, Version 2, as published by Sam Hocevar. See
* http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import os, sys, textwrap, datetime, argparse, configparser, distutils.util
from decimal import *

""" Settings are stored in .qlrc in user's home folder. """
settings = os.path.expanduser("~/.qlrc")
config = configparser.ConfigParser()

def main():
	"""
	Reads command line arguments to determine if a file is specified.		
	"""
	parser = argparse.ArgumentParser(description="ql: Quick `ledger' entry creation tool.", prog='ql')
	parser.add_argument('-f', '--file',
		action='store', dest='ledger_file', default=None,
		help='Specify Ledger file.')
	parser.add_argument('-a', '--account',
		action='store', dest='account', default=None,
		help="Specify account from ql's configuration file.")
	parser.add_argument('-m', '--merchant',
		action='store', dest='merchant', default=None,
		help='Not Implemented')
	parser.add_argument('--set-acct',
		action='store_true', dest='set_acct',
		help="Add accounts to ql's configuration file.")
	args = parser.parse_args()
	if args.set_acct:
		set_acct()
	read_config(ledger_file=args.ledger_file, account=args.account, merchant=args.merchant)

def read_config(ledger_file, account, merchant):
	"""
	If a settings file is specified on the command line, then just skip to the 
	actual ledger entry. If not, ql checks for the file. If it is there, then 
	ql reads from it. If there is no settings file and no file was specified, then
	we move to set up the config file.	
	"""
	if os.path.exists(settings):
		config.read(settings)
		if ledger_file is None:
			try:
				ledger_file = config['ql']['ledger_file']
			except:
				ledger_file = None
		if account is None:
			try:
				default_account = config['ql']['default_account']
			except:
				default_account = None
			if default_account is not None:
				try:
					account = config['ql'][default_account]
				except:
					account = None
		"""
		if merchant is not None:
			try:
				account = config['ql'][merchant]
			except:
				print("No merchant named %s found in ql configuration file." % merchant)
		"""
			
		if os.path.isfile(ledger_file):
			datesel(ledger_file, account, merchant)
		else:
			print("Error! Cannot find %s" % ledger_file)
	else:
		set_config(account, merchant)

def set_config(account, merchant):
	"""
	Checks for both $LEDGER and $LEDGER_FILE environment variables.
	Sets system_ledger to their value if they exist.
	"""
	try:
		if os.environ['LEDGER']:
			system_ledger = os.path.expanduser(os.environ['LEDGER'])
		elif os.environ['LEDGER_FILE']:
			system_ledger = os.path.expanduser(os.environ['LEDGER_FILE'])
	except:
		system_ledger = None

	"""
	Asks if the above value should be set as the default file for `ql'
	"""
	if system_ledger is not None: 
		print(textwrap.dedent("""
		Looks like your default ledger file is
		%s
		""") % (system_ledger))
		query = input("Use this file for ql? [y/n] ")
		try:
			boolquery = distutils.util.strtobool(query)
		except:
			print("Must enter yes or no.")
			set_config(account)
		if boolquery == True:
			led_file = system_ledger
		else:
			led_file = None
	else:
		led_file = None
	"""
	If either the $LEDGER and $LEDGER_FILE variables are empty or the user
	declines to use their value, it will request that the file be typed in manually.
	If the file is not found, an error will print.
	"""
	if led_file is None:
		led_input = input("Ledger file location: ")
		led_file = os.path.expanduser(led_input)	
		if not os.path.isfile(led_file):
			print("File not found.")
			quit()	
	"""
	Checks again to make sure the ledger_file actually exists.
	If it does, then it writes that value to .qlrc in the $HOME folder.
	"""	
	if os.path.isfile(led_file):
		config ['ql'] = {'ledger_file': led_file}
		with open(settings, 'w') as configfile:
			config.write(configfile)
		read_config(led_file, account, merchant)

def set_account():
	print("You are a star.")
	quit()

def datesel(ledger_file, account, merchant):
	tdateraw = []
	today = datetime.date.today()
	tdateraw.append(today)
	tdate = str(tdateraw[0])
	merchsel(ledger_file, account, merchant, tdate)

def merchsel(ledger_file, account, merchant, tdate):
	try:
		merchant = str(input("Merchant name:\n\t"))
		category = str("Expenses:")+str(input("Expense category:\n\tExpenses:"))
		if account is None:
			account = str("Assets:")+str(input("Account:\n\tAssets:"))
	except KeyboardInterrupt:
		print("\nUser exit.")
		quit()
	except:
		print("Syntax error.")
		merchsel(ledger_file, account, tdate)
	amountsel(ledger_file, tdate, merchant, category, account)

def amountsel(ledger_file, tdate, merchant, category, account):
	try:
		amount_dec = Decimal(input("Amount: $")).quantize(Decimal('1.00'))
	except KeyboardInterrupt:
		print("\nUser exit.")
		quit()
	except: 
		print("Amount must be a number.")
		amountsel(ledger_file, tdate, merchant, category, account)
	amount = str(amount_dec)
	printer(ledger_file, tdate, merchant, category, account, amount)

def printer(ledger_file, tdate, merchant, category, account, amount):
	ledger_entry = tdate+" * "+merchant+"\n\t"+category+"\t\t$"+amount+"\n\t"+account+"\n"
	try:
		with open(ledger_file, "a") as ledger_write:
			ledger_write.write(ledger_entry)
			ledger_write.close()
			print("\n\nWrote entry to "+ledger_file+":\n\n"+ledger_entry)
	except PermissionError:
		print("Cannot write to %s. Permission error!" % ledger_file)
	quit()
main()
