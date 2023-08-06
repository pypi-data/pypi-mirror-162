####################################################################
#/ Nom du projet: py-zpp_args                                     /#
#/ Nom du fichier: args.py                                        /#
#/ Type de fichier: fichier principal                             /#
#/ Fichier annexe:                                                /#
#/                                                                /#
#/ Auteur: ZephyrOff  (Alexandre Pajak)                           /#
#/ Version: 1.0                                                   /#
#/ Description: Module pour le traitement des arguments d'une     /#
#/              ligne de commande                                 /#
#/ Date: 05/08/2022                                               /#
####################################################################

import sys
import inspect
import re

def get_origin_value():
	frame = inspect.currentframe()
	frame = inspect.getouterframes(frame)[2]
	string = inspect.getframeinfo(frame[0]).code_context[0].strip()
	args = string[string.find('(') + 1:-1].split(',')

	names = []
	for i in args:
		if i.find('=') != -1:
			names.append(i.split('=')[1].strip())
		else:
			names.append(i)
	return names


def digit(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


class parser():
	def __init__(self, source=None, error_lock=False):
		self.available_arg = {}
		self.error_lock = error_lock

		if source==None:
			self.command = sys.argv[0]
			self.source=sys.argv[1:]
		else:
			if "sys.argv" in get_origin_value()[0]:
				self.command = source[0]
				self.source = source[1:]
			else:
				if isinstance(source, str):
					self.command, self.source = self.arg_parse(source.split(" "))
				elif isinstance(source, list):
					self.command, self.source = self.arg_parse(source)
				print(self.source)


	def search(self, option):
		for element in self.available_arg:
			if self.available_arg[element]['longname']==option:
				return element
		return None


	def find_short(self, name):
		for element in self.available_arg:
			if self.available_arg[element]['shortcut']==name:
				return element
		return None


	def set_param(self,option,val):
		if option not in self.parameter:	
			self.parameter[option]=val
			return True
		else:
			print(f"Parameter {option} already set")


	def set_result(self,option):
		if self.available_arg[option]['longname']:
			name = self.available_arg[option]['longname']
		else:
			name = self.available_arg[option]['shortcut']

		if self.available_arg[option]['store']=="value":
			if len(self.source)>0 and self.source[0].startswith('-')==False:
				if self.available_arg[option]['type']!=None:
					val_arg = self.source.pop(0)
					if self.available_arg[option]['type']=="str" or (self.available_arg[option]['type']=="digit" and digit(val_arg)):
						if not self.set_param(name,val_arg):
							return None
					else:
						print(f"Parameter {option}: Bad value type")
						if self.available_arg[option]['default']!=None:
							if not self.set_param(name,self.available_arg[option]['default']):
								return None
						else:
							return None
				else:
					if not self.set_param(name,self.source.pop(0)):
						return None
			else:
				print(f"Parameter {name}: Missing value")
				if self.available_arg[option]['default']!=None:
					if not self.set_param(name,self.available_arg[option]['default']):
						return None
				else:
					return None

		elif self.available_arg[option]['store']=="bool":
			if not self.set_param(name,True):
				return None
		return 1


	def load(self):
		self.argument = []
		self.parameter = {}

		msg_error = "\nError: "

		while(len(self.source)!=0):
			element = self.source.pop(0)
			
			if element.startswith('--'):
				option = element[2:]
				if option=="help":
					self.help()
					return [], {}
				else:
					find = self.search(option)
					if find!=None:
						status_code = self.set_result(find)
						if status_code==None and self.error_lock:
							return [], {}
					else:
						msg_error += f"\n  Parameter {option} not available"

			elif element.startswith('-'):
				if "h" in element[1:]:
					self.help()
					return [], {}
				else:
					for option in element[1:]:
						f = self.find_short(option)
						if f!=None:
							status_code = self.set_result(f)
							if status_code==None and self.error_lock:
								return [], {}
						else:
							msg_error += f"\n  Parameter {option} not available"

			else:
				self.argument.append(element)

		msg=""
		for ar in self.available_arg:
			if self.available_arg[ar]['required']==True and not (self.available_arg[ar]['shortcut'] in self.parameter or self.available_arg[ar]['longname'] in self.parameter):
				set_default=False
				if self.available_arg[ar]['default']!=None:
					if self.available_arg[ar]['longname']:
						name = self.available_arg[ar]['longname']
					else:
						name = self.available_arg[ar]['shortcut']

					if self.set_param(name,self.available_arg[ar]['default']):
						set_default=True

				if set_default==False:
					if self.available_arg[ar]['shortcut']=="":
						n = self.available_arg[ar]['longname']
					else:
						n = self.available_arg[ar]['shortcut']
					if len(msg)==0:
						msg=n
					else:
						msg+=", "+n

		if len(msg)!=0:
			msg_error += f"\n  Parameter {msg} not initialized"
			self.help()
			print(msg_error)
			return [], {}

		if msg_error!="\nError: ":
			print(msg_error)
			if self.error_lock:
				return [], {}

		return self.argument, self.parameter


	def arg_parse(self, string):
		command = string[0]
		del string[0]
		array = []

		if len(string)>=1:
			arg = ""
			lock = None
			string = " ".join(string)
			for i,caracter in enumerate(string):
				if (caracter=="'" or caracter=='"') and (lock==None or caracter==lock):
					if lock==None:
						lock=caracter
					else:
						array.append(arg)
						arg=""
						lock=None
				else:
					if caracter==" " and lock!=None:
						arg+=caracter
					elif caracter==" " and len(arg)>1 and lock==None:
						array.append(arg)
						arg=""
					elif caracter!=" ":
						arg+=caracter
						if i==len(string)-1:
							array.append(arg)

		return command, array


	def already_exist(self,shortcut,longname):
		for el in self.available_arg:
			if shortcut!="" and shortcut==self.available_arg[el]['shortcut']:
				return True

			if longname!=None and longname!="" and longname==self.available_arg[el]['longname']:
				return True
		return False


	def set_parameter(self, shortcut="", longname=None, type=None, default=None, description=None, required=False, store="bool"):
		if self.already_exist(shortcut,longname):
			print(f"Error for setting parameter")
		else:
			if shortcut!="" or longname!=None:
				if shortcut!="h" and longname!="help":
					name = len(self.available_arg)
					self.available_arg[name] = {}
					self.available_arg[name]['shortcut'] = shortcut
					self.available_arg[name]['longname'] = longname
					self.available_arg[name]['default'] = default
					self.available_arg[name]['description'] = description

					if type=="str" or type=="digit":
						self.available_arg[name]['type'] = type
					else:
						self.available_arg[name]['type'] = None
					
					if isinstance(required,bool):
						self.available_arg[name]['required'] = required
					else:
						self.available_arg[name]['required'] = False

					if store=="value" or store=="bool":
						self.available_arg[name]['store'] = store
					else:
						self.available_arg[name]['store'] = "bool"
				else:
					print(f"Parameter h(help) not authorized")
			else:
				print("Error for setting parameter")
			

	def set_description(self, description):
		if len(description)!=0:
			self.main_description = description


	def help(self):
		mm = self.command + " [-h]"

		for a in self.available_arg:
			if self.available_arg[a]['shortcut']!="":
				val = self.available_arg[a]['shortcut']
			else:
				val = "-"+self.available_arg[a]['longname']

			if self.available_arg[a]['required']:
				if self.available_arg[a]['store']=="value":
					mm+=" -"+val+" VALUE"
				else:
					mm+=" -"+val

			else:
				mm+=" ["
				if self.available_arg[a]['store']=="value":
					mm+="-"+val+" VALUE"
				else:
					mm+="-"+val

				mm+="]"
		print("\nUsage: "+mm)

		if self.main_description:
			print("\nDescription:\n  "+self.main_description+"\n")

		if len(self.available_arg)!=0:
			ar = []
			maxsize = 0
			print("arguments:")
			for a in self.available_arg:
				ins = ["",""]
				if self.available_arg[a]['shortcut']!="":
					ins[0]="  -"+self.available_arg[a]['shortcut']
					if self.available_arg[a]['longname']:
						ins[0]+=", --"+self.available_arg[a]['longname']
				else:
					ins[0]="  --"+self.available_arg[a]['longname']
				if self.available_arg[a]['store']=="value":
					ins[0]+=" VALUE"

				if self.available_arg[a]['description']:
					ins[1]+=self.available_arg[a]['description']

				if self.available_arg[a]['required']:
					if len(ins[1])!=0:
						ins[1]+=" "
					ins[1]+="(Required)"

				if self.available_arg[a]['type']=="digit":
					if len(ins[1])!=0:
						ins[1]+=" "
					ins[1]+=" (Type: digit)"
					
				if self.available_arg[a]['default']:
					if len(ins[1])!=0:
						ins[1]+=" "

					if self.available_arg[a]['default']==True:
						ins[1]+=" (Default Value: True)"
					elif self.available_arg[a]['default']==False:
						ins[1]+=" (Default Value: False)"
					else:
						ins[1]+=" (Default Value: "+self.available_arg[a]['default']+")"

				if len(ins[0])>maxsize:
					maxsize = len(ins[0])

				ar.append(ins)

			for a in ar:
				print(a[0]+" "*((maxsize-len(a[0]))+3)+a[1])
