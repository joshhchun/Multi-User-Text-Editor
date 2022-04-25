

class CDRT:
	def __init__(self, val, sys_count, inst_count, pos):
		self.val = val
		self.sys_count = sys_count
		self.inst_count = inst_count
		self.pos = pos

	def getval(self):
		return self.val
	
	def printval(self):
		print(self.val)

	#def getidn(self):
	#	return self.idn

	def change_pos(self, new_val, sys_count):
		if(self.inst_count != sys_count):
			return -1
		else:
			self.val = new_val
			self.inst_count += 1

def main():
	
	system_count = 0
	test_string  = "Hello World"
	

	cdrt_array = []
	for char, index  in enumerate(test_string):
		cdrt_array.append(CDRT(char, system_count, system_count, index))

	for cdrt in cdrt_array:
		cdrt.printval
		

if __name__ == "__main__":
	main()
		
		
